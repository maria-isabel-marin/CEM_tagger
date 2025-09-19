import tkinter as tk
import os
import json
from tkinter import ttk, scrolledtext, messagebox
import xml.etree.ElementTree as ET
import json
from . import config


class VentanaEtiquetadoOraciones:
    def __init__(self, root, ruta_xml, tipo_texto):
        self.root = root
        self.root.title("SIMULTEXT - Etiquetado de Oraciones")
        self.root.geometry("1400x800")
        self.root.configure(bg=config.COLOR_FONDO)

        self.ruta_xml = ruta_xml
        self.tipo_texto = tipo_texto
        self.oraciones = []
        self.etiquetas = config.ETIQUETAS_ORACIONES
        self.widgets_oraciones = {}  # Diccionario {id_oracion: {codigo: BooleanVar}}

        self.cargar_datos_xml()
        self.crear_interfaz()

    def cargar_datos_xml(self):
        """Carga las oraciones del XML."""
        try:
            tree = ET.parse(self.ruta_xml)
            root = tree.getroot()
            self.oraciones = []

            for parrafo in root.findall(".//paragraph"):
                id_parrafo = parrafo.get("id")

                for idx, oracion in enumerate(parrafo.findall(".//sentence"), start=1):
                    tokens = [token.get("form", "") for token in oracion.findall(".//token")]
                    texto_oracion = " ".join(tokens)

                    self.oraciones.append({
                        "id_parrafo": id_parrafo,
                        "id_oracion": oracion.get("id", f"{id_parrafo}_{idx}"),  # usa id propio si existe
                        "texto": texto_oracion.strip()
                    })

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el XML: {str(e)}")

    def crear_interfaz(self):
        # Frame principal
        main_frame = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)

        # === IZQUIERDA: ETIQUETADO ===
        left_frame = ttk.Frame(main_frame, style="Fondo.TFrame")
        main_frame.add(left_frame, weight=3)

        # === DERECHA: TEXTO ===
        right_frame = ttk.Frame(main_frame, style="Fondo.TFrame")
        main_frame.add(right_frame, weight=1)

        # Configurar grid para left_frame (etiquetado)
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=0)

        # === LADO IZQUIERDO - ETIQUETADO ===
        contenido_frame = ttk.Frame(left_frame, style="Fondo.TFrame")
        contenido_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=5)

        titulo_etiquetado = ttk.Label(
            contenido_frame,
            text="ETIQUETADO DE ORACIONES",
            font=("Arial", 14, "bold"),
            foreground=config.COLOR_TITULO,
            background=config.COLOR_FONDO
        )
        titulo_etiquetado.pack(pady=10)

        # Contenedor scrollable
        canvas = tk.Canvas(contenido_frame, bg=config.COLOR_FONDO, highlightthickness=0)
        scroll_y = ttk.Scrollbar(contenido_frame, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas, style="Fondo.TFrame")

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll_y.set)

        canvas.pack(side="left", fill="both", expand=True, padx=5)
        scroll_y.pack(side="right", fill="y")

                # === Vincular scroll con la rueda del mouse ===
        # Función de scroll para Linux
        def _on_mousewheel_linux(event):
            if event.num == 4:  # rueda arriba
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:  # rueda abajo
                canvas.yview_scroll(1, "units")

        # Vincular solo al canvas
        canvas.bind("<Button-4>", _on_mousewheel_linux)
        canvas.bind("<Button-5>", _on_mousewheel_linux)


        # Estilo más pequeño
        style = ttk.Style()
        style.configure("Small.TCheckbutton", font=("TkDefaultFont", 8))

        # === ITERAR ORACIONES ===
        for oracion in self.oraciones:
            frame_oracion = ttk.LabelFrame(
                scroll_frame,
                text=f"Oración {oracion['id_oracion']}",
                style="Fondo.TFrame"
            )
            frame_oracion.pack(fill="x", padx=5, pady=5)

            # Texto de la oración
            label_texto = ttk.Label(
                frame_oracion,
                text=oracion["texto"],
                wraplength=500,
                background=config.COLOR_FONDO,
                foreground=config.COLOR_TEXTO,
                font=("Arial", 11, "bold")
            )
            label_texto.pack(anchor="w", padx=10, pady=5)

            # Diccionario de variables para esta oración
            vars_oracion = {}
            self.widgets_oraciones[oracion["id_oracion"]] = vars_oracion

            # Notebook con categorías
            notebook = ttk.Notebook(frame_oracion, style="Custom.TNotebook")
            notebook.pack(fill="x", padx=5, pady=5)

            for categoria, datos in self.etiquetas.items():
                tab = ttk.Frame(notebook, style="Fondo.TFrame")
                notebook.add(tab, text=categoria.replace("_", " ").title())

                n = len(datos)
                mitad = (n + 1) // 2

                for i, (subtipo, codigo) in enumerate(datos.items()):
                    if i < mitad:
                        fila = i
                        col = 0
                    else:
                        fila = i - mitad
                        col = 1

                    var_check = tk.BooleanVar(value=False)
                    vars_oracion[codigo] = var_check

                    cb = ttk.Checkbutton(
                        tab,
                        text=f"{subtipo} ({codigo})",
                        variable=var_check,
                        style="Small.TCheckbutton"
                    )
                    cb.grid(row=fila, column=col, sticky="w", padx=10, pady=1)

        # === BOTONES ===
        botones_frame = ttk.Frame(left_frame, style="Fondo.TFrame")
        botones_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        botones_frame.columnconfigure(0, weight=1)
        botones_frame.columnconfigure(1, weight=1)

        self.btn_guardar = tk.Button(
            botones_frame,
            text="GUARDAR",
            command=self.guardar_etiquetas,
            bg=config.COLOR_BOTON_VERDE,
            fg=config.COLOR_BOTON_TEXTO,
            font=config.FUENTE_BOTON,
            borderwidth=1,
            relief="raised",
            height=1
        )
        self.btn_guardar.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.btn_cancelar = tk.Button(
            botones_frame,
            text="CANCELAR",
            command=self.root.destroy,
            bg=config.COLOR_BOTON_AZUL_CLARO,
            fg=config.COLOR_BOTON_TEXTO,
            font=config.FUENTE_BOTON,
            borderwidth=1,
            relief="raised",
            height=1
        )
        self.btn_cancelar.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # === LADO DERECHO - TEXTO COMPLETO ===
        titulo_label = ttk.Label(
            right_frame,
            text="TEXTO",
            font=("Arial", 14, "bold"),
            foreground=config.COLOR_TITULO,
            background=config.COLOR_FONDO
        )
        titulo_label.pack(pady=10)

        self.texto_area = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            width=25,
            font=(config.FUENTE_TEXTO, 8),
            bg=config.COLOR_FONDO,
            fg=config.COLOR_TEXTO,
            relief=tk.FLAT,
            borderwidth=1,
            padx=5,
            pady=10
        )
        self.texto_area.pack(fill=tk.BOTH, expand=True, padx=2, pady=5)
        self.mostrar_texto_completo()

        self.configurar_estilos()

    def configurar_estilos(self):
        style = ttk.Style()
        style.configure("Fondo.TFrame", background=config.COLOR_FONDO)
        style.configure("TLabel", background=config.COLOR_FONDO, foreground=config.COLOR_TEXTO)

        # Cambiar color de la pestaña seleccionada
        style.map("Custom.TNotebook.Tab",
                background=[("selected", config.COLOR_BOTON_VERDE)],
                foreground=[("selected", "white")])  # Texto en blanco para la pestaña seleccionada



    def mostrar_texto_completo(self):
        """Construye párrafos a partir de self.oraciones y los muestra en el ScrolledText."""
        from collections import OrderedDict

        parrafos = OrderedDict()
        for o in self.oraciones:
            pid = o.get("id_parrafo", "0")
            parrafos.setdefault(pid, []).append(o.get("texto", ""))

        texto_formateado = []
        for pid, oraciones in parrafos.items():
            texto_parrafo = " ".join(s.strip() for s in oraciones).strip()
            texto_formateado.append(f" {str(pid).upper()}\n{'-'*40}\n{texto_parrafo}\n")

        final = "\n".join(texto_formateado).strip()

        self.texto_area.config(state=tk.NORMAL)
        self.texto_area.delete("1.0", tk.END)
        self.texto_area.insert(tk.END, final)
        self.texto_area.config(state=tk.DISABLED)

    def guardar_etiquetas(self):
        try:
            etiquetas_guardar = {}
            for oracion_id, vars_dict in self.widgets_oraciones.items():
                seleccionadas = [codigo for codigo, var in vars_dict.items() if var.get()]
                if seleccionadas:
                    etiquetas_guardar[oracion_id] = seleccionadas

            if not etiquetas_guardar:
                messagebox.showwarning(
                    "Etiquetado incompleto",
                    "No se seleccionó ninguna etiqueta. Por favor, etiqueta al menos una oración."
                )
                return

            # Nombre base del archivo
            nombre_base = os.path.splitext(os.path.basename(self.ruta_xml))[0]
            nombre_archivo = f"{nombre_base}_etiquetas.json"

            datos_completos = {
                "metadata": {
                    "tipo_texto": self.tipo_texto,
                    "archivo_origen": self.ruta_xml
                },
                "etiquetas_oraciones": etiquetas_guardar
            }

            if os.path.exists(nombre_archivo):
                # Cargar contenido existente
                with open(nombre_archivo, "r", encoding="utf-8") as f:
                    try:
                        contenido = json.load(f)
                    except json.JSONDecodeError:
                        contenido = {}

                # Asegurar estructura
                if "metadata" not in contenido:
                    contenido["metadata"] = datos_completos["metadata"]
                if "etiquetas_oraciones" not in contenido:
                    contenido["etiquetas_oraciones"] = {}

                # Actualizar etiquetas (sobrescribe las de la misma oración)
                contenido["etiquetas_oraciones"].update(etiquetas_guardar)

                with open(nombre_archivo, "w", encoding="utf-8") as f:
                    json.dump(contenido, f, ensure_ascii=False, indent=2)

            else:
                # Crear nuevo archivo
                with open(nombre_archivo, "w", encoding="utf-8") as f:
                    json.dump(datos_completos, f, ensure_ascii=False, indent=2)

            resumen = f"✅ Etiquetas guardadas exitosamente!\n\n"
            resumen += f"📁 Archivo: {nombre_archivo}\n"
            resumen += f"📝 Oraciones etiquetadas: {len(etiquetas_guardar)}/{len(self.oraciones)}"
            messagebox.showinfo("Guardado exitoso", resumen)
            self.root.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar las etiquetas: {str(e)}")