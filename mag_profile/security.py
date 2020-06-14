from _sha256 import sha256

from werkzeug.security import generate_password_hash, check_password_hash



def hash_password(password):
    return generate_password_hash(password)

def check_password(password, db_password):
    return check_password_hash(db_password, password)

def check_key(key, db_key):
    return check_password_hash(db_key, key)

def encoded_key(key):
    enc_key = sha256(key.encode('ascii')).hexdigest()
    return enc_key
