import tkinter as tk
from tkinter import filedialog, messagebox
import etiquetado.config as config
import xmltodict
from etiquetado.parrafos import VentanaEtiquetadoParrafos
from etiquetado.oraciones import VentanaEtiquetadoOraciones

class Simultext:
    def __init__(self, root):
        self.root = root
        self.root.title("SIMULTEXT")
        self.root.geometry(f"{config.VENTANA_ANCHO}x{config.VENTANA_ALTO}")
        self.root.configure(bg=config.COLOR_FONDO)
        self.root.minsize(600, 420)

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
        self.boton_seleccionar_xml = tk.Button(
            marco_botones,
            text="Seleccionar XML",
            command=self.seleccionar_xml,
            bg=config.COLOR_BOTON_VERDE,
            **opciones_boton
        )
        self.boton_seleccionar_xml.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.boton_etiquetar_parrafos = tk.Button(
            marco_botones,
            text="Etiquetar Párrafos\ny Tipo de Discurso",
            command=self.etiquetar_parrafos,
            bg=config.COLOR_BOTON_AZUL,
            **opciones_boton
        )
        self.boton_etiquetar_parrafos.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.boton_etiquetar_oraciones = tk.Button(
            marco_botones,
            text="Etiquetar Oraciones",
            command=self.etiquetar_oraciones,
            bg=config.COLOR_BOTON_AZUL,
            **opciones_boton
        )
        self.boton_etiquetar_oraciones.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        # Segunda fila de botones (nuevos botones)
        self.boton_conectores = tk.Button(
            marco_botones,
            text="Conectores\nLógico-Temporales",
            command=self.conectores_logico_temporales,
            bg=config.COLOR_BOTON_AZUL_CLARO,
            **opciones_boton
        )
        self.boton_conectores.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.boton_correferencia = tk.Button(
            marco_botones,
            text="Correferencia\nTextual",
            command=self.correferencia_textual,
            bg=config.COLOR_BOTON_AZUL_CLARO,
            **opciones_boton
        )
        self.boton_correferencia.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.boton_tema_rema = tk.Button(
            marco_botones,
            text="Tema y Rema",
            command=self.tema_rema,
            bg=config.COLOR_BOTON_AZUL_CLARO,
            **opciones_boton
        )
        self.boton_tema_rema.grid(row=1, column=2, padx=10, pady=10, sticky="ew")

        # Tercera fila - Botón de ayuda
        self.boton_ayuda = tk.Button(
            marco_botones,
            text="Ayuda",
            command=self.ayuda,
            bg=config.COLOR_BOTON_AZUL_CLARO,
            **opciones_boton
        )
        self.boton_ayuda.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

    # --------------------
    # Métodos placeholder para nuevos botones
    # --------------------
    def conectores_logico_temporales(self):
        """Placeholder para conectores lógico-temporales"""
        messagebox.showinfo(
            "Conectores Lógico-Temporales",
            "Funcionalidad en desarrollo.\n\n"
            "Aquí se implementará el etiquetado de conectores lógicos y temporales."
        )

    def correferencia_textual(self):
        """Placeholder para correferencia textual"""
        messagebox.showinfo(
            "Correferencia Textual", 
            "Funcionalidad en desarrollo.\n\n"
            "Aquí se implementará el análisis de correferencia textual."
        )

    def tema_rema(self):
        """Placeholder para tema y rema"""
        messagebox.showinfo(
            "Tema y Rema",
            "Funcionalidad en desarrollo.\n\n"
            "Aquí se implementará el análisis de tema y rema."
        )

    def ayuda(self):
        """Esta funcion se encarga de mostrar un mensaje de ayuda"""
        messagebox.showinfo(
            "Ayuda",
            "Este programa permite etiquetar textos en formato XML.\n\n"
            "1. Seleccione un archivo XML.\n"
            "2. Etiquete los párrafos y tipo de discurso\n"
            "3. Etiquete las oraciones\n"
            "4. Conectores lógico-temporales (en desarrollo)\n"
            "5. Correferencia textual (en desarrollo)\n"
            "6. Tema y rema (en desarrollo)\n\n"
            "Al finalizar se generarán archivos JSON con las etiquetas.\n"
            "Con el nombre del archivo original y las extensiones:\n"
            "  - _etiquetas.json: párrafos y discurso\n"
            "  - _oraciones.json: oraciones\n"
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

    def seleccionar_xml(self):
        """Permite seleccionar un archivo XML y mostrar su metadata en la interfaz"""
        ruta = filedialog.askopenfilename(
            filetypes=[("Archivos XML", "*.xml")]
        )
        if not ruta:
            return

        self.archivo_xml = ruta
        print(ruta)
        try:
            with open(self.archivo_xml, "r", encoding="utf-8") as xml_file:
                contenido = xml_file.read()
                datos = xmltodict.parse(contenido)

            doc = datos.get("document", {}).get("metadata", {})
            titulo = doc.get("title", "N/A")
            numero = doc.get("number", {}).get("@id_doc", "N/A")
            nivel = doc.get("level", "N/A")
            genero_tipo = doc.get("textual_genre", {}).get("@type", "N/A")
            genero_subtipo = doc.get("textual_genre", {}).get("@subtype", "N/A")
            pais = doc.get("country", {}).get("@name", "N/A")
            genero = f"{genero_tipo}, {genero_subtipo}"

            # Guardar el tipo de texto
            self.tipo_texto = genero_tipo

            # Usar el metodo auxiliar para actualizar
            self.actualizar_campo("titulo", titulo)
            self.actualizar_campo("numero", numero)
            self.actualizar_campo("nivel", nivel)
            self.actualizar_campo("genero_textual", genero)
            self.actualizar_campo("pais", pais)

            # Diccionario de superestructuras
            subtipo_dict = {
                "Noticia": "Titular, entrada (resumen breve de la noticia), cuerpo de la noticia (detalles adicionales organizados de lo mas importante a lo menos importante), y conclusion o cierre.",
                "Notas de enciclopedia": "Titulo del articulo, definicion o descripcion inicial, desarrollo del tema (incluye secciones y subsecciones), ejemplos y referencias bibliograficas.",
                "Mini cuento": "Introduccion (planteamiento de la situacion), desarrollo (accion y conflicto), climax (punto culminante de la historia), y desenlace (resolucion del conflicto).",
                "Columna de opinion": "Titulo, introduccion (presentacion del tema y tesis), desarrollo (argumentacion y exposicion de ideas), y conclusion (resumen y cierre).",
                "Resena": "Titulo, datos bibliograficos (autor, titulo de la obra, etc.), resumen de la obra, analisis critico (opinion and valoracion), y conclusion.",
                "Relato": "Introduccion (contextualizacion del evento), desarrollo (narracion de hechos diarios), y desenlace (conclusion o reflexion final).",
                "Teatro": "Actos y escenas, acotaciones (indicaciones sobre el escenario, acciones y gestos), dialogos de los personajes, y en algunos casos, prologo y epilogo.",
                "Mito": "Introduccion (contexto y personajes), desarrollo (narracion de hechos y eventos sobrenaturales), climax, y desenlace (consecuencias de los eventos).",
                "Biografia": "Introduccion (datos generales del personaje), desarrollo (narracion de eventos importantes en la vida del personaje), y conclusion (logros y legado).",
                "Editorial": "Titulo, introduccion (presentacion del tema), desarrollo (exposicion de argumentos y puntos de vista), y conclusion (resumen y cierre).",
                "Cuento": "Introduccion (planteamiento de la situacion), desarrollo (accion y conflicto), climax (punto culminante de la historia), y desenlace (resolucion del conflicto).",
                "Ensayo": "Titulo, introduccion (presentacion del tema y tesis), desarrollo (argumentacion y analisis), y conclusion (resumen y cierre)."
            }

            if genero_subtipo in subtipo_dict:
                self.actualizar_campo("superestructura", subtipo_dict[genero_subtipo])

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo extraer metadata: {e}")

    def etiquetar_parrafos(self):
        """Abre la ventana de etiquetado de párrafos"""
        if not hasattr(self, "archivo_xml"):
            messagebox.showwarning("Archivo no seleccionado", "Primero seleccione un archivo XML.")
            return
        
        nueva_ventana = tk.Toplevel(self.root)
        app = VentanaEtiquetadoParrafos(nueva_ventana, self.archivo_xml, self.tipo_texto)

    def etiquetar_oraciones(self):
        """Abre la ventana de etiquetado de oraciones"""
        if not hasattr(self, "archivo_xml"):
            messagebox.showwarning("Archivo no seleccionado", "Primero seleccione un archivo XML.")
            return

        nueva_ventana = tk.Toplevel(self.root)
        app = VentanaEtiquetadoOraciones(nueva_ventana, self.archivo_xml, self.tipo_texto)