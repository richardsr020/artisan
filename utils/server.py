from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from datetime import datetime
import json

class EncryptionService:
    def __init__(self):
        """Initialisation de la classe d'encryption"""
        pass

    def encrypt_message(self, public_key_pem, phone_number, email, limit):
        """
        Encrypte un message avec la clé publique de l'utilisateur, le numéro de téléphone,
        la limite et la date d'aujourd'hui, tout en formattant le message dans des accolades.

        Args:
        - public_key_pem (str): La clé publique de l'utilisateur en format PEM.
        - phone_number (str): Le numéro de téléphone de l'utilisateur.
        - limit (int): La limite à ajouter dans le message.

        Returns:
        - encrypted_message (bytes): Le message crypté.
        """
        # Récupère la clé publique de l'utilisateur
        public_key = serialization.load_pem_public_key(public_key_pem.encode())

        # Récupère la date d'aujourd'hui
        today_date = datetime.today().strftime('%Y-%m-%d')

        # Crée le message à chiffrer

        message = json.dumps({
            "phone": phone_number,
            "email": email,
            "limit": limit,
            "date": today_date
        })


        # Encrypte le message
        encrypted_message = public_key.encrypt(
            message.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        print(message)
        return encrypted_message


# Exemple d'utilisation de la classe
if __name__ == "__main__":
    # Exemple de clé publique PEM (pour une vraie utilisation, récupérer la clé publique d'un utilisateur)
    example_public_key_pem = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAjNCelYNQ6ndRgQfWwoHf
WKU6ciHEmZhmQpy/qUgc816PxOpbN1ah/lshlQkhWik37GJEH7OsAZbWNI+qxIHJ
q7ZwCwwf5sU6/dtg5Vuj4UHFJmQqpe9EeyEXwEV7U/jZG25QVmiLD7Z7AdXNTZjD
amaEwFc9/chf/P3JRMj1seN1IwSr+cxlGR2fZ/SEfv4kBRZ0mmT/BKo5HSDWgPeS
u4HQTfOBvgKiyyXh8v+s2w+j9LzXaXNCgjywFRMQxkiXfls7n/jnqrnh7A25Xj25
jk9MH2GrF5GyjDlwxRJ3Jovx9X3XEf3PiONS4V11q2GuvTPgMTTigAyJNczlfRmT
zwIDAQAB
-----END PUBLIC KEY-----
"""
    
    phone_number = "0840149027"
    limit = 100
    email = "richard@gmail.com"  # Placeholder, utiliser l'email de l'utilisateur

    # Initialisation du service d'encryption
    encryption_service = EncryptionService()

    # Encryption du message
    encrypted_message = encryption_service.encrypt_message(example_public_key_pem, phone_number, email, limit)

    # Affichage du message crypté (en bytes)
    with open ("cipherKey.bin","wb") as file:
        file.write(encrypted_message)
    # print(f"Message crypté : {encrypted_message}")
