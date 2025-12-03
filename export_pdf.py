
from io import BytesIO

import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def generar_reporte_pdf(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, "Reporte de gastos empresariales")
    y -= 30

    if df.empty:
        c.setFont("Helvetica", 12)
        c.drawString(40, y, "No hay facturas registradas.")
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer.getvalue()

    df2 = df.copy()
    df2["fecha"] = pd.to_datetime(df2["fecha"], errors="coerce", format="mixed")
    df2["anio"] = df2["fecha"].dt.year
    df2["mes"] = df2["fecha"].dt.month

    total_general = df2["total"].sum()
    c.setFont("Helvetica", 12)
    c.drawString(40, y, f"Total general: $ {total_general:,.2f}")
    y -= 20

    # Totales por año
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Totales por año:")
    y -= 18
    c.setFont("Helvetica", 11)
    tot_anio = df2.groupby("anio")["total"].sum().reset_index()
    for _, row in tot_anio.iterrows():
        c.drawString(60, y, f"{int(row['anio'])}: $ {row['total']:,.2f}")
        y -= 16

    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Totales por año y mes:")
    y -= 18
    c.setFont("Helvetica", 11)
    tot_mes = df2.groupby(["anio", "mes"])["total"].sum().reset_index()
    for _, row in tot_mes.iterrows():
        line = f"{int(row['anio'])}-{int(row['mes']):02d}: $ {row['total']:,.2f}"
        c.drawString(60, y, line)
        y -= 16
        if y < 50:
            c.showPage()
            y = height - 50

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
