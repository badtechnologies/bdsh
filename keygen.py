from paramiko import RSAKey

key = RSAKey.generate(bits=2048)

private_key_file = "server_rsa_key"
key.write_private_key_file(private_key_file)

public_key = key.get_base64()
print("Public Key:", public_key)