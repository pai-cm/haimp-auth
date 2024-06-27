import jwt
import pytest

from src.tokens.auth import load_pem
import json
import base64
from datetime import datetime
from jwt.exceptions import ExpiredSignatureError, InvalidAudienceError


def test_jwt_encode_and_decode(given_private_pem_file):
    given_payload = {
        "username": "pai-cm",
        "usergroup": "paip-developer",
        "role": "admin",
    }

    private_pem = load_pem(given_private_pem_file)

    jwt_token = jwt.encode(given_payload, private_pem, algorithm='RS256')
    header_b64, payload_b64, signature = jwt_token.split('.')

    # header 확인
    result_header = json.loads(base64.decodebytes(header_b64.encode('utf-8')))
    assert result_header['alg'] == 'RS256'
    assert result_header['typ'] == 'JWT'

    # payload 확인
    result_payload = json.loads(base64.decodebytes(payload_b64.encode('utf-8')))
    assert result_payload == given_payload


def test_verify_using_jwt(given_private_pem_file, given_public_pem_file):
    given_payload = {
        "username": "pai-cm",
        "usergroup": "paip-developer",
        "role": "admin",
    }

    private_pem = load_pem(given_private_pem_file)
    public_pem = load_pem(given_public_pem_file)
    jwt_token = jwt.encode(given_payload, private_pem, algorithm='RS256')

    output = jwt.decode(jwt_token, public_pem, algorithms=['RS256'])

    assert given_payload == output


def test_spec_exp_jwt_normal_case(given_private_pem_file, given_public_pem_file):
    given_payload = {
        "exp": datetime.now().timestamp() + 10,
        "username": "pai-cm",
        "usergroup": "paip-developer",
        "role": "admin",
    }

    private_pem = load_pem(given_private_pem_file)
    public_pem = load_pem(given_public_pem_file)
    jwt_token = jwt.encode(given_payload, private_pem, algorithm='RS256')

    output = jwt.decode(jwt_token, public_pem, algorithms=['RS256'])

    assert given_payload == output


def test_spec_exp_jwt_expired_case(given_private_pem_file, given_public_pem_file):
    given_payload = {
        "exp": datetime.now().timestamp() - 10,
        "username": "pai-cm",
        "usergroup": "paip-developer",
        "role": "admin",
    }

    private_pem = load_pem(given_private_pem_file)
    public_pem = load_pem(given_public_pem_file)
    jwt_token = jwt.encode(given_payload, private_pem, algorithm='RS256')

    with pytest.raises(ExpiredSignatureError):
        jwt.decode(jwt_token, public_pem, algorithms=['RS256'])


def test_skip_verify_decode(given_private_pem_file, given_public_pem_file):
    """
    만료가 되더라도 payload 확인하고 싶을 때, 이 코드 활용
    ex) 만료된 사람이 계속 요청할 때, 누가 요청 보내는지 확인하고 싶을 때 사용
    """
    given_payload = {
        "exp": datetime.now().timestamp() - 10,
        "username": "pai-cm",
        "usergroup": "paip-developer",
        "role": "admin",
    }

    private_pem = load_pem(given_private_pem_file)
    public_pem = load_pem(given_public_pem_file)
    jwt_token = jwt.encode(given_payload, private_pem, algorithm='RS256')

    output = jwt.decode(jwt_token, public_pem, algorithms=['RS256'], options={
        "verify_signature": False
    })

    assert given_payload == output


def test_spec_leeway(given_private_pem_file, given_public_pem_file):
    """ api 호출 될 때 10초까지는 봐주자 라는 활용 """
    given_payload = {
        "exp": datetime.now().timestamp() - 3,
        "username": "pai-cm",
        "usergroup": "paip-developer",
        "role": "admin",
    }

    private_pem = load_pem(given_private_pem_file)
    public_pem = load_pem(given_public_pem_file)
    jwt_token = jwt.encode(given_payload, private_pem, algorithm='RS256')

    output = jwt.decode(jwt_token, public_pem, algorithms=['RS256'], leeway=10)

    assert given_payload == output


def test_spec_audience(given_private_pem_file, given_public_pem_file):
    """
    sub -> subject 유저 객체

    aud 나를 위해 발급한거야? 지칭
    admin gateway
    client gateway 가 있을 때,
    하나의 auth 서버에서 aud 를 쓰면 된다
    """
    given_payload = {
        "aud": "paip-api-gateway",
        "username": "pai-cm",
        "usergroup": "paip-developer",
        "role": "admin",
    }

    private_pem = load_pem(given_private_pem_file)
    public_pem = load_pem(given_public_pem_file)
    jwt_token = jwt.encode(given_payload, private_pem, algorithm='RS256')

    # api gateway 에서 사용할 것
    output = jwt.decode(jwt_token, public_pem, algorithms=['RS256'], audience='paip-api-gateway')
    # output = jwt.decode(jwt_token, public_pem, algorithms=['RS256'], options={
    #     "verify_aud": False,
    # })
    assert given_payload == output

    with pytest.raises(InvalidAudienceError):
        jwt.decode(jwt_token, public_pem, algorithms=['RS256'])
