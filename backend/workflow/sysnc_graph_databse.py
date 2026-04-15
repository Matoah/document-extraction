"""
同步图数据库，将文档解析结果同步到图数据库
"""
from pathlib import Path
from py2neo import Graph
import os
import json
import logging

logger = logging.getLogger(__name__)

index_map = {}

type_mapping = {
    "standard": "标准",
    "specification": "规范",
    "guideline": "细则",
    "procedure": "规程",
    "guide": "导则",
    "method": "办法",
    "quota": "定额",
    "guidance": "指南",
    "drawing": "通用图",
}


# ------------------ 工具函数 ------------------

def _get_index(domain: str) -> int:
    """获取领域索引"""
    if domain not in index_map:
        index_map[domain] = 0
    index_map[domain] += 1
    return index_map[domain]


def _clear_dict(dict_data: dict):
    """清理字典中的值"""
    new_data = {}
    for key, value in dict_data.items():
        if value is not None:
            if isinstance(value, str):
                if value.strip() != "":
                    new_data[key] = value
            elif isinstance(value, list):
                if value:
                    new_data[key] = value
    return new_data


def merge_node(label: str, identifier: dict, graph: Graph, properties: dict | None = None) -> dict:
    """MERGE 节点"""
    properties = properties or {}
    properties = _clear_dict(properties)
    id_keys = ", ".join([f"{k}: ${k}" for k in identifier.keys()])
    cypher = f"""
    MERGE (n:{label} {{ {id_keys} }})
    SET n += $props
    RETURN n
    """
    params = {**identifier, "props": properties}
    return graph.run(cypher, **params).evaluate()


def merge_relationship(
        source_label: str,
        source_id: dict,
        rel: str,
        target_label: str,
        target_id: dict,
        graph: Graph,
):
    """MERGE 关系"""
    s_keys = ", ".join([f"{k}: $s_{k}" for k in source_id])
    t_keys = ", ".join([f"{k}: $t_{k}" for k in target_id])

    cypher = f"""
    MATCH (a:{source_label} {{ {s_keys} }})
    MATCH (b:{target_label} {{ {t_keys} }})
    MERGE (a)-[:{rel}]->(b)
    """

    params = {
        **{f"s_{k}": v for k, v in source_id.items()},
        **{f"t_{k}": v for k, v in target_id.items()},
    }

    graph.run(cypher, **params)


def to_page_index(page_index: dict, key: str):
    value = page_index.get(key)
    if isinstance(value, list):
        return ",".join(map(str, value))
    if isinstance(value, int) and value != -1:
        return value
    return None


# ------------------ Identifier ------------------


def spec_id(d): return "标准规范", {"编号": d.get("code")}


def doc_id(d): return "文档", {"文件名称": d.get("name")}


def person_id(d): return "人员", {"姓名": d.get("name")}


def org_id(d): return "组织机构", {"组织机构名称": d.get("name")}


def announcement_id(d): return "公告", {"编号": d.get("code")}


def notice_id(d): return "通知", {"编号": d.get("code")}


def content_id(d): return "文档内容", {"编号": d.get("code")}


def term_id(d): return "术语", {"名称": d.get("name_zh")}


def symbol_id(d): return "符号", {"符号": d.get("symbol")}


# ------------------ 通用关系封装 ------------------


def link_people(source, rel, people, graph: Graph):
    for p in people or []:
        if p:
            pid = person_id(p)
            merge_node(pid[0], pid[1], graph)
            merge_relationship(source[0], source[1], rel, pid[0], pid[1], graph)


def link_terms(source, rel, terms, graph: Graph):
    for term in terms or []:
        if term:
            tid = term_id(term)
            merge_node(tid[0], tid[1], graph, {
                "缩写": term.get("alias"),
                "名称": term.get("name_zh"),
                "定义": term.get("definition"),
                "英文名称": term.get("name_en"),
            })
            merge_relationship(source[0], source[1], rel, tid[0], tid[1], graph)


def link_symbols(source, rel, symbols, graph: Graph):
    for symbol in symbols or []:
        if symbol:
            sid = symbol_id(symbol)
            merge_node(sid[0], sid[1], graph, {
                "符号": symbol.get("symbol"),
                "别名": symbol.get("alias"),
                "名称": symbol.get("name"),
                "单位": symbol.get("unit")
            })
            merge_relationship(source[0], source[1], rel, sid[0], sid[1], graph)


