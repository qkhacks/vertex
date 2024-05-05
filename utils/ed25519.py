from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
import base64


def generate_ed25519_keys() -> (ed25519.Ed25519PrivateKey, ed25519.Ed25519PublicKey):
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key


def private_key_to_string(private_key: ed25519.Ed25519PrivateKey) -> str:
    return base64.urlsafe_b64encode(private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )).decode('utf-8')


def public_key_to_string(public_key: ed25519.Ed25519PublicKey) -> str:
    return base64.urlsafe_b64encode(public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )).decode('utf-8')


def string_to_private_key(private_key_str: str) -> ed25519.Ed25519PrivateKey:
    private_key_bytes = base64.urlsafe_b64decode(private_key_str.encode('utf-8'))
    return ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)


def string_to_public_key(public_key_str: str) -> ed25519.Ed25519PublicKey:
    public_key_bytes = base64.urlsafe_b64decode(public_key_str.encode('utf-8'))
    return ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
