import tkinter as tk
import os
import json
from tkinter import ttk, scrolledtext, messagebox
import xml.etree.ElementTree as ET
from . import config


class VentanaEtiquetadoOraciones:
    def __init__(self, root, ruta_json, tipo_texto):
        self.root = root
        self.root.title("SIMULTEXT - Etiquetado de Oraciones")
        self.root.geometry("1400x800")
        self.root.configure(bg=config.COLOR_FONDO)

        self.ruta_json = ruta_json
        self.tipo_texto = tipo_texto
        self.oraciones = []
        self.etiquetas = config.ETIQUETAS_ORACIONES
        self.widgets_oraciones = {}  # Diccionario {id_oracion: {codigo: BooleanVar}}
        self.etiquetas_existentes = {}  # Para cargar etiquetas guardadas
        self.notebooks_oraciones = {}  # Diccionario {id_oracion: notebook}

        self.cargar_datos_desde_json()
        self.crear_interfaz()

    def cargar_datos_desde_json(self):
        """Carga las oraciones y etiquetas existentes desde el JSON."""
        try:
            with open(self.ruta_json, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            # Cargar etiquetas existentes si las hay
            etiquetado = datos.get("document", {}).get("Etiquetado", {})
            self.etiquetas_existentes = etiquetado.get("oraciones", {})
            
            # Cargar oraciones desde la estructura del documento
            self.oraciones = []
            documento = datos.get("document", {})
            
            # Obtener los párrafos - en tu estructura es "paragraph" como lista
            parrafos = documento.get("paragraph", [])
            
            # Si es un solo párrafo (diccionario), convertirlo a lista
            if isinstance(parrafos, dict):
                parrafos = [parrafos]
            
            for parrafo in parrafos:
                if not parrafo:
                    continue
                    
                id_parrafo = parrafo.get("@id", "p0")
                
                # Obtener las oraciones del párrafo
                oraciones_parrafo = parrafo.get("sentence", [])
                
                # Si es una sola oración (diccionario), convertirla a lista
                if isinstance(oraciones_parrafo, dict):
                    oraciones_parrafo = [oraciones_parrafo]
                
                for oracion in oraciones_parrafo:
                    if not oracion:
                        continue
                        
                    id_oracion = oracion.get("@id", f"{id_parrafo}_s0")
                    
                    # Extraer texto de la oración desde los tokens
                    texto_oracion = ""
                    tokens = oracion.get("token", [])
                    
                    # Si es un solo token (diccionario), convertirlo a lista
                    if isinstance(tokens, dict):
                        tokens = [tokens]
                    
                    for token in tokens:
                        if isinstance(token, dict):
                            texto_oracion += token.get("@form", "") + " "
                    
                    self.oraciones.append({
                        "id_parrafo": id_parrafo,
                        "id_oracion": id_oracion,
                        "texto": texto_oracion.strip()
                    })

            print(f"Se cargaron {len(self.oraciones)} oraciones desde el JSON")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el JSON: {str(e)}")
            print(f"Error detallado: {e}")

    def encontrar_pestaña_por_etiqueta(self, codigo_etiqueta):
        """Encuentra en qué pestaña (categoría) se encuentra una etiqueta específica."""
        for categoria, etiquetas_categoria in self.etiquetas.items():
            if codigo_etiqueta in etiquetas_categoria.values():
                return categoria
        return None

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

        # Mostrar información de etiquetas existentes
        if self.etiquetas_existentes:
            info_label = ttk.Label(
                contenido_frame,
                text=f"✓ Se cargaron {len(self.etiquetas_existentes)} oraciones etiquetadas previamente",
                font=("Arial", 10, "italic"),
                foreground=config.COLOR_BOTON_VERDE,
                background=config.COLOR_FONDO
            )
            info_label.pack(pady=5)

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
        def _on_mousewheel_linux(event):
            if event.num == 4:  # rueda arriba
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:  # rueda abajo
                canvas.yview_scroll(1, "units")

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
            self.notebooks_oraciones[oracion["id_oracion"]] = notebook

            # Crear pestañas y checkboxes
            pestañas = {}  # Para mapear categorías a índices de pestañas
            for idx, (categoria, datos) in enumerate(self.etiquetas.items()):
                tab = ttk.Frame(notebook, style="Fondo.TFrame")
                notebook.add(tab, text=categoria.replace("_", " ").title())
                pestañas[categoria] = idx

                n = len(datos)
                mitad = (n + 1) // 2

                for i, (subtipo, codigo) in enumerate(datos.items()):
                    if i < mitad:
                        fila = i
                        col = 0
                    else:
                        fila = i - mitad
                        col = 1

                    # Verificar si esta etiqueta ya estaba seleccionada
                    valor_inicial = False
                    pestaña_a_abrir = None
                    if oracion["id_oracion"] in self.etiquetas_existentes:
                        etiquetas_oracion = self.etiquetas_existentes[oracion["id_oracion"]]
                        if isinstance(etiquetas_oracion, list):
                            valor_inicial = codigo in etiquetas_oracion
                        elif isinstance(etiquetas_oracion, str):
                            valor_inicial = codigo == etiquetas_oracion
                        
                        # Si esta etiqueta está seleccionada, determinar qué pestaña abrir
                        if valor_inicial:
                            pestaña_a_abrir = self.encontrar_pestaña_por_etiqueta(codigo)

                    var_check = tk.BooleanVar(value=valor_inicial)
                    vars_oracion[codigo] = var_check

                    cb = ttk.Checkbutton(
                        tab,
                        text=f"{subtipo} ({codigo})",
                        variable=var_check,
                        style="Small.TCheckbutton"
                    )
                    cb.grid(row=fila, column=col, sticky="w", padx=10, pady=1)

            # Después de crear todos los checkboxes, abrir la pestaña correspondiente
            # si hay etiquetas seleccionadas para esta oración
            if oracion["id_oracion"] in self.etiquetas_existentes:
                etiquetas_oracion = self.etiquetas_existentes[oracion["id_oracion"]]
                if etiquetas_oracion:
                    # Tomar la primera etiqueta para determinar la pestaña
                    primera_etiqueta = etiquetas_oracion[0] if isinstance(etiquetas_oracion, list) else etiquetas_oracion
                    pestaña_a_abrir = self.encontrar_pestaña_por_etiqueta(primera_etiqueta)
                    
                    if pestaña_a_abrir and pestaña_a_abrir in pestañas:
                        notebook.select(pestañas[pestaña_a_abrir])

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
                foreground=[("selected", "white")])

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
            oraciones_sin_etiqueta = []

            # Recorre todas las oraciones y recoge las etiquetas seleccionadas
            for oracion_id, vars_dict in self.widgets_oraciones.items():
                seleccionadas = [codigo for codigo, var in vars_dict.items() if var.get()]
                if seleccionadas:
                    etiquetas_guardar[oracion_id] = seleccionadas
                else:
                    oraciones_sin_etiqueta.append(oracion_id)

            # Si no se seleccionó ninguna etiqueta
            if not etiquetas_guardar:
                messagebox.showwarning(
                    "Etiquetado incompleto",
                    "No se seleccionó ninguna etiqueta. Por favor, etiqueta al menos una oración.",
                    parent=self.root
                )
                return

            # Si hay oraciones sin etiqueta, preguntar al usuario
            if oraciones_sin_etiqueta:
                if not messagebox.askyesno(
                    "Oraciones sin etiquetar",
                    f"Hay {len(oraciones_sin_etiqueta)} oraciones sin etiqueta.\n"
                    "¿Deseas guardar de todas formas?",
                    parent=self.root
                ):
                    return

            # Cargar el JSON existente
            with open(self.ruta_json, 'r', encoding='utf-8') as f:
                datos = json.load(f)

            # Actualizar las etiquetas de oraciones
            if 'document' not in datos:
                datos['document'] = {}
            
            if 'Etiquetado' not in datos['document']:
                datos['document']['Etiquetado'] = {}
            
            datos['document']['Etiquetado']['oraciones'] = etiquetas_guardar

            # Guardar el JSON actualizado
            with open(self.ruta_json, 'w', encoding='utf-8') as f:
                json.dump(datos, f, ensure_ascii=False, indent=2)

            # Mensaje de resumen
            resumen = f"Etiquetas guardadas exitosamente!\n\n"
            resumen += f"Archivo: {os.path.basename(self.ruta_json)}\n"
            resumen += f"Oraciones etiquetadas: {len(etiquetas_guardar)}/{len(self.oraciones)}"
            messagebox.showinfo("Guardado exitoso", resumen, parent=self.root)

            self.root.destroy()

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudieron guardar las etiquetas: {str(e)}",
                parent=self.root
            )