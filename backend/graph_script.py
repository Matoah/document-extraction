from pathlib import Path
from datetime import datetime
import json
from py2neo import Graph, Node, Relationship
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("")

load_dotenv()

graph = Graph(os.getenv("NEO4J_URI"), name=os.getenv("NEO4J_DATABASE"), auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")))

dir_path = Path(__file__).parent.parent / "graph_script"

dir_path.mkdir(parents=True, exist_ok=True)

now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

file_path = dir_path / f"neo4j-{now_str}.txt"

output_dir = Path(__file__).parent.parent / "output"

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
    "drawing": "通用图"
}


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


def _to_str(_list: list[int], sep: str = ",") -> str:
    """将列表转换为字符串"""
    return sep.join(map(str, _list))

def _to_page_index(page_index: dict, attr: str) -> int | None:
    if attr in page_index:
        value = page_index.get(attr)
        if isinstance(value, list):
            return _to_str(value, ",")# type: ignore
        if isinstance(value, int):
            return value if value != -1 else None
    return None

def gen_update_script(properties: dict) -> tuple[str, dict]:
    """生成更新属性脚本"""
    values = {}
    update_script = []
    for key, value in properties.items():
        var_name = f"update_var{_get_index("neo4j_update_var")}"
        update_script.append(f"n.{key} = ${var_name}")
        values[var_name] = value
    return " SET "+",".join(update_script) if update_script else " RETURN n", values

def gen_where_script(identifier: dict) -> tuple[str,dict]:
    values = {}
    where_script = []
    for key, value in identifier.items():
        var_name = f"varname{_get_index("neo4j_query_var")}"
        where_script.append(f"n.{key} = ${var_name}")
        values[var_name] = value
    return " WHERE "+" AND ".join(where_script), values

def merge_entity(entity_name: str, identifier: dict, properties: dict):
    """更新实体，如果不存在则创建，否则更新属性"""
    where_script, where_values = gen_where_script(identifier)
    result = graph.run(f"MATCH (n:{entity_name}){where_script} RETURN n",**where_values)
    datas = result.data()
    entity = None
    if len(datas) > 0:
        entity = datas[0]["n"]
    if entity is not None:
        # 更新属性
        update_script, update_values = gen_update_script(properties)
        graph.run(f"MATCH (n:{entity_name}){where_script}{update_script}",  **update_values,**identifier,**where_values)
    else:
        # 创建实体
        entity = Node(entity_name, **properties,**identifier)
        graph.create(entity)

def query_entity(entity_name: str, identifier: dict):
    """查询实体"""
    where_script, where_values = gen_where_script(identifier)
    result = graph.run(f"MATCH (n:{entity_name}){where_script} RETURN n",**where_values)
    datas = result.data()
    if len(datas) > 0:
        return datas[0]["n"]
    return None

def merge_relation(source: tuple[str, dict], relation_name: str, target: tuple[str, dict]):
    """更新关系，如果不存在则创建"""
    source_entity = query_entity(source[0], identifier=source[1])
    if source_entity is None:
        raise ValueError(f"源实体 {source[0]} 不存在, 无法创建关系，条件信息：{json.dumps(source[1])}")
    target_entity = query_entity(target[0], identifier=target[1])
    if target_entity is None:
        raise ValueError(f"目标实体 {target[0]} 不存在, 无法创建关系，条件信息：{json.dumps(target[1])}")
    result = graph.run(f"MATCH (source)-[r:{relation_name}]->(target) WHERE id(source) = $source_id AND id(target) = $target_id RETURN r", source_id=source_entity.identity, target_id=target_entity.identity)
    datas = result.data()
    if len(datas) < 1:
        # 创建关系
        graph.create(Relationship(source_entity, relation_name, target_entity))

def get_specification_identifier(_standard_specification: dict) -> tuple[str, dict]:
    """获取标准规范的标识符"""
    return "标准规范", {"编号": _standard_specification.get("code")}

def get_document_identifier(document: dict) -> tuple[str, dict]:
    return "文档", {"文件名称": document.get("name")}

def get_person_identifier(person: dict) -> tuple[str, dict]:
    return "人员", {"姓名": person.get("name")}

def get_organization_identifier(organization: dict) -> tuple[str, dict]:
    return "组织机构", {"组织机构名称": organization.get("name")}

