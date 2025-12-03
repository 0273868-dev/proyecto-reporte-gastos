
import os
import tempfile

import pandas as pd
import streamlit as st

from database import DatabaseManager
from parser_xml import CFDIParser
from parser_pdf import PDFParser
from visualizaciones import (
    grafica_totales_por_mes,
    grafica_totales_por_anio,
    grafica_por_rfc_emisor,
)
from export_pdf import generar_reporte_pdf


st.set_page_config(
    page_title="Sistema de Reporte de Gastos",
    page_icon="📊",
    layout="wide",
)

db = DatabaseManager()


def cargar_datos() -> pd.DataFrame:
    return db.obtener_facturas()


def pagina_cargar_facturas():
    st.title("📥 Cargar Facturas XML y PDF")
    st.write("Sube facturas de tu empresa en formato XML (CFDI) o PDF.")

    archivos = st.file_uploader(
        "Selecciona uno o varios archivos",
        type=["xml", "pdf"],
        accept_multiple_files=True,
    )

    if not archivos:
        st.info("Sube al menos un archivo para empezar.")
        return

    if st.button("🚀 Procesar facturas"):
        resultados = []
        for archivo in archivos:
            nombre = archivo.name
            ext = nombre.lower().split(".")[-1]

            if ext == "xml":
                try:
                    xml_bytes = archivo.read()
                    parser = CFDIParser(xml_bytes)
                    res = parser.parse()
                    if not res.get("success"):
                        resultados.append(
                            {
                                "archivo": nombre,
                                "tipo": "XML",
                                "status": "Error",
                                "mensaje": res.get("error", "Error desconocido"),
                            }
                        )
                        continue
                    factura = res["factura"]
                    ok, msg = db.insertar_factura(factura)
                    resultados.append(
                        {
                            "archivo": nombre,
                            "tipo": "XML",
                            "status": "Éxito" if ok else "Error",
                            "mensaje": msg,
                        }
                    )
                except Exception as e:
                    resultados.append(
                        {"archivo": nombre, "tipo": "XML", "status": "Error", "mensaje": str(e)}
                    )

            elif ext == "pdf":
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(archivo.read())
                        tmp_path = tmp.name
                    parser = PDFParser(tmp_path)
                    res = parser.parse()
                    os.remove(tmp_path)
                    if not res.get("success"):
                        resultados.append(
                            {
                                "archivo": nombre,
                                "tipo": "PDF",
                                "status": "Error",
                                "mensaje": res.get("error", "Error al leer el PDF"),
                            }
                        )
                        continue
                    factura = res["factura"]
                    ok, msg = db.insertar_factura(factura)
                    resultados.append(
                        {
                            "archivo": nombre,
                            "tipo": "PDF",
                            "status": "Éxito" if ok else "Error",
                            "mensaje": msg,
                        }
                    )
                except Exception as e:
                    resultados.append(
                        {"archivo": nombre, "tipo": "PDF", "status": "Error", "mensaje": str(e)}
                    )
            else:
                resultados.append(
                    {
                        "archivo": nombre,
                        "tipo": "Desconocido",
                        "status": "Error",
                        "mensaje": "Extensión no soportada",
                    }
                )

        st.success("Procesamiento completado.")
        st.subheader("Resultados del procesamiento")
        st.dataframe(pd.DataFrame(resultados))


def pagina_dashboard():
    st.title("📊 Dashboard de Gastos Empresariales")

    df = cargar_datos()
    if df.empty:
        st.info("Aún no hay facturas registradas. Ve a 'Cargar facturas' para comenzar.")
        return

    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce", format="mixed")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total facturas", len(df))
    col2.metric("Total facturado", f"$ {df['total'].sum():,.2f}")
    col3.metric("Total impuestos", f"$ {df['impuestos'].sum():,.2f}")
    col4.metric("RFC emisores", df["rfc_emisor"].nunique())

    fig_mes = grafica_totales_por_mes(df)
    fig_anio = grafica_totales_por_anio(df)
    fig_rfc = grafica_por_rfc_emisor(df)

    if fig_mes:
        st.plotly_chart(fig_mes, use_container_width=True)
    if fig_anio:
        st.plotly_chart(fig_anio, use_container_width=True)
    if fig_rfc:
        st.plotly_chart(fig_rfc, use_container_width=True)


def pagina_consultar():
    st.title("🔍 Consultar facturas")

    df = cargar_datos()
    if df.empty:
        st.info("No hay facturas registradas todavía.")
        return

    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce", format="mixed")

    emisores = ["Todos"] + sorted(df["rfc_emisor"].dropna().unique().tolist())
    rfc_sel = st.selectbox("Filtrar por RFC emisor", emisores)
    if rfc_sel != "Todos":
        df = df[df["rfc_emisor"] == rfc_sel]

    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Descargar CSV",
        data=csv,
        file_name="reporte_facturas.csv",
        mime="text/csv",
    )


def pagina_reportes():
    st.title("📄 Reportes avanzados y exportación a PDF")

    df = cargar_datos()
    if df.empty:
        st.info("No hay datos para generar reportes.")
        return

    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce", format="mixed")
    df["anio"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month

    st.subheader("Totales por año")
    st.dataframe(df.groupby("anio")["total"].sum().reset_index())

    st.subheader("Totales por año y mes")
    st.dataframe(df.groupby(["anio", "mes"])["total"].sum().reset_index())

    if st.button("📄 Generar reporte PDF"):
        pdf_bytes = generar_reporte_pdf(df)
        st.download_button(
            "⬇️ Descargar reporte en PDF",
            data=pdf_bytes,
            file_name="reporte_gastos.pdf",
            mime="application/pdf",
        )

       st.markdown("---")
    st.subheader("⚠️ Herramientas de Administración")

    if st.button("🧹 Vaciar todas las facturas"):
        try:
            conn = db._get_conn()
            cur = conn.cursor()
            cur.execute("DELETE FROM facturas")
            conn.commit()
            conn.close()
            st.success("Todas las facturas fueron eliminadas correctamente.")
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")


def main():
    st.sidebar.title("Navegación")
    opcion = st.sidebar.radio(
        "Ir a:",
        ["Cargar facturas", "Dashboard", "Consultar facturas", "Reportes avanzados"],
    )

    if opcion == "Cargar facturas":
        pagina_cargar_facturas()
    elif opcion == "Dashboard":
        pagina_dashboard()
    elif opcion == "Consultar facturas":
        pagina_consultar()
    elif opcion == "Reportes avanzados":
        pagina_reportes()


if __name__ == "__main__":
    main()
