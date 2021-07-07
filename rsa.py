import jwt
import json
policy = ([{
    'att': 'patient+thepatientid',
    'act': 'read'
}, {
    'att': 'doctor, thepatientdoctor',
    'act': 'write'
}])

# policies = json.loads(policy)


def validate(policies, att1, att2):
    for policy in policies:
        print(policy)

        att = policy['att']
        act = policy['act']

        if att1 in att:
            print("You can access that data")
            print(f'You have an access to {policy["act"]}')
            if act == 'write':
                return 'rw'
            elif act == 'read':
                return 'r'
            else:
                return 'rw'
        elif att1 in att:
            print("You can access that data")
            print(f'You have an access to {policy["act"]}')
            if act == 'write':
                return 'rw'
            elif act == 'read':
                return 'r'
            else:
                return 'rw'
            continue
        else:
            return 'none'


action = validate(policy, 'patient+thepatientid', 'patient-thepatientid')
print(action)


# secret_key = open('keypair.pem').read()
# token = jwt.encode({'policy': policy}, secret_key,
#                    algorithm='RS256')
# print(token.split('.'))
# # print(secret_key)

# public_key = open('publickey.crt').read()
# string = jwt.decode(token, public_key, algorithms='RS256')
# print(string)
