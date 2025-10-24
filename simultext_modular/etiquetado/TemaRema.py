import tkinter as tk
from tkinter import ttk, messagebox
import xml.etree.ElementTree as ET
import os
import json

class VentanaEtiquetadoTemaRema:
    def __init__(self, root, ruta_xml, tipo_texto):
        self.root = root
        self.ruta_xml = ruta_xml
        self.tipo_texto = tipo_texto

        # Crear ventana Toplevel
        self.ventana = self.root
        self.ventana.title("Análisis de Progresión Temática - Tema y Rema")
        self.ventana.geometry("1200x800")

        # Variables de datos
        self.parrafos = []
        self.tokens_por_parrafo = {}
        self.texto_original_por_parrafo = {}
        
        # Variables para el análisis temático
        self.estructuras_tematicas = {}  # {parrafo_id: {oracion_id: {tema: [], rema: []}}}
        self.oraciones_por_parrafo = {}
        
        # Variables de estado
        self.modo_seleccion = None  # 'tema' o 'rema'
        self.parrafo_actual = None
        self.oracion_actual = None
        self.seleccion_temporal = set()
        self.colores = {'tema': '#FF9999', 'rema': '#99FF99'}

        # Categorías de Tema y Rema
        self.categorias_tema = {
            "Tema_Dado": "Tema dado - Información conocida del contexto",
            "Tema_Nuevo": "Tema nuevo - Información introducida por primera vez",
            "Tema_Derivado": "Tema derivado - Inferido del contexto anterior",
            "Tema_Implícito": "Tema implícito - No expresado directamente"
        }
        
        self.categorias_rema = {
            "Rema_Completivo": "Rema completivo - Completa la información del tema",
            "Rema_Contrastivo": "Rema contrastivo - Establece contraste o oposición",
            "Rema_Focal": "Rema focal - Información enfatizada o destacada",
            "Rema_Expansivo": "Rema expansivo - Amplía o desarrolla la información"
        }

        # === Frame principal ===
        main_frame = ttk.Frame(self.ventana)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # === Frame para controles ===
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill="x", pady=(0, 10))

        # Botones para selección de oración
        ttk.Label(control_frame, text="Seleccionar Oración:").pack(side="left", padx=(0, 5))
        self.parrafo_var = tk.StringVar()
        self.parrafo_combo = ttk.Combobox(control_frame, textvariable=self.parrafo_var, 
                                         state="readonly", width=15)
        self.parrafo_combo.pack(side="left", padx=(0, 10))
        self.parrafo_combo.bind('<<ComboboxSelected>>', self.on_parrafo_seleccionado)

        self.oracion_var = tk.StringVar()
        self.oracion_combo = ttk.Combobox(control_frame, textvariable=self.oracion_var, 
                                         state="readonly", width=15)
        self.oracion_combo.pack(side="left", padx=(0, 20))
        self.oracion_combo.bind('<<ComboboxSelected>>', self.on_oracion_seleccionado)

        # Botones para Tema y Rema
        ttk.Button(control_frame, text="Seleccionar Tema", 
                  command=self.iniciar_seleccion_tema, style="Tema.TButton").pack(side="left", padx=(0, 10))
        ttk.Button(control_frame, text="Seleccionar Rema", 
                  command=self.iniciar_seleccion_rema, style="Rema.TButton").pack(side="left", padx=(0, 10))

        # Botones de gestión
        ttk.Button(control_frame, text="Finalizar Análisis", 
                  command=self.finalizar_analisis).pack(side="left", padx=(20, 10))
        ttk.Button(control_frame, text="Limpiar Selección", 
                  command=self.limpiar_seleccion).pack(side="left", padx=(0, 10))
        ttk.Button(control_frame, text="Ver Progresión Temática", 
                  command=self.mostrar_progresion_tematica).pack(side="left", padx=(0, 10))
        ttk.Button(control_frame, text="Guardar Análisis", 
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
        info_frame.pack(side="right", fill="y", padx=(10, 0))

        # Panel de categorías de Tema
        ttk.Label(info_frame, text="Categorías de Tema", 
                 font=("Arial", 10, "bold"), foreground="darkred").pack(pady=(0, 5))
        
        self.categoria_tema_var = tk.StringVar()
        self.categoria_tema_combo = ttk.Combobox(info_frame, textvariable=self.categoria_tema_var, 
                                                values=list(self.categorias_tema.keys()), 
                                                state="readonly")
        self.categoria_tema_combo.pack(fill="x", pady=(0, 5))
        self.categoria_tema_combo.bind('<<ComboboxSelected>>', self.mostrar_descripcion_tema)
        
        self.descripcion_tema_label = ttk.Label(info_frame, text="", wraplength=280, 
                                               font=("Arial", 8), foreground="darkred")
        self.descripcion_tema_label.pack(fill="x", pady=(0, 10))

        # Panel de categorías de Rema
        ttk.Label(info_frame, text="Categorías de Rema", 
                 font=("Arial", 10, "bold"), foreground="darkgreen").pack(pady=(0, 5))
        
        self.categoria_rema_var = tk.StringVar()
        self.categoria_rema_combo = ttk.Combobox(info_frame, textvariable=self.categoria_rema_var, 
                                                values=list(self.categorias_rema.keys()), 
                                                state="readonly")
        self.categoria_rema_combo.pack(fill="x", pady=(0, 5))
        self.categoria_rema_combo.bind('<<ComboboxSelected>>', self.mostrar_descripcion_rema)
        
        self.descripcion_rema_label = ttk.Label(info_frame, text="", wraplength=280, 
                                               font=("Arial", 8), foreground="darkgreen")
        self.descripcion_rema_label.pack(fill="x", pady=(0, 10))

        # Panel de análisis actual
        ttk.Label(info_frame, text="Análisis Actual", 
                 font=("Arial", 10, "bold")).pack(pady=(0, 5))
        
        self.seleccion_text = tk.Text(info_frame, wrap="word", width=35, height=8, 
                                     font=("Arial", 9), state="disabled")
        self.seleccion_text.pack(fill="x", pady=(0, 10))

        # Panel de progresión temática
        ttk.Label(info_frame, text="Progresión Temática", 
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
        self.estado_label = ttk.Label(bottom_frame, text="Seleccione un párrafo y oración para comenzar")
        self.estado_label.pack(side="left")

        # Configurar estilos para botones
        style = ttk.Style()
        style.configure("Tema.TButton", foreground="darkred")
        style.configure("Rema.TButton", foreground="darkgreen")

        # Cargar datos del XML
        self.cargar_datos_xml()
        self.actualizar_combo_parrafos()

    def mostrar_descripcion_tema(self, event=None):
        """Muestra la descripción de la categoría de Tema seleccionada."""
        categoria = self.categoria_tema_var.get()
        if categoria in self.categorias_tema:
            self.descripcion_tema_label.config(text=self.categorias_tema[categoria])

    def mostrar_descripcion_rema(self, event=None):
        """Muestra la descripción de la categoría de Rema seleccionada."""
        categoria = self.categoria_rema_var.get()
        if categoria in self.categorias_rema:
            self.descripcion_rema_label.config(text=self.categorias_rema[categoria])

    def on_parrafo_seleccionado(self, event=None):
        """Cuando se selecciona un párrafo del combo."""
        parrafo_id = self.parrafo_var.get()
        if parrafo_id:
            self.parrafo_actual = parrafo_id
            self.actualizar_combo_oraciones()
            self.estado_label.config(text=f"Párrafo seleccionado: {parrafo_id}")

    def on_oracion_seleccionado(self, event=None):
        """Cuando se selecciona una oración del combo."""
        oracion_id = self.oracion_var.get()
        if oracion_id and self.parrafo_actual:
            self.oracion_actual = oracion_id
            self.actualizar_panel_seleccion()
            self.estado_label.config(text=f"Analizando: P{self.parrafo_actual} - O{self.oracion_actual}")

    def cargar_datos_xml(self):
        """Carga párrafos, oraciones y tokens desde el archivo XML."""
        try:
            tree = ET.parse(self.ruta_xml)
            root = tree.getroot()

            self.parrafos = []
            self.tokens_por_parrafo = {}
            self.oraciones_por_parrafo = {}
            self.texto_original_por_parrafo = {}

            for parrafo in root.findall(".//paragraph"):
                parrafo_id = parrafo.get("id")
                self.parrafos.append(parrafo_id)
                self.oraciones_por_parrafo[parrafo_id] = []
                self.tokens_por_parrafo[parrafo_id] = {}
                self.estructuras_tematicas[parrafo_id] = {}

                texto_parrafo = ""

                for oracion in parrafo.findall(".//sentence"):
                    oracion_id = oracion.get("id")
                    self.oraciones_por_parrafo[parrafo_id].append(oracion_id)
                    self.estructuras_tematicas[parrafo_id][oracion_id] = {
                        'tema': {'tokens': [], 'categoria': ''},
                        'rema': {'tokens': [], 'categoria': ''}
                    }

                    tokens_info = []
                    for token in oracion.findall(".//token"):
                        form = token.get("form", "")
                        token_id = token.get("id", "")

                        tokens_info.append({
                            "form": form,
                            "id": token_id,
                            "form_lower": form.lower()
                        })

                        texto_parrafo += form + " "

                    self.tokens_por_parrafo[parrafo_id][oracion_id] = tokens_info

                self.texto_original_por_parrafo[parrafo_id] = texto_parrafo.strip()

            self.mostrar_texto_con_tokens()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el XML: {str(e)}", parent=self.ventana)

    def mostrar_texto_con_tokens(self):
        """Muestra el texto con los tokens formateados para selección."""
        self.text_widget.configure(state="normal")
        self.text_widget.delete("1.0", tk.END)

        for parrafo_id in self.parrafos:
            # Encabezado del párrafo
            self.text_widget.insert(tk.END, f"PÁRRAFO {parrafo_id}:\n", "parrafo_header")
            
            for oracion_id in self.oraciones_por_parrafo[parrafo_id]:
                # Encabezado de oración
                self.text_widget.insert(tk.END, f"  Oración {oracion_id}: ", "oracion_header")
                
                tokens = self.tokens_por_parrafo[parrafo_id][oracion_id]
                
                for token_info in tokens:
                    token_text = token_info['form']
                    token_id_text = f"({token_info['id']}) "

                    tag_name = f"token_{parrafo_id}_{oracion_id}_{token_info['id']}"

                    # Insertar palabra
                    self.text_widget.insert(tk.END, token_text, (tag_name, "token_text"))
                    # Insertar id
                    self.text_widget.insert(tk.END, token_id_text, (tag_name, "token_id"))

                    # Tag principal para eventos
                    self.text_widget.tag_bind(tag_name, "<Button-1>",
                                            lambda e, tid=token_info['id'], pid=parrafo_id, oid=oracion_id:
                                            self.seleccionar_token(tid, pid, oid))

                self.text_widget.insert(tk.END, "\n")
            
            self.text_widget.insert(tk.END, "\n")
        
        # Configurar estilos
        self.text_widget.tag_configure("parrafo_header", font=("Arial", 12, "bold"), 
                                      foreground="darkblue", spacing3=8)
        self.text_widget.tag_configure("oracion_header", font=("Arial", 10, "bold"), 
                                      foreground="darkgreen")
        self.text_widget.tag_configure("token_text", font=("Arial", 11))
        self.text_widget.tag_configure("token_id", font=("Arial", 6), foreground="gray")
        
        self.text_widget.configure(state="disabled")

    def actualizar_combo_parrafos(self):
        """Actualiza el combobox de párrafos."""
        self.parrafo_combo['values'] = self.parrafos
        if self.parrafos and not self.parrafo_var.get():
            self.parrafo_var.set(self.parrafos[0])
            self.parrafo_actual = self.parrafos[0]
            self.actualizar_combo_oraciones()

    def actualizar_combo_oraciones(self):
        """Actualiza el combobox de oraciones para el párrafo actual."""
        if self.parrafo_actual:
            oraciones = self.oraciones_por_parrafo[self.parrafo_actual]
            self.oracion_combo['values'] = oraciones
            if oraciones and not self.oracion_var.get():
                self.oracion_var.set(oraciones[0])
                self.oracion_actual = oraciones[0]
                self.actualizar_panel_seleccion()

    def iniciar_seleccion_tema(self):
        """Inicia la selección de Tema."""
        if not self.oracion_actual:
            messagebox.showwarning("Advertencia", 
                                 "Primero debe seleccionar una oración.", 
                                 parent=self.ventana)
            return
        
        self.modo_seleccion = "tema"
        self.seleccion_temporal.clear()
        self.actualizar_panel_seleccion()
        self.actualizar_colores_temporal()
        self.estado_label.config(text="Seleccionando TEMA - Elija los tokens que constituyen el tema")

    def iniciar_seleccion_rema(self):
        """Inicia la selección de Rema."""
        if not self.oracion_actual:
            messagebox.showwarning("Advertencia", 
                                 "Primero debe seleccionar una oración.", 
                                 parent=self.ventana)
            return
        
        self.modo_seleccion = "rema"
        self.seleccion_temporal.clear()
        self.actualizar_panel_seleccion()
        self.actualizar_colores_temporal()
        self.estado_label.config(text="Seleccionando REMA - Elija los tokens que constituyen el rema")

    def finalizar_analisis(self):
        """Finaliza el análisis de Tema/Rema para la oración actual."""
        if not self.oracion_actual or not self.parrafo_actual:
            messagebox.showwarning("Advertencia", 
                                 "No hay oración seleccionada.", 
                                 parent=self.ventana)
            return
        
        if self.modo_seleccion == "tema" and not self.categoria_tema_var.get():
            messagebox.showwarning("Advertencia", 
                                 "Debe seleccionar una categoría para el Tema.", 
                                 parent=self.ventana)
            return
        
        if self.modo_seleccion == "rema" and not self.categoria_rema_var.get():
            messagebox.showwarning("Advertencia", 
                                 "Debe seleccionar una categoría para el Rema.", 
                                 parent=self.ventana)
            return
        
        if self.modo_seleccion == "tema":
            # Guardar Tema
            self.estructuras_tematicas[self.parrafo_actual][self.oracion_actual]['tema'] = {
                'tokens': sorted(self.seleccion_temporal),
                'categoria': self.categoria_tema_var.get()
            }
            self.estado_label.config(text=f"Tema definido para Oración {self.oracion_actual}")
            
        elif self.modo_seleccion == "rema":
            # Guardar Rema
            self.estructuras_tematicas[self.parrafo_actual][self.oracion_actual]['rema'] = {
                'tokens': sorted(self.seleccion_temporal),
                'categoria': self.categoria_rema_var.get()
            }
            self.estado_label.config(text=f"Rema definido para Oración {self.oracion_actual}")
        
        # Limpiar selección temporal
        self.modo_seleccion = None
        self.seleccion_temporal.clear()
        
        self.actualizar_colores()
        self.actualizar_info_panel()
        self.actualizar_panel_seleccion()

    def seleccionar_token(self, token_id, parrafo_id, oracion_id):
        """Maneja la selección de un token."""
        if parrafo_id != self.parrafo_actual or oracion_id != self.oracion_actual:
            messagebox.showwarning("Advertencia", 
                                 "Solo puede seleccionar tokens de la oración actual.", 
                                 parent=self.ventana)
            return
        
        token_full_id = f"{parrafo_id}_{oracion_id}_{token_id}"
        
        if self.modo_seleccion in ['tema', 'rema']:
            if token_full_id in self.seleccion_temporal:
                # Deseleccionar
                self.seleccion_temporal.remove(token_full_id)
            else:
                # Seleccionar
                self.seleccion_temporal.add(token_full_id)
            
            self.actualizar_colores_temporal()
            self.actualizar_panel_seleccion()

    def actualizar_panel_seleccion(self):
        """Actualiza el panel de análisis actual."""
        self.seleccion_text.configure(state="normal")
        self.seleccion_text.delete("1.0", tk.END)
        
        if self.parrafo_actual and self.oracion_actual:
            self.seleccion_text.insert(tk.END, f"Párrafo: {self.parrafo_actual}\n")
            self.seleccion_text.insert(tk.END, f"Oración: {self.oracion_actual}\n\n")
            
            # Mostrar análisis actual de la oración
            analisis = self.estructuras_tematicas[self.parrafo_actual][self.oracion_actual]
            
            if analisis['tema']['tokens']:
                self.seleccion_text.insert(tk.END, "TEMA definido:\n", "tema_tag")
                self.seleccion_text.insert(tk.END, f"Categoría: {analisis['tema']['categoria']}\n")
                for token_id in analisis['tema']['tokens']:
                    token_text = self.obtener_texto_token(token_id)
                    self.seleccion_text.insert(tk.END, f"• {token_text}\n")
                self.seleccion_text.insert(tk.END, "\n")
            else:
                self.seleccion_text.insert(tk.END, "TEMA: No definido\n\n")
            
            if analisis['rema']['tokens']:
                self.seleccion_text.insert(tk.END, "REMA definido:\n", "rema_tag")
                self.seleccion_text.insert(tk.END, f"Categoría: {analisis['rema']['categoria']}\n")
                for token_id in analisis['rema']['tokens']:
                    token_text = self.obtener_texto_token(token_id)
                    self.seleccion_text.insert(tk.END, f"• {token_text}\n")
            else:
                self.seleccion_text.insert(tk.END, "REMA: No definido\n")
            
            # Mostrar selección temporal
            if self.modo_seleccion and self.seleccion_temporal:
                self.seleccion_text.insert(tk.END, f"\nSeleccionando {self.modo_seleccion.upper()}:\n")
                for token_id in sorted(self.seleccion_temporal):
                    token_text = self.obtener_texto_token(token_id)
                    self.seleccion_text.insert(tk.END, f"• {token_text}\n")
        
        else:
            self.seleccion_text.insert(tk.END, "Seleccione un párrafo y oración")
        
        # Configurar colores para Tema y Rema
        self.seleccion_text.tag_configure("tema_tag", foreground="darkred")
        self.seleccion_text.tag_configure("rema_tag", foreground="darkgreen")
        self.seleccion_text.configure(state="disabled")

    def obtener_texto_token(self, token_full_id):
        """Obtiene el texto de un token dado su ID completo."""
        try:
            parrafo_id, oracion_id, token_id = token_full_id.split('_')
            tokens = self.tokens_por_parrafo[parrafo_id][oracion_id]
            token_info = next((t for t in tokens if t['id'] == token_id), None)
            return token_info['form'] if token_info else "N/A"
        except:
            return "N/A"

    def actualizar_colores(self):
        """Actualiza los colores de los tokens según el análisis temático."""
        self.text_widget.configure(state="normal")
        
        # Resetear todos los colores
        for parrafo_id in self.parrafos:
            for oracion_id in self.oraciones_por_parrafo[parrafo_id]:
                tokens = self.tokens_por_parrafo[parrafo_id][oracion_id]
                for token_info in tokens:
                    tag_name = f"token_{parrafo_id}_{oracion_id}_{token_info['id']}"
                    self.text_widget.tag_configure(tag_name, background="white", foreground="black")
        
        # Colorear según el análisis
        for parrafo_id, oraciones in self.estructuras_tematicas.items():
            for oracion_id, analisis in oraciones.items():
                # Colorear Tema
                for token_id in analisis['tema']['tokens']:
                    tag_name = f"token_{token_id}"
                    self.text_widget.tag_configure(tag_name, background=self.colores['tema'], 
                                                 foreground="black", relief="raised")
                
                # Colorear Rema
                for token_id in analisis['rema']['tokens']:
                    tag_name = f"token_{token_id}"
                    self.text_widget.tag_configure(tag_name, background=self.colores['rema'], 
                                                 foreground="black", relief="raised")
        
        self.text_widget.configure(state="disabled")

    def actualizar_colores_temporal(self):
        """Actualiza solo los colores de la selección temporal."""
        if not self.modo_seleccion:
            return
            
        self.text_widget.configure(state="normal")
        
        # Resetear colores de selección temporal en la oración actual
        if self.parrafo_actual and self.oracion_actual:
            tokens = self.tokens_por_parrafo[self.parrafo_actual][self.oracion_actual]
            for token_info in tokens:
                tag_name = f"token_{self.parrafo_actual}_{self.oracion_actual}_{token_info['id']}"
                # Solo resetear si no está en el análisis permanente
                if not self.esta_token_en_analisis(tag_name):
                    self.text_widget.tag_configure(tag_name, background="white", foreground="black")
        
        # Colorear selección temporal
        if self.seleccion_temporal:
            color = self.colores[self.modo_seleccion]
            for token_id in self.seleccion_temporal:
                tag_name = f"token_{token_id}"
                self.text_widget.tag_configure(tag_name, background=color, foreground="black", 
                                             relief="sunken")
        
        self.text_widget.configure(state="disabled")

    def esta_token_en_analisis(self, tag_name):
        """Verifica si un token ya está en el análisis permanente."""
        for parrafo_id, oraciones in self.estructuras_tematicas.items():
            for oracion_id, analisis in oraciones.items():
                for token_id in analisis['tema']['tokens']:
                    if tag_name == f"token_{token_id}":
                        return True
                for token_id in analisis['rema']['tokens']:
                    if tag_name == f"token_{token_id}":
                        return True
        return False

    def actualizar_info_panel(self):
        """Actualiza el panel de información con la progresión temática."""
        self.info_text.configure(state="normal")
        self.info_text.delete("1.0", tk.END)
        
        if not any(any(analisis['tema']['tokens'] or analisis['rema']['tokens'] 
                      for analisis in oraciones.values()) 
                  for oraciones in self.estructuras_tematicas.values()):
            self.info_text.insert(tk.END, "No hay análisis temático definido")
        else:
            for parrafo_id in self.parrafos:
                if any(analisis['tema']['tokens'] or analisis['rema']['tokens'] 
                      for analisis in self.estructuras_tematicas[parrafo_id].values()):
                    
                    self.info_text.insert(tk.END, f"PÁRRAFO {parrafo_id}:\n", "parrafo_info")
                    
                    for oracion_id in self.oraciones_por_parrafo[parrafo_id]:
                        analisis = self.estructuras_tematicas[parrafo_id][oracion_id]
                        
                        if analisis['tema']['tokens'] or analisis['rema']['tokens']:
                            self.info_text.insert(tk.END, f"  Oración {oracion_id}:\n")
                            
                            if analisis['tema']['tokens']:
                                self.info_text.insert(tk.END, "    TEMA: ", "tema_info")
                                tema_tokens = [self.obtener_texto_token(tid) for tid in analisis['tema']['tokens']]
                                self.info_text.insert(tk.END, f"{' '.join(tema_tokens)}\n")
                                if analisis['tema']['categoria']:
                                    desc = self.categorias_tema.get(analisis['tema']['categoria'], "")
                                    self.info_text.insert(tk.END, f"    [{analisis['tema']['categoria']}: {desc}]\n")
                            
                            if analisis['rema']['tokens']:
                                self.info_text.insert(tk.END, "    REMA: ", "rema_info")
                                rema_tokens = [self.obtener_texto_token(tid) for tid in analisis['rema']['tokens']]
                                self.info_text.insert(tk.END, f"{' '.join(rema_tokens)}\n")
                                if analisis['rema']['categoria']:
                                    desc = self.categorias_rema.get(analisis['rema']['categoria'], "")
                                    self.info_text.insert(tk.END, f"    [{analisis['rema']['categoria']}: {desc}]\n")
                            
                            self.info_text.insert(tk.END, "\n")
                    
                    self.info_text.insert(tk.END, "\n")
        
        # Configurar colores
        self.info_text.tag_configure("parrafo_info", font=("Arial", 9, "bold"), foreground="darkblue")
        self.info_text.tag_configure("tema_info", foreground="darkred")
        self.info_text.tag_configure("rema_info", foreground="darkgreen")
        self.info_text.configure(state="disabled")

    def limpiar_seleccion(self):
        """Limpia la selección temporal."""
        self.modo_seleccion = None
        self.seleccion_temporal.clear()
        self.actualizar_colores()
        self.actualizar_panel_seleccion()
        self.estado_label.config(text="Selección temporal limpiada")

    def mostrar_progresion_tematica(self):
        """Muestra un resumen de la progresión temática."""
        mensaje = "PROGRESIÓN TEMÁTICA - TEMA Y REMA:\n\n"
        
        for parrafo_id in self.parrafos:
            tiene_analisis = False
            parrafo_msg = f"Párrafo {parrafo_id}:\n"
            
            for oracion_id in self.oraciones_por_parrafo[parrafo_id]:
                analisis = self.estructuras_tematicas[parrafo_id][oracion_id]
                
                if analisis['tema']['tokens'] or analisis['rema']['tokens']:
                    tiene_analisis = True
                    oracion_msg = f"  Oración {oracion_id}:\n"
                    
                    if analisis['tema']['tokens']:
                        tema_tokens = [self.obtener_texto_token(tid) for tid in analisis['tema']['tokens']]
                        oracion_msg += f"    TEMA: {' '.join(tema_tokens)}\n"
                        if analisis['tema']['categoria']:
                            oracion_msg += f"    Categoría: {analisis['tema']['categoria']}\n"
                    
                    if analisis['rema']['tokens']:
                        rema_tokens = [self.obtener_texto_token(tid) for tid in analisis['rema']['tokens']]
                        oracion_msg += f"    REMA: {' '.join(rema_tokens)}\n"
                        if analisis['rema']['categoria']:
                            oracion_msg += f"    Categoría: {analisis['rema']['categoria']}\n"
                    
                    parrafo_msg += oracion_msg + "\n"
            
            if tiene_analisis:
                mensaje += parrafo_msg + "\n"
        
        if mensaje == "PROGRESIÓN TEMÁTICA - TEMA Y REMA:\n\n":
            mensaje += "No hay análisis temático definido"
        
        messagebox.showinfo("Progresión Temática - Tema y Rema", mensaje, parent=self.ventana)

    def guardar_json(self):
        """Guarda el análisis temático en formato JSON."""
        try:
            # Verificar que hay análisis para guardar
            tiene_analisis = False
            for parrafo_id, oraciones in self.estructuras_tematicas.items():
                for oracion_id, analisis in oraciones.items():
                    if analisis['tema']['tokens'] or analisis['rema']['tokens']:
                        tiene_analisis = True
                        break
                if tiene_analisis:
                    break
            
            if not tiene_analisis:
                messagebox.showwarning("Advertencia", "No hay análisis temático para guardar.", parent=self.ventana)
                return

            # Construir la estructura de datos
            datos_analisis = {}
            
            for parrafo_id, oraciones in self.estructuras_tematicas.items():
                datos_analisis[parrafo_id] = {}
                
                for oracion_id, analisis in oraciones.items():
                    if analisis['tema']['tokens'] or analisis['rema']['tokens']:
                        datos_analisis[parrafo_id][oracion_id] = {}
                        
                        if analisis['tema']['tokens']:
                            datos_analisis[parrafo_id][oracion_id]['tema'] = {
                                'tokens': self.formatear_tokens_para_json(analisis['tema']['tokens']),
                                'categoria': analisis['tema']['categoria'],
                                'descripcion': self.categorias_tema.get(analisis['tema']['categoria'], "")
                            }
                        
                        if analisis['rema']['tokens']:
                            datos_analisis[parrafo_id][oracion_id]['rema'] = {
                                'tokens': self.formatear_tokens_para_json(analisis['rema']['tokens']),
                                'categoria': analisis['rema']['categoria'],
                                'descripcion': self.categorias_rema.get(analisis['rema']['categoria'], "")
                            }

            # Generar nombre de archivo
            nombre_base = os.path.basename(self.ruta_xml).replace(".xml", "")
            nombre_archivo = f"{nombre_base}_tema_rema.json"

            # Crear estructura completa del JSON
            datos_completos = {
                "metadata": {
                    "archivo_origen": os.path.basename(self.ruta_xml),
                    "tipo_analisis": "tema_rema",
                    "categorias_tema": self.categorias_tema,
                    "categorias_rema": self.categorias_rema
                },
                "analisis_tematico": datos_analisis
            }

            # Guardar archivo
            with open(nombre_archivo, "w", encoding="utf-8") as f:
                json.dump(datos_completos, f, ensure_ascii=False, indent=2)

            # Contar análisis realizados
            total_oraciones = sum(len(oraciones) for oraciones in datos_analisis.values())
            resumen = (
                f"Análisis de Tema y Rema guardado correctamente.\n"
                f"Archivo: {nombre_archivo}\n"
                f"Párrafos analizados: {len(datos_analisis)}\n"
                f"Oraciones analizadas: {total_oraciones}"
            )
            messagebox.showinfo("Guardado exitoso", resumen, parent=self.ventana)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el análisis: {str(e)}", parent=self.ventana)

    def formatear_tokens_para_json(self, tokens):
        """Convierte una lista de tokens a formato JSON."""
        tokens_formateados = []
        for token_id in tokens:
            parrafo_id, oracion_id, token_num = token_id.split('_')
            tokens_list = self.tokens_por_parrafo[parrafo_id][oracion_id]
            token_info = next((t for t in tokens_list if t["id"] == token_num), None)
            if token_info:
                tokens_formateados.append({
                    "parrafo": parrafo_id,
                    "oracion": oracion_id,
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
        self.root.title("SIMULTEX - Análisis de Tema y Rema")
        self.root.geometry("300x200")

        # Botón para abrir análisis de Tema y Rema
        btn = ttk.Button(
            self.root,
            text="Análisis Tema-Rema",
            command=self.analisis_tema_rema
        )
        btn.pack(padx=20, pady=20)

    def analisis_tema_rema(self):
        ruta_xml = "prueba.xml"
        tipo_texto = "ejemplo"

        if not os.path.exists(ruta_xml):
            messagebox.showerror("Error", f"No se encontró el archivo {ruta_xml}")
            return

        ventana = VentanaEtiquetadoTemaRema(
            self.root,
            ruta_xml,
            tipo_texto
        )
        ventana.ventana.grab_set()


if __name__ == "__main__":
    root = tk.Tk()
    app = VentanaPrincipal(root)
    root.mainloop()