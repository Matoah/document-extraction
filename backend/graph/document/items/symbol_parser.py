from graph.document.state.document_state import DocumentState
from model.text import Text
from role.symbol import Symbol as RoleSymbol, SymbolResult
from model.symbol import Symbol
from cache.cache import cache_symbol, exist_symbol_cache, get_symbol

def get_symbol_child(index, text_level, content_list):
    symbol_children = []
    for i in range(index+1, len(content_list)):
        content = content_list[i]
        if isinstance(content, Text) and 0 < content.text_level <= text_level:
            break
        else:
            symbol_children.append(content)
    return symbol_children

def symbol_parser(state: DocumentState):
    content_list = state.document.content_list
    if content_list:
        index = 0
        role_term = RoleSymbol()
        while index < len(content_list):
            content = content_list[index]
            if isinstance(content, Text) and content.text_level > 0 and "符号" in content.content.replace(" ", ""):
                text_level = content.text_level
                symbol_content = [content]
                symbol_children = get_symbol_child(index, text_level, content_list)
                symbol_content.extend(symbol_children)
                index += max(len(symbol_children), 1)
                symbol_script = "\n".join([term_item.to_md_script() for term_item in symbol_content])
                if symbol_script:
                    if exist_symbol_cache(state.spec_code, state.document.name, symbol_script):
                        cache_data = get_symbol(state.spec_code, state.document.name, symbol_script)
                        symbol_result = SymbolResult(**cache_data)
                    else:
                        symbol_result = role_term.ask(symbol_script)
                        cache_symbol(state.spec_code, state.document.name, symbol_script, symbol_result.model_dump())
                    if symbol_result:
                        for definition in symbol_result.definition:
                            state.document.symbol_list.append(Symbol(**definition.model_dump()))
            else:
                index += 1
    return {}