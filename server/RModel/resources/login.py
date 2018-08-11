import json
from RModel.utils import gen_token
import RModel.ResourceManager
from RModel.ResourceManager import register


@register('POST', '/login', ('USER', 'BIN', 'REDIS', 'DB'))
async def login_post(request, **kwargs):
    # TODO check login and password, get id of this user
    redis = kwargs['redis']
    data = json.loads(request['BIN'].decode())
    # one time token for GET /login
    token = gen_token()
    await redis.set(f'token:{token}', 0)
    return {
        'USER': 'u000001',
        'USER-TOKEN': token,
    }


@register('GET', '/login', ('USER-TOKEN', 'REDIS'))
async def login_get(request, **headers):
    token = gen_token()
    # 24 hours token
    print(token)
    redis = headers['redis']
    await redis.set(f'token:{token}', 1, expire=86400)
    token_json = json.dumps({'TOKEN': token}).encode()
    return {
        'BIN': token_json
    }