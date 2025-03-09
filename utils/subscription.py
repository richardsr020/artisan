import sqlite3
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import tkinter as tk
from tkinter import PhotoImage, Toplevel, Label, Entry, Frame, Button, messagebox, filedialog
import json
import hashlib
from pprint import pprint
from utils.cipher import Cipher  # Importation de la classe Cipher

DB_NAME = "subscription.db"
ENCRYPTION_KEY = "your_secret_key"  # Clé de chiffrement pour la classe Cipher

class Subscription:
    def __init__(self, root):
        """Initialise la base de données SQLite et crée les tables"""
        self.conn = sqlite3.connect(DB_NAME)
        self.cipher = Cipher(ENCRYPTION_KEY)  # Initialisation de la classe Cipher
        self.create_tables_once()  # Crée les tables si elles n'existent pas déjà

        self.root = root

    def create_tables_once(self):
        """Crée les tables USER et ARGUMENTS une seule fois si elles n'existent pas déjà"""
        cursor = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
        if not cursor.fetchone():
            self.conn.execute('''CREATE TABLE IF NOT EXISTS user (
                phone TEXT PRIMARY KEY,
                email TEXT,
                ul TEXT,
                public TEXT,
                private TEXT
            )''')
        
        cursor = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='arguments'")
        if not cursor.fetchone():  # Si la table 'arguments' n'existe pas
            self.conn.execute('''CREATE TABLE IF NOT EXISTS arguments (
                encrypted_message_hash TEXT PRIMARY KEY,
                encrypted_message TEXT
            )''')

        self.conn.commit()

    def convert_private_key_to_pkcs8(self, private_key):
        """Convertit la clé privée en format PKCS#8 pour une meilleure gestion"""
        return private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

    def register_user(self, phone, email):
        """Génère une paire de clés RSA et enregistre un nouvel utilisateur dans la table USER"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()

        private_pem = self.convert_private_key_to_pkcs8(private_key).decode()
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

        try:
            # Chiffrement des données sensibles avant stockage
            encrypted_phone = self.cipher.encrypt(phone)
            encrypted_email = self.cipher.encrypt(email)
            encrypted_usage_limit = self.cipher.encrypt(str(0))  # ul initialisé à 100
            encrypted_public_pem = self.cipher.encrypt(public_pem)
            encrypted_private_pem = self.cipher.encrypt(private_pem)

            # Insère un nouvel utilisateur dans la table USER
            self.conn.execute("INSERT INTO user (phone, email, ul, public, private) VALUES (?, ?, ?, ?, ?)",
                              (encrypted_phone, encrypted_email, encrypted_usage_limit, encrypted_public_pem, encrypted_private_pem))
            self.conn.commit()
            messagebox.showinfo("Inscription", "Successfully registered!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Erreur", "Number allready used!")

    def recharge(self, encrypted_message):
        """Déchiffre le message RSA et met à jour le quota d'abonnement de l'utilisateur"""
        cursor = self.conn.execute("SELECT private FROM user")
        row = cursor.fetchone()
        
        if row:
            try:
                # Déchiffrement de la clé privée
                decrypted_private_key = self.cipher.decrypt(row[0])
                private_key = serialization.load_pem_private_key(
                    decrypted_private_key.encode(),
                    password=None
                )

                # Déchiffrement du message
                decrypted_value = private_key.decrypt(
                    encrypted_message,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )

                # Décodage du message déchiffré
                data = self.decode_message(decrypted_value)
                if data:
                    self.update_user_quota(data)
            except Exception as e:
                messagebox.showerror("Erreur", f"loading failed : {e}")
        else:
            messagebox.showerror("Erreur", "No user found")

    def decode_message(self, decrypted_value):
        """Décode la valeur déchiffrée en JSON"""
        try:
            decoded_value = decrypted_value.decode('utf-8')
            data = json.loads(decoded_value)
            return data
        except UnicodeDecodeError as e:
            
            messagebox.showerror("Erreur", f"Error when decode message : {e}")
            return None
        except json.JSONDecodeError as e:
           
            messagebox.showerror("Erreur", f"Erreur de décodage JSON : {e}")
            return None

    def update_user_quota(self, data):
        """Met à jour le quota d'abonnement de l'utilisateur"""
        if not self.store_encrypted_message(data):
            return
        
        try:
            new_usage_limit = int(data['limit'])
            cursor = self.conn.execute("SELECT phone, ul FROM user")
            row = cursor.fetchone()
            if row:
                encrypted_phone = row[0]
                encrypted_usage_limit = row[1]
                decrypted_phone = self.cipher.decrypt(encrypted_phone)
                decrypted_usage_limit = int(self.cipher.decrypt(encrypted_usage_limit))

                # Mise à jour du quota
                new_usage_limit_total = decrypted_usage_limit + new_usage_limit
                encrypted_new_usage_limit = self.cipher.encrypt(str(new_usage_limit_total))

                self.conn.execute("UPDATE user SET ul = ? WHERE phone = ?",
                                  (encrypted_new_usage_limit, encrypted_phone))
                self.conn.commit()
                messagebox.showinfo("Successfully", f"User: {decrypted_phone}\nNew quota: {new_usage_limit_total}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Something went wrong: {e}")

    def store_encrypted_message(self, data):
        """Enregistre le message crypté dans la table 'arguments' après avoir vérifié le hash"""
        message_json = json.dumps(data, sort_keys=True)
        message_bytes = message_json.encode('utf-8')
        message_hash = hashlib.sha256(message_bytes).hexdigest()
        
        cursor = self.conn.execute("SELECT encrypted_message_hash FROM arguments WHERE encrypted_message_hash = ?", (message_hash,))
        row = cursor.fetchone()
        
        if row:
            messagebox.showerror("Erreur", "Do not use expired Artisan-Key!")
            return False
        else:
            encrypted_message = self.cipher.encrypt(message_json)
            self.conn.execute("INSERT INTO arguments (encrypted_message_hash, encrypted_message) VALUES (?, ?)",
                              (message_hash, encrypted_message))
            self.conn.commit()
            return True

    def show_user_info(self):
        """Affiche les informations de l'utilisateur dans une fenêtre Toplevel"""
        cursor = self.conn.execute("SELECT phone, email, ul, public FROM user")
        row = cursor.fetchone()
        
        if row:
            # Déchiffrement des données
            decrypted_phone = self.cipher.decrypt(row[0])
            decrypted_email = self.cipher.decrypt(row[1])
            decrypted_usage_limit = self.cipher.decrypt(row[2])
            decrypted_public_key = self.cipher.decrypt(row[3])

            top = Toplevel(self.root)
            icon = PhotoImage(file="icons/icon0.png")  # Chargement de l'icône
            top.iconphoto(False, icon)  # Définir l'icône
            top.title("User Info")
            top.geometry("500x350")
            top.resizable(False, False)
                
            info_text = f"""Phone: {decrypted_phone}\nEmail: {decrypted_email}\nUsage_quota: {decrypted_usage_limit} pages\n\nUser_Address: \n XXXX-XXXX-XXXX-XXXX \n\nContact us to get new quota: \n Our website: linker.alwaysdata.net \nContactlinker@gmail.com \n Phone: +243 993 900 488 or +243 840149027 (WhatsApp)"""
            
            Label(top, text=info_text).pack(padx=10, pady=10)
            
            def copy_info(phone, email):
                top.clipboard_clear()
                top.clipboard_append(f"Numéro: {phone}, Email: {email}")
                
            Button(top, text="Copy all", command=lambda: copy_info(decrypted_phone, decrypted_email)).pack(pady=5)
            
            def save_address():
                filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
                if filepath:
                    with open(filepath, "w") as f:
                        f.write(decrypted_public_key)
                    messagebox.showinfo("Successfully", f"Saved Key: {filepath}")
            
            Button(top, text="Save Address", command=save_address).pack(pady=5)

    def check_and_show_window(self):
        """Vérifie si l'utilisateur a un compte, si oui, affiche les informations, sinon, l'invite à s'inscrire"""
        if self.is_user_registered():
            self.show_user_info()
        else:
            self.show_register_window()

    def show_register_window(self):
        """Fenêtre d'inscription utilisateur avec un formulaire"""
        if not self.is_user_registered():
            root = Toplevel(self.root)
            icon = PhotoImage(file="icons/icon0.png")  # Chargement de l'icône
            root.iconphoto(False, icon)  # Définir l'icône
            root.title("signUp")

            frame = Frame(root)
            frame.pack(padx=20, pady=20)

            phone_label = tk.Label(frame, text="Phone")
            phone_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
            phone_entry = tk.Entry(frame)
            phone_entry.grid(row=0, column=1, padx=10, pady=5)

            email_label = tk.Label(frame, text="Email")
            email_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
            email_entry = tk.Entry(frame)
            email_entry.grid(row=1, column=1, padx=10, pady=5)

            def on_submit():
                phone = phone_entry.get()
                email = email_entry.get()
                if phone and email:
                    self.register_user(phone, email)
                    root.destroy()
                else:
                    messagebox.showerror("Erreur", "all field must be fill.")

            submit_button = tk.Button(frame, text="S'inscrire", command=on_submit)
            submit_button.grid(row=2, columnspan=2, pady=10)

            root.mainloop()

    def is_user_registered(self):
        """Vérifie si un utilisateur est déjà inscrit dans la table USER"""
        cursor = self.conn.execute("SELECT COUNT(*) FROM user")
        row = cursor.fetchone()
        return row[0] > 0

    def getAllData(self):
        """
        Récupère tout le contenu des tables USER et ARGUMENTS, puis affiche les données formatées.
        """
        data = {}

        cursor = self.conn.execute("SELECT * FROM user")
        user_rows = cursor.fetchall()

        cursor = self.conn.execute("SELECT * FROM arguments")
        argument_rows = cursor.fetchall()

        user_columns = [desc[0] for desc in cursor.description]
        argument_columns = [desc[0] for desc in cursor.description]

        users = [dict(zip(user_columns, row)) for row in user_rows]
        arguments = [dict(zip(argument_columns, row)) for row in argument_rows]

        data["Users"] = users
        data["Arguments"] = arguments

        pprint(data)

    def decrement_usage_limit(self, value):
        """Décrémente le quota d'abonnement de l'utilisateur"""
        cursor = self.conn.execute("SELECT phone, ul FROM user")
        row = cursor.fetchone()
        
        if row:
            encrypted_phone = row[0]
            encrypted_usage_limit = row[1]
            decrypted_usage_limit = int(self.cipher.decrypt(encrypted_usage_limit))

            if value < decrypted_usage_limit:
                new_usage_limit = decrypted_usage_limit - value
                encrypted_new_usage_limit = self.cipher.encrypt(str(new_usage_limit))
                self.conn.execute("UPDATE user SET ul = ? WHERE phone = ?",
                                  (encrypted_new_usage_limit, encrypted_phone))
                self.conn.commit()
            else:
                remain_quota = self.get_usage_limit()
                messagebox.showerror("Erreur", f"You have {remain_quota} quota \n You don't have enough. Contact our support to add quota.")
                self.show_user_info()
        else:
            messagebox.showerror("Erreur", "Aucun utilisateur trouvé")

    def get_usage_limit(self):
        """Récupère la valeur du quota d'abonnement de l'utilisateur"""
        cursor = self.conn.execute("SELECT ul FROM user")
        row = cursor.fetchone()
        if row:
            return int(self.cipher.decrypt(row[0]))
        return 0

# # Utilisation de la classe
# if __name__ == "__main__":
#     root = tk.Tk()
#     subscription = Subscription(root)
#     subscription.decrement_usage_limit(1960)
#     root.mainloop()