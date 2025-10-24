import tkinter as tk
from tkinter import filedialog, messagebox
import etiquetado.config as config
import xmltodict
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from etiquetado.parrafos import VentanaEtiquetadoParrafos
from etiquetado.oraciones import VentanaEtiquetadoOraciones
from etiquetado.conectores import VentanaEtiquetadoConectores
from etiquetado.correferentes import VentanaEtiquetadoCorreferentes
from etiquetado.TemaRema import VentanaEtiquetadoTemaRema


class Simultext:
    def __init__(self, root):
        self.root = root
        self.root.title("SIMULTEXT")
        self.root.geometry(f"{config.VENTANA_ANCHO}x{config.VENTANA_ALTO}")
        self.root.configure(bg=config.COLOR_FONDO)
        self.root.minsize(600, 420)

        # Variables para archivos - SOLO guardamos la ruta del JSON
        self.archivo_json = None  # Esta es la ruta principal que usaremos
        self.tipo_texto = "N/A"

        # --------------------
        # Titulo
        # --------------------
        self.etiqueta_titulo = tk.Label(
            root,
            text="SIMULTEXT",
            font=config.FUENTE_TITULO,
            fg=config.COLOR_TITULO,
            bg=config.COLOR_FONDO,
            justify=tk.CENTER
        )
        self.etiqueta_titulo.pack(pady=(20, 6))

        # Subtitulo
        self.etiqueta_subtitulo = tk.Label(
            root,
            text="Sistema Informatico Multinivel para el etiquetado de corpus a partir de la Linguistica Textual",
            font=config.FUENTE_TEXTO,
            fg=config.COLOR_TITULO,
            bg=config.COLOR_FONDO,
            wraplength=config.VENTANA_ANCHO - 80,
            justify=tk.CENTER
        )
        self.etiqueta_subtitulo.pack(pady=(0, 12))

        # --------------------
        # Frame de metadatos
        # --------------------
        marco_metadatos = tk.Frame(root, bg=config.COLOR_FONDO)
        marco_metadatos.pack(padx=20, pady=8, fill="x")
        marco_metadatos.columnconfigure(1, weight=1)

        self.campos_metadatos = {}
        etiquetas_metadatos = {
            "Titulo": "titulo",
            "ID del Documento": "numero",
            "Nivel": "nivel",
            "Genero Textual": "genero_textual",
            "Pais": "pais",
        }
        for fila, (etiqueta, campo) in enumerate(etiquetas_metadatos.items()):
            tk.Label(marco_metadatos, text=f"{etiqueta}:", font=config.FUENTE_TEXTO, bg=config.COLOR_FONDO).grid(row=fila, column=0, sticky="w", padx=5, pady=2)
            entrada = tk.Entry(marco_metadatos, font=config.FUENTE_TEXTO)
            entrada.grid(row=fila, column=1, padx=5, pady=2, sticky="ew")
            entrada.config(state=tk.DISABLED)
            self.campos_metadatos[campo] = entrada

        # --------------------
        # Frame de botones PRINCIPALES
        # --------------------
        marco_botones = tk.Frame(root, bg=config.COLOR_FONDO)
        marco_botones.pack(padx=30, pady=18, fill="x", expand=False)

        # Configurar 3 columnas para los botones principales
        marco_botones.columnconfigure(0, weight=1)
        marco_botones.columnconfigure(1, weight=1)
        marco_botones.columnconfigure(2, weight=1)

        opciones_boton = dict(borderwidth=1, relief="raised", font=config.FUENTE_BOTON, 
                            fg=config.COLOR_BOTON_TEXTO, height=config.ALTURA_BOTON1)

        # Primera fila de botones
        self.boton_nuevo_proyecto = tk.Button(
            marco_botones,
            text="Nuevo Proyecto\n(Seleccionar XML)",
            command=self.nuevo_proyecto,
            bg=config.COLOR_BOTON_VERDE,
            **opciones_boton
        )
        self.boton_nuevo_proyecto.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.boton_abrir_proyecto = tk.Button(
            marco_botones,
            text="Abrir Proyecto\n(Seleccionar JSON)",
            command=self.abrir_proyecto,
            bg=config.COLOR_BOTON_VERDE_CLARO,
            **opciones_boton
        )
        self.boton_abrir_proyecto.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.boton_etiquetar_parrafos = tk.Button(
            marco_botones,
            text="Etiquetar Párrafos\ny Tipo de Discurso",
            command=self.etiquetar_parrafos,
            bg=config.COLOR_BOTON_AZUL,
            **opciones_boton
        )
        self.boton_etiquetar_parrafos.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        # Segunda fila de botones
        self.boton_etiquetar_oraciones = tk.Button(
            marco_botones,
            text="Etiquetar Oraciones",
            command=self.etiquetar_oraciones,
            bg=config.COLOR_BOTON_AZUL,
            **opciones_boton
        )
        self.boton_etiquetar_oraciones.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.boton_conectores = tk.Button(
            marco_botones,
            text="Conectores\nLógico-Temporales",
            command=self.conectores_logico_temporales,
            bg=config.COLOR_BOTON_AZUL,
            **opciones_boton
        )
        self.boton_conectores.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.boton_correferencia = tk.Button(
            marco_botones,
            text="Correferencia\nTextual",
            command=self.correferencia_textual,
            bg=config.COLOR_BOTON_AZUL_CLARO,
            **opciones_boton
        )
        self.boton_correferencia.grid(row=1, column=2, padx=10, pady=10, sticky="ew")

        # Tercera fila de botones
        self.boton_tema_rema = tk.Button(
            marco_botones,
            text="Progresión tematica",
            command=self.tema_rema,
            bg=config.COLOR_BOTON_AZUL_CLARO,
            **opciones_boton
        )
        self.boton_tema_rema.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.boton_ayuda = tk.Button(
            marco_botones,
            text="Ayuda",
            command=self.ayuda,
            bg=config.COLOR_BOTON_AZUL_CLARO,
            **opciones_boton
        )
        self.boton_ayuda.grid(row=2, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

    def ayuda(self):
        """Esta funcion se encarga de mostrar un mensaje de ayuda actualizada"""
        messagebox.showinfo(
            "Ayuda",
            "Este programa permite etiquetar textos en formato XML.\n\n"
            "OPCIONES:\n"
            "• NUEVO PROYECTO: Seleccione un XML para crear un nuevo proyecto (se crea automáticamente el JSON)\n"
            "• ABRIR PROYECTO: Continúe un proyecto existente seleccionando un JSON\n\n"
            "FLUJO DE ETIQUETADO:\n"
            "1. Etiquete los párrafos y tipo de discurso\n"
            "2. Etiquete las oraciones\n"
            "3. Conectores lógico-temporales\n"
            "4. Correferencia textual\n"
            "5. Progresión temática\n\n"
            "Al crear un nuevo proyecto se genera automáticamente:\n"
            "  - [nombre]_etiquetado.json: archivo principal del proyecto\n"
            "  - TODAS las operaciones trabajan con el archivo JSON\n"
        )
    
    def actualizar_campo(self, nombre_campo, valor):
        """Actualiza el contenido de un campo de metadatos de forma segura"""
        if nombre_campo not in self.campos_metadatos:
            return
        campo = self.campos_metadatos[nombre_campo]
        campo.config(state="normal")
        campo.delete(0, tk.END)
        campo.insert(0, valor)
        campo.config(state="disabled")

    def nuevo_proyecto(self):
        """Crea un nuevo proyecto seleccionando un XML y crea automáticamente el JSON"""
        ruta = filedialog.askopenfilename(
            filetypes=[("Archivos XML", "*.xml")]
        )
        if not ruta:
            return

        try:
            # Crear archivo JSON automáticamente usando la nueva función
            ruta_json = self.convert_xml_to_json(ruta)
            
            if ruta_json:
                # Establecer el archivo JSON como proyecto actual (ÚNICA ruta que guardamos)
                self.archivo_json = ruta_json
                
                # Ahora cargar la metadata desde el JSON creado
                self.cargar_metadata_desde_json(ruta_json)
                
                messagebox.showinfo(
                    "Proyecto creado", 
                    f"Proyecto creado exitosamente!\n\n"
                    f"JSON: {os.path.basename(ruta_json)}\n"
                    f"Todas las operaciones usarán este archivo JSON."
                )
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el proyecto: {e}")

    def abrir_proyecto(self):
        """Abre un proyecto existente seleccionando un archivo JSON"""
        ruta = filedialog.askopenfilename(
            filetypes=[("Archivos JSON", "*.json")]
        )
        if not ruta:
            return

        try:
            # Establecer el archivo JSON como proyecto actual (ÚNICA ruta que guardamos)
            self.archivo_json = ruta
            
            # Cargar metadata desde el JSON seleccionado
            self.cargar_metadata_desde_json(ruta)
            
            messagebox.showinfo(
                "Proyecto cargado", 
                f"Proyecto cargado exitosamente!\n\n"
                f"Archivo: {os.path.basename(ruta)}"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el proyecto: {e}")

    def convert_xml_to_json(self, file_path):
        """Convierte un archivo XML a JSON con estructura organizada"""
        if not file_path or not os.path.exists(file_path):
            messagebox.showwarning("Archivo No Válido", "Por favor, seleccione un archivo XML válido.")
            return None

        try:
            # Leer y parsear XML
            with open(file_path, 'r', encoding='utf-8') as xml_file:
                xml_content = xml_file.read()
                json_data = xmltodict.parse(xml_content, encoding='utf-8', process_namespaces=True)
            
            # Extraer metadata del XML
            metadata_completa = self.extraer_metadata_xml(json_data)
            
            # AGREGAR LA METADATA COMPLETA AL JSON
            if 'document' in json_data:
                # Si ya existe metadata en el documento, combinarla con la extraída
                if 'metadata' in json_data['document']:
                    # Combinar metadata existente con la extraída
                    json_data['document']['metadata'].update(metadata_completa)
                else:
                    # Crear nueva metadata
                    json_data['document']['metadata'] = metadata_completa
                
                # AGREGAR ESTRUCTURA DE ETIQUETADO
                json_data['document']['Etiquetado'] = {
                        "parrafos": [],
                        "oraciones": [],
                        "conectores": [],
                        "correferentes": [],
                        "tema_rema": []
                }
            
            # Crear estructura final del JSON
            estructura_json = json_data

            # Guardar JSON con el nombre original + _etiquetado.json
            ruta_base = os.path.splitext(file_path)[0]
            ruta_json = f"{ruta_base}_etiquetado.json"
            
            with open(ruta_json, 'w', encoding='utf-8') as f:
                json.dump(estructura_json, f, ensure_ascii=False, indent=2)
            
            print(f"JSON creado: {ruta_json}")
            return ruta_json
            
        except Exception as e:
            messagebox.showerror("Error de Conversión", f"No se pudo convertir el archivo XML a JSON: {str(e)}")
            return None

    def extraer_metadata_xml(self, datos_xml):
        """Extrae la metadata del XML para incluirla en el JSON - Adaptada a la nueva estructura"""
        try:
            # Obtener metadata desde la estructura document -> metadata
            doc_metadata = datos_xml.get("document", {}).get("metadata", {})
            
            # Si no hay metadata en document, buscar en la raíz
            if not doc_metadata:
                doc_metadata = datos_xml.get("metadata", {})
            
            # Extraer campos principales de manera más directa
            titulo = doc_metadata.get("title", "N/A")
            autor = doc_metadata.get("author", "N/A")
            fecha_publicacion = doc_metadata.get("publication_date", "N/A")
            nombre_publicacion = doc_metadata.get("publication_name", "N/A")
            fuente = doc_metadata.get("source", "N/A")
            fecha_consulta = doc_metadata.get("query_date", "N/A")
            responsable = doc_metadata.get("responsable", "N/A")
            
            # Extraer número del documento
            numero_data = doc_metadata.get("number", {})
            if isinstance(numero_data, dict) and "@id_doc" in numero_data:
                numero = numero_data["@id_doc"]
            else:
                numero = str(numero_data) if numero_data else "N/A"
            
            # Extraer nivel
            nivel = doc_metadata.get("level", "N/A")
            
            # Extraer género textual
            genero_textual = doc_metadata.get("textual_genre", {})
            if isinstance(genero_textual, dict):
                genero_tipo = genero_textual.get("@type", "N/A")
                genero_subtipo = genero_textual.get("@subtype", "N/A")
            else:
                genero_tipo = str(genero_textual)
                genero_subtipo = "N/A"
            
            # Formatear género textual para mostrar
            genero_formateado = f"{genero_tipo}"
            if genero_subtipo != "N/A":
                genero_formateado += f", {genero_subtipo}"
            
            # Extraer país
            pais_data = doc_metadata.get("country", {})
            if isinstance(pais_data, dict):
                pais = pais_data.get("@name", "N/A")
            else:
                pais = str(pais_data) if pais_data else "N/A"

            # Guardar el tipo de texto para uso interno
            self.tipo_texto = genero_tipo

            # Diccionario de superestructuras
            subtipo_dict = {
                "Noticia": "Titular, entrada (resumen breve de la noticia), cuerpo de la noticia (detalles adicionales organizados de lo mas importante a lo menos importante), y conclusion o cierre.",
                "Notas de enciclopedia": "Titulo del articulo, definicion o descripcion inicial, desarrollo del tema (incluye secciones y subsecciones), ejemplos y referencias bibliograficas.",
                "Mini cuento": "Introduccion (planteamiento de la situacion), desarrollo (accion y conflicto), climax (punto culminante de la historia), y desenlace (resolucion del conflicto).",
                "Columna de opinión": "Titulo, introduccion (presentacion del tema y tesis), desarrollo (argumentacion y exposicion de ideas), y conclusion (resumen y cierre).",
                "Reseña": "Titulo, datos bibliograficos (autor, titulo de la obra, etc.), resumen de la obra, analisis critico (opinion and valoracion), y conclusion.",
                "Relato": "Introduccion (contextualizacion del evento), desarrollo (narracion de hechos diarios), y desenlace (conclusion o reflexion final).",
                "Teatro": "Actos y escenas, acotaciones (indicaciones sobre el escenario, acciones y gestos), dialogos de los personajes, y en algunos casos, prologo y epilogo.",
                "Mito": "Introduccion (contexto y personajes), desarrollo (narracion de hechos y eventos sobrenaturales), climax, y desenlace (consecuencias de los eventos).",
                "Biografia": "Introduccion (datos generales del personaje), desarrollo (narracion de eventos importantes en la vida del personaje), y conclusion (logros y legado).",
                "Editorial": "Titulo, introduccion (presentacion del tema), desarrollo (exposicion de argumentos y puntos de vista), y conclusion (resumen y cierre).",
                "Cuento": "Introduccion (planteamiento de la situacion), desarrollo (accion y conflicto), climax (punto culminante de la historia), y desenlace (resolucion del conflicto).",
                "Ensayo": "Titulo, introduccion (presentacion del tema y tesis), desarrollo (argumentacion y analisis), y conclusion (resumen y cierre)."
            }

            superestructura = subtipo_dict.get(genero_subtipo, "No especificada")

            # Retornar metadata completa
            return {
                "titulo": titulo,
                "autor": autor,
                "fecha_publicacion": fecha_publicacion,
                "nombre_publicacion": nombre_publicacion,
                "fuente": fuente,
                "fecha_consulta": fecha_consulta,
                "responsable": responsable,
                "numero_documento": numero,
                "nivel": nivel,
                "genero_textual": genero_formateado,
                "pais": pais,
                "superestructura": superestructura,
                "tipo_texto": genero_tipo,
                "subtipo_texto": genero_subtipo
            }
            
        except Exception as e:
            print(f"Error extrayendo metadata: {e}")
            # Devolver metadata básica en caso de error
            return {
                "titulo": "N/A",
                "autor": "N/A",
                "fecha_publicacion": "N/A",
                "nombre_publicacion": "N/A",
                "fuente": "N/A",
                "fecha_consulta": "N/A",
                "responsable": "N/A",
                "numero_documento": "N/A",
                "nivel": "N/A",
                "genero_textual": "N/A",
                "pais": "N/A",
                "superestructura": "No especificada",
                "tipo_texto": "N/A",
                "subtipo_texto": "N/A"
            }

    def cargar_metadata_desde_json(self, ruta_json):
        """Carga la metadata desde un archivo JSON - Actualizada para nuevos campos"""
        try:
            with open(ruta_json, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            metadata = datos.get("document", {}).get("metadata", {})
            
            # Actualizar campos en la interfaz (solo los que se muestran)
            self.actualizar_campo("titulo", metadata.get("titulo", "N/A"))
            self.actualizar_campo("numero", metadata.get("numero_documento", "N/A"))
            self.actualizar_campo("nivel", metadata.get("nivel", "N/A"))
            self.actualizar_campo("genero_textual", metadata.get("genero_textual", "N/A"))
            self.actualizar_campo("pais", metadata.get("pais", "N/A"))
            
            # Guardar el tipo de texto para uso interno
            self.tipo_texto = metadata.get("tipo_texto", "N/A")
            
            print(f"Metadata cargada desde JSON: {ruta_json}")
            
        except Exception as e:
            raise Exception(f"No se pudo cargar metadata desde JSON: {e}")

    def verificar_proyecto_cargado(self):
        """Verifica si hay un proyecto JSON cargado"""
        if not self.archivo_json:
            messagebox.showwarning("Proyecto no cargado", "Primero seleccione o cree un proyecto.")
            return False
        return True

    def etiquetar_parrafos(self):
        """Abre la ventana de etiquetado de párrafos"""
        if not self.verificar_proyecto_cargado():
            return
        
        nueva_ventana = tk.Toplevel(self.root)
        # Pasar la ruta del JSON en lugar del XML
        app = VentanaEtiquetadoParrafos(nueva_ventana, self.archivo_json, self.tipo_texto)

    def etiquetar_oraciones(self):
        """Abre la ventana de etiquetado de oraciones"""
        if not self.verificar_proyecto_cargado():
            return

        nueva_ventana = tk.Toplevel(self.root)
        # Pasar la ruta del JSON en lugar del XML
        app = VentanaEtiquetadoOraciones(nueva_ventana, self.archivo_json, self.tipo_texto)

    def conectores_logico_temporales(self):
        """Abre la ventana de etiquetado de conectores"""
        if not self.verificar_proyecto_cargado():
            return
            
        nueva_ventana = tk.Toplevel(self.root)
        # Pasar la ruta del JSON en lugar del XML
        app = VentanaEtiquetadoConectores(nueva_ventana, self.archivo_json, self.tipo_texto)
        
    def correferencia_textual(self):
        """Abre la ventana de etiquetado de correferencia"""
        if not self.verificar_proyecto_cargado():
            return
            
        nueva_ventana2 = tk.Toplevel(self.root)
        # Pasar la ruta del JSON en lugar del XML
        ventana = VentanaEtiquetadoCorreferentes(nueva_ventana2, self.archivo_json, self.tipo_texto)

    def tema_rema(self):
        """Abre la ventana de etiquetado de tema-rema"""
        if not self.verificar_proyecto_cargado():
            return
            
        nueva_ventana3 = tk.Toplevel(self.root)
        # Pasar la ruta del JSON en lugar del XML
        ventana = VentanaEtiquetadoTemaRema(nueva_ventana3, self.archivo_json, self.tipo_texto)