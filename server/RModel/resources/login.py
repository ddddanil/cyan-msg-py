from resources import register

@register('POST', '/login', ('USER', 'BIN'))
def login_post():
    # TODO check login and password, get id of this user
    data = json.loads(headers['BIN'].decode())
    # one time token for GET /login
    token = self.gen_token()
    await self.redis.set(f'token:{token}', 0)
    return {
        'USER': 'u000001',
        'USER-TOKEN': token,
    }

@register('GET', '/login', ('USER-TOKEN', ))
def login_get():
    token = self.gen_token()
    # 24 hours token
    print(token)
    await self.redis.set(f'token:{token}', 1, expire=86400)
    token_json = json.dumps({'TOKEN': token}).encode()
    return {
        'BIN': token_json
    }
