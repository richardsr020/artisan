import json
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class ConfiguratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Configurator")
        self.root.geometry("400x200")

        # Variables
        self.file_path = tk.StringVar()
        self.password = tk.StringVar(value="merged_file_password")

        # Create UI
        self.create_widgets()

    def create_widgets(self):
        # File Selection
        ttk.Label(self.root, text="PDF File:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        ttk.Entry(self.root, textvariable=self.file_path, width=30).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.root, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=5, pady=5)

        # Password
        ttk.Label(self.root, text="Password:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        ttk.Entry(self.root, textvariable=self.password, show="*").grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Save Button
        ttk.Button(self.root, text="Save Configuration", command=self.save_config).grid(row=2, column=1, pady=20)

    def browse_file(self):
        filetypes = [("PDF files", "*.pdf")]
        filename = filedialog.askopenfilename(title="Select PDF File", filetypes=filetypes)
        if filename:
            self.file_path.set(filename)

    def save_config(self):
        config_data = {
            "file_path": self.file_path.get(),
            "password": self.password.get()
        }

        if not config_data["file_path"]:
            messagebox.showerror("Error", "Please select a PDF file")
            return

        if not config_data["file_path"].lower().endswith('.pdf'):
            messagebox.showerror("Error", "Only PDF files are allowed")
            return

        try:
            with open("printer.json", "w") as f:
                json.dump(config_data, f, indent=4)
            messagebox.showinfo("Success", "Configuration saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfiguratorApp(root)
    root.mainloop()