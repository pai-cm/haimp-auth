"""
암호화
encrypt (message, public key) -> encrypted value
decrypt (encrypted value, private key) -> message

서명 <- 부인방지
sign (message, private key) -> signature
verify (message, signature, public key) -> true false

jwt: header message signature (H.P.S)
base64 를 통해 h 와 p 는 나온다
"""
import json
from src.tokens.signature import sign_data_by_rsa, verify_data_by_rsa


def test_generate_signature_and_verify(given_private_pem_file, given_public_pem_file):
    given_payload = {
        "username": "pai-cm",
        "usergroup": "haimp-developer",
        "role": "admin",
    }
    given_message = json.dumps(given_payload).encode("utf-8")

    # 부인방지를 위해 signature
    # 시나리오 상 이걸 작업하는 곳은 auth server
    signature = sign_data_by_rsa(message=given_message, private_key_path=given_private_pem_file)

    # 검증하고 싶은 곳: api gateway
    assert verify_data_by_rsa(given_message, signature, given_public_pem_file) is True


def test_scenario1_client_is_thief(given_private_pem_file, given_public_pem_file):
    given_payload = {
        "username": "pai-cm",
        "usergroup": "haimp-developer",
        "role": "admin",
    }
    given_message = json.dumps(given_payload).encode("utf-8")

    # 거짓된 시그니처를 담아서 보내기
    signature = b'12122312ds2131231231212'

    # 검증하고 싶은 곳: api gateway
    assert verify_data_by_rsa(given_message, signature, given_public_pem_file) is False


def test_scenario2_client_is_thief(given_private_pem_file, given_public_pem_file):
    given_payload = {
        "username": "pai-cm",
        "usergroup": "haimp-developer",
        "role": "admin",
    }
    given_message = json.dumps(given_payload).encode("utf-8")

    # 부인방지를 위해 signature
    # 시나리오 상 이걸 작업하는 곳은 auth server
    signature = sign_data_by_rsa(message=given_message, private_key_path=given_private_pem_file)

    given_payload['username'] = 'sangjae'
    fraud_message = json.dumps(given_payload).encode('utf-8')

    # 검증하고 싶은 곳: api gateway
    assert verify_data_by_rsa(fraud_message, signature, given_public_pem_file) is False
