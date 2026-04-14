"""
解析MinerU解析的结果，列出所有类型
"""
import pathlib
import json

result_dir = "/Users/matoah/MinerU"

dir_path = pathlib.Path(result_dir)
if not dir_path.exists():
    raise "路径不存在"

content_list = dir_path.glob("**/*_content_list.json")
type_set = set()
for content_file in content_list:
    content = pathlib.Path(content_file).read_text(encoding="utf-8")
    object_list = json.loads(content)
    for obj in object_list:
        type = obj["type"]
        if type == "code":
            print(content_file)
        type_set.add(type)

print(type_set)