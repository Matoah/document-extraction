from py2neo import Graph
from collections import defaultdict
import os
from dotenv import load_dotenv

load_dotenv()

# ====== 配置 ======
IGNORE_PROPS = {"_id", "id", "created_at", "updated_at"}
REL_SAMPLE_LIMIT = 50   # 每种关系最多采样数量
GLOBAL_REL_LIMIT = 500  # 全局最大关系采样

# ====== 连接 Neo4j ======
graph = Graph(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")),
    name=os.getenv("NEO4J_DATABASE")
)

# ====== 1. 获取节点属性（含类型） ======
node_query = """
CALL db.schema.nodeTypeProperties()
YIELD nodeType, propertyName, propertyTypes
RETURN nodeType, propertyName, propertyTypes
"""

node_raw = graph.run(node_query).data()

nodes = defaultdict(dict)

for row in node_raw:
    label = row["nodeType"].replace(":", "")
    prop = row["propertyName"]

    if prop in IGNORE_PROPS:
        continue

    types = row["propertyTypes"]
    prop_type = types[0] if types else "ANY"

    nodes[label][prop] = prop_type

# ====== 2. 获取关系结构（新版：真实数据推断 + 安全兜底） ======

relationships = set()

# --- 2.1 获取所有关系类型 ---
rel_types_query = "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType"
rel_types = [r["relationshipType"] for r in graph.run(rel_types_query)]

# --- 2.2 按关系类型逐个采样 ---
for rel_type in rel_types:
    query = f"""
    MATCH (a)-[r:`{rel_type}`]->(b)
    RETURN DISTINCT labels(a) AS from_labels,
                    labels(b) AS to_labels
    LIMIT {REL_SAMPLE_LIMIT}
    """

    results = graph.run(query).data()

    for row in results:
        from_labels = row["from_labels"]
        to_labels = row["to_labels"]

        if not from_labels or not to_labels:
            continue

        from_label = from_labels[0]
        to_label = to_labels[0]

        relationships.add((from_label, rel_type, to_label))

# --- 2.3 兜底：补充“无数据关系类型” ---
# 防止某些关系没有数据被漏掉
for rel_type in rel_types:
    if not any(r[1] == rel_type for r in relationships):
        relationships.add(("Unknown", rel_type, "Unknown"))

# ====== 3. 生成 Schema 文本 ======
def format_nodes(nodes_dict):
    lines = []
    for label in sorted(nodes_dict.keys()):
        props = nodes_dict[label]
        if props:
            props_str = ", ".join(
                f"{k}: {v}" for k, v in sorted(props.items())
            )
        else:
            props_str = ""
        lines.append(f"- {label} {{{props_str}}}")
    return "\n".join(lines)


def format_relationships(rels):
    lines = []
    for from_label, rel_type, to_label in sorted(rels):
        lines.append(f"- ({from_label})-[:{rel_type}]->({to_label})")
    return "\n".join(lines)


schema_text = f"""Graph Schema:
节点定义:
{format_nodes(nodes)}

关系定义:
{format_relationships(relationships)}
"""

print(schema_text)

# ====== 4. 生成 LLM Prompt ======
# prompt = f"""
# You are a Neo4j expert.
#
# Use ONLY the following graph schema to generate Cypher queries.
#
# {schema_text}
#
# Rules:
# 1. Only use the provided node labels, relationship types, and properties
# 2. Do NOT use CREATE, DELETE, MERGE
# 3. Always add LIMIT 50
# 4. Avoid full graph scan
# 5. Prefer using indexed properties if possible
#
# Return ONLY Cypher query.
# """
#
# print("\n" + "=" * 50)
# print("LLM PROMPT:")
# print("=" * 50)
# print(prompt)