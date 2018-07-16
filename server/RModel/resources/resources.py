from functools import partial, wraps
import re

def register(req_t, path_s, require):
        Resources = ResourcesClass()
        path = Resources.path_re(path_s)
        
        if not path or not req_t in ('POST', 'GET'):
            raise ValueError
        
        def deco(func):
            @wraps(func)
            async def new_func(*args):
                await func(*args)
            Resources.resources_func[(req_t, path.group(1))] = (new_func, require)
            return new_func
        
        return deco

class WrongMethodError(ValueError):
    def __init__(self, code=405, message="Method not allowed"):
        self.message = message
        self.code = code

    def __repr__(self):
        return f"<{self.__class__.__name__} code={self.code} message='{self.message}'>"

    def __str__(self):
        return f"{self.__class__.__name__}: {self.message}"

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class ResourcesClass(metaclass=Singleton):
    resources_func = {}
    path_re = re.compile(r"(/.+)(/.*)")
    # /group1/group2

    def __getitem__(self, key: tuple) -> tuple:
        if not isinstance(key, tuple) or len(key) != 2:
            raise ValueError
        req_t = key[0]
        path = self.path_re.match(key[1])
        if not path or not req_t in ('POST', 'GET'):
            raise KeyError
        
        func, require = self.resources_func[(req_t, path.group(1))]
        if path.group(2):
            func = partial(func, path.group(2))

        return (func, require)
