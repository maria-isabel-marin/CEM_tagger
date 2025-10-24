# ==========================
# Configuracion de estilos SIMULTEXT
# ==========================

# Colores
COLOR_FONDO = "#f5f5f5"
COLOR_TITULO = "#2c3e50"
COLOR_TEXTO = "#000000"

COLOR_BOTON_VERDE = "#25b060"
COLOR_BOTON_AZUL = "#20B2AA"
COLOR_BOTON_AZUL_CLARO = "#B0C4DE"
COLOR_BOTON_VERDE_CLARO = "#58D68D"  # Nuevo: verde más claro
COLOR_BOTON_TEXTO = "white"

# Fuentes
FUENTE_TITULO = ("Arial", 24, "bold")
FUENTE_SUBTITULO = ("Arial", 24, "bold")

FUENTE_TEXTO = ("Arial", 12)
FUENTE_BOTON = ("Arial", 16)

# Tamaño ventana
VENTANA_ANCHO = 800
VENTANA_ALTO = 600

#tamaños
ALTURA_BOTON1 = 3


# Etiquetas Parrafos
# Diccionario de etiquetas para textos NARRATIVOS
# Diccionario de etiquetas para textos NARRATIVOS
ETIQUETAS_NARRATIVO = {
    "Introducción": "N_Intro",
    "Desarrollo": "N_Dllo", 
    "Clímax": "N_Clim",
    "Desenlace": "N_Des",
    "Título": "N_Tit",
    "Subtítulo": "N_Subt",
    "Datos del autor": "N_DA"
}

# Diccionario de etiquetas para textos ARGUMENTATIVOS
ETIQUETAS_ARGUMENTATIVO = {
    "Introducción": "A_Intro",
    "Desarrollo": "A_Dllo",
    "Conclusión": "A_Con",
    "Datos bibliográficos": "A_DB",
    "Título": "A_Tit",
    "Subtítulo": "A_Subt",
    "Datos del autor": "A_DA",
    "Referencias": "A_Ref"
}

# config.py

# Tipos de discurso disponibles
TIPOS_DISCURSO = {
    "Político": "D_Pol",
    "Jurídico": "D_Jur", 
    "Religioso": "D_Rel",
    "Comercial o Publicitario": "D_CP",
    "Didáctico": "D_Did",
    "Social": "D_Soc",
    "Periodístico": "D_Per",
    "Científico": "D_Cien",
    "Literario": "D_Lit",
    "Académico": "D_Acad"
}


#Diccionario de etiquetas de oraciones
# Diccionario de etiquetas de oraciones
ETIQUETAS_ORACIONES = {
    "ind_simple": {
        "Hablante - Enunciativas afirmativas": "OS_AH_EA",
        "Hablante - Enunciativas negativas": "OS_AH_EN",
        "Hablante - Interrogativas directas totales con sentido literal": "OS_AH_IDTSL",
        "Hablante - Interrogativas directas parciales con sentido literal": "OS_AH_IDPSL",
        "Hablante - Interrogativas disyuntivas": "OS_AH_ID",
        "Hablante - Estructura interrogativa con sujeto antepuesto": "OS_AH_ISA",
        "Hablante - Interrogativas precedidas de tópico": "OS_AH_IPT",
        "Hablante - Exclamativas": "OS_AH_Exc",
        "Hablante - Exhortativas-Imperativas": "OS_AH_Exh",
        "Hablante - Dubitativas con indicativo": "OS_AH_DI",
        "Hablante - Dubitativas con subjuntivo": "OS_AH_DS",

        "Predicado - Impersonales con el verbo 'haber'": "OS_NP_IVH",
        "Predicado - Copulativas": "OS_NP_C",
        "Predicado - Atributivas": "OS_NP_A",
        "Predicado - Transitivas": "OS_NP_T",
        "Predicado - Intransitivas": "OS_NP_I",
        "Predicado - Reflexivas": "OS_NP_R",
        "Predicado - Pasivas perifrásticas": "OS_NP_PP",

        "Frase o enunciado - Frase": "Frase",
        "Frase o enunciado - Enunciado": "Enun",
    },

    "ind_coordinada": {
        "Copulativas - Con la conjunción 'y'": "OC_CCy",
        "Copulativas - Negativas con la conjunción 'ni'": "OC_Ncni",
        "Copulativas - Sustitución de 'y' por 'e'": "C_Sye",
        "Copulativas - Asíndeton": "C_A",
        "Copulativas - Polisíndeton": "C_P",

        "Adversativas - Con la conjunción 'pero'": "A_Cp",
        "Adversativas - Con 'sin embargo'": "A_SE",
        "Adversativas - Con 'aunque'": "A_A",
        "Adversativas - Con 'sino'": "A_S",
        "Adversativas - Con 'no obstante'": "A_NO",

        "Disyuntivas - Con la conjunción 'o'": "D_Co",
        "Disyuntivas - Sustitución de 'o' por 'u'": "D_Sou",

        "Distributivas - Con 'uno... otro'": "D_CUO",
    },

    "ind_yuxtaposicion": {
        "Yuxtaposición - Por coma": "O_Yuxt_Coma",
        "Yuxtaposición - Por punto y coma": "O_Yuxt_PuntoComa",
        "Yuxtaposición - Por dos puntos": "O_Yuxt_DosPuntos",
    },

    "dep_subordinada": {
        "Subordinada - Sustantivas": "O_Sub_Sust",
        "Subordinada - Adjetivas o Relativas": "O_Sub_AdjRel",
        "Subordinada - Adverbiales": "O_Sub_Adv",
    },
}

