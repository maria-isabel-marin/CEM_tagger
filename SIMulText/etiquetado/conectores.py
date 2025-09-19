# tagging_connectors.py
import tkinter as tk
from tkinter import messagebox

class ConnectorsTagger:
    def __init__(self, root, file_path):
        self.root = root
        self.file_path_json = file_path
        self.crear_ventana_aviso()

    def crear_ventana_aviso(self):
        messagebox.showinfo(
            "Función en desarrollo",
            "La función de etiquetado de conectores lógico-temporales aún está en desarrollo."
        )