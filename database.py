
import sqlite3
from typing import Optional
import pandas as pd

DB_PATH = "facturas.db"


class DatabaseManager:
    def __init__(self, db_path: str = DB_PATH) -> None:
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS facturas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT,
                origen TEXT,
                fecha TEXT,
                rfc_emisor TEXT,
                nombre_emisor TEXT,
                rfc_receptor TEXT,
                nombre_receptor TEXT,
                uso_cfdi TEXT,
                moneda TEXT,
                subtotal REAL,
                impuestos REAL,
                total REAL,
                concepto_principal TEXT
            )"""
        )
        conn.commit()
        conn.close()

    def insertar_factura(self, factura: dict) -> tuple[bool, str]:
        try:
            conn = self._get_conn()
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO facturas
                (uuid, origen, fecha, rfc_emisor, nombre_emisor,
                 rfc_receptor, nombre_receptor, uso_cfdi, moneda,
                 subtotal, impuestos, total, concepto_principal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    factura.get("uuid"),
                    factura.get("origen"),
                    factura.get("fecha"),
                    factura.get("rfc_emisor"),
                    factura.get("nombre_emisor"),
                    factura.get("rfc_receptor"),
                    factura.get("nombre_receptor"),
                    factura.get("uso_cfdi"),
                    factura.get("moneda", "MXN"),
                    factura.get("subtotal", 0.0),
                    factura.get("impuestos", 0.0),
                    factura.get("total", 0.0),
                    factura.get("concepto_principal", ""),
                ),
            )
            conn.commit()
            conn.close()
            return True, "Factura insertada correctamente"
        except Exception as e:  # pragma: no cover
            return False, str(e)

    def obtener_facturas(self) -> pd.DataFrame:
        conn = self._get_conn()
        df = pd.read_sql_query("SELECT * FROM facturas", conn)
        conn.close()
        return df

    def obtener_estadisticas(self) -> dict:
        df = self.obtener_facturas()
        if df.empty:
            return {
                "total_facturas": 0,
                "total_dinero": 0.0,
                "total_impuestos": 0.0,
                "total_emisores": 0,
            }
        return {
            "total_facturas": int(len(df)),
            "total_dinero": float(df["total"].sum()),
            "total_impuestos": float(df["impuestos"].sum()),
            "total_emisores": int(df["rfc_emisor"].nunique()),
        }
