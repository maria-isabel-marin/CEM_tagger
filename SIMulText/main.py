import importlib       # 👈 primero importa la libreria
import ui_main         # importa tu modulo
importlib.reload(ui_main)   # fuerza la recarga del archivo
from ui_main import Simultext   # 👈 mismo nombre de la clase
import tkinter as tk


def main():
    root = tk.Tk()
    root.title("SIMULTEXT")
    app = Simultext(root)
    root.mainloop()

if __name__ == "__main__":
    main()