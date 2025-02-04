import sqlite3
from pysqlcipher3 import dbapi2 as sqlcipher
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import tkinter as tk
from tkinter import Toplevel, Label, Entry, Frame,Button, messagebox,filedialog
import json
import hashlib
import os
from pprint import pprint  # Permet d'afficher les données de façon lisible

DB_PASSWORD = "mon_mot_de_passe_securise"  # 🔒 Mot de passe pour SQLCipher

class Subscription:
    def __init__(self, root):
        """Initialise la base de données chiffrée avec SQLCipher et crée les tables"""
        self.conn = sqlcipher.connect("utils/subscription.db")
        self.conn.execute(f"PRAGMA key = '{DB_PASSWORD}';")  # 🔐 Déchiffrement obligatoire
        self.create_tables_once()  # Vérifie si les tables existent déjà et les crée si nécessaire

        self.root = root

    def create_tables_once(self):
        """Crée les tables USER et ARGUMENTS une seule fois si elles n'existent pas déjà"""
        # Vérifier si les tables existent déjà
        cursor = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
        if not cursor.fetchone():  # Si la table 'user' n'existe pas
            self.conn.execute('''CREATE TABLE IF NOT EXISTS user (
                phone TEXT PRIMARY KEY,
                email TEXT,
                UsageLimit INTEGER,
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
            # Insère un nouvel utilisateur dans la table USER
            self.conn.execute("INSERT INTO user (phone, email, UsageLimit, public, private) VALUES (?, ?, ?, ?, ?)",
                              (phone, email, 100, public_pem, private_pem))  # UsageLimit initialisé à 100
            self.conn.commit()
            messagebox.showinfo("Inscription", "Utilisateur inscrit avec succès!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Erreur", "Ce numéro est déjà inscrit!")

    def recharge(self, encrypted_message):
            """Déchiffre le message RSA et met à jour le quota d'abonnement de l'utilisateur"""
            # Recherche de la clé privée pour l'utilisateur
            cursor = self.conn.execute("SELECT private FROM user")
            row = cursor.fetchone()
            
            if row:
                try:
                    # Déchiffrement du message
                    decrypted_value = self.decrypt_message(row[0], encrypted_message)
                    
                    # Si le déchiffrement réussit, essayer de le décoder
                    if decrypted_value:
                        data = self.decode_message(decrypted_value)
                        
                        if data:
                            self.update_user_quota(data)
                except Exception as e:
                    
                    messagebox.showerror("Erreur", f"Échec du rechargement : {e}")
            else:
                messagebox.showerror("Erreur", "Utilisateur non trouvé")

    def decrypt_message(self, private_key_pem, encrypted_message):
        """Déchiffre le message RSA en utilisant la clé privée"""
        try:
            private_key = serialization.load_pem_private_key(
                private_key_pem.encode(),
                password=None
            )
            decrypted_value = private_key.decrypt(
                encrypted_message,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return decrypted_value
        except Exception as e:
            print(f"Erreur lors du déchiffrement : {e}")
            messagebox.showerror("Erreur", f"Erreur de déchiffrement : {e}")
            return None

    def decode_message(self, decrypted_value):
        """Décode la valeur déchiffrée en JSON"""
        try:
            decoded_value = decrypted_value.decode('utf-8')
            data = json.loads(decoded_value)
            return data
        except UnicodeDecodeError as e:
            print(f"Erreur de décodage UTF-8 : {e}")
            messagebox.showerror("Erreur", f"Erreur de décodage du message : {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Erreur de décodage JSON : {e}")
            messagebox.showerror("Erreur", f"Erreur de décodage JSON : {e}")
            return None

    def update_user_quota(self, data):
        """Met à jour le quota d'abonnement de l'utilisateur"""

        # Appel de la méthode pour stocker le message crypté après mise à jour
        if not self.store_encrypted_message(data):
            return
        
        try:
            new_usage_limit = int(data['limit'])
            self.conn.execute("UPDATE user SET UsageLimit = UsageLimit + ? WHERE phone = ?",
                              (new_usage_limit, data['phone']))
            self.conn.commit()

            # Affichage du message de succès
            messagebox.showinfo("Successfully", f"User: {data['phone']}\nEmail: {data['email']}\nNew quota: {new_usage_limit}")

            
        except Exception as e:
            messagebox.showerror("Erreur", f"Something went wrong: {e}")

    def store_encrypted_message(self, data):
        """Enregistre le message crypté dans la table 'arguments' après avoir vérifié le hash"""

        # Convertir le dictionnaire en chaîne JSON
        message_json = json.dumps(data, sort_keys=True)

        # Encoder la chaîne JSON en bytes
        message_bytes = message_json.encode('utf-8') 
        # Calcul du hash du message crypté pour éviter les doublons
        message_hash = hashlib.sha256(message_bytes).hexdigest()
        
        # Vérification si le hash existe déjà dans la table arguments
        cursor = self.conn.execute("SELECT encrypted_message_hash FROM arguments WHERE encrypted_message_hash = ?", (message_hash,))
        row = cursor.fetchone()
        
        
        if row:
            messagebox.showerror("Erreur", " do not use expired Artisan-Key!")
            return False
        else:
            # Enregistrement du message crypté dans la table arguments
            self.conn.execute("INSERT INTO arguments (encrypted_message_hash) VALUES (?)", (message_hash,))
            self.conn.commit()
            return True

    def show_user_info(self):
        """Affiche les informations de l'utilisateur dans une fenêtre Toplevel"""
        cursor = self.conn.execute("SELECT phone, email, public FROM user")
        row = cursor.fetchone()
        
        if row:
            # Création de la fenêtre Toplevel pour afficher les infos
            top = Toplevel(self.root)
            top.title("Informations Utilisateur")
            top.geometry("300x150")  # Taille fixe
            top.resizable(False, False)  # Désactiver le redimensionnement
                
            
            info_text = f"Numéro: {row[0]}\nEmail: {row[1]}"
            
            # Ajout d'un label pour afficher les informations
            Label(top, text=info_text).pack(padx=10, pady=10)
            
            # Fonction pour copier les informations dans le presse-papiers
            def copy_info(phone, email):
                """Copie le numéro de téléphone et l'email dans le presse-papiers"""
                top.clipboard_clear()
                top.clipboard_append(f"Numéro: {phone}, Email: {email}")
                

            # Ajout d'un bouton pour copier les informations
            Button(top, text="Copy Email et Numéro", command=lambda: copy_info(row[0], row[1])).pack(pady=5)
            
            # Fonction pour sauvegarder la clé publique dans un fichier à un emplacement spécifique
            def save_address():
                """Permet de sauvegarder la clé publique dans un fichier à un emplacement choisi"""
                filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
                if filepath:  # Si l'utilisateur a sélectionné un emplacement
                    with open(filepath, "w") as f:
                        f.write(row[2])  # Sauvegarde de la clé publique dans le fichier
                    messagebox.showinfo("Sauvegardé", f"Clé publique sauvegardée dans: {filepath}")
            
            # Ajout d'un bouton "Browse" pour choisir l'emplacement de sauvegarde
            Button(top, text="get your adress", command=save_address).pack(pady=5)
            

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
            root.title("Inscription Utilisateur")

            frame = Frame(root)
            frame.pack(padx=20, pady=20)

            # Labels et champs de saisie
            phone_label = tk.Label(frame, text="Numéro de téléphone")
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
                    messagebox.showerror("Erreur", "Tous les champs doivent être remplis.")

            submit_button = tk.Button(frame, text="S'inscrire", command=on_submit)
            submit_button.grid(row=2, columnspan=2, pady=10)

            root.mainloop()


    def is_user_registered(self):
        """Vérifie si un utilisateur est déjà inscrit dans la table USER"""
        cursor = self.conn.execute("SELECT COUNT(*) FROM user")
        row = cursor.fetchone()
        return row[0] > 0  # Retourne True si un utilisateur est enregistré, sinon False



    def getAllData(self):
        """
        Récupère tout le contenu des tables USER et TRANSACTIONS, puis affiche les données formatées.
        :return: Dictionnaire contenant les données des deux tables.
        """
        data = {}

        # Récupération de la table USER
        cursor = self.conn.execute("SELECT * FROM user")
        user_rows = cursor.fetchall()

        # Récupération de la table TRANSACTIONS (ou une autre table)
        cursor = self.conn.execute("SELECT * FROM arguments")
        transaction_rows = cursor.fetchall()

        # Récupérer les noms des colonnes pour structurer les données
        user_columns = [desc[0] for desc in cursor.description]
        transaction_columns = [desc[0] for desc in cursor.description]

        # Conversion en format dictionnaire (clé = nom de colonne)
        users = [dict(zip(user_columns, row)) for row in user_rows]
        transactions = [dict(zip(transaction_columns, row)) for row in transaction_rows]

        # Stocker les données formatées
        data["Users"] = users
        data["arguments"] = transactions

        # Afficher les données bien formatées
        pprint(data)


        


    def decrement_usage_limit(self, value):
        """Décrémente le quota d'abonnement de l'utilisateur en s'assurant que la valeur à décrémenter soit valide"""
        cursor = self.conn.execute("SELECT UsageLimit FROM user")
        row = cursor.fetchone()
        
        if row:
            if value < row[0]:
                # Décrémente la valeur du quota d'abonnement
                self.conn.execute("UPDATE user SET UsageLimit = UsageLimit - ? WHERE phone = ?", (value, row[0]))
                self.conn.commit()
                messagebox.showinfo("Décrémentation", f"Quota d'abonnement réduit de {value}")
            else:
                messagebox.showerror("Erreur", "La valeur à décrémenter est supérieure au quota actuel.")
        else:
            messagebox.showerror("Erreur", "Aucun utilisateur trouvé")

    def get_usage_limit(self):
        """Récupère la valeur du quota d'abonnement de l'utilisateur"""
        cursor = self.conn.execute("SELECT UsageLimit FROM user")
        row = cursor.fetchone()
        if row:
            return row[0]
        return 0  # Retourne 0 si aucun utilisateur n'est trouvé
    

# #utiliation de la classe
if __name__ == "__main__":

    root = tk.Tk()
    
    subscription = Subscription(root)
    subscription.show_user_info()
    print(subscription.get_usage_limit())

    root.mainloop()