def get_announcement_identifier(announcement: dict) -> tuple[str, dict]:
    return "公告", {"编号": announcement.get("code")}

def get_notice_identifier(notice: dict) -> tuple[str, dict]:
    return "通知", {"编号": notice.get("code")}

def get_code_identifier(document_name: str, code_data: dict) -> tuple[str, dict]:
    code_var = f"{document_name}_code{_get_index(f"{document_name}_code")}"
    return "代码", {"标识": code_var}

def get_equation_identifier(document_name: str, equation_data: dict) -> tuple[str, dict]:
    equation_var = f"{document_name}_equation{_get_index(f"{document_name}_equation")}"
    return "公式", {"标识": equation_var}

def get_table_identifier(document_name: str, table_data: dict) -> tuple[str, dict]:
    table_var = f"{document_name}_table{_get_index(f"{document_name}_table")}"
    return "表格", {"标识": table_var}

def get_image_identifier(document_name: str, image_data: dict) -> tuple[str, dict]:
    image_var = f"{document_name}_image{_get_index(f"{document_name}_image")}"
    return "图片", {"标识": image_var}

def get_toc_identifier(document_name: str, toc_data: dict) -> tuple[str, dict]:
    toc_var = f"{document_name}_toc{_get_index(f"{document_name}_toc")}"
    return "目录", {"标识": toc_var}

def get_toc_item_identifier(document_name: str, toc_item_data: dict) -> tuple[str, dict]:
    return "目录项", {"标识": f"{document_name}-目录项-{toc_item_data.get('id')}"}

def gen_specification_entity(_standard_specification: dict, _standard_specification_config: dict):
    """生成标准规范实体"""
    entity_name,identifier = get_specification_identifier(_standard_specification)
    properties = {
        "板块": _standard_specification.get("plate"),
        "模块": _standard_specification.get("module"),
        "名称": _standard_specification.get("name"),
        "标准规范类型": _standard_specification.get("standard_nature"),
        "一级分类": _standard_specification.get("category_level_1"),
        "二级分类": _standard_specification.get("category_level_2"),
        "类型": type_mapping.get(_standard_specification.get("type")),
        "生命周期阶段": _standard_specification.get("stage"),
        "领域": _standard_specification.get("domain"),
        "发布日期": _standard_specification.get("release_date"),
        "实施日期": _standard_specification.get("effective_date"),
        "批准部门": _standard_specification_config.get("approved_by"),
        "关键字": ",".join(_standard_specification_config.get("keywords", [])),
    }
    merge_entity(entity_name, identifier, properties)


