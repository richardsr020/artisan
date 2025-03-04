import hashlib
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256
import tkinter as tk
from tkinter import messagebox

class Cipher:
    def __init__(self, encryption_key):
        # Ensure the encryption key is 32 bytes long using SHA-256
        self.encryption_key = SHA256.new(encryption_key.encode('utf-8')).digest()

    # Function to encrypt data
    def encrypt(self, data):
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv)
        # We need to pad the data to make it a multiple of the block size
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

    # Method to calculate, verify and store the file hash
    def handle_file_hash(self, file_path, hash_file_path='hashes.txt'):
        hash_sha256 = hashlib.sha256()

        try:
            # Calculate the file hash
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):  # Read file in chunks
                    hash_sha256.update(chunk)
            file_hash = hash_sha256.hexdigest()

            # Check if the hash already exists in the hash text file
            with open(hash_file_path, 'r') as hash_file:
                hashes = hash_file.readlines()
                if file_hash + '\n' in hashes:
                    messagebox.showerror("Error", "Expired key was used")
                    return  # Exit if the hash is found

            # If the hash is not found, store it in the file
            with open(hash_file_path, 'a') as hash_file:
                hash_file.write(file_hash + '\n')
        except FileNotFoundError:
            messagebox.showerror("Error", "file not found")


        

# # Example usage
# encryption_key = 'your_secret_key'  # Provide your secret key (will be hashed to 32 bytes)
# secure_db = Cipher(encryption_key)

# # Encrypt and decrypt example
# data = "sensitive data"
# encrypted_data = secure_db.encrypt(data)
# decrypted_data = secure_db.decrypt(encrypted_data)
# print(decrypted_data)  # Outputs "sensitive data"

# # Handle file hash (calculate, verify and store if necessary)
# file_path = 'example_file.bin'  # Specify the path to your .bin file
# secure_db.handle_file_hash(file_path)
