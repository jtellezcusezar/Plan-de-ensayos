import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from openpyxl import load_workbook

st.set_page_config(
    page_title="Plan de Ensayos 2026", page_icon="🏗️",
    layout="wide", initial_sidebar_state="collapsed",
)

# ── CONSTANTES ─────────────────────────────────────────────────────────────────
MESES = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
         7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}
ESTADO_MAP = {"*":"Planeado", "0":"No Realizado", "0,5":"Incompleto", "1":"Completo"}
META = 90

CONTROL_AREA_OPTIONS = ["Torre", "Zonas comunes", "Diseño", "Curado", "Producto terminado"]

PRODUCTO_TERMINADO_ENSAYOS = [
    ("Estructura", "Acero", "Ferroscan"),
    ("Estructura", "Pilotaje", "Pruebas Pit"),
    ("Obra Gris", "Muretes", "Resistencia a la Compresión (muros internos)"),
    ("Obra Gris", "Muretes", "Resistencia a la Compresión (fachadas)"),
    ("Obra Gris", "Muretes", "Resistencia a la Compresión (Mamposteria Estructural)"),
    ("Obra Gris", "Acero", "Ferroscan"),
    ("Obra Blanca", "Ascensores", "Certificado de ascensores"),
    ("Obra Blanca", "Puertas Eléctricas", "Certificado de puertas electricas"),
    ("Obra Blanca", "Equipo de Suministro", "Manografo"),
    ("Obra Blanca", "Equipo de Suministro", "Certificado de lavado de tanques"),
    ("Obra Blanca", "Red Contra Incendios", "Hidrostatica"),
    ("Obra Blanca", "Red Contra Incendios", "Apertura maual de valvulas"),
    ("Obra Blanca", "Red Contra Incendios", "Pitometrica"),
    ("Obra Blanca", "Seguridad y Control", "Señalización e iluminacion ruta de evacuación"),
    ("Obra Blanca", "Electrica", "Apantallamiento"),
    ("Obra Blanca", "Barandas", "Prueba de carga baranda"),
    ("Obra Blanca", "Impermeabilización de Cubierta", "Estanqueidad en placas descubiertas"),
    ("Obra Blanca", "Impermeabilización de Fachada", "Tubo Rilem o pipetas de Karsten."),
    ("Obra Blanca", "Impermeabilización de Fachada", "Prueba de Perlado"),
]

PRODUCTO_TERMINADO_CONTROLES = [
    ("Torre", "Estructura", "Control Instalaciones Sanitarias (Estanqueidad)"),
    ("Torre", "Estructura", "Control Instalaciones Sanitarias (Flujo)"),
    ("Torre", "Obra gris y Obra blanca", "Acta de liberacion Pañete"),
    ("Torre", "Obra gris y Obra blanca", "Acta de liberacion Mamposteria"),
    ("Torre", "Obra gris y Obra blanca", "Afinados de pisos"),
    ("Torre", "Obra gris y Obra blanca", "Control Aparatos Sanitarios"),
    ("Torre", "Obra gris y Obra blanca", "Control de pintura"),
    ("Torre", "Producto terminado", "Control instrumentacion pantallas"),
    ("Torre", "Producto terminado", "Actas de liberacion control Niveles placa techo estructura"),
    ("Torre", "Producto terminado", "Control de Asentamiento"),
    ("Torre", "Producto terminado", "Niveles de ruido"),
    ("Torre", "Producto terminado", "Prueba de estanqueidad, Terrazas"),
    ("Torre", "Producto terminado", "Inspección recepción foso de ascensor"),
]

