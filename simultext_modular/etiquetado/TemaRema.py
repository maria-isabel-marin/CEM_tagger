import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import etiquetado.config as config


class VentanaEtiquetadoTemaRema:
    """
    Ventana para etiquetado de tema y rema por ORACIÓN.
    Panel izquierdo: texto con tokens (selección múltiple por cursor)
    Panel derecho: interfaz de etiquetado
    La oración actual se detecta automáticamente a partir de los tokens seleccionados.
    """

    def __init__(self, root, ruta_json, tipo_texto):
        self.root = root
        self.root.title("SIMULTEXT - Tema/Rema por Oración")
        self.root.geometry("1600x900")
        self.root.configure(bg=config.COLOR_FONDO)

        self.ruta_json = ruta_json
        self.tipo_texto = tipo_texto

        # Estructuras de datos
        self.tokens_por_oracion = {}
        self.token_posiciones = {}
        self.etiquetado_oraciones = {}  # oracion_id -> {tema: [], rema: [], etiqueta: ""}
        self.grupos_progresion = []     # lista de grupos: [{"etiqueta": valor, "oraciones": [id1, id2, ...]}, ...]
        self.token_info = {}
        self.oracion_actual = None
        self.tokens_seleccionados = set()
        self.drag_start = None
        
        # Variable para botones de etiqueta de progresión (en ventana principal, pero ahora solo visual)
        self.var_etiqueta_progresion = tk.StringVar()
        
        # Cargar datos
        self.cargar_datos_desde_json()
        
        # Crear interfaz completa
        self.crear_interfaz()
        
        # Mostrar texto
        self.mostrar_texto()
        
        # Cargar etiquetado existente si existe
        self.cargar_etiquetado_existente()

    # =========================================================
    # CARGA DEL JSON
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
                    "etiqueta": ""
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
                        "oracion": oracion_id
                    }

    def cargar_etiquetado_existente(self):
        """Carga el etiquetado de tema/rema y los grupos de progresión existentes desde el JSON."""
        try:
            etiquetado = self.datos_completos.get("document", {}).get("Etiquetado", {})
            tema_rema_data = etiquetado.get("tema_rema", {})
            
            if tema_rema_data:
                for oracion_id, etiquetas in tema_rema_data.items():
                    if oracion_id in self.etiquetado_oraciones:
                        self.etiquetado_oraciones[oracion_id]["tema"] = etiquetas.get("tema", [])
                        self.etiquetado_oraciones[oracion_id]["rema"] = etiquetas.get("rema", [])
                        self.etiquetado_oraciones[oracion_id]["etiqueta"] = etiquetas.get("etiqueta", "")
            
            # Cargar grupos de progresión
            grupos_data = etiquetado.get("grupos_progresion", [])
            if grupos_data:
                self.grupos_progresion = grupos_data  # ya debería tener la estructura correcta
        except Exception as e:
            print(f"Error al cargar etiquetado existente: {e}")

    # =========================================================
    # INTERFAZ SIMPLIFICADA
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
            text="TEXTO PARA ANÁLISIS DE TEMA/REMA",
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
            cursor="hand2"
        )
        self.text_area.pack(fill="both", expand=True)

        # Configurar tags
        self.text_area.tag_config("token", font=config.FUENTE_TOKEN)
        self.text_area.tag_config("id", font=config.FUENTE_TOKEN_ID)
        self.text_area.tag_config("tema", background=config.COLOR_TEMA, foreground="black")
        self.text_area.tag_config("rema", background=config.COLOR_REMA, foreground="black")
        self.text_area.tag_config("seleccionado", background=config.COLOR_SELECCIONADO, foreground="black")
        self.text_area.tag_config("oracion_actual", background="#E6F3FF", relief="ridge", borderwidth=1)

        # Bind eventos del mouse
        self.text_area.bind("<Button-1>", self.on_text_click_start)
        self.text_area.bind("<B1-Motion>", self.on_text_drag)
        self.text_area.bind("<ButtonRelease-1>", self.on_text_click_end)
        self.text_area.bind("<Control-Button-1>", self.on_text_ctrl_click)
        self.text_area.bind("<Button-3>", self.on_text_right_click)

        # ========== PANEL DERECHO: ETIQUETADO ==========
        tk.Label(
            right_panel,
            text="ETIQUETADO TEMA/REMA",
            font=("Arial", 14, "bold"),
            bg=config.COLOR_FONDO,
            fg=config.COLOR_TITULO
        ).pack(pady=5)

        # Información de la oración actual
        frame_info_oracion = tk.Frame(right_panel, bg=config.COLOR_FONDO)
        frame_info_oracion.pack(fill="x", pady=(0, 10))

        tk.Label(
            frame_info_oracion,
            text="Oración actual:",
            font=("Arial", 11, "bold"),
            bg=config.COLOR_FONDO
        ).pack(side="left", padx=(0, 5))

        self.label_oracion_actual = tk.Label(
            frame_info_oracion,
            text="(seleccione un token)",
            font=("Arial", 11),
            bg=config.COLOR_FONDO,
            fg="#555555"
        )
        self.label_oracion_actual.pack(side="left")

        # Botón para limpiar la oración actual
        tk.Button(
            frame_info_oracion,
            text="Limpiar Oración",
            bg=config.COLOR_BOTON_ROJO,
            fg="white",
            font=("Arial", 10),
            command=self.limpiar_oracion_actual
        ).pack(side="right")

        # Información de tokens seleccionados
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

        # Botones de etiquetado rápido
        frame_botones_rapidos = tk.Frame(right_panel, bg=config.COLOR_FONDO)
        frame_botones_rapidos.pack(fill="x", pady=(0, 10))

        tk.Label(
            frame_botones_rapidos,
            text="Etiquetado Rápido:",
            font=("Arial", 11, "bold"),
            bg=config.COLOR_FONDO
        ).pack(anchor="w", pady=(0, 5))

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

        # Botón para abrir ventana de asignación de progresión
        tk.Button(
            right_panel,
            text="ASIGNAR PROGRESIÓN",
            bg="#FFA500",  # naranja
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.abrir_ventana_progresion,
            width=20,
            height=2
        ).pack(pady=(10, 10))

        # Visualización del etiquetado actual
        frame_etiquetado = tk.Frame(right_panel, bg=config.COLOR_FONDO)
        frame_etiquetado.pack(fill="both", expand=True, pady=(0, 5))

        tk.Label(
            frame_etiquetado,
            text="Etiquetado Actual de la Oración:",
            font=("Arial", 11, "bold"),
            bg=config.COLOR_FONDO
        ).pack(anchor="w", pady=(0, 5))

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

        # Botones de guardar/cancelar
        frame_botones_finales = tk.Frame(right_panel, bg=config.COLOR_FONDO)
        frame_botones_finales.pack(fill="x", pady=(10, 0))
        
        tk.Button(
            frame_botones_finales,
            text="GUARDAR TODO",
            bg=config.COLOR_BOTON_VERDE,
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.guardar_en_json,
            width=20,
            height=2
        ).pack(side="left", padx=(0, 20))
        
        tk.Button(
            frame_botones_finales,
            text="CANCELAR",
            bg=config.COLOR_BOTON_ROJO,
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.root.destroy,
            width=15,
            height=2
        ).pack(side="right")

        # Inicialmente no hay oración seleccionada
        self.actualizar_info_seleccion()

    # =========================================================
    # DETECCIÓN DE ORACIÓN ACTUAL DESDE SELECCIÓN
    # =========================================================
    def actualizar_oracion_actual_por_seleccion(self):
        """Establece la oración actual basada en el primer token seleccionado."""
        if self.tokens_seleccionados:
            # Tomar el primer token seleccionado
            token_id = next(iter(self.tokens_seleccionados))
            if token_id in self.token_info:
                oracion_id = self.token_info[token_id]['oracion']
                if oracion_id != self.oracion_actual:
                    self.oracion_actual = oracion_id
                    self.actualizar_vista_etiquetado()
                    self.resaltar_oracion_actual()
                    # Actualizar etiqueta visual de oración actual
                    self.label_oracion_actual.config(text=f"{oracion_id}")
        else:
            # No hay selección, se puede dejar la oración actual o poner "ninguna"
            # Por ahora, no cambiamos para no perder referencia, pero se podría poner None
            pass

    # =========================================================
    # MOSTRAR TEXTO Y RESALTADO
    # =========================================================
    def mostrar_texto(self):
        self.text_area.config(state="normal")
        self.text_area.delete("1.0", tk.END)

        self.token_posiciones = {}

        for oracion_id, tokens in self.tokens_por_oracion.items():
            self.text_area.insert(tk.END, f"\nORACIÓN {oracion_id.upper()}\n")

            for tk_info in tokens:
                palabra = tk_info["form"]
                tid = tk_info["id"]

                inicio = self.text_area.index("end-1c")
                tag_token = f"token_{tid}"
                self.text_area.tag_config(tag_token, font=config.FUENTE_TOKEN)
                self.text_area.insert(tk.END, palabra, (tag_token, "token"))
                self.text_area.insert(tk.END, f"({tid}) ", "id")

                pos_inicio = self.text_area.index(f"{inicio}")
                pos_fin = self.text_area.index(f"{inicio}+{len(palabra)}c")
                self.token_posiciones[tid] = {
                    "inicio": pos_inicio,
                    "fin": pos_fin,
                    "tag": tag_token,
                    "oracion": oracion_id
                }

            self.text_area.insert(tk.END, "\n\n")

        self.resaltar_etiquetado_en_texto()
        self.text_area.config(state="disabled")

    def resaltar_etiquetado_en_texto(self):
        for oracion_id, etiquetas in self.etiquetado_oraciones.items():
            for token_id in etiquetas["tema"]:
                if token_id in self.token_posiciones:
                    pos = self.token_posiciones[token_id]
                    self.text_area.tag_add("tema", pos["inicio"], pos["fin"])
            for token_id in etiquetas["rema"]:
                if token_id in self.token_posiciones:
                    pos = self.token_posiciones[token_id]
                    self.text_area.tag_add("rema", pos["inicio"], pos["fin"])

    def resaltar_oracion_actual(self):
        self.text_area.tag_remove("oracion_actual", "1.0", tk.END)
        if not self.oracion_actual:
            return
        start_pattern = f"\nORACIÓN {self.oracion_actual.upper()}\n"
        start_index = self.text_area.search(start_pattern, "1.0", tk.END)
        if start_index:
            end_search = self.text_area.index(f"{start_index}+1c")
            end_index = self.text_area.search("\nORACIÓN ", end_search, tk.END)
            if not end_index:
                end_index = tk.END
            else:
                end_index = self.text_area.index(f"{end_index}-1c")
            self.text_area.tag_add("oracion_actual", start_index, end_index)

    # =========================================================
    # MANEJO DE SELECCIÓN DE TOKENS
    # =========================================================
    def on_text_click_start(self, event):
        if not (event.state & 0x4):
            self.limpiar_seleccion()
        self.drag_start = f"@{event.x},{event.y}"
        self.procesar_seleccion_en_punto(self.drag_start)

    def on_text_drag(self, event):
        if not self.drag_start:
            return
        self.text_area.tag_remove("seleccion_temp", "1.0", tk.END)
        drag_end = f"@{event.x},{event.y}"
        if self.text_area.compare(self.drag_start, "<", drag_end):
            self.text_area.tag_add("seleccion_temp", self.drag_start, drag_end)
        else:
            self.text_area.tag_add("seleccion_temp", drag_end, self.drag_start)
        self.text_area.tag_config("seleccion_temp", background="#FFCCCC", foreground="black")

    def on_text_click_end(self, event):
        if not self.drag_start:
            return
        drag_end = f"@{event.x},{event.y}"
        start_index = self.drag_start
        end_index = drag_end
        if self.text_area.compare(start_index, ">", end_index):
            start_index, end_index = end_index, start_index
        tokens_en_rango = []
        for token_id, pos in self.token_posiciones.items():
            if (self.text_area.compare(pos["inicio"], ">=", start_index) and
                self.text_area.compare(pos["inicio"], "<=", end_index)):
                tokens_en_rango.append(token_id)
        for token_id in tokens_en_rango:
            self.tokens_seleccionados.add(token_id)
            pos = self.token_posiciones[token_id]
            self.text_area.tag_add("seleccionado", pos["inicio"], pos["fin"])
        self.text_area.tag_remove("seleccion_temp", "1.0", tk.END)
        self.actualizar_info_seleccion()
        self.actualizar_oracion_actual_por_seleccion()
        self.drag_start = None

    def on_text_ctrl_click(self, event):
        index = f"@{event.x},{event.y}"
        self.procesar_seleccion_en_punto(index)

    def on_text_right_click(self, event):
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
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def procesar_seleccion_en_punto(self, index):
        token_encontrado = None
        for token_id, pos in self.token_posiciones.items():
            if self.posicion_en_rango(index, pos["inicio"], pos["fin"]):
                token_encontrado = token_id
                break
        if token_encontrado:
            if token_encontrado in self.tokens_seleccionados:
                self.tokens_seleccionados.remove(token_encontrado)
                pos = self.token_posiciones[token_encontrado]
                self.text_area.tag_remove("seleccionado", pos["inicio"], pos["fin"])
            else:
                self.tokens_seleccionados.add(token_encontrado)
                pos = self.token_posiciones[token_encontrado]
                self.text_area.tag_add("seleccionado", pos["inicio"], pos["fin"])
            self.actualizar_info_seleccion()
            self.actualizar_oracion_actual_por_seleccion()

    def seleccionar_toda_oracion_actual(self):
        if not self.oracion_actual:
            return
        self.limpiar_seleccion()
        for token_id, pos in self.token_posiciones.items():
            if pos["oracion"] == self.oracion_actual:
                self.tokens_seleccionados.add(token_id)
                self.text_area.tag_add("seleccionado", pos["inicio"], pos["fin"])
        self.actualizar_info_seleccion()

    def limpiar_seleccion(self):
        self.text_area.tag_remove("seleccionado", "1.0", tk.END)
        self.text_area.tag_remove("seleccion_temp", "1.0", tk.END)
        self.tokens_seleccionados.clear()
        self.actualizar_info_seleccion()

    def actualizar_info_seleccion(self):
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
        return self.text_area.compare(pos, ">=", inicio) and self.text_area.compare(pos, "<=", fin)

    # =========================================================
    # ETIQUETADO TEMA/REMA
    # =========================================================
    def agregar_tema(self):
        self.agregar_tokens_seleccionados("tema")

    def agregar_rema(self):
        self.agregar_tokens_seleccionados("rema")

    def agregar_tokens_seleccionados(self, tipo):
        if not self.tokens_seleccionados:
            messagebox.showwarning("Advertencia", "Por favor, seleccione al menos un token.")
            return
        
        if not self.oracion_actual:
            messagebox.showwarning("Advertencia", "No se ha detectado una oración. Seleccione un token para definir la oración actual.")
            return
        
        tokens_agregados = 0
        tokens_movidos = 0
        otro_tipo = "rema" if tipo == "tema" else "tema"
        
        for token_id in list(self.tokens_seleccionados):
            # Remover de otras oraciones
            for oracion_id, etiquetas in self.etiquetado_oraciones.items():
                if oracion_id != self.oracion_actual:
                    if token_id in etiquetas["tema"]:
                        etiquetas["tema"].remove(token_id)
                    if token_id in etiquetas["rema"]:
                        etiquetas["rema"].remove(token_id)
            
            # Remover del otro grupo de esta oración
            if token_id in self.etiquetado_oraciones[self.oracion_actual][otro_tipo]:
                self.etiquetado_oraciones[self.oracion_actual][otro_tipo].remove(token_id)
                tokens_movidos += 1
            
            # Agregar al grupo actual si no está
            if token_id not in self.etiquetado_oraciones[self.oracion_actual][tipo]:
                self.etiquetado_oraciones[self.oracion_actual][tipo].append(token_id)
                tokens_agregados += 1
        
        self.actualizar_vista_etiquetado()
        self.resaltar_etiquetado_en_texto()
        self.limpiar_seleccion()
        
        info_text = f"{tokens_agregados} token(s) etiquetados como {tipo.upper()}"
        if tokens_movidos > 0:
            info_text += f" ({tokens_movidos} movidos de {otro_tipo.upper()})"
        self.label_seleccion_info.config(text=info_text, fg="#006600")

    def limpiar_oracion_actual(self):
        if not self.oracion_actual:
            return
        respuesta = messagebox.askyesno(
            "Confirmar",
            f"¿Está seguro de que desea limpiar todo el etiquetado de la oración {self.oracion_actual}?",
            parent=self.root
        )
        if respuesta:
            # Eliminar la oración de cualquier grupo de progresión
            for grupo in self.grupos_progresion[:]:  # iterar sobre copia
                if self.oracion_actual in grupo["oraciones"]:
                    grupo["oraciones"].remove(self.oracion_actual)
                    if not grupo["oraciones"]:  # si el grupo queda vacío, eliminarlo
                        self.grupos_progresion.remove(grupo)
            
            # Limpiar etiquetado de la oración
            self.etiquetado_oraciones[self.oracion_actual] = {
                "tema": [], 
                "rema": [],
                "etiqueta": ""
            }
            self.actualizar_vista_etiquetado()
            # Quitar resaltado en texto para esta oración
            for token_id in self.tokens_por_oracion.get(self.oracion_actual, []):
                tid = token_id["id"]
                if tid in self.token_posiciones:
                    pos = self.token_posiciones[tid]
                    self.text_area.tag_remove("tema", pos["inicio"], pos["fin"])
                    self.text_area.tag_remove("rema", pos["inicio"], pos["fin"])
            self.limpiar_seleccion()

    def actualizar_vista_etiquetado(self):
        self.etiquetado_area.config(state="normal")
        self.etiquetado_area.delete("1.0", tk.END)
        
        if not self.oracion_actual:
            self.etiquetado_area.insert(tk.END, "Seleccione una oración para ver su etiquetado.")
            self.etiquetado_area.config(state="disabled")
            return
        
        etiquetas = self.etiquetado_oraciones[self.oracion_actual]
        
        # Mostrar a qué grupo(s) de progresión pertenece la oración
        grupos_oracion = [g for g in self.grupos_progresion if self.oracion_actual in g["oraciones"]]
        if grupos_oracion:
            self.etiquetado_area.insert(tk.END, "GRUPOS DE PROGRESIÓN:\n", "subtitulo")
            for g in grupos_oracion:
                nombre_etiqueta = config.ETIQUETAS_PROGRESION.get(g["etiqueta"], g["etiqueta"])
                self.etiquetado_area.insert(tk.END, f"  • {nombre_etiqueta} (con {len(g['oraciones'])} oraciones)\n")
            self.etiquetado_area.insert(tk.END, "\n")
        
        if etiquetas["etiqueta"]:
            nombre_etiqueta = config.ETIQUETAS_PROGRESION.get(
                etiquetas["etiqueta"], 
                etiquetas["etiqueta"]
            )
            self.etiquetado_area.insert(tk.END, f"ETIQUETA INDIVIDUAL: {nombre_etiqueta}\n\n", "titulo")
        
        self.etiquetado_area.insert(tk.END, "TEMA:\n", "subtitulo")
        if etiquetas["tema"]:
            tokens_tema = []
            for token_id in etiquetas["tema"]:
                if token_id in self.token_info:
                    token = self.token_info[token_id]
                    oracion_original = token['oracion']
                    tokens_tema.append(f"  • {token_id}: '{token['form']}' (oración original: {oracion_original})")
            self.etiquetado_area.insert(tk.END, "\n".join(tokens_tema) + "\n\n")
        else:
            self.etiquetado_area.insert(tk.END, "  No hay tokens etiquetados como tema.\n\n")
        
        self.etiquetado_area.insert(tk.END, "REMA:\n", "subtitulo")
        if etiquetas["rema"]:
            tokens_rema = []
            for token_id in etiquetas["rema"]:
                if token_id in self.token_info:
                    token = self.token_info[token_id]
                    oracion_original = token['oracion']
                    tokens_rema.append(f"  • {token_id}: '{token['form']}' (oración original: {oracion_original})")
            self.etiquetado_area.insert(tk.END, "\n".join(tokens_rema))
        else:
            self.etiquetado_area.insert(tk.END, "  No hay tokens etiquetados como rema.")
        
        self.etiquetado_area.config(state="disabled")
        self.etiquetado_area.tag_config("titulo", font=("Arial", 11, "bold"), foreground=config.COLOR_TITULO)
        self.etiquetado_area.tag_config("subtitulo", font=("Arial", 11, "bold"))

    # =========================================================
    # VENTANA DE ASIGNACIÓN DE PROGRESIÓN (con grupos)
    # =========================================================
    def abrir_ventana_progresion(self):
        """Abre una ventana secundaria para asignar etiquetas de progresión a múltiples oraciones, creando grupos."""
        # Verificar que haya al menos una oración con tema/rema etiquetado
        oraciones_con_etiquetado = [
            oid for oid, et in self.etiquetado_oraciones.items()
            if et["tema"] or et["rema"]
        ]
        if not oraciones_con_etiquetado:
            messagebox.showinfo("Sin datos", "No hay oraciones con etiquetado de tema/rema para asignar progresión.")
            return
        
        VentanaAsignacionProgresion(self.root, self)


    # =========================================================
    # GUARDAR EN JSON (con grupos)
    # =========================================================
    def guardar_en_json(self):
        try:
            etiquetado_filtrado = {}
            oraciones_con_etiquetado = 0
            
            for oracion_id, etiquetas in self.etiquetado_oraciones.items():
                tiene_etiquetado = (
                    len(etiquetas["tema"]) > 0 or 
                    len(etiquetas["rema"]) > 0 or 
                    etiquetas["etiqueta"] != ""
                )
                if tiene_etiquetado:
                    oraciones_con_etiquetado += 1
                    etiquetado_filtrado[oracion_id] = {
                        "tema": etiquetas["tema"].copy(),
                        "rema": etiquetas["rema"].copy(),
                        "etiqueta": etiquetas["etiqueta"]
                    }
            
            if oraciones_con_etiquetado == 0 and not self.grupos_progresion:
                respuesta = messagebox.askyesno(
                    "Sin etiquetado",
                    "No hay ninguna etiqueta de tema/rema ni grupos de progresión.\n\n¿Desea guardar una estructura vacía?"
                )
                if not respuesta:
                    return
            
            try:
                with open(self.ruta_json, "r", encoding="utf-8") as f:
                    datos_completos = json.load(f)
            except FileNotFoundError:
                datos_completos = {"document": {}}
            except json.JSONDecodeError as e:
                messagebox.showerror("Error en archivo JSON", f"El archivo tiene formato JSON inválido:\n{e}", parent=self.root)
                return
            
            if "document" not in datos_completos:
                datos_completos["document"] = {}
            if "Etiquetado" not in datos_completos["document"]:
                datos_completos["document"]["Etiquetado"] = {}
            
            # Guardar etiquetado por oración
            datos_completos["document"]["Etiquetado"]["tema_rema"] = etiquetado_filtrado
            # Guardar grupos de progresión
            datos_completos["document"]["Etiquetado"]["grupos_progresion"] = self.grupos_progresion.copy()
            
            try:
                json_final = json.dumps(datos_completos, ensure_ascii=False, indent=2)
                import os, shutil
                if os.path.exists(self.ruta_json):
                    backup_path = self.ruta_json + ".backup"
                    shutil.copy2(self.ruta_json, backup_path)
                with open(self.ruta_json, "w", encoding="utf-8") as f:
                    f.write(json_final)
            except PermissionError:
                messagebox.showerror("Error de permisos", f"No tiene permisos para escribir en:\n{self.ruta_json}", parent=self.root)
                return
            except Exception as e:
                messagebox.showerror("Error de escritura", f"No se pudo guardar el archivo:\n{e}", parent=self.root)
                return
            
            total_tokens_tema = sum(len(v["tema"]) for v in etiquetado_filtrado.values())
            total_tokens_rema = sum(len(v["rema"]) for v in etiquetado_filtrado.values())
            oraciones_con_progresion = sum(1 for v in etiquetado_filtrado.values() if v["etiqueta"])
            
            mensaje = f"✅ ETIQUETADO GUARDADO EXITOSAMENTE\n\n"
            mensaje += f"📁 Archivo: {self.ruta_json}\n"
            mensaje += f"📊 Estadísticas:\n"
            mensaje += f"   • Oraciones etiquetadas: {oraciones_con_etiquetado}\n"
            mensaje += f"   • Tokens TEMA: {total_tokens_tema}\n"
            mensaje += f"   • Tokens REMA: {total_tokens_rema}\n"
            mensaje += f"   • Oraciones con progresión individual: {oraciones_con_progresion}\n"
            mensaje += f"   • Grupos de progresión: {len(self.grupos_progresion)}\n"
            
            if oraciones_con_etiquetado > 0:
                mensaje += f"\n📋 Oraciones guardadas:\n"
                for i, oid in enumerate(list(etiquetado_filtrado.keys())[:5]):
                    et = etiquetado_filtrado[oid]["etiqueta"] or "Sin etiqueta"
                    mensaje += f"   {oid}: {et}\n"
                if oraciones_con_etiquetado > 5:
                    mensaje += f"   ... y {oraciones_con_etiquetado - 5} más\n"
            
            if self.oracion_actual and self.oracion_actual not in etiquetado_filtrado:
                mensaje += f"\n⚠️  La oración actual ({self.oracion_actual}) no fue guardada porque no tiene etiquetado."
            
            messagebox.showinfo("Guardado Exitoso", mensaje, parent=self.root)
            self.label_seleccion_info.config(text=f"✓ Guardado: {oraciones_con_etiquetado} oraciones", fg="#006600")
            self.root.after(3000, lambda: self.actualizar_info_seleccion())
            
        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Ocurrió un error inesperado:\n\n{str(e)}", parent=self.root)


