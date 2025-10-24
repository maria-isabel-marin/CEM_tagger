import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import json
from datetime import datetime
from . import config
import os

class VentanaEtiquetadoConectores:
    def __init__(self, root, ruta_json, tipo_texto):
        self.root = root
        self.ruta_json = ruta_json
        self.tipo_texto = tipo_texto
        self.parrafos = []
        self.tokens_por_parrafo = {}
        self.texto_original_por_parrafo = {}
        self.etiquetas_guardadas = {}  # {etiqueta: [ [token1, token2], [token3] ] }
        self.indice_parrafo_actual = 0
        
        self.CASOS_CONECTORES = config.CASOS_CONECTORES
        
        # Preparar lista de conectores
        self.lista_conectores_ordenada = []
        for categoria, (conectores, etiqueta, color) in self.CASOS_CONECTORES.items():
            for conector in conectores:
                self.lista_conectores_ordenada.append({
                    'texto': conector.lower(),
                    'categoria': categoria,
                    'etiqueta': etiqueta,
                    'color': color,
                    'palabras': conector.lower().split(),
                    'longitud': len(conector.split())
                })
        
        self.lista_conectores_ordenada.sort(key=lambda x: x['longitud'], reverse=True)
        self.conectores_detectados = {}
        self.parrafo_actual = None
        
        self.configurar_ventana()
        self.inicializar_ui()
        self.cargar_datos_desde_json()
    
    def configurar_ventana(self):
        self.root.title("Etiquetado de Conectores")
        self.root.geometry("1400x800")

    def inicializar_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Configurar filas principales
        main_frame.rowconfigure(0, weight=0)  # info
        main_frame.rowconfigure(1, weight=0)  # navegación principal
        main_frame.rowconfigure(2, weight=0)  # botones párrafos
        main_frame.rowconfigure(3, weight=1)  # contenido
        main_frame.columnconfigure(0, weight=1)

        # === INFORMACIÓN === (más compacta)
        info_label = ttk.Label(
            main_frame,
            text=f"Archivo: {os.path.basename(self.ruta_json)} ",
            font=("Arial", 12)
        )
        info_label.grid(row=0, column=0, pady=(0, 5), sticky="w")

        # === NAVEGACIÓN PRINCIPAL === (más compacta)
        frame_navegacion = ttk.Frame(main_frame)
        frame_navegacion.grid(row=1, column=0, sticky="ew", pady=2)
        frame_navegacion.columnconfigure(1, weight=1)

        # Navegación básica a la izquierda
        frame_nav_basica = ttk.Frame(frame_navegacion)
        frame_nav_basica.grid(row=0, column=0, sticky="w")
        
        self.btn_anterior = ttk.Button(frame_nav_basica, text="Anterior", width=10, command=self.anterior_parrafo)
        self.btn_anterior.pack(side="left", padx=1)
        
        self.label_parrafo_actual = ttk.Label(frame_nav_basica, text="Párrafo 0/0", font=("Arial", 9, "bold"))
        self.label_parrafo_actual.pack(side="left", padx=10)
        
        self.btn_siguiente = ttk.Button(frame_nav_basica, text="Siguiente", width=10, command=self.siguiente_parrafo)
        self.btn_siguiente.pack(side="left", padx=1)

        # === BOTONES DE PÁRRAFOS === (más compacto)
        frame_botones_container = ttk.Frame(main_frame)
        frame_botones_container.grid(row=2, column=0, sticky="ew", pady=2)
        frame_botones_container.columnconfigure(0, weight=1)
        
        # Scrollbar horizontal para botones
        canvas = tk.Canvas(frame_botones_container, height=28, highlightthickness=0)
        scroll_x = ttk.Scrollbar(frame_botones_container, orient="horizontal", command=canvas.xview)
        
        canvas.configure(xscrollcommand=scroll_x.set)
        canvas.grid(row=0, column=0, sticky="ew")
        scroll_x.grid(row=1, column=0, sticky="ew")
        
        self.frame_botones = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=self.frame_botones, anchor="nw")
        
        def configurar_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        self.frame_botones.bind("<Configure>", configurar_scroll)

        # === CONTENIDO PRINCIPAL === (reorganizado en 2 columnas)
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=3, column=0, sticky="nsew", pady=(5, 0))
        content_frame.columnconfigure(0, weight=2)  # Textos más ancho
        content_frame.columnconfigure(1, weight=1)  # Panel lateral más estrecho
        content_frame.rowconfigure(0, weight=1)

        # --- PANEL IZQUIERDO: Textos (2 filas) ---
        frame_textos = ttk.Frame(content_frame)
        frame_textos.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        frame_textos.columnconfigure(0, weight=1)
        frame_textos.rowconfigure(0, weight=1)  # Texto original
        frame_textos.rowconfigure(1, weight=1)  # Texto con IDs

        # Texto original
        frame_original = ttk.LabelFrame(frame_textos, text="Texto Original", padding="3")
        frame_original.grid(row=0, column=0, sticky="nsew", pady=(0, 3))
        frame_original.columnconfigure(0, weight=1)
        frame_original.rowconfigure(0, weight=1)
        
        self.texto_original = scrolledtext.ScrolledText(
            frame_original, wrap="word", font=("Arial", 10), height=8
        )
        self.texto_original.grid(row=0, column=0, sticky="nsew")

        # Texto con IDs
        frame_con_ids = ttk.LabelFrame(frame_textos, text="Texto con IDs", padding="3")
        frame_con_ids.grid(row=1, column=0, sticky="nsew", pady=(3, 0))
        frame_con_ids.columnconfigure(0, weight=1)
        frame_con_ids.rowconfigure(0, weight=1)
        
        self.texto_con_ids = scrolledtext.ScrolledText(
            frame_con_ids, wrap="word", font=("Courier New", 8), height=6
        )
        self.texto_con_ids.grid(row=0, column=0, sticky="nsew")

        # --- PANEL DERECHO: Etiquetado (más compacto) ---
        frame_etiquetado = ttk.LabelFrame(content_frame, text="Etiquetado Manual", padding="5")
        frame_etiquetado.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        frame_etiquetado.columnconfigure(0, weight=1)
        frame_etiquetado.rowconfigure(0, weight=0)  # Tokens
        frame_etiquetado.rowconfigure(1, weight=0)  # Categorías
        frame_etiquetado.rowconfigure(2, weight=0)  # Botones
        frame_etiquetado.rowconfigure(3, weight=1)  # Etiquetas guardadas

        # Tokens disponibles (más compacto)
        ttk.Label(frame_etiquetado, text="Tokens:", font=("Arial", 8, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 2)
        )
        frame_tokens = ttk.Frame(frame_etiquetado, height=80)
        frame_tokens.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        frame_tokens.columnconfigure(0, weight=1)
        
        self.lista_tokens = tk.Listbox(frame_tokens, selectmode="multiple", 
                                    font=("Courier New", 8), height=14, justify="center")
        self.lista_tokens.grid(row=0, column=0, sticky="ew")
        
        scroll_tokens = ttk.Scrollbar(frame_tokens, orient="vertical", command=self.lista_tokens.yview)
        scroll_tokens.grid(row=0, column=1, sticky="ns")
        self.lista_tokens.config(yscrollcommand=scroll_tokens.set)

        # Categorías (más compacto)
        ttk.Label(frame_etiquetado, text="Etiquetas:", font=("Arial", 8, "bold")).grid(
            row=1, column=0, sticky="w", pady=(5, 2)
        )
        
        self.etiqueta_seleccionada = tk.StringVar()
        
        # --- Categorías con Radiobuttons en dos columnas ---
        self.etiqueta_seleccionada = tk.StringVar()
        self.etiqueta_seleccionada.set(next(iter(self.CASOS_CONECTORES)))  # Selección por defecto

        # Frame contenedor de radiobuttons
        frame_radiobuttons = ttk.Frame(frame_etiquetado)
        frame_radiobuttons.grid(row=1, column=0, sticky="nsew", pady=(0, 5))

        # Convertir a lista para poder indexar
        categorias = list(self.CASOS_CONECTORES.keys())
        num_columnas = 5
        num_filas = (len(categorias) + num_columnas - 1) // num_columnas

        # Crear Radiobuttons distribuidos en 2 columnas
        for i, categoria in enumerate(categorias):
            fila = i % num_filas
            columna = i // num_filas
            rb = ttk.Radiobutton(
                frame_radiobuttons,
                text=categoria,
                value=categoria,
                variable=self.etiqueta_seleccionada,
                style="Small.TRadiobutton"  # estilo para letra más pequeña
            )
            rb.grid(row=fila, column=columna, sticky="w", padx=5, pady=1)

        # --- Definir estilo de letra más pequeña ---
        style = ttk.Style()
        style.configure("Small.TRadiobutton", font=("Arial", 9))

        # Botones de etiquetado (más compactos)
        frame_botones_etq = ttk.Frame(frame_etiquetado)
        frame_botones_etq.grid(row=2, column=0, sticky="ew", pady=5)
        
        self.btn_agregar_etiqueta = ttk.Button(frame_botones_etq, text="+ Etiqueta", 
                                            command=self.agregar_etiqueta)
        self.btn_agregar_etiqueta.pack(side="left", padx=2, fill="x", expand=True)
        
        self.btn_eliminar_etiqueta = ttk.Button(frame_botones_etq, text="- Etiqueta", 
                                            command=self.eliminar_etiqueta_selectiva)
        self.btn_eliminar_etiqueta.pack(side="left", padx=2, fill="x", expand=True)
        
        # Botón para agregar etiquetas automáticas
        self.btn_agregar_automaticas = ttk.Button(frame_botones_etq, text="+ Automáticas", 
                                                command=self.agregar_etiquetas_automaticas)
        self.btn_agregar_automaticas.pack(side="left", padx=2, fill="x", expand=True)

        # Etiquetas guardadas
        ttk.Label(frame_etiquetado, text="Guardadas:", font=("Arial", 8, "bold")).grid(
            row=3, column=0, sticky="w", pady=(10, 2)
        )
        
        self.texto_etiquetas_guardadas = scrolledtext.ScrolledText(
            frame_etiquetado, wrap="word", font=("Courier New", 8), height=10
        )
        self.texto_etiquetas_guardadas.grid(row=4, column=0, sticky="nsew", pady=(0, 5))
        self.texto_etiquetas_guardadas.config(state="disabled")

        # Botones inferiores
        frame_botones_inferiores = ttk.Frame(frame_etiquetado)
        frame_botones_inferiores.grid(row=5, column=0, sticky="ew", pady=5)
        
        self.btn_guardar_json = ttk.Button(frame_botones_inferiores, text="Guardar JSON", 
                                        command=self.guardar_json)
        self.btn_guardar_json.pack(side="left", padx=2, fill="x", expand=True)
        
        self.btn_cerrar_abajo = ttk.Button(frame_botones_inferiores, text="Cerrar", 
                                         command=self.cerrar_aplicacion)
        self.btn_cerrar_abajo.pack(side="left", padx=2, fill="x", expand=True)

        # === CONFIGURAR COLORES ===
        for categoria, (_, _, color) in self.CASOS_CONECTORES.items():
            self.texto_original.tag_config(categoria, background=color, foreground="black")
            # Configurar colores también para el texto con IDs
            self.texto_con_ids.tag_config(categoria, background=color, foreground="black")

        # Asegurar que todo se expanda correctamente
        main_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(0, weight=2)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)

    def cerrar_aplicacion(self):
        """Cierra la aplicación"""
        if messagebox.askokcancel("Salir", "¿Estás seguro de que quieres salir?"):
            self.root.destroy()

    def obtener_categoria_seleccionada(self):
        """Obtiene la categoría seleccionada en la lista"""
        return self.etiqueta_seleccionada.get()

    def cargar_datos_desde_json(self):
        """Carga los párrafos y etiquetas existentes desde el JSON."""
        try:
            with open(self.ruta_json, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            # Cargar etiquetas existentes si las hay
            etiquetado = datos.get("document", {}).get("Etiquetado", {})
            self.etiquetas_existentes = etiquetado.get("conectores", {})
            
            # Cargar párrafos desde la estructura del documento
            self.parrafos = []
            self.tokens_por_parrafo = {}
            self.texto_original_por_parrafo = {}
            
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
                texto_parrafo = ""
                texto_con_ids = ""
                tokens_info = []

                # Obtener las oraciones del párrafo
                oraciones_parrafo = parrafo.get("sentence", [])
                
                # Si es una sola oración (diccionario), convertirla a lista
                if isinstance(oraciones_parrafo, dict):
                    oraciones_parrafo = [oraciones_parrafo]
                
                for oracion in oraciones_parrafo:
                    if not oracion:
                        continue
                    
                    # Extraer tokens de la oración
                    tokens = oracion.get("token", [])
                    
                    # Si es un solo token (diccionario), convertirlo a lista
                    if isinstance(tokens, dict):
                        tokens = [tokens]
                    
                    for token in tokens:
                        if isinstance(token, dict):
                            form = token.get("@form", "")
                            token_id = token.get("@id", "")
                            
                            tokens_info.append({
                                'form': form,
                                'id': token_id,
                                'form_lower': form.lower()
                            })
                            
                            texto_parrafo += form + " "
                            texto_con_ids += f"{form}[{token_id}] "

                texto_limpio = texto_parrafo.strip()
                texto_con_ids_limpio = texto_con_ids.strip()
                
                self.parrafos.append(id_parrafo)
                self.tokens_por_parrafo[id_parrafo] = tokens_info
                self.texto_original_por_parrafo[id_parrafo] = texto_limpio
                
                # Detectar conectores automáticamente
                self.detectar_conectores_automaticos(id_parrafo, tokens_info)
            
            if self.parrafos:
                self.crear_botones_parrafos()
                self.mostrar_parrafo_por_id(self.parrafos[0])
                self.actualizar_botones_navegacion()
                
                # Cargar etiquetas existentes - CORREGIDO: asegurar que es diccionario
                self.etiquetas_guardadas = {}
                if isinstance(self.etiquetas_existentes, dict):
                    self.etiquetas_guardadas = self.etiquetas_existentes.copy()
                self.actualizar_etiquetas_guardadas_texto()
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el JSON: {str(e)}")
            print(f"Error detallado: {e}")
    
    def crear_botones_parrafos(self):
        """Crea botones para cada párrafo"""
        for widget in self.frame_botones.winfo_children():
            widget.destroy()
        
        self.botones_parrafos = []
        
        for i, id_parrafo in enumerate(self.parrafos):
            btn = ttk.Button(self.frame_botones, 
                           text=f"Párr {i+1}", 
                           command=lambda p=id_parrafo: self.mostrar_parrafo_por_id(p))
            btn.pack(side=tk.LEFT, padx=1)
            self.botones_parrafos.append(btn)
    
    def detectar_conectores_automaticos(self, id_parrafo, tokens):
        """Detección automática de conectores para resaltado inicial"""
        conectores_encontrados = []
        tokens_utilizados = set()
        
        for conector_info in self.lista_conectores_ordenada:
            palabras_conector = conector_info['palabras']
            longitud = conector_info['longitud']
            
            for i in range(len(tokens) - longitud + 1):
                if any(i + j in tokens_utilizados for j in range(longitud)):
                    continue
                
                coincide = True
                for j in range(longitud):
                    if tokens[i + j]['form_lower'] != palabras_conector[j]:
                        coincide = False
                        break
                
                if coincide:
                    token_ids = [tokens[i + j]['id'] for j in range(longitud)]
                    conectores_encontrados.append({
                        'categoria': conector_info['categoria'],
                        'token_ids': token_ids,
                        'texto': " ".join([tokens[i + j]['form'] for j in range(longitud)])
                    })
                    tokens_utilizados.update(range(i, i + longitud))
        
        self.conectores_detectados[id_parrafo] = conectores_encontrados
    
    def mostrar_parrafo_por_id(self, id_parrafo):
        """Muestra un párrafo específico por su ID"""
        if id_parrafo in self.parrafos:
            self.indice_parrafo_actual = self.parrafos.index(id_parrafo)
            self.mostrar_parrafo_actual()
    
    def mostrar_parrafo_actual(self):
        """Muestra el párrafo actual en las tres columnas"""
        if 0 <= self.indice_parrafo_actual < len(self.parrafos):
            id_parrafo = self.parrafos[self.indice_parrafo_actual]
            self.parrafo_actual = id_parrafo
            tokens = self.tokens_por_parrafo[id_parrafo]
            
            # Actualizar label de navegación
            self.label_parrafo_actual.config(text=f"Párrafo: {self.indice_parrafo_actual + 1}/{len(self.parrafos)} (ID: {id_parrafo})")
            
            # Limpiar todos los textos
            self.texto_original.delete(1.0, tk.END)
            self.texto_con_ids.delete(1.0, tk.END)
            self.lista_tokens.delete(0, tk.END)
            
            # Columna 1: Texto original con conectores resaltados
            texto_original = self.texto_original_por_parrafo[id_parrafo]
            self.texto_original.insert(1.0, texto_original)
            
            # Columna 2: Texto con IDs
            texto_con_ids = ""
            for token in tokens:
                texto_con_ids += f"{token['form']}[{token['id']}] "
            self.texto_con_ids.insert(1.0, texto_con_ids.strip())
            
            # Resaltar conectores en ambos textos
            if id_parrafo in self.conectores_detectados:
                for conector in self.conectores_detectados[id_parrafo]:
                    self.resaltar_conector_texto_original(conector['texto'], conector['categoria'])
                    self.resaltar_conector_texto_con_ids(conector, tokens)
            
            # Columna 3: Lista de tokens seleccionables
            for token in tokens:
                self.lista_tokens.insert(tk.END, f"{token['form']} [{token['id']}]")
            
            # Actualizar etiquetas guardadas para este párrafo
            self.actualizar_etiquetas_guardadas_texto()
    
    def resaltar_conector_texto_original(self, texto_conector, categoria):
        """Resalta un conector en el texto original"""
        start_index = "1.0"
        while True:
            start_index = self.texto_original.search(texto_conector, start_index, tk.END)
            if not start_index:
                break
            
            end_index = f"{start_index}+{len(texto_conector)}c"
            self.texto_original.tag_add(categoria, start_index, end_index)
            start_index = end_index
    
    def resaltar_conector_texto_con_ids(self, conector, tokens):
        """Resalta un conector en el texto con IDs"""
        # Crear el patrón de búsqueda con IDs
        patron_busqueda = ""
        for token_id in conector['token_ids']:
            # Encontrar el token correspondiente
            for token in tokens:
                if token['id'] == token_id:
                    patron_busqueda += f"{token['form']}[{token_id}] "
                    break
        
        patron_busqueda = patron_busqueda.strip()
        
        start_index = "1.0"
        while True:
            start_index = self.texto_con_ids.search(patron_busqueda, start_index, tk.END)
            if not start_index:
                break
            
            end_index = f"{start_index}+{len(patron_busqueda)}c"
            self.texto_con_ids.tag_add(conector['categoria'], start_index, end_index)
            start_index = end_index
    
    def agregar_etiquetas_automaticas(self):
        """Agrega automáticamente las etiquetas de conectores detectados"""
        if not self.parrafo_actual:
            return
        
        if self.parrafo_actual not in self.conectores_detectados:
            return
        
        conectores = self.conectores_detectados[self.parrafo_actual]
        contador = 0
        
        for conector in conectores:
            categoria = conector['categoria']
            
            if categoria not in self.etiquetas_guardadas:
                self.etiquetas_guardadas[categoria] = []
            
            # Agregar el conector como una lista de tokens
            conector_tokens = conector['token_ids']
            
            # Verificar si este conector ya existe
            conector_existente = False
            for conector_guardado in self.etiquetas_guardadas[categoria]:
                if conector_guardado == conector_tokens:
                    conector_existente = True
                    break
            
            if not conector_existente:
                self.etiquetas_guardadas[categoria].append(conector_tokens)
                contador += 1
        
        self.actualizar_etiquetas_guardadas_texto()
        
        if contador > 0:
            messagebox.showinfo("Éxito", f"Se agregaron {contador} conectores automáticamente.", parent=self.root)
    
    def agregar_etiqueta(self):
        """Agrega una nueva etiqueta con los tokens seleccionados como un conector"""
        if not self.parrafo_actual:
            messagebox.showwarning("Advertencia", "No hay párrafo actual seleccionado.", parent=self.root)
            return
        
        seleccionados = self.lista_tokens.curselection()
        if not seleccionados:
            messagebox.showwarning("Advertencia", "Por favor selecciona al menos un token.", parent=self.root)
            return
        
        categoria = self.obtener_categoria_seleccionada()
        if not categoria:
            messagebox.showwarning("Advertencia", "Por favor selecciona una categoría.", parent=self.root)
            return
        
        # Obtener IDs de tokens seleccionados y ordenarlos por posición
        tokens_seleccionados = []
        for index in seleccionados:
            texto_item = self.lista_tokens.get(index)
            token_id = texto_item.split('[')[1].split(']')[0]
            tokens_seleccionados.append(token_id)
        
        # Ordenar tokens por su posición (asumiendo que los IDs reflejan el orden)
        tokens_seleccionados.sort()
        
        # Agregar o actualizar la etiqueta
        if categoria not in self.etiquetas_guardadas:
            self.etiquetas_guardadas[categoria] = []
        
        # Verificar si este conector ya existe
        conector_existente = False
        for conector_guardado in self.etiquetas_guardadas[categoria]:
            if conector_guardado == tokens_seleccionados:
                conector_existente = True
                break
        
        if not conector_existente:
            self.etiquetas_guardadas[categoria].append(tokens_seleccionados)
            messagebox.showinfo("Éxito", f"Conector '{categoria}' agregado con {len(tokens_seleccionados)} tokens.", parent=self.root)
        else:
            messagebox.showwarning("Advertencia", f"Este conector ya existe en la categoría '{categoria}'.", parent=self.root)

        self.lista_tokens.selection_clear(0, tk.END)
        self.actualizar_etiquetas_guardadas_texto()
    

    def eliminar_etiqueta_selectiva(self):
        """Elimina conectores específicos de una etiqueta"""
        if not self.etiquetas_guardadas:
            messagebox.showwarning("Advertencia", "No hay etiquetas para eliminar.")
            return
        
        # Crear ventana de selección para eliminar conectores específicos
        ventana_eliminar = tk.Toplevel(self.root)
        ventana_eliminar.title("Eliminar Conectores")
        ventana_eliminar.geometry("600x400")
        ventana_eliminar.transient(self.root)
        ventana_eliminar.grab_set()
        
        ttk.Label(ventana_eliminar, text="Selecciona los conectores que deseas eliminar:").pack(pady=10)
        
        # Crear notebook (pestañas)
        notebook = ttk.Notebook(ventana_eliminar)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Diccionario para almacenar las listas de conectores por etiqueta
        listas_conectores = {}
        
        # Crear una pestaña por cada etiqueta
        for etiqueta, conectores in self.etiquetas_guardadas.items():
            frame_etiqueta = ttk.Frame(notebook)
            notebook.add(frame_etiqueta, text=etiqueta)
            
            # Label con información
            ttk.Label(frame_etiqueta, text=f"Conectores de la etiqueta '{etiqueta}':").pack(pady=5, anchor="w")
            
            # Listbox para los conectores de esta etiqueta
            lista_conectores = tk.Listbox(frame_etiqueta, height=12, selectmode="multiple")
            lista_conectores.pack(fill=tk.BOTH, expand=True, pady=5)
            
            # Scrollbar
            scroll_conectores = ttk.Scrollbar(lista_conectores, orient="vertical", command=lista_conectores.yview)
            scroll_conectores.pack(side=tk.RIGHT, fill=tk.Y)
            lista_conectores.config(yscrollcommand=scroll_conectores.set)
            
            # Llenar la lista con los conectores de esta etiqueta
            for conector in conectores:
                # Obtener texto del conector
                texto_conector = ""
                if self.parrafo_actual and self.parrafo_actual in self.tokens_por_parrafo:
                    for token_id in conector:
                        for token in self.tokens_por_parrafo[self.parrafo_actual]:
                            if token['id'] == token_id:
                                texto_conector += token['form'] + " "
                                break
                lista_conectores.insert(tk.END, f"{texto_conector.strip()} [{', '.join(conector)}]")
            
            # Guardar referencia a la lista
            listas_conectores[etiqueta] = lista_conectores
        
        def confirmar_eliminacion():
            # Obtener la pestaña activa (etiqueta seleccionada)
            indice_pestaña = notebook.index(notebook.select())
            nombre_etiqueta = list(self.etiquetas_guardadas.keys())[indice_pestaña]
            
            # Obtener la lista de conectores de esta etiqueta
            lista_conectores = listas_conectores[nombre_etiqueta]
            seleccion_conectores = lista_conectores.curselection()
            
            if not seleccion_conectores:
                messagebox.showwarning("Advertencia", f"Selecciona al menos un conector para eliminar de la etiqueta '{nombre_etiqueta}'.")
                return
            
            # Eliminar conectores seleccionados (en orden inverso para evitar problemas de índices)
            for index in reversed(seleccion_conectores):
                if index < len(self.etiquetas_guardadas[nombre_etiqueta]):
                    del self.etiquetas_guardadas[nombre_etiqueta][index]
            
            # Si la etiqueta queda vacía, eliminarla
            if not self.etiquetas_guardadas[nombre_etiqueta]:
                del self.etiquetas_guardadas[nombre_etiqueta]
                messagebox.showinfo("Éxito", f"Se eliminaron {len(seleccion_conectores)} conectores y la etiqueta '{nombre_etiqueta}' quedó vacía, por lo que fue eliminada.")
            else:
                messagebox.showinfo("Éxito", f"Se eliminaron {len(seleccion_conectores)} conectores de la etiqueta '{nombre_etiqueta}'.")
            
            self.actualizar_etiquetas_guardadas_texto()
            ventana_eliminar.destroy()
        
        frame_botones = ttk.Frame(ventana_eliminar)
        frame_botones.pack(pady=10)
        
        ttk.Button(frame_botones, text="Eliminar conectores seleccionados", command=confirmar_eliminacion).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="Cancelar", command=ventana_eliminar.destroy).pack(side=tk.LEFT, padx=5)

    def actualizar_etiquetas_guardadas_texto(self):
        """Actualiza el cuadro de texto con las etiquetas guardadas"""
        self.texto_etiquetas_guardadas.config(state=tk.NORMAL)
        self.texto_etiquetas_guardadas.delete(1.0, tk.END)
        
        if self.etiquetas_guardadas:
            for etiqueta, conectores in self.etiquetas_guardadas.items():
                self.texto_etiquetas_guardadas.insert(tk.END, f"{etiqueta}:\n")
                for i, conector in enumerate(conectores):
                    # Obtener texto del conector
                    texto_conector = ""
                    if self.parrafo_actual and self.parrafo_actual in self.tokens_por_parrafo:
                        for token_id in conector:
                            for token in self.tokens_por_parrafo[self.parrafo_actual]:
                                if token['id'] == token_id:
                                    texto_conector += token['form'] + " "
                                    break
                    self.texto_etiquetas_guardadas.insert(tk.END, f"  {i+1}. {texto_conector.strip()} [{', '.join(conector)}]\n")
                self.texto_etiquetas_guardadas.insert(tk.END, f"  Total: {len(conectores)} conectores\n")
                self.texto_etiquetas_guardadas.insert(tk.END, "-" * 40 + "\n")
        else:
            self.texto_etiquetas_guardadas.insert(tk.END, "No hay etiquetas guardadas.\n")
        
        self.texto_etiquetas_guardadas.config(state=tk.DISABLED)
    
    def anterior_parrafo(self):
        """Navega al párrafo anterior"""
        if self.indice_parrafo_actual > 0:
            self.indice_parrafo_actual -= 1
            self.mostrar_parrafo_actual()
            self.actualizar_botones_navegacion()
    
    def siguiente_parrafo(self):
        """Navega al párrafo siguiente"""
        if self.indice_parrafo_actual < len(self.parrafos) - 1:
            self.indice_parrafo_actual += 1
            self.mostrar_parrafo_actual()
            self.actualizar_botones_navegacion()
    
    def actualizar_botones_navegacion(self):
        """Actualiza el estado de los botones de navegación"""
        self.btn_anterior.config(state="normal" if self.indice_parrafo_actual > 0 else "disabled")
        self.btn_siguiente.config(state="normal" if self.indice_parrafo_actual < len(self.parrafos) - 1 else "disabled")
    
    def guardar_json(self):
        """Guarda las etiquetas en el mismo archivo JSON del proyecto"""
        try:
            if not self.etiquetas_guardadas:
                messagebox.showwarning("Advertencia", "No hay etiquetas para guardar.", parent=self.root)
                return

            # === Crear un mapa de nombre -> código corto ===
            mapa_categorias = {
                nombre: valores[1]  # el segundo elemento es el código corto
                for nombre, valores in self.CASOS_CONECTORES.items()
            }

            # === Traducir etiquetas_guardadas ===
            etiquetas_convertidas = {}
            for categoria, conectores in self.etiquetas_guardadas.items():
                codigo = mapa_categorias.get(categoria, categoria)  # usa código si existe
                etiquetas_convertidas[codigo] = conectores

            # Cargar el JSON existente
            with open(self.ruta_json, 'r', encoding='utf-8') as f:
                datos = json.load(f)

            # Actualizar las etiquetas en el JSON
            if 'document' not in datos:
                datos['document'] = {}
            
            if 'Etiquetado' not in datos['document']:
                datos['document']['Etiquetado'] = {}
            
            datos['document']['Etiquetado']['conectores'] = etiquetas_convertidas

            # Guardar el JSON actualizado
            with open(self.ruta_json, 'w', encoding='utf-8') as f:
                json.dump(datos, f, ensure_ascii=False, indent=2)

            resumen = (
                f"Etiquetas guardadas correctamente.\n"
                f"Archivo: {os.path.basename(self.ruta_json)}\n"
                f"Cantidad de categorías: {len(etiquetas_convertidas)}\n"
                f"Total de conectores: {sum(len(conectores) for conectores in etiquetas_convertidas.values())}"
            )
            messagebox.showinfo("Guardado exitoso", resumen, parent=self.root)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar las etiquetas: {str(e)}", parent=self.root)