def _rgba(c, alpha):
    c = str(c).strip().lstrip("#")
    if len(c) != 6:
        c = "7BA7D4"
    r, g, b = tuple(int(c[i:i+2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


COLORS = {
    "Planeado": "#7BA7D4",
    "Completo": "#6BBF9E",
    "Incompleto": "#E8C17A",
    "No Realizado": "#D98B8B",
}

BASE_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", size=12),
    margin=dict(t=40, b=10, l=10, r=10),
)

def apply_base(fig, h=300, legend_h=True):
    """Aplica el layout base y la leyenda horizontal (por defecto)."""
    fig.update_layout(
        paper_bgcolor=BASE_LAYOUT["paper_bgcolor"],
        plot_bgcolor=BASE_LAYOUT["plot_bgcolor"],
        font=BASE_LAYOUT["font"],
        margin=BASE_LAYOUT["margin"],
        height=h,
    )
    if legend_h:
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                font=dict(size=11),
            )
        )
    return fig

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');
.stApp,[data-testid="stAppViewContainer"],[data-testid="stAppViewContainer"]>.main {
  --bg: var(--background-color, #F6F8FB);
  --surface: var(--secondary-background-color, #FFFFFF);
  --surface-alt: color-mix(in srgb, var(--secondary-background-color, #FFFFFF) 88%, var(--background-color, #F6F8FB));
  --text: var(--text-color, #111827);
  --muted: color-mix(in srgb, var(--text-color, #111827) 56%, transparent);
  --border: color-mix(in srgb, var(--text-color, #111827) 12%, var(--background-color, #F6F8FB));
  --grid: color-mix(in srgb, var(--text-color, #111827) 8%, var(--background-color, #F6F8FB));
  --hover-bg: color-mix(in srgb, var(--secondary-background-color, #FFFFFF) 90%, var(--background-color, #F6F8FB));
  --accent: var(--primary-color, #4A7BA8);
  --accent-soft: color-mix(in srgb, var(--primary-color, #4A7BA8) 16%, var(--secondary-background-color, #FFFFFF));
  --accent-border: color-mix(in srgb, var(--primary-color, #4A7BA8) 30%, var(--secondary-background-color, #FFFFFF));
  --input-bg: color-mix(in srgb, var(--secondary-background-color, #FFFFFF) 92%, var(--background-color, #F6F8FB));
  --focus-shadow: rgba(123,167,212,.16);
  --scrollbar: color-mix(in srgb, var(--text-color, #111827) 18%, transparent);
  --hm-100-bg: color-mix(in srgb, #6BBF9E 38%, var(--surface));
  --hm-100-text: color-mix(in srgb, #2D6A4F 88%, var(--text));
  --hm-75-bg: color-mix(in srgb, #DDE8B2 50%, var(--surface));
  --hm-75-text: color-mix(in srgb, #667A1E 86%, var(--text));
  --hm-50-bg: color-mix(in srgb, #F4E1A6 56%, var(--surface));
  --hm-50-text: color-mix(in srgb, #A97B12 86%, var(--text));
  --hm-25-bg: color-mix(in srgb, #EEC39F 52%, var(--surface));
  --hm-25-text: color-mix(in srgb, #A45724 86%, var(--text));
  --hm-0-bg: color-mix(in srgb, #D98B8B 44%, var(--surface));
  --hm-0-text: color-mix(in srgb, #8B2B2B 88%, var(--text));
  --hm-na-bg: color-mix(in srgb, var(--surface) 85%, var(--bg));
  --hm-na-text: color-mix(in srgb, var(--text) 36%, transparent);
  --badge-complete-bg: color-mix(in srgb, #6BBF9E 16%, var(--surface));
  --badge-complete-text: color-mix(in srgb, #3D8B6E 88%, var(--text));
  --badge-incomplete-bg: color-mix(in srgb, #E8C17A 18%, var(--surface));
  --badge-incomplete-text: color-mix(in srgb, #C49A3C 88%, var(--text));
  --badge-none-bg: color-mix(in srgb, #D98B8B 18%, var(--surface));
  --badge-none-text: color-mix(in srgb, #B05B5B 88%, var(--text));
  --badge-plan-bg: color-mix(in srgb, var(--primary-color, #4A7BA8) 14%, var(--surface));
  --badge-plan-text: color-mix(in srgb, var(--primary-color, #4A7BA8) 84%, var(--text));
  --ok-bg: color-mix(in srgb, #6BBF9E 14%, var(--surface));
  --ok-border: color-mix(in srgb, #6BBF9E 36%, var(--surface));
  --ok-text: color-mix(in srgb, #3D8B6E 82%, var(--text));
}
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;color:var(--text)!important;}
body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stAppViewContainer"]>.main{background:var(--bg)!important;color:var(--text)!important;}
#MainMenu,footer{visibility:hidden;}
.block-container{padding-top:0!important;max-width:100%!important;padding-left:2rem!important;padding-right:2rem!important;}
[data-testid="stSidebar"]{display:none;}
[data-testid="stToolbar"]{background:transparent!important;}
.app-header{background:var(--surface);border-bottom:1px solid var(--border);padding:14px 32px;display:flex;align-items:center;justify-content:space-between;margin:-1rem -2rem 0 -2rem;position:sticky;top:0;z-index:100;box-shadow:0 1px 10px rgba(2,6,23,.10);}
.logo-box{width:36px;height:36px;background:linear-gradient(135deg,#7BA7D4,#4A7BA8);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;}
.app-title{font-size:16px;font-weight:700;color:var(--text);margin:0;}
.app-sub{font-size:11px;color:var(--muted);font-weight:500;text-transform:uppercase;letter-spacing:.04em;margin:0;}
.hdr-badge{background:var(--accent-soft);color:var(--accent);font-size:12px;font-weight:600;padding:4px 12px;border-radius:20px;border:1px solid var(--accent-border);}
.hdr-date{font-size:12px;color:var(--muted);font-family:'DM Mono',monospace;}
.stTabs [data-baseweb="tab-list"]{background:var(--surface);border-bottom:1px solid var(--border);padding:0;gap:0;margin:0 -2rem;padding-left:2rem;}
.stTabs [data-baseweb="tab"]{font-size:13px!important;font-weight:600!important;color:var(--muted)!important;padding:14px 22px!important;border-bottom:2px solid transparent!important;background:transparent!important;}
.stTabs [aria-selected="true"]{color:var(--accent)!important;border-bottom-color:var(--accent)!important;}
.stTabs [data-baseweb="tab-panel"]{padding-top:24px;}
.stTabs [data-baseweb="tab-highlight"]{display:none;}
.filter-bar{margin-bottom:16px;}
.filter-bar-title{display:none;}
div[data-testid="stSelectbox"]>label,div[data-testid="stTextInput"]>label{font-size:11px!important;font-weight:600!important;color:var(--muted)!important;text-transform:uppercase!important;letter-spacing:.05em!important;margin-bottom:4px!important;}
div[data-testid="stSelectbox"]>div>div,div[data-testid="stTextInput"]>div>input{border-radius:10px!important;border:1.5px solid var(--border)!important;background:var(--input-bg)!important;font-size:13px!important;color:var(--text)!important;}
div[data-testid="stSelectbox"] svg{fill:var(--muted)!important;}
div[data-testid="stSelectbox"]>div>div:focus-within,div[data-testid="stTextInput"]>div>input:focus{border-color:var(--accent)!important;box-shadow:0 0 0 3px var(--focus-shadow)!important;}
.kpi-card{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:18px 20px;position:relative;overflow:hidden;box-shadow:0 1px 4px rgba(15,23,42,.05);transition:transform .15s,box-shadow .15s;}
.kpi-card:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(15,23,42,.08);}
.kpi-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;border-radius:14px 14px 0 0;}
.kp-blue::before{background:#7BA7D4;}.kp-green::before{background:#6BBF9E;}.kp-yellow::before{background:#E8C17A;}.kp-red::before{background:#D98B8B;}.kp-slate::before{background:linear-gradient(90deg,#7BA7D4,#6BBF9E);}
.kpi-icon{font-size:20px;margin-bottom:8px;}.kpi-label{font-size:10px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px;}
.kpi-value{font-size:28px;font-weight:800;line-height:1;font-family:'DM Mono',monospace;margin-bottom:4px;}.kpi-sub{font-size:11px;color:var(--muted);}
.kp-blue .kpi-value{color:#4A7BA8;}.kp-green .kpi-value{color:#3D8B6E;}.kp-yellow .kpi-value{color:#C49A3C;}.kp-red .kpi-value{color:#B05B5B;}.kp-slate .kpi-value{color:var(--accent);}
.section-head{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;margin:0 0 10px 0;padding-bottom:8px;border-bottom:1px solid var(--border);}
.section-title{font-size:15px;font-weight:700;color:var(--text);line-height:1.2;margin:0;}
.section-sub{font-size:11px;color:var(--muted);line-height:1.4;text-align:right;max-width:60%;margin:0;}
.dash-card{background:transparent;border:none;border-radius:0;padding:0;margin-bottom:18px;box-shadow:none;}
.card-title{font-size:14px;font-weight:700;color:var(--text);margin-bottom:2px;}.card-sub{font-size:11px;color:var(--muted);margin-bottom:14px;}
.info-note{padding:9px 14px;background:var(--accent-soft);border:1px solid var(--accent-border);border-radius:10px;font-size:12px;color:var(--accent);font-weight:500;margin-bottom:18px;}
.ok-note{padding:9px 14px;background:var(--ok-bg);border:1px solid var(--ok-border);border-radius:10px;font-size:12px;color:var(--ok-text);font-weight:500;}
.sem-grid{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:20px;}
.sem-card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:14px 18px;min-width:160px;position:relative;overflow:hidden;box-shadow:0 1px 4px rgba(15,23,42,.05);transition:transform .15s;}
.sem-card:hover{transform:translateY(-1px);}
.sem-card::after{content:'';position:absolute;bottom:0;left:0;right:0;height:3px;border-radius:0 0 12px 12px;}
.sv::after{background:#6BBF9E;}.sa::after{background:#E8C17A;}.sr::after{background:#D98B8B;}
.sem-dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:6px;}
.sem-name{font-size:12px;font-weight:700;color:var(--text);margin-bottom:6px;display:flex;align-items:center;}
.sem-tasa{font-size:22px;font-weight:800;font-family:'DM Mono',monospace;}
.sv .sem-tasa{color:#3D8B6E;}.sa .sem-tasa{color:#C49A3C;}.sr .sem-tasa{color:#B05B5B;}
.sem-detail{font-size:11px;color:var(--muted);margin-top:3px;}
.hm-wrap{overflow-x:auto;border-radius:10px;border:1px solid var(--border);}
.hm-table{width:100%;border-collapse:collapse;font-size:12px;}
.hm-table th{background:var(--surface-alt);padding:9px 8px;text-align:center;font-size:10px;font-weight:700;color:var(--muted);text-transform:uppercase;border-bottom:1px solid var(--border);white-space:nowrap;}
.hm-table th.hmp{text-align:left;min-width:160px;padding-left:16px;}
.hm-table td{padding:8px;text-align:center;font-weight:700;font-family:'DM Mono',monospace;border-bottom:1px solid var(--grid);}
.hm-table td.hmpn{text-align:left;font-family:'Inter',sans-serif;font-size:12px;padding-left:16px;color:var(--text);font-weight:600;}
.hm-table tr:last-child td{border-bottom:none;}.hm-table tr:hover td{filter:brightness(.97);}
.h100{background:var(--hm-100-bg);color:var(--hm-100-text);}.h75{background:var(--hm-75-bg);color:var(--hm-75-text);}.h50{background:var(--hm-50-bg);color:var(--hm-50-text);}.h25{background:var(--hm-25-bg);color:var(--hm-25-text);}.h0{background:var(--hm-0-bg);color:var(--hm-0-text);}.hna{background:var(--hm-na-bg);color:var(--hm-na-text);font-family:'Inter',sans-serif;font-weight:500;font-size:11px;}
.badge{display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;}
.bc{background:var(--badge-complete-bg);color:var(--badge-complete-text);}.bi{background:var(--badge-incomplete-bg);color:var(--badge-incomplete-text);}.bn{background:var(--badge-none-bg);color:var(--badge-none-text);}.bp{background:var(--badge-plan-bg);color:var(--badge-plan-text);}
.rt{width:100%;border-collapse:collapse;font-size:13px;}
.rt th{background:var(--surface-alt);padding:10px 14px;text-align:left;font-size:10px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;border-bottom:1px solid var(--border);white-space:nowrap;}
.rt td{padding:10px 14px;border-bottom:1px solid var(--grid);color:var(--muted);}
.rt td:first-child{color:var(--text);font-weight:600;}.rt tr:last-child td{border-bottom:none;}.rt tr:hover td{background:var(--hover-bg);}
.hml{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px;align-items:center;}
.hml span{font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;}
div[data-testid="stDownloadButton"] button{background:var(--accent-soft)!important;color:var(--accent)!important;border:1.5px solid var(--accent-border)!important;border-radius:8px!important;font-size:12px!important;font-weight:600!important;padding:6px 14px!important;}
div[data-testid="stDownloadButton"] button:hover{background:var(--accent)!important;color:#fff!important;}
::-webkit-scrollbar{width:5px;height:5px;}::-webkit-scrollbar-track{background:transparent;}::-webkit-scrollbar-thumb{background:var(--scrollbar);border-radius:3px;}
</style>
""", unsafe_allow_html=True)

# ── DATA ───────────────────────────────────────────────────────────────────────
EXCEL_PATH = Path("Plan_de_ensayos_2026.xlsx")

def read_excel_table(path, table_name):
    """Lee una tabla nombrada de Excel sin depender del nombre de la hoja."""
    wb = load_workbook(path, data_only=True, read_only=False)
    try:
        for ws in wb.worksheets:
            if table_name in ws.tables:
                ref = ws.tables[table_name].ref
                rows = list(ws[ref])
                data = [[cell.value for cell in row] for row in rows]
                headers = data[0]
                values = data[1:]
                return pd.DataFrame(values, columns=headers)
    finally:
        wb.close()
    raise ValueError(f"No se encontró la tabla '{table_name}' en {path}.")

def normalize_text_columns(df):
    """Limpia espacios en columnas de texto."""
    df = df.copy()
    for col in df.columns:
        if pd.api.types.is_object_dtype(df[col]):
            df[col] = df[col].astype(str).str.strip()
    return df

def normalize_status_series(series):
    series = series.astype(str).str.strip()
    return series.replace({
        "0.0": "0",
        "1.0": "1",
        "0.5": "0,5",
        "nan": None,
        "None": None,
        "": None,
    })

def parse_text_value(value):
    if value is None or pd.isna(value):
        return None
    txt = str(value).strip()
    if txt in {"", "None", "nan", "*"}:
        return None
    txt = txt.replace("%", "").replace(",", ".")
    try:
        num = float(txt)
    except ValueError:
        return None
    return num * 100 if 0 <= num <= 1 else num

@st.cache_data
def load_data(file_mtime):
    df_ensayos = read_excel_table(EXCEL_PATH, "Ensayos")
    df_ensayos = df_ensayos.rename(columns={
        "Etapa": "ETAPA",
        "Material": "MATERIAL",
        "Ensayo": "ENSAYO",
        "Frecuencia": "FRECUENCIA",
        "Valor": "Cantidad",
    })
    df_ensayos = normalize_text_columns(df_ensayos)

    df_controles = read_excel_table(EXCEL_PATH, "Controles")
    df_controles = normalize_text_columns(df_controles)
    if "Valor" in df_controles.columns:
        df_controles["Valor"] = normalize_status_series(df_controles["Valor"])
        df_controles["Valor_num"] = pd.to_numeric(
            df_controles["Valor"].replace({"0,5": "0.5", "*": None}),
            errors="coerce"
        )

    df_ensayos["Cantidad"] = normalize_status_series(df_ensayos["Cantidad"])
    df_ensayos["MesNombre"]    = df_ensayos["Mes"].map(MESES)
    df_ensayos["Estado"]       = df_ensayos["Cantidad"].map(lambda x: ESTADO_MAP.get(x, str(x)))
    df_ensayos["EsEjecutado"]  = df_ensayos["Cantidad"] != "*"
    df_ensayos["Cantidad_num"] = pd.to_numeric(
        df_ensayos["Cantidad"].replace({"0,5": "0.5", "*": None}),
        errors="coerce"
    )
    return df_ensayos, df_controles

df_full, df_controles = load_data(EXCEL_PATH.stat().st_mtime)
meses_con_datos = sorted(df_full[df_full["EsEjecutado"]]["Mes"].unique().tolist())
mes_label = " – ".join([MESES[meses_con_datos[0]], MESES[meses_con_datos[-1]]]) if len(meses_con_datos) > 1 else MESES[meses_con_datos[0]]
MES_ACTUAL = datetime.now(ZoneInfo("America/Bogota")).month
MESES_VENCIDOS = list(range(1, MES_ACTUAL))
meses_vencidos_label = "Sin meses vencidos" if not MESES_VENCIDOS else (
    MESES[MESES_VENCIDOS[0]] if len(MESES_VENCIDOS) == 1
    else f"{MESES[MESES_VENCIDOS[0]]} – {MESES[MESES_VENCIDOS[-1]]}"
)

ALL_P   = ["Todos"] + sorted(df_full["Proyecto"].unique().tolist())
ALL_E   = ["Todas"] + sorted(df_full["ETAPA"].unique().tolist())
ALL_M   = ["Todos"] + list(MESES.values())
ALL_MAT = ["Todos"] + sorted(df_full["MATERIAL"].unique().tolist())
ALL_EST = ["Todos"] + list(ESTADO_MAP.values())
all_ciudades = set()
if "Ciudad" in df_controles.columns:
    all_ciudades.update(df_controles["Ciudad"].dropna().tolist())
if "Ciudad" in df_full.columns:
    all_ciudades.update(df_full["Ciudad"].dropna().tolist())
ALL_CIUD = ["Todas"] + sorted(all_ciudades)

all_proyectos_controles = set()
if "Proyecto" in df_controles.columns:
    all_proyectos_controles.update(df_controles["Proyecto"].dropna().tolist())
if "Proyecto" in df_full.columns:
    all_proyectos_controles.update(df_full["Proyecto"].dropna().tolist())
ALL_PC = ["Todos"] + sorted(all_proyectos_controles)

# ── HELPERS ────────────────────────────────────────────────────────────────────
def kpi(icon, label, value, sub, css):
    return (f'<div class="kpi-card {css}"><div class="kpi-icon">{icon}</div>'
            f'<div class="kpi-label">{label}</div><div class="kpi-value">{value}</div>'
            f'<div class="kpi-sub">{sub}</div></div>')

def section_header(title, subtitle=""):
    subtitle_html = f'<div class="section-sub">{subtitle}</div>' if subtitle else ""
    return (
        f'<div class="section-head">'
        f'<div class="section-title">{title}</div>'
        f'{subtitle_html}'
        f'</div>'
    )

def get_kpis(df):
    ex   = df[df["EsEjecutado"]]
    comp = int((ex["Cantidad_num"] == 1).sum())
    inc  = int((ex["Cantidad_num"] == 0.5).sum())
    no_r = int((ex["Cantidad_num"] == 0).sum())
    plan = int(len(df))
    pend = int((df["Cantidad"] == "*").sum())
    tot  = comp + inc + no_r
    tasa = round((comp + inc * 0.5) / tot * 100, 1) if tot > 0 else 0.0
    return comp, inc, no_r, plan, pend, tot, tasa

def filt(df, col, val, empty_val):
    return df if val == empty_val else df[df[col] == val]

def filt_mes(df, val):
    if val == "Todos": return df
    return df[df["Mes"].isin([k for k, v in MESES.items() if v == val])]

def hm_cls(t):
    if t >= 90: return "h100"
    if t >= 70: return "h75"
    if t >= 50: return "h50"
    if t >= 25: return "h25"
    return "h0"

def heatmap_legend():
    return f"""<div class="hml">
      <span style="background:var(--hm-100-bg);color:var(--hm-100-text);">≥ 90%</span>
      <span style="background:var(--hm-75-bg);color:var(--hm-75-text);">70–89%</span>
      <span style="background:var(--hm-50-bg);color:var(--hm-50-text);">50–69%</span>
      <span style="background:var(--hm-25-bg);color:var(--hm-25-text);">25–49%</span>
      <span style="background:var(--hm-0-bg);color:var(--hm-0-text);">&lt; 25%</span>
      <span style="background:var(--hm-na-bg);color:var(--hm-na-text);">Sin datos</span>
      <span style="font-size:11px;color:var(--muted);margin-left:4px;">· Meta: {META}%</span>
    </div>"""

def render_heatmap_table(first_col_label, rows_data):
    col_values = {m: [] for m in range(12)}
    body_rows = []

    for row in rows_data:
        row_vals = [v for v in row["values"] if v is not None]
        row_avg = round(sum(row_vals) / len(row_vals), 1) if row_vals else None
        row_html = [f'<tr><td class="hmpn">{row["label"]}</td>']
        for idx, val in enumerate(row["values"]):
            if val is None:
                row_html.append('<td class="hna">—</td>')
            else:
                col_values[idx].append(val)
                title = row.get("titles", [None] * 12)[idx]
                title_attr = f' title="{title}"' if title else ""
                row_html.append(f'<td class="{hm_cls(val)}"{title_attr}>{val:.0f}%</td>')
        if row_avg is None:
            row_html.append('<td class="hna"><strong>—</strong></td>')
        else:
            row_html.append(f'<td class="{hm_cls(row_avg)}" title="Promedio de la fila"><strong>{row_avg:.0f}%</strong></td>')
        row_html.append("</tr>")
        body_rows.append("".join(row_html))

    avg_row = ['<tr><td class="hmpn"><strong>Promedio</strong></td>']
    avg_row_values = []
    for idx in range(12):
        vals = col_values[idx]
        if vals:
            avg_val = round(sum(vals) / len(vals), 1)
            avg_row_values.append(avg_val)
            avg_row.append(f'<td class="{hm_cls(avg_val)}" title="Promedio de la columna"><strong>{avg_val:.0f}%</strong></td>')
        else:
            avg_row.append('<td class="hna"><strong>—</strong></td>')
    grand_vals = [v for v in avg_row_values if v is not None]
    if grand_vals:
        grand_avg = round(sum(grand_vals) / len(grand_vals), 1)
        avg_row.append(f'<td class="{hm_cls(grand_avg)}" title="Promedio general"><strong>{grand_avg:.0f}%</strong></td>')
    else:
        avg_row.append('<td class="hna"><strong>—</strong></td>')
    avg_row.append("</tr>")
    body_rows.append("".join(avg_row))

    ths = "".join(f"<th>{MESES[m][:3]}</th>" for m in range(1, 13))
    ths += "<th>Prom.</th>"
    return (
        f'<div class="hm-wrap"><table class="hm-table"><thead><tr><th class="hmp">{first_col_label}</th>{ths}</tr></thead>'
        f'<tbody>{"".join(body_rows)}</tbody></table></div>'
    )

def badge(estado):
    m = {"Completo":("bc","✅"), "Incompleto":("bi","⚠️"),
         "No Realizado":("bn","❌"), "Planeado":("bp","🔵")}
    cls, ico = m.get(estado, ("bp","🔵"))
    return f'<span class="badge {cls}">{ico} {estado}</span>'

def sem_card(name, tasa, ej, crit):
    cls = "sv" if tasa >= META else "sa" if tasa >= META * 0.6 else "sr"
    dot = COLORS["Completo"] if tasa >= META else COLORS["Incompleto"] if tasa >= META * 0.6 else COLORS["No Realizado"]
    return (f'<div class="sem-card {cls}"><div class="sem-name">'
            f'<span class="sem-dot" style="background:{dot}"></span>{name}</div>'
            f'<div class="sem-tasa">{tasa:.1f}%</div>'
            f'<div class="sem-detail">{ej} ejecutables · {crit} crítico{"s" if crit!=1 else ""}</div></div>')

def bar_col(t):
    return COLORS["Completo"] if t >= META else COLORS["Incompleto"] if t >= META * 0.6 else COLORS["No Realizado"]

def control_area_title(area):
    return {
        "Torre": "Control de Torres",
        "Zonas comunes": "Control de Zonas Comunes",
        "Diseño": "Control de Diseño",
        "Curado": "Control de Curado",
        "Producto terminado": "Control de Producto Terminado",
    }.get(area, f"Control de {area}")

def control_area_mask(df, area):
    if area == "Curado":
        return (df["Area"] == "-") & (df["Control"] == "Curado")
    if area == "Producto terminado":
        return pd.Series([False] * len(df), index=df.index)
    if area == "Torre":
        return (df["Area"] == area) & (~df["Etapa"].astype(str).str.contains("Producto terminado", case=False, na=False))
    return df["Area"] == area

def control_row_label(row):
    etapa = str(row.get("Etapa", "")).strip()
    control = str(row.get("Control", "")).strip()
    if not etapa or etapa in {"-", "nan", "None"}:
        return control
    return f"{etapa} - {control}"

def build_heatmap_rows(df_ctrl, df_ens, area):
    rows = []
    ctrl_filtered = df_ctrl[control_area_mask(df_ctrl, area)].copy()
    if area == "Producto terminado":
        proyectos_ens = set()
        for etapa, material, ensayo in PRODUCTO_TERMINADO_ENSAYOS:
            mask = (
                (df_ens["ETAPA"] == etapa) &
                (df_ens["MATERIAL"] == material) &
                (df_ens["ENSAYO"] == ensayo)
            )
            proyectos_ens.update(df_ens.loc[mask, "Proyecto"].dropna().tolist())

        proyectos_ctrl = set()
        for area_v, etapa_v, control_v in PRODUCTO_TERMINADO_CONTROLES:
            mask = (
                (df_ctrl["Area"] == area_v) &
                (df_ctrl["Etapa"] == etapa_v) &
                (df_ctrl["Control"] == control_v)
            )
            proyectos_ctrl.update(df_ctrl.loc[mask, "Proyecto"].dropna().tolist())

        proyectos = sorted(proyectos_ens | proyectos_ctrl)
    else:
        proyectos = sorted(
            set(ctrl_filtered["Proyecto"].dropna().tolist()) |
            set(df_ens["Proyecto"].dropna().tolist())
        )

    for proyecto in proyectos:
        ctrl_proy = ctrl_filtered[ctrl_filtered["Proyecto"] == proyecto]
        ens_parts = []
        ctrl_parts = []
        if area == "Producto terminado":
            for etapa, material, ensayo in PRODUCTO_TERMINADO_ENSAYOS:
                mask = (
                    (df_ens["Proyecto"] == proyecto) &
                    (df_ens["ETAPA"] == etapa) &
                    (df_ens["MATERIAL"] == material) &
                    (df_ens["ENSAYO"] == ensayo)
                )
                ens_parts.append(df_ens.loc[mask, ["Mes", "Cantidad_num"]].rename(columns={"Cantidad_num": "Valor_num"}))

            for area_v, etapa_v, control_v in PRODUCTO_TERMINADO_CONTROLES:
                mask = (
                    (df_ctrl["Proyecto"] == proyecto) &
                    (df_ctrl["Area"] == area_v) &
                    (df_ctrl["Etapa"] == etapa_v) &
                    (df_ctrl["Control"] == control_v)
                )
                ctrl_parts.append(df_ctrl.loc[mask, ["Mes", "Valor_num"]])

        extras = pd.concat(ens_parts + ctrl_parts, ignore_index=True) if (ens_parts or ctrl_parts) else pd.DataFrame(columns=["Mes", "Valor_num"])
        values = []
        titles = []

        for m in range(1, 13):
            vals_ctrl = ctrl_proy.loc[ctrl_proy["Mes"] == m, "Valor_num"].dropna()
            vals_extra = extras.loc[extras["Mes"] == m, "Valor_num"].dropna()
            vals = pd.concat([vals_ctrl, vals_extra], ignore_index=True)
            if area == "Curado":
                raw_vals = ctrl_proy.loc[ctrl_proy["Mes"] == m, "Valor"].dropna()
                parsed_vals = [parse_text_value(v) for v in raw_vals]
                parsed_vals = [v for v in parsed_vals if v is not None]
                if not parsed_vals:
                    values.append(None)
                    titles.append(None)
                    continue
                t = round(parsed_vals[-1], 1)
                values.append(t)
                titles.append("Valor registrado")
            elif vals.empty:
                values.append(None)
                titles.append(None)
            else:
                t = round(vals.mean() * 100, 1)
                values.append(t)
                titles.append(f"Promedio de {len(vals)} valores")
        rows.append({"label": proyecto, "values": values, "titles": titles})

    return rows

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="height:28px"></div>
<div class="app-header">
  <div style="display:flex;align-items:center;gap:12px;">
    <div class="logo-box">🏗️</div>
    <div><p class="app-title">Plan de Ensayos 2026</p>
         <p class="app-sub">Panel de Control de Calidad · Cusezar</p></div>
  </div>
  <div style="display:flex;align-items:center;gap:14px;">
    <span class="hdr-badge">{df_full['Proyecto'].nunique()} Proyectos · {len(df_full):,} Ensayos</span>
    <span class="hdr-date">Datos hasta: {mes_label}</span>
  </div>
</div><div style="height:8px"></div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊  Resumen General",
    "🏗️  Por Proyecto y Material",
    "📅  Línea de Tiempo y Alertas",
    "🔍  Consulta de Ensayos",
    "🛠️  Controles",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    c1, c2, c3 = st.columns(3)
    sel_proy  = c1.selectbox("Proyecto", ALL_P,  key="t1p")
    sel_etapa = c2.selectbox("Etapa",    ALL_E,  key="t1e")
    sel_mes   = c3.selectbox("Mes",      ALL_M,  key="t1m")

    df1 = filt(filt(filt_mes(df_full, sel_mes), "ETAPA", sel_etapa, "Todas"), "Proyecto", sel_proy, "Todos")

    st.markdown(
        f'<div class="info-note">ℹ️ Cumplimiento calculado sobre datos ejecutados '
        f'(<strong>{mes_label} 2026</strong>). Planeados (*) excluidos. Meta: <strong>{META}%</strong></div>',
        unsafe_allow_html=True)

    comp, inc, no_r, plan, pend, tot, tasa = get_kpis(df1)
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.markdown(kpi("📋","Planeados",         f"{plan:,}", f"Pendientes: {pend:,}",                              "kp-blue"),   unsafe_allow_html=True)
    k2.markdown(kpi("✅","Completos",         f"{comp:,}", f"{comp/tot*100:.1f}% del ejecutable" if tot else "—","kp-green"),  unsafe_allow_html=True)
    k3.markdown(kpi("⚠️","Incompletos",       f"{inc:,}",  f"{inc/tot*100:.1f}% del ejecutable"  if tot else "—","kp-yellow"), unsafe_allow_html=True)
    k4.markdown(kpi("❌","No Realizados",     f"{no_r:,}", f"{no_r/tot*100:.1f}% del ejecutable" if tot else "—","kp-red"),    unsafe_allow_html=True)
    k5.markdown(kpi("📈","Tasa Cumplimiento", f"{tasa}%",  f"Meta: ≥ {META}%",                                  "kp-slate"),  unsafe_allow_html=True)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Donut ──
    d1, d2 = st.columns([1, 1.5])
    with d1:
        st.markdown(section_header("Distribución por Estado", "Total de registros en el plan"), unsafe_allow_html=True)
        st.markdown('<div class="dash-card">', unsafe_allow_html=True)
        ec = df1["Estado"].value_counts().reset_index()
        ec.columns = ["Estado","n"]
        ec["C"] = ec["Estado"].map(COLORS)
        fig_donut = go.Figure(go.Pie(
            labels=ec["Estado"], values=ec["n"], hole=0.58,
            marker_colors=ec["C"].tolist(),
            textinfo="percent",
            textposition="outside",
            insidetextorientation="horizontal",
            hovertemplate="<b>%{label}</b><br>%{value:,} · %{percent}<extra></extra>",
        ))
        # Aplicar layout sin legend primero, luego agregar legend vertical y annotations
        apply_base(fig_donut, h=270, legend_h=False)
        fig_donut.update_layout(
            showlegend=True,
            legend=dict(orientation="v", x=1.02, y=0.5, font=dict(size=12)),
            annotations=[dict(text=f"<b>{len(df1):,}</b>", x=0.5, y=0.5,
                              font_size=16, showarrow=False)],
        )
        st.plotly_chart(fig_donut, use_container_width=True, theme="streamlit", config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Barras por proyecto ──
    with d2:
        st.markdown(section_header("Avance por Proyecto", "Proyectos con ensayos ejecutados · ordenado por tasa de cumplimiento"), unsafe_allow_html=True)
        st.markdown('<div class="dash-card">', unsafe_allow_html=True)
        ex1 = df1[df1["EsEjecutado"] & (df1["Estado"] != "Planeado")]
        if not ex1.empty:
            orden = (ex1.groupby("Proyecto")
                       .apply(lambda g: (((g["Cantidad_num"] == 1).sum()) + ((g["Cantidad_num"] == 0.5).sum() * 0.5)) / len(g) * 100)
                       .sort_values().index.tolist())
            pg = ex1.groupby(["Proyecto","Estado"])["Cantidad_num"].count().reset_index()
            pg.columns = ["Proyecto","Estado","n"]
            fig_proy = px.bar(pg, x="n", y="Proyecto", color="Estado",
                              orientation="h", barmode="stack",
                              color_discrete_map=COLORS,
                              category_orders={"Proyecto": orden,
                                               "Estado": ["No Realizado","Incompleto","Completo"]})
            fig_proy.update_traces(hovertemplate="<b>%{y}</b><br>%{data.name}: %{x}<extra></extra>",
                                   marker_line_width=0)
            apply_base(fig_proy, h=270)
            fig_proy.update_layout(xaxis=dict(title=""),
                                   yaxis=dict(title="", gridwidth=0))
            st.plotly_chart(fig_proy, use_container_width=True, theme="streamlit", config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Línea temporal ──
    st.markdown(section_header("Ensayos por Mes — 2026", "Líneas sólidas = ejecutados por estado · Punteada = total planeado del mes · Curva suavizada"), unsafe_allow_html=True)
    st.markdown('<div class="dash-card">', unsafe_allow_html=True)
    mp = (df1.groupby("Mes").size()
            .reindex(range(1,13), fill_value=0).reset_index())
    mp.columns = ["Mes","n"]
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=mp["Mes"].map(lambda m: MESES[m]), y=mp["n"],
        name="Plan del mes", mode="lines+markers",
        line=dict(color=COLORS["Planeado"], width=2, dash="dot", shape="spline", smoothing=0.8),
        marker=dict(size=6),
        hovertemplate="<b>%{x}</b><br>Plan del mes: %{y}<extra></extra>",
    ))
    fill_map_line = {
        "Completo": _rgba(COLORS["Completo"], 0.18),
        "Incompleto": None,
        "No Realizado": None,
    }
    for est, fc in [("Completo", fill_map_line["Completo"]), ("Incompleto", fill_map_line["Incompleto"]), ("No Realizado", fill_map_line["No Realizado"])]:
        sub = (df1[df1["EsEjecutado"] & (df1["Estado"]==est)]
                 .groupby("Mes").size()
                 .reindex(meses_con_datos, fill_value=0).reset_index())
        sub.columns = ["Mes","n"]
        fig_line.add_trace(go.Scatter(
            x=sub["Mes"].map(lambda m: MESES[m]), y=sub["n"],
            name=est, mode="lines+markers",
            line=dict(color=COLORS[est], width=2.5, shape="spline", smoothing=1.0),
            marker=dict(size=8, line=dict(color="white", width=1.5)),
            fill="tozeroy" if est == "Completo" else None, fillcolor=fc,
            hovertemplate=f"<b>%{{x}}</b><br>{est}: %{{y}}<extra></extra>",
        ))
    apply_base(fig_line, h=295)
    fig_line.update_layout(xaxis=dict(), yaxis=dict())
    st.plotly_chart(fig_line, use_container_width=True, theme="streamlit", config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    f2a, f2b, f2c = st.columns(3)
    sel2_proy  = f2a.selectbox("Proyecto", ALL_P,   key="t2p")
    sel2_etapa = f2b.selectbox("Etapa",    ALL_E,   key="t2e")
    sel2_mat   = f2c.selectbox("Material", ALL_MAT, key="t2m")

    df2 = filt(filt(filt(df_full, "Proyecto", sel2_proy, "Todos"), "ETAPA", sel2_etapa, "Todas"), "MATERIAL", sel2_mat, "Todos")
    ex2 = df2[df2["EsEjecutado"]].copy()

    # ── Heatmap ──
    st.markdown(section_header('Heatmap de Cumplimiento — Proyecto × Mes', 'Tasa = promedio de valores ejecutados (0, 0.5, 1). "Plan." = sin datos ejecutados ese mes.'), unsafe_allow_html=True)
    st.markdown('<div class="dash-card">', unsafe_allow_html=True)
    st.markdown(heatmap_legend(), unsafe_allow_html=True)

    rows_hm = []
    for p in sorted(df2["Proyecto"].unique()):
        values = []
        titles = []
        for m in range(1, 13):
            sub_hm = ex2[(ex2["Proyecto"]==p) & (ex2["Mes"]==m)]
            if len(sub_hm) == 0:
                has_plan = len(df2[(df2["Proyecto"]==p) & (df2["Mes"]==m) & (df2["Cantidad"]=="*")]) > 0
                values.append(None)
                titles.append("Plan." if has_plan else None)
            else:
                cn = int((sub_hm["Cantidad_num"]==1).sum())
                iN = int((sub_hm["Cantidad_num"]==0.5).sum())
                nn = int((sub_hm["Cantidad_num"]==0).sum())
                prom = sub_hm["Cantidad_num"].mean()
                t = round(prom * 100, 1) if pd.notna(prom) else 0.0
                values.append(t)
                titles.append(f"{cn} compl. · {iN} incompl. · {nn} no-real · Promedio: {prom:.2f}")
        rows_hm.append({"label": p, "values": values, "titles": titles})

    st.markdown(render_heatmap_table("Proyecto", rows_hm), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Tasa por proyecto ──
    st.markdown(section_header("Tasa de Cumplimiento por Proyecto", f"% de completos sobre el total planeado en meses vencidos ({meses_vencidos_label}) · Meta: {META}%"), unsafe_allow_html=True)
    st.markdown('<div class="dash-card">', unsafe_allow_html=True)
    if not df2.empty:
        t_df = (df2.groupby("Proyecto")
                   .apply(lambda g: pd.Series({
                       "tasa": round((((g["Cantidad_num"] == 1).sum()) + ((g["Cantidad_num"] == 0.5).sum() * 0.5)) / len(g[g["Mes"].isin(MESES_VENCIDOS)]) * 100, 1)
                               if len(g[g["Mes"].isin(MESES_VENCIDOS)]) > 0 else 0.0,
                       "comp": int((g["Cantidad_num"] == 1).sum()),
                       "inc": int((g["Cantidad_num"] == 0.5).sum()),
                       "no_r": int((g["Cantidad_num"] == 0).sum()),
                       "tot": len(g[g["Mes"].isin(MESES_VENCIDOS)]),
                   }))
                   .reset_index()
                   .sort_values("tasa", ascending=False))
        fig_tasa = go.Figure(go.Bar(
            x=t_df["tasa"], y=t_df["Proyecto"],
            orientation="h",
            marker_color=[bar_col(t) for t in t_df["tasa"]],
            marker_line_width=0,
            text=t_df["tasa"].map(lambda t: f"{t:.1f}%"),
            textposition="outside",
            textfont=dict(size=11),
            customdata=t_df[["comp", "inc", "no_r", "tot"]].values,
            hovertemplate="<b>%{y}</b><br>Cumplimiento: %{x:.1f}%<br>Completos: %{customdata[0]}<br>Incompletos: %{customdata[1]}<br>No realizados: %{customdata[2]}<br>Total plan meses vencidos: %{customdata[3]}<extra></extra>",
        ))
        fig_tasa.add_vline(x=META, line_dash="dot", line_color=COLORS["Planeado"], line_width=1.5,
                           annotation_text=f"Meta {META}%",
                           annotation_position="top right")
        apply_base(fig_tasa, h=340, legend_h=False)
        fig_tasa.update_layout(
            showlegend=False,
            xaxis=dict(range=[0,115], ticksuffix="%", title=""),
            yaxis=dict(gridwidth=0, title=""),
        )
        st.plotly_chart(fig_tasa, use_container_width=True, theme="streamlit", config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    f3a, f3b = st.columns([2, 1])
    sel3_proy = f3a.selectbox("Proyecto",      ALL_P,  key="t3p")
    sel3_mes  = f3b.selectbox("Mes con datos", ["Todos"] + [MESES[m] for m in meses_con_datos], key="t3m")

    df3 = filt(df_full, "Proyecto", sel3_proy, "Todos")
    sm3 = meses_con_datos if sel3_mes == "Todos" else [k for k, v in MESES.items() if v == sel3_mes]

    # Semáforo
    tasa3 = (df3[df3["EsEjecutado"]]
               .groupby("Proyecto")
               .apply(lambda g: pd.Series({
                   "tasa": round((((g["Cantidad_num"] == 1).sum()) + ((g["Cantidad_num"] == 0.5).sum() * 0.5)) / len(g) * 100, 1) if len(g) > 0 else 0.0,
                   "ej":   len(g),
                   "crit": int((g["Cantidad_num"]==0).sum()),
               }))
               .reset_index())

    st.markdown(f"### Semáforo por Proyecto")
    st.markdown(f"Cumplimiento global · 🟢 ≥{META}%  🟡 {int(META*.6)}–{META-1}%  🔴 <{int(META*.6)}%")
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div class="sem-grid">' +
        "".join(sem_card(r.Proyecto, r.tasa, int(r.ej), int(r.crit))
                for _, r in tasa3.sort_values("tasa", ascending=False).iterrows()) +
        "</div>",
        unsafe_allow_html=True)

    # Área acumulada
    st.markdown(section_header("Evolución Acumulada por Estado", "Progresión mensual · curvas suavizadas"), unsafe_allow_html=True)
    st.markdown('<div class="dash-card">', unsafe_allow_html=True)
    rows_a = []
    for m in sorted(sm3):
        sub_m = df3[df3["EsEjecutado"] & (df3["Mes"] == m)]
        rows_a.append({"Mes": MESES[m],
                        "Completo":     int((sub_m["Cantidad_num"]==1).sum()),
                        "Incompleto":   int((sub_m["Cantidad_num"]==0.5).sum()),
                        "No Realizado": int((sub_m["Cantidad_num"]==0).sum())})
    adf = pd.DataFrame(rows_a)
    if not adf.empty:
        for c_ in ["Completo","Incompleto","No Realizado"]:
            adf[f"{c_}_ac"] = adf[c_].cumsum()
        fig_area = go.Figure()
        fill_map_area = {
            "Completo": _rgba(COLORS["Completo"], 0.18),
            "Incompleto": _rgba(COLORS["Incompleto"], 0.14),
            "No Realizado": _rgba(COLORS["No Realizado"], 0.12),
        }
        for est, fc in [("Completo", fill_map_area["Completo"]),
                         ("Incompleto", fill_map_area["Incompleto"]),
                         ("No Realizado", fill_map_area["No Realizado"])]:
            fig_area.add_trace(go.Scatter(
                x=adf["Mes"], y=adf[f"{est}_ac"],
                name=f"{est} (acum.)", mode="lines+markers",
                line=dict(color=COLORS[est], width=2.5, shape="spline", smoothing=1.0),
                marker=dict(size=8, line=dict(color="white", width=1.5)),
                fill="tozeroy", fillcolor=fc,
                hovertemplate=f"<b>%{{x}}</b><br>{est} acum.: %{{y}}<extra></extra>",
            ))
        apply_base(fig_area, h=300)
        fig_area.update_layout(xaxis=dict(), yaxis=dict())
        st.plotly_chart(fig_area, use_container_width=True, theme="streamlit", config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

    # Tabla críticos
    st.markdown(section_header("🚨 Ensayos Críticos — No Realizados", "Ensayos con valor = 0 en el período analizado"), unsafe_allow_html=True)
    st.markdown('<div class="dash-card">', unsafe_allow_html=True)
    crit_df = df3[
        df3["EsEjecutado"] & (df3["Cantidad_num"] == 0) & df3["Mes"].isin(sm3)
    ][["Proyecto","ETAPA","MATERIAL","ENSAYO","NTC","MesNombre","Estado"]].copy()
    crit_df.columns = ["Proyecto","Etapa","Material","Ensayo","NTC","Mes","Estado"]
    if not crit_df.empty:
        col_dl, _ = st.columns([1, 5])
        with col_dl:
            st.download_button("⬇ Exportar CSV",
                               crit_df.to_csv(index=False).encode("utf-8"),
                               "ensayos_criticos.csv", "text/csv", key="dl3")
        rows_t = "".join(
            f"<tr><td>{r.Proyecto}</td><td>{r.Etapa}</td><td>{r.Material}</td>"
            f"<td>{r.Ensayo}</td><td>{r.NTC}</td><td>{r.Mes}</td><td>{badge(r.Estado)}</td></tr>"
            for _, r in crit_df.iterrows())
        st.markdown(
            f'<div style="overflow-x:auto;border-radius:10px;border:1px solid var(--border);">'
            f'<table class="rt"><thead><tr><th>Proyecto</th><th>Etapa</th><th>Material</th>'
            f'<th>Ensayo</th><th>NTC</th><th>Mes</th><th>Estado</th></tr></thead>'
            f'<tbody>{rows_t}</tbody></table></div>',
            unsafe_allow_html=True)
    else:
        st.markdown('<div class="ok-note">✅ No hay ensayos sin realizar en el período seleccionado.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 🔍 Consulta de Ensayos")
    st.markdown("Filtra y encuentra exactamente qué ensayos aplican según proyecto, mes y material.")
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    q1, q2, q3 = st.columns(3)
    sel4_proy  = q1.selectbox("Proyecto",  ALL_P,   key="t4p")
    sel4_etapa = q1.selectbox("Etapa",     ALL_E,   key="t4e")
    sel4_mes   = q2.selectbox("Mes",       ALL_M,   key="t4m")
    sel4_mat   = q2.selectbox("Material",  ALL_MAT, key="t4mat")
    sel4_est   = q3.selectbox("Estado",    ALL_EST, key="t4est")
    buscar     = q3.text_input("🔎 Buscar por nombre de ensayo",
                               placeholder="Ej: resistencia, fraguado, granulometría...")

    df4 = filt(filt(filt_mes(filt(filt(filt(df_full,
        "Proyecto", sel4_proy, "Todos"),
        "ETAPA", sel4_etapa, "Todas"),
        "MATERIAL", sel4_mat, "Todos"),
        sel4_mes),
        "Estado", sel4_est, "Todos"),
        "Proyecto", sel4_proy, "Todos")  # already applied but safe
    # cleaner re-apply
    df4 = df_full.copy()
    if sel4_proy  != "Todos": df4 = df4[df4["Proyecto"] == sel4_proy]
    if sel4_etapa != "Todas": df4 = df4[df4["ETAPA"]    == sel4_etapa]
    if sel4_mes   != "Todos": df4 = df4[df4["Mes"].isin([k for k,v in MESES.items() if v == sel4_mes])]
    if sel4_mat   != "Todos": df4 = df4[df4["MATERIAL"] == sel4_mat]
    if sel4_est   != "Todos": df4 = df4[df4["Estado"]   == sel4_est]
    if buscar:                df4 = df4[df4["ENSAYO"].str.contains(buscar, case=False, na=False)]

    comp4, inc4, no4, plan4, pend4, tot4, tasa4 = get_kpis(df4)
    a, b, c_, d, e = st.columns(5)
    a.markdown(kpi("🔍","Resultados",    f"{len(df4):,}", "registros","kp-slate"),  unsafe_allow_html=True)
    b.markdown(kpi("📋","Planeados",     f"{plan4:,}",    f"Pendientes: {pend4:,}", "kp-blue"),   unsafe_allow_html=True)
    c_.markdown(kpi("✅","Completos",    f"{comp4:,}",    "",          "kp-green"),  unsafe_allow_html=True)
    d.markdown(kpi("⚠️","Incompletos",   f"{inc4:,}",     "",          "kp-yellow"), unsafe_allow_html=True)
    e.markdown(kpi("❌","No Realizados", f"{no4:,}",      "",          "kp-red"),    unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    st.markdown(section_header("Resultados de la Consulta"), unsafe_allow_html=True)
    st.markdown('<div class="dash-card">', unsafe_allow_html=True)

    if not df4.empty:
        disp = df4[["Proyecto","ETAPA","MATERIAL","ENSAYO","NTC","FRECUENCIA","MesNombre","Estado"]].copy()
        disp.columns = ["Proyecto","Etapa","Material","Ensayo","NTC","Frecuencia","Mes","Estado"]
        col_dl4, _ = st.columns([1, 5])
        with col_dl4:
            st.download_button("⬇ Descargar CSV",
                               disp.to_csv(index=False).encode("utf-8"),
                               "consulta_ensayos.csv", "text/csv", key="dl4")
        prev = disp.head(50)
        rows4 = "".join(
            f"<tr><td>{r.Proyecto}</td><td>{r.Etapa}</td><td>{r.Material}</td>"
            f"<td>{r.Ensayo}</td><td>{r.NTC}</td>"
            f"<td style='max-width:180px;white-space:normal;font-size:11px;color:var(--muted)'>{r.Frecuencia}</td>"
            f"<td>{r.Mes}</td><td>{badge(r.Estado)}</td></tr>"
            for _, r in prev.iterrows())
        st.markdown(f'<div class="card-sub">Mostrando {min(50,len(disp))} de {len(disp):,} registros.</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div style="overflow-x:auto;border-radius:10px;border:1px solid var(--border);max-height:480px;overflow-y:auto;">'
            f'<table class="rt"><thead><tr><th>Proyecto</th><th>Etapa</th><th>Material</th>'
            f'<th>Ensayo</th><th>NTC</th><th>Frecuencia</th><th>Mes</th><th>Estado</th></tr></thead>'
            f'<tbody>{rows4}</tbody></table></div>',
            unsafe_allow_html=True)
    else:
        st.info("ℹ️ No se encontraron ensayos con los filtros aplicados.")
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("### 🛠️ Controles")
    st.markdown("Consulta el avance mensual de controles por ciudad, proyecto y tipo de control.")
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    c5a, c5b, c5c = st.columns(3)
    sel5_ciud = c5a.selectbox("Ciudad", ALL_CIUD, key="t5c")
    sel5_proy = c5b.selectbox("Proyecto", ALL_PC, key="t5p")
    sel5_area = c5c.selectbox("Control", CONTROL_AREA_OPTIONS, index=0, key="t5a")

    df5_ctrl = df_controles.copy()
    df5_ens = df_full.copy()
    if sel5_ciud != "Todas":
        df5_ctrl = df5_ctrl[df5_ctrl["Ciudad"] == sel5_ciud]
        df5_ens = df5_ens[df5_ens["Ciudad"] == sel5_ciud]
    if sel5_proy != "Todos":
        df5_ctrl = df5_ctrl[df5_ctrl["Proyecto"] == sel5_proy]
        df5_ens = df5_ens[df5_ens["Proyecto"] == sel5_proy]

    title5 = control_area_title(sel5_area)
    st.markdown(section_header(title5, "Promedio mensual con 12 meses fijos. Los registros sin valor no se incluyen en el cálculo."), unsafe_allow_html=True)
    st.markdown('<div class="dash-card">', unsafe_allow_html=True)
    st.markdown(heatmap_legend(), unsafe_allow_html=True)

    rows5 = build_heatmap_rows(df5_ctrl, df5_ens, sel5_area)
    if rows5:
        st.markdown(render_heatmap_table("Proyecto", rows5), unsafe_allow_html=True)
    else:
        st.info("ℹ️ No se encontraron controles con los filtros aplicados.")
    st.markdown('</div>', unsafe_allow_html=True)
