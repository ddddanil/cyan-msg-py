import random

def gen_token(length=64):
    ALLOWED_TOKEN_CHARACTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    token = ''
    for _ in range(length):
        token += random.choice(ALLOWED_TOKEN_CHARACTERS)
    return token
