#dependences
import os
import fitz  # PyMuPDF
from PyPDF2 import PdfReader, PdfWriter
from tkinter import Tk, Canvas, messagebox, PhotoImage, Button, Toplevel, Label, Entry, IntVar, Frame, CENTER
from PIL import Image, ImageTk
from tkinter import font, filedialog, IntVar, StringVar, BooleanVar,colorchooser, ttk

#dependences personalisés
from utils.utils import * 







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
        self.interval = {"start": 0, "end": 0}  # Intervalle pour numéroter les annotations
        self.num_pages_to_duplicate = 1  # Nombre de duplications de la page
        self.is_file_loaded = False
        self.font_settings = {}

        # Graphique
        self.root = None  # Fenêtre principale Tkinter
        self.canvas = None  # Canevas pour afficher le PDF
        self.sidebar = None  # Sidebar pour les icônes
        self.icons = {}  # Dictionnaire pour stocker les icônes chargées

    ### Partie graphique ###









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
        icon_names = ["icon1", "icon2", "icon3", "icon4", "icon5", "icon6"]
        for icon_name in icon_names:
            icon_path = os.path.join("icons", f"{icon_name}.png")
            image = Image.open(icon_path)
            self.icons[icon_name] = ImageTk.PhotoImage(image.resize((30, 30)))

    def create_sidebar(self):
        """
        Crée une barre latérale à gauche de la fenêtre principale avec des icônes.
        """
        self.sidebar = Frame(self.root, bg="#D3D4D4", width=40)
        self.sidebar.pack(side="left", fill="y")

        # Charger les icônes
        self.load_icons()

        # Ajouter les boutons avec leurs icônes et commandes respectives
        Button(
            self.sidebar,
            image=self.icons["icon1"],
            command= self.render_pdf_to_canvas,
            bg="#D3D3D3",
            relief="flat",
        ).pack(pady=5)

        Button(
            self.sidebar,
            image=self.icons["icon2"],
            command=self.reload_page,
            bg="#D3D3D3",
            relief="flat",
        ).pack(pady=5)

        Button(
            self.sidebar,
            image=self.icons["icon3"],
            command=self.config_and_duplicate,
            bg="#D3D3D3",
            relief="flat",
        ).pack(pady=5)

        Button(
            self.sidebar,
            image=self.icons["icon4"],
            command=self.config_and_numbering_page,
            bg="#D3D3D3",
            relief="flat",
        ).pack(pady=5)

        Button(
            self.sidebar,
            image=self.icons["icon5"],
            command= self.draw_number,
            bg="#D3D3D3",
            relief="flat",
        ).pack(pady=5)

        Button(
            self.sidebar,
            image=self.icons["icon6"],
            command= self.config_and_numbering_page,
            bg="#D3D3D3",
            relief="flat",
        ).pack(pady=5)
        

    
    
    
    
    
    def reload_page (self):
        """
        Efface les coordonnées actuelles.
        """
        
        self.coordinates = []

        # recharger la page
        doc = fitz.open(self.pdf_path)
        page = doc[0]
        pix = page.get_pixmap()
        width, height = pix.width, pix.height

        # Calculer le ratio d'ajustement pour limiter la taille si nécessaire
        max_width, max_height = self.root.winfo_screenwidth() - 100, self.root.winfo_screenheight() - 100
        scale_factor = min(max_width / width, max_height / height, 1)

        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)

        # Créer un canevas pour afficher le PDF et l'ajouter à la fenêtre principale
        self.canvas = Canvas(self.root, bg="white")
        self.canvas.pack(side="right", fill="both", expand=True)
        self.track_clicks()

        # Redimensionner le canevas
        self.canvas.config(width=new_width, height=new_height)
        self.canvas.pack_propagate(False)

        # Centrer le canevas
        self.canvas.place(relx=0.5, rely=0.5, anchor="center")

        # Redimensionner l'image PDF en utilisant get_pixmap() avec un facteur d'échelle
        pix_resized = page.get_pixmap(matrix=fitz.Matrix(scale_factor, scale_factor))

        img = PhotoImage(data=pix_resized.tobytes("ppm"))
        self.canvas.create_image(0, 0, image=img, anchor="nw")
        self.canvas.img = img

        # Ajuster la fenêtre principale
        self.root.geometry(f"{new_width + 100}x{new_height + 100}")

        
    
    
    
    
    
    
    def render_pdf_to_canvas(self):
        """
        Rendu de la première page du PDF sur le canevas Tkinter et ajustement des dimensions.
        """
        def select_file():
            """"""
            # Crée une fenêtre Toplevel temporaire
            file_explorer = Toplevel(self.root)
            file_explorer.title("Configuration")
            # Centrer la fenêtre de configuration
            file_explorer.geometry(f"300x200+{self.root.winfo_x() + 100}+{self.root.winfo_y() + 100}")
            
            try:
                # Ouvre l'explorateur de fichiers
                file_path = filedialog.askopenfilename(parent=file_explorer, title="Sélectionnez un pdf")
                
                # Affiche le chemin sélectionné ou un message si aucun fichier n'est sélectionné
                if file_path:
                    return file_path
                else:
                    return None
            finally:
                # Détruit la fenêtre Toplevel pour libérer les ressources
                file_explorer.destroy()
            
        # Ouvre une boîte de dialogue pour sélectionner un fichier
        self.pdf_path = select_file()
        self.input_pdf_path = self.pdf_path

        doc = fitz.open(self.pdf_path)
        page = doc[0]
        pix = page.get_pixmap()
        width, height = pix.width, pix.height

        # Calculer le ratio d'ajustement pour limiter la taille si nécessaire
        max_width, max_height = self.root.winfo_screenwidth() - 100, self.root.winfo_screenheight() - 100
        scale_factor = min(max_width / width, max_height / height, 1)

        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)

        # Créer un canevas pour afficher le PDF et l'ajouter à la fenêtre principale
        self.canvas = Canvas(self.root, bg="white")
        self.canvas.pack(side="right", fill="both", expand=True)
        self.track_clicks()

        # Redimensionner le canevas
        self.canvas.config(width=new_width, height=new_height)
        self.canvas.pack_propagate(False)

        # Centrer le canevas
        self.canvas.place(relx=0.5, rely=0.5, anchor="center")

        # Redimensionner l'image PDF en utilisant get_pixmap() avec un facteur d'échelle
        pix_resized = page.get_pixmap(matrix=fitz.Matrix(scale_factor, scale_factor))

        img = PhotoImage(data=pix_resized.tobytes("ppm"))
        self.canvas.create_image(0, 0, image=img, anchor="nw")
        self.canvas.img = img

        #marquer le fichier comme etant deja chqrgé
        if self.canvas:
            self.is_file_loaded = True

        # Ajuster la fenêtre principale
        self.root.geometry(f"{new_width + 100}x{new_height + 100}")


    
    
    
    
    
    
    ### Partie logique ###
    def track_clicks(self):
        """
        Configure un gestionnaire d'événements pour suivre les clics sur le canevas
        et dessiner un cercle aux coordonnées cliquées.
        """
        def on_canvas_click(event):
            x, y = event.x, event.y
            self.coordinates.append((x, y))
            radius = 2
            self.canvas.create_oval(
                x - radius, y - radius, x + radius, y + radius, outline="black"
            )
            print(f"Clic à : ({x}, {y})")
            print(f"Coordonnées enregistrées : {self.coordinates}")

        self.canvas.bind("<Button-1>", on_canvas_click)

    
    
    
    
    
    
    def config_and_duplicate (self):
        """
        Ouvre une fenêtre de configuration au centre de la fenêtre principale pour
        permettre à l'utilisateur de définir les attributs `interval` et `num_pages_to_duplicate`.
        """
        # verifier la presence d'un fichier ouvert
        if not self.is_file_loaded:
            messagebox.showerror("Erreur", "The file must be load before")
            return
        
        
        
        config_window = Toplevel(self.root)
        config_window.title("Duplicate_page")

        # Centrer la fenêtre de configuration
        config_window.geometry(f"250x80+{self.root.winfo_x() + 200}+{self.root.winfo_y() + 200}")
        
        num_pages_var = IntVar(value=self.num_pages_to_duplicate)

        Entry(config_window, textvariable=num_pages_var).grid(row=2, column=0, padx=5, pady=5 )
        Label(config_window, text="pages").grid(row=2, column=1, padx=5, pady=5)



        def duplicate_pdf_page(num_duplicates = 50):
            """
            Duplique une page PDF x fois et stocke les pages dupliquées dans un dossier temporaire.

            Args:
                self.pdf_path (str): Le chemin du fichier PDF source (doit contenir une seule page).
                output_dir (str): Le dossier où les fichiers dupliqués seront stockés (par défaut 'temp').
                num_duplicates (int): Nombre de duplications à effectuer (par défaut 10).

            Returns:
                list: Liste des chemins des fichiers PDF dupliqués.
            """
            output_dir = "temp"  # par défaut, les pages dupliquées seront stockées dans le dossier 'temp'

            if self.paths_to_duplicated_pages:
                self.paths_to_duplicated_pages = [] # vider la liste des path temporaires
                clear_folder("temp/") # clear le dossier temp
                self.pdf_path = self.input_pdf_path # rendre le path du pdf d'origine au self.pdf_path

            # Vérifie si le fichier d'entrée existe
            if not os.path.exists(self.pdf_path):
                messagebox.showerror("Erreur", f"{self.pdf_path} do not exist or deleted")
                return

            # Crée le dossier temporaire s'il n'existe pas
            os.makedirs(output_dir, exist_ok=True)

            # Lis le fichier PDF source
            reader = PdfReader(self.pdf_path)
            if len(reader.pages) != 1:
                messagebox.showerror("Erreur", "The file must contain 1 page ")
                return

            # Prépare la liste des chemins des fichiers dupliqués
            duplicated_files = []
            new_temp_path = output_dir + "/page_1.pdf"

            # Duplique la page et sauvegarde chaque copie
            for i in range(1, num_duplicates + 1):
                writer = PdfWriter()
                writer.add_page(reader.pages[0])  # Ajoute la page unique au nouvel objet PDF

                # Définit le chemin de sortie pour chaque duplication
                output_path = os.path.join(output_dir, f"page_{i}.pdf")
                with open(output_path, "wb") as output_file:
                    writer.write(output_file)

                duplicated_files.append(output_path)
            
            self.paths_to_duplicated_pages = duplicated_files
            # charcger la page_1 du pdf a partir du dossier temporaire pour travailler dessus
            self.pdf_path = new_temp_path
            # recharger la page avec le nouveau pdf du dossier temporaire
            self.reload_page



        def save_and_start_duplicate():
            # Exiger une valeure superieur à 1 pour dupliquer
            if num_pages_var.get() == 1 :
                messagebox.showerror("Erreur", "unable to duplicate once")
                return
            
            self.num_pages_to_duplicate = num_pages_var.get()

            duplicate_pdf_page(self.num_pages_to_duplicate)
            messagebox.showinfo("Succès", f"{self.num_pages_to_duplicate} pages duplicated")
            config_window.destroy()

        Button(config_window, text="Duplicate", command = save_and_start_duplicate).grid(row=3, column=0, columnspan=2, pady=10)


    
    
    
    
    def config_and_numbering_page(self):
        """
        Ouvre une fenêtre de configuration au centre de la fenêtre principale pour
        permettre à l'utilisateur de définir les attributs `interval`, `font_size`,
        `font_family`, `font_color`, `italic`, et `bold`.
        """
        # si le fichier est chargé
        if not self.is_file_loaded:
            messagebox.showerror("Erreur", "No file loaded")
            return
        
        # si les pages sont dejà dupliquées
        if not self.paths_to_duplicated_pages:
            messagebox.showerror("Erreur", "Duplicate page before")
            return
        # si les coodonees ont ete marquées
        if not self.coordinates :
            messagebox.showerror("Erreur", "Undifined number area")
            return
        
        

        config_window = Toplevel(self.root)
        config_window.title("Config interval")

        # Centrer la fenêtre de configuration
        config_window.geometry(f"400x400+{self.root.winfo_x() + 100}+{self.root.winfo_y() + 100}")

        # Variables pour les champs de configuration
        start_var = IntVar(value=self.interval.get("start", 0))
        end_var = IntVar(value=self.interval.get("end", 0))
        font_size_var = IntVar(value=12)
        font_family_var = StringVar(value="Arial")
        font_color_var = StringVar(value="#000000")  # Couleur par défaut : noir
        italic_var = BooleanVar(value=False)
        bold_var = BooleanVar(value=False)

        # Configuration de l'intervalle
        Label(config_window, text="Start:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        Entry(config_window, textvariable=start_var).grid(row=0, column=1, padx=5, pady=5)

        Label(config_window, text="End:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        Entry(config_window, textvariable=end_var).grid(row=1, column=1, padx=5, pady=5)

        # Taille de police
        Label(config_window, text="Font Size:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        Entry(config_window, textvariable=font_size_var).grid(row=2, column=1, padx=5, pady=5)

        # Liste déroulante pour le choix de la police
        Label(config_window, text="Font Family:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        font_choices = ["Arial", "Times New Roman", "Courier New", "Verdana", "Helvetica"]
        ttk.Combobox(config_window, textvariable=font_family_var, values=font_choices, state="readonly").grid(row=3, column=1, padx=5, pady=5)

        # Palette de couleurs pour la police
        Label(config_window, text="Font Color:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        color_display = Label(config_window, text="  ", bg=font_color_var.get(), relief="sunken", width=10)
        color_display.grid(row=4, column=1, padx=5, pady=5)

        def choose_color():
            color_code = colorchooser.askcolor(title="Choisissez une couleur")[0]
            if color_code:
                font_color_var.set(color_code)
                color_display.config(bg=color_code)

        Button(config_window, text="Choose", command=choose_color).grid(row=4, column=2, padx=5, pady=5)

        # Styles (Italic, Bold)
        Label(config_window, text="Styles:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        italic_check = ttk.Checkbutton(config_window, text="Italic", variable=italic_var)
        italic_check.grid(row=5, column=1, sticky="w")

        bold_check = ttk.Checkbutton(config_window, text="Bold", variable=bold_var)
        bold_check.grid(row=5, column=2, sticky="w")

        # Actions
        def save_configuration():
            self.interval = {"start": start_var.get(), "end": end_var.get()}
            self.font_settings = {
                "size": font_size_var.get(),
                "family": font_family_var.get(),
                "color": font_color_var.get(),
                "italic": italic_var.get(),
                "bold": bold_var.get(),
            }

            config_window.destroy()
          
            

        def cancel_configuration():
            config_window.destroy()

        Button(config_window, text="Save", command=save_configuration).grid(row=6, column=0, columnspan=2, pady=10)
        Button(config_window, text="Cancel", command=cancel_configuration).grid(row=6, column=2, columnspan=2, pady=10)
        

    
    
    
    
    
    def draw_number(self):
        pages_range = len(self.paths_to_duplicated_pages)
        print("drawer")
        
        def load_file(path):
            """
            Ouvre un fichier PDF avec PyMuPDF.
            
            :param file_path: Chemin du fichier PDF.
            :return: Document PDF ouvert.
            """
            try:
                doc = fitz.open(path)
                print(f"PDF '{path}' ouvert avec succès.")
                return doc
            except Exception as e:
                print(f"Erreur lors de l'ouverture du fichier PDF : {e}")
                raise


        def draw(doc, number, coordinates):
            """
            Ajoute un numéro sur une page PDF à des coordonnées spécifiées.
            
            :param doc: Document PDF ouvert.
            :param page_number: Numéro de la page (index 0).
            :param number: Numéro à ajouter.
            :param coordinates: Liste de 4 coordonnées [(x1, y1), (x2, y2), ...].
            """
            try:
                page = doc[0]  # Récupérer la page spécifiée
                for x, y in coordinates:
                    # Ajouter le texte à chaque coordonnée
                    page.insert_text((x, y), str(self.interval["start"]), fontsize= int(self.font_settings["size"]), color=self.font_settings["color"])
                    self.interval["start"] = self.interval["start"] + 1
                
            except Exception as e:
                raise

           
        
        def save_changes (doc, output_path):
            """
            Enregistre un fichier PDF modifié.
            
            :param doc: Document PDF ouvert et modifié.
            :param output_path: Chemin du fichier de sortie.
            """
            try:
                doc.save(output_path)
                print(f"PDF enregistré sous '{output_path}'.")
            except Exception as e:
                print(f"Erreur lors de l'enregistrement du fichier PDF : {e}")
                raise



        """
        Processus complet pour ouvrir, modifier, et enregistrer un fichier PDF.
        
        :param file_path: Chemin du fichier PDF source.
        :param output_path: Chemin du fichier PDF modifié.
        :param number: Numéro à ajouter.
        :param coordinates: Liste de 4 coordonnées [(x1, y1), (x2, y2), ...].
        """
        # Étape 1 : Ouvrir le fichier PDF

        for index, single_path in enumerate(self.paths_to_duplicated_pages):

            doc = load_file(single_path)
            
            # Étape 2 : Ajouter le numéro sur la première page
            draw(doc,self.interval["start"], self.coordinates)
            
            # Étape 3 : Enregistrer le PDF modifié
            pdf_out_path = self.output_path+"out_pdf"+ str(index)
            save_changes(doc,pdf_out_path)
            
            # Étape 4 : Fermer le document
            doc.close()
            print("Processus terminé avec succès.")
        
        self.reload_page



    def start(self):
        """
        Démarre l'application graphique.
        """
        self.create_main_window()


# Exemple d'utilisation
if __name__ == "__main__":
    renderer = PDFCanvasRenderer()
    renderer.start()
