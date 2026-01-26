import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import re
import etiquetado.config as config


class VentanaEtiquetadoCorreferentes:
    """
    Ventana completa para etiquetado de correferencias.
    """

    def __init__(self, root, ruta_json, tipo_texto):
        self.root = root
        self.root.title("SIMULTEXT - Correferencia Textual")
        self.root.geometry("1400x800")
        self.root.configure(bg=config.COLOR_FONDO)

        self.ruta_json = ruta_json
        self.tipo_texto = tipo_texto

        self.tokens_por_parrafo = {}
        # {"R1": [ {corr, tipo, tokens}, ... ]}
        self.etiquetas_correferencia = {}
        # {"t1": (inicio, fin), "t2": (inicio, fin), ...}
        self.token_posiciones = {}

        # Configurar colores de resaltado para cada referente
        self.colores_resaltado = {
            "R1": "#FFB3B3",  # Rojo claro
            "R2": "#D9FFB3",  # Verde lima claro
            "R3": "#B3FFF8",  # Cian claro
            "R4": "#B3C5FF",  # Azul claro
            "R5": "#FFB3EA"   # Magenta claro
        }

        self.referente_seleccionado = None
        self.botones_referentes = {}   # ### para marcar visualmente el referente activo

        self.cargar_datos_desde_json()
        self.crear_interfaz()
        self.configurar_tags_resaltado()
        self.resaltar_todo_desde_etiquetas()  # ### resalta lo que ya estaba etiquetado
        self.actualizar_json_final()          # ### muestra las correferencias iniciales (si existen)

    # =========================================================
    # CARGA DEL JSON
    # =========================================================
    def cargar_datos_desde_json(self):
        try:
            with open(self.ruta_json, "r", encoding="utf-8") as f:
                datos = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo JSON:\n{e}")
            return

        parrafos = datos.get("document", {}).get("paragraph", [])
        if isinstance(parrafos, dict):
            parrafos = [parrafos]

        for parrafo in parrafos:
            if not parrafo:
                continue

            pid = parrafo.get("@id", "p0")
            self.tokens_por_parrafo[pid] = []

            oraciones = parrafo.get("sentence", [])
            if isinstance(oraciones, dict):
                oraciones = [oraciones]

            for oracion in oraciones:
                tokens = oracion.get("token", [])
                if isinstance(tokens, dict):
                    tokens = [tokens]

                for tk_info in tokens:
                    self.tokens_por_parrafo[pid].append({
                        "form": tk_info.get("@form", ""),
                        "id": tk_info.get("@id", "")
                    })

        # ### Cargar correferentes ya guardados, si existen
        self.etiquetas_correferencia = datos.get("document", {}) \
                                         .get("Etiquetado", {}) \
                                         .get("correferentes", {}) or {}

    # =========================================================
    # INTERFAZ COMPLETA
    # =========================================================
    def crear_interfaz(self):

        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill="both", expand=True)

        # ---------------------------------------
        # IZQUIERDA : TEXTO
        # ---------------------------------------
        left_frame = tk.Frame(paned, bg=config.COLOR_FONDO)
        paned.add(left_frame, weight=1)

        tk.Label(
            left_frame,
            text="TEXTO PARA CORREFERENCIA",
            font=("Arial", 14, "bold"),
            bg=config.COLOR_FONDO,
            fg=config.COLOR_TITULO
        ).pack(pady=5)

        self.text_area = scrolledtext.ScrolledText(
            left_frame, wrap="word",
            font=("Arial", 12), bg="white", padx=10, pady=10
        )
        self.text_area.pack(fill="both", expand=True)

        self.text_area.tag_config("token", font=("Arial", 12, "bold"))
        self.text_area.tag_config("id", font=("Arial", 7, "italic"))

        # Tag para selección temporal
        self.text_area.tag_config("seleccion_temporal", background="#add8e6", foreground="black")

        self.mostrar_texto()

        # ---------------------------------------
        # DERECHA : CONTROLES
        # ---------------------------------------
        right_frame = tk.Frame(paned, bg=config.COLOR_FONDO, padx=10, pady=10)
        paned.add(right_frame, weight=1)

        # ======== BOTONES R1–R5 ========
        tk.Label(
            right_frame, text="REFERENTES:",
            font=("Arial", 12, "bold"),
            bg=config.COLOR_FONDO, fg=config.COLOR_TITULO
        ).pack(anchor="w", pady=(0, 5))

        fila = tk.Frame(right_frame, bg=config.COLOR_FONDO)
        fila.pack(anchor="w", pady=(0, 5))

        for r in ["R1", "R2", "R3", "R4", "R5"]:
            btn = tk.Button(
                fila, text=r, width=6,
                bg=config.COLORES_REFERENTES[r],
                fg="black",
                font=("Arial", 12, "bold"),
                command=lambda ref=r: self.seleccionar_referente(ref)
            )
            btn.pack(side="left", padx=4)
            self.botones_referentes[r] = btn  # ### guardar referencia

        # Label para mostrar referente actual
        self.label_referente_actual = tk.Label(
            right_frame,
            text="Referente actual: Ninguno",
            font=("Arial", 10, "italic"),
            bg=config.COLOR_FONDO,
            fg=config.COLOR_TEXTO
        )
        self.label_referente_actual.pack(anchor="w", pady=(0, 10))

        # ======== MENÚ DESPLEGABLE ========
        tk.Label(
            right_frame, text="TIPO DE CORREFERENCIA:",
            font=("Arial", 12, "bold"), bg=config.COLOR_FONDO,
            fg=config.COLOR_TITULO
        ).pack(anchor="w", pady=(10, 5))

        opciones = list(config.ETIQUETAS_CORREFERENCIA.keys())
        self.tipo_correferencia = tk.StringVar(value=opciones[0])

        ttk.Combobox(
            right_frame, textvariable=self.tipo_correferencia,
            values=opciones, state="readonly", width=40
        ).pack(anchor="w", pady=(0, 15))

        # ======== BOTONES AÑADIR / GUARDAR ========
        botones = tk.Frame(right_frame, bg=config.COLOR_FONDO)
        botones.pack(fill="x", pady=(0, 15))

        tk.Button(
            botones, text="AÑADIR",
            bg=config.COLOR_BOTON_AZUL, fg="white",
            font=("Arial", 12, "bold"),
            command=self.anadir_correferencia
        ).pack(side="left", expand=True, fill="x", padx=4)

        tk.Button(
            botones, text="GUARDAR",
            bg=config.COLOR_BOTON_VERDE, fg="white",
            font=("Arial", 12, "bold"),
            command=self.guardar_en_json
        ).pack(side="left", expand=True, fill="x", padx=4)

        # ======== CUADRO DE CADENAS (ENTRADAS) ========
        tk.Label(
            right_frame, text="Historial de etiquetado",
            font=("Arial", 12, "bold"), bg=config.COLOR_FONDO,
            fg=config.COLOR_TITULO
        ).pack(anchor="w", pady=(0, 5))

        self.cuadro_cadenas = scrolledtext.ScrolledText(
            right_frame, height=8, font=("Courier New", 11), bg="white"
        )
        self.cuadro_cadenas.pack(fill="x", pady=(0, 10))

        # ======== SEGUNDO CUADRO: JSON FINAL ========
        tk.Label(
            right_frame, text="Cadena correferencial",
            font=("Arial", 12, "bold"), bg=config.COLOR_FONDO,
            fg=config.COLOR_TITULO
        ).pack(anchor="w", pady=(0, 5))

        self.cuadro_json_final = scrolledtext.ScrolledText(
            right_frame, height=10, font=("Courier New", 11), bg="white"
        )
        self.cuadro_json_final.pack(fill="both", expand=True)

    def configurar_tags_resaltado(self):
        """Configura los tags de resaltado para cada referente."""
        for ref, color in self.colores_resaltado.items():
            self.text_area.tag_config(
                f"resaltado_{ref}",
                background=color,
                foreground="black",
                relief="raised",
                borderwidth=1
            )

    # =========================================================
    # MOSTRAR TEXTO
    # =========================================================
    def mostrar_texto(self):
        self.text_area.config(state="normal")
        self.text_area.delete("1.0", tk.END)

        # Limpiar posiciones anteriores
        self.token_posiciones = {}

        for pid, tokens in self.tokens_por_parrafo.items():
            self.text_area.insert(tk.END, f"\nPÁRRAFO {pid.upper()}\n")

            for tk_info in tokens:
                palabra = tk_info["form"]
                tid = tk_info["id"]

                # Guardar posición de inicio del token
                inicio = self.text_area.index("end-1c")

                # Insertar palabra
                self.text_area.insert(tk.END, palabra, "token")

                # Insertar ID
                self.text_area.insert(tk.END, f"({tid}) ", "id")

                # Guardar posición del token (sin incluir el ID)
                pos_inicio = self.text_area.index(f"{inicio}")
                pos_fin = self.text_area.index(f"{inicio}+{len(palabra)}c")
                self.token_posiciones[tid] = (pos_inicio, pos_fin)

            self.text_area.insert(tk.END, "\n\n")

        self.text_area.config(state="disabled")

    # =========================================================
    # EXTRAER TOKENS DEL TEXTO SELECCIONADO
    # =========================================================
    def obtener_tokens_de_seleccion(self):
        try:
            seleccionado = self.text_area.selection_get()
        except tk.TclError:
            return []

        # Extraer tokens de la selección
        tokens = re.findall(r"\(([^)]+)\)", seleccionado)

        # Resaltar temporalmente la selección actual
        self.resaltar_seleccion_temporal()

        return tokens

    def resaltar_seleccion_temporal(self):
        """Resalta temporalmente la selección actual."""
        try:
            # Limpiar resaltado temporal anterior
            self.text_area.tag_remove("seleccion_temporal", "1.0", tk.END)

            # Aplicar resaltado temporal a la selección actual
            if self.text_area.tag_ranges("sel"):
                inicio = self.text_area.index("sel.first")
                fin = self.text_area.index("sel.last")
                self.text_area.tag_add("seleccion_temporal", inicio, fin)
        except Exception:
            pass

    # =========================================================
    # SELECCIONAR REFERENTE
    # =========================================================
    def seleccionar_referente(self, ref):
        self.referente_seleccionado = ref
        self.cuadro_cadenas.insert(tk.END, f"// Seleccionado {ref}\n")
        self.cuadro_cadenas.see(tk.END)

        # Actualizar label
        self.label_referente_actual.config(text=f"Referente actual: {ref}")

        # Actualizar aspecto de botones
        for r, btn in self.botones_referentes.items():
            if r == ref:
                btn.config(relief="sunken", bd=3)
            else:
                btn.config(relief="raised", bd=1)

    # =========================================================
    # AÑADIR CORREFERENTE
    # =========================================================
    def anadir_correferencia(self):
        if not self.referente_seleccionado:
            messagebox.showwarning("Falta referente", "Seleccione un referente (R1–R5).", parent=self.root)
            return

        tipo_legible = self.tipo_correferencia.get()
        codigo_tipo = config.ETIQUETAS_CORREFERENCIA[tipo_legible]

        tokens = self.obtener_tokens_de_seleccion()
        if not tokens:
            messagebox.showwarning("Error", "Debe seleccionar tokens del texto.", parent=self.root)
            return

        lista_ref = self.etiquetas_correferencia.setdefault(self.referente_seleccionado, [])

        # Asignar corr = c0 si es referente,
        # c1, c2... para los demás
        if codigo_tipo == "R":
            corr = "c0"
        else:
            corr = f"c{len(lista_ref)}"

        entrada = {
            "corr": corr,
            "tipo": codigo_tipo,
            "tokens": tokens
        }

        lista_ref.append(entrada)

        # Mostrar en el primer cuadro
        self.cuadro_cadenas.insert(
            tk.END,
            json.dumps(entrada, ensure_ascii=False, separators=(",", ":")) + "\n"
        )
        self.cuadro_cadenas.see(tk.END)

        # Resaltar los tokens en el texto
        self.resaltar_tokens(tokens, self.referente_seleccionado)

        # Actualizar el JSON final abajo
        self.actualizar_json_final()

    def resaltar_tokens(self, tokens, referente):
        """Resalta los tokens en el texto con el color del referente."""
        for token_id in tokens:
            if token_id in self.token_posiciones:
                inicio, fin = self.token_posiciones[token_id]
                tag_name = f"resaltado_{referente}"
                self.text_area.tag_add(tag_name, inicio, fin)

    def resaltar_todo_desde_etiquetas(self):
        """Resalta todas las correferencias ya cargadas desde el JSON."""
        for ref, lista in self.etiquetas_correferencia.items():
            for entrada in lista:
                tokens = entrada.get("tokens", [])
                self.resaltar_tokens(tokens, ref)

    # =========================================================
    # ACTUALIZAR VISTA DEL JSON FINAL
    # =========================================================
    def actualizar_json_final(self):
        self.cuadro_json_final.config(state="normal")
        self.cuadro_json_final.delete("1.0", tk.END)

        # Si no hay correferencias, mostramos un objeto vacío
        if not self.etiquetas_correferencia:
            self.cuadro_json_final.insert(tk.END, "{}")
            self.cuadro_json_final.see(tk.END)
            return

        # Construimos JSON final con cada correferente en UNA sola línea
        texto = "{\n"
        for ref, lista in self.etiquetas_correferencia.items():
            texto += f'  "{ref}": [\n'
            for item in lista:
                linea = json.dumps(item, ensure_ascii=False, separators=(",", ":"))
                texto += f"    {linea},\n"
            if lista:
                texto = texto.rstrip(",\n") + "\n"
            texto += "  ],\n"
        texto = texto.rstrip(",\n") + "\n}"

        self.cuadro_json_final.insert(tk.END, texto)
        self.cuadro_json_final.see(tk.END)

    # =========================================================
    # GUARDAR EN ARCHIVO JSON REAL
    # =========================================================
    def guardar_en_json(self):
        """
        Guarda EXACTAMENTE lo que está escrito en el cuadro_json_final,
        sin reacomodar, sin compactar todo, sin modificar formato.
        """
        try:
            # Leer el texto del cuadro
            contenido_json = self.cuadro_json_final.get("1.0", tk.END).strip()

            # Validar que sea JSON correcto
            try:
                correferencias = json.loads(contenido_json)
            except json.JSONDecodeError as e:
                msg = (
                    f"El contenido del cuadro JSON no es válido.\n\n"
                    f"Línea: {e.lineno}, Columna: {e.colno}\n"
                    f"Detalle: {e.msg}"
                )
                messagebox.showerror("Error en JSON", msg, parent=self.root)
                return

            # Cargar archivo original
            with open(self.ruta_json, "r", encoding="utf-8") as f:
                datos = json.load(f)

            # Reemplazar solo la parte de correferentes
            datos.setdefault("document", {}).setdefault("Etiquetado", {})
            datos["document"]["Etiquetado"]["correferentes"] = correferencias

            # Guardar el archivo JSON EXACTAMENTE como en cuadro,
            # pero embebido correctamente dentro del JSON existente.
            # → Construimos el JSON manualmente para respetar formato.
            texto_final = json.dumps(datos, ensure_ascii=False, indent=2)

            # Sobrescribir archivo completo con texto formateado
            with open(self.ruta_json, "w", encoding="utf-8") as f:
                f.write(texto_final)

            messagebox.showinfo("Guardado", "Correferencias guardadas correctamente.", parent=self.root)
            self.root.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}", parent=self.root)

