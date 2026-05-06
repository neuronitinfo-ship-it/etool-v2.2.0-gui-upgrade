import base64
import json
from datetime import datetime, timedelta, timezone
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

PRIVATE_KEY_PEM = '''-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDPdlDp/JH5oj6x
PsFB9f1H1dMIwwd2AHCmlKJie1GwXrr0u/p+bc7yOj0j2J0PEGBJPcbcR5Hp6hd3
O3MhCHc5obdVq+SK8JLnCjBHch5TN2jSqA5W2jAq30NF03rvhxOUomEmop/4A405
BmZ5dZN2Se5XievFFr9zIEZcn8AIxY7D9spJPBL2vPTUbXMPXHtzfQC8+IohThDH
E0qcDVUPQEGZEXfI8SVTUFnpNNc2/fe/i5237zdkR5k7SZIIqkpsCLTu6XzIIiyn
p7SeHpeLQXpQ/USE0r7MugGMB1a6sLAnkAf0+xWkDscSqbeldRMH2x5F2upZOcJj
6wcax1TRAgMBAAECggEATyE8yZK5hvLYYLij8+nEmrK3FJ926A5Q6WjF6zRIOzJW
suRELhbqGUAXc+W6OjWv1B/JCtoNkJ/mJWc6iX32I7hH+lhfCpOqJI+hTI79fBYl
WDwbhAsi1idkPGzmdhgaYtXwolDjHTEVm4uSaH9tKHAYhbEoiXscuOe1jryr/WvU
uHyUIqgG0XXW7lwAWsEIh0AOThT4t4eFcUFP0RJYI+rszUSEQqBVhdN0nxQ1WqAN
hZ8vYXnstSX+brSvw3JVlKuX0cWGvZY4iRS09rl76kfkeKuQf0bfif56+K9z00kf
zZkA2I/edG8Y5P3mSx/1vOgbasttm5O4o1gJNqUOtQKBgQD4KAXyNtOKo97LW7vp
cy9DPRec8UyytuGOBRtbQm2Q07I1fxdzLXccYJLjDuNTjyITNAOf4sadld/1yflI
5rDc9vJkN1YDUhrOwj4utkmoFinl9C+64gWE7HP8Wiv5S61veoQGWs+JLns6JV79
Zqehz0ef7KavehPdlIcRODk8PwKBgQDWBQNC+kngKwCRinE3HpWgQq32twBqZIhg
oD8kOLzj8nErfSZBNAYiKRSNFL8SDSvYMoxVcyg68OZ9mBiO74EqHwngn4QQ/9XM
SIObZcN6T3UivZUGWvIGUrV0mN57utl6TmOiyxsKJZOT7lavtPP1//l2T2JfcWuN
a8mhNBpq7wKBgFPfAxN4IEstU3Gb0Yj3WzP4g/CRRYDpepZLd5GChBF82zBlggF1
jlpS8ZI4R/DH4ZZn8Amr1cERFJ634r8W6RPlissAQNvidhkHYYjcJ0zeIM8Nlsws
8/yXBiR2PYKGZ1nUKKcVLiuJQDDIzLAMb/+qVOTiUPvh4LD1MClLvVx1AoGARGo5
zrFf6E8W0W+mHW6jeiWWouWBNoGIrwrK5HNWvq+Dydkp33IX+9eSAD9/jO+08lnG
TpKPa7gSlleGkjqx2ZsudyXG/AAsgi80EvsG8BRyZ3afKvbro2XRJ8KubHMgjl58
r0+qByZX9NQd1fFMg3keb9mUotoI/Z5VSDj1sPUCgYAQ9yAfzMwwukrXm9eY/P5O
lOwk6vazliqjh+KBiwDmmHkRn2+6EYarmRFGi3PH7QY3g3lDgCcjDWn7ckVOIHPV
xxaMDPMcClHeREktNWZQecUDwzoSyt1TAxtxLGd4+YTE0bmhFlm0PRZb5CsTnNmt
qscBoJPvlIYw2b9SsgkFLw==
-----END PRIVATE KEY-----'''

PUBLIC_KEY_PEM = '''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAz3ZQ6fyR+aI+sT7BQfX9
R9XTCMMHdgBwppSiYntRsF669Lv6fm3O8jo9I9idDxBgST3G3EeR6eoXdztzIQh3
OaG3VavkivCS5wowR3IeUzdo0qgOVtowKt9DRdN674cTlKJhJqKf+AONOQZmeXWT
dknuV4nrxRa/cyBGXJ/ACMWOw/bKSTwS9rz01G1zD1x7c30AvPiKIU4QxxNKnA1V
D0BBmRF3yPElU1BZ6TTXNv33v4udt+83ZEeZO0mSCKpKbAi07ul8yCIsp6e0nh6X
i0F6UP1EhNK+zLoBjAdWurCwJ5AH9PsVpA7HEqm3pXUTB9seRdrqWTnCY+sHGsdU
0QIDAQAB
-----END PUBLIC KEY-----'''

# Note: Replace PRIVATE_KEY_PEM with your actual private key for signing.

from core.license_manager import verify_license


def create_test_license():
    key = RSA.import_key(PRIVATE_KEY_PEM)
    payload = {
        'user': 'Test User',
        'expiry': (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
        'features': ['android_frp', 'ios_passcode', 'ios_flashing', 'imei_repair'],
        'license_id': 'TEST-0001'
    }
    payload_bytes = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode('utf-8')
    signature = pkcs1_15.new(key).sign(SHA256.new(payload_bytes))
    token = {'payload': payload, 'signature': base64.b64encode(signature).decode('utf-8')}
    return base64.b64encode(json.dumps(token).encode('utf-8')).decode('utf-8')


if __name__ == '__main__':
    license_str = create_test_license()
    print('Generated license string:')
    print(license_str)
    print('\nVerification result:')
    result = verify_license(license_str)
    print(result)
