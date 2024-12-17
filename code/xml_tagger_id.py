import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

# Función para solicitar los datos al usuario
def solicitar_datos():
    title = input("Ingrese el título del documento: ")
    author = input("Ingrese el nombre del autor: ")
    publication_date = input("Ingrese la fecha de publicación (dd/mm/yyyy): ")
    publication_name = input("Ingrese el nombre de la publicación: ")
    source = input("Ingrese la fuente (URL): ")
    query_date = input("Ingrese la fecha de consulta (dd/mm/yyyy): ")
    id_doc = input("Ingrese el número de documento: ")
    level = input("Ingrese el nivel (por ejemplo, B1): ")
    type = input("Ingrese el tipo de documento: ")
    subtype = input("Ingrese el subtipo de documento: ")
    country = input("Ingrese el país (código ISO, por ejemplo, esp): ")
    responsable = input("Ingrese el nombre del responsable: ")
    
    # Crear el elemento metadata
    metadata = ET.Element("metadata")
    
    # Agregar los elementos con los valores proporcionados por el usuario
    ET.SubElement(metadata, "title").text = title
    ET.SubElement(metadata, "author").text = author
    ET.SubElement(metadata, "publication_date").text = publication_date
    ET.SubElement(metadata, "publication_name").text = publication_name
    ET.SubElement(metadata, "source").text = source
    ET.SubElement(metadata, "query_date").text = query_date
    ET.SubElement(metadata, "number", id_doc=id_doc)
    ET.SubElement(metadata, "level").text = level
    ET.SubElement(metadata, "textual_genre", type=type, subtype=subtype)
    ET.SubElement(metadata, "country", name=country)
    ET.SubElement(metadata, "responsable").text = responsable

    type = type[0]+subtype[0:2]

    name = str(id_doc)+"_"+str(level)+"_"+type+"_"+str(country)+".xml"
    
    return metadata,name

# Función para convertir solo la metadata en un formato con saltos de línea
def prettify_metadata(elem):
    """Return a pretty-printed XML string for the metadata Element."""
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

# Función para asignar IDs a párrafos, oraciones y tokens
def asignar_ids(xmlFile):
    # Cargar y parsear el archivo XML
    tree = ET.parse(xmlFile)
    root = tree.getroot()

    # Inicializar contadores
    paragraph_counter = 1
    sentence_counter = 1

    # Recorrer cada párrafo
    for paragraph in root.findall('paragraph'):
        paragraph.set('id', "p"+str(paragraph_counter))  # Asignar id de párrafo
        
        # Recorrer cada oración dentro del párrafo
        for sentence in paragraph.findall('sentence'):
            sentence.set('id', "s"+str(sentence_counter))  # Asignar id de oración
            token_counter = 0
            
            # Recorrer cada token dentro de la oración
            for token in sentence.findall('token'):
                token.set('id', f"t{sentence_counter}.{token_counter}")  # Asignar id de token
                token_counter += 1
            
            sentence_counter += 1
        paragraph_counter += 1

    # Guardar los cambios en un nuevo archivo XML
    tree.write('archivo_modificado.xml', encoding='utf-8', xml_declaration=True)
    print("IDs asignados y archivo guardado como 'archivo_modificado.xml'.")

# Función para agregar metadata al archivo XML
def agregar_metadata_al_xml(xmlFile):
    # Abrir o cargar el archivo XML original
    tree = ET.parse(xmlFile)  
    root = tree.getroot()

    # Verificar si ya existe el elemento de metadata
    if root.find('metadata') is None:
        metadata,name = solicitar_datos()
        
        # Insertar los metadatos al inicio del XML
        # root.insert(0, metadata)
        
        # Guardar el archivo con formato solo para la metadata
        with open(name, 'w', encoding='utf-8') as f:
            # Escribir la metadata con formato bonito
            f.write(prettify_metadata(metadata))
            
            # Escribir el resto del XML sin modificar su formato
            f.write(ET.tostring(root, encoding='unicode', method='xml'))
        
        print(f"Metadata agregada y archivo guardado como {name}.")
    else:
        print("La metadata ya existe en el archivo. No se agregará nuevamente.")


# Función principal que ejecuta ambas partes
def procesar_xml(xmlFile):
    # Asignar IDs a párrafos, oraciones y tokens
    asignar_ids(xmlFile)
    # Agregar metadata al archivo
    agregar_metadata_al_xml('archivo_modificado.xml')

# Ejecutar el script
procesar_xml("corpus.xml")
