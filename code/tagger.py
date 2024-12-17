import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import xml.etree.ElementTree as ET
import xmltodict

import json
import os


class CEMTaggerApp:
    def __init__(self, root):
        """Inicializa la aplicación de etiquetado SIMuLText
        Organigrama de las ventanas
        root
        |-> tagging_window_paragraphs
        |-> tagging_window
        |-> tagging_discurso


        
        """
        self.root = root
        self.root.title("SIMuLText")

        # Crear una etiqueta de bienvenida con el texto adicional
        welcome_title = "SIMuLText"
        welcome_text = ("\n"
+                        "Sistema Informático Multinivel para el etiquetado de corpus a partir de la Lingüística Textual \n")
        self.label_title = tk.Label(root, text=welcome_title, font=("Arial", 24), justify=tk.CENTER)
        self.label_title.pack(pady=10)

        self.label_text = tk.Label(root, text=welcome_text, font=("Arial", 12), justify=tk.LEFT)
        self.label_text.pack(pady=10)

        # Crear un marco para contener los campos de metadata
        metadata_frame = tk.Frame(root)
        metadata_frame.pack(padx=10, pady=10, fill=tk.X)

        # Configurar el grid de la columna para que todos los campos tengan el mismo tamaño
        metadata_frame.columnconfigure(1, weight=1)  # Hacer que la segunda columna expanda

        # Crear campos para mostrar metadata
        self.metadata_fields = {}
        metadata_labels = {
            "Título": "title",
            "ID del Documento": "number",
            "Nivel": "level",
            "Género Textual": "textual_genre",
            "País": "country",
            "Responsable": "responsable"
        }

        for row, (label, field) in enumerate(metadata_labels.items()):
            # Etiqueta
            tk.Label(metadata_frame, text=f"{label}:", font=("Arial", 12)).grid(row=row, column=0, sticky="w", padx=5, pady=2)
            # Campo de entrada
            entry = tk.Entry(metadata_frame, font=("Arial", 12))
            entry.grid(row=row, column=1, padx=5, pady=2, sticky="ew")
            entry.config(state=tk.DISABLED)
            self.metadata_fields[field] = entry

    

        # Crear un marco para contener los botones
        button_frame = tk.Frame(root)
        button_frame.pack(pady=20, padx=10, fill=tk.X)

        # Configurar el grid de columnas para los botones
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        # Crear el botón para seleccionar XML
        self.select_xml_button = tk.Button(button_frame, text="Seleccionar XML", command=self.select_xml, borderwidth=1, relief="raised", width=35, height=2, font=("Arial", 16), bg="#25b060", fg="white")
        self.select_xml_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
   
        # Crear el botón para etiquetar parrafos
        self.tag_sentences_button = tk.Button(button_frame, text="Etiquetado de parrafos \n y tipo de discurso", command=self.tag_paragraphs, borderwidth=1, relief="raised", width=35, height=2, font=("Arial", 16), bg="#20B2AA", fg="white")
        self.tag_sentences_button.grid(row=0, column=1, columnspan=2, padx=10, pady=5, sticky="ew")
    
        # Crear el botón para etiquetar oraciones
        self.tag_sentences_button = tk.Button(button_frame, text="Etiquetado de Oraciones", command=self.tag_sentences, borderwidth=1, relief="raised", width=35, height=2, font=("Arial", 16), bg="#20B2AA", fg="white")
        self.tag_sentences_button.grid(row=1, column=1, columnspan=2, padx=10, pady=5, sticky="ew")

        #Crear botón de ayuda de color azul
        self.btn_ayuda = tk.Button(button_frame, text="Ayuda", command=self.ayuda, borderwidth=1, relief="raised", width=35, height=2, font=("Arial", 16), bg="#B0C4DE", fg="white")
        self.btn_ayuda.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # Crear boton para etiquetar conectores
        self.tag_sentences_button = tk.Button(button_frame, text="Etiquetado de Conectores \n logico-temporales", command=self.tag_connectors, borderwidth=1, relief="raised", width=35, height=2, font=("Arial", 16), bg="#20B2AA", fg="white")
        self.tag_sentences_button.grid(row=2, column=1, columnspan=2, padx=10, pady=5, sticky="ew")

    def tag_connectors(self):
        #Despliega un mensaje de advertencia
        messagebox.showwarning("Advertencia", "Esta función aún no está disponible. \n\n")

    def select_xml(self):
        """Esta función se encarga de abrir un cuadro de diálogo para seleccionar un archivo XML y mostrar su metadata"""
        # Abrir el cuadro de diálogo para seleccionar un archivo XML
        file_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if not file_path:
            return  # El usuario canceló la selección
        # Guardar la ruta del archivo seleccionado para su uso posterior
        self.selected_file_path = file_path

        self.display_metadata()

    def display_metadata(self):
        """Esta función se encarga de extraer la metadata del archivo XML y mostrarla en los campos correspondientes"""
        try:
            with open(self.selected_file_path, 'r', encoding='utf-8') as xml_file:
                xml_content = xml_file.read()
                data_dict = xmltodict.parse(xml_content, encoding='utf-8', process_namespaces=True)
                self.title = data_dict['document']['metadata']['title']
                self.level = data_dict['document']['metadata']['level']
                # Obtener el tipo y subtipo del género textual
                text_type = str(data_dict.get('document', {}).get('metadata', {}).get('textual_genre', {}).get('@type', 'N/A') + ', ' + data_dict.get('document', {}).get('metadata', {}).get('textual_genre', {}).get('@subtype', 'N/A'))
                # Actualizar campos con valores del XML, o 'N/A' si no están presentes
                self.update_metadata_field("title", data_dict['document']['metadata']['title'])  
                self.update_metadata_field("number", data_dict['document']['metadata']['number']["@id_doc"])
                self.update_metadata_field("level", data_dict['document']['metadata']['level'])
                self.update_metadata_field("textual_genre", text_type)
                self.update_metadata_field("Subtipo", data_dict['document']['metadata']['textual_genre']['@subtype'])

                self.update_metadata_field("country", data_dict['document']['metadata']['country']['@name'])
                self.update_metadata_field("responsable", data_dict['document']['metadata']['responsable'])
            
                data = {
                   "Noticia": "Titular, entrada (resumen breve de la noticia), cuerpo de la noticia (detalles adicionales organizados de lo más importante a lo menos importante), y conclusión o cierre.",
                    "Notas de enciclopedia": "Título del artículo, definición o descripción inicial, desarrollo del tema (incluye secciones y subsecciones), ejemplos y referencias bibliográficas.",
                    "Mini cuento": "Introducción (planteamiento de la situación), desarrollo (acción y conflicto), clímax (punto culminante de la historia), y desenlace (resolución del conflicto).",
                    "Columna de opinión": "Título, introducción (presentación del tema y tesis), desarrollo (argumentación y exposición de ideas), y conclusión (resumen y cierre).",
                    "Reseña": "Título, datos bibliográficos (autor, título de la obra, etc.), resumen de la obra, análisis crítico (opinión y valoración), y conclusión.",
                    "Relato": "Introducción (contextualización del evento), desarrollo (narración de hechos diarios), y desenlace (conclusión o reflexión final).",
                    "Teatro":"Actos y escenas, acotaciones (indicaciones sobre el escenario, acciones y gestos), diálogos de los personajes, y en algunos casos, prólogo y epílogo.",
                    "Mito": "Introducción (contexto y personajes), desarrollo (narración de hechos y eventos sobrenaturales), clímax, y desenlace (consecuencias de los eventos).",
                    "Biografía": "Introducción (datos generales del personaje), desarrollo (narración de eventos importantes en la vida del personaje), y conclusión (logros y legado).",
                    "Editorial": "Título, introducción (presentación del tema), desarrollo (exposición de argumentos y puntos de vista), y conclusión (resumen y cierre).",
                    "Cuento": "Introducción (planteamiento de la situación), desarrollo (acción y conflicto), clímax (punto culminante de la historia), y desenlace (resolución del conflicto)."
                    }
                subtipo = data_dict['document']['metadata']['textual_genre']['@subtype']
                self.update_metadata_field("superestructura", data[subtipo])
        except Exception as e:
            messagebox.showerror("Error al Extraer Metadata", f"No se pudo extraer la metadata del archivo XML: {str(e)}")


    def update_metadata_field(self, field, value):
        entry = self.metadata_fields.get(field)
        if entry:
            entry.config(state=tk.NORMAL)
            entry.delete(0, tk.END)
            entry.insert(0, value)
            entry.config(state=tk.DISABLED)


    def convert_xml_to_json(self,file_path):
        if not hasattr(self, 'selected_file_path') or not self.selected_file_path:
            messagebox.showwarning("Archivo No Seleccionado", "Por favor, seleccione un archivo XML.")
            return

        # Intentar convertir XML a JSON
        try:
            with open(file_path, 'r', encoding='utf-8') as xml_file:
                xml_content = xml_file.read()
                json_data = xmltodict.parse(xml_content, encoding='utf-8', process_namespaces=True)
        except Exception as e:
            messagebox.showerror("Error de Conversión", f"No se pudo convertir el archivo XML a JSON: {str(e)}")
            return

        # Pedir al usuario que ingrese el nombre del archivo para guardar
        filename = "converter_xml.json"

        # Ruta de destino es la carpeta del archivo XML a la misma direccion de self.selected_file_path
        save_path = os.path.dirname(self.selected_file_path)
        if not save_path:
            return  # El usuario canceló la selección de la carpeta

        # Combinar la ruta y el nombre del archivo
        full_path = os.path.join(save_path, filename)

        try:
            with open(full_path, 'w', encoding='utf-8') as json_file:
                json.dump(json_data, json_file, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Error al Guardar", f"No se pudo guardar el archivo JSON: {str(e)}")
            return
   

    def ayuda(self):
        """Esta función se encarga de mostrar un mensaje de ayuda"""
        messagebox.showinfo("Ayuda", "Este programa permite etiquetar textos en formato XML. \n\n"
                                     "1. Seleccione un archivo XML. \n"
                                     "2. Etiquete los parrafos \n"
                                        "3. Etiquete el tipo de discurso \n"
                                        "4. Etiquete las oraciones \n\n"
                                        "Al finalizar se generará un archivo JSON con las etiquetas. \n"
                                        "Con el nombre del archivo original y las extensiones: \n"
                                        "par: para los párrafos y discurso\n"
                                        "orac: para las oraciones \n")




    def tag_paragraphs(self):
        """Esta función se encarga de etiquetar los párrafos del texto"""

        if not hasattr(self, 'selected_file_path') or not self.selected_file_path:
            messagebox.showwarning("Archivo No Seleccionado", "Por favor, seleccione un archivo XML antes de etiquetar.")
            return


        #Si existe el archivo "pivot.json" se elimina
        if os.path.exists("pivot.json"):
            os.remove("pivot.json")
        
        # Algoritmo para enumerar los párrafos del xml añadiendo un id
        tree = ET.parse(self.selected_file_path)
        root = tree.getroot()
        id = 1

        for paragraph in root.findall('paragraph'):
            paragraph.set('id', "p"+str(id))
            id += 1

        #Se crea un archivo xml con los párrafos enumerados
        tree.write('paragraphs.xml')

        #Se crea la ventana de etiquetado de párrafos
        self.tagging_window_paragraphs = tk.Toplevel(self.root)
        self.tagging_window_paragraphs.title("Etiquetado de Parrafos")

        # Se cuentan cuantos parrafos hay en el archivo
        num_parrafos = 0
        for paragraph in root.findall('paragraph'):
            num_parrafos += 1

        # Se pone la metadata en la ventana de etiquetado
        metadata_frame = tk.Frame(self.tagging_window_paragraphs)
        metadata_frame.pack(pady=8, padx=21, fill=tk.X)

        # Configurar el grid de la columna para que todos los campos tengan el mismo tamaño
        metadata_frame.columnconfigure(1, weight=1)  # Hacer que la segunda columna expanda

        # Crear campos para mostrar metadata
        self.metadata_fields = {}
        metadata_labels = {
            "Título": "title",
            "ID del Documento": "number",
            "Nivel": "level",
            "Género Textual": "textual_genre",
            "País": "country",
            "Responsable": "responsable",
            "Superestructura": "superestructura"  
        }

        for row, (label, field) in enumerate(metadata_labels.items()):
            # Etiqueta
            tk.Label(metadata_frame, text=f"{label}:", font=("Arial", 8)).grid(row=row, column=0, sticky="w", padx=5, pady=2)
            # Campo de entrada
            entry = tk.Entry(metadata_frame, font=("Arial", 8))
            entry.grid(row=row, column=1, padx=5, pady=1, sticky="ew")
            entry.config(state=tk.DISABLED)
            self.metadata_fields[field] = entry

        self.display_metadata()

        # Crear un marco principal para organizar los elementos
        main_frame = tk.Frame(self.tagging_window_paragraphs)
        main_frame.pack(fill="both", expand=True)

        # Configurar main_frame para permitir la expansión de filas y columnas
        main_frame.grid_columnconfigure(0, weight=2)

        # Crear un marco para los botones de párrafos
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Extraer los párrafos
        paragraphs = self.extraer_parrafos('paragraphs.xml')

        # Crear un canvas para contener los botones
        canvas = tk.Canvas(button_frame)
        scrollbar_y = tk.Scrollbar(button_frame, orient="vertical", command=canvas.yview)
        scrollbar_x = tk.Scrollbar(button_frame, orient="horizontal", command=canvas.xview)

        self.scrollable_frame = tk.Frame(canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.config(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")

        #lista para almacenar los identificadores de los parrafos
        self.identificadores = []

        #Agregar un campo de texto para mostrar los identificadores de los parrafos etiquetados
        self.text_identificadores = tk.Text(main_frame, height=5, width=50, font=("Arial", 12))
        self.text_identificadores.grid(row=1, column=0, padx=5, pady=2, sticky="ew")

        #boton terminar
        self.btn_terminar = tk.Button(self.tagging_window_paragraphs, text="Guardar", command=self.teminar_parrafos, borderwidth=1, relief="raised", width=35, height=2, font=("Arial", 16), bg="#25b060", fg="white")
        self.btn_terminar.pack(pady=2, padx=2)



        for paragraph in paragraphs:
            # Crear un botón dentro del frame scrollable
            self.botones_parrafo = tk.Button(self.scrollable_frame, text=paragraph, anchor="w", command=lambda text=paragraph: self.procesar_parrafo(text),bg ="#B0E0E6")
            self.botones_parrafo.pack(fill="both", expand=True)

        return 1
    
    def procesar_parrafo(self, parrafo):
        """Esta función se encarga de procesar el párrafo seleccionado y abrir la ventana de etiquetado de párrafos"""
        # Extraer el identificador del párrafo
        self.identificador = parrafo.split(")")[0].replace("(id= p","")
        self.identificador = self.identificador.split(")")[0].replace("(","")
        self.identificador=self.identificador.replace("id=","")



        # Crear la ventana de etiquetado de párrafos
        self.tagging_window = tk.Toplevel(self.root)
        self.tagging_window.title("Etiquetado de Parrafos")

        # Configurar la ventana para adaptarse al contenido
        self.tagging_window.columnconfigure(0, weight=1)
        self.tagging_window.columnconfigure(1, weight=1)
        self.tagging_window.rowconfigure([0, 1, 2, 3,4,5,6,7,8,9,10,11], weight=1)


        # Crear los títulos
        tk.Label(self.tagging_window, text="Atributos Narrativo", font=("Arial", 14)).grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        tk.Label(self.tagging_window, text="Atributos Argumentativo", font=("Arial", 14)).grid(row=0, column=1, sticky="ew", padx=10, pady=10)

        # Atributos Narrativo

        # Boton "Introducción". Al pulsarlo agrega introduccion al cuadro de texto
        self.btn_introduccion = tk.Button(self.tagging_window, text="Introducción - (N_Intro)", command= lambda: self.text_atributos.insert(tk.END, "N_Intro, "), borderwidth=1, relief="raised", width=25, height=1, font=("Arial", 16), bg="#2271b3", fg="white")
        self.btn_introduccion.grid(row=2, column=0, padx=10, pady=0, sticky="ew")

        #Boton "Desarrollo". Al pulsarlo agrega desarrollo al cuadro de texto
        self.btn_desarrollo = tk.Button(self.tagging_window, text="Desarrollo (N_Dllo)", command= lambda: self.text_atributos.insert(tk.END, "N_Dllo, "), borderwidth=1, relief="raised", width=25, height=1, font=("Arial", 16), bg="#2271b3", fg="white")
        self.btn_desarrollo.grid(row=3, column=0, padx=10, pady=0, sticky="ew")

        # Boton "Climax". Al pulsarlo agrega climax al cuadro de texto
        self.btn_climax = tk.Button(self.tagging_window, text="Climax - (N_Clim)", command= lambda: self.text_atributos.insert(tk.END, "N_Clim, "), borderwidth=1, relief="raised", width=25, height=1, font=("Arial", 16), bg="#2271b3", fg="white")
        self.btn_climax.grid(row=4, column=0, padx=10, pady=0, sticky="ew")

        # Boton "Desenlace". Al pulsarlo agrega desenlace al cuadro de texto
        self.btn_desenlace = tk.Button(self.tagging_window, text="Desenlace - (N_Des)", command= lambda: self.text_atributos.insert(tk.END, "N_Des, "), borderwidth=1, relief="raised", width=25, height=1, font=("Arial", 16), bg="#2271b3", fg="white")
        self.btn_desenlace.grid(row=5, column=0, padx=10, pady=0, sticky="ew")

        # Boton "Título". Al pulsarlo agrega título al cuadro de texto
        self.btn_titulo = tk.Button(self.tagging_window, text="Título - (N_Tit)", command= lambda: self.text_atributos.insert(tk.END, "N_Tit, "), borderwidth=1, relief="raised", width=25, height=1, font=("Arial", 16), bg="#2271b3", fg="white")
        self.btn_titulo.grid(row=6, column=0, padx=10, pady=0, sticky="ew")

        # Boton "Subtítulo". Al pulsarlo agrega subtítulo al cuadro de texto
        self.btn_subtitulo = tk.Button(self.tagging_window, text="Subtítulo - (N_Subt)", command= lambda: self.text_atributos.insert(tk.END, "N_Subt, "), borderwidth=1, relief="raised", width=25, height=1, font=("Arial", 16), bg="#2271b3", fg="white")
        self.btn_subtitulo.grid(row=7, column=0, padx=10, pady=0, sticky="ew")

        # Boton "Datos Autor". Al pulsarlo agrega datos_autor al cuadro de texto
        self.btn_datos_autor = tk.Button(self.tagging_window, text="Datos Autor - (N_DA)", command= lambda: self.text_atributos.insert(tk.END, "N_DA, "), borderwidth=1, relief="raised", width=25, height=1, font=("Arial", 16), bg="#2271b3", fg="white")
        self.btn_datos_autor.grid(row=8, column=0, padx=10, pady=0, sticky="ew")

        # Atributos Argumentativo

        #Boton "Introduccion o situacion inicial". Al pulsarlo agrega introduccion al cuadro de texto
        self.btn_introduccion_arg = tk.Button(self.tagging_window, text="Introducción - (A_Intro)", command= lambda: self.text_atributos.insert(tk.END, "A_Intro, "), borderwidth=1, relief="raised", width=25, height=1, font=("Arial", 16), bg="#6aa9d6", fg="white")
        self.btn_introduccion_arg.grid(row=2, column=1, padx=10, pady=0, sticky="ew")

        #Boton "Desarrollo o argumentos". Al pulsarlo agrega desarrollo al cuadro de texto
        self.btn_desarrollo_arg = tk.Button(self.tagging_window, text="Desarrollo - (A_Dllo)", command= lambda: self.text_atributos.insert(tk.END, "A_Dllo, "), borderwidth=1, relief="raised", width=25, height=1, font=("Arial", 16), bg="#6aa9d6", fg="white")
        self.btn_desarrollo_arg.grid(row=3, column=1, padx=10, pady=0, sticky="ew")

        # Boton "Conclusión". Al pulsarlo agrega climax al cuadro de texto
        self.btn_conclusion_arg = tk.Button(self.tagging_window, text="Conclusión - (A_Con)", command= lambda: self.text_atributos.insert(tk.END, "A_Con, "), borderwidth=1, relief="raised", width=25, height=1, font=("Arial", 16), bg="#6aa9d6", fg="white")
        self.btn_conclusion_arg.grid(row=4, column=1, padx=10, pady=0, sticky="ew")

        # Boton "Datos bibliograficos". Al pulsarlo agrega datos_bibliograficos al cuadro de texto
        self.btn_datos_bibliograficos = tk.Button(self.tagging_window, text="Datos bibliográficos - (A_DB)", command= lambda: self.text_atributos.insert(tk.END, "A_DB, "), borderwidth=1, relief="raised", width=25, height=1, font=("Arial", 16), bg="#6aa9d6", fg="white")
        self.btn_datos_bibliograficos.grid(row=5, column=1, padx=10, pady=0, sticky="ew")

        # Boton "Titulo". Al pulsarlo agrega titulo al cuadro de texto
        self.btn_titulo_arg = tk.Button(self.tagging_window, text="Título - (A_Tit)", command= lambda: self.text_atributos.insert(tk.END, "A_Tit, "), borderwidth=1, relief="raised", width=25, height=1, font=("Arial", 16), bg="#6aa9d6", fg="white")
        self.btn_titulo_arg.grid(row=6, column=1, padx=10, pady=0, sticky="ew")

        # Boton "Subtitulo". Al pulsarlo agrega subtitulo al cuadro de texto
        self.btn_subtitulo_arg = tk.Button(self.tagging_window, text="Subtítulo - (A_Subt)", command= lambda: self.text_atributos.insert(tk.END, "A_Subt, "), borderwidth=1, relief="raised", width=25, height=1, font=("Arial", 16), bg="#6aa9d6", fg="white")
        self.btn_subtitulo_arg.grid(row=7, column=1, padx=10, pady=0, sticky="ew")

        # Boton "Datos autor". Al pulsarlo agrega datos_autor al cuadro de texto
        self.btn_datos_autor_arg = tk.Button(self.tagging_window, text="Datos Autor - (A_DA)", command= lambda: self.text_atributos.insert(tk.END, "A_DA, "), borderwidth=1, relief="raised", width=25, height=1, font=("Arial", 16), bg="#6aa9d6", fg="white")
        self.btn_datos_autor_arg.grid(row=8, column=1, padx=10, pady=0, sticky="ew")

        # Boton "Referencia". Al pulsarlo agrega referencia al cuadro de texto
        self.btn_referencia_arg = tk.Button(self.tagging_window, text="Referencia - (A_Ref)", command= lambda: self.text_atributos.insert(tk.END, "A_Ref, "), borderwidth=1, relief="raised", width=25, height=1, font=("Arial", 16), bg="#6aa9d6", fg="white")
        self.btn_referencia_arg.grid(row=9, column=1, padx=10, pady=0, sticky="ew")

        #Cuadro de texto para visualizar los atributos asignados al parrafo. Se expande en todo el ancho
        self.text_atributos = tk.Text(self.tagging_window, height=6, width=50, font=("Arial", 12))
        self.text_atributos.grid(row=10, columnspan=2, padx=5, pady=5, sticky="ew")
        
        #Escribir el parrafo en el cuadro de texto y dejar un espacio en blanco
        self.text_atributos.insert(tk.END, parrafo + "\n\n")

        # Botón de Guardar
        self.btn_guardar = tk.Button(self.tagging_window, text="Guardar", command=self.guardar_etiquetas_parrafo, borderwidth=1, relief="raised", width=35, height=2, font=("Arial", 16), bg="#25b060", fg="white")
        self.btn_guardar.grid(row=11, column=0, pady=10)

        # Botón de Cancelar
        self.btn_cancelar = tk.Button(self.tagging_window, text="Cancelar", command=self.tagging_window.destroy, borderwidth=1, relief="raised", width=35, height=2, font=("Arial", 16), bg="#B0C4DE", fg="white")
        self.btn_cancelar.grid(row=11, column=1, pady=10)

        return 1
    



    def guardar_etiquetas_parrafo(self):
        """Esta función se encarga de guardar las etiquetas asignadas al párrafo en el archivo JSON"""
        # Extraer el texto del cuadro de texto
        etiquetas = self.text_atributos.get("1.0", tk.END)
        etiquetas = etiquetas.split("\n\n")[1] # Extraer solo las etiquetas
        etiquetas = etiquetas.split(", ") # Separar las etiquetas por coma
        etiquetas = [x for x in etiquetas if x != "\n"]

        #Abrir archivo json para agregar las etiquetas
        name = "pivot.json"

        #Crear archivo json "pivot.json" si no existe
        if not os.path.exists(name):
            with open(name, "w") as outfile:
                json.dump({"Super_Estructura": {}}, outfile, indent=4)
        
        #Abrir archivo json para agregar las etiquetas
        with open(name, "r") as read_file:
            data = json.load(read_file)
            data["Super_Estructura"][self.identificador] = etiquetas
            with open(name, "w") as write_file:
                json.dump(data, write_file, indent=4)
        
        #Agregar el identificador al cuadro de texto
        self.identificadores.append(self.identificador)

                #Añadir el identificador al cuadro de texto
        self.text_identificadores.insert(tk.END, self.identificador + ", ")

        #Cerrar la ventana de etiquetado de parrafos
        self.tagging_window.destroy()       
        return 1
    


    
    def teminar_parrafos(self):
        """Esta función se encarga de guardar el tipo de discurso seleccionado en el archivo JSON"""
        #Cerrar la ventana de etiquetado de parrafos
        self.tagging_window_paragraphs.destroy()

        #Convertir "paragraphs.xml" a json
        self.convert_xml_to_json("paragraphs.xml")


        #Se etiqueta el tipo de discurso
        self.etiquetar_discurso()

        return 1
    


    
    def etiquetar_discurso(self):
        """Esta función se encarga de etiquetar el tipo de discurso del texto"""

        # Crea una ventana nueva self.tagging_discurso para etiquetar el tipo de discurso
        self.tagging_discurso = tk.Toplevel(self.root)
        self.tagging_discurso.title("Etiquetado de Discurso")

        # Pone un título: "Seleccione el tipo de discurso"
        tk.Label(self.tagging_discurso, text="Seleccione el tipo de discurso", font=("Arial", 14)).pack(pady=10)

        # Crea un frame para organizar los botones en dos columnas
        button_frame = tk.Frame(self.tagging_discurso)
        button_frame.pack(pady=10)

        # Se crean los botones con los tipos de discurso y se organizan en dos columnas

        # Primera columna
        self.btn_politico = tk.Button(button_frame, text="Político - (D_Pol)", command= lambda: self.text_identificadores_discurso.insert(tk.END, "D_Pol, "), borderwidth=1, relief="raised", width=25, height=1, font=("Arial", 16), bg="#92c5fc", fg="white")
        self.btn_politico.grid(row=0, column=0, padx=5, pady=5)

        self.btn_religioso = tk.Button(button_frame, text="Religioso - (D_Rel)", command= lambda: self.text_identificadores_discurso.insert(tk.END, "D_Rel, "), borderwidth=1, relief="raised", width=25, height=1, font=("Arial", 16), bg="#92c5fc", fg="white")
        self.btn_religioso.grid(row=1, column=0, padx=5, pady=5)

        self.btn_didactico = tk.Button(button_frame, text="Didáctico - (D_Did)", command= lambda: self.text_identificadores_discurso.insert(tk.END, "D_Did, "), borderwidth=1, relief="raised", width=25, height=1, font=("Arial", 16), bg="#92c5fc", fg="white")
        self.btn_didactico.grid(row=2, column=0, padx=5, pady=5)

        self.btn_periodistico = tk.Button(button_frame, text="Periodístico - (D_Per)", command= lambda: self.text_identificadores_discurso.insert(tk.END, "D_Per, "), borderwidth=1, relief="raised", width=25, height=1, font=("Arial", 16), bg="#92c5fc", fg="white")
        self.btn_periodistico.grid(row=3, column=0, padx=5, pady=5)

        self.btn_literario = tk.Button(button_frame, text="Literario - (D_Lit)", command= lambda: self.text_identificadores_discurso.insert(tk.END, "D_Lit, "), borderwidth=1, relief="raised", width=25, height=1, font=("Arial", 16), bg="#92c5fc", fg="white")
        self.btn_literario.grid(row=4, column=0, padx=5, pady=5)

        # Segunda columna
        self.btn_juridico = tk.Button(button_frame, text="Jurídico - (D_Jur)", command= lambda: self.text_identificadores_discurso.insert(tk.END, "D_Jur, "), borderwidth=1, relief="raised", width=25, height=1, font=("Arial", 16), bg="#92c5fc", fg="white")
        self.btn_juridico.grid(row=0, column=1, padx=5, pady=5)

        self.btn_comercial = tk.Button(button_frame, text="Comercial \n o Publicitario - (D_CP)", command= lambda: self.text_identificadores_discurso.insert(tk.END, "D_CP, "), borderwidth=1, relief="raised", width=25, height=2, font=("Arial", 16), bg="#92c5fc", fg="white")
        self.btn_comercial.grid(row=1, column=1, padx=5, pady=5)

        self.btn_social = tk.Button(button_frame, text="Social - (D_Soc)", command= lambda: self.text_identificadores_discurso.insert(tk.END, "D_Soc, "), borderwidth=1, relief="raised", width=25, height=1, font=("Arial", 16), bg="#92c5fc", fg="white")
        self.btn_social.grid(row=2, column=1, padx=5, pady=5)

        self.btn_cientifico = tk.Button(button_frame, text="Científico - (D_Cien)", command= lambda: self.text_identificadores_discurso.insert(tk.END, "D_Cien, "), borderwidth=1, relief="raised", width=25, height=1, font=("Arial", 16), bg="#92c5fc", fg="white")
        self.btn_cientifico.grid(row=3, column=1, padx=5, pady=5)

        self.btn_academico = tk.Button(button_frame, text="Académico - (D_Acad)", command= lambda: self.text_identificadores_discurso.insert(tk.END, "D_Acad, "), borderwidth=1, relief="raised", width=25, height=1, font=("Arial", 16), bg="#92c5fc", fg="white")
        self.btn_academico.grid(row=4, column=1, padx=5, pady=5)

        # Se crea un campo de texto para mostrar los identificadores de los tipos de discursos seleccionados
        self.text_identificadores_discurso = tk.Text(self.tagging_discurso, height=3, width=50, font=("Arial", 12))
        self.text_identificadores_discurso.pack(pady=10)

        # Botones de Guardar y Cancelar
        self.btn_guardar_discurso = tk.Button(self.tagging_discurso, text="Guardar", command=self.guardar_discurso, borderwidth=1, relief="raised", width=35, height=2, font=("Arial", 16), bg="#25b060", fg="white")
        self.btn_guardar_discurso.pack(pady=5)

        self.btn_cancelar_discurso = tk.Button(self.tagging_discurso, text="Cancelar", command=self.tagging_discurso.destroy, borderwidth=1, relief="raised", width=35, height=2, font=("Arial", 16), bg="#B0C4DE", fg="white")
        self.btn_cancelar_discurso.pack(pady=5)

        return 1

        
    def guardar_discurso(self): 
        """Esta función se encarga de guardar el tipo de discurso seleccionado en el archivo JSON"""
  
        #Se extrae la información del campo de texto como una lista
        discurso = self.text_identificadores_discurso.get("1.0", tk.END)
        discurso = discurso.split(", ")

        #Se eliminan los saltos de linea
        discurso = [x for x in discurso if x != "\n"]
        self.tipo_discurso = discurso

        #Agregar "pivot.json" al final de "converter_xml.json"
        name = "converter_xml.json"
        etiquetado = "pivot.json"

        #pegar etiquetado al final de name
        with open(name, "r") as read_file:
            data = json.load(read_file)
            with open(etiquetado, "r") as read_file:
                data_etiquetado = json.load(read_file)
                data["Super_Estructura"] = data_etiquetado["Super_Estructura"]
                with open(name, "w") as write_file:
                    json.dump(data, write_file, indent=4)
        
        if self.tipo_discurso != 0:
            #Agregar el tipo de texto en la document/metadata del json
            with open(name, "r") as read_file:
                data = json.load(read_file)
                data["document"]["metadata"]["tipo_discurso"] = self.tipo_discurso
                with open(name, "w") as write_file:
                    json.dump(data, write_file, indent=4)
   

        #Guardar el json en un archivo con el nombre del archivo xml original sin la extensión y con "_par.json"
        name = self.selected_file_path.split(".")[0] + "_par.json"
        with open(name, "w") as write_file:
            json.dump(data, write_file, indent=4)

        #Eliminar "pivot.json"
        os.remove("pivot.json")

        #Eliminar "paragraphs.xml"
        os.remove("paragraphs.xml")

        #Se cierra la ventana de etiquetado de discurso
        self.tagging_discurso.destroy()
        

        #avisar que se ha terminado de etiquetar los parrafos
        messagebox.showinfo("Terminado", "Se ha terminado de etiquetar los parrafos y discurso")
        return 1

        
    def extraer_parrafos(self,ruta_archivo):
        # Extraer los párrafos del archivo XML
        tree = ET.parse(ruta_archivo)
        root = tree.getroot()
        parrafos = []

        for paragraph in root.findall('.//paragraph'):
            parrafo_texto = []
            for token in paragraph.findall('.//token'):
                palabra = token.get('form')
                parrafo_texto.append(palabra)
            
            id = paragraph.get('id')
            parrafo = "(id="+id + ") - " + ' '.join(parrafo_texto) # Unir las palabras en una sola cadena
            parrafos.append(parrafo)
        
        return parrafos


    def tag_sentences(self):
        """Esta función se encarga de etiquetar las oraciones del texto"""
        if not hasattr(self, 'selected_file_path') or not self.selected_file_path:
            messagebox.showwarning("Archivo No Seleccionado", "Por favor, seleccione un archivo XML antes de etiquetar.")
            return

        with open("oraciones.json", "w") as outfile:
            json.dump({"oraciones": {"ind_simple":{},"ind_coordinada" :{},"dep_subordinada":{}, "dep_subordinada":{},"ind_yuxtaposicion":{}}}, outfile, indent=4)

        # Crear la ventana de etiquetado de oraciones
        self.tagging_window_sentences = tk.Toplevel(self.root)
        self.tagging_window_sentences.title("Etiquetado de Oraciones simples y compuestas")

        # Maximizar la ventana de etiquetado al inicio
        # self.tagging_window_sentences.attributes('-zoomed', True)

        # Crear un marco para los campos de metadata
        metadata_frame = tk.Frame(self.tagging_window_sentences)
        metadata_frame.pack(pady=8, padx=21, fill=tk.X)

        # Configurar el grid de la columna para que todos los campos tengan el mismo tamaño
        metadata_frame.columnconfigure(1, weight=1)  # Hacer que la segunda columna expanda

        # Crear campos para mostrar metadata
        self.metadata_fields = {}
        metadata_labels = {
            "Título": "title",
            "ID del Documento": "number",
            "Nivel": "level",
            "Género Textual": "textual_genre",
            "País": "country",
            "Responsable": "responsable",
            "Superestructura": "superestructura"  
        }

        for row, (label, field) in enumerate(metadata_labels.items()):
            # Etiqueta
            tk.Label(metadata_frame, text=f"{label}:", font=("Arial", 8)).grid(row=row, column=0, sticky="w", padx=5, pady=2)
            # Campo de entrada
            entry = tk.Entry(metadata_frame, font=("Arial", 8))
            entry.grid(row=row, column=1, padx=5, pady=1, sticky="ew")
            entry.config(state=tk.DISABLED)
            self.metadata_fields[field] = entry


        self.display_metadata()


        # Crear un marco principal para organizar los elementos
        main_frame = tk.Frame(self.tagging_window_sentences)
        main_frame.pack(fill="both", expand=True)
    
        # Configurar main_frame para permitir la expansión de filas y columnas
        main_frame.grid_columnconfigure(0, weight=2)  # Permitir que la primera columna se expanda

        # Crear un marco para los botones de oraciones
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=0, column=0,padx = 10,pady=10, sticky="ew")


        # Extraer las oraciones y mostrarlas en el cuadro de texto
        oraciones = self.extraer_oraciones(self.selected_file_path)

        # Crear un canvas para contener los botones
        canvas = tk.Canvas(button_frame)
        scrollbar_y = tk.Scrollbar(button_frame, orient="vertical", command=canvas.yview)
        scrollbar_x = tk.Scrollbar(button_frame, orient="horizontal", command=canvas.xview)

        self.scrollable_frame = tk.Frame(canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))) 

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.config(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set) 

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")

        #lista para almacenar los identificadores de las oraciones
        self.identificadores = []

        #Agregar un campo de texto para mostrar los identificadores de las oraciones etiquetadas
        self.text_identificadores = tk.Text(main_frame, height=4, width=50, font=("Arial", 12))
        self.text_identificadores.grid(row=1, column=0, padx=5, pady=5, sticky="ew")



        #boton terminar 
        self.btn_terminar = tk.Button(self.tagging_window_sentences, text="Guardar", command=self.terminar, borderwidth=1, relief="raised", width=35, height=2, font=("Arial", 16), bg="#25b060", fg="white")
        self.btn_terminar.pack(pady=5)



        for oracion in oraciones:
            # Crear un botón dentro del frame scrollable
            self.botones_oracion = tk.Button(self.scrollable_frame, text=oracion,anchor="w", command=lambda text=oracion: self.procesar_oracion(text), bg = "#B0E0E6")
            self.botones_oracion.pack(fill="both", expand=True)



    def terminar(self):
        """Esta función se encarga de guardar las etiquetas de las oraciones en un archivo json y cerrar la ventana de etiquetado de oraciones"""

        #Se abre el archivo json convertido para agregar las etiquetas
        name = str(self.selected_file_path.split(".")[0] + "_par.json")
        etiquetado = "oraciones.json"

        #pegar etiquetado al final de name
        with open(name, "r") as read_file:
            data = json.load(read_file)
            with open(etiquetado, "r") as read_file:
                data_etiquetado = json.load(read_file)
                data["oraciones"] = data_etiquetado["oraciones"]
                with open(name, "w") as write_file:
                    json.dump(data, write_file, indent=4)

        #Guardar el json en un archivo con el nombre del archivo del name original sin la extensión y con "_orac.json"
        name = name.split(".")[0] + "_orac.json"
        with open(name, "w") as write_file:
            json.dump(data, write_file, indent=4)

        #Eliminar "oraciones.json"
        os.remove("oraciones.json")

        #Cerrar la ventana de etiquetado de oraciones
        self.tagging_window_sentences.destroy()

        #avisar que se ha terminado de etiquetar las oraciones
        messagebox.showinfo("Terminado", "Se ha terminado de etiquetar las oraciones")

        return 1

 

    def extraer_oraciones(self,ruta_archivo):
        # Extraer las oraciones del archivo XML
        tree = ET.parse(ruta_archivo)
        root = tree.getroot()
        oraciones = []

        for paragraph in root.findall('paragraph'):
            for sentence in paragraph.findall('sentence'):
                # Crear una lista de palabras para cada oración
                palabras = []
                for token in sentence.findall('token'):
                    forma = token.get('form')
                    palabras.append(forma)
                id = sentence.get('id')
                oracion = "(id="+id + ") - " + ' '.join(palabras) # Unir las palabras en una sola cadena
                oraciones.append(oracion)

        return oraciones

    
    def procesar_oracion(self, oracion):
        # Extraer el identificador de la oración
        self.identificador = oracion.split(")")[0].replace("(id=","")

        # Se guarda la oración
        self.oracion = oracion

        # Crear la ventana de etiquetado de oraciones
        self.tagging_window = tk.Toplevel(self.root)
        self.tagging_window.title("Tipo de independencia de las oraciones")

        #Pone un título: "Seleccione el tipo de independencia de las oraciones"
        tk.Label(self.tagging_window, text="Seleccione el tipo de independencia de las oraciones", font=("Arial", 14)).pack(pady=10)

        # Crear un marco para organizar los botones en tres columnas
        button_frame = tk.Frame(self.tagging_window)

        #Crear un espacio de texto para poner la oracion
        self.text_oracion = tk.Text(self.tagging_window, height=7, width=70, font=("Arial", 12))
        self.text_oracion.pack(pady=10)

        #Escribir la oracion en el cuadro de texto
        self.text_oracion.insert(tk.END, oracion)

        # se organizan los botones en tres columnas
        button_frame.pack(pady=20)


        # Se crean los botones con los tipos de independencia de las oraciones y se organizan en tres filas

        #Boton de independencia simple
        self.btn_independencia_simple = tk.Button(button_frame, text="Independencia \n Simple - (O_Simp)", command=self.oraciones_independencia_simple, borderwidth=1, relief="raised", width=25, height=2, font=("Arial", 16), bg="#20B2AA", fg="white")
        self.btn_independencia_simple.grid(row=0, column=0, padx=10, pady=5, sticky="ew")


        #Boton de independencia coordinada
        self.btn_independencia_coordinada = tk.Button(button_frame, text="Independencia \n Coordinada - (O_Coord)", command=self.oraciones_independencia_coordinada, borderwidth=1, relief="raised", width=25, height=2, font=("Arial", 16), bg="#20B2AA", fg="white")
        self.btn_independencia_coordinada.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        #Boton de independencia por yuxtaposición
        self.btn_independencia_yuxtaposicion = tk.Button(button_frame, text="Independencia por \n Yuxtaposición - (O_Yuxt)", command=self.oraciones_independencia_yuxtaposicion, borderwidth=1, relief="raised", width=25, height=2, font=("Arial", 16), bg="#20B2AA", fg="white")
        self.btn_independencia_yuxtaposicion.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # Boton de Dependencia Subordinada
        self.btn_dependencia_subordinada = tk.Button(button_frame, text="Dependencia \n Subordinada - (O_Sub)", command=self.oraciones_dependencia_subordinada, borderwidth=1, relief="raised", width=25, height=2, font=("Arial", 16), bg="#20B2AA", fg="white")
        self.btn_dependencia_subordinada.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        # Boton de cancelar en en color gris
        self.btn_cancelar = tk.Button(self.tagging_window, text="Cancelar", command=self.tagging_window.destroy, borderwidth=1, relief="raised", width=35, height=3, font=("Arial", 16), bg="#B0C4DE", fg="white")
        self.btn_cancelar.pack(pady=5)
        
        

        
        return 1
    
    def oraciones_dependencia_subordinada(self):
        #cierra la ventana de etiquetado de oraciones
        self.tagging_window.destroy()

        #Crea un vantana para etiquetar oraciones con dependencia subordinada
        self.tagging_window_subordinada = tk.Toplevel(self.root)

        #Pone un título: "Seleccione el tipo de dependencia subordinada de las oraciones"
        tk.Label(self.tagging_window_subordinada, text="Seleccione el tipo de dependencia subordinada de las oraciones", font=("Arial", 14)).pack(pady=10)



        opciones = ["Sustantivas - (O_Sub_Sust)", "Adjetivas o Relativo - (O_Sub_AdjRel)", "Adverbiales - (O_Sub_Adv)"]


        #Crear un espacio de texto para poner la oracion
        self.text_oracion = tk.Text(self.tagging_window_subordinada, height=7, width=70, font=("Arial", 12))
        self.text_oracion.pack(pady=10)

        # Crea un menú desplegable con las opciones
        self.opcion_sub = tk.StringVar(self.tagging_window_subordinada)
        self.opcion_sub.set("Dependencia Subordinada")
        self.menu_sub = tk.OptionMenu(self.tagging_window_subordinada, self.opcion_sub, *opciones)
        self.menu_sub.pack(pady=20)


        #Escribir la oracion en el cuadro de texto
        self.text_oracion.insert(tk.END, self.oracion + "\n\n")

        # Boton de guardar en color verde
        self.btn_guardar = tk.Button(self.tagging_window_subordinada, text="Guardar", command=self.guardar_datos_oraciones_subordinada, borderwidth=1, relief="raised", width=35, height=2, font=("Arial", 16), bg="#25b060", fg="white")
        self.btn_guardar.pack(pady=5)

        # Boton de cancelar en en color gris
        self.btn_cancelar = tk.Button(self.tagging_window_subordinada, text="Cancelar", command=self.tagging_window_subordinada.destroy, borderwidth=1, relief="raised", width=35, height=2, font=("Arial", 16), bg="#B0C4DE", fg="white")
        self.btn_cancelar.pack(pady=5)




        return 1

    
    def oraciones_independencia_simple(self):
        #cierra la ventana de etiquetado de oraciones
        self.tagging_window.destroy()

        #Crea un vantana para etiquetar oraciones con independencia simple
        self.tagging_window_simple = tk.Toplevel(self.root)
        self.tagging_window_simple.title("Etiquetado de Oraciones Simples")

        #Configurar la ventana para adaptarse al contenido
        self.tagging_window_simple.columnconfigure(0, weight=1)
        self.tagging_window_simple.columnconfigure(1, weight=1)
        self.tagging_window_simple.columnconfigure(2, weight=1)
        self.tagging_window_simple.rowconfigure([0, 1,2,3,4], weight=1)

        #Pone un título: "Seleccione el tipo de independencia simple de las oraciones"
        tk.Label(self.tagging_window_simple, text="Seleccione el tipo de independencia simple de las oraciones", font=("Arial", 14)).grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        #Crear un espacio de texto para poner la oracion
        self.text_oracion = tk.Text(self.tagging_window_simple, height=7, width=70, font=("Arial", 12))
        self.text_oracion.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        #Escribir la oracion en el cuadro de texto
        self.text_oracion.insert(tk.END, self.oracion + "\n\n")

        # Variables
        hablante = ["Enunciativas  afirmativas - (OS_AH_EA)","Enunciativas  negativas - (OS_AH_EN)","Interrogativas directas totales con sentido literal - (OS_AH_IDTSL)","Interrogativas directas parciales con sentido literal - (OS_AH_IDPSL)",
                    "Interrogativas disyuntivas - (OS_AH_ID)","Estructura interrogativa con sujeto antepuesto - (OS_AH_ISA)","Interrogativas precedidas de tópico - (OS_AH_IPT)","Exclamativas - (OS_AH_Exc)","Exhortativas-Imperativas - (OS_AH_Exh)","Dubitativas con indicativo - (OS_AH_DI)",
                    "Dubitativas con subjuntivo - (OS_AH_DS)"]
        predicado = ["Impersonales con el verbo 'haber' - (OS_NP_IVH)","Copulativas - (OS_NP_C)","Atributivas - (OS_NP_A)","Transitivas - (OS_NP_T)","Intransitivas - (OS_NP_I)","Reflexivas - (OS_NP_R)","Pasivas perifrásticas - (OS_NP_PP)"]
        frase_enunciado = ["Frase - (Frase)","Enunciado - (enun)"]

        # Hablante
        self.opcion_hablante = tk.StringVar(self.tagging_window_simple)
        self.opcion_hablante.set("Según la actitud del hablante")
        self.menu_hablante = tk.OptionMenu(self.tagging_window_simple, self.opcion_hablante, *hablante)
        self.menu_hablante.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # Predicado
        self.opcion_predicado = tk.StringVar(self.tagging_window_simple)
        self.opcion_predicado.set("Según la naturaleza del predicado")
        self.menu_predicado = tk.OptionMenu(self.tagging_window_simple, self.opcion_predicado, *predicado)
        self.menu_predicado.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # Frase o enunciado
        self.opcion_frase = tk.StringVar(self.tagging_window_simple)
        self.opcion_frase.set("Frase o Enunciado")
        self.menu_frase = tk.OptionMenu(self.tagging_window_simple, self.opcion_frase, *frase_enunciado)
        self.menu_frase.grid(row=2, column=2, padx=10, pady=5, sticky="ew")

        # Boton de guardar en color verde
        self.btn_guardar = tk.Button(self.tagging_window_simple, text="Guardar", command=self.guardar_datos_oraciones_simple, borderwidth=1, relief="raised", width=35, height=2, font=("Arial", 16), bg="#25b060", fg="white")
        self.btn_guardar.grid(row=3, column=0, columnspan=3, pady=10)

        # Boton de cancelar en en color gris
        self.btn_cancelar = tk.Button(self.tagging_window_simple, text="Cancelar", command=self.tagging_window_simple.destroy, borderwidth=1, relief="raised", width=35, height=2, font=("Arial", 16), bg="#B0C4DE", fg="white")
        self.btn_cancelar.grid(row=4, column=0, columnspan=3, pady=10)


        return 1
    
    def guardar_datos_oraciones_simple(self):

        #Abrir archivo json para agregar las etiquetas
        name = "oraciones.json"

        hablante = self.opcion_hablante.get()
        predicado = self.opcion_predicado.get()
        frase = self.opcion_frase.get()

        etiquetas = []

        if hablante != "Según la actitud del hablante":
            etiquetas.append(hablante.split(" - ")[1].replace("(","").replace(")",""))

        if predicado != "Según la naturaleza del predicado":
            etiquetas.append(predicado.split(" - ")[1].replace("(","").replace(")",""))

        if frase != "Frase o Enunciado":
            etiquetas.append(frase.split(" - ")[1].replace("(","").replace(")",""))

        #Abrir archivo json para agregar las etiquetas
        with open(name, "r") as read_file:
            data = json.load(read_file)
            data["oraciones"]["ind_simple"][str(self.identificador)] = etiquetas
            with open(name, "w") as write_file:
                json.dump(data, write_file, indent=4)

        #Agregar el identificador de la oracion al campo de texto
        self.text_identificadores.insert(tk.END, self.identificador + " Sim, ")   

        #Cerrar la ventana de etiquetado de oraciones
        self.tagging_window_simple.destroy()     

        return 1

    
    def oraciones_independencia_coordinada(self):
        #cierra la ventana de etiquetado de oraciones
        self.tagging_window.destroy()


        #Crea un vantana para etiquetar oraciones con independencia coordinada
        self.tagging_window_coordinada = tk.Toplevel(self.root)
        self.tagging_window_coordinada.title("Etiquetado de Oraciones Coordinadas")

        #Configurar la ventana para adaptarse al contenido
        self.tagging_window_coordinada.columnconfigure(0, weight=1)
        self.tagging_window_coordinada.columnconfigure(1, weight=1)
        self.tagging_window_coordinada.rowconfigure([0, 1,2,3,4,5], weight=1)

        #Pone un título: "Seleccione el tipo de independencia coordinada de las oraciones"        
        #Asigna el título a la primera fila
        tk.Label(self.tagging_window_coordinada, text="Seleccione el tipo de independencia coordinada de las oraciones", font=("Arial", 14)).grid(row=0, column=0, columnspan=2, padx=10, pady=10)



        #Crear un espacio de texto para poner la oracion
        self.text_oracion = tk.Text(self.tagging_window_coordinada, height=7, width=70, font=("Arial", 12))
        self.text_oracion.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        #Escribir la oracion en el cuadro de texto
        self.text_oracion.insert(tk.END, self.oracion + "\n\n")

        # Variables
        copulativas = ["Con la conjunción 'y' - (OC_CCy)","Negativas con la conjunción 'ni - (OC_Ncni)' ","Sustitución de 'y' por 'e' - (C_Sye)","Asíndeton - (C_A)","Polisíndeton - (C_P)"]
        adversativas = ["Con la conjunción 'pero' - (A_Cp)", "Con 'sin embargo' - (A_SE)" ,"Con 'aunque' - (A_A)", "Con 'sino - (A_S)", "Con No obstante - (A_NO)"]
        disyuntivas = ["Con la conjuncion 'o' - (D_Co)","Sustitución de 'o' por 'u' - (D_Sou)"]
        distributivas = ["Con uno... otro - (D_CUO)"]


        # Copulativas
        self.opcion_copulativas = tk.StringVar(self.tagging_window_coordinada)
        self.opcion_copulativas.set("Copulativas")
        self.menu_copulativas = tk.OptionMenu(self.tagging_window_coordinada, self.opcion_copulativas, *copulativas)
        self.menu_copulativas.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # Adversativas
        self.opcion_adversativas = tk.StringVar(self.tagging_window_coordinada)
        self.opcion_adversativas.set("Adversativas")
        self.menu_adversativas = tk.OptionMenu(self.tagging_window_coordinada, self.opcion_adversativas, *adversativas)
        self.menu_adversativas.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # Disyuntivas
        self.opcion_disyuntivas = tk.StringVar(self.tagging_window_coordinada)
        self.opcion_disyuntivas.set("Disyuntivas")
        self.menu_disyuntivas = tk.OptionMenu(self.tagging_window_coordinada, self.opcion_disyuntivas, *disyuntivas)
        self.menu_disyuntivas.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        # Distributivas
        self.opcion_distributivas = tk.StringVar(self.tagging_window_coordinada)
        self.opcion_distributivas.set("Distributivas")
        self.menu_distributivas = tk.OptionMenu(self.tagging_window_coordinada, self.opcion_distributivas, *distributivas)
        self.menu_distributivas.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        # Boton de guardar en color verde
        self.btn_guardar = tk.Button(self.tagging_window_coordinada, text="Guardar", command=self.guardar_datos_oraciones_coordinada, borderwidth=1, relief="raised", width=35, height=2, font=("Arial", 16), bg="#25b060", fg="white")
        self.btn_guardar.grid(row=4, column=0, columnspan=2, pady=10)

        # Boton de cancelar en en color gris
        self.btn_cancelar = tk.Button(self.tagging_window_coordinada, text="Cancelar", command=self.tagging_window_coordinada.destroy, borderwidth=1, relief="raised", width=35, height=2, font=("Arial", 16), bg="#B0C4DE", fg="white")
        self.btn_cancelar.grid(row=5, column=0, columnspan=2, pady=10)


        return 1
    
    def guardar_datos_oraciones_coordinada(self):

        #Abrir archivo json para agregar las etiquetas
        name = "oraciones.json"

        #Etiquetas adversativas
        adversativas = self.opcion_adversativas.get()

        #Etiquetas copulativas
        copulativas = self.opcion_copulativas.get()

        #Etiquetas disyuntivas
        disyuntivas = self.opcion_disyuntivas.get()

        #Etiquetas distributivas
        distributivas = self.opcion_distributivas.get()

        if adversativas != "Adversativas":
            etiqueta = adversativas.split(" - ")[1].replace("(","").replace(")","")

        elif copulativas != "Copulativas":
            etiqueta = copulativas.split(" - ")[1].replace("(","").replace(")","")
            
        elif disyuntivas != "Disyuntivas":
            etiqueta = disyuntivas.split(" - ")[1].replace("(","").replace(")","")

        elif distributivas != "Distributivas":
            etiqueta = distributivas.split(" - ")[1].replace("(","").replace(")","")
        else:
            #warning si no se ha seleccionado ninguna etiqueta
            messagebox.showwarning("Advertencia", "No se ha seleccionado ninguna etiqueta")

        #Abrir archivo json para agregar las etiquetas
        with open(name, "r") as read_file:
            data = json.load(read_file)
            data["oraciones"]["ind_coordinada"][self.identificador] = etiqueta
            with open(name, "w") as write_file:
                json.dump(data, write_file, indent=4)

        #Se agrega el identificador al cuadro de texto self.text_identificadores
        self.text_identificadores.insert(tk.END, self.identificador + " Cor, ")        
                    
        
        #Se cierra la ventana de etiquetado de oraciones
        self.tagging_window_coordinada.destroy()
        



        return 1
    
    
    def oraciones_independencia_yuxtaposicion(self):
        #cierra la ventana de etiquetado de oraciones
        self.tagging_window.destroy()

        #Crea un vantana para etiquetar oraciones con yuxtaposición
        self.tagging_window_yuxtaposicion = tk.Toplevel(self.root)

        #Pone un título: "Seleccione el tipo de yuxtaposición de las oraciones"
        tk.Label(self.tagging_window_yuxtaposicion, text="Seleccione el tipo de yuxtaposición de las oraciones", font=("Arial", 14)).pack(pady=10)

        # Crear un marco para organizar los botones en tres columnas
        button_frame = tk.Frame(self.tagging_window_yuxtaposicion)

        #Crear un espacio de texto para poner la oracion
        self.text_oracion = tk.Text(self.tagging_window_yuxtaposicion, height=7, width=70, font=("Arial", 12))
        self.text_oracion.pack(pady=10)

        #Escribir la oracion en el cuadro de texto
        self.text_oracion.insert(tk.END, self.oracion + "\n\n")


        # se organizan los botones en cuatro filas
        button_frame.pack(pady=20)

        # Se crean los botones de yuxtaposición y se organizan en tres filas

        #Boton de yuxtaposición por coma (,) - (O_Yuxt_Coma) y se escribe la etiqueta en el cuadro de texto
        self.btn_yuxtaposicion_coma = tk.Button(button_frame, text="Yuxtaposición por \n coma - (O_Yuxt_Coma)", command= lambda: self.text_oracion.insert(tk.END, "O_Yuxt_Coma, "), borderwidth=1, relief="raised", width=25, height=2, font=("Arial", 16), bg="#B0E0E6", fg="white")
        self.btn_yuxtaposicion_coma.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        #Boton de yuxtaposición por punto y coma (;) - (O_Yuxt_PuntoComa) y se escribe la etiqueta en el cuadro de texto
        self.btn_yuxtaposicion_punto_coma = tk.Button(button_frame, text="Yuxtaposición por  punto  \n y coma - (O_Yuxt_PuntoComa)", command= lambda: self.text_oracion.insert(tk.END, "O_Yuxt_PuntoComa, "), borderwidth=1, relief="raised", width=25, height=2, font=("Arial", 16), bg="#B0E0E6", fg="white")
        self.btn_yuxtaposicion_punto_coma.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        #Boton de yuxtaposición por dos puntos (:) - (O_Yuxt_DosPuntos) y se escribe la etiqueta en el cuadro de texto
        self.btn_yuxtaposicion_dos_puntos = tk.Button(button_frame, text="Yuxtaposición por  dos \n puntos - (O_Yuxt_DosPuntos)", command= lambda: self.text_oracion.insert(tk.END, "O_Yuxt_DosPuntos, "), borderwidth=1, relief="raised", width=25, height=2, font=("Arial", 16), bg="#B0E0E6", fg="white")
        self.btn_yuxtaposicion_dos_puntos.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # Boton de guardar en color verde
        self.btn_guardar = tk.Button(self.tagging_window_yuxtaposicion, text="Guardar", command=self.guardar_datos_oraciones_yuxtaposicion, borderwidth=1, relief="raised", width=35, height=2, font=("Arial", 16), bg="#25b060", fg="white")
        self.btn_guardar.pack(pady=5)

        # Boton de cancelar en en color gris
        self.btn_cancelar = tk.Button(self.tagging_window_yuxtaposicion, text="Cancelar", command=self.tagging_window_yuxtaposicion.destroy, borderwidth=1, relief="raised", width=35, height=2, font=("Arial", 16), bg="#B0C4DE", fg="white")
        self.btn_cancelar.pack(pady=5)


    
        return 1

    def guardar_datos_oraciones_yuxtaposicion(self):

        #Abrir archivo json para agregar las etiquetas
        name = "oraciones.json"

        #etiqueta del cuadro de texto
        etiquetas = self.text_oracion.get("1.0", tk.END)
        etiquetas = etiquetas.split("\n\n")[1]
        etiquetas = etiquetas.split(", ")[0]   

        #Abrir archivo json para agregar las etiquetas
        with open(name, "r") as read_file:
            data = json.load(read_file)
            data["oraciones"]["ind_yuxtaposicion"][self.identificador] = etiquetas
            with open(name, "w") as write_file:
                json.dump(data, write_file, indent=4)

        #Se cierra la ventana de etiquetado de oraciones
        self.tagging_window_yuxtaposicion.destroy()

        #Se agrega el identificador al cuadro de texto self.text_identificadores
        self.text_identificadores.insert(tk.END, self.identificador + " Yux, ")
        


        return 1


    def guardar_datos_oraciones_subordinada(self):
            
        #Abrir archivo json para agregar las etiquetas
        name = "oraciones.json"

        #etiqueta del cuadro de texto
        etiquetas = self.opcion_sub.get()
        etiquetas = etiquetas.split(" - ")[1].replace("(","").replace(")","")

        #Abrir archivo json para agregar las etiquetas
        with open(name, "r") as read_file:
            data = json.load(read_file)
            data["oraciones"]["dep_subordinada"][self.identificador] = etiquetas
            with open(name, "w") as write_file:
                json.dump(data, write_file, indent=4)

        #Se cierra la ventana de etiquetado de oraciones
        self.tagging_window_subordinada.destroy()

        #Se agrega el identificador al cuadro de texto self.text_identificadores
        self.text_identificadores.insert(tk.END, self.identificador + " Sub, ")

        return 1
    
    ##Segunda parte: Etiquetado de conectores logico-temporales

    # def extraer_tokens(self):
    #     # Ruta del archivo JSON
    #     path = self.file_path_json
        
    #     # Lista para almacenar las palabras y sus identificadores
    #     tokens_list = []

    #     # Abrir el archivo JSON
    #     with open(path, "r") as read_file:
    #         data = json.load(read_file)

    #     # Recorrer los párrafos
    #     for paragraph in data["document"]["paragraph"]:
    #         # Si la oración está en formato de diccionario (una sola oración)
    #         if isinstance(paragraph["sentence"], dict):
    #             sentence = paragraph["sentence"]
    #             # Si el token es un solo diccionario
    #             if isinstance(sentence["token"], dict):
    #                 token = sentence["token"]
    #                 tokens_list.append(f"{token['@form']} - (id = {token['@id']})")
    #             # Si el token es una lista de diccionarios
    #             elif isinstance(sentence["token"], list):
    #                 for token in sentence["token"]:
    #                     tokens_list.append(f"{token['@form']} - (id = {token['@id']})")
    #         # Si la oración es una lista de oraciones
    #         elif isinstance(paragraph["sentence"], list):
    #             for sentence in paragraph["sentence"]:
    #                 # Si el token es un solo diccionario
    #                 if isinstance(sentence["token"], dict):
    #                     token = sentence["token"]
    #                     tokens_list.append(f"{token['@form']} - (id = {token['@id']})")
    #                 # Si el token es una lista de diccionarios
    #                 elif isinstance(sentence["token"], list):
    #                     for token in sentence["token"]:
    #                         tokens_list.append(f"{token['@form']} - (id = {token['@id']})")

    #     return tokens_list



    # def tag_connectors(self):
    #     #Pedir al usuario que seleccione un archivo json
    #     self.file_path_json = filedialog.askopenfilename(title="Seleccionar archivo JSON", filetypes=[("JSON files", "*.json")])

    #     #Si no se selecciona un archivo, se muestra un mensaje de advertencia
    #     if not self.file_path_json:
    #         messagebox.showwarning("Archivo No Seleccionado", "Por favor, seleccione un archivo JSON antes de etiquetar.")
    #         return
        
    #     #Abrir el archivo json
    #     with open(self.file_path_json, "r") as read_file:
    #         data = json.load(read_file)
    #         self.data = data

    #     titulo = data["document"]["metadata"]["title"]
    #     id_documento = data["document"]["metadata"]["number"]["@id_doc"]
    #     nivel = data["document"]["metadata"]["level"]
    #     género_textual = data["document"]["metadata"]["textual_genre"]["@type"] + ", "+ data["document"]["metadata"]["textual_genre"]["@subtype"]
    #     responsable = data["document"]["metadata"]["responsable"]


    #     #Crear la ventana de etiquetado de conectores
    #     self.tagging_window_connectors = tk.Toplevel(self.root)
    #     self.tagging_window_connectors.title("Etiquetado de Conectores Lógico-Temporales")

    #     #Configurar la ventana para adaptarse al contenido
    #     self.tagging_window_connectors.columnconfigure(0, weight=1)
    #     self.tagging_window_connectors.columnconfigure(1, weight=1)
    #     self.tagging_window_connectors.columnconfigure(2, weight=1)
    #     self.tagging_window_connectors.columnconfigure(3, weight=1)
    #     self.tagging_window_connectors.columnconfigure(4, weight=1)


    #     self.tagging_window_connectors.rowconfigure([0, 1,2,3,4,5], weight=1)

    #     #Metadata
    #     metadata_frame = tk.Frame(self.tagging_window_connectors)
    #     metadata_frame.grid(row=0, column=0, columnspan=5, padx=10, pady=10, sticky="ew")
    #     metadata_frame.columnconfigure(1, weight=1)

    #     #Crear campos para mostrar metadata
    #     self.metadata_fields = {}
    #     metadata_labels = {
    #         "Título": "title",
    #         "ID del Documento": "number",
    #         "Nivel": "level",
    #         "Género Textual": "textual_genre",
    #         "Etiquetado por": "responsable",
    #     }

    #     for row, (label, field) in enumerate(metadata_labels.items()):
    #         # Etiqueta
    #         tk.Label(metadata_frame, text=f"{label}:", font=("Arial", 8)).grid(row=row, column=0, sticky="w", padx=5, pady=2)
    #         # Campo de entrada
    #         entry = tk.Entry(metadata_frame, font=("Arial", 8))
    #         entry.grid(row=row, column=1, padx=5, pady=1, sticky="ew")
    #         entry.config(state=tk.DISABLED)
    #         self.metadata_fields[field] = entry

    #     #Agregar título al campo
    #     self.update_metadata_field("title", titulo)  
    #     self.update_metadata_field("number", id_documento)
    #     self.update_metadata_field("level", nivel)
    #     self.update_metadata_field("textual_genre", género_textual)
    #     self.update_metadata_field("responsable", responsable)

    #     texto = self.extraer_tokens()
    #     # Crear un canvas para hacer el frame scrolleable
    #     canvas = tk.Canvas(self.tagging_window_connectors)
    #     canvas.grid(row=1, column=1, columnspan=4, padx=10, pady=10, sticky="ew")

    #     # Agregar un scrollbar
    #     scrollbar = tk.Scrollbar(self.tagging_window_connectors, orient="vertical", command=canvas.yview)
    #     scrollbar.grid(row=1, column=5, sticky="nsew")

    #     # Configurar el canvas con el scrollbar
    #     canvas.configure(yscrollcommand=scrollbar.set)
    #     canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    #     # Crear un frame dentro del canvas
    #     button_frame = tk.Frame(canvas)
    #     canvas.create_window((0, 0), window=button_frame, anchor="nw")
    #     n=0
    #     m=0
    #     # Agregar botones al frame por cada elemento de texto
        for idx, token in enumerate(texto):
            
            btn = tk.Button(button_frame, text=token, font=("Arial", 10), command=lambda t=token: self.seleccionar_token(t),bg="#B0E0E6")
            btn.grid(row=m, column=n, padx=5, pady=5, sticky="ew")
            n+=1
            if n==3:
                n=0
                m+=1

        # Configurar el frame de botones para que se ajuste al canvas
        button_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))


    def seleccionar_token(self, token):
        # Aquí puedes definir lo que sucede cuando se selecciona un token
        print(f"Token seleccionado: {token}")        




        


if __name__ == "__main__":
    root = tk.Tk()
    app = CEMTaggerApp(root)
    root.mainloop()




