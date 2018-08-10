import sys
from os.path import dirname, abspath
from os import pardir

# same as 'network/../'
sys.path.append(abspath(dirname(__file__)) + '/' + pardir)
print(sys.path)


from RModel import run


if __name__ == '__main__':
    print('cool')
