import tkinter as tk
from PyPDF2 import PdfReader
import fitz  # PyMuPDF
import os
from PIL import ImageGrab
from reportlab.pdfgen import canvas
from tkinter import Toplevel, IntVar, Canvas, PhotoImage, StringVar, BooleanVar, messagebox, colorchooser, Label, Entry, Button, ttk

#dependences personalisés
from utils.utils import * 

class Drawer:
    def __init__(self, root, canvas, coordinates):
        self.root = root
        self.canvas = canvas
        self.coordinates = coordinates
        self.projected_coordinates = None
        self.paths_to_duplicated_pages = None

        # Déclaration des attributs de classe
        self.config = None
        self.out_temp = "out_temp"
        self.is_loaded_file = False

        self.wf_config_data = None

    
    def load_config(self):
        self.wf_config_data = read_workflow_config()
        self.paths_to_duplicated_pages = self.wf_config_data[1]
        self.config = self.wf_config_data[0]



    
    def add_leading_zeros(self,number):
        """
        Ajoute deux zéros devant le nombre s'il est inférieur à 100.
        
        Args:
            number (int): Le nombre à traiter.
        
        Returns:
            str: Le nombre formaté avec deux zéros devant si nécessaire.
        """
        if number < 100:
            return f"{number:03d}"  # Format en ajoutant des zéros devant jusqu'à une longueur de 3 caractères
        # si non retourner le nombre tel qu'il est
        return str(number)
    
    
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


        # Open the PDF file with fitz
        pdf_document = fitz.open(pdf_copy_path)

        # Get the first page (assuming one-page PDF for simplicity)
        page = pdf_document[0]

        # Get the dimensions of the PDF page in points (1 point = 1/72 inch)
        pdf_width, pdf_height = page.rect.width, page.rect.height


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
        

        # Créer un PDF avec les mêmes dimensions que le Canvas Tkinter
        pdf_canvas = canvas.Canvas(pdf_path, pagesize=(image.width, image.height))

        # Ajouter l'image dans le PDF avec les bonnes dimensions
        pdf_canvas.drawImage(png_path, 0, 0, width=image.width, height=image.height)

        # Finaliser le PDF
        pdf_canvas.save()




    def one_per_page(self):


        # Créer le dossier temporaire si nécessaire
        output_dir = "out_temp"
        os.makedirs(output_dir, exist_ok=True)
        
        number_of_pages = len(self.paths_to_duplicated_pages) # les nombre de page du facturier
        start_number = self.config["start"]  # Numéro de départ
        font_size = self.config["font_size"]


        #document temporaire à numeroter
        doc = None

        #boucler sur les nombre de pages
        for i in range(number_of_pages):

            item = start_number # ce tavlau contien un nombre x de chiffre qui seront ecrit sur des coordonees precis

            #ouvrir le pdf
            doc = self.open_pdf(self.paths_to_duplicated_pages[i])

            #faire une projection de coordonees du canvas vers des point sur pdf
            self.project_canvas_coords_to_pdf_points()
            
            # Récupérer la première et unique coordonnée de self.projected_coordinates
            if self.projected_coordinates:  # Vérifier que la liste n'est pas vide
                x, y = self.projected_coordinates[0]  # Extraire la première (et unique) coordonnée

                # Insert the text on the PDF
                page = doc[0]  # Accéder à la première page du document
                page.insert_text(
                    (x, y),
                    self.add_leading_zeros(item),  # Insérer la valeur actuelle de item
                    fontsize=int(font_size),
                    color=(244 / 255, 32 / 255, 32 / 255)
                )

                # Incrémenter le numéro de départ
                start_number = start_number + 1

             # Save the modified PDF
            doc.save("out_temp/" + os.path.basename(self.paths_to_duplicated_pages[i]))
            doc.close()   

    
    def two_per_page(self):
       
        # Récupérer les paramètres de style
        #font_family = self.config["font_family"]
        font_size = self.config["font_size"]
        
        output_dir = "out_temp"
        os.makedirs(output_dir, exist_ok=True)
        
        number_of_pages = len(self.paths_to_duplicated_pages) # les nombre de page du facturier
        start_number = self.config["start"]  # Numéro de départ


        #document temporaire à numeroter
        doc = None

        #boucler sur les nombre de pages
        for i in range(number_of_pages):

            item = [start_number, start_number + number_of_pages] # ce tavlau contien un nombre x de chiffre qui seront ecrit sur des coordonees precis

            item_index = 0 # le selecteur du numero a ecrir via son index dans le tableau item


            #ouvrir le pdf
            doc = self.open_pdf(self.paths_to_duplicated_pages[i])

            #faire une projection de coordonees du canvas vers des point sur pdf
            self.project_canvas_coords_to_pdf_points()
            
            #boucler sur les coordonees en points
            for x, y in self.projected_coordinates:
            
                # Insert the text on the PDF
                page = doc[0]
                page.insert_text((x, y), self.add_leading_zeros(item[item_index]), fontsize= int(font_size), color=(244/255, 32/255, 32/255))
            
                item_index = item_index + 1 # on incremente l'index
            
            start_number = start_number + 1 # on incremente le numero de depart

            
             # Save the modified PDF
            doc.save("out_temp/" + os.path.basename(self.paths_to_duplicated_pages[i]))
            doc.close()   


    
    def three_per_page(self):

        # Récupérer les paramètres de style
        #font_family = self.config["font_family"]
        font_size = self.config["font_size"]
        #font_weight = "bold" if self.config["bold"] else "normal"
        #font_slant = "italic" if self.config["italic"] else "roman"

        # Créer une couleur avec les paramètres
        #color = self.config["font_color"]

        # Créer le dossier temporaire si nécessaire
        output_dir = "out_temp"
        os.makedirs(output_dir, exist_ok=True)
        
        number_of_pages = len(self.paths_to_duplicated_pages) # les nombre de page du facturier
        start_number = self.config["start"]  # Numéro de départ


        #document temporaire à numeroter
        doc = None

        #boucler sur les nombre de pages
        for i in range(number_of_pages):

            item = [start_number, start_number + number_of_pages, start_number + number_of_pages * 2] # ce tavlau contien un nombre x de chiffre qui seront ecrit sur des coordonees precis

            item_index = 0 # le selecteur du numero a ecrir via son index dans le tableau item


            #ouvrir le pdf
            doc = self.open_pdf(self.paths_to_duplicated_pages[i])

            #faire une projection de coordonees du canvas vers des point sur pdf
            self.project_canvas_coords_to_pdf_points()
            
            #boucler sur les coordonees en points
            for x, y in self.projected_coordinates:
            
                # Insert the text on the PDF
                page = doc[0]
                page.insert_text((x, y), self.add_leading_zeros(item[item_index]), fontsize= int(font_size), color=(244/255, 32/255, 32/255))
            
                item_index = item_index + 1 # on incremente l'index
            
            start_number = start_number + 1 # on incremente le numero de depart

            
             # Save the modified PDF
            doc.save("out_temp/" + os.path.basename(self.paths_to_duplicated_pages[i]))
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

        # Créer le dossier temporaire si nécessaire
        output_dir = "out_temp"
        os.makedirs(output_dir, exist_ok=True)

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
                page.insert_text((x, y), self.add_leading_zeros(item), fontsize= int(font_size), color=(244/255, 32/255, 32/255))
            
                item = item + 1 # on obtien le deuxieme nompbre par le premier nombre + 1

                # Save the modified PDF
                doc.save("out_temp/" + os.path.basename(self.paths_to_duplicated_pages[i]))

            doc.close()    
                

            
           


    def start_numbering(self):

        #charger le fichier de configuration pour le numeroteur
        self.load_config()
        
        if not self.config["start"]:
            return False
        
        items_per_page = len(self.coordinates)

        if items_per_page == 1:
            self.one_per_page()
            return True

        if items_per_page == 2:
            self.two_per_page()
            return True
        if items_per_page == 3:
            self.three_per_page()
            return True
        if items_per_page > 3:
            self.many_per_page()
            return True
        
        # Cas non pris en charge
        messagebox.showerror("Erreur", "Unknown invoice configuration")
        return False
  

# Exemple d'utilisation
if __name__ == "__main__":
    root = tk.Tk()

    interval = {"start": 1}
    font_settings = {"size": 12, "family": "Arial", "color": "#000000", "italic": False, "bold": False}
    coordinates = True  # Simuler des coordonnées marquées
    paths_to_duplicated_pages = ["page1", "page2"]  # Simuler des pages dupliquées

    def open_config_window():
        config_window = Drawer(root, coordinates, paths_to_duplicated_pages)
        config_window.open()

    Button(root, text="Open Config Window", command=open_config_window).pack(pady=20)

    root.mainloop()
