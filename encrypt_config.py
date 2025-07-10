import os
import json
from cryptography.fernet import Fernet

def generate_key():
    key = Fernet.generate_key()
    with open("encryption.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    return open("encryption.key", "rb").read()

def encrypt_config(config_file, encrypted_file):
    if not os.path.exists("encryption.key"):
        generate_key()

    key = load_key()
    f = Fernet(key)

    with open(config_file, "rb") as file:
        config_data = file.read()

    encrypted_data = f.encrypt(config_data)

    with open(encrypted_file, "wb") as file:
        file.write(encrypted_data)

if __name__ == "__main__":
    config_file = "enhancer_config.json"
    encrypted_file = "encrypted_config.json"
    encrypt_config(config_file, encrypted_file)
    print(f"'{config_file}' encrypted to '{encrypted_file}'. Key stored in 'encryption.key'")