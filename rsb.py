# importing the required modules
from Crypto import Random
from Crypto.Cipher import AES
import jwt
import json


class generateCipher():

    # initializing the class
    def __init__(self, key):
        # defining the class attributes
        self.key = key
        self.IV = (16 * '\x00').encode('utf-8')
        self.mode = AES.MODE_CBC
        self.alg = 'RS256'
        self.sk = open('./keypair.pem').read()
        self.pk = open('./publickey.crt').read()

    def encrypt(self, data):
        # changing the data to bytes
        data = data.encode('utf-8')
        encryptor = AES.new(self.key, self.mode, IV=self.IV)
        # setting the data bytes to equal the key bytes
        length = 16 - (len(data) % 16)
        data += bytes([length]) * length
        # generating the ciphertext
        ciphertext = encryptor.encrypt(data)
        return ciphertext

    def decrypt(self, data):

        decryptor = AES.new(self.key, self.mode, IV=self.IV)
        # decrypting the data
        plaintext = decryptor.decrypt(data)
        # removing all paddings from the plain text
        plaintext = plaintext[:-plaintext[-1]]
        return plaintext

    @staticmethod
    def generate_key():
        return Random.get_random_bytes(16)

    # encoding the policy
    def encode(self, data):
        token = jwt.encode(data, self.sk, algorithm=self.alg)
        ct = self.encrypt(token)
        return ct

    # decoding the policy
    def decode(self, data):
        text = self.decrypt(data)
        policy = jwt.decode(text, self.pk, algorithms=self.alg)
        return policy

    # validating the user's access
    @staticmethod
    def validate(policies, att1, att2):

        for policy in policies:

            att = policy['att']
            act = policy['act']

            if att1 in att:
                # print("You can access that data")
                # print(f'You have an access to {policy["act"]}')
                if act == 'write':
                    return 'rw'
                elif act == 'read':
                    return 'r'
                else:
                    return 'rw'
            elif att2 in att:
                # print("You can access that data")
                # print(f'You have an access to {policy["act"]}')
                if act == 'write':
                    return 'rw'
                elif act == 'read':
                    return 'r'
                else:
                    return 'rw'
            else:
                continue

            return None


# policy = json.dumps([{
#     'att': 'patient+thepatientid',
#     'act': 'read'
# }, {
#     'att': 'doctor+thepatientdoctor',
#     'act': 'write'
# }])
# # generating a private key
# key = b'\xdd\x92\xff,\xe5\xff\x06U|y\xb2\xa9\x1c\x11u\x95'
# generateCipher = generateCipher(key)

# # encoding the policy
# data = generateCipher.encode({"policy": policy})
# print(data)
# # extracting the attribute policy out of the decoded ciphertext
# po = generateCipher.decode(data)
# print(po)
# print(type(po['policy']))
