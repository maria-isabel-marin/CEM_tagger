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
COLOR_BOTON_TEXTO = "white"

# Fuentes
FUENTE_TITULO = ("Arial", 24, "bold")
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
