import fitz  # PyMuPDF
import os
import tkinter as tk
from tkinter import PhotoImage, messagebox, Canvas, Scrollbar, Frame,Toplevel
from PIL import Image, ImageTk

class PDFViewer:
    def __init__(self, root, pdf_path, password):
        """Initialise l'affichage du PDF sans enregistrer de copie."""
        self.pdf_path = pdf_path
        self.password = password
        self.window_width = 560
        self.window_height = 700
        self.page_width = self.window_width - 20  # Marges de 10px à gauche et à droite
        self.page_height = self.window_height - 20
        self.image_refs = []  # Stocker les images pour éviter leur suppression par le garbage collector

        # Création de la fenêtre principale
        self.root = Toplevel(root)
        self.icon = PhotoImage(file="icons/icon0.png")  # Chargement de l'icône
        self.root.iconphoto(False, self.icon)  # Définir l'icône
        self.root.title("PDF Viewer")
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        self.root.resizable(False, False)

        # Vérifier et charger le PDF
        self.load_pdf()
        self.setup_ui()

        self.root.mainloop()

    def load_pdf(self):
        """Ouvre le PDF et gère le mot de passe si nécessaire."""
        if not os.path.exists(self.pdf_path):
            messagebox.showerror("Erreur", "Le fichier PDF n'existe pas.")
            self.root.destroy()
            return

        try:
            self.doc = fitz.open(self.pdf_path)
            if self.doc.needs_pass and not self.doc.authenticate(self.password):
                messagebox.showerror("Erreur", "Mot de passe incorrect!")
                self.root.destroy()
                return

            self.total_pages = len(self.doc)

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le PDF : {e}")
            self.root.destroy()

    def setup_ui(self):
        """Crée l'interface graphique pour l'affichage du PDF."""
        frame = Frame(self.root)
        frame.pack(fill="both", expand=True)

        # Barre de défilement verticale
        scrollbar = Scrollbar(frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        # Canevas contenant les pages
        self.canvas_container = Canvas(frame, bg="white", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.canvas_container.yview)
        self.canvas_container.pack(side="left", fill="both", expand=True)

        self.inner_frame = Frame(self.canvas_container)
        self.canvas_container.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.render_pdf()

    def render_pdf(self):
        """Rend les pages PDF avec un canevas séparé pour chaque page."""
        
        # Nettoyer les widgets existants avant d'afficher les nouvelles pages
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        self.image_refs.clear()  # Vider la liste des images pour éviter l'accumulation

        for page in self.doc:
            # Convertir la page en image avec redimensionnement
            pix = page.get_pixmap()
            scale_factor = min(self.page_width / pix.width, self.page_height / pix.height)
            scaled_pix = page.get_pixmap(matrix=fitz.Matrix(scale_factor, scale_factor))
            
            img = Image.frombytes("RGB", [scaled_pix.width, scaled_pix.height], scaled_pix.samples)
            photo = ImageTk.PhotoImage(img)  # Convertir pour Tkinter
            
            # Ajouter l'image à l'instance pour la garder en mémoire
            self.image_refs.append(photo)  # Stocker l'image pour éviter le garbage collector

            # Création d'un canevas pour chaque page
            page_canvas = Canvas(self.inner_frame, width=self.page_width, height=self.page_height, bg="white")

            # Attacher l'image au `page_canvas`
            page_canvas.image = photo  # Référence persistante à l'image
            page_canvas.create_image(self.page_width // 2, self.page_height // 2, image=photo, anchor="center")
            page_canvas.pack(pady=5)  # Espacement entre les pages

        self.inner_frame.update_idletasks()
        self.canvas_container.config(scrollregion=self.canvas_container.bbox("all"))
