import tkinter as tk
import os
import json
from tkinter import ttk, scrolledtext, messagebox
import xml.etree.ElementTree as ET
from . import config


class VentanaEtiquetadoParrafos:
    def __init__(self, root, ruta_json, tipo_texto):
        self.root = root
        self.root.title("SIMULTEXT - Etiquetado de Párrafos")
        self.root.geometry("1400x750")
        self.root.configure(bg=config.COLOR_FONDO)
        
        self.ruta_json = ruta_json
        self.tipo_texto = tipo_texto
        self.parrafos = []
        self.etiquetas_parrafos = {}

        # Tipos de discurso
        self.tipos_discurso_disponibles = list(config.TIPOS_DISCURSO.keys())

        # Configurar etiquetas según tipo de texto
        if tipo_texto == "Argumentativo":
            self.etiquetas = config.ETIQUETAS_ARGUMENTATIVO
        elif tipo_texto == "Narrativo":
            self.etiquetas = config.ETIQUETAS_NARRATIVO
        else:
            self.etiquetas = config.ETIQUETAS_ARGUMENTATIVO
        self.etiquetas_disponibles = list(self.etiquetas.keys())
        
        self.cargar_datos_desde_json()
        self.crear_interfaz()

    def cargar_datos_desde_json(self):
        """Carga los párrafos y etiquetas existentes desde el JSON."""
        try:
            with open(self.ruta_json, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            # Cargar etiquetas existentes si las hay
            etiquetado = datos.get("document", {}).get("Etiquetado", {})
            self.etiquetas_existentes_parrafos = etiquetado.get("parrafos", {})
            self.etiquetas_existentes_discurso = etiquetado.get("discurso", [])
            
            # Cargar párrafos desde la estructura del documento
            self.parrafos = []
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
                
                # Extraer texto del párrafo desde las oraciones y tokens
                texto_parrafo = ""
                oraciones_parrafo = parrafo.get("sentence", [])
                
                # Si es una sola oración (diccionario), convertirla a lista
                if isinstance(oraciones_parrafo, dict):
                    oraciones_parrafo = [oraciones_parrafo]
                
                for oracion in oraciones_parrafo:
                    if not oracion:
                        continue
                    
                    # Extraer texto de la oración desde los tokens
                    tokens = oracion.get("token", [])
                    
                    # Si es un solo token (diccionario), convertirlo a lista
                    if isinstance(tokens, dict):
                        tokens = [tokens]
                    
                    for token in tokens:
                        if isinstance(token, dict):
                            texto_parrafo += token.get("@form", "") + " "
                
                self.parrafos.append({
                    "id": id_parrafo,
                    "texto": texto_parrafo.strip()
                })

            print(f"Se cargaron {len(self.parrafos)} párrafos desde el JSON")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el JSON: {str(e)}")
            print(f"Error detallado: {e}")

    def crear_interfaz(self):
        main_frame = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Lado izquierdo: texto
        left_frame = ttk.Frame(main_frame, style='Fondo.TFrame')
        main_frame.add(left_frame, weight=1)

        titulo_label = ttk.Label(
            left_frame, text="TEXTO COMPLETO", 
            font=("Arial", 14, "bold"),
            foreground=config.COLOR_TITULO, background=config.COLOR_FONDO
        )
        titulo_label.pack(pady=10)
        
        self.texto_area = scrolledtext.ScrolledText(
            left_frame, wrap=tk.WORD, font=(config.FUENTE_TEXTO, 8),width=55,
            bg=config.COLOR_FONDO, fg=config.COLOR_TEXTO,
            relief=tk.FLAT, borderwidth=1, padx=10, pady=10
        )
        self.texto_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.mostrar_texto_completo()

        # Lado derecho: etiquetado
        right_frame = ttk.Frame(main_frame, style='Fondo.TFrame')
        main_frame.add(right_frame, weight=3)

        titulo_etiquetado = ttk.Label(
            right_frame, text="ETIQUETADO DE PÁRRAFOS",
            font=("Arial", 14, "bold"),
            foreground=config.COLOR_TITULO, background=config.COLOR_FONDO
        )
        titulo_etiquetado.pack(pady=10)
        
        tipo_label = ttk.Label(
            right_frame, text=f"Tipo: {self.tipo_texto}", 
            font=("Arial", 10, "italic"),
            foreground=config.COLOR_TEXTO, background=config.COLOR_FONDO
        )
        tipo_label.pack(pady=5)

        # Mostrar información de etiquetas existentes
        if self.etiquetas_existentes_parrafos or self.etiquetas_existentes_discurso:
            info_text = []
            if self.etiquetas_existentes_parrafos:
                info_text.append(f"{len(self.etiquetas_existentes_parrafos)} párrafos etiquetados")
            if self.etiquetas_existentes_discurso:
                info_text.append(f"{len(self.etiquetas_existentes_discurso)} tipos de discurso")
            
            info_label = ttk.Label(
                right_frame,
                text=f"✓ Se cargaron previamente: {', '.join(info_text)}",
                font=("Arial", 10, "italic"),
                foreground=config.COLOR_BOTON_VERDE,
                background=config.COLOR_FONDO
            )
            info_label.pack(pady=5)
        
        parrafos_frame = ttk.Frame(right_frame, style='Fondo.TFrame')
        parrafos_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollable
        canvas = tk.Canvas(parrafos_frame, bg=config.COLOR_FONDO, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parrafos_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Fondo.TFrame')
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Widgets párrafos
        self.widgets_parrafos = {}
        for parrafo in self.parrafos:
            frame_parrafo = ttk.Frame(scrollable_frame, relief="solid", borderwidth=1, style='Borde.TFrame')
            frame_parrafo.pack(fill=tk.X, pady=8, padx=5)
            
            label_parrafo = ttk.Label(
                frame_parrafo, text=f"PÁRRAFO {parrafo['id']}",
                font=("Arial", 10, "bold"),
                foreground=config.COLOR_TITULO, background=config.COLOR_FONDO
            )
            label_parrafo.pack(anchor="w", padx=5, pady=2)
            
            texto_corto = parrafo['texto'][:150] + "..." if len(parrafo['texto']) > 150 else parrafo['texto']
            label_texto = ttk.Label(
                frame_parrafo, text=texto_corto, wraplength=350, justify="left",
                font=config.FUENTE_TEXTO, foreground=config.COLOR_TEXTO, background=config.COLOR_FONDO
            )
            label_texto.pack(anchor="w", padx=5, pady=3)

            # Radiobuttons para etiquetas
            var = tk.StringVar(value="")
            
            # Establecer valor inicial si existe etiqueta guardada
            if parrafo['id'] in self.etiquetas_existentes_parrafos:
                etiqueta_guardada = self.etiquetas_existentes_parrafos[parrafo['id']]
                # Buscar la clave correspondiente al valor guardado
                for clave, valor in self.etiquetas.items():
                    if valor == etiqueta_guardada:
                        var.set(clave)
                        break
            
            opciones_frame = ttk.Frame(frame_parrafo, style="Fondo.TFrame")
            opciones_frame.pack(anchor="w", padx=10, pady=3)

            for etiqueta in self.etiquetas_disponibles:
                ttk.Radiobutton(
                    opciones_frame, text=etiqueta,
                    variable=var, value=etiqueta,
                    style="Fondo.TRadiobutton"
                ).pack(side=tk.LEFT, padx=3)

            self.widgets_parrafos[parrafo['id']] = var

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # === Vincular scroll con la rueda del mouse ===
        def _on_mousewheel_linux(event):
            if event.num == 4:  # rueda arriba
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:  # rueda abajo
                canvas.yview_scroll(1, "units")

        canvas.bind("<Button-4>", _on_mousewheel_linux)
        canvas.bind("<Button-5>", _on_mousewheel_linux)

        # Sección Discurso
        marco_discurso = ttk.Frame(right_frame, style='Fondo.TFrame')
        marco_discurso.pack(fill=tk.X, pady=10, padx=5)
        
        ttk.Label(
            marco_discurso, text="TIPO DE DISCURSO",
            font=("Arial", 12, "bold"),
            foreground=config.COLOR_TITULO, background=config.COLOR_FONDO
        ).pack(anchor="w", pady=3)
        
        self.vars_discurso = {}
        frame_checks = ttk.Frame(marco_discurso, style='Fondo.TFrame')
        frame_checks.pack(fill=tk.X)

        for i, tipo in enumerate(self.tipos_discurso_disponibles):
            var = tk.BooleanVar(value=False)
            
            # Establecer valor inicial si existe en etiquetas guardadas
            if self.etiquetas_existentes_discurso:
                codigo_discurso = config.TIPOS_DISCURSO[tipo]
                if codigo_discurso in self.etiquetas_existentes_discurso:
                    var.set(True)
            
            self.vars_discurso[tipo] = var
            ttk.Checkbutton(
                frame_checks, text=tipo,
                variable=var, style='Fondo.TCheckbutton'
            ).grid(row=i // 2, column=i % 2, sticky="w", padx=5, pady=2)

        # Botones
        botones_frame = ttk.Frame(right_frame, style='Fondo.TFrame')
        botones_frame.pack(pady=15, padx=5, fill=tk.X)

        self.btn_guardar = tk.Button(
            botones_frame, text="GUARDAR", command=self.guardar_etiquetas,
            bg=config.COLOR_BOTON_VERDE, fg=config.COLOR_BOTON_TEXTO,
            font=config.FUENTE_BOTON, borderwidth=1, relief="raised", height=1
        )
        self.btn_guardar.pack(side=tk.LEFT, padx=5, expand=True)

        self.btn_cancelar = tk.Button(
            botones_frame, text="CANCELAR", command=self.root.destroy,
            bg=config.COLOR_BOTON_AZUL_CLARO, fg=config.COLOR_BOTON_TEXTO,
            font=config.FUENTE_BOTON, borderwidth=1, relief="raised", height=1
        )
        self.btn_cancelar.pack(side=tk.LEFT, padx=5, expand=True)

        self.configurar_estilos()

    def configurar_estilos(self):
        style = ttk.Style()
        style.configure('Fondo.TFrame', background=config.COLOR_FONDO)
        style.configure('Borde.TFrame', background=config.COLOR_FONDO)
        style.configure('TLabel', background=config.COLOR_FONDO, foreground=config.COLOR_TEXTO)
        style.configure("Fondo.TRadiobutton", background=config.COLOR_FONDO, foreground=config.COLOR_TEXTO)
        style.configure('Fondo.TCheckbutton', background=config.COLOR_FONDO, foreground=config.COLOR_TEXTO)

    def mostrar_texto_completo(self):
        texto_formateado = ""
        for parrafo in self.parrafos:
            texto_formateado += f"PÁRRAFO {parrafo['id'].upper()}\n{'-'*40}\n{parrafo['texto']}\n\n"
        self.texto_area.delete(1.0, tk.END)
        self.texto_area.insert(tk.END, texto_formateado.strip())
        self.texto_area.config(state=tk.DISABLED)

    def guardar_etiquetas(self):
        try:
            etiquetas_guardar = {}
            parrafos_sin_etiqueta = []
            
            for parrafo_id, var in self.widgets_parrafos.items():
                clave_etiqueta = var.get()
                if clave_etiqueta:
                    valor_etiqueta = self.etiquetas.get(clave_etiqueta, clave_etiqueta)
                    etiquetas_guardar[parrafo_id] = valor_etiqueta
                else:
                    parrafos_sin_etiqueta.append(parrafo_id)
            
            if not etiquetas_guardar:
                messagebox.showwarning("Etiquetado incompleto", "No hay párrafos etiquetados.",parent=self.root)
                return
            
            if parrafos_sin_etiqueta:
                if not messagebox.askyesno("Incompleto", f"Hay {len(parrafos_sin_etiqueta)} párrafos sin etiquetar.\n¿Deseas guardar de todas formas?",parent=self.root):
                    return

            discurso_guardar = [
                config.TIPOS_DISCURSO[tipo]
                for tipo, valor in self.vars_discurso.items()
                if valor.get()
            ]

            # Cargar el JSON existente
            with open(self.ruta_json, 'r', encoding='utf-8') as f:
                datos = json.load(f)

            # Actualizar las etiquetas en el JSON
            if 'document' not in datos:
                datos['document'] = {}
            
            if 'Etiquetado' not in datos['document']:
                datos['document']['Etiquetado'] = {}
            
            datos['document']['Etiquetado']['parrafos'] = etiquetas_guardar
            datos['document']['Etiquetado']['discurso'] = discurso_guardar

            # Guardar el JSON actualizado
            with open(self.ruta_json, 'w', encoding='utf-8') as f:
                json.dump(datos, f, ensure_ascii=False, indent=2)
            
            resumen = f" Etiquetas guardadas!\n Archivo: {os.path.basename(self.ruta_json)}\n Tipo: {self.tipo_texto}\n Párrafos etiquetados: {len(etiquetas_guardar)}\n Categorías discurso: {len(discurso_guardar)}"
            messagebox.showinfo("Guardado exitoso", resumen,parent=self.root)
            self.root.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar las etiquetas: {str(e)}")