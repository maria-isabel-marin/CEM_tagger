import tkinter as tk
from tkinter import ttk, messagebox
import xml.etree.ElementTree as ET
import os
import json

class VentanaEtiquetadoCorreferentes:
    def __init__(self, root, ruta_xml, tipo_texto):
        self.root = root
        self.ruta_xml = ruta_xml
        self.tipo_texto = tipo_texto

        # Crear ventana Toplevel
        self.ventana = self.root
        self.ventana.title("Correferencia textual")
        self.ventana.geometry("1200x800")

        # Variables de datos
        self.parrafos = []
        self.tokens_por_parrafo = {}
        self.texto_original_por_parrafo = {}
        
        # Variables para la correferencia
        self.referentes = {}  # {referente_id: [lista_de_tokens]}
        self.correferentes_por_referente = {}  # {referente_id: {correferente_id: {etiqueta: str, tokens: []}}}
        self.referente_actual = None
        self.modo_seleccion = None  # 'referente' o 'correferente'
        self.seleccion_temporal = set()
        self.colores = ['#FF9999', '#99FF99', '#9999FF', '#FFFF99', '#FF99FF', '#99FFFF']
        self.contador_referentes = 1
        self.contador_correferentes = {}  # {referente_id: contador}

        # Diccionario de etiquetas
        self.etiquetas = {
            "An_Fi": "Anáfora fiel",
            "An_inf": "Anáfora infiel",
            "An_met": "Anáfora metafórica",
            "An_con": "Anáfora conceptual",
            "An_aso": "Anáfora asociativa",
            "An_ref": "Anáfora de referencia",
            "An_sup": "Anáfora de sentido o superficial",
            "An_tot": "Anáfora total",
            "An_par": "Anáfora parcial",
            "An_signom": "Sintagma nominal",
            "An_sigv": "Sintagma verbal",
            "An_sigadv": "Sintagma adverbial",
            "An_ora": "Oración completa, hecho o idea",
            "An_pps": "Anáfora de pronombre personal",
            "An_ppcom": "Anáfora de pronombre personal complemento",
            "An_ppo": "Anáfora de pronombre personal objeto",
            "An_ppd": "Anáfora de pronombre personal demostrativo",
            "An_ppp": "Anáfora de pronombre personal posesivo",
            "An_pref": "Anáfora de referencia",
            "An_rel": "Anáfora relativa",
            "An_snart": "Anáfora de sintagma nominal",
            "An_sndet": "Anáfora de sintagma nominal determinado",
            "An_ver": "Anáfora verbal",
            "An_vercom": "Anáfora verbal compuesta",
            "An_temp": "Anáfora adverbial temporal",
            "An_loc": "Anáfora adverbial locativa",
            "An_integ": "Anáforas integrativas",
            "An_det": "Anáfora determinativa"
        }

        # === Frame principal ===
        main_frame = ttk.Frame(self.ventana)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # === Frame para controles ===
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill="x", pady=(0, 10))

        # Botones para referentes
        ttk.Label(control_frame, text="Referentes:").pack(side="left", padx=(0, 5))
        ttk.Button(control_frame, text="Nuevo Referente", 
                  command=self.iniciar_nuevo_referente).pack(side="left", padx=(0, 10))
        ttk.Button(control_frame, text="Finalizar Referente", 
                  command=self.finalizar_referente).pack(side="left", padx=(0, 10))

        # Botones para correferentes
        ttk.Label(control_frame, text="Correferentes:").pack(side="left", padx=(20, 5))
        ttk.Button(control_frame, text="Añadir Tokens Correferente", 
                  command=self.anadir_tokens_correferente).pack(side="left", padx=(0, 10))
        ttk.Button(control_frame, text="Finalizar Correferente", 
                  command=self.finalizar_correferente).pack(side="left", padx=(0, 10))

        # Botones generales
        ttk.Button(control_frame, text="Limpiar Selección", 
                  command=self.limpiar_seleccion).pack(side="left", padx=(20, 10))
        ttk.Button(control_frame, text="Ver Relaciones", 
                  command=self.mostrar_relaciones).pack(side="left", padx=(0, 10))
        ttk.Button(control_frame, text="Guardar JSON", 
                  command=self.guardar_json).pack(side="left")

        # === Frame para contenido ===
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill="both", expand=True)

        # Text widget con scrollbar
        text_frame = ttk.Frame(content_frame)
        text_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.text_widget = tk.Text(text_frame, wrap="word", font=("Arial", 11), 
                                  cursor="hand2", selectbackground="lightblue")
        
        v_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_widget.yview)
        h_scrollbar = ttk.Scrollbar(text_frame, orient="horizontal", command=self.text_widget.xview)
        self.text_widget.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.text_widget.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")

        # Bind events para selección de texto
        self.text_widget.bind("<Button-1>", self.on_text_click)
        self.text_widget.configure(state="disabled")

        # === Frame para información y controles ===
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(side="right", fill="y")

        # Panel de selección de referente
        ttk.Label(info_frame, text="Seleccionar Referente", 
                 font=("Arial", 10, "bold")).pack(pady=(0, 5))
        
        self.referente_var = tk.StringVar()
        self.referente_combo = ttk.Combobox(info_frame, textvariable=self.referente_var, 
                                           state="readonly")
        self.referente_combo.pack(fill="x", pady=(0, 10))
        self.referente_combo.bind('<<ComboboxSelected>>', self.on_referente_seleccionado)

        # Panel de etiquetas
        ttk.Label(info_frame, text="Seleccionar Etiqueta", 
                 font=("Arial", 10, "bold")).pack(pady=(0, 5))
        
        self.etiqueta_var = tk.StringVar()
        self.etiqueta_combo = ttk.Combobox(info_frame, textvariable=self.etiqueta_var, 
                                          values=list(self.etiquetas.keys()), state="readonly")
        self.etiqueta_combo.pack(fill="x", pady=(0, 10))
        self.etiqueta_combo.bind('<<ComboboxSelected>>', self.mostrar_descripcion_etiqueta)
        
        self.descripcion_label = ttk.Label(info_frame, text="", wraplength=280, 
                                          font=("Arial", 8), foreground="gray")
        self.descripcion_label.pack(fill="x", pady=(0, 10))

        # Panel de selección actual
        ttk.Label(info_frame, text="Selección Actual", 
                 font=("Arial", 10, "bold")).pack(pady=(0, 5))
        
        self.seleccion_text = tk.Text(info_frame, wrap="word", width=35, height=8, 
                                     font=("Arial", 9), state="disabled")
        self.seleccion_text.pack(fill="x", pady=(0, 10))

        # Panel de relaciones
        ttk.Label(info_frame, text="Relaciones de Correferencia", 
                 font=("Arial", 10, "bold")).pack(pady=(0, 5))

        self.info_text = tk.Text(info_frame, wrap="word", width=35, height=15, 
                                font=("Arial", 9), state="disabled")
        info_scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scrollbar.set)
        
        self.info_text.pack(side="left", fill="both", expand=True)
        info_scrollbar.pack(side="right", fill="y")

        # === Frame inferior ===
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(bottom_frame, text="Cerrar", command=self.ventana.destroy).pack(side="right")

        # Estado actual
        self.estado_label = ttk.Label(bottom_frame, text="Listo para seleccionar")
        self.estado_label.pack(side="left")

        # Cargar datos del XML
        self.cargar_datos_xml()
        self.actualizar_combo_referentes()

    def mostrar_descripcion_etiqueta(self, event=None):
        """Muestra la descripción de la etiqueta seleccionada."""
        etiqueta = self.etiqueta_var.get()
        if etiqueta in self.etiquetas:
            self.descripcion_label.config(text=self.etiquetas[etiqueta])

    def on_referente_seleccionado(self, event=None):
        """Cuando se selecciona un referente del combo."""
        referente_id = self.referente_var.get()
        if referente_id and referente_id in self.referentes:
            self.referente_actual = referente_id
            self.actualizar_panel_seleccion()
            self.estado_label.config(text=f"Referente seleccionado: {referente_id}")

    def cargar_datos_xml(self):
        """Carga párrafos, tokens y texto original desde el archivo XML."""
        try:
            tree = ET.parse(self.ruta_xml)
            root = tree.getroot()

            self.parrafos = []
            self.tokens_por_parrafo = {}
            self.texto_original_por_parrafo = {}

            for parrafo in root.findall(".//paragraph"):
                id_parrafo = parrafo.get("id")
                texto_parrafo = ""
                tokens_info = []

                for oracion in parrafo.findall(".//sentence"):
                    for token in oracion.findall(".//token"):
                        form = token.get("form", "")
                        token_id = token.get("id", "")

                        tokens_info.append({
                            "form": form,
                            "id": token_id,
                            "form_lower": form.lower()
                        })

                        texto_parrafo += form + " "

                texto_limpio = texto_parrafo.strip()

                self.parrafos.append(id_parrafo)
                self.tokens_por_parrafo[id_parrafo] = tokens_info
                self.texto_original_por_parrafo[id_parrafo] = texto_limpio

            self.mostrar_texto_con_tokens()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el XML: {str(e)}", parent=self.ventana)

    def mostrar_texto_con_tokens(self):
        """Muestra el texto con los tokens formateados para selección, incluyendo IDs."""
        self.text_widget.configure(state="normal")
        self.text_widget.delete("1.0", tk.END)

        for parrafo_id in self.parrafos:
            # Encabezado del párrafo
            self.text_widget.insert(tk.END, f"Párrafo {parrafo_id}:\n", "parrafo_header")
            
            tokens = self.tokens_por_parrafo[parrafo_id]
            
            # Configurar estilos una sola vez
            self.text_widget.tag_configure("token_text", font=("Arial", 11, "bold"))
            self.text_widget.tag_configure("token_id", font=("Arial", 6), foreground="gray")

            for i, token_info in enumerate(tokens):
                token_text = token_info['form']
                token_id_text = f"({token_info['id']}) "

                tag_name = f"token_{parrafo_id}_{token_info['id']}"

                # Insertar palabra con estilo "texto en negrita"
                self.text_widget.insert(tk.END, token_text, (tag_name, "token_text"))

                # Insertar id con estilo "más pequeño"
                self.text_widget.insert(tk.END, token_id_text, (tag_name, "token_id"))

                # Tag principal para eventos y colores
                self.text_widget.tag_bind(tag_name, "<Button-1>",
                                        lambda e, tid=token_info['id'], pid=parrafo_id:
                                        self.seleccionar_token(tid, pid))


            
            self.text_widget.insert(tk.END, "\n\n")
        
        # Configurar estilo para encabezados de párrafo
        self.text_widget.tag_configure("parrafo_header", font=("Arial", 11, "bold"), 
                                      foreground="darkblue", spacing3=5)
        
        self.text_widget.configure(state="disabled")

    def iniciar_nuevo_referente(self):
        """Inicia la selección de un nuevo referente."""
        self.modo_seleccion = "referente"
        self.seleccion_temporal.clear()
        self.actualizar_panel_seleccion()
        self.estado_label.config(text="Seleccione tokens para el NUEVO REFERENTE (múltiples tokens permitidos)")

    def finalizar_referente(self):
        """Finaliza la selección del referente."""
        if not self.seleccion_temporal:
            messagebox.showwarning("Advertencia", 
                                 "No hay tokens seleccionados para el referente.", 
                                 parent=self.ventana)
            return
        
        # Crear nuevo referente
        referente_id = f"R{self.contador_referentes}"
        self.contador_referentes += 1
        
        # Inicializar contador de correferentes para este referente
        self.contador_correferentes[referente_id] = 1
        
        # Guardar referente
        self.referentes[referente_id] = sorted(self.seleccion_temporal)
        self.correferentes_por_referente[referente_id] = {}
        
        # Actualizar interfaz
        self.actualizar_combo_referentes()
        self.referente_var.set(referente_id)
        self.referente_actual = referente_id
        self.modo_seleccion = None
        self.seleccion_temporal.clear()
        
        self.actualizar_colores()
        self.actualizar_info_panel()
        self.actualizar_panel_seleccion()
        self.estado_label.config(text=f"Referente {referente_id} creado. Seleccione correferentes.")

    def anadir_tokens_correferente(self):
        """Inicia la selección de tokens para un nuevo correferente."""
        if not self.referente_actual:
            messagebox.showwarning("Advertencia", 
                                 "Primero debe seleccionar un referente.", 
                                 parent=self.ventana)
            return
        
        if not self.etiqueta_var.get():
            messagebox.showwarning("Advertencia", 
                                 "Debe seleccionar una etiqueta para el correferente.", 
                                 parent=self.ventana)
            return
        
        self.modo_seleccion = "correferente"
        self.seleccion_temporal.clear()
        self.actualizar_panel_seleccion()
        self.estado_label.config(text="Seleccione tokens para el CORREFERENTE (múltiples tokens permitidos)")

    def finalizar_correferente(self):
        """Finaliza la selección del correferente."""
        if not self.referente_actual:
            messagebox.showwarning("Advertencia", 
                                 "No hay referente seleccionado.", 
                                 parent=self.ventana)
            return
        
        if not self.seleccion_temporal:
            messagebox.showwarning("Advertencia", 
                                 "No hay tokens seleccionados para el correferente.", 
                                 parent=self.ventana)
            return
        
        if not self.etiqueta_var.get():
            messagebox.showwarning("Advertencia", 
                                 "Debe seleccionar una etiqueta para el correferente.", 
                                 parent=self.ventana)
            return
        
        # Verificar que no se esté seleccionando tokens del referente
        referente_tokens = set(self.referentes[self.referente_actual])
        if self.seleccion_temporal.intersection(referente_tokens):
            messagebox.showwarning("Advertencia", 
                                 "No puede seleccionar tokens del referente como correferente.", 
                                 parent=self.ventana)
            return
        
        # Crear nuevo correferente
        etiqueta = self.etiqueta_var.get()
        corref_id = f"corr{self.contador_correferentes[self.referente_actual]}"
        self.contador_correferentes[self.referente_actual] += 1
        
        # Guardar correferente
        self.correferentes_por_referente[self.referente_actual][corref_id] = {
            "etiqueta": etiqueta,
            "tokens": sorted(self.seleccion_temporal)
        }
        
        # Actualizar interfaz
        self.modo_seleccion = None
        self.seleccion_temporal.clear()
        
        self.actualizar_colores()
        self.actualizar_info_panel()
        self.actualizar_panel_seleccion()
        self.estado_label.config(text=f"Correferente {corref_id} añadido al referente {self.referente_actual}")

    def seleccionar_token(self, token_id, parrafo_id):
        """Maneja la selección de un token."""
        token_full_id = f"{parrafo_id}_{token_id}"
        
        if self.modo_seleccion == "referente":
            # Modo selección de referente
            if token_full_id in self.seleccion_temporal:
                # Deseleccionar
                self.seleccion_temporal.remove(token_full_id)
            else:
                # Seleccionar
                self.seleccion_temporal.add(token_full_id)
            
            self.actualizar_colores_temporal()
            self.actualizar_panel_seleccion()
            
        elif self.modo_seleccion == "correferente":
            # Modo selección de correferente
            if token_full_id in self.seleccion_temporal:
                # Deseleccionar
                self.seleccion_temporal.remove(token_full_id)
            else:
                # Verificar que no sea parte del referente actual
                if self.referente_actual and token_full_id in self.referentes[self.referente_actual]:
                    messagebox.showwarning("Token inválido", 
                                         "No puede seleccionar un token del referente como correferente.", 
                                         parent=self.ventana)
                    return
                # Seleccionar
                self.seleccion_temporal.add(token_full_id)
            
            self.actualizar_colores_temporal()
            self.actualizar_panel_seleccion()

    def actualizar_combo_referentes(self):
        """Actualiza el combobox de referentes."""
        referentes = list(self.referentes.keys())
        self.referente_combo['values'] = referentes
        if referentes and not self.referente_var.get():
            self.referente_var.set(referentes[0])
            self.referente_actual = referentes[0]

    def actualizar_panel_seleccion(self):
        """Actualiza el panel de selección actual."""
        self.seleccion_text.configure(state="normal")
        self.seleccion_text.delete("1.0", tk.END)
        
        if self.modo_seleccion == "referente":
            self.seleccion_text.insert(tk.END, "Modo: SELECCIÓN DE REFERENTE\n\n")
            if self.seleccion_temporal:
                self.seleccion_text.insert(tk.END, "Tokens seleccionados:\n")
                for token_id in sorted(self.seleccion_temporal):
                    parrafo_id, token_num = token_id.split("_")
                    tokens = self.tokens_por_parrafo[parrafo_id]
                    token_text = next((t["form"] for t in tokens if t["id"] == token_num), "N/A")
                    self.seleccion_text.insert(tk.END, f"• {token_text} (ID: {token_num})\n")
            else:
                self.seleccion_text.insert(tk.END, "No hay tokens seleccionados")
                
        elif self.modo_seleccion == "correferente":
            self.seleccion_text.insert(tk.END, f"Modo: SELECCIÓN DE CORREFERENTE\n")
            self.seleccion_text.insert(tk.END, f"Referente: {self.referente_actual}\n")
            self.seleccion_text.insert(tk.END, f"Etiqueta: {self.etiqueta_var.get()}\n\n")
            
            if self.seleccion_temporal:
                self.seleccion_text.insert(tk.END, "Tokens seleccionados:\n")
                for token_id in sorted(self.seleccion_temporal):
                    parrafo_id, token_num = token_id.split("_")
                    tokens = self.tokens_por_parrafo[parrafo_id]
                    token_text = next((t["form"] for t in tokens if t["id"] == token_num), "N/A")
                    self.seleccion_text.insert(tk.END, f"• {token_text} (ID: {token_num})\n")
            else:
                self.seleccion_text.insert(tk.END, "No hay tokens seleccionados")
                
        else:
            if self.referente_actual:
                self.seleccion_text.insert(tk.END, f"Referente actual: {self.referente_actual}\n\n")
                self.seleccion_text.insert(tk.END, "Tokens del referente:\n")
                for token_id in self.referentes[self.referente_actual]:
                    parrafo_id, token_num = token_id.split("_")
                    tokens = self.tokens_por_parrafo[parrafo_id]
                    token_text = next((t["form"] for t in tokens if t["id"] == token_num), "N/A")
                    self.seleccion_text.insert(tk.END, f"• {token_text} (ID: {token_num})\n")
                
                # Mostrar correferentes actuales
                if self.referente_actual in self.correferentes_por_referente and self.correferentes_por_referente[self.referente_actual]:
                    self.seleccion_text.insert(tk.END, "\nCorreferentes:\n")
                    for corref_id, corref_data in self.correferentes_por_referente[self.referente_actual].items():
                        self.seleccion_text.insert(tk.END, f"  {corref_id}:\n")
                        for token_id in corref_data["tokens"]:
                            parrafo_id, token_num = token_id.split("_")
                            tokens = self.tokens_por_parrafo[parrafo_id]
                            token_text = next((t["form"] for t in tokens if t["id"] == token_num), "N/A")
                            self.seleccion_text.insert(tk.END, f"    • {token_text} (ID: {token_num})\n")
                        self.seleccion_text.insert(tk.END, f"    Etiqueta: {corref_data['etiqueta']}\n")
            else:
                self.seleccion_text.insert(tk.END, "No hay referente seleccionado")
        
        self.seleccion_text.configure(state="disabled")

    def actualizar_colores(self):
        """Actualiza los colores de los tokens seleccionados."""
        self.text_widget.configure(state="normal")
        
        # Resetear todos los colores
        for parrafo_id in self.parrafos:
            tokens = self.tokens_por_parrafo[parrafo_id]
            for token_info in tokens:
                tag_name = f"token_{parrafo_id}_{token_info['id']}"
                self.text_widget.tag_configure(tag_name, background="white", foreground="black")
        
        # Colorear referentes y correferentes
        color_idx = 0
        for referente_id, tokens_referente in self.referentes.items():
            color = self.colores[color_idx % len(self.colores)]
            
            # Colorear referente
            for token_id in tokens_referente:
                parrafo_id, token_num = token_id.split("_")
                tag_name = f"token_{parrafo_id}_{token_num}"
                self.text_widget.tag_configure(tag_name, background=color, foreground="white")
            
            # Colorear correferentes
            if referente_id in self.correferentes_por_referente:
                for corref_id, corref_data in self.correferentes_por_referente[referente_id].items():
                    for token_id in corref_data["tokens"]:
                        parrafo_id, token_num = token_id.split("_")
                        tag_name = f"token_{parrafo_id}_{token_num}"
                        self.text_widget.tag_configure(tag_name, background=color, foreground="white")
            
            color_idx += 1
        
        self.text_widget.configure(state="disabled")

    def actualizar_colores_temporal(self):
        """Actualiza solo los colores de la selección temporal."""
        self.text_widget.configure(state="normal")
        
        # Resetear colores de selección temporal
        for parrafo_id in self.parrafos:
            tokens = self.tokens_por_parrafo[parrafo_id]
            for token_info in tokens:
                tag_name = f"token_{parrafo_id}_{token_info['id']}"
                # Solo resetear si no está en una relación permanente
                if not self.esta_token_en_relacion(tag_name):
                    self.text_widget.tag_configure(tag_name, background="white", foreground="black")
        
        # Colorear selección temporal
        if self.seleccion_temporal:
            color = "#FFB6C1" if self.modo_seleccion == "referente" else "#B6C1FF"
            for token_id in self.seleccion_temporal:
                parrafo_id, token_num = token_id.split("_")
                tag_name = f"token_{parrafo_id}_{token_num}"
                self.text_widget.tag_configure(tag_name, background=color, foreground="black")
        
        self.text_widget.configure(state="disabled")

    def esta_token_en_relacion(self, tag_name):
        """Verifica si un token ya está en una relación permanente."""
        for tokens_referente in self.referentes.values():
            for token_id in tokens_referente:
                parrafo_id, token_num = token_id.split("_")
                if tag_name == f"token_{parrafo_id}_{token_num}":
                    return True
        
        for referente_id in self.correferentes_por_referente:
            for corref_data in self.correferentes_por_referente[referente_id].values():
                for token_id in corref_data["tokens"]:
                    parrafo_id, token_num = token_id.split("_")
                    if tag_name == f"token_{parrafo_id}_{token_num}":
                        return True
        
        return False

    def actualizar_info_panel(self):
        """Actualiza el panel de información con las relaciones actuales."""
        self.info_text.configure(state="normal")
        self.info_text.delete("1.0", tk.END)
        
        if not self.referentes:
            self.info_text.insert(tk.END, "No hay relaciones definidas")
        else:
            for i, (referente_id, tokens_referente) in enumerate(self.referentes.items()):
                color = self.colores[i % len(self.colores)]
                self.info_text.insert(tk.END, f"{referente_id}:\n", f"color_{i}")
                self.info_text.tag_configure(f"color_{i}", background=color, foreground="white")
                
                # Mostrar tokens del referente
                self.info_text.insert(tk.END, "  Referente:\n")
                for token_id in tokens_referente:
                    parrafo_id, token_num = token_id.split("_")
                    tokens = self.tokens_por_parrafo[parrafo_id]
                    token_text = next((t["form"] for t in tokens if t["id"] == token_num), "N/A")
                    self.info_text.insert(tk.END, f"    • {token_text} (ID: {token_num})\n")
                
                # Mostrar correferentes
                if referente_id in self.correferentes_por_referente and self.correferentes_por_referente[referente_id]:
                    self.info_text.insert(tk.END, "  Correferentes:\n")
                    for corref_id, corref_data in self.correferentes_por_referente[referente_id].items():
                        self.info_text.insert(tk.END, f"    {corref_id}:\n")
                        for token_id in corref_data["tokens"]:
                            parrafo_id, token_num = token_id.split("_")
                            tokens = self.tokens_por_parrafo[parrafo_id]
                            token_text = next((t["form"] for t in tokens if t["id"] == token_num), "N/A")
                            self.info_text.insert(tk.END, f"      • {token_text} (ID: {token_num})\n")
                        etiqueta = corref_data["etiqueta"]
                        descripcion = self.etiquetas.get(etiqueta, "")
                        self.info_text.insert(tk.END, f"      [{etiqueta}: {descripcion}]\n\n")
                else:
                    self.info_text.insert(tk.END, "  (Sin correferentes)\n")
                self.info_text.insert(tk.END, "\n")
        
        self.info_text.configure(state="disabled")

    def limpiar_seleccion(self):
        """Limpia la selección temporal."""
        self.modo_seleccion = None
        self.seleccion_temporal.clear()
        self.actualizar_colores()
        self.actualizar_panel_seleccion()
        self.estado_label.config(text="Selección temporal limpiada")

    def mostrar_relaciones(self):
        """Muestra un resumen de todas las relaciones."""
        if not self.referentes:
            messagebox.showinfo("Relaciones", "No hay relaciones definidas", parent=self.ventana)
            return
        
        mensaje = "Relaciones de correferencia:\n\n"
        for referente_id, tokens_referente in self.referentes.items():
            mensaje += f"{referente_id}:\n"
            
            # Mostrar tokens del referente
            mensaje += "  Referente:\n"
            for token_id in tokens_referente:
                parrafo_id, token_num = token_id.split("_")
                tokens = self.tokens_por_parrafo[parrafo_id]
                token_text = next((t["form"] for t in tokens if t["id"] == token_num), "N/A")
                mensaje += f"    • {token_text} (ID: {token_num})\n"
            
            # Mostrar correferentes
            if referente_id in self.correferentes_por_referente:
                for corref_id, corref_data in self.correferentes_por_referente[referente_id].items():
                    mensaje += f"  {corref_id}:\n"
                    for token_id in corref_data["tokens"]:
                        parrafo_id, token_num = token_id.split("_")
                        tokens = self.tokens_por_parrafo[parrafo_id]
                        token_text = next((t["form"] for t in tokens if t["id"] == token_num), "N/A")
                        mensaje += f"    • {token_text} (ID: {token_num})\n"
                    etiqueta = corref_data["etiqueta"]
                    descripcion = self.etiquetas.get(etiqueta, "")
                    mensaje += f"    Etiqueta: {etiqueta} - {descripcion}\n"
            mensaje += "\n"
        
        messagebox.showinfo("Resumen de Relaciones", mensaje, parent=self.ventana)

    def guardar_json(self):
        """Guarda las correferencias en formato JSON con la estructura solicitada."""
        try:
            if not self.referentes:
                messagebox.showwarning("Advertencia", "No hay relaciones para guardar.", parent=self.ventana)
                return

            # Construir la estructura de anáforas
            anaphoras = {}
            
            for referente_id, tokens_referente in self.referentes.items():
                # Crear entrada para el referente
                anaphoras[referente_id] = {
                    "Ref": self.formatear_tokens_para_json(tokens_referente)
                }
                
                # Añadir correferentes si existen
                if referente_id in self.correferentes_por_referente:
                    for corref_id, corref_data in self.correferentes_por_referente[referente_id].items():
                        anaphoras[referente_id][corref_id] = {
                            "id": self.formatear_tokens_para_json(corref_data["tokens"]),
                            "etiqueta": corref_data["etiqueta"]
                        }

            # Generar nombre de archivo: <nombre>.xml → <nombre>_correferencias.json
            nombre_base = os.path.basename(self.ruta_xml).replace(".xml", "")
            nombre_archivo = f"{nombre_base}_correferencias.json"

            # Crear estructura completa del JSON
            datos_completos = {
                "metadata": {
                    "archivo_origen": os.path.basename(self.ruta_xml),
                    "tipo": "correferencias"
                },
                "Anaforas": anaphoras
            }

            # Guardar archivo
            with open(nombre_archivo, "w", encoding="utf-8") as f:
                json.dump(datos_completos, f, ensure_ascii=False, indent=2)

            resumen = (
                f"Correferencias guardadas correctamente.\n"
                f"Archivo: {nombre_archivo}\n"
                f"Referentes: {len(anaphoras)}"
            )
            messagebox.showinfo("Guardado exitoso", resumen, parent=self.ventana)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar las correferencias: {str(e)}", parent=self.ventana)

    def formatear_tokens_para_json(self, tokens):
        """Convierte una lista de tokens a formato JSON."""
        tokens_formateados = []
        for token_id in tokens:
            parrafo_id, token_num = token_id.split("_")
            tokens_list = self.tokens_por_parrafo[parrafo_id]
            token_info = next((t for t in tokens_list if t["id"] == token_num), None)
            if token_info:
                tokens_formateados.append({
                    "parrafo": parrafo_id,
                    "token_id": token_num,
                    "texto": token_info["form"]
                })
        return tokens_formateados

    def on_text_click(self, event):
        """Maneja el clic en el texto."""
        pass


class VentanaPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("SIMULTEX")
        self.root.geometry("300x200")

        # Botón para abrir correferencia
        btn = ttk.Button(
            self.root,
            text="Correferencia textual",
            command=self.correferencia_textual
        )
        btn.pack(padx=20, pady=20)

    def correferencia_textual(self):
        ruta_xml = "prueba.xml"
        tipo_texto = "ejemplo"

        if not os.path.exists(ruta_xml):
            messagebox.showerror("Error", f"No se encontró el archivo {ruta_xml}")
            return

        ventana = VentanaEtiquetadoCorreferentes(
            self.root,
            ruta_xml,
            tipo_texto
        )
        ventana.ventana.grab_set()


if __name__ == "__main__":
    root = tk.Tk()
    app = VentanaPrincipal(root)
    root.mainloop()