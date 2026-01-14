
import streamlit as st
from docxtpl import DocxTemplate
from docx2python import docx2python
import io
import pathlib
import re

# --- Función para extraer campos en orden ---
def extract_fields(path_docx: pathlib.Path):
    text = docx2python(str(path_docx)).text
    campos = re.findall(r"{{\s*([A-Za-z0-9_]+)\s*}}", text)
    # Eliminar duplicados manteniendo el orden
    vistos = set()
    ordenados = []
    for c in campos:
        if c not in vistos:
            vistos.add(c)
            ordenados.append(c)
    return ordenados

# --- Diccionario para etiquetas amigables ---
labels_amigables = {
    "ANO": "AÑO",
    "Nombre_Apellidos_Razon_Social": "Nombre y apellidos / Razón Social",
    "Nombre_Representante": "Nombre del representante del menor (en caso de menor)",
    "representado": "Socio titular / Representante legal (Padre/Madre/Tutor) de: ",
    "Secretario": "Nombre del Secretario/a",
    
}

# --- Carpeta donde buscar plantillas ---
BASE_DIR = pathlib.Path(__file__).parent
plantillas = list(BASE_DIR.glob("*.docx"))

if not plantillas:
    st.error("No se han encontrado archivos .docx junto a app.py.")
    st.stop()

# Crear diccionario para selector
label_to_path = {p.stem.replace("_", " ").title(): p for p in plantillas}
etiquetas = sorted(label_to_path.keys())

# ---------------------- INTERFAZ ----------------------
st.title("🖨 Generador de Documentos - Plantillas Simples")

# Selector de plantilla
choice_label = st.selectbox("Elige tu plantilla", etiquetas)
ruta_plantilla = label_to_path[choice_label]

# Cargar plantilla y extraer campos
tpl = DocxTemplate(str(ruta_plantilla))
campos = extract_fields(ruta_plantilla)

# ---------------------- FORMULARIO ----------------------
st.markdown("### Rellena los campos:")
context = {}
for c in campos:
    etiqueta = labels_amigables.get(c, c)  # Si no está en el diccionario, usa el original
    context[c] = st.text_input(etiqueta)

# ---------------------- GENERAR DOCUMENTO ----------------------
if st.button("🖨 Generar Documento"):
    tpl.render(context)
    buf = io.BytesIO()
    tpl.save(buf)
    buf.seek(0)

    st.download_button(
        "⬇ Descargar .docx",
        data=buf,
        file_name=f"{ruta_plantilla.stem}_rellenado.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

