
import xml.etree.ElementTree as ET
from typing import Any


class CFDIParser:
    """Parser sencillo para CFDI 3.3 / 4.0 en XML."""

    def __init__(self, xml_bytes: bytes) -> None:
        self.xml_bytes = xml_bytes

    def parse(self) -> dict[str, Any]:
        try:
            root = ET.fromstring(self.xml_bytes)
        except Exception as e:  # pragma: no cover
            return {"success": False, "error": f"XML inválido: {e}"}

        # namespaces típicos de CFDI
        ns = {"cfdi": "http://www.sat.gob.mx/cfd/4"}
        if not root.tag.endswith("Comprobante"):
            # intentar sin namespace
            ns = {}
        attrib = root.attrib

        fecha = attrib.get("Fecha") or attrib.get("fecha") or ""
        subtotal = float(attrib.get("SubTotal", "0"))
        total = float(attrib.get("Total", "0"))
        moneda = attrib.get("Moneda", "MXN")
        tipo = attrib.get("TipoDeComprobante", "")
        version = attrib.get("Version", "")

        emisor = root.find("cfdi:Emisor", ns) or root.find("Emisor")
        receptor = root.find("cfdi:Receptor", ns) or root.find("Receptor")
        conceptos = root.find("cfdi:Conceptos", ns) or root.find("Conceptos")

        rfc_emisor = emisor.attrib.get("Rfc") if emisor is not None else ""
        nombre_emisor = emisor.attrib.get("Nombre") if emisor is not None else ""
        rfc_receptor = receptor.attrib.get("Rfc") if receptor is not None else ""
        nombre_receptor = receptor.attrib.get("Nombre") if receptor is not None else ""
        uso_cfdi = receptor.attrib.get("UsoCFDI") if receptor is not None else ""

        concepto_principal = ""
        if conceptos is not None and list(conceptos):
            concepto_principal = list(conceptos)[0].attrib.get("Descripcion", "")

        # impuestos trasladados
        impuestos_node = root.find("cfdi:Impuestos", ns) or root.find("Impuestos")
        total_impuestos = 0.0
        if impuestos_node is not None:
            traslados = impuestos_node.find("cfdi:Traslados", ns) or impuestos_node.find("Traslados")
            if traslados is not None:
                for t in list(traslados):
                    try:
                        total_impuestos += float(t.attrib.get("Importe", "0"))
                    except ValueError:
                        pass

        factura = {
            "uuid": attrib.get("Folio", "") or "",
            "origen": "XML",
            "fecha": fecha.split("T")[0] if "T" in fecha else fecha,
            "rfc_emisor": rfc_emisor,
            "nombre_emisor": nombre_emisor,
            "rfc_receptor": rfc_receptor,
            "nombre_receptor": nombre_receptor,
            "uso_cfdi": uso_cfdi,
            "moneda": moneda,
            "subtotal": subtotal,
            "impuestos": total_impuestos,
            "total": total,
            "tipo_comprobante": tipo,
            "version_cfdi": version,
            "concepto_principal": concepto_principal,
        }

        return {"success": True, "factura": factura}
