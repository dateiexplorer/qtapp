def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in list(instances.keys()):
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance
