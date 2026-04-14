from pydantic import BaseModel

from model.organization import Organization
from model.person import Person


def get_doc_page_index(start_index: int, count: int, page_list: list[list[dict]])->list[int]:
    """获取文档页码，非真实页码"""
    if start_index >= len(page_list):
        return []
    doc_page_index = []
    data = page_list[start_index: start_index + count]
    for page in data:
        for item in page:
            _type = item.get("type","text")
            if _type == "page_number":
                page_text = item.get("text")
                # 去除字符串中非数字字符
                page_text = "".join(filter(str.isdigit, page_text)) # type: ignore[assignment]
                # 检查是否为空
                if page_text.isdigit():
                    doc_page_index.append(int(page_text))
    return doc_page_index

def _merge_field_value(source: BaseModel, target: BaseModel) -> bool:
    """合并字段值"""
    flag = False
    for field, value in source.__dict__.items():
        exist_value = getattr(target, field)
        if isinstance(value, str):
            if exist_value is None or exist_value.strip() == "":
                flag = True
                setattr(target, field, value)
        elif isinstance(value, list):
            for item in value:
                if not item in exist_value:
                    flag = True
                    exist_value.append(item)
    return flag

def merge_doc_organization_list(organization_list: list[Organization], organizations: list[Organization]) -> bool:
    """合并单位列表"""
    flag = False
    for organization in organization_list:
        flag |= merge_doc_organization(organization, organizations)
    return flag

def merge_doc_person_list(person_list: list[Person], persons: list[Person]) -> bool:
    """合并人员列表"""
    flag = False
    for person in person_list:
        flag |= merge_doc_person(person, persons)
    return flag

def merge_doc_organization(organization: Organization, organizations: list[Organization]) -> bool:
    """合并单位"""
    exist_org = next((org for org in organizations if org.name == organization.name), None)
    if exist_org:
        return _merge_field_value(organization, exist_org)
    else:
        organizations.append(organization)
        return True

def merge_doc_person(person: Person, persons: list[Person]) -> bool:
    """合并人员"""
    exist_person = next((exist_person for exist_person in persons if exist_person.name == person.name), None)
    if exist_person:
        return _merge_field_value(person, exist_person)
    else:
        persons.append(person)
        return True