def link_orgs(source, rel, orgs, graph: Graph):
    for o in orgs or []:
        if o:
            oid = org_id(o)
            merge_node(oid[0], oid[1], graph, {
                "地址": o.get("address"),
                "邮编": o.get("postal_code"),
                "电子邮箱": o.get("email"),
                "联系电话": o.get("phone"),
                "传真": o.get("fax"),
            })
            merge_relationship(source[0], source[1], rel, oid[0], oid[1], graph)


# ------------------ 实体生成 ------------------


def gen_specification(spec, spec_config, graph: Graph):
    sid = spec_id(spec)

    props = {
        "板块": spec.get("plate"),
        "模块": spec.get("module"),
        "名称": spec.get("name"),
        "标准规范类型": spec.get("standard_nature"),
        "一级分类": spec.get("category_level_1"),
        "二级分类": spec.get("category_level_2"),
        "类型": type_mapping.get(spec.get("type")),
        "生命周期阶段": spec.get("stage"),
        "领域": spec.get("domain"),
        "发布日期": spec.get("release_date"),
        "实施日期": spec.get("effective_date"),
        "批准部门": spec.get("approved_by"),
        "关键字": ",".join(spec_config.get("keywords", [])),
    }

    merge_node(sid[0], sid[1], graph, props)


def gen_document(spec, docs, graph: Graph):
    sid = spec_id(spec)

    for index, d in enumerate(docs):
        logger.info(f"处理文档: {d.get('name')} {index + 1}/{len(docs)}")
        did = doc_id(d)

        merge_node(did[0], did[1], graph, {
            "文件大小": d.get("size"),
            "创建时间": d.get("create_time"),
            "修改时间": d.get("modify_time"),
            "文件唯一标识": d.get("md5"),
        })

        merge_relationship(sid[0], sid[1], "关联文档", did[0], did[1], graph)

        link_people(did, "主编", d.get("chief_editor"), graph)
        link_people(did, "主要参编人员", d.get("main_contributors"), graph)
        link_people(did, "参加人员", d.get("contributors"), graph)
        link_people(did, "主审", d.get("chief_reviewer"), graph)
        link_people(did, "参审人员", d.get("reviewing_participant"), graph)
        link_people(did, "联系人", d.get("contact_person"), graph)

        link_orgs(did, "主编单位", d.get("chief_editor_organization"), graph)
        link_orgs(did, "参编单位", d.get("participating_organization"), graph)
        link_orgs(did, "联系单位", d.get("contact_organization"), graph)

        link_terms(did, "术语", d.get("term_list"), graph)

        link_symbols(did, "符号", d.get("symbol_list"), graph)

        for c in d.get("content_list", []):
            handle_content(did, d["name"], c, graph)


