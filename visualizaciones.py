
import pandas as pd
import plotly.express as px


def grafica_totales_por_mes(df: pd.DataFrame):
    if df.empty:
        return None
    
    df = df.copy()

    df["fecha"] = df["fecha"].astype(str).str.replace("T", " ", regex=False)
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    df["anio"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month
    
    g = df.groupby(["anio", "mes"], as_index=False)["total"].sum()
    g["mes_str"] = g["anio"].astype(str) + "-" + g["mes"].astype(str).str.zfill(2)

    fig = px.bar(
        g,
        x="mes_str",
        y="total",
        title="Totales por mes",
        labels={"mes_str": "Año-Mes", "total": "Total"},
    )
    return fig



def grafica_totales_por_anio(df: pd.DataFrame):
    if df.empty:
        return None
    df = df.copy()
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce", format="mixed")
    g = df.groupby(df["fecha"].dt.year)["total"].sum().reset_index()
    g.columns = ["anio", "total"]
    fig = px.bar(g, x="anio", y="total", title="Totales por año", labels={"anio": "Año", "total": "Total"})
    return fig


def grafica_por_rfc_emisor(df: pd.DataFrame):
    if df.empty:
        return None
    g = df.groupby("rfc_emisor")["total"].sum().reset_index()
    fig = px.bar(g, x="rfc_emisor", y="total", title="Totales por RFC emisor")
    return fig
