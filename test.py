import tkinter as tk
from tkinter import filedialog, messagebox

# Ouvrir la boîte de dialogue pour sélectionner un fichier .txt
file_path = filedialog.askopenfilename(filetypes=[("Fichiers texte", "*.txt")])

# Vérifier si un fichier a été sélectionné
if file_path:
    try:
        # Lire le contenu du fichier et le stocker dans la variable `key`
        with open(file_path, "r", encoding="utf-8") as file:
            key = file.read()

        # Afficher un message de succès
        messagebox.showinfo("Succès", "Fichier chargé avec succès !")

        # Afficher le contenu dans la console
        print("Contenu du fichier :")
        print(key)

    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de lire le fichier : {e}")
else:
    messagebox.showwarning("Annulation", "Aucun fichier sélectionné.")
