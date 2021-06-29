import jwt
import json
policy = json.dumps([{
    'att': 'patient+thepatientid',
    'act': 'read'
}, {
    'att': 'doctor, thepatientdoctor',
    'act': 'write'
}])

# policies = json.loads(policy)

# for policy in policies:
#     print(policy)

#     att = policy['att'].split('+')

#     if 'patient' in att:
#         print("You can access that data")
#         print(f'You have an access to ${policy["act"]}')
#     else:
#         continue


secret_key = open('keypair.pem').read()
token = jwt.encode({'policy': policy}, secret_key,
                   algorithm='RS256')
print(token.split('.'))
# print(secret_key)

public_key = open('publickey.crt').read()
string = jwt.decode(token, public_key, algorithms='RS256')
print(string)
