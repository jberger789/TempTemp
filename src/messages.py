def format_message(message_type: str, auth_code: str|None = None, params: dict|None = None) -> str:
    param_str = ""
    if params is not None:
        for p in params:
            #TODO
            pass
    return f"{message_type}|{auth_code or ''}|{param_str}"

def unpack_param_str(param_str: str) -> dict:
    params = {}
    #TODO
    return params

def unformat_message(formatted_str: str) -> tuple[str, str|None, dict|None]:
    '''Returns a ValueError if not in correct format'''
    message_type,auth_code,ps = formatted_str.split('|')
    params = unpack_param_str(ps)

    return message_type, auth_code, params

