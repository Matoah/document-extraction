from graph.document.state.document_state import DocumentState
from graph.page.index import invoke as page_invoke

def document_paser(state: DocumentState):
    """文档解析"""
    origin_document = state.origin_document
    spec_code = state.spec_code
    document_name = origin_document.name
    standard_specification = state.standard_specification
    page_list = origin_document.page_list
    #document = Document.from_original_document(origin_document)
    #document_state: DocumentState = DocumentState(origin_document=origin_document, document=document)
    page_index = 0
    page_size = len(page_list)
    while page_index < page_size:
        # logger.info(f"正在解析第{page_index+1}/{page_size}页")
        page = page_list[page_index]
        page_state = page_invoke(page_content=page, specification_code=spec_code, document_name=document_name,
                                 page_index=page_index, page_list=page_list, document_state=state,
                                 standard_specification=standard_specification)
        page_index += page_state.get("page_step")
    return {}