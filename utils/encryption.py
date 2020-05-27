import os

from cryptography.fernet import Fernet


def to_binary(str):
    return f'{str}'.encode('utf-8')


key = to_binary(os.environ.get('ENCRYPTION_KEY'))
encryption_type = Fernet(key)


def encrypt(str):
    return encryption_type.encrypt(to_binary(str)).decode('ascii')


def decrypt(str):
    return encryption_type.decrypt(str.encode('ascii')).decode('ascii')
