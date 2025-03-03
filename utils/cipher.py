from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256
import base64

class Cipher :
    def __init__(self, encryption_key):
        # Ensure the encryption key is 32 bytes long using SHA-256
        self.encryption_key = SHA256.new(encryption_key.encode('utf-8')).digest()

    # Function to encrypt data
    def encrypt(self, data):
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv)
        # We need to pad the data to make it a multiple of the block size
        # Using padding to ensure correct length
        data_padded = data + (AES.block_size - len(data) % AES.block_size) * chr(AES.block_size - len(data) % AES.block_size)
        encrypted_data = cipher.encrypt(data_padded.encode('utf-8'))
        # Return the IV and encrypted data encoded in base64 for storage
        return base64.b64encode(iv + encrypted_data).decode('utf-8')

    # Function to decrypt data
    def decrypt(self, encrypted_data):
        encrypted_data = base64.b64decode(encrypted_data.encode('utf-8'))
        iv = encrypted_data[:AES.block_size]
        cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv)
        data = cipher.decrypt(encrypted_data[AES.block_size:])
        # Remove the padding
        padding_length = data[-1]
        decrypted_data = data[:-padding_length].decode('utf-8')
        return decrypted_data

# Example usage
encryption_key = 'your_secret_key'  # Provide your secret key (will be hashed to 32 bytes)
secure_db = SecureDatabase(encryption_key)

# Encryption
data = "sensitive data"
encrypted_data = secure_db.encrypt(data)

# Example of inserting into the database (simulated here)
# INSERT INTO table (column) VALUES ('$encrypted_data')

# Decryption
decrypted_data = secure_db.decrypt(encrypted_data)
print(decrypted_data)  # Outputs "sensitive data"
