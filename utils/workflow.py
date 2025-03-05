import tkinter as tk
from tkinter import PhotoImage, Toplevel, Label, Entry, Button, StringVar, IntVar, ttk, messagebox
from PyPDF2 import PdfReader, PdfWriter
import os

# Import des classes et modules personnalisés
from utils.utils import *


class WorkflowConfig:
    def __init__(self, root, in_pdf):
        """
        Initialise la classe avec la fenêtre principale Tkinter.
        :param root: La fenêtre principale Tkinter.
        """
        self.root = root
        self.config = {
            "start": 1,
            "font_size": "12",
            "num_pages_to_duplicate": 50,
        }
        self.paths_to_duplicated_pages = []
        self.input_pdf_path = in_pdf  # Chemin d'exemple, à adapter
        self.pdf_path = self.input_pdf_path
        self.is_configurations_saved = False

    def duplicate_pdf_page(self, num_duplicates):
        """
        Duplication de la page PDF spécifiée.
        :param num_duplicates: Nombre de duplications souhaitées.
        """
        output_dir = "temp"
        self.paths_to_duplicated_pages = []
        self.pdf_path = self.input_pdf_path

        if not os.path.exists(self.pdf_path):
            messagebox.showerror("Erreur", f"{self.pdf_path} does not exist or was deleted")
            return

        # Crée le répertoire s'il n'existe pas
        os.makedirs(output_dir, exist_ok=True)

        # Vide le répertoire s'il contient des fichiers
        for file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de nettoyer le répertoire: {e}")
                return

        reader = PdfReader(self.pdf_path)

        if len(reader.pages) != 1:
            messagebox.showerror("Erreur", "The file must contain only 1 page")
            return

        for i in range(1, num_duplicates + 1):
            writer = PdfWriter()
            writer.add_page(reader.pages[0])
            output_path = os.path.join(output_dir, f"page_{i}.pdf")
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            self.paths_to_duplicated_pages.append(output_path)

    def open_config_window(self):
        """
        Ouvre une fenêtre de configuration simplifiée.
        """
        config_window = Toplevel(self.root)
        icon = PhotoImage(file="icons/icon0.png")  # Chargement de l'icône
        config_window.iconphoto(False, icon)  # Définir l'icône
        config_window.title("Configuration")
        config_window.geometry("300x200")
        config_window.resizable(False, False)
        config_window.attributes("-topmost", True)

        # Configuration du numéro de départ
        Label(config_window, text="Start:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        start_var = StringVar(value=self.config["start"])
        Entry(config_window, textvariable=start_var).grid(row=0, column=1, padx=10, pady=5)

        # Configuration de la taille de police
        Label(config_window, text="Font Size:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        font_size_var = StringVar(value=self.config["font_size"])
        Entry(config_window, textvariable=font_size_var).grid(row=1, column=1, padx=10, pady=5)

        # Configuration du nombre de duplications
        Label(config_window, text="Pages to duplicate:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        num_pages_var = IntVar(value=self.config["num_pages_to_duplicate"])
        Entry(config_window, textvariable=num_pages_var, width=5).grid(row=2, column=1, padx=10, pady=5, sticky="w")

        def save_configuration():
            """
            Enregistre la configuration et ferme la fenêtre si réussi.
            """
            try:
                self.config.update({
                    "start": int(start_var.get()),
                    "font_size": font_size_var.get(),
                    "num_pages_to_duplicate": num_pages_var.get(),
                })
                self.duplicate_pdf_page(self.config["num_pages_to_duplicate"])
                save_workflow_config(self.config, self.paths_to_duplicated_pages)
                config_window.destroy()
            except ValueError:
                messagebox.showerror("Erreur", "Invalid configuration values")

        def cancel_configuration():
            config_window.destroy()

        # Boutons d'action
        Button(config_window, text="Save", command=save_configuration).grid(row=3, column=0, padx=10, pady=10)
        Button(config_window, text="Cancel", command=cancel_configuration).grid(row=3, column=1, padx=10, pady=10)

    def get_workflow_config(self):
        """
        Retourne la configuration et les chemins vers les pages dupliquées si elle est sauvegardée.
        """
        if self.is_configurations_saved:
            return self.config, self.paths_to_duplicated_pages
