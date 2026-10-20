from datetime import date, time

SPECIAL_CHARS = ['|',';','_']

def format_message(message_type: str, auth_code: str|None = None, params: dict|None = None) -> str:
    return f"{message_type}|{auth_code or ''}|{format_params(params) or ''}"

def format_params(params: dict | None):
    if params is not None:
        return ';'.join([format_single_param(k,params[k]) for k in params.keys()])
    else:
        return None

def format_single_param(name: str, val: int | float | str | date | time | list | dict) -> str:
    fp = f"{name}_"
    if isinstance(val, int):
        fp += f"I_{str(val)}"
    elif isinstance(val, float):
        fp += f"F_{str(val)}"
    elif isinstance(val, str):
        fp += f"S_{val}"
    elif isinstance(val, date):
        fp += f"D_{val.strftime('%Y-%m-%d')}"
    elif isinstance(val, time):
        fp += f"T_{val.strftime('%H:%M')}"
    elif isinstance(val, list):
        fp += format_list(val)
    elif isinstance(val, dict):
        fp += format_dict(val)
    else:
        raise(TypeError(f"'{name}' has invalid parameter type '{type(val)}'"))
    return fp

def format_list(l: list) -> str:
    if len(l)==0:
        return "LS_()"
    else:
        rs = "L"
        if isinstance(l[0], int):
            rs += "I_"
        elif isinstance(l[0], float):
            rs += "F_"
        elif isinstance(l[0], str):
            rs += "S_"
        else:
            raise(TypeError(f"First value '{l[0]}' has invalid parameter type '{type(l[0])}'"))
        rs += '('+',,'.join([str(v) for v in l])+')'
        return rs

def format_dict(d: dict) -> str:
    rs = "MS_" # In practice, the only dicts we work with have string values so we don't need to check the type
    rs += '('+',,'.join([f"{k}->{d[k]}" for k in d.keys()])+')'
    return rs


def unpack_param_str(param_str: str) -> dict:
    params = {}
    #TODO
    return params

def unformat_message(formatted_str: str) -> tuple[str, str|None, dict|None]:
    '''Returns a ValueError if not in correct format'''
    message_type,auth_code,ps = formatted_str.split('|')
    params = unpack_param_str(ps)

    return message_type, auth_code, params

