import json
import random
from RModel.ResourceManager import register


@register('POST', '/login', ('USER', 'BIN'))
async def login_post(redis, **headers):
    # TODO check login and password, get id of this user
    data = json.loads(headers['BIN'].decode())
    # one time token for GET /login
    token = gen_token()
    await redis.set(f'token:{token}', 0)
    return {
        'USER': 'u000001',
        'USER-TOKEN': token,
    }


@register('GET', '/login', ('USER-TOKEN', ))
async def login_get(redis, **headers):
    token = gen_token()
    # 24 hours token
    print(token)
    await redis.set(f'token:{token}', 1, expire=86400)
    token_json = json.dumps({'TOKEN': token}).encode()
    return {
        'BIN': token_json
    }


def gen_token(length=64):
    ALLOWED_TOKEN_CHARACTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    token = ''
    for _ in range(length):
        token += random.choice(ALLOWED_TOKEN_CHARACTERS)
    return token