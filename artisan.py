#dependences
import os
import re
import fitz  # PyMuPDF
import pikepdf
import platform
import subprocess
from PIL import Image, ImageTk
from tkinter import filedialog
from PyPDF2 import PdfReader, PdfMerger
from tkinter import Tk, Canvas, messagebox, PhotoImage, Button, Toplevel, Frame, CENTER


#dependences personalisés
from utils.utils import * 
from utils.drawer import * 
from utils.workflow import *
from utils.subscription import *
from utils.printers import *
from utils.pdf_viewer import *


class PDFCanvasRenderer:
    def __init__(self):
        """
        Initialise la classe avec le chemin du fichier PDF et ses attributs.

        Args:
            pdf_path (str): Le chemin du fichier PDF à afficher.
        """
        # Logique
        self.input_pdf_path = None #path du premier pdf
        self.pdf_path = None #le path du pdf qui chqnge en 'temp/' quand le pdf est chargé
        self.output_path = "out/"
        self.paths_to_duplicated_pages = []
        self.coordinates = []  # Liste pour stocker les coordonnées des clics
        self.merged_file_name = None # Nom du fichier finale fusioné
        self.merged_file_password = None # Mot de passe du fichier final fusioné
        
        # signatures de fonction apres execution de celle-ci
        self.is_file_loaded = False
        self.is_numbering_done = False
        self.is_merged_and_protect_pdfs = False
        

        # Graphique
        self.root = None  # Fenêtre principale Tkinter
        self.canvas = None  # Canevas pour afficher le PDF
        self.sidebar = None  # Sidebar pour les icônes
        self.icons = {}  # Dictionnaire pour stocker les icônes chargées



    ### initialisation des outils ###
        self.drawer = None   # attribut qui initialise l'objet Drawer
        self.workflow = None # attribut qui initialise l'objet workflowConfig
        self.wf_config_data = None
        self.drawer_config_data = None
        self.subscription = None 
        self.final_invoice_path = None # initalisation du path de la facture final
        self.final_invoice_password = None #initialiser le mot de passe de la facture final

        # Initialisation des outils

        self.init_subscription_()



    
    def launch_pdf_viewer(self):

        PDFViewer(self.root, self.merged_file_name, self.merged_file_password)




    

    def save_print_config(self):
        """Save PDF file path and password to printer.json
        Returns True if successful, False otherwise"""

        # Create config data
        config_data = {
            "file_path": self.final_invoice_path,
            "password": self.final_invoice_password
        }

        # Save to file
        try:
            with open("printer.json", "w") as f:
                json.dump(config_data, f, indent=4)
            return True
        except Exception as e:
            messagebox.showerror("Erreur", f"unable to save config")
            return False

       
    def launch_printer_exe(self):
        """lunch the printer .exe app""" 
        self.save_print_config()
        try:
            # Check OS
            if platform.system() == "Windows":
                subprocess.run("winPrinter_1.0.exe")
            else:
                messagebox.showerror("Erreur", "Unable to launch printer.exe")
        except Exception as e:
            messagebox.showerror("Erreur", f"Unable to launch printer.exe")



    
    
    def init_subscription_(self):
        """
        Initialise les composants graphiques pour la gestion des abonnements
        """
        self.subscription = Subscription(self.root)
        
    
   
   
   
    def create_subscriptionn(self):
                # Ouvrir la boîte de dialogue pour sélectionner un fichier .txt
        file_path = filedialog.askopenfilename()

        # Vérifier si un fichier a été sélectionné
        if file_path:
            try:
                # Lire le contenu du fichier et le stocker dans la variable `key`
                with open(file_path, "rb") as file:
                    key = file.read()
                    

                # Afficher un message de succès
                messagebox.showinfo("Succès", "Your key is ready click on OK !")

                # Lancer le reabonnement
                self.subscription.recharge(key)

            except Exception as e:
                messagebox.showerror("Erreur", f"unable to read the file: {e}")
        else:
            messagebox.showwarning("Annulation", "No file selected.")


    
    
    def get_user_subscription_status(self):
        self.subscription.check_and_show_window()
    
    
   
    def create_main_window(self):
        """
        Initialise la fenêtre principale et les composants graphiques.
        """
        self.root = Tk()
        self.root.title("Artisan ND")

        # Créer la barre latérale
        self.create_sidebar()

        """ Définir la largeur initiale seulement si le canvas n'est pas definit ce qui implique
            qu'aucun fichier n'est ouvert
        """
        if not self.canvas:
            # Définir la largeur initiale de la fenêtre à 1000 pixels, hauteur ajustée automatiquement
            self.root.geometry("600x750")  # Largeur initiale fixée à 1000px, hauteur ajustable

        # Démarrer la boucle principale
        self.root.mainloop()




    
    def load_icons(self):
        """
        Charge les icônes à partir du dossier 'icons' et les stocke dans un dictionnaire.
        """
        icon_names = ["icon0","icon1", "icon2", "icon3", "icon4", "icon5","icon6","icon7","icon8"]
        for icon_name in icon_names:
            icon_path = os.path.join("icons", f"{icon_name}.png")
            image = Image.open(icon_path)
            self.icons[icon_name] = ImageTk.PhotoImage(image.resize((30, 30)))

    
    
    
    
    
    def create_sidebar(self):
        """
        Crée une barre latérale à gauche de la fenêtre principale avec des icônes.
        """
        self.sidebar = Frame(self.root, bg="#A5A6A6", width=50)
        self.sidebar.pack(side="left", fill="y")

        # Charger les icônes
        self.load_icons()

        # Ajouter les boutons avec leurs icônes et commandes respectives
        Label(
            self.sidebar,
            image=self.icons["icon0"],
            bg="#A5A6A6", 
        ).pack(pady=5)


        Button(
            self.sidebar,
            image=self.icons["icon1"],
            command= self.render_pdf_to_canvas,
            bg="#A5A6A6",
            relief="flat",
            borderwidth=0,  # Supprime la bordure
            highlightthickness=0  # Supprime l'effet de focus
        ).pack(pady=5)

        Button(
            self.sidebar,
            image=self.icons["icon2"],
            command=self.reload_page,
            bg="#A5A6A6",
            relief="flat",
            borderwidth=0,  # Supprime la bordure
            highlightthickness=0  # Supprime l'effet de focus
        ).pack(pady=5)

        Button(
            self.sidebar,
            image=self.icons["icon3"],
            command=self.workflow_config,
            bg="#A5A6A6",
            relief="flat",
            borderwidth=0,  # Supprime la bordure
            highlightthickness=0  # Supprime l'effet de focus
        ).pack(pady=5)

        Button(
            self.sidebar,
            image=self.icons["icon4"],
            command = self.drawer_start,
            bg="#A5A6A6",
            relief="flat",
            borderwidth=0,  # Supprime la bordure
            highlightthickness=0  # Supprime l'effet de focus
        ).pack(pady=5)


        Button(
            self.sidebar,
            image=self.icons["icon5"],
            command= self.merge_and_protect_pdfs,
            bg="#A5A6A6",
            relief="flat",
            borderwidth=0,  # Supprime la bordure
            highlightthickness=0  # Supprime l'effet de focus
        ).pack(pady=5)

        Button(
            self.sidebar,
            image=self.icons["icon6"],
            command= self.launch_printer_exe,
            bg="#A5A6A6",
            relief="flat",
            borderwidth=0,  # Supprime la bordure
            highlightthickness=0  # Supprime l'effet de focus
        ).pack(pady=5)
        
        Button(
            self.sidebar,
            image=self.icons["icon7"],
            command= self.create_subscriptionn,
            bg="#A5A6A6",
            relief="flat",
            borderwidth=0,  # Supprime la bordure
            highlightthickness=0  # Supprime l'effet de focus
        ).pack(pady=5)
        
        Button(
            self.sidebar,
            image=self.icons["icon8"],
            command= self.get_user_subscription_status,
            bg="#A5A6A6",
            relief="flat",
            borderwidth=0,  # Supprime la bordure
            highlightthickness=0  # Supprime l'effet de focus
        ).pack(pady=5)

    
    
    
    def display_pdf_on_canvas(self, pdf_path):
        """
        Affiche un fichier PDF sur le canevas Tkinter.
        
        Args:
            pdf_path (str): Chemin du fichier PDF à afficher.
        """
        # Ouvrir le fichier PDF

        # verifier si le fichier exist


        if not os.path.exists(pdf_path):
            messagebox.showerror("Erreur", "The file does not exist")
            return
        
        if not pdf_path.lower().endswith('.pdf'):
            messagebox.showerror("Erreur", "Pdf file is required")
            return

        try:
                
            doc = fitz.open(pdf_path)
            page = doc[0]

            #verification si le pdf contien une page
            reader = PdfReader(self.pdf_path)
            if len(reader.pages) != 1:
                messagebox.showerror("Erreur", "The file must contain only 1 page")
                return
            #conversion pdf en pixel
            pix = page.get_pixmap()
            width, height = pix.width, pix.height

            # Calculer le ratio d'ajustement pour limiter la taille si nécessaire
            max_width, max_height = self.root.winfo_screenwidth() - 100, self.root.winfo_screenheight() - 100
            scale_factor = min(max_width / width, max_height / height, 1)

            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)

            # Créer ou réutiliser le canevas
            if not hasattr(self, "canvas") or self.canvas is None:
                self.canvas = Canvas(self.root, bg="white")
                self.canvas.pack(side="right", fill="both", expand=True)
                self.track_clicks()
            else:
                # Effacer tout contenu existant du canevas
                self.canvas.delete("all")

            # Redimensionner et centrer le canevas
            self.canvas.config(width=new_width, height=new_height)
            self.canvas.pack_propagate(False)
            self.canvas.place(relx=0.5, rely=0.5, anchor="center")

            # Redimensionner l'image PDF en utilisant get_pixmap() avec un facteur d'échelle
            pix_resized = page.get_pixmap(matrix=fitz.Matrix(scale_factor, scale_factor))

            img = PhotoImage(data=pix_resized.tobytes("ppm"))
            self.canvas.create_image(0, 0, image=img, anchor="nw")
            self.canvas.img = img  # Référence nécessaire pour éviter que l'image ne soit libérée

            # Ajuster la taille de la fenêtre principale
            self.root.geometry(f"{new_width + 100}x{new_height + 100}")

            self.is_file_loaded = True

        except Exception as e:
            messagebox.showerror("Erreur", f"Failed to open :'{pdf_path}'")
            return


    
    
    
    def reload_page (self):
        """
        Efface les coordonnées actuelles.
        """
        if not self.is_file_loaded:
        # Si le fichier n'est pas chargé, afficher un message d'erreur dans une boîte de dialogue
            messagebox.showerror("Erreur", "No file loaded")
            return
        
        self.coordinates = []

        # Vérifier si numeroteur a renvoyé sa signature pour charger un nouveau path
        if self.is_numbering_done:
            # Chemin du fichier page_1.pdf dans le dossier out_temp
            file_path = "out_temp/page_1.pdf"
            
            # Vérification si le fichier existe dans le dossier out_temp
            if os.path.exists(file_path):
                self.pdf_path = file_path  # chargement du nouveau chemin dans self.pdf_path
            else:
                self.pdf_path = "temp/page_1.pdf"
        
        # Afficher le fichier PDF sur le canevas
        self.display_pdf_on_canvas(self.pdf_path)


       

        
    
    
    def count_pdf_in_directory(self, directory):
        return sum(1 for file in os.listdir(directory) if file.endswith('.pdf'))


    
    
    
    def render_pdf_to_canvas(self):
        """
        Rendu de la première page du PDF sur le canevas Tkinter et ajustement des dimensions.
        """
        if not self.subscription.is_user_registered():
            self.subscription.show_register_window()
            return

        def select_file():
            """
            Ouvre une boîte de dialogue pour sélectionner un fichier PDF.
            """
            # Crée une fenêtre Toplevel temporaire
            file_explorer = Toplevel(self.root)
            file_explorer.title("Configuration")
            # Centrer la fenêtre de configuration
            file_explorer.geometry(f"300x200+{self.root.winfo_x() + 100}+{self.root.winfo_y() + 100}")
            
            try:
                # Ouvre l'explorateur de fichiers
                file_path = filedialog.askopenfilename(parent=file_explorer, title="Sélectionnez un PDF")
                
                # Retourne le chemin sélectionné ou None si aucun fichier n'est sélectionné
                return file_path if file_path else None
            finally:
                # Détruit la fenêtre Toplevel pour libérer les ressources
                file_explorer.destroy()
        
        # Ouvre une boîte de dialogue pour sélectionner un fichier
        self.pdf_path = select_file()
        if not self.pdf_path:
            return  # Sortir si aucun fichier n'est sélectionné
        
        self.input_pdf_path = self.pdf_path

        # Afficher le fichier PDF sur le canevas
        self.display_pdf_on_canvas(self.pdf_path)


    
    
    
    
    
    ### Partie logique ###
    def track_clicks(self):
        """
        Configure un gestionnaire d'événements pour suivre les clics sur le canevas
        et dessiner un cercle aux coordonnées cliquées.
        """
        def on_canvas_click(event):
            x, y = event.x, event.y
            self.coordinates.append((x, y))
            radius = 3
            self.canvas.create_oval(
                x - radius, y - radius, x + radius, y + radius, outline="red"
            )

        self.canvas.bind("<Button-1>", on_canvas_click)

    
    
    
    
    
    
    def workflow_config(self):

        if not self.is_file_loaded:
            # Si le fichier n'est pas chargé, afficher un message d'erreur dans une boîte de dialogue
            messagebox.showerror("Erreur", "No file loaded")
            return
        
        self.workflow = WorkflowConfig(self.root, self.input_pdf_path )
        self.workflow.open_config_window()


        
        



    def drawer_start(self):
        """
        Ouvre une fenêtre de configuration au centre de la fenêtre principale pour
        permettre à l'utilisateur de définir les attributs  `font_size`,
        `font_family`, `font_color`, `italic`, et `bold`.
        """
        if not self.coordinates:
            messagebox.showerror("Erreur", "Please marks before ")
            return
        
        self.drawer = Drawer(self.root, self.canvas, self.coordinates)
        
           # Appeler le méthode de numerotation du Drawer et vérifier le résultat
        if self.drawer.start_numbering():
            self.is_numbering_done = True
            self.reload_page()
        else:
            # Si False, afficher un message d'erreur dans une boîte de dialogue
            messagebox.showerror("Erreur", "Numbering Failed.")
      




    def clean_out_temp_folder(self):
        """
        Vide le contenu du dossier spécifié, en supprimant tous les fichiers et sous-dossiers.
        
        :param folder_path: Chemin du dossier à vider.
        """
        folder_path = "out_temp"  # par défaut, le dossier contenant les pages dupliquées sera vider

        # Vérifier si le dossier existe et supprimer tous les éléments s'il existe (fichiers et sous-dossiers)  # ATTENTION: cette action supprime tous les éléments du dossier, ce qui est dangereux en production!
        # Pour éviter ce risque, vous pouvez demander une confirmation à l'utilisateur avant de supprimer le dossier
        if os.path.exists(folder_path):
            # Lister tous les fichiers et sous-dossiers dans le dossier
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):  # Supprimer les fichiers
                    os.remove(file_path)

                elif os.path.isdir(file_path):  # Supprimer les sous-dossiers
                    shutil.rmtree(file_path)
                    
        else:
            messagebox.showerror("Erreur", "folder not found")

    


    def merge_and_protect_pdfs(self):
        """
        Fusionne tous les fichiers PDF d'un dossier en un seul fichier PDF,
        protège le fichier fusionné avec un mot de passe, et le stocke dans un dossier spécifié.
        
        :param input_folder: Chemin du dossier contenant les fichiers PDF.
        :param output_folder: Chemin du dossier où stocker le fichier fusionné.
        :param output_filename: Nom du fichier PDF fusionné.
        :param password: Mot de passe pour protéger le fichier PDF.
        """

        if not self.is_file_loaded:
            # Si le fichier n'est pas chargé, afficher un message d'erreur dans une boîte de dialogue
            messagebox.showerror("Erreur", "No file loaded")
            return



        # Fonction pour extraire le numéro de la page
        def extract_page_number(filename):
            match = re.search(r'page_(\d+)\.pdf', filename)
            return int(match.group(1)) if match else float('inf')  # Utiliser "inf" si pas de numéro


        input_folder="out_temp"
        output_folder="invoice"
        output_filename= os.path.basename(self.input_pdf_path) 
        self.merged_file_password="merged_file_password"
        # Construire le chemin du fichier final
        self.final_invoice_path = os.path.join(output_folder, output_filename)
        self.final_invoice_password = self.merged_file_password #initialiser le mot de passe de la facture final


        count_file_in_input_directory = self.count_pdf_in_directory(input_folder)

        if not count_file_in_input_directory :
            messagebox.showerror("Erreur", "launch numbering befor saving")
            return
        #decrementer le quota d'utilisation
        self.subscription.decrement_usage_limit(count_file_in_input_directory)


        # Vérifier si le dossier source existe
        if not os.path.exists(input_folder):
             messagebox.showerror("Erreur", "folder not found")
             return

        # Créer le dossier de sortie s'il n'existe pas
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Chemin complet pour le fichier fusionné
        temp_output_file = os.path.join(output_folder, "temp_" + output_filename)
        final_output_file = os.path.join(output_folder, output_filename)

        #initialiser l'attribut qui contiendra le path finale
        self.merged_file_name = final_output_file

        
        # Récupérer la liste des fichiers PDF dans le dossier
        pdf_files = [f for f in os.listdir("out_temp") if f.endswith('.pdf')]

        if not pdf_files:
             messagebox.showerror("Erreur", "file not found")
             return

        # Trier la liste en fonction du numéro extrait
        pdf_files_sorted = sorted(pdf_files, key=extract_page_number)

        # Fusionner les fichiers PDF
        merger = PdfMerger()
        try:

            for pdf_file in  pdf_files_sorted:
                file_path = os.path.join(input_folder, pdf_file)
                merger.append(file_path)
            
            # Écrire le fichier fusionné temporaire
            merger.write(temp_output_file)
            
        finally:
            merger.close()

        # Ajouter une protection par mot de passe avec pikepdf
        try:
            with pikepdf.Pdf.open(temp_output_file) as pdf:
                pdf.save(final_output_file, encryption=pikepdf.Encryption(owner=self.merged_file_password, user=self.merged_file_password))
                
                #signer la fusion comme etant faite
                self.is_merged_and_protect_pdfs = True
                self.clean_out_temp_folder()
             
                
        finally:

            # Supprimer le fichier temporaire
            os.remove(temp_output_file)

                            # Boîte de dialogue avec options
            preview = messagebox.askyesno("File saved successfuly", "Do you want to preview?")

            if preview:  
                self.launch_pdf_viewer()  # Lancer la prévisualisation si l'utilisateur clique sur "Yes"
                 

        
        

        

    def start(self):
        """
        Démarre l'application graphique.
        """
        self.create_main_window()


# Exemple d'utilisation
if __name__ == "__main__":
    renderer = PDFCanvasRenderer()
    renderer.start()
