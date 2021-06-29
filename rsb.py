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
        return token

    # decoding the policy
    def decode(self, data):
        policy = jwt.decode(data, self.pk, algorithms=self.alg)
        return policy


policy = json.dumps([{
    'att': 'patient+thepatientid',
    'act': 'read'
}, {
    'att': 'doctor+thepatientdoctor',
    'act': 'write'
}])
# generating a private key
key = generateCipher.generate_key()
# encoding the policy
data = generateCipher(key).encode({"policy": policy})
print(data)
# generating the ciphertext
ct = generateCipher(key).encrypt(data)
print(ct)
# decoding the cipher text
pt = generateCipher(key).decrypt(ct)
print(pt)
# extracting the attribute policy out of the decoded ciphertext
po = generateCipher(key).decode(pt)
print(po)
