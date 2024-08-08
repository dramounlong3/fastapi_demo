import src.config as user_config



def svc():
    svc_config = user_config.get_value()
    print("user_config:", svc_config)
    svc_config["first_key"]["inner1"] = {"aaaaa":[1,2,3,4]}
    user_config.set_value(svc_config)
    print("user_config:", user_config.get_value())