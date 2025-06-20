# utils.py
import os
import shutil
import json
from tkinter import messagebox


def clear_folder(folder_path):
    if not os.path.exists(folder_path):
        return

    if not os.listdir(folder_path):
        return

    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.unlink(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)
    
def smart_messagebox(parent, titre, message):
    """Centre une boîte de message au centre de la fenêtre parente."""

    parent.update_idletasks()  # Assure que la fenêtre parente a les bonnes dimensions

    largeur_parent = parent.winfo_width()
    hauteur_parent = parent.winfo_height()
    x_parent = parent.winfo_rootx()
    y_parent = parent.winfo_rooty()
    x_centre_parent = x_parent + largeur_parent // 2
    y_centre_parent = y_parent + hauteur_parent // 2

    # Estimation de la taille de la boîte de message (peut nécessiter des ajustements)
    largeur_messagebox = 300
    hauteur_messagebox = 150

    x_messagebox = x_centre_parent - largeur_messagebox // 2
    y_messagebox = y_centre_parent - hauteur_messagebox // 2

    # Création de la boîte de message
    messagebox.showinfo(titre, message, parent=parent)

    # Positionnement de la boîte de message
    # Malheureusement, messagebox.showinfo ne permet pas de modifier la géométrie après sa création.
    # Pour un contrôle total, il faut créer une fenêtre Toplevel personnalisée.
    # Ou utiliser une librairie comme CTkMessagebox qui le permet.    



def save_workflow_config(*collections):
    """
    Crée ou vide le fichier `workflow_config.json` pour y sauvegarder les collections fournies.

    :param collections: Une ou plusieurs collections Python (listes ou dictionnaires) à sauvegarder dans le fichier JSON.
    """
    file = "workflow_config.json"
    try:
        # Combine toutes les collections dans une seule liste pour les sauvegarder
        combined_data = list(collections)  # On regroupe toutes les collections dans une liste

        # Ouvre le fichier en mode écriture (cela vide son contenu s'il existe)
        with open(file, "w") as json_file:
            json.dump(combined_data, json_file, indent=4)  # Sauvegarde les données combinées dans le fichier JSON
        
    except Exception as e:
        messagebox.showerror("Erreur", "Json: somthing went wrong")


def read_workflow_config():
    """
    Lit le contenu du fichier `workflow_config.json` et retourne les données sous forme de dictionnaire ou de liste Python.

    :return: Le contenu du fichier sous forme de dictionnaire ou liste Python, ou None en cas d'erreur.
    """
    file = "workflow_config.json"
    try:
        # Vérifie si le fichier existe
        if not os.path.exists(file):
            print(f"The file '{file}' does not exist.")
            return None

        # Lit et charge le contenu du fichier JSON
        with open(file, "r") as json_file:
            data = json.load(json_file)
        
        return data
    except json.JSONDecodeError as e:
        messagebox.showerror("Erreur", "Json: somthing went wrong")
        return None
    except Exception as e:
        messagebox.showerror("Erreur", "Json: somthing went wrong")
        return None
