import hashlib
from Crypto.Cipher import AES


def get_token(*p):
    base = ''.join(p)
    d = "0"
    for i in range(10000):
        h = hashlib.md5((base + (d := str(i))).encode()).hexdigest()
        if len(h.split("0")) - 1 > 4:
            break
    return "0." + d

def decrypt(response):
    basekey = "38s91"
    decryptkey = "f65nm"

    crypted_data, nonce = response[:-12], response[-12:]
    key = hashlib.sha256((basekey + decryptkey).encode()).digest()

    cipher = AES.new(key=key, mode=AES.MODE_GCM, nonce=nonce)
    decrypted_data = cipher.decrypt(crypted_data)

    # В plain_text присутствует какие-то лишние символы на конце, скорее всего паддинг для зашифровки. Не проверял.
    plain_text = decrypted_data.decode(errors="ignore")

    # Отрезаем лишние символы справа
    pt = plain_text[:plain_text.rfind("}") + 1]

    return pt