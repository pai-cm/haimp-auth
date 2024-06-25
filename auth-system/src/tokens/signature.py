from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from src.tokens.auth import load_rsa_key


def load_sig_scheme(key_path: str):
    key = load_rsa_key(key_path)
    return pkcs1_15.new(key)


def sign_data_by_rsa(message: bytes, private_key_path: str) -> bytes:
    """
    서명하기
    """
    # hash A -> B 로 나오는데 A' 를 넣

    # RS256 HS256

    # hash (message, secrete) ->

    # sha 256 적용
    digest = SHA256.new(message)
    sig_scheme = load_sig_scheme(private_key_path)
    return sig_scheme.sign(digest)


def verify_data_by_rsa(message: bytes, signature, public_key_path: str) -> bool:
    """
    검증하기
    """
    digset = SHA256.new(message)
    sig_scheme = load_sig_scheme(public_key_path)

    try:
        sig_scheme.verify(digset, signature)
        return True
    except ValueError:
        return False