# Definir categorías de conectores con colores
CASOS_CONECTORES = {
    "Comentadores": [["pues", "pues_bien", "dicho esto", "dicho eso", "así las cosas", "por cierto", "a propósito", "a todo esto"], "MD_Com", "lightblue"],
    "Ordenadores": [["en primer lugar", "en segundo lugar", "por una parte", "por otra parte", "de un lado", "de otro lado", "para empezar", "finalmente", "para terminar", "primeramente", "segundamente"], "MD_Ord", "lightgreen"],
    "Ordenadores-temporales": [["mientras", "mientras_que", "cuando", "antes_de que", "antes_de", "después que", "aún no", "luego_que"], "MD_OrdTemp", "lightgreen"],
    "Digresores": [["por cierto", "a propósito", "a todo esto"], "MD_Dig", "lightyellow"],
    "Aditivos": [["además", "encima", "aparte", "incluso"], "MD_Adit", "lightpink"],
    "Consecutivos": [["por tanto", "por_consiguiente", "por_ende", "en_consecuencia", "de ahí", "entonces", "pues", "así", "así_pues", "aunque"], "MD_Cons", "lightcoral"],
    "Contraargumentativos": [["en cambio", "por_el_contrario", "por contra", "antes_bien", "sin embargo", "no_obstante", "con todo"], "MD_Contra", "lightsalmon"],
    "Explicativos": [["o_sea", "es decir", "esto es", "a saber", "en otras palabras", "porque", "como", "dado_que", "visto que", "puesto que", "pues", "ya_que"], "MD_Exp", "lightseagreen"],
    "De rectificación": [["mejor dicho", "mejor aún", "más bien", "antes", "antes que"], "MD_Rect", "lightsteelblue"],
    "De distanciamiento": [["en cualquier caso", "en_todo_caso", "de_todos_modos"], "MD_Dist", "lightcyan"],
    "Recapitulativos": [["en suma", "en conclusión", "en definitiva", "en fin", "a_el_fin_y_a_el_cabo", "por lo demás"], "MD_Recap", "lightgoldenrod"],
    "De refuerzo argumentativo": [["en realidad", "en el fondo", "de hecho"], "MD_Refa", "lightpink"],
    "De concreción": [["por_ejemplo", "en particular"], "MD_Conc", "lightskyblue"],
    "Epistémicos": [["claro", "desde_luego", "por_supuesto", "naturalmente", "sin duda", "en efecto", "por lo visto", "a el parecer"], "MD_Epis", "lightgray"],
    "Adversativo": [["pero", "mas", "empero", "sino"], "MD_Adv", "darkorange"]
}