def gen_document_entity(_standard_specification: dict, _document_list: list[dict]):
    """生成文档实体"""
    specification_identifier = get_specification_identifier(_standard_specification)
    for document in _document_list:
        document_name = document.get("name")
        document_identifier = get_document_identifier(document)
        properties = {
            "文件大小": document.get("size"),
            "创建时间": document.get("create_time"),
            "修改时间": document.get("modify_time"),
            "文件唯一标识": document.get("md5"),
        }
        merge_entity(document_identifier[0], document_identifier[1], properties)
        merge_relation(specification_identifier, "关联文档", document_identifier)
        chief_editor = document.get("chief_editor", [])
        for editor in chief_editor:
            gen_person_entity(editor)
            merge_relation(document_identifier, "主编", get_person_identifier(editor))
        main_contributors = document.get("main_contributors", [])
        for contributor in main_contributors:
            gen_person_entity(contributor)
            merge_relation(document_identifier, "主要参编人员", get_person_identifier(contributor))
        contributors = document.get("contributors", [])
        for contributor in contributors:
            gen_person_entity(contributor)
            merge_relation(document_identifier, "参加人员", get_person_identifier(contributor))
        chief_reviewer = document.get("chief_reviewer", [])
        for reviewer in chief_reviewer:
            gen_person_entity(reviewer)
            merge_relation(document_identifier, "主审", get_person_identifier(reviewer))
        reviewing_participant = document.get("reviewing_participant", [])
        for participant in reviewing_participant:
            gen_person_entity(participant)
            merge_relation(document_identifier, "参审人员", get_person_identifier(participant))
        contact_person = document.get("contact_person", [])
        for person in contact_person:
            if person:
                gen_person_entity(person)
                merge_relation(document_identifier, "联系人", get_person_identifier(person))
        chief_editor_organization = document.get("chief_editor_organization", [])
        for organization in chief_editor_organization:
            gen_organization_entity(organization)
            merge_relation(document_identifier, "主编单位", get_organization_identifier(organization))
        participating_organization = document.get("participating_organization", [])
        for organization in participating_organization:
            gen_organization_entity(organization)
            merge_relation(document_identifier, "参编单位", get_organization_identifier(organization))
        contact_organization = document.get("contact_organization", [])
        for organization in contact_organization:
            if organization:
                gen_organization_entity(organization)
                merge_relation(document_identifier, "联系单位", get_organization_identifier(organization))
        content_list = document.get("content_list", [])
        for content in content_list:
            type = content.get("type", "text")
            if type == "announcement":
                gen_announcement_entity(content)
                merge_relation(document_identifier, "关联公告", get_announcement_identifier(content))
            elif type == "notice":
                gen_notice_entity(content)
                merge_relation(document_identifier, "关联通知", get_notice_identifier(content))
            elif type == "toc":
                toc_identifier = gen_toc_entity(document_name, content)
                merge_relation(document_identifier, "关联目录", toc_identifier)
            elif type == "code":
                code_identifier = gen_code_entity(document_name,content)
                merge_relation(document_identifier, "关联代码", code_identifier)
            elif type == "equation":
                equation_identifier = gen_equation_entity(document_name, content)
                merge_relation(document_identifier, "关联公式", equation_identifier)
            elif type == "table":
                table_identifier = gen_table_script(document_name, content)
                merge_relation(document_identifier, "关联表格", table_identifier)
            elif type == "image":
                image_identifier = gen_image_entity(document_name, content)
                merge_relation(document_identifier, "关联图片", image_identifier)


def gen_person_entity(person_data: dict):
    """生成人员实体"""
    entity_name, identifier = get_person_identifier(person_data)
    properties = {}
    merge_entity(entity_name, identifier, properties)

def gen_organization_entity(organization: dict):
    """生成组织机构实体"""
    entity_name, identifier = get_organization_identifier(organization)
    properties = {
        "地址": organization.get("address"),
        "邮编": organization.get("postal_code"),
        "电子邮箱": organization.get("email"),
        "联系电话": organization.get("phone"),
        "传真": organization.get("fax"),
    }
    merge_entity(entity_name, identifier, properties)


def gen_announcement_entity(announcement_data: dict):
    """生成公告实体"""
    announcement_identifier = get_announcement_identifier(announcement_data)
    properties = {
        "标题": announcement_data.get("title"),
        "主题": announcement_data.get("subject"),
        "内容": announcement_data.get("content"),
        "发布日期": announcement_data.get("release_date"),
        "印发日期": announcement_data.get("issue_date"),
        "真实页码": _to_page_index(announcement_data, "page_index"),
        "文档页码": _to_page_index(announcement_data, "doc_page_index"),
    }
    merge_entity(announcement_identifier[0], announcement_identifier[1], properties)
    release_org = announcement_data.get("release_org")
    if release_org:
        gen_organization_entity(release_org)
        merge_relation(announcement_identifier, "发文机关", get_organization_identifier(release_org))
    issue_org = announcement_data.get("issue_org")
    if issue_org:
        gen_organization_entity(issue_org)
        merge_relation(announcement_identifier, "印发机关", get_organization_identifier(issue_org))

def gen_notice_entity(notice_data: dict):
    """生成通知实体"""
    notice_identifier = get_notice_identifier(notice_data)
    properties = {
        "标题": notice_data.get("title"),
        "内容": notice_data.get("content"),
        "发布日期": notice_data.get("release_date"),
        "真实页码": _to_page_index(notice_data, "page_index"),
        "文档页码": _to_page_index(notice_data, "doc_page_index"),
    }
    release_org = notice_data.get("release_org")
    if release_org:
        gen_organization_entity(release_org)
        merge_relation(notice_identifier, "发文机关", get_organization_identifier(release_org))
    merge_entity(notice_identifier[0], notice_identifier[1], properties)


