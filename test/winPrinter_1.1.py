import os
import fitz
import win32print
import tkinter as tk
from tkinter import ttk, messagebox
from io import BytesIO

class PrinterApp:
    def __init__(self, root, file_path, password):
        self.root = root
        self.root.title("PDF Printing Application")
        self.file_path = file_path
        self.password = password

        # Variables
        self.selected_printer = tk.StringVar()
        self.page_range = tk.StringVar(value="all")

        # UI Components
        self.create_widgets()

    def create_widgets(self):
        # Printer selection
        ttk.Label(self.root, text="Select Printer:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.printer_combo = ttk.Combobox(self.root, textvariable=self.selected_printer)
        self.printer_combo['values'] = self.get_available_printers()
        self.printer_combo.grid(row=0, column=1, padx=5, pady=5, sticky="we")

        # Page range
        ttk.Label(self.root, text="Page Range (ex: 1-3,5 or 'all'):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(self.root, textvariable=self.page_range).grid(row=1, column=1, padx=5, pady=5, sticky="we")

        # Print button
        ttk.Button(self.root, text="Print PDF", command=self.print_pdf).grid(row=2, column=1, padx=5, pady=10, sticky="e")

    def get_available_printers(self):
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL, None, 1)
        return [printer[2] for printer in printers]

    def parse_page_range(self, total_pages):
        page_range = self.page_range.get().lower().strip()
        if page_range in ["", "all"]:
            return list(range(1, total_pages + 1))

        pages = set()
        parts = page_range.split(',')
        
        for part in parts:
            part = part.strip()
            if '-' in part:
                start, end = part.split('-', 1)
                try:
                    start = int(start)
                    end = int(end)
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
        try:
            # Validate inputs
            if not all([
                os.path.exists(self.file_path),
                self.file_path.lower().endswith('.pdf'),
                self.selected_printer.get()
            ]):
                raise ValueError("Invalid print parameters")

            # Open and decrypt PDF
            doc = fitz.open(self.file_path)
            if doc.is_encrypted and not doc.authenticate(self.password):
                raise ValueError("Incorrect password or password required")

            # Process page selection
            total_pages = doc.page_count
            selected_pages = self.parse_page_range(total_pages)

            # Create in-memory PDF
            buffer = BytesIO()
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=min(selected_pages)-1, to_page=max(selected_pages)-1)
            new_doc.save(buffer)
            pdf_data = buffer.getvalue()
            new_doc.close()
            doc.close()

            # Send to printer
            hprinter = win32print.OpenPrinter(self.selected_printer.get())
            try:
                win32print.StartDocPrinter(hprinter, 1, ("PDF Print", None, "RAW"))
                win32print.StartPagePrinter(hprinter)
                win32print.WritePrinter(hprinter, pdf_data)
                win32print.EndPagePrinter(hprinter)
                win32print.EndDocPrinter(hprinter)
            finally:
                win32print.ClosePrinter(hprinter)

            messagebox.showinfo("Success", "PDF printed successfully")

        except Exception as e:
            messagebox.showerror("Print Error", str(e))

if __name__ == "__main__":
    # Example usage with hardcoded values
    root = tk.Tk()
    app = PrinterApp(
        root=root,
        file_path="C:/path/to/your/file.pdf",  # Replace with actual path
        password="your_password"               # Replace with actual password
    )
    root.mainloop()