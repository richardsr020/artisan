import tkinter as tk
from PyPDF2 import PdfReader
import fitz  # PyMuPDF
import os
from PIL import ImageGrab
from reportlab.pdfgen import canvas
from tkinter import Toplevel, IntVar, Canvas, PhotoImage, StringVar, BooleanVar, messagebox, colorchooser, Label, Entry, Button, ttk

class Drawer:
    def __init__(self, root, canvas, coordinates, paths_to_duplicated_pages):
        self.root = root
        self.canvas = canvas
        self.coordinates = coordinates
        self.projected_coordinates = None
        self.paths_to_duplicated_pages = paths_to_duplicated_pages

        # Déclaration des attributs de classe
        self.config = {}
        self.out_temp = "out_temp"
        self.is_loaded_file = False
    def project_canvas_coords_to_pdf_points(self, screen_dpi=96):
        """
        Projects coordinates from a canvas (which already has a PDF) onto a new 
        coordinate in point for new PDF file.
        
        Args:
            canvas (object): A canvas object that already has the PDF drawn on it.
            pdf_copy_path (str): Path to the copied PDF file to which we want to project the coordinates.
            coords_on_canvas (list): List of coordinates [(x1, y1), (x2, y2), ...] on the canvas in pixels.
            screen_dpi (int): Screen DPI (default 96 for standard screens).
        
        Returns:
            list: New coordinates projected onto the PDF in points.
        """
        canvas = self.canvas
        pdf_copy_path = self.paths_to_duplicated_pages[0]
        coords_on_canvas = self.coordinates  # Coordinates on the canvas in pixels

        # Get the canvas dimensions in point
        # point = (pixel/DPI)*72
        canvas_width_in_point = (canvas.winfo_width()/96) * 72  # Canvas width in pixels
        canvas_height_in_point =  (canvas.winfo_height()/96) * 72  # Canvas height in pixels


        print("canvas size :")
        print(canvas_width_in_point)
        print(canvas_height_in_point)

        # Open the PDF file with fitz
        pdf_document = fitz.open(pdf_copy_path)

        # Get the first page (assuming one-page PDF for simplicity)
        page = pdf_document[0]

        # Get the dimensions of the PDF page in points (1 point = 1/72 inch)
        pdf_width, pdf_height = page.rect.width, page.rect.height

        print("pdf size :")
        print(pdf_width)
        print(pdf_height)

        # Scale factors between the canvas size and the PDF page size
        scale_x = pdf_width / canvas_width_in_point
        scale_y = pdf_height / canvas_height_in_point


        # Initialize a list to store the new coordinates after projection
        projected_coords = []

        # Project each coordinate
        for (x, y) in coords_on_canvas:
            # Project the canvas coordinates to PDF space and convert to points
            # on convertis chaque pixel en poit via (pixel/96)*72 multiplier par le facteur de scaling
            pdf_x = ((x/96)*72)* scale_x 
            pdf_y = ((y/96)*72)* scale_y

            # Add the projected coordinates to the new list
            projected_coords.append((pdf_x, pdf_y))

        # Return the new projected coordinates
        self.projected_coordinates = projected_coords
    


    def open(self):
        """
        Ouvre une fenêtre de configuration au centre de la fenêtre principale pour
        permettre à l'utilisateur de définir divers attributs de style et d'intervalle.
        """

        # Vérifications initiales
        if not self.paths_to_duplicated_pages:
            messagebox.showerror("Erreur", "Duplicate page before")
            return

        if not self.coordinates:
            messagebox.showerror("Erreur", "Undefined number area")
            return

        # Création de la fenêtre de configuration
        config_window = Toplevel(self.root)
        config_window.title("Config interval")

        # Centrer la fenêtre de configuration
        config_window.geometry(f"400x400+{self.root.winfo_x() + 100}+{self.root.winfo_y() + 100}")

        # Valeurs par défaut
        default_config = {
            "start": "1",  # Numéro de départ par défaut
            "font_size": "12",  # Taille de police par défaut
            "font_family": "Arial",  # Famille de police par défaut
            "font_color": "#000000",  # Couleur de police par défaut
            "italic": False,  # Style italique par défaut
            "bold": False,  # Style gras par défaut
        }

        # Initialiser le dictionnaire de configuration
        self.config = default_config.copy()

        # Configuration des numéros et disposition
        Label(config_window, text="Start:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        start_var = StringVar(value=self.config["start"])
        Entry(config_window, textvariable=start_var).grid(row=0, column=1, padx=5, pady=5)

        # Configuration des styles de police
        Label(config_window, text="Font Size:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        font_size_var = StringVar(value=self.config["font_size"])
        Entry(config_window, textvariable=font_size_var).grid(row=1, column=1, padx=5, pady=5)

        Label(config_window, text="Font Family:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        font_choices = ["Courier","Helvetica", "Times-Roman", "Symbol", "ZapfDingbats"]
        font_family_var = StringVar(value=self.config["font_family"])
        ttk.Combobox(config_window, textvariable=font_family_var, values=font_choices, state="readonly").grid(row=2, column=1, padx=5, pady=5)

        Label(config_window, text="Font Color:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        font_color_var = StringVar(value=self.config["font_color"])
        color_display = Label(config_window, text="  ", bg=font_color_var.get(), relief="sunken", width=10)
        color_display.grid(row=3, column=1, padx=5, pady=5)

        def choose_color():
            color_code = colorchooser.askcolor(title="Choisissez une couleur")[1]
            if color_code:
                font_color_var.set(color_code)
                color_display.config(bg=color_code)

        Button(config_window, text="Choose", command=choose_color).grid(row=3, column=2, padx=5, pady=5)

        Label(config_window, text="Styles:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        italic_var = BooleanVar(value=self.config["italic"])
        ttk.Checkbutton(config_window, text="Italic", variable=italic_var).grid(row=4, column=1, sticky="w")

        bold_var = BooleanVar(value=self.config["bold"])
        ttk.Checkbutton(config_window, text="Bold", variable=bold_var).grid(row=4, column=2, sticky="w")

        # Actions
        def save_configuration():
            self.config.update({
                "start": int(start_var.get()),
                "font_size": font_size_var.get(),
                "font_family": font_family_var.get(),
                "font_color": font_color_var.get(),
                "italic": italic_var.get(),
                "bold": bold_var.get(),
            })
            config_window.destroy()

        def cancel_configuration():
            config_window.destroy()

        Button(config_window, text="Save", command=save_configuration).grid(row=5, column=0, columnspan=2, pady=10)
        Button(config_window, text="Cancel", command=cancel_configuration).grid(row=5, column=2, columnspan=2, pady=10)


    
    def open_pdf(self, path):
        """
        Rendu de la première page du PDF sur le canevas Tkinter et ajustement des dimensions.
        """
        doc = fitz.open(path)
        return doc
        
    def save_canvas_to_pdf(self,path):
        """
        Enregistre le contenu d'un Canvas Tkinter en tant qu'image PNG dans 'png_temp',
        puis en tant que PDF dans 'out_temp'.
        
        Args:
            tk_canvas (Canvas): Le Canvas Tkinter contenant les dessins.
            path (str): Chemin où le PDF sera sauvegardé.
        """
        # Extraire le nom du fichier depuis le chemin
        tk_canvas = self.canvas
        file_name = os.path.basename(path)
        file_name_without_ext = os.path.splitext(file_name)[0]  # Nom sans extension

        # Dossiers de sortie pour PNG et PDF
        png_temp_dir = "png_temp"
        pdf_temp_dir = "out_temp"
        os.makedirs(png_temp_dir, exist_ok=True)
        os.makedirs(pdf_temp_dir, exist_ok=True)

        # Chemins de sauvegarde
        png_path = os.path.join(png_temp_dir, f"{file_name_without_ext}.png")
        pdf_path = os.path.join(pdf_temp_dir, f"{file_name_without_ext}.pdf")

        # Obtenir la région de dessin du Canvas Tkinter
        x0 = tk_canvas.winfo_rootx()
        y0 = tk_canvas.winfo_rooty()
        x1 = x0 + tk_canvas.winfo_width()
        y1 = y0 + tk_canvas.winfo_height()

        # Capturer l'image du Canvas
        image = ImageGrab.grab(bbox=(x0, y0, x1, y1))
        image.save(png_path, "PNG")  # Sauvegarder l'image dans png_temp
        print(f"Image PNG sauvegardée dans : {png_path}")

        # Créer un PDF avec les mêmes dimensions que le Canvas Tkinter
        pdf_canvas = canvas.Canvas(pdf_path, pagesize=(image.width, image.height))

        # Ajouter l'image dans le PDF avec les bonnes dimensions
        pdf_canvas.drawImage(png_path, 0, 0, width=image.width, height=image.height)

        # Finaliser le PDF
        pdf_canvas.save()

        print(f"PDF sauvegardé dans : {pdf_path}")



    def one_per_page(self):
        
        # Récupérer les paramètres de style
        font_family = self.config["font_family"]
        font_size = self.config["font_size"]
        font_weight = "bold" if self.config["bold"] else "normal"
        font_slant = "italic" if self.config["italic"] else "roman"
  
        # Créer une police avec les paramètres
        font = (font_family, font_size, font_weight, font_slant)

        # Créer une couleur avec les paramètres
        color = self.config["font_color"]


        item = 0 # cette variable contien le premier chiffre qui sera ecrit sur des coordonees precis
        item = self.config["start"] # on initialise la premiere valeur au numero de depart
        number_of_pages = len(self.paths_to_duplicated_pages) # les nombre de page du facturier

        #boucler sur les nombre de pages
        for i in range(number_of_pages):

            self.render_pdf_to_canvas(self.paths_to_duplicated_pages[i])

            x, y = coordinates

            self.canvas.create_text(x, y, text=str(item), font=font, fill=color)

            item = item + 1

            # enregistrement de la page courante en pdf
            self.save_canvas_to_pdf(self.paths_to_duplicated_pages[i])

            # supprimer le canevas pour la prochaine page
            self.canvas.destroy()
            self.canvas = None

    
    
    def two_per_page(self):
        # Récupérer les paramètres de style
        font_family = self.config["font_family"]
        font_size = self.config["font_size"]
        font_weight = "bold" if self.config["bold"] else "normal"
        font_slant = "italic" if self.config["italic"] else "roman"
  
        # Créer une police avec les paramètres
        font = (font_family, font_size, font_weight, font_slant)

        # Créer une couleur avec les paramètres
        color = self.config["font_color"]

        item = [] # ce tavlau contien un nombre x de chiffre qui seront ecrit sur des coordonees precis
        item [0] = self.config["start"] # on initialise la premiere valeur au numero de depart
        item [1] = self.config["start"] # a cette valeur sera ajoutée le nombre de pages du facturier et former le deuxieme nombre

        number_of_pages = len(self.paths_to_duplicated_pages) # les nombre de page du facturier

        item_index = 0 # le selecteur du numero a ecrir via son index dans le tableau item

        #boucler sur les nombre de pages
        for i in range(number_of_pages):

            self.render_pdf_to_canvas(self.paths_to_duplicated_pages[i])

            #boucler sur les coordonees
            for x, y in self.coordinates:
                self.canvas.create_text(x, y, text=str(item[item_index]), font=font, fill=color)
                item_index += 1 # mise a jour du selecteur
                item[item_index] = item[item_index] + number_of_pages # on obtien le deuxieme nompbre par le premier nombre + le nbr de pages du facturier

            item[0] = item[0] + 1

            # enregistrement de la page courante en pdf
                        # enregistrement de la page courante en pdf
            self.save_canvas_to_pdf(self.paths_to_duplicated_pages[i])

            # supprimer le canevas pour la prochaine page
            self.canvas.destroy()
            self.canvas = None

    
    def three_per_page(self):
        # Récupérer les paramètres de style
        #font_family = self.config["font_family"]
        font_size = self.config["font_size"]
        #font_weight = "bold" if self.config["bold"] else "normal"
        #font_slant = "italic" if self.config["italic"] else "roman"

        # Créer une couleur avec les paramètres
        #color = self.config["font_color"]

        item = [3] # ce tavlau contien un nombre x de chiffre qui seront ecrit sur des coordonees precis
        item [0] = self.config["start"] # on initialise la premiere valeur au numero de depart
        item [1] = self.config["start"] # a cette valeur sera ajoutée le nombre de pages du facturier et former le deuxieme nombre
        item [2] = self.config["start"] # a cette valeur sera ajoutée le nombre de pages du facturier x 2 et former le troisieme nombre
        
        number_of_pages = len(self.paths_to_duplicated_pages) # les nombre de page du facturier

        item_index = 0 # le selecteur du numero a ecrir via son index dans le tableau item

        #document temporaire à numeroter
        doc = None


        number_of_pages = len(self.paths_to_duplicated_pages) # les nombre de page du facturier


        #boucler sur les nombre de pages
        for i in range(number_of_pages):

            #ouvrir le pdf
            doc = self.open_pdf(self.paths_to_duplicated_pages[i])

            #faire une projection de coordonees du canvas vers des point sur pdf
            self.project_canvas_coords_to_pdf_points()
            
            #boucler sur les coordonees en points
            for x, y in self.projected_coordinates:
            
                # Insert the text on the PDF
                page = doc[0]
                page.insert_text((x, y), str(item[item_index]), fontsize= int(font_size), color=(244/255, 32/255, 32/255))
            
                item[item_index] = item[item_index] + number_of_pages # on obtien le deuxieme nompbre par le premier nombre + le nbr de pages du facturier

                # Save the modified PDF
                doc.save("out_temp/" + os.path.basename(self.paths_to_duplicated_pages[i]))
                
            #on passe a la deuxieme page en incrementant le premier numero
            item[0] = item[0] + 1
            doc.close()   



    def many_per_page(self):
        # Récupérer les paramètres de style
        #font_path = "fonts/arial/ARIAL.TTF"  # Chemin vers votre fichier de police
        #font_family = fitz.open_font(font_path)  # Charger le fichier de police

        #font_family = self.config["font_family"]
        font_size = self.config["font_size"]
        # font_weight = "bold" if self.config["bold"] else "normal"
        # font_slant = "italic" if self.config["italic"] else "roman"

        # # Créer une police avec les paramètres
        # font = (font_family, font_size, font_weight, font_slant)

        # # Créer une couleur avec les paramètres
        # color = self.config["font_color"]

        
        doc = None

        item = 0 # cette variable contien le premier chiffre qui sera ecrit sur des coordonees precis
        item = self.config["start"] # cette variable contien un nombre à ecrir sur des coordonees precis


        number_of_pages = len(self.paths_to_duplicated_pages) # les nombre de page du facturier


        #boucler sur les nombre de pages
        for i in range(number_of_pages):

            #ouvrir le pdf
            doc = self.open_pdf(self.paths_to_duplicated_pages[i])

            #faire une projection de coordonees du canvas vers des point sur pdf
            self.project_canvas_coords_to_pdf_points()
            
            #boucler sur les coordonees en points
            for x, y in self.projected_coordinates:
            
                # Insert the text on the PDF
                page = doc[0]
                page.insert_text((x, y), str(item), fontsize= int(font_size), color=(244/255, 32/255, 32/255))
            
                item = item + 1 # on obtien le deuxieme nompbre par le premier nombre + 1

                # Save the modified PDF
                doc.save("out_temp/" + os.path.basename(self.paths_to_duplicated_pages[i]))

            doc.close()    
                

            
           


    def start_numbering(self):

        if not self.config["start"]:
            return
        
        items_per_page = len(self.coordinates)

        if items_per_page == 1:
            self.one_per_page()
            return

        if items_per_page == 2:
            self.two_per_page()
            return
        if items_per_page == 3:
            self.three_per_page()
            return
        if items_per_page > 3:
            self.many_per_page()
            return
        
        # Cas non pris en charge
        messagebox.showerror("Erreur", "Unknown invoice configuration")
        
  

# Exemple d'utilisation
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x400")

    interval = {"start": 1}
    font_settings = {"size": 12, "family": "Arial", "color": "#000000", "italic": False, "bold": False}
    coordinates = True  # Simuler des coordonnées marquées
    paths_to_duplicated_pages = ["page1", "page2"]  # Simuler des pages dupliquées

    def open_config_window():
        config_window = Drawer(root, coordinates, paths_to_duplicated_pages)
        config_window.open()

    Button(root, text="Open Config Window", command=open_config_window).pack(pady=20)

    root.mainloop()
