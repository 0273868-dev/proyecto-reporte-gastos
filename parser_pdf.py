
import re
from datetime import datetime
from typing import Any

import pdfplumber


class PDFParser:
    """Parser sencillo de facturas PDF basado en patrones de texto."""

    def __init__(self, pdf_path: str) -> None:
        self.pdf_path = pdf_path

    def parse(self) -> dict[str, Any]:
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception as e:  # pragma: no cover
            return {"success": False, "error": f"No se pudo leer el PDF: {e}"}

        def find(pattern: str) -> str | None:
            m = re.search(pattern, text, re.IGNORECASE)
            return m.group(1).strip() if m else None

        empresa = find(r"Empresa:\s*(.+)")
        rfc = find(r"RFC:\s*([A-Z0-9]{12,13})")
        fecha = find(r"Fecha:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})")
        if not fecha:
            # intentar dd/mm/aaaa
            fecha_dm = find(r"Fecha:\s*([0-9]{2}/[0-9]{2}/[0-9]{4})")
            if fecha_dm:
                try:
                    fecha = datetime.strptime(fecha_dm, "%d/%m/%Y").strftime("%Y-%m-%d")
                except ValueError:
                    fecha = None

        total_txt = find(r"Total:\s*([0-9,\.]+)")
        total = 0.0
        if total_txt:
            total = float(total_txt.replace(",", "").strip())

        if not empresa and not total:
            return {"success": False, "error": "No se encontraron datos reconocibles en el PDF."}

        factura = {
            "uuid": f"PDF-{datetime.now().timestamp()}",
            "origen": "PDF",
            "fecha": fecha or datetime.now().strftime("%Y-%m-%d"),
            "rfc_emisor": rfc or "XAXX010101000",
            "nombre_emisor": empresa or "Empresa desde PDF",
            "rfc_receptor": "XEXX010101000",
            "nombre_receptor": "Cliente genérico",
            "uso_cfdi": "",
            "moneda": "MXN",
            "subtotal": total,
            "impuestos": 0.0,
            "total": total,
            "tipo_comprobante": "I",
            "version_cfdi": "PDF",
            "concepto_principal": "Gasto leído desde PDF",
        }

        return {"success": True, "factura": factura}
