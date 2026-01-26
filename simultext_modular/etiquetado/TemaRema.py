import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import etiquetado.config as config


class VentanaEtiquetadoTemaRema:
    """
    Ventana para etiquetado de tema y rema por ORACIÓN.
    Panel izquierdo: texto con tokens (selección múltiple por cursor)
    Panel derecho: interfaz de etiquetado
    """

    def __init__(self, root, ruta_json, tipo_texto):
        self.root = root
        self.root.title("SIMULTEXT - Tema/Rema por Oración")
        self.root.geometry("1600x900")
        self.root.configure(bg=config.COLOR_FONDO)

        self.ruta_json = ruta_json
        self.tipo_texto = tipo_texto

        # Estructuras de datos
        self.tokens_por_oracion = {}  # Cambiado: ahora por oración
        self.token_posiciones = {}
        self.etiquetado_oraciones = {}  # Diccionario: oracion_id -> {tema: [], rema: [], etiqueta: ""}
        self.token_info = {}  # Para mapear token_id -> información completa
        self.oracion_actual = None  # Cambiado: ahora trabajamos con oraciones
        self.tokens_seleccionados = set()
        self.drag_start = None
        
        # Variables para botones de selección única
        self.var_etiqueta_progresion = tk.StringVar()
        self.botones_etiquetas = {}  # Diccionario para manejar botones de etiquetas
        
        # Cargar datos
        self.cargar_datos_desde_json()
        
        # Crear interfaz completa
        self.crear_interfaz()
        
        # Mostrar texto
        self.mostrar_texto()
        
        # Cargar etiquetado existente si existe
        self.cargar_etiquetado_existente()

    # =========================================================
    # CARGA DEL JSON (AHORA POR ORACIÓN)
    # =========================================================
    def cargar_datos_desde_json(self):
        try:
            with open(self.ruta_json, "r", encoding="utf-8") as f:
                self.datos_completos = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo JSON:\n{e}")
            return

        parrafos = self.datos_completos.get("document", {}).get("paragraph", [])
        if isinstance(parrafos, dict):
            parrafos = [parrafos]

        contador_oracion = 0
        
        for parrafo in parrafos:
            if not parrafo:
                continue

            oraciones = parrafo.get("sentence", [])
            if isinstance(oraciones, dict):
                oraciones = [oraciones]

            for oracion in oraciones:
                contador_oracion += 1
                oracion_id = f"s{contador_oracion}"
                
                # Inicializar estructura para esta oración
                self.tokens_por_oracion[oracion_id] = []
                self.etiquetado_oraciones[oracion_id] = {
                    "tema": [], 
                    "rema": [],
                    "etiqueta": ""  # Tipo de progresión
                }

                tokens = oracion.get("token", [])
                if isinstance(tokens, dict):
                    tokens = [tokens]

                for tk_info in tokens:
                    token_id = tk_info.get("@id", "")
                    self.tokens_por_oracion[oracion_id].append({
                        "form": tk_info.get("@form", ""),
                        "id": token_id,
                        "pos": tk_info.get("@pos", ""),
                        "lemma": tk_info.get("@lemma", "")
                    })
                    self.token_info[token_id] = {
                        "form": tk_info.get("@form", ""),
                        "pos": tk_info.get("@pos", ""),
                        "lemma": tk_info.get("@lemma", ""),
                        "oracion": oracion_id  # Cambiado: ahora guardamos oración
                    }

    def cargar_etiquetado_existente(self):
        """Carga el etiquetado de tema/rema existente desde el JSON."""
        try:
            etiquetado = self.datos_completos.get("document", {}).get("Etiquetado", {})
            tema_rema_data = etiquetado.get("tema_rema", {})
            
            if tema_rema_data:
                # Asumimos que la estructura existente ya es por oración
                for oracion_id, etiquetas in tema_rema_data.items():
                    if oracion_id in self.etiquetado_oraciones:
                        self.etiquetado_oraciones[oracion_id]["tema"] = etiquetas.get("tema", [])
                        self.etiquetado_oraciones[oracion_id]["rema"] = etiquetas.get("rema", [])
                        self.etiquetado_oraciones[oracion_id]["etiqueta"] = etiquetas.get("etiqueta", "")
        except Exception as e:
            print(f"Error al cargar etiquetado existente: {e}")

    # =========================================================
    # INTERFAZ COMPLETA
    # =========================================================
    def crear_interfaz(self):
        # Marco principal con dos paneles
        main_frame = tk.Frame(self.root, bg=config.COLOR_FONDO)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Panel izquierdo (60% del ancho)
        left_panel = tk.Frame(main_frame, bg=config.COLOR_FONDO)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Panel derecho (40% del ancho)
        right_panel = tk.Frame(main_frame, bg=config.COLOR_FONDO)
        right_panel.pack(side="right", fill="both", expand=True)

        # ========== PANEL IZQUIERDO: TEXTO ==========
        tk.Label(
            left_panel,
            text="TEXTO PARA ANÁLISIS DE TEMA/REMA POR ORACIÓN",
            font=("Arial", 14, "bold"),
            bg=config.COLOR_FONDO,
            fg=config.COLOR_TITULO
        ).pack(pady=5)

        # Botón para limpiar selección
        frame_seleccion = tk.Frame(left_panel, bg=config.COLOR_FONDO)
        frame_seleccion.pack(fill="x", pady=(0, 5))
        
        tk.Button(
            frame_seleccion,
            text="Limpiar Selección",
            bg=config.COLOR_BOTON_ROJO,
            fg="white",
            font=("Arial", 10),
            command=self.limpiar_seleccion
        ).pack(side="right")

        # Área de texto con scroll
        self.text_area = scrolledtext.ScrolledText(
            left_panel, 
            wrap="word",
            font=("Arial", 12), 
            bg="white", 
            padx=10, 
            pady=10,
            cursor="hand2"  # Cambia el cursor a mano
        )
        self.text_area.pack(fill="both", expand=True)

        # Configurar tags para visualización
        self.text_area.tag_config("token", font=config.FUENTE_TOKEN)
        self.text_area.tag_config("id", font=config.FUENTE_TOKEN_ID)
        self.text_area.tag_config("tema", background=config.COLOR_TEMA, foreground="black")
        self.text_area.tag_config("rema", background=config.COLOR_REMA, foreground="black")
        self.text_area.tag_config("seleccionado", background=config.COLOR_SELECCIONADO, foreground="black")
        self.text_area.tag_config("oracion_actual", background="#E6F3FF", relief="ridge", borderwidth=1)

        # Bind eventos del mouse para selección múltiple
        self.text_area.bind("<Button-1>", self.on_text_click_start)
        self.text_area.bind("<B1-Motion>", self.on_text_drag)
        self.text_area.bind("<ButtonRelease-1>", self.on_text_click_end)
        self.text_area.bind("<Control-Button-1>", self.on_text_ctrl_click)  # Ctrl+click para añadir
        self.text_area.bind("<Button-3>", self.on_text_right_click)  # Click derecho para menú contextual

        # ========== PANEL DERECHO: ETIQUETADO ==========
        # Título del panel derecho
        tk.Label(
            right_panel,
            text="ETIQUETADO TEMA/REMA POR ORACIÓN",
            font=("Arial", 14, "bold"),
            bg=config.COLOR_FONDO,
            fg=config.COLOR_TITULO
        ).pack(pady=5)

        # Frame para selección de oración con botones
        frame_oracion = tk.Frame(right_panel, bg=config.COLOR_FONDO)
        frame_oracion.pack(fill="x", pady=(0, 10))

        tk.Label(
            frame_oracion,
            text="Seleccionar Oración:",
            font=("Arial", 11, "bold"),
            bg=config.COLOR_FONDO
        ).pack(anchor="w", pady=(0, 5))

        # Frame para botones de oraciones con scroll
        frame_botones_oraciones = tk.Frame(frame_oracion, bg=config.COLOR_FONDO)
        frame_botones_oraciones.pack(fill="x", pady=(0, 10))

        # Canvas y scrollbar para botones de oraciones
        self.canvas_oraciones = tk.Canvas(frame_botones_oraciones, bg=config.COLOR_FONDO, height=50)
        scrollbar_oraciones = tk.Scrollbar(frame_botones_oraciones, orient="horizontal", command=self.canvas_oraciones.xview)
        
        # Frame interno para los botones
        self.frame_botones_interno = tk.Frame(self.canvas_oraciones, bg=config.COLOR_FONDO)
        
        # Configurar canvas
        self.canvas_oraciones.configure(xscrollcommand=scrollbar_oraciones.set)
        self.canvas_oraciones_window = self.canvas_oraciones.create_window((0, 0), window=self.frame_botones_interno, anchor="nw")
        
        self.canvas_oraciones.pack(side="top", fill="x", expand=True)
        scrollbar_oraciones.pack(side="bottom", fill="x")
        
        # Configurar el frame interno para ajustar tamaño
        self.frame_botones_interno.bind("<Configure>", self.on_frame_configure_oraciones)
        
        # Crear botones de oraciones
        self.botones_oraciones = {}
        for oracion_id in sorted(self.tokens_por_oracion.keys(), 
                                 key=lambda x: int(x[1:]) if x[1:].isdigit() else 0):
            btn = tk.Button(
                self.frame_botones_interno,
                text=f"Oración {oracion_id[1:]}",
                bg=config.COLOR_BOTON_AZUL,
                fg="white",
                font=("Arial", 10),
                width=12,
                command=lambda oid=oracion_id: self.seleccionar_oracion(oid)
            )
            btn.pack(side="left", padx=2, pady=2)
            self.botones_oraciones[oracion_id] = btn
        
        # Botón para nueva oración
        tk.Button(
            frame_oracion,
            text="+ NUEVA ORACIÓN",
            bg=config.COLOR_BOTON_VERDE,
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.nueva_oracion,
            width=15
        ).pack(side="left", padx=(0, 10))
        
        # Botón para limpiar etiquetado de la oración actual
        tk.Button(
            frame_oracion,
            text="Limpiar Oración",
            bg=config.COLOR_BOTON_ROJO,
            fg="white",
            font=("Arial", 10),
            command=self.limpiar_oracion_actual,
            width=12
        ).pack(side="right")

        # Frame para información de selección
        frame_seleccion_info = tk.Frame(right_panel, bg=config.COLOR_FONDO)
        frame_seleccion_info.pack(fill="x", pady=(0, 10))

        tk.Label(
            frame_seleccion_info,
            text="Tokens seleccionados:",
            font=("Arial", 11, "bold"),
            bg=config.COLOR_FONDO
        ).grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.label_seleccion_info = tk.Label(
            frame_seleccion_info,
            text="0 tokens",
            font=("Arial", 11),
            bg=config.COLOR_FONDO,
            fg="#555555"
        )
        self.label_seleccion_info.grid(row=0, column=1, sticky="w")

        # Frame para botones de etiquetado rápido
        frame_botones_rapidos = tk.Frame(right_panel, bg=config.COLOR_FONDO)
        frame_botones_rapidos.pack(fill="x", pady=(0, 10))

        tk.Label(
            frame_botones_rapidos,
            text="Etiquetado Rápido:",
            font=("Arial", 11, "bold"),
            bg=config.COLOR_FONDO
        ).pack(anchor="w", pady=(0, 5))

        # Botones para etiquetado rápido
        frame_botones_accion = tk.Frame(frame_botones_rapidos, bg=config.COLOR_FONDO)
        frame_botones_accion.pack(fill="x")

        tk.Button(
            frame_botones_accion,
            text="+ TEMA",
            bg=config.COLOR_BOTON_TEMA,
            fg="black",
            font=("Arial", 11, "bold"),
            command=self.agregar_tema,
            width=12,
            height=2
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            frame_botones_accion,
            text="+ REMA",
            bg=config.COLOR_BOTON_REMA,
            fg="black",
            font=("Arial", 11, "bold"),
            command=self.agregar_rema,
            width=12,
            height=2
        ).pack(side="left")



        # Frame para selección de etiqueta de progresión (BOTONES)
        frame_etiqueta = tk.Frame(right_panel, bg=config.COLOR_FONDO)
        frame_etiqueta.pack(fill="x", pady=(0, 10))

        tk.Label(
            frame_etiqueta,
            text="Etiqueta de Progresión:",
            font=("Arial", 11, "bold"),
            bg=config.COLOR_FONDO
        ).pack(anchor="w", pady=(0, 5))

        # Frame para botones de etiquetas (selección única)
        frame_botones_etiquetas = tk.Frame(frame_etiqueta, bg=config.COLOR_FONDO)
        frame_botones_etiquetas.pack(fill="x", pady=(0, 5))
        
        # Crear botones para cada tipo de etiqueta
        for nombre, valor in config.TIPOS_PROGRESION:
            # Crear variable para este botón
            btn = tk.Radiobutton(
                frame_botones_etiquetas,
                text=nombre,
                variable=self.var_etiqueta_progresion,
                value=valor,
                command=self.aplicar_etiqueta_desde_boton,
                bg=config.COLOR_FONDO,
                font=("Arial", 8),
                indicatoron=0,  # Botón estilo botón, no círculo de radio
                width=28,
                height=2
            )
            btn.pack(side="left", padx=2, pady=2)
            self.botones_etiquetas[valor] = btn
        
        # Botón para limpiar etiqueta
        tk.Button(
            frame_etiqueta,
            text="Limpiar Etiqueta",
            bg="#999999",
            fg="white",
            font=("Arial", 10),
            command=self.limpiar_etiqueta,
            width=15
        ).pack(side="right", pady=(5, 0))

        # Frame para visualización de etiquetado actual
        frame_etiquetado = tk.Frame(right_panel, bg=config.COLOR_FONDO)
        frame_etiquetado.pack(fill="both", expand=True, pady=(0, 5))

        tk.Label(
            frame_etiquetado,
            text="Etiquetado Actual de la Oración:",
            font=("Arial", 11, "bold"),
            bg=config.COLOR_FONDO
        ).pack(anchor="w", pady=(0, 5))

        # Área para mostrar tokens etiquetados
        self.etiquetado_area = scrolledtext.ScrolledText(
            frame_etiquetado,
            wrap="word",
            font=("Arial", 11),
            bg="white",
            height=7,
            padx=10,
            pady=10
        )
        self.etiquetado_area.pack(fill="both", expand=True)
        self.etiquetado_area.config(state="disabled")

        # ========== BOTONES DE GUARDAR/CANCELAR ==========
        frame_botones_etiquetado = tk.Frame(frame_etiquetado, bg=config.COLOR_FONDO)
        frame_botones_etiquetado.pack(fill="x", pady=(10, 0))
        
        # Botón GUARDAR TODO - más prominente
        tk.Button(
            frame_botones_etiquetado,
            text="GUARDAR TODO",
            bg=config.COLOR_BOTON_VERDE,
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.guardar_en_json,
            width=20,
            height=2
        ).pack(side="left", padx=(0, 20))
        
        # Botón CERRAR
        tk.Button(
            frame_botones_etiquetado,
            text="CANCELAR",
            bg=config.COLOR_BOTON_ROJO,
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.root.destroy,
            width=15,
            height=2
        ).pack(side="right")

        # Establecer primera oración como seleccionada
        if self.tokens_por_oracion:
            primera_oracion = list(self.tokens_por_oracion.keys())[0]
            self.seleccionar_oracion(primera_oracion)

    def on_frame_configure_oraciones(self, event):
        """Ajusta el scrollregion del canvas cuando cambia el tamaño del frame interno."""
        self.canvas_oraciones.configure(scrollregion=self.canvas_oraciones.bbox("all"))

    # =========================================================
    # FUNCIONES PARA MOSTRAR TEXTO
    # =========================================================
    def mostrar_texto(self):
        self.text_area.config(state="normal")
        self.text_area.delete("1.0", tk.END)

        # Limpiar posiciones anteriores
        self.token_posiciones = {}

        contador_oracion = 0
        for oracion_id, tokens in self.tokens_por_oracion.items():
            contador_oracion += 1
            self.text_area.insert(tk.END, f"\nORACIÓN {oracion_id.upper()}\n")

            for tk_info in tokens:
                palabra = tk_info["form"]
                tid = tk_info["id"]

                # Guardar posición de inicio del token
                inicio = self.text_area.index("end-1c")

                # Insertar palabra con tag especial para identificación
                tag_token = f"token_{tid}"
                self.text_area.tag_config(tag_token, font=config.FUENTE_TOKEN)
                self.text_area.insert(tk.END, palabra, (tag_token, "token"))

                # Insertar ID
                self.text_area.insert(tk.END, f"({tid}) ", "id")

                # Guardar posición del token
                pos_inicio = self.text_area.index(f"{inicio}")
                pos_fin = self.text_area.index(f"{inicio}+{len(palabra)}c")
                self.token_posiciones[tid] = {
                    "inicio": pos_inicio,
                    "fin": pos_fin,
                    "tag": tag_token,
                    "oracion": oracion_id
                }

            self.text_area.insert(tk.END, "\n\n")

        # Aplicar colores según etiquetado existente
        self.resaltar_etiquetado_en_texto()
        
        self.text_area.config(state="disabled")

    def resaltar_etiquetado_en_texto(self):
        """Resalta los tokens etiquetados en el texto."""
        for oracion_id, etiquetas in self.etiquetado_oraciones.items():
            # Resaltar tokens de tema
            for token_id in etiquetas["tema"]:
                if token_id in self.token_posiciones:
                    pos = self.token_posiciones[token_id]
                    self.text_area.tag_add("tema", pos["inicio"], pos["fin"])
            
            # Resaltar tokens de rema
            for token_id in etiquetas["rema"]:
                if token_id in self.token_posiciones:
                    pos = self.token_posiciones[token_id]
                    self.text_area.tag_add("rema", pos["inicio"], pos["fin"])

    def resaltar_oracion_actual(self):
        """Resalta visualmente la oración actualmente seleccionada."""
        # Primero limpiar cualquier resaltado anterior
        self.text_area.tag_remove("oracion_actual", "1.0", tk.END)
        
        if not self.oracion_actual:
            return
        
        # Buscar dónde empieza y termina la oración en el texto
        # Buscamos el encabezado de la oración
        start_pattern = f"\nORACIÓN {self.oracion_actual.upper()}\n"
        start_index = self.text_area.search(start_pattern, "1.0", tk.END)
        
        if start_index:
            # Encontrar dónde termina esta oración (buscar siguiente ORACIÓN)
            end_search = self.text_area.index(f"{start_index}+1c")
            end_index = self.text_area.search("\nORACIÓN ", end_search, tk.END)
            
            if not end_index:
                # Si no hay más oraciones, ir al final
                end_index = tk.END
            else:
                # Retroceder un poco para no incluir el encabezado de la siguiente
                end_index = self.text_area.index(f"{end_index}-1c")
            
            # Aplicar el resaltado
            self.text_area.tag_add("oracion_actual", start_index, end_index)

    # =========================================================
    # MANEJO DE EVENTOS DEL MOUSE (SELECCIÓN MÚLTIPLE)
    # =========================================================
    def on_text_click_start(self, event):
        """Inicia la selección al hacer clic."""
        # Limpiar selección anterior si no se está presionando Ctrl
        if not event.state & 0x4:  # Si Ctrl no está presionado
            self.limpiar_seleccion()
        
        self.drag_start = f"@{event.x},{event.y}"
        # Procesar el clic inicial
        self.procesar_seleccion_en_punto(self.drag_start)

    def on_text_drag(self, event):
        """Maneja el arrastre para selección múltiple."""
        if not self.drag_start:
            return
            
        # Limpiar selección temporal
        self.text_area.tag_remove("seleccion_temp", "1.0", tk.END)
        
        # Obtener punto final del arrastre
        drag_end = f"@{event.x},{event.y}"
        
        # Crear selección temporal durante el arrastre
        if self.text_area.compare(self.drag_start, "<", drag_end):
            self.text_area.tag_add("seleccion_temp", self.drag_start, drag_end)
        else:
            self.text_area.tag_add("seleccion_temp", drag_end, self.drag_start)
        
        # Configurar tag temporal
        self.text_area.tag_config("seleccion_temp", background="#FFCCCC", foreground="black")

    def on_text_click_end(self, event):
        """Finaliza la selección al soltar el clic."""
        if not self.drag_start:
            return
            
        drag_end = f"@{event.x},{event.y}"
        
        # Obtener todos los tokens en el rango seleccionado
        start_index = self.drag_start
        end_index = drag_end
        
        # Asegurarse de que start_index < end_index
        if self.text_area.compare(start_index, ">", end_index):
            start_index, end_index = end_index, start_index
        
        # Buscar tokens en el texto seleccionado
        tokens_en_rango = []
        
        # Recorrer todas las posiciones de tokens
        for token_id, pos in self.token_posiciones.items():
            # Verificar si el token está dentro del rango seleccionado
            if (self.text_area.compare(pos["inicio"], ">=", start_index) and
                self.text_area.compare(pos["inicio"], "<=", end_index)):
                tokens_en_rango.append(token_id)
        
        # Agregar tokens al conjunto de selección
        for token_id in tokens_en_rango:
            self.tokens_seleccionados.add(token_id)
            # Resaltar token
            pos = self.token_posiciones[token_id]
            self.text_area.tag_add("seleccionado", pos["inicio"], pos["fin"])
        
        # Limpiar selección temporal
        self.text_area.tag_remove("seleccion_temp", "1.0", tk.END)
        
        # Actualizar información de selección
        self.actualizar_info_seleccion()
        
        self.drag_start = None

    def on_text_ctrl_click(self, event):
        """Añade o quita tokens individuales con Ctrl+clic."""
        index = f"@{event.x},{event.y}"
        self.procesar_seleccion_en_punto(index)

    def on_text_right_click(self, event):
        """Menú contextual para selección rápida."""
        # Crear menú emergente
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Seleccionar toda la oración actual", 
                        command=self.seleccionar_toda_oracion_actual)
        menu.add_command(label="Limpiar selección", 
                        command=self.limpiar_seleccion)
        menu.add_separator()
        menu.add_command(label="Etiquetar como TEMA", 
                        command=self.agregar_tema)
        menu.add_command(label="Etiquetar como REMA", 
                        command=self.agregar_rema)
        
        # Mostrar menú en posición del clic
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def procesar_seleccion_en_punto(self, index):
        """Procesa la selección en un punto específico."""
        # Buscar token en el punto del clic
        token_encontrado = None
        for token_id, pos in self.token_posiciones.items():
            if self.posicion_en_rango(index, pos["inicio"], pos["fin"]):
                token_encontrado = token_id
                break
        
        if token_encontrado:
            # Alternar selección (agregar si no está, quitar si está)
            if token_encontrado in self.tokens_seleccionados:
                self.tokens_seleccionados.remove(token_encontrado)
                # Quitar resaltado
                pos = self.token_posiciones[token_encontrado]
                self.text_area.tag_remove("seleccionado", pos["inicio"], pos["fin"])
            else:
                self.tokens_seleccionados.add(token_encontrado)
                # Aplicar resaltado
                pos = self.token_posiciones[token_encontrado]
                self.text_area.tag_add("seleccionado", pos["inicio"], pos["fin"])
            
            # Actualizar información de selección
            self.actualizar_info_seleccion()

    def seleccionar_toda_oracion_actual(self):
        """Selecciona todos los tokens de la oración actual."""
        if not self.oracion_actual:
            return
        
        # Limpiar selección anterior
        self.limpiar_seleccion()
        
        # Seleccionar todos los tokens de la oración actual
        for token_id, pos in self.token_posiciones.items():
            if pos["oracion"] == self.oracion_actual:
                self.tokens_seleccionados.add(token_id)
                self.text_area.tag_add("seleccionado", pos["inicio"], pos["fin"])
        
        # Actualizar información
        self.actualizar_info_seleccion()

    def limpiar_seleccion(self):
        """Limpia la selección visual actual."""
        self.text_area.tag_remove("seleccionado", "1.0", tk.END)
        self.text_area.tag_remove("seleccion_temp", "1.0", tk.END)
        self.tokens_seleccionados.clear()
        self.actualizar_info_seleccion()

    def actualizar_info_seleccion(self):
        """Actualiza la información de tokens seleccionados."""
        count = len(self.tokens_seleccionados)
        if count == 0:
            self.label_seleccion_info.config(text="0 tokens")
        elif count == 1:
            token_id = next(iter(self.tokens_seleccionados))
            if token_id in self.token_info:
                token = self.token_info[token_id]
                self.label_seleccion_info.config(
                    text=f"1 token: '{token['form']}' ({token_id})"
                )
        else:
            # Mostrar primeros 3 tokens como ejemplo
            sample_tokens = []
            for i, token_id in enumerate(list(self.tokens_seleccionados)[:3]):
                if token_id in self.token_info:
                    sample_tokens.append(f"'{self.token_info[token_id]['form']}'")
            
            sample_text = ", ".join(sample_tokens)
            if count > 3:
                sample_text += f"... (+{count-3} más)"
            
            self.label_seleccion_info.config(
                text=f"{count} tokens: {sample_text}"
            )

    def posicion_en_rango(self, pos, inicio, fin):
        """Verifica si una posición está dentro de un rango."""
        return self.text_area.compare(pos, ">=", inicio) and self.text_area.compare(pos, "<=", fin)

    # =========================================================
    # FUNCIONES DE GESTIÓN DE ORACIONES (CON BOTONES)
    # =========================================================
    def seleccionar_oracion(self, oracion_id):
        """Selecciona una oración usando botones."""
        self.oracion_actual = oracion_id
        
        # Actualizar apariencia de botones
        for oid, btn in self.botones_oraciones.items():
            if oid == oracion_id:
                btn.config(bg=config.COLOR_BOTON_ACTIVO, fg="white")
            else:
                btn.config(bg=config.COLOR_BOTON_AZUL, fg="white")
        
        # Actualizar etiqueta de progresión
        if self.oracion_actual in self.etiquetado_oraciones:
            etiqueta_actual = self.etiquetado_oraciones[self.oracion_actual].get("etiqueta", "")
            if etiqueta_actual:
                self.var_etiqueta_progresion.set(etiqueta_actual)
                # Resaltar botón seleccionado
                for valor, btn in self.botones_etiquetas.items():
                    if valor == etiqueta_actual:
                        btn.config(bg=config.COLOR_BOTON_ACTIVO, fg="white")
                    else:
                        btn.config(bg=config.COLOR_FONDO, fg="black")
            else:
                self.var_etiqueta_progresion.set("")
                # Deseleccionar todos los botones de etiquetas
                for btn in self.botones_etiquetas.values():
                    btn.config(bg=config.COLOR_FONDO, fg="black")
        
        self.actualizar_vista_etiquetado()
        self.limpiar_seleccion()
        self.resaltar_oracion_actual()

    def nueva_oracion(self):
        """Crea una nueva oración para etiquetado."""
        # Determinar el siguiente ID de oración
        oraciones_existentes = list(self.tokens_por_oracion.keys())
        if oraciones_existentes:
            # Encontrar el máximo número de oración existente
            numeros = []
            for oracion_id in oraciones_existentes:
                if oracion_id.startswith("s"):
                    try:
                        numero = int(oracion_id[1:])
                        numeros.append(numero)
                    except:
                        pass
            
            if numeros:
                nuevo_numero = max(numeros) + 1
            else:
                nuevo_numero = len(oraciones_existentes) + 1
        else:
            nuevo_numero = 1
        
        nuevo_id = f"s{nuevo_numero}"
        
        # Crear nueva entrada en las estructuras de datos
        self.tokens_por_oracion[nuevo_id] = []
        self.etiquetado_oraciones[nuevo_id] = {
            "tema": [], 
            "rema": [],
            "etiqueta": ""
        }
        
        # Crear nuevo botón
        btn = tk.Button(
            self.frame_botones_interno,
            text=f"Oración {nuevo_numero}",
            bg=config.COLOR_BOTON_AZUL,
            fg="white",
            font=("Arial", 10),
            width=12,
            command=lambda: self.seleccionar_oracion(nuevo_id)
        )
        btn.pack(side="left", padx=2, pady=2)
        self.botones_oraciones[nuevo_id] = btn
        
        # Seleccionar la nueva oración
        self.seleccionar_oracion(nuevo_id)
        
        messagebox.showinfo("Nueva Oración", 
                          f"Se ha creado la oración {nuevo_id}.\n\n"
                          f"Ahora puedes seleccionar tokens de cualquier parte del texto "
                          f"y etiquetarlos para esta oración.")

    def aplicar_etiqueta_desde_boton(self):
        """Aplica la etiqueta de progresión seleccionada desde botón."""
        if not self.oracion_actual:
            messagebox.showwarning("Advertencia", "Por favor, seleccione una oración.")
            return
        
        etiqueta_valor = self.var_etiqueta_progresion.get()
        if not etiqueta_valor:
            # Si está vacío, eliminar la etiqueta
            self.etiquetado_oraciones[self.oracion_actual]["etiqueta"] = ""
        else:
            # Aplicar etiqueta
            self.etiquetado_oraciones[self.oracion_actual]["etiqueta"] = etiqueta_valor
        
        self.actualizar_vista_etiquetado()

    def limpiar_etiqueta(self):
        """Limpia la etiqueta de progresión actual."""
        self.var_etiqueta_progresion.set("")
        if self.oracion_actual:
            self.etiquetado_oraciones[self.oracion_actual]["etiqueta"] = ""
            self.actualizar_vista_etiquetado()
        
        # Deseleccionar todos los botones de etiquetas
        for btn in self.botones_etiquetas.values():
            btn.config(bg=config.COLOR_FONDO, fg="black")

    # =========================================================
    # FUNCIONES DE ETIQUETADO (SIN FILTRO POR ORACIÓN)
    # =========================================================
    def agregar_tema(self):
        """Agrega los tokens seleccionados a la lista de tema de la oración actual."""
        self.agregar_tokens_seleccionados("tema")

    def agregar_rema(self):
        """Agrega los tokens seleccionados a la lista de rema de la oración actual."""
        self.agregar_tokens_seleccionados("rema")

    def agregar_tokens_seleccionados(self, tipo):
        """Agrega los tokens seleccionados como tema o rema de la oración actual."""
        if not self.tokens_seleccionados:
            messagebox.showwarning("Advertencia", "Por favor, seleccione al menos un token.")
            return
        
        if not self.oracion_actual:
            messagebox.showwarning("Advertencia", "Por favor, seleccione una oración.")
            return
        
        tokens_agregados = 0
        tokens_movidos = 0
        
        otro_tipo = "rema" if tipo == "tema" else "tema"
        
        for token_id in list(self.tokens_seleccionados):
            # IMPORTANTE: Ya no verificamos la oración del token
            
            # Verificar si el token ya está etiquetado en OTRA oración
            for oracion_id, etiquetas in self.etiquetado_oraciones.items():
                if oracion_id != self.oracion_actual:
                    # Remover de tema de otras oraciones
                    if token_id in etiquetas["tema"]:
                        etiquetas["tema"].remove(token_id)
                    
                    # Remover de rema de otras oraciones
                    if token_id in etiquetas["rema"]:
                        etiquetas["rema"].remove(token_id)
            
            # Verificar que no esté ya etiquetado en el otro grupo de ESTA oración
            if token_id in self.etiquetado_oraciones[self.oracion_actual][otro_tipo]:
                self.etiquetado_oraciones[self.oracion_actual][otro_tipo].remove(token_id)
                tokens_movidos += 1
            
            # Agregar si no está ya en la lista
            if token_id not in self.etiquetado_oraciones[self.oracion_actual][tipo]:
                self.etiquetado_oraciones[self.oracion_actual][tipo].append(token_id)
                tokens_agregados += 1
        
        # Actualizar interfaces
        self.actualizar_vista_etiquetado()
        self.resaltar_etiquetado_en_texto()
        
        # Limpiar selección después de etiquetar
        self.limpiar_seleccion()
        
        # Mostrar mensaje informativo
        info_text = f"{tokens_agregados} token(s) etiquetados como {tipo.upper()}"
        if tokens_movidos > 0:
            info_text += f" ({tokens_movidos} movidos de {otro_tipo.upper()})"
        
        self.label_seleccion_info.config(text=info_text, fg="#006600")


    def limpiar_oracion_actual(self):
        """Limpia todo el etiquetado de la oración actual."""
        if not self.oracion_actual:
            return
        
        respuesta = messagebox.askyesno(
            "Confirmar",
            f"¿Está seguro de que desea limpiar todo el etiquetado de la oración {self.oracion_actual}?", parent = self.root
        )
        
        if respuesta:
            self.etiquetado_oraciones[self.oracion_actual] = {
                "tema": [], 
                "rema": [],
                "etiqueta": ""
            }
            self.var_etiqueta_progresion.set("")
            self.actualizar_vista_etiquetado()
            # Limpiar resaltado en texto para tokens de esta oración
            for token_id in self.tokens_por_oracion.get(self.oracion_actual, []):
                token_id_val = token_id["id"]
                if token_id_val in self.token_posiciones:
                    pos = self.token_posiciones[token_id_val]
                    self.text_area.tag_remove("tema", pos["inicio"], pos["fin"])
                    self.text_area.tag_remove("rema", pos["inicio"], pos["fin"])
            
            # Deseleccionar botones de etiquetas
            for btn in self.botones_etiquetas.values():
                btn.config(bg=config.COLOR_FONDO, fg="black")
            
            self.limpiar_seleccion()

    def actualizar_vista_etiquetado(self):
        """Actualiza el área que muestra el etiquetado actual."""
        self.etiquetado_area.config(state="normal")
        self.etiquetado_area.delete("1.0", tk.END)
        
        if not self.oracion_actual:
            return
        
        etiquetas = self.etiquetado_oraciones[self.oracion_actual]
        
        # Mostrar etiqueta de progresión
        if etiquetas["etiqueta"]:
            nombre_etiqueta = config.ETIQUETAS_PROGRESION.get(
                etiquetas["etiqueta"], 
                etiquetas["etiqueta"]
            )
            self.etiquetado_area.insert(tk.END, f"ETIQUETA: {nombre_etiqueta}\n\n", "titulo")
        
        # Mostrar tokens de tema
        self.etiquetado_area.insert(tk.END, "TEMA:\n", "subtitulo")
        if etiquetas["tema"]:
            tokens_tema = []
            for token_id in etiquetas["tema"]:
                if token_id in self.token_info:
                    token = self.token_info[token_id]
                    # Mostrar de qué oración original viene el token
                    oracion_original = token['oracion']
                    tokens_tema.append(f"  • {token_id}: '{token['form']}' (oración original: {oracion_original})")
            self.etiquetado_area.insert(tk.END, "\n".join(tokens_tema) + "\n\n")
        else:
            self.etiquetado_area.insert(tk.END, "  No hay tokens etiquetados como tema.\n\n")
        
        # Mostrar tokens de rema
        self.etiquetado_area.insert(tk.END, "REMA:\n", "subtitulo")
        if etiquetas["rema"]:
            tokens_rema = []
            for token_id in etiquetas["rema"]:
                if token_id in self.token_info:
                    token = self.token_info[token_id]
                    # Mostrar de qué oración original viene el token
                    oracion_original = token['oracion']
                    tokens_rema.append(f"  • {token_id}: '{token['form']}' (oración original: {oracion_original})")
            self.etiquetado_area.insert(tk.END, "\n".join(tokens_rema))
        else:
            self.etiquetado_area.insert(tk.END, "  No hay tokens etiquetados como rema.")
        
        self.etiquetado_area.config(state="disabled")
        # Configurar tags para títulos
        self.etiquetado_area.tag_config("titulo", font=("Arial", 11, "bold"), foreground=config.COLOR_TITULO)
        self.etiquetado_area.tag_config("subtitulo", font=("Arial", 11, "bold"))

    # =========================================================
    # GUARDAR EN JSON - VERSIÓN SIMPLIFICADA
    # =========================================================
    def guardar_en_json(self):
        """
        Guarda el etiquetado actual DESDE LA MEMORIA al archivo JSON,
        usando la nueva estructura {tema: [], rema: [], etiqueta: ""}
        """
        try:
            # ==============================================
            # 1. OBTENER DATOS ACTUALES DESDE LA MEMORIA
            # ==============================================
            etiquetado_filtrado = {}
            oraciones_con_etiquetado = 0
            
            # Filtrar solo oraciones que tienen algún etiquetado
            for oracion_id, etiquetas in self.etiquetado_oraciones.items():
                # Verificar si tiene etiquetado (tema, rema o etiqueta)
                tiene_etiquetado = (
                    len(etiquetas["tema"]) > 0 or 
                    len(etiquetas["rema"]) > 0 or 
                    etiquetas["etiqueta"] != ""
                )
                
                if tiene_etiquetado:
                    oraciones_con_etiquetado += 1
                    etiquetado_filtrado[oracion_id] = {
                        "tema": etiquetas["tema"].copy(),  # Usar copia para seguridad
                        "rema": etiquetas["rema"].copy(),
                        "etiqueta": etiquetas["etiqueta"]
                    }
            
            # Si no hay nada etiquetado, preguntar si quiere guardar vacío
            if oraciones_con_etiquetado == 0:
                respuesta = messagebox.askyesno(
                    "Sin etiquetado",
                    "No hay ninguna etiqueta de tema/rema asignada.\n\n"
                    "¿Desea guardar una estructura vacía?"
                )
                if not respuesta:
                    return
            
            # ==============================================
            # 2. PREPARAR LA ESTRUCTURA JSON COMPLETA
            # ==============================================
            # Primero, cargar los datos originales del archivo
            try:
                with open(self.ruta_json, "r", encoding="utf-8") as f:
                    datos_completos = json.load(f)
            except FileNotFoundError:
                # Si el archivo no existe, crear estructura nueva
                datos_completos = {"document": {}}
            except json.JSONDecodeError as e:
                messagebox.showerror(
                    "Error en archivo JSON", 
                    f"El archivo {self.ruta_json} tiene formato JSON inválido:\n{e}",
                    parent=self.root
                )
                return
            
            # Asegurar estructura básica
            if "document" not in datos_completos:
                datos_completos["document"] = {}
            
            # Crear o actualizar la sección Etiquetado
            if "Etiquetado" not in datos_completos["document"]:
                datos_completos["document"]["Etiquetado"] = {}
            
            # Actualizar SOLO la sección tema_rema, manteniendo otras secciones de Etiquetado
            datos_completos["document"]["Etiquetado"]["tema_rema"] = etiquetado_filtrado
            
            # ==============================================
            # 3. GUARDAR EN DISCO
            # ==============================================
            try:
                # Convertir a JSON formateado
                json_final = json.dumps(datos_completos, ensure_ascii=False, indent=2)
                
                # Hacer backup del archivo original si existe
                import os
                import shutil
                if os.path.exists(self.ruta_json):
                    backup_path = self.ruta_json + ".backup"
                    shutil.copy2(self.ruta_json, backup_path)
                    print(f"Backup creado: {backup_path}")
                
                # Guardar el archivo
                with open(self.ruta_json, "w", encoding="utf-8") as f:
                    f.write(json_final)
                    
            except PermissionError:
                messagebox.showerror(
                    "Error de permisos",
                    f"No tiene permisos para escribir en:\n{self.ruta_json}\n\n"
                    f"Por favor, cierre el archivo si está abierto en otro programa.",
                    parent=self.root
                )
                return
            except Exception as e:
                messagebox.showerror(
                    "Error de escritura",
                    f"No se pudo guardar el archivo:\n{e}",
                    parent=self.root
                )
                return
            
            # ==============================================
            # 4. MOSTRAR CONFIRMACIÓN
            # ==============================================
            # Calcular estadísticas para el mensaje
            total_tokens_tema = sum(len(v["tema"]) for v in etiquetado_filtrado.values())
            total_tokens_rema = sum(len(v["rema"]) for v in etiquetado_filtrado.values())
            oraciones_con_progresion = sum(
                1 for v in etiquetado_filtrado.values() if v["etiqueta"]
            )
            
            # Preparar mensaje de confirmación
            mensaje = f"✅ ETIQUETADO GUARDADO EXITOSAMENTE\n\n"
            mensaje += f"📁 Archivo: {self.ruta_json}\n"
            mensaje += f"📊 Estadísticas:\n"
            mensaje += f"   • Oraciones etiquetadas: {oraciones_con_etiquetado}\n"
            mensaje += f"   • Tokens TEMA: {total_tokens_tema}\n"
            mensaje += f"   • Tokens REMA: {total_tokens_rema}\n"
            mensaje += f"   • Oraciones con progresión: {oraciones_con_progresion}\n"
            
            # Listar oraciones guardadas (máximo 5)
            if oraciones_con_etiquetado > 0:
                mensaje += f"\n📋 Oraciones guardadas:\n"
                for i, oracion_id in enumerate(list(etiquetado_filtrado.keys())[:5]):
                    etiqueta = etiquetado_filtrado[oracion_id]["etiqueta"]
                    if not etiqueta:
                        etiqueta = "Sin etiqueta"
                    mensaje += f"   {oracion_id}: {etiqueta}\n"
                
                if oraciones_con_etiquetado > 5:
                    mensaje += f"   ... y {oraciones_con_etiquetado - 5} más\n"
            
            # Mostrar advertencia si hay oración actual sin guardar
            if self.oracion_actual and self.oracion_actual not in etiquetado_filtrado:
                mensaje += f"\n⚠️  La oración actual ({self.oracion_actual}) no fue guardada "
                mensaje += f"porque no tiene etiquetado."
            
            messagebox.showinfo("Guardado Exitoso", mensaje, parent=self.root)
            
            # Feedback visual en la interfaz
            self.label_seleccion_info.config(
                text=f"✓ Guardado: {oraciones_con_etiquetado} oraciones",
                fg="#006600"
            )
            
            # Temporizador para limpiar el mensaje después de 3 segundos
            self.root.after(3000, lambda: self.actualizar_info_seleccion())
            
        except Exception as e:
            messagebox.showerror(
                "Error Inesperado", 
                f"Ocurrió un error inesperado:\n\n{str(e)}",
                parent=self.root
            )