def gen_table_script(document_name: str, table_data: dict) -> tuple[str, dict]:
    """生成表格实体"""
    table_identifier = get_table_identifier(document_name, table_data)
    properties = {
        "标题": table_data.get("title"),
        "编码": table_data.get("code"),
        "图片路径": table_data.get("img_path"),
        "内容": table_data.get("table_body"),
        "是否续表": table_data.get("is_continued"),
        "脚注": "\n".join(table_data.get("footer_notes", [])),
        "真实页码": _to_page_index(table_data, "page_index"),
        "文档页码": _to_page_index(table_data, "doc_page_index"),
    }
    merge_entity(table_identifier[0], table_identifier[1], properties)
    return table_identifier


def gen_toc_entity(document_name: str, toc_data: dict):
    """生成目录实体"""
    toc_identifier = get_toc_identifier(document_name,toc_data)
    properties = {
        "标题": toc_data.get("title"),
        "真实页码": _to_page_index(toc_data, "page_index"),
        "文档页码": _to_page_index(toc_data, "doc_page_index"),
    }
    merge_entity(toc_identifier[0], toc_identifier[1], properties)
    toc_item_list = toc_data.get("items", [])
    gen_toc_item_entity(document_name, toc_identifier, toc_item_list)
    return toc_identifier


def gen_toc_item_entity(document_name: str, parent_identifier: tuple[str, dict], items: list[dict]):
    for toc_item in items:
        toc_item_identifier = get_toc_item_identifier(document_name, toc_item)
        properties = {
            "标题": toc_item.get("title"),
            "真实页码": _to_page_index(toc_item, "page_index"),
            "文档页码": _to_page_index(toc_item, "doc_page_index"),
        }
        merge_entity(toc_item_identifier[0], toc_item_identifier[1], properties)
        merge_relation(parent_identifier, "子目录项", toc_item_identifier)
        children = toc_item.get("children", [])
        if children:
            gen_toc_item_entity(document_name, toc_item_identifier, children)


def gen_code_entity(document_name: str,code_data: dict):
    """生成代码实体"""
    code_identifier = get_code_identifier(document_name, code_data)
    properties = {
        "标题": "\n".join(code_data.get("code_caption", [])),
        "内容": code_data.get("code_body"),
        "语言": code_data.get("code_language"),
        "真实页码": _to_page_index(code_data, "page_index"),
        "文档页码": _to_page_index(code_data, "doc_page_index"),
    }
    merge_entity(code_identifier[0], code_identifier[1], properties)
    return code_identifier


def gen_equation_entity(document_name: str, equation_data: dict):
    """生成公式实体"""
    equation_identifier = get_equation_identifier(document_name, equation_data)
    properties = {
        "格式": equation_data.get("format"),
        "内容": equation_data.get("content"),
        "标签": equation_data.get("tag"),
        "真实页码": _to_page_index(equation_data, "page_index"),
        "文档页码": _to_page_index(equation_data, "doc_page_index"),
    }
    merge_entity(equation_identifier[0], equation_identifier[1], properties)
    return equation_identifier


def gen_image_entity(document_name: str, image_data: dict):
    """生成图片实体"""
    image_identifier = get_image_identifier(document_name, image_data)
    properties = {
        "编号": image_data.get("code"),
        "标题": image_data.get("title"),
        "脚注": "\n".join(image_data.get("footer_notes", [])),
        "描述": image_data.get("desc"),
        "图片路径": image_data.get("path"),
        "真实页码": _to_page_index(image_data, "page_index"),
        "文档页码": _to_page_index(image_data, "doc_page_index"),
    }
    merge_entity(image_identifier[0], image_identifier[1], properties)
    return image_identifier


if output_dir.exists():
    data_files = list(output_dir.glob("**/data.json"))
    data_size = len(data_files)
    for index, file in enumerate(data_files):
        data = json.loads(file.read_text(encoding="utf-8"))
        standard_specification_config = data.get("standard_specification_config")
        logger.info(f"正在处理标准规范：{standard_specification_config.get("code")}  {index + 1}/{data_size}")
        standard_specification = data.get("standard_specification")
        document_list = data.get("document_list", [])
        gen_specification_entity(standard_specification, standard_specification_config)
        gen_document_entity(standard_specification, document_list)
else:
    raise FileNotFoundError(f"未找到标准规范解析结果！")
