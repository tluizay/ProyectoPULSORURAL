from __future__ import annotations
import subprocess
from pathlib import Path

EXTENSIONES_IMAGENES_PERMITIDAS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}
MINIMO_CARACTERES_TEXTO_NATIVO = 200

def _extraer_texto_pdf_nativo(ruta_archivo: Path) -> str:
    """Extrae el texto de un PDF preservando la estructura de columnas."""
    resultado_proceso = subprocess.run(
        ["pdftotext", "-layout", str(ruta_archivo), "-"],
        capture_output=True,
        text=True,
    )
    return resultado_proceso.stdout

def _extraer_texto_imagen_ocr(ruta_archivo: Path) -> str:
    """Aplica reconocimiento óptico de caracteres (OCR) sobre una imagen."""
    import pytesseract
    from PIL import Image

    return pytesseract.image_to_string(Image.open(ruta_archivo), lang="spa+eng")

def _extraer_texto_pdf_escaneado_ocr(ruta_archivo: Path) -> str:
    """Convierte las páginas de un PDF escaneado en imágenes y aplica OCR a cada una."""
    import tempfile
    import pytesseract
    from PIL import Image

    textos_paginas = []
    with tempfile.TemporaryDirectory() as directorio_temporal:
        prefijo_pagina = f"{directorio_temporal}/pagina"
        subprocess.run(
            ["pdftoppm", "-jpeg", "-r", "200", str(ruta_archivo), prefijo_pagina],
            capture_output=True,
        )
        for ruta_imagen_pagina in sorted(Path(directorio_temporal).glob("pagina*.jpg")):
            texto_pagina = pytesseract.image_to_string(Image.open(ruta_imagen_pagina), lang="spa+eng")
            textos_paginas.append(texto_pagina)
            
    return "\n".join(textos_paginas)

def extraer_texto_archivo(ruta_archivo: Path) -> str:
    """Devuelve el texto plano del archivo, detectando automáticamente si requiere OCR."""
    extension = ruta_archivo.suffix.lower()

    if extension in EXTENSIONES_IMAGENES_PERMITIDAS:
        return _extraer_texto_imagen_ocr(ruta_archivo)

    if extension == ".pdf":
        texto_extraido = _extraer_texto_pdf_nativo(ruta_archivo)
        # Si el texto extraído es muy escaso, se asume que es un PDF escaneado
        if len(texto_extraido.strip()) < MINIMO_CARACTERES_TEXTO_NATIVO:
            texto_extraido = _extraer_texto_pdf_escaneado_ocr(ruta_archivo)
        return texto_extraido

    raise ValueError(f"Formato de archivo no soportado: {extension}")
