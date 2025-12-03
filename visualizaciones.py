
import pandas as pd
import plotly.express as px


def grafica_totales_por_mes(df):
    if df.empty:
        return None
    
    df = df.copy()
    df["fecha"] = pd.to_datetime(df["fecha"].astype(str).str.replace("T", " "), errors="coerce")

    df["anio"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month

    df = df.dropna(subset=["anio", "mes"])
    df["anio"] = df["anio"].astype(int)
    df["mes"] = df["mes"].astype(int)

    g = df.groupby(["anio", "mes"], as_index=False)["total"].sum()
    g["mes_str"] = g["anio"].astype(str) + "-" + g["mes"].astype(str).str.zfill(2)

    fig = px.bar(g, x="mes_str", y="total", title="Totales por mes")
    return fig




def grafica_totales_por_anio(df):
    if df.empty:
        return None
    
    df = df.copy()
    df["fecha"] = pd.to_datetime(df["fecha"].astype(str).str.replace("T", " "), errors="coerce")

    g = df.groupby(df["fecha"].dt.year)["total"].sum().reset_index()
    g.columns = ["anio", "total"]

    g = g.dropna(subset=["anio"])
    g["anio"] = g["anio"].astype(int)

    fig = px.bar(g, x="anio", y="total", title="Totales por año")
    return fig



def grafica_por_rfc_emisor(df):
    if df.empty:
        return None
    
    g = df.groupby("rfc_emisor")["total"].sum().reset_index()
    fig = px.bar(g, x="rfc_emisor", y="total", title="Totales por RFC emisor")
    return fig
