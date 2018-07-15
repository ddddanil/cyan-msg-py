from functools import partial, wraps
import re

def register(req_t, path_s, require):
        path = Resources.path_re(path_s)
        if not path or not req_t in ['POST', 'GET']:
            raise ValueError
        
        def deco(func):
            @wraps(func)
            def new_func(*args):
                func(*args)
            Resources.resources_func[(req_t, path.group(1))] = (new_func, require)
            return new_func
        
        return deco

class WrongMethodError(ValueError):
    def __init__(self, code=400, message=None):
        self.message = message
        self.code = code

    def __repr__(self):
        return f"<{self.__class__.__name__} code={self.code} message='{self.message}'>"

    def __str__(self):
        return f"{self.__class__.__name__}: {self.message}"

class ResourcesClass():
    resources_func = {}
    path_re = re.compile(r"(/.+)(/.*)")
    # /group1/group2

    def __getitem__(self, key: tuple) -> tuple:
        if not isinstance(key, tuple) or len(key) != 2:
            raise ValueError
        req_t = key[0]
        path = self.path_re.match(key[1])
        if not path or not req_t in ['POST', 'GET']:
            raise KeyError
        
        func, require = self.resources_func[(req_t, path.group(1))]
        if path.group(2):
            func = partial(func, path.group(2))

        return (func, require)

Resources = ResourcesClass