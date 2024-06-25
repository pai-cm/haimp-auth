import os

import pytest
from Crypto.PublicKey import RSA


def test_generate_private_key():
    """Crpyto를 활용해 공개키/개인키 생성 테스트
    """
    given_key_length = 2048

    # key pair 가 생성
    key_pair = RSA.generate(given_key_length)

    # Public Key 에 관련된 값 (n, e)
    assert hasattr(key_pair, "n")
    assert hasattr(key_pair, "e")

    # Private key 에 관련된 값 (N, d)
    assert hasattr(key_pair, "d")
    assert hasattr(key_pair, "p")
    assert hasattr(key_pair, "q")


def test_raise_error_if_length_is_under_1024():
    """ 1024 이하이면 에러가 발생 """
    given_key_length = 1023
    with pytest.raises(ValueError):
        RSA.generate(given_key_length)


def test_generate_public_key():
    """공개키 생성하기
    공개키에는 d, p, q가 존재하지 않음
    """
    given_key_length = 1024

    # key pair 가 생성
    # key pair 의 일부를 public key 에 주는 것
    # key_pair.d 는 있지만 public_key.d 는 없음
    key_pair = RSA.generate(given_key_length)

    public_key = key_pair.public_key()

    assert not hasattr(public_key, 'd')
    assert not hasattr(public_key, 'p')
    assert not hasattr(public_key, 'q')


def check_generate_key_double():
    """ 난수를 만드는 것이기 때문에 key pair0 과 1이 달라야함 """
    given_key_length = 1024

    key_pair0 = RSA.generate(given_key_length)
    key_pair1 = RSA.generate(given_key_length)

    assert key_pair0.n != key_pair1.n


def test_generate_private_key_pen_text():
    """ 프라이빗 키의 팸 텍스트 확인하기 """
    given_key_length = 1024

    key_pair = RSA.generate(given_key_length)
    text = key_pair.export_key()

    assert text.decode('utf-8').startswith('-----BEGIN RSA PRIVATE KEY-----\n')
    assert text.decode('utf-8').endswith('\n-----END RSA PRIVATE KEY-----')


def test_generate_public_key_pen_text():
    """ 프라이빗 키의 팸 텍스트 확인하기 """
    given_key_length = 1024

    key_pair = RSA.generate(given_key_length)

    public_key = key_pair.public_key()
    text = public_key.export_key()

    assert text.decode('utf-8').startswith('-----BEGIN PUBLIC KEY-----\n')
    assert text.decode('utf-8').endswith('\n-----END PUBLIC KEY-----')


def test_write_private_pem_file():
    given_private_key_path = 'private-key.pem'
    given_public_key_path = 'public_key.pem'

    given_key_length = 1024

    key_pair = RSA.generate(given_key_length)
    public_key = key_pair.public_key()

    with open(given_private_key_path, 'wb') as f:
        f.write(key_pair.export_key())

    with open(given_public_key_path, 'wb') as f:
        f.write(public_key.export_key())

    # 지워주도록
    os.remove(given_private_key_path)
    os.remove(given_public_key_path)