class VentanaAsignacionProgresion:
    """Ventana secundaria para asignar etiqueta de progresión a múltiples oraciones, creando un grupo."""

    def __init__(self, parent, ventana_principal):
        self.parent = parent
        self.ventana_principal = ventana_principal
        self.top = tk.Toplevel(parent)
        self.top.title("Asignar progresión temática")
        self.top.geometry("600x500")
        self.top.configure(bg=config.COLOR_FONDO)
        self.top.transient(parent)
        self.top.grab_set()

        # Variables
        self.var_etiqueta = tk.StringVar()
        self.checkboxes = {}  # oracion_id -> tk.BooleanVar

        self.crear_interfaz()

    def crear_interfaz(self):
        # Título
        tk.Label(
            self.top,
            text="Seleccione oraciones y asigne una etiqueta de progresión\n(Se creará un grupo con las seleccionadas)",
            font=("Arial", 12, "bold"),
            bg=config.COLOR_FONDO,
            fg=config.COLOR_TITULO
        ).pack(pady=10)

        # Frame para lista de oraciones con scroll
        frame_lista = tk.Frame(self.top, bg=config.COLOR_FONDO)
        frame_lista.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(frame_lista, text="Oraciones con etiquetado de tema/rema:", bg=config.COLOR_FONDO).pack(anchor="w")

        canvas = tk.Canvas(frame_lista, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(frame_lista, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Llenar lista con oraciones que tienen tema/rema
        for oracion_id, etiquetas in self.ventana_principal.etiquetado_oraciones.items():
            if etiquetas["tema"] or etiquetas["rema"]:
                var = tk.BooleanVar()
                self.checkboxes[oracion_id] = var
                num_tema = len(etiquetas["tema"])
                num_rema = len(etiquetas["rema"])
                # Indicar si ya pertenece a algún grupo
                grupos = [g for g in self.ventana_principal.grupos_progresion if oracion_id in g["oraciones"]]
                grupo_info = f" (en grupo: {', '.join(g['etiqueta'] for g in grupos)})" if grupos else ""
                texto = f"Oración {oracion_id}  (tema: {num_tema}, rema: {num_rema}){grupo_info}"
                cb = tk.Checkbutton(
                    scrollable_frame,
                    text=texto,
                    variable=var,
                    bg="white",
                    anchor="w",
                    justify="left"
                )
                cb.pack(fill="x", padx=5, pady=2)

        # Frame para etiquetas de progresión
        frame_etiquetas = tk.Frame(self.top, bg=config.COLOR_FONDO)
        frame_etiquetas.pack(fill="x", padx=10, pady=10)

        tk.Label(frame_etiquetas, text="Etiqueta de progresión:", bg=config.COLOR_FONDO).pack(anchor="w")

        # Radiobuttons para cada tipo
        for nombre, valor in config.TIPOS_PROGRESION:
            rb = tk.Radiobutton(
                frame_etiquetas,
                text=nombre,
                variable=self.var_etiqueta,
                value=valor,
                bg=config.COLOR_FONDO
            )
            rb.pack(anchor="w")

        # Botones
        frame_botones = tk.Frame(self.top, bg=config.COLOR_FONDO)
        frame_botones.pack(fill="x", padx=10, pady=10)

        tk.Button(
            frame_botones,
            text="Crear grupo y aplicar",
            bg=config.COLOR_BOTON_VERDE,
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.aplicar
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            frame_botones,
            text="Cerrar",
            bg=config.COLOR_BOTON_ROJO,
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.top.destroy
        ).pack(side="right")

    def aplicar(self):
        """Crea un nuevo grupo con las oraciones seleccionadas y la etiqueta elegida."""
        etiqueta = self.var_etiqueta.get()
        if not etiqueta:
            messagebox.showwarning("Advertencia", "Debe seleccionar una etiqueta de progresión.", parent=self.top)
            return

        seleccionadas = [oid for oid, var in self.checkboxes.items() if var.get()]
        if not seleccionadas:
            messagebox.showwarning("Advertencia", "Debe seleccionar al menos una oración.", parent=self.top)
            return

        # Eliminar estas oraciones de cualquier grupo anterior
        for grupo in self.ventana_principal.grupos_progresion[:]:  # iterar sobre copia
            for oid in seleccionadas:
                if oid in grupo["oraciones"]:
                    grupo["oraciones"].remove(oid)
            if not grupo["oraciones"]:
                self.ventana_principal.grupos_progresion.remove(grupo)

        # Crear nuevo grupo
        nuevo_grupo = {
            "etiqueta": etiqueta,
            "oraciones": seleccionadas
        }
        self.ventana_principal.grupos_progresion.append(nuevo_grupo)

        # Actualizar las etiquetas individuales de esas oraciones (para coherencia)
        for oid in seleccionadas:
            self.ventana_principal.etiquetado_oraciones[oid]["etiqueta"] = etiqueta

        # Actualizar vista en la ventana principal si la oración actual es una de las modificadas
        if self.ventana_principal.oracion_actual in seleccionadas:
            self.ventana_principal.actualizar_vista_etiquetado()

        messagebox.showinfo("Éxito", f"Grupo con etiqueta '{etiqueta}' creado con {len(seleccionadas)} oración(es).", parent=self.top)
        self.top.destroy()