def handle_content(doc_identifier, doc_name, content, graph: Graph):
    t = content.get("type")

    if t == "announcement":
        aid = announcement_id(content)
        merge_node(aid[0], aid[1], graph, {
            "标题": content.get("title"),
            "内容": content.get("content"),
            "发布日期": content.get("release_date"),
            "印发日期": content.get("issue_date"),
            "真实页码": to_page_index(content, "page_index"),
            "文档页码": to_page_index(content, "doc_page_index"),
        })
        merge_relationship(doc_identifier[0], doc_identifier[1], "关联公告", aid[0], aid[1], graph)
        link_orgs(aid, "发文机关", [content.get("release_org")] if content.get("release_org") else [], graph)
        link_orgs(aid, "印发机关", [content.get("issue_org")] if content.get("issue_org") else [], graph)

    elif t == "notice":
        nid = notice_id(content)
        merge_node(nid[0], nid[1], graph, {
            "标题": content.get("title"),
            "内容": content.get("content"),
            "发布日期": content.get("release_date"),
            "真实页码": to_page_index(content, "page_index"),
            "文档页码": to_page_index(content, "doc_page_index"),
        })
        merge_relationship(doc_identifier[0], doc_identifier[1], "关联通知", nid[0], nid[1], graph)
        link_orgs(nid, "发文机关", content.get("release_org"), graph)

    elif t == "toc":
        tid = ("目录", {"标识": f"{doc_name}_toc{_get_index(f"{doc_name}_toc")}"})
        merge_node(tid[0], tid[1], graph, {
            "标题": content.get("title"),
            "真实页码": to_page_index(content, "page_index"),
            "文档页码": to_page_index(content, "doc_page_index"),
        })
        merge_relationship(doc_identifier[0], doc_identifier[1], "关联目录", tid[0], tid[1], graph)

        def handle_toc_item(children, pid):
            for item in children or []:
                item_id = ("目录项", {"标识": f"{doc_name}-目录项-{item.get('id')}"})
                merge_node(item_id[0], item_id[1], graph, {
                    "标题": item.get("title"),
                    "真实页码": to_page_index(item, "page_index"),
                    "文档页码": to_page_index(item, "doc_page_index"),
                })
                merge_relationship(pid[0], pid[1], "子目录项", item_id[0], item_id[1], graph)
                handle_toc_item(item.get("children"), item_id)

        handle_toc_item(content.get("items"), tid)

    elif t == "code":
        cid = ("代码", {"标识": f"{doc_name}_code{_get_index(f"{doc_name}_code")}"})
        merge_node(cid[0], cid[1], graph, {
            "标题": "\n".join(content.get("code_caption", [])),
            "内容": content.get("code_body"),
            "语言": content.get("code_language"),
            "真实页码": to_page_index(content, "page_index"),
            "文档页码": to_page_index(content, "doc_page_index"),
        })
        merge_relationship(doc_identifier[0], doc_identifier[1], "关联代码", cid[0], cid[1], graph)

    elif t == "equation":
        eid = ("公式", {"标识": f"{doc_name}_equation{_get_index(f"{doc_name}_equation")}"})
        merge_node(eid[0], eid[1], graph, {
            "格式": content.get("format"),
            "内容": content.get("content"),
            "标签": content.get("tag"),
            "真实页码": to_page_index(content, "page_index"),
            "文档页码": to_page_index(content, "doc_page_index"),
        })
        merge_relationship(doc_identifier[0], doc_identifier[1], "关联公式", eid[0], eid[1], graph)

    elif t == "table":
        tid = ("表格", {"标识": f"{doc_name}_table_{_get_index(f"{doc_name}_table")}"})
        merge_node(tid[0], tid[1], graph, {
            "标题": content.get("title"),
            "编码": content.get("code"),
            "内容": content.get("table_body"),
            "图片路径": content.get("img_path"),
            "是否续表": content.get("is_continued"),
            "脚注": "\n".join(content.get("footer_notes", [])),
            "真实页码": to_page_index(content, "page_index"),
            "文档页码": to_page_index(content, "doc_page_index"),
        })
        merge_relationship(doc_identifier[0], doc_identifier[1], "关联表格", tid[0], tid[1], graph)

    elif t == "image":
        iid = ("图片", {"标识": f"{doc_name}_image{_get_index(f"{doc_name}_image")}"})
        merge_node(iid[0], iid[1], graph, {
            "编号": content.get("code"),
            "标题": content.get("title"),
            "脚注": "\n".join(content.get("footer_notes", [])),
            "描述": content.get("desc"),
            "路径": content.get("path"),
            "真实页码": to_page_index(content, "page_index"),
            "文档页码": to_page_index(content, "doc_page_index"),
        })
        merge_relationship(doc_identifier[0], doc_identifier[1], "关联图片", iid[0], iid[1], graph)


def sync_graph_database():
    graph = Graph(
        os.getenv("NEO4J_URI"),
        name=os.getenv("NEO4J_DATABASE"),
        auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")),
    )

    output_dir = Path(__file__).parent.parent.parent / "output"
    if not output_dir.exists():
        raise FileNotFoundError("未找到数据目录")

    files = list(output_dir.glob("**/data.json"))

    for i, f in enumerate(files, 1):
        data = json.loads(f.read_text("utf-8"))

        config = data.get("standard_specification_config", {})
        standard_spec = data.get("standard_specification", {})

        logger.info(f"处理标准规范: {config.get('code')} ({i}/{len(files)})")

        gen_specification(standard_spec, config, graph)
        gen_document(standard_spec, data.get("document_list", []), graph)
