import os 
import json
import fitz
import win32print
import tkinter as tk
from tkinter import PhotoImage, Toplevel, ttk, messagebox
from io import BytesIO

class PrinterApp:
    _instance = None  # Variable de classe pour garantir qu'il n'y a qu'une seule instance de la fenêtre d'impression
    
    def __init__(self, root, file_path, password=""):
        # Si une instance existe déjà, on ne crée pas une nouvelle fenêtre
        if PrinterApp._instance is not None:
            return
        
        PrinterApp._instance = self
        
        self.root = Toplevel(root)
        self.root.title("artisanPrint")
        self.root.resizable(False, False)
        self.file_path = file_path
        self.password = password
        
        icon = PhotoImage(file="icons/icon0.png")
        self.root.iconphoto(False, icon)
        
        self.selected_printer = tk.StringVar()
        self.page_range = tk.StringVar(value="all")
        
        self.create_widgets()
        self.set_default_printer()
        self.root.lift()  # Pour s'assurer que la fenêtre est au-dessus de la fenêtre principale
        self.root.attributes("-topmost", True)  # Met la fenêtre d'impression toujours au-dessus de la fenêtre principale
        
    def create_widgets(self):
        ttk.Label(self.root, text="Printer:").pack(padx=5, pady=5, anchor="w")
        self.printer_combo = ttk.Combobox(self.root, textvariable=self.selected_printer, width=40)
        self.printer_combo['values'] = self.get_available_printers()
        self.printer_combo.pack(padx=5, pady=5, fill="x")

        ttk.Label(self.root, text="Page Range (ex: 1-3,5 or 'all'):").pack(padx=5, pady=5, anchor="w")
        ttk.Entry(self.root, textvariable=self.page_range, width=40).pack(padx=5, pady=5, fill="x")
        
        print_icon = PhotoImage(file="icons/icon6.png")
        self.print_button = ttk.Button(self.root, text=" Print PDF", image=print_icon, compound="left", command=self.print_pdf)
        self.print_button.image = print_icon
        self.print_button.pack(padx=5, pady=10, anchor="e")

    def get_available_printers(self):
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL, None, 1)
        return [printer[2] for printer in printers]

    def set_default_printer(self):
        printers = self.get_available_printers()
        if printers:
            self.selected_printer.set(printers[0])  # Sélectionne le premier imprimante comme imprimante par défaut

    def parse_page_range(self, total_pages):
        page_range = self.page_range.get().lower().strip()
        if page_range in ["", "all"]:
            return list(range(1, total_pages + 1))
        pages = set()
        parts = page_range.split(',')
        
        for part in parts:
            part = part.strip()
            if '-' in part:
                try:
                    start, end = map(int, part.split('-'))
                    if 1 <= start <= end <= total_pages:
                        pages.update(range(start, end + 1))
                except ValueError:
                    pass
            else:
                try:
                    page = int(part)
                    if 1 <= page <= total_pages:
                        pages.add(page)
                except ValueError:
                    pass

        return sorted(pages) if pages else list(range(1, total_pages + 1))

    def print_pdf(self):
        printer_name = self.selected_printer.get()
        
        if not all([self.file_path, os.path.exists(self.file_path), self.file_path.lower().endswith('.pdf')]):
            messagebox.showerror("Error", "Invalid or missing PDF file")
            return

        try:
            doc = fitz.open(self.file_path)
            
            if doc.is_encrypted and not doc.authenticate(self.password):
                raise ValueError("Incorrect password or password required")

            total_pages = doc.page_count
            selected_pages = self.parse_page_range(total_pages)
            
            buffer = BytesIO()
            new_doc = fitz.open()
            
            for pg in selected_pages:
                new_doc.insert_pdf(doc, from_page=pg-1, to_page=pg-1)
            
            new_doc.save(buffer)
            pdf_data = buffer.getvalue()
            new_doc.close()
            doc.close()

            hprinter = win32print.OpenPrinter(printer_name)
            try:
                win32print.StartDocPrinter(hprinter, 1, ("PDF Print", None, "RAW"))
                win32print.StartPagePrinter(hprinter)
                win32print.WritePrinter(hprinter, pdf_data)
                win32print.EndPagePrinter(hprinter)
                win32print.EndDocPrinter(hprinter)
            finally:
                win32print.ClosePrinter(hprinter)

            messagebox.showinfo("Success", "PDF printed successfully")
            self.root.destroy()  # Ferme la fenêtre après l'impression réussie

        except Exception as e:
            messagebox.showerror("Print Error", str(e))

    def start_printing(self):
        self.print_pdf()
