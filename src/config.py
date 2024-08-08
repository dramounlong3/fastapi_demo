


def _init(): 
    global _user_config_info 
    _user_config_info = {
    "first_key": {
        "inner1": None
    },
    "second_key": None,
}
def set_value(config): 
    _user_config_info = config
    
def get_value(): 
    return _user_config_info