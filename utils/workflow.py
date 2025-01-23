import tkinter as tk
from tkinter import Toplevel, Label, Entry, Button, StringVar, IntVar, ttk, messagebox, colorchooser
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
            "font_family": "Arial",
            "font_color": "#000000",
            "italic": False,
            "bold": False,
            "num_pages_to_duplicate": 50,
        }
        self.paths_to_duplicated_pages = []
        self.input_pdf_path = in_pdf # Chemin d'exemple, à adapter
        self.pdf_path = self.input_pdf_path

        #signature des methodes
        self.is_configurations_saved = False

    
    def hex_to_rgb(self, hex_color):
        """
        Convertit une couleur hexadécimale en tuple RGB.
        :param hex_color: Couleur en format hexadécimal (e.g. "#000000").
        :return: Tuple RGB correspondant (e.g. (0, 0, 0)).
        """
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

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
        Ouvre une fenêtre de configuration pour gérer les styles et la duplication de pages.
        """
        # Création de la fenêtre Toplevel
        config_window = Toplevel(self.root)
        config_window.title("Drawer & Duplicator Configuration")
        config_window.geometry("450x400")
        config_window.resizable(False, False)
         # S'assurer que la fenêtre principale reste en avant-plan
        config_window.attributes("-topmost", True)

        # Cadre pour les configurations de style
        style_frame = ttk.LabelFrame(config_window, text="Style Configuration")
        style_frame.pack(fill="x", padx=10, pady=10)

        # Configuration des numéros et disposition
        Label(style_frame, text="Start:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        start_var = StringVar(value=self.config["start"])
        Entry(style_frame, textvariable=start_var).grid(row=0, column=1, padx=5, pady=5)

        # Configuration des styles de police
        Label(style_frame, text="Font Size:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        font_size_var = StringVar(value=self.config["font_size"])
        Entry(style_frame, textvariable=font_size_var).grid(row=1, column=1, padx=5, pady=5)

        Label(style_frame, text="Font Family:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        font_choices = ["Courier", "Helvetica", "Times-Roman", "Symbol", "ZapfDingbats"]
        font_family_var = StringVar(value=self.config["font_family"])
        ttk.Combobox(style_frame, textvariable=font_family_var, values=font_choices, state="readonly").grid(row=2, column=1, padx=5, pady=5)

        Label(style_frame, text="Font Color:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        font_color_var = StringVar(value=self.config["font_color"])
        color_display = Label(style_frame, text="  ", bg=font_color_var.get(), relief="sunken", width=10)
        color_display.grid(row=3, column=1, padx=5, pady=5)

        def choose_color():
             
            color_code = colorchooser.askcolor(title="Choose a color", parent = config_window)[1]
            if color_code:
                font_color_var.set(color_code)
                color_display.config(bg=color_code)
            

        Button(style_frame, text="Choose", command=choose_color).grid(row=3, column=2, padx=5, pady=5)

        Label(style_frame, text="Styles:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        italic_var = tk.BooleanVar(value=self.config["italic"])
        ttk.Checkbutton(style_frame, text="Italic", variable=italic_var).grid(row=4, column=1, sticky="w")

        bold_var = tk.BooleanVar(value=self.config["bold"])
        ttk.Checkbutton(style_frame, text="Bold", variable=bold_var).grid(row=4, column=2, sticky="w")

        # Cadre pour la duplication des pages
        duplicate_frame = ttk.LabelFrame(config_window, text="Page Duplication")
        duplicate_frame.pack(fill="x", padx=10, pady=10)

        Label(duplicate_frame, text="Number of pages to duplicate:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        num_pages_var = IntVar(value=self.config["num_pages_to_duplicate"])
        Entry(duplicate_frame, textvariable=num_pages_var, width=5).grid(row=0, column=1, padx=5, pady=5, sticky="w")

        def save_configuration():
            """
            Enregistre la configuration et ferme la fenêtre si réussi.
            """
            try:
                # Mise à jour de la configuration
                self.config.update({
                    "start": int(start_var.get()),
                    "font_size": font_size_var.get(),
                    "font_family": font_family_var.get(),
                    "font_color": self.hex_to_rgb(font_color_var.get()),
                    "italic": italic_var.get(),
                    "bold": bold_var.get(),
                    "num_pages_to_duplicate": num_pages_var.get(),
                })
                
                # Logique d'utilisation après mise à jour
                self.duplicate_pdf_page(self.config["num_pages_to_duplicate"])

                save_workflow_config(self.config, self.paths_to_duplicated_pages)

                
                # Fermeture de la fenêtre de configuration
                config_window.destroy()
            except ValueError:
                messagebox.showerror("Erreur", "Invalid configuration values")
            
        

        def cancel_configuration():
            config_window.destroy()

        # Boutons d'action
        Button(config_window, text="Save Config", command=save_configuration).pack(side="left", padx=20, pady=10)
        Button(config_window, text="Cancel", command=cancel_configuration).pack(side="right", padx=20, pady=10)
        


    # def start(self):
    #     """
    #     Démarre le workflow : convertit la couleur en RGB et lance la duplication.
    #     :return: self.config, self.paths_to_duplicated_pages
    #     """
    #     self.open_config_window()




    def get_workflow_config(self):
        """
        Retourne la configuration et les chemins vers les pages dupliquées si elle est sauvegardée.
        :return: self.config, self.paths_to_duplicated_pages
        """

        if self.is_configurations_saved:
            
            return self.config, self.paths_to_duplicated_pages

        
