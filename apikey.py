import secrets

# Genera una secret key de longitud 32 bytes
secret_key = secrets.token_hex(32)

print("Secret key generada:", secret_key)