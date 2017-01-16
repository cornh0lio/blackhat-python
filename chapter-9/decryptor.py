import zlib
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

private_key = ""

# We instantiate our RSA class with the private key
rsakey = RSA.importKey(private_key)
rsakey = PKCS1_OAEP.new(rsakey)

chunk_size = 256
offset = 0
decrypted = ""
# Base64-decode our encoded blob from Tumblr
encrypted = base64.b64decode(encrypted)

# We then start our decytping-loop to rebuild our original string
while offset < len(encrypted):
    decrypted += rsakey.decrypt(encrypted[offset:offset+chunk_size])
    offset += chunk_size

# Now we can decompress to original
plaintext = zlib.decompress(decrypted)

print plaintext

