import os

from cache.cache import exist_term_cache, get_term, cache_term
from graph.document.state.document_state import DocumentState
from model.text import Text
from role.term import Term as RoleTerm, TermResult
from model.term import Term
from model.announcement import Announcement
from model.notice import Notice
from model.toc import TOC
from utils.token_util import count_tokens


def get_term_child(index, text_level, content_list):
    term_children = []
    for i in range(index + 1, len(content_list)):
        content = content_list[i]
        if isinstance(content, Text) and 0 < content.text_level <= text_level:
            break
        else:
            term_children.append(content)
    return term_children

def _merge_term(definition, state):
    _exists = False
    term_list = state.document.term_list
    term_inst = Term(**definition.model_dump())
    for index,term in enumerate(term_list):
        if term.name_zh == term_inst.name_zh:
            term_list[index] = term_inst
            _exists = True
    if not _exists:
        term_list.append(term_inst)


def _parser_hole_doc(state: DocumentState):
    """
    解析文档术语
    :param state:
    :return:
    """
    content_list = state.document.content_list
    doc_name = state.document.name
    term_content_list = []
    max_token = int(os.getenv("COMPLETION_MAX_TOKEN"))
    for content in content_list:
        if type(content) not in [Announcement, Notice, TOC]:
            term_content_list.append(content)
    if term_content_list:
        chunk_list = []
        current_chunk_token = 0
        index = 0
        chunk = []
        while index < len(term_content_list):
            content = term_content_list[index]
            content_script = content.to_md_script()
            token_count = count_tokens(content_script)
            if current_chunk_token + token_count > max_token:
                chunk_list.append(chunk)
                current_chunk_token = 0
                chunk = []
                if index - 3 > 0:
                    # 回退2个内容，防止内容被截断
                    index -= 3
            else:
                chunk.append(content)
                current_chunk_token += token_count
            index += 1
        if chunk:
            chunk_list.append(chunk)
        for chunk in chunk_list:
            chunk_content = "\n".join([item.to_md_script() for item in chunk])
            if exist_term_cache(state.spec_code, doc_name, chunk_content):
                cache_data = get_term(state.spec_code, doc_name, chunk_content)
                term_result = TermResult(**cache_data)
            else:
                role_term = RoleTerm()
                term_result = role_term.ask(chunk_content)
                cache_term(state.spec_code, doc_name, chunk_content, term_result.model_dump())
            if term_result:
                for definition in term_result.definition:
                    _merge_term(definition, state)


def _parser_by_paragraph(state: DocumentState):
    """
    从段落中解析术语定义
    :param state:
    :return:
    """
    content_list = state.document.content_list
    if content_list:
        index = 0
        role_term = RoleTerm()
        while index < len(content_list):
            content = content_list[index]
            if isinstance(content, Text) and content.text_level > 0 and "术语" in content.content.replace(" ", ""):
                text_level = content.text_level
                term_content = [content]
                term_children = get_term_child(index, text_level, content_list)
                term_content.extend(term_children)
                index += max(len(term_children), 1)
                term_script = "\n".join([term_item.to_md_script() for term_item in term_content])
                if term_script:
                    if exist_term_cache(state.spec_code, state.document.name, term_script):
                        cache_data = get_term(state.spec_code, state.document.name, term_script)
                        term_result = TermResult(**cache_data)
                    else:
                        term_result = role_term.ask(term_script)
                        cache_term(state.spec_code, state.document.name, term_script, term_result.model_dump())
                    if term_result:
                        for definition in term_result.definition:
                            state.document.term_list.append(Term(**definition.model_dump()))
            else:
                index += 1


def term_parser(state: DocumentState):
    """
    解析文档术语
    解析逻辑：
    1、如果文档名称包含术语，则认为整个文档都是术语定义
    2、如果文档名称不包含术语，则根据文档内容解析术语定义
    """
    doc_name = state.document.name
    doc_name = doc_name.replace(" ", "")
    if "术语" in doc_name:
        _parser_hole_doc(state)
    else:
        _parser_by_paragraph(state)
    return {}
