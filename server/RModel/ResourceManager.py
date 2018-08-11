import resources
import functools
import re
from logging import getLogger

logger = getLogger("RModel.Resources")


class _TrieNode:

    def __init__(self, word: str, regex=False, finish=False, func=None):
        self.regex = regex
        if regex:
            self.word = re.compile(word)
        else:
            self.word = word
        self.children = []
        self.finish = finish
        self.func = func

    def __str__(self):
        return f"{self.word} re={self.regex} finish={self.finish} func={self.func}"


class _Trie:

    def __init__(self):
        self.GET_root = _TrieNode('/')
        self.POST_root = _TrieNode('/')

    def add(self, req_t: str, path: list, func, require: tuple):
        if req_t == 'GET':
            node = self.GET_root
        else:
            node = self.POST_root
        # path[('resource', 0), ('[0-9]+', 1)]
        # 1 means that this part is regex
        for i, j in enumerate(path):
            part, t = j
            cnt = 0
            for child in node.children:
                if (child.regex and child.word.match(part)) or child.word == path:
                    node = child
                    cnt += 1

            # create new node
            if cnt == 0:
                finish = (len(path) - 1 == i)
                regex = bool(t)
                f = (func, require) if finish else None
                new_node = _TrieNode(part, regex=regex, finish=finish, func=f)
                node.children.append(new_node)
                node = new_node

            elif cnt > 1:
                raise ValueError('more than one way accept this path')
        print(f'add {path}')

    def get(self, req_t: str, path: list):
        if req_t == 'GET':
            node = self.GET_root
        else:
            node = self.POST_root

        param = {}

        for part in path:
            cnt = 0
            for child in node.children:
                if child.regex and child.word.match(part):
                    param.update(child.word.match(part).groupdict())
                    node = child
                    cnt += 1

                elif not child.regex and part == child.word:
                    node = child
                    cnt += 1

            if cnt == 0:
                raise WrongMethodError
            elif cnt > 1:
                print('COLLISION')
        if not node.func:
            raise WrongMethodError

        return functools.partial(node.func[0], **param), node.func[1]


def register(req_t: str, path: str, require):
    """

    :param req_t: must be GET or POST
    :param path: must be str, without "/<>()" in regex and looks like
                 '/resource/<id: \d+>'
                 '/login'
                 'register'
                 regex: <name_of_parameter: regex>
    :param require: ('USER-TOKEN', 'TYPE'and etc...)
    :return: function that was given
    """
    resources = ResourceManager()
    path_re = resources.path_re.match(path)

    if not path_re or req_t not in ('POST', 'GET'):
        raise ValueError

    # parse path
    parts = []
    new_part = True
    part = ''
    regex = False

    for char in path[1:] + '/':
        if new_part and char == '<':
            regex = True
            new_part = False

        elif char == '/':
            if regex:
                part = part.strip()[:-1]
                name, r = part.split(':', maxsplit=1)
                name = name.strip()
                r = r.strip()
                r = f'(?P<{name}>{r})'
                parts.append((r, 1))
            else:
                parts.append((part, 0))
            new_part = True
            part = ''
            regex = False

        else:
            part += char

    # logger.debug(parts)

    def deco(func):
        resources.resources_func.add(req_t, parts, func, require)
        return func

    print(f"Added {req_t} -> {path}")

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


class ResourceManager(metaclass=Singleton):
    resources_func = _Trie()
    path_re = re.compile(r"(/[A-Za-z0-9]+)+")

    # /group1/group2

    def __getitem__(self, key: tuple) -> tuple:
        if len(key) != 2:
            raise ValueError
        req_t = key[0]
        path = self.path_re.match(key[1])
        if not path:
            raise KeyError("Malformed resource")
        if req_t not in ('POST', 'GET'):
            raise WrongMethodError
        func = require = None
        try:
            func, require = self.resources_func.get(req_t, path[0].split('/')[1:])
        except WrongMethodError:
            pass
        return func, require

