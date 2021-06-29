from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA512, SHA384, SHA256, SHA, MD5
from Crypto import Random
from base64 import b64encode, b64decode
hash = "SHA-256"


def newkeys(keysize):
    random_generator = Random.new().read
    key = RSA.generate(keysize, random_generator)
    private, public = key, key.publickey()
    return public, private


def importKey(externKey):
    return RSA.importKey(externKey)


def getpublickey(priv_key):
    return priv_key.publickey()


def encrypt(message, pub_key):
    # cipher = PKCS1_OAEP.new(pub_key)
    cipher = AES.new(pub_key, AES.MODE_CBC, Random.new().read(AES.block_size))
    return cipher.encrypt(message)


def decrypt(ciphertext, priv_key):
    # cipher = PKCS1_OAEP.new(priv_key)
    cipher = AES.new(priv_key, AES.MODE_CBC,
                     Random.new().read(AES.block_size))
    return cipher.decrypt(ciphertext)


# pk, sk = newkeys(1024)
# print(pk, sk)
sk = Random.get_random_bytes(16)


# npk = getpublickey(sk)
# print(npk)
data = b'tCu1dVvHOK7te5Z3ZGNDmnnfnCREKz3wLzBBi81xsg51_YuDznUTeba2UQuW3LcpOZHWc-al_qwtBKGlCrRLB1ZX2rHGjPpR7ZdUqyBLluK4rWYXXN6fbWqmmZF1AzKJR4nPl0oLSx9ffOyFL-1TSUcV6gpD22il8rS1xylXoNbhLXvMR63BTFVxXP1ne0Ooyp8vKuvjPO6woFMvojqSmDTjXEYHY_N8GOa4CDTrW_1lXkOYGVmPZh1q7loNGCu6aCP-i_E9Do5dDwAW5t8sadkGjCdBoXJh7yp_xvdOWj7xB1Odg_4Lt5FApvZMcyJWBWgYQLDy8SRuU1Q-TAaz-w'

length = 16 - (len(data) % 16)
data += bytes([length]) * length

ct = encrypt(data, sk)
print(ct)

msg = decrypt(ct, sk)
msg = msg[:-msg[-1]]
print(msg)
