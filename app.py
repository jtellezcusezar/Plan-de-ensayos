import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from openpyxl import load_workbook
import json
from uuid import uuid4

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

COLORS = {
    "Planeado":     "#7BA7D4",
    "Completo":     "#6BBF9E",
    "Incompleto":   "#E8C17A",
    "No Realizado": "#D98B8B",
}

BASE_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#272829", size=12),
    margin=dict(t=40, b=10, l=10, r=10),
    hoverlabel=dict(
        bgcolor="#1E293B",
        font_color="#F1F5F9",
        font_size=12,
        bordercolor="#334155",
    ),
)

def apply_base(fig, h=300, legend_h=True):
    """Aplica el layout base y la leyenda horizontal (por defecto)."""
    fig.update_layout(
        paper_bgcolor=BASE_LAYOUT["paper_bgcolor"],
        plot_bgcolor=BASE_LAYOUT["plot_bgcolor"],
        font=BASE_LAYOUT["font"],
        margin=BASE_LAYOUT["margin"],
        hoverlabel=BASE_LAYOUT["hoverlabel"],
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
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;}
#MainMenu,footer{visibility:hidden;}
.block-container{padding-top:0!important;max-width:100%!important;padding-left:2rem!important;padding-right:2rem!important;}
[data-testid="stSidebar"]{display:none;}
.app-header{background:#fff;border-bottom:1px solid #E5E9F0;padding:14px 32px;display:flex;align-items:center;justify-content:space-between;margin:-1rem -2rem 0 -2rem;position:sticky;top:0;z-index:100;box-shadow:0 1px 6px rgba(15,23,42,.07);}
.logo-box{width:36px;height:36px;background:linear-gradient(135deg,#7BA7D4,#4A7BA8);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;}
.app-title{font-size:16px;font-weight:700;color:#111827;margin:0;}
.app-sub{font-size:11px;color:#9CA3AF;font-weight:500;text-transform:uppercase;letter-spacing:.04em;margin:0;}
.hdr-badge{background:#EEF3FA;color:#4A7BA8;font-size:12px;font-weight:600;padding:4px 12px;border-radius:20px;}
.hdr-date{font-size:12px;color:#9CA3AF;font-family:'DM Mono',monospace;}
.stTabs [data-baseweb="tab-list"]{background:#fff;border-bottom:1px solid #E5E9F0;padding:0;gap:0;margin:0 -2rem;padding-left:2rem;}
.stTabs [data-baseweb="tab"]{font-size:13px!important;font-weight:600!important;color:#9CA3AF!important;padding:14px 22px!important;border-bottom:2px solid transparent!important;background:transparent!important;}
.stTabs [aria-selected="true"]{color:#4A7BA8!important;border-bottom-color:#4A7BA8!important;}
.stTabs [data-baseweb="tab-panel"]{padding-top:24px;}
.stTabs [data-baseweb="tab-highlight"]{display:none;}
.filter-bar{margin-bottom:16px;}
.filter-bar-title{display:none;}
div[data-testid="stSelectbox"]>label{font-size:11px!important;font-weight:600!important;color:#6B7280!important;text-transform:uppercase!important;letter-spacing:.05em!important;margin-bottom:4px!important;}
div[data-testid="stSelectbox"]>div>div{border-radius:10px!important;border:1.5px solid #E5E9F0!important;background:#FAFBFC!important;font-size:13px!important;color:#374151!important;}
div[data-testid="stSelectbox"]>div>div:focus-within{border-color:#7BA7D4!important;box-shadow:0 0 0 3px rgba(123,167,212,.12)!important;}
div[data-testid="stTextInput"]>label{font-size:11px!important;font-weight:600!important;color:#6B7280!important;text-transform:uppercase!important;letter-spacing:.05em!important;}
div[data-testid="stTextInput"]>div>input{border-radius:10px!important;border:1.5px solid #E5E9F0!important;background:#FAFBFC!important;font-size:13px!important;color:#374151!important;}
div[data-testid="stTextInput"]>div>input:focus{border-color:#7BA7D4!important;box-shadow:0 0 0 3px rgba(123,167,212,.12)!important;}
.kpi-card{background:#fff;border:1px solid #E5E9F0;border-radius:14px;padding:18px 20px;position:relative;overflow:hidden;box-shadow:0 1px 4px rgba(15,23,42,.05);transition:transform .15s,box-shadow .15s;}
.kpi-card:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(15,23,42,.08);}
.kpi-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;border-radius:14px 14px 0 0;}
.kp-blue::before{background:#7BA7D4;}.kp-green::before{background:#6BBF9E;}.kp-yellow::before{background:#E8C17A;}.kp-red::before{background:#D98B8B;}.kp-slate::before{background:linear-gradient(90deg,#7BA7D4,#6BBF9E);}
.kpi-icon{font-size:20px;margin-bottom:8px;}.kpi-label{font-size:10px;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px;}
.kpi-value{font-size:28px;font-weight:800;line-height:1;font-family:'DM Mono',monospace;margin-bottom:4px;}.kpi-sub{font-size:11px;color:#9CA3AF;}
.kp-blue .kpi-value{color:#4A7BA8;}.kp-green .kpi-value{color:#3D8B6E;}.kp-yellow .kpi-value{color:#C49A3C;}.kp-red .kpi-value{color:#B05B5B;}.kp-slate .kpi-value{color:#4A7BA8;}
.section-head{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;margin:0 0 10px 0;padding-bottom:8px;border-bottom:1px solid #E5E9F0;}
.section-title{font-size:15px;font-weight:700;color:#111827;line-height:1.2;margin:0;}
.section-sub{font-size:11px;color:#9CA3AF;line-height:1.4;text-align:right;max-width:60%;margin:0;}
.dash-card{background:transparent;border:none;border-radius:0;padding:0;margin-bottom:18px;box-shadow:none;}
.card-title{font-size:14px;font-weight:700;color:#111827;margin-bottom:2px;}.card-sub{font-size:11px;color:#9CA3AF;margin-bottom:14px;}
.info-note{padding:9px 14px;background:#EEF3FA;border:1px solid #C8DCF0;border-radius:10px;font-size:12px;color:#4A7BA8;font-weight:500;margin-bottom:18px;}
.ok-note{padding:9px 14px;background:#E4F4EE;border:1px solid #A8D5BF;border-radius:10px;font-size:12px;color:#3D8B6E;font-weight:500;}
.sem-grid{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:20px;}
.sem-card{background:#fff;border:1px solid #E5E9F0;border-radius:12px;padding:14px 18px;min-width:160px;position:relative;overflow:hidden;box-shadow:0 1px 4px rgba(15,23,42,.05);transition:transform .15s;}
.sem-card:hover{transform:translateY(-1px);}
.sem-card::after{content:'';position:absolute;bottom:0;left:0;right:0;height:3px;border-radius:0 0 12px 12px;}
.sv::after{background:#6BBF9E;}.sa::after{background:#E8C17A;}.sr::after{background:#D98B8B;}
.sem-dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:6px;}
.sem-name{font-size:12px;font-weight:700;color:#111827;margin-bottom:6px;display:flex;align-items:center;}
.sem-tasa{font-size:22px;font-weight:800;font-family:'DM Mono',monospace;}
.sv .sem-tasa{color:#3D8B6E;}.sa .sem-tasa{color:#C49A3C;}.sr .sem-tasa{color:#B05B5B;}
.sem-detail{font-size:11px;color:#9CA3AF;margin-top:3px;}
.hm-wrap{overflow-x:auto;border-radius:10px;border:1px solid #E5E9F0;}
.hm-table{width:100%;border-collapse:collapse;font-size:12px;}
.hm-table th{background:#F8F9FB;padding:9px 8px;text-align:center;font-size:10px;font-weight:700;color:#9CA3AF;text-transform:uppercase;border-bottom:1px solid #E5E9F0;white-space:nowrap;}
.hm-table th.hmp{text-align:left;min-width:160px;padding-left:16px;}
.hm-table td{padding:8px;text-align:center;font-weight:700;font-family:'DM Mono',monospace;border-bottom:1px solid #F3F4F6;}
.hm-table td.hmpn{text-align:left;font-family:'Inter',sans-serif;font-size:12px;padding-left:16px;color:#111827;font-weight:600;}
.hm-table tr:last-child td{border-bottom:none;}.hm-table tr:hover td{filter:brightness(.97);}
.h100{background:#B8E4D0;color:#2D6A4F;}.h75{background:#DDE8B2;color:#667A1E;}.h50{background:#F4E1A6;color:#A97B12;}.h25{background:#EEC39F;color:#A45724;}.h0{background:#F0C8C8;color:#8B2B2B;}.hna{background:#F8F9FB;color:#C4CAD4;font-family:'Inter',sans-serif;font-weight:500;font-size:11px;}
.badge{display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;}
.bc{background:#E4F4EE;color:#3D8B6E;}.bi{background:#FBF3E0;color:#C49A3C;}.bn{background:#F8E8E8;color:#B05B5B;}.bp{background:#EEF3FA;color:#4A7BA8;}
.rt{width:100%;border-collapse:collapse;font-size:13px;}
.rt th{background:#F8F9FB;padding:10px 14px;text-align:left;font-size:10px;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:.05em;border-bottom:1px solid #E5E9F0;white-space:nowrap;}
.rt td{padding:10px 14px;border-bottom:1px solid #F3F4F6;color:#6B7280;}
.rt td:first-child{color:#111827;font-weight:600;}.rt tr:last-child td{border-bottom:none;}.rt tr:hover td{background:#FAFBFC;}
.ig-wrap{display:flex;justify-content:center;}
.ig-table{width:100%;max-width:1180px;border-collapse:collapse;font-size:12px;table-layout:fixed;}
.ig-table th{background:#B5545C;padding:8px 8px;text-align:center;font-size:10px;font-weight:700;color:#FFF7F7;text-transform:uppercase;letter-spacing:.05em;border-bottom:1px solid #9F434B;white-space:normal;line-height:1.2;word-break:break-word;}
.ig-table td{padding:7px 8px;border-bottom:1px solid #F1D9DB;color:#6B7280;text-align:center;line-height:1.15;word-break:break-word;}
.ig-table td:first-child{background:#F8E8E8;color:#8F3942;font-weight:700;text-align:center;}
.ig-table tr.ig-summary-row td{background:#E9C9CC!important;border-top:1px solid #DCA9AE;border-bottom:1px solid #DCA9AE;font-weight:700;}
.ig-table tr.ig-summary-row td:first-child{background:#E9C9CC!important;color:#7D2F37!important;text-transform:uppercase;letter-spacing:.04em;}
.ig-table tr.ig-summary-row td.h100,
.ig-table tr.ig-summary-row td.h75,
.ig-table tr.ig-summary-row td.h50,
.ig-table tr.ig-summary-row td.h25,
.ig-table tr.ig-summary-row td.h0,
.ig-table tr.ig-summary-row td.hna{background:#E9C9CC!important;}
.ig-table tr:last-child td{border-bottom:none;}
.hml{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px;align-items:center;}
.hml span{font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;}
div[data-testid="stDownloadButton"] button{background:#EEF3FA!important;color:#4A7BA8!important;border:1.5px solid #C8DCF0!important;border-radius:8px!important;font-size:12px!important;font-weight:600!important;padding:6px 14px!important;}
div[data-testid="stDownloadButton"] button:hover{background:#7BA7D4!important;color:#fff!important;}
::-webkit-scrollbar{width:5px;height:5px;}::-webkit-scrollbar-track{background:transparent;}::-webkit-scrollbar-thumb{background:#E5E9F0;border-radius:3px;}
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


def normalize_project_key(value):
    if value is None or pd.isna(value):
        return None
    text = " ".join(str(value).split()).strip()
    if not text or text.lower() in {"nan", "none"}:
        return None
    return text.casefold()

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


def render_echarts(option, height=320):
    chart_id = f"echart-{uuid4().hex}"
    option_json = json.dumps(option, ensure_ascii=False)
    option_json_js = json.dumps(option_json, ensure_ascii=False)
    html = f"""
    <div id="{chart_id}" style="width:100%;height:{height}px;"></div>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
    <script>
      function reviveEchartsFunctions(value) {{
        if (Array.isArray(value)) {{
          return value.map(reviveEchartsFunctions);
        }}
        if (value && typeof value === 'object') {{
          for (const key of Object.keys(value)) {{
            value[key] = reviveEchartsFunctions(value[key]);
          }}
          return value;
        }}
        if (typeof value === 'string' && value.startsWith('__JS__') && value.endsWith('__JS__')) {{
          const fnBody = value.slice(6, -6);
          return eval('(' + fnBody + ')');
        }}
        return value;
      }}

      const chart = echarts.init(document.getElementById('{chart_id}'));
      const rawOption = {option_json_js};
      const option = reviveEchartsFunctions(JSON.parse(rawOption));
      chart.setOption(option);
      window.addEventListener('resize', () => chart.resize());
    </script>
    """
    components.html(html, height=height, scrolling=False)

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
      <span style="background:#B8E4D0;color:#2D6A4F;">≥ 90%</span>
      <span style="background:#DDE8B2;color:#667A1E;">70–89%</span>
      <span style="background:#F4E1A6;color:#A97B12;">50–69%</span>
      <span style="background:#EEC39F;color:#A45724;">25–49%</span>
      <span style="background:#F0C8C8;color:#8B2B2B;">&lt; 25%</span>
      <span style="background:#F8F9FB;color:#C4CAD4;">Sin datos</span>
      <span style="font-size:11px;color:#9CA3AF;margin-left:4px;">· Meta: {META}%</span>
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


HEATMAP_RANGE_COLORS = {
    "na": "#F8F9FB",
    "lt25": "#F0C8C8",
    "lt50": "#EEC39F",
    "lt70": "#F4E1A6",
    "lt90": "#DDE8B2",
    "gte90": "#B8E4D0",
}


def build_echarts_heatmap_config(rows_data):
    month_labels = [MESES[m][:3] for m in range(1, 13)] + ["Prom."]
    col_values = [[] for _ in range(12)]
    matrix_rows = []

    for row in rows_data:
        row_vals = [v for v in row["values"] if v is not None]
        row_avg = round(sum(row_vals) / len(row_vals), 1) if row_vals else None
        display_values = []
        titles = row.get("titles", [None] * 12)
        for idx, val in enumerate(row["values"]):
            if val is not None:
                col_values[idx].append(val)
            display_values.append({"value": val, "title": titles[idx]})
        display_values.append({"value": row_avg, "title": "Promedio de la fila" if row_avg is not None else None})
        matrix_rows.append({"label": row["label"], "cells": display_values})

    avg_cells = []
    avg_row_values = []
    for idx in range(12):
        vals = col_values[idx]
        if vals:
            avg_val = round(sum(vals) / len(vals), 1)
            avg_row_values.append(avg_val)
            avg_cells.append({"value": avg_val, "title": "Promedio de la columna"})
        else:
            avg_cells.append({"value": None, "title": None})
    grand_avg = round(sum(avg_row_values) / len(avg_row_values), 1) if avg_row_values else None
    avg_cells.append({"value": grand_avg, "title": "Promedio general" if grand_avg is not None else None})
    matrix_rows.append({"label": "Promedio", "cells": avg_cells})

    data = []
    y_labels = [row["label"] for row in matrix_rows]
    for y_idx, row in enumerate(matrix_rows):
        for x_idx, cell in enumerate(row["cells"]):
            value = cell["value"]
            visual_value = -1 if value is None else round(float(value), 1)
            display_text = "—" if value is None else f"{round(float(value))}%"
            data.append([x_idx, y_idx, visual_value, display_text, cell["title"] or "Sin datos"])

    option = {
        "textStyle": {"fontFamily": "Inter, sans-serif"},
        "tooltip": {
            "position": "top",
            "formatter": """__JS__function (params) {
                const raw = params.data;
                const titulo = raw[4];
                const valor = raw[3];
                return '<b>' + params.name + '</b><br/>' + valor + '<br/>' + titulo;
            }__JS__""",
        },
        "grid": {"left": 110, "right": 18, "top": 10, "bottom": 20, "containLabel": True},
        "xAxis": {
            "type": "category",
            "position": "top",
            "data": month_labels,
            "splitArea": {"show": True},
            "axisLabel": {"color": "#6B7280", "fontFamily": "Inter, sans-serif", "fontSize": 11},
            "axisLine": {"lineStyle": {"color": "#E5E7EB"}},
        },
        "yAxis": {
            "type": "category",
            "data": y_labels,
            "inverse": True,
            "splitArea": {"show": True},
            "axisLabel": {"color": "#374151", "fontFamily": "Inter, sans-serif", "fontSize": 11},
            "axisTick": {"show": False},
            "axisLine": {"lineStyle": {"color": "#E5E7EB"}},
        },
        "visualMap": {
            "show": False,
            "min": -1,
            "max": 100,
            "dimension": 2,
            "pieces": [
                {"value": -1, "color": HEATMAP_RANGE_COLORS["na"]},
                {"min": 0, "max": 24.999, "color": HEATMAP_RANGE_COLORS["lt25"]},
                {"min": 25, "max": 49.999, "color": HEATMAP_RANGE_COLORS["lt50"]},
                {"min": 50, "max": 69.999, "color": HEATMAP_RANGE_COLORS["lt70"]},
                {"min": 70, "max": 89.999, "color": HEATMAP_RANGE_COLORS["lt90"]},
                {"min": 90, "max": 100, "color": HEATMAP_RANGE_COLORS["gte90"]},
            ],
        },
        "series": [{
            "name": "Cumplimiento",
            "type": "heatmap",
            "data": data,
            "label": {
                "show": True,
                "formatter": """__JS__function (params) { return params.data[3]; }__JS__""",
                "fontFamily": "Inter, sans-serif",
                "fontSize": 10,
                "fontWeight": 700,
                "color": "#374151",
            },
            "itemStyle": {"borderColor": "#E5E9F0", "borderWidth": 1},
            "emphasis": {"itemStyle": {"shadowBlur": 0, "borderColor": "#CBD5E1", "borderWidth": 1}},
        }],
    }
    return option, max(280, 44 + len(y_labels) * 32)

def badge(estado):
    m = {"Completo":("bc","✅"), "Incompleto":("bi","⚠️"),
         "No Realizado":("bn","❌"), "Planeado":("bp","🔵")}
    cls, ico = m.get(estado, ("bp","🔵"))
    return f'<span class="badge {cls}">{ico} {estado}</span>'

def sem_card(name, tasa, ej, crit):
    cls = "sv" if tasa >= META else "sa" if tasa >= META * 0.6 else "sr"
    dot = "#6BBF9E" if tasa >= META else "#E8C17A" if tasa >= META * 0.6 else "#D98B8B"
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


def build_pending_controls_rows(df_ctrl, proyectos, show_repeat_count=False):
    pending_df = df_ctrl[df_ctrl["Valor_num"].isin([0, 0.5])].copy()
    rows = []

    for proyecto in proyectos:
        proy_df = pending_df[pending_df["Proyecto"] == proyecto]

        torre_mask = (
            (proy_df["Area"] == "Torre") &
            (proy_df["Etapa"].isin(["Estructura", "Obra gris y Obra blanca"]))
        )
        producto_mask = (
            (proy_df["Area"] == "Torre") &
            (proy_df["Etapa"] == "Producto terminado")
        )
        zonas_mask = proy_df["Area"] == "Zonas comunes"

        def format_controls(subdf):
            controles = (
                subdf["Control"]
                .dropna()
                .astype(str)
                .str.strip()
            )
            controles = [c for c in controles.tolist() if c and c not in {"nan", "None"}]
            if not controles:
                return '<span style="color:#9CA3AF;">—</span>'
            if show_repeat_count:
                counts = {}
                ordered = []
                for control in controles:
                    if control not in counts:
                        counts[control] = 0
                        ordered.append(control)
                    counts[control] += 1
                formatted = [
                    f"{control} ({counts[control]})" if counts[control] >= 2 else control
                    for control in ordered
                ]
                return "<br>".join(formatted)
            controles = list(dict.fromkeys(controles))
            return "<br>".join(controles)

        rows.append({
            "Proyecto": proyecto,
            "Control de torre": format_controls(proy_df[torre_mask]),
            "Producto terminado de torres": format_controls(proy_df[producto_mask]),
            "Control zonas comunes": format_controls(proy_df[zonas_mask]),
        })

    return [
        row for row in rows
        if any(row[col] != '<span style="color:#9CA3AF;">—</span>' for col in [
            "Control de torre",
            "Producto terminado de torres",
            "Control zonas comunes",
        ])
    ]


def get_material_month_map(df_ens, month):
    result = {}
    for proyecto in sorted(df_ens["Proyecto"].dropna().unique().tolist()):
        sub = df_ens[
            (df_ens["Proyecto"] == proyecto) &
            (df_ens["EsEjecutado"]) &
            (df_ens["Mes"] == month)
        ]
        result[proyecto] = round(sub["Cantidad_num"].mean() * 100, 1) if not sub.empty else None
    return result


def get_control_month_map(df_ctrl, df_ens, area, month):
    rows = build_heatmap_rows(df_ctrl, df_ens, area)
    return {
        row["label"]: row["values"][month - 1] if len(row["values"]) >= month else None
        for row in rows
    }


def get_project_city_map():
    frames = []
    for df in (df_full, df_controles):
        if {"Proyecto", "Ciudad"}.issubset(df.columns):
            sub = df[["Proyecto", "Ciudad"]].copy()
            sub = sub.dropna(subset=["Proyecto", "Ciudad"])
            sub["Proyecto"] = sub["Proyecto"].astype(str).str.strip()
            sub["Ciudad"] = sub["Ciudad"].astype(str).str.strip()
            sub = sub[
                sub["Proyecto"].ne("") &
                sub["Ciudad"].ne("") &
                sub["Proyecto"].str.lower().ne("nan") &
                sub["Ciudad"].str.lower().ne("nan") &
                sub["Proyecto"].str.lower().ne("none") &
                sub["Ciudad"].str.lower().ne("none")
            ]
            sub["ProyectoKey"] = sub["Proyecto"].map(normalize_project_key)
            sub = sub[sub["ProyectoKey"].notna()]
            frames.append(sub)

    if not frames:
        return {}

    cities_df = pd.concat(frames, ignore_index=True).drop_duplicates()
    city_map = {}
    for proyecto_key, group in cities_df.groupby("ProyectoKey", sort=True):
        ciudades = (
            group["Ciudad"]
            .dropna()
            .astype(str)
            .str.strip()
        )
        ciudades = [
            ciudad for ciudad in ciudades.tolist()
            if ciudad and ciudad.lower() not in {"nan", "none"}
        ]
        if ciudades:
            city_map[proyecto_key] = ciudades[0]
    return city_map


def average_values(values):
    valid_values = [float(v) for v in values if v is not None and not pd.isna(v)]
    return round(sum(valid_values) / len(valid_values), 1) if valid_values else None


def percent_cell_html(value):
    if value is None or pd.isna(value):
        return '<td class="hna"><strong>—</strong></td>'
    cls = hm_cls(float(value))
    text_colors = {
        "h100": "#2D6A4F",
        "h75": "#667A1E",
        "h50": "#A97B12",
        "h25": "#A45724",
        "h0": "#8B2B2B",
    }
    color = text_colors.get(cls, "#374151")
    return f'<td class="{cls}" style="color:{color};"><strong>{float(value):.0f}%</strong></td>'

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

tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📌  Informe General",
    "📊  Resumen General",
    "🏗️  Por Proyecto y Material",
    "📅  Línea de Tiempo y Alertas",
    "🔍  Consulta de Ensayos",
    "🛠️  Controles",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 0
# ══════════════════════════════════════════════════════════════════════════════
with tab0:
    default_mes_general = MESES[MESES_VENCIDOS[-1]] if MESES_VENCIDOS else list(MESES.values())[0]
    default_mes_general_idx = ALL_M.index(default_mes_general) if default_mes_general in ALL_M else 1

    gcol, _ = st.columns([1.2, 4.8])
    with gcol:
        sel0_mes = st.selectbox(
            "Mes",
            ALL_M[1:],
            index=max(0, default_mes_general_idx - 1),
            key="t0m",
        )

    mes0_num = next((k for k, v in MESES.items() if v == sel0_mes), None)

    st.markdown(section_header("Informe General", f"Resumen consolidado por proyecto para {sel0_mes}"), unsafe_allow_html=True)
    st.markdown('<div class="dash-card">', unsafe_allow_html=True)
    st.markdown(heatmap_legend(), unsafe_allow_html=True)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    materiales_map = get_material_month_map(df_full, mes0_num)
    torre_map = get_control_month_map(df_controles, df_full, "Torre", mes0_num)
    producto_map = get_control_month_map(df_controles, df_full, "Producto terminado", mes0_num)
    zonas_map = get_control_month_map(df_controles, df_full, "Zonas comunes", mes0_num)
    diseno_map = get_control_month_map(df_controles, df_full, "Diseño", mes0_num)
    curado_map = get_control_month_map(df_controles, df_full, "Curado", mes0_num)
    project_city_map = get_project_city_map()

    mostrar_diseno = any(v is not None for v in diseno_map.values())
    proyectos_general = sorted(
        set(materiales_map.keys()) |
        set(torre_map.keys()) |
        set(producto_map.keys()) |
        set(zonas_map.keys()) |
        set(diseno_map.keys()) |
        set(curado_map.keys())
    )

    header_cells = [
        "<th>Proyecto</th>",
        "<th>Control de Materiales</th>",
        "<th>Control de Torre</th>",
        "<th>Control de producto terminado</th>",
        "<th>Control de Zonas comunes</th>",
    ]
    if mostrar_diseno:
        header_cells.append("<th>Control de diseño</th>")
    header_cells.extend([
        "<th>Curado</th>",
        "<th>Promedio mes</th>",
    ])

    city_groups = {}
    for proyecto in proyectos_general:
        ciudad = project_city_map.get(normalize_project_key(proyecto), "Sin ciudad")
        city_groups.setdefault(ciudad, []).append(proyecto)

    body_rows = []
    for ciudad in sorted(city_groups):
        city_projects = sorted(city_groups[ciudad])
        city_row_values = []

        for proyecto in city_projects:
            row_values = [
                materiales_map.get(proyecto),
                torre_map.get(proyecto),
                producto_map.get(proyecto),
                zonas_map.get(proyecto),
            ]
            if mostrar_diseno:
                row_values.append(diseno_map.get(proyecto))
            row_values.append(curado_map.get(proyecto))

            promedio_mes = average_values(row_values)
            city_row_values.append(row_values + [promedio_mes])

            row_html = [f"<tr><td>{proyecto}</td>"]
            row_html.append(percent_cell_html(materiales_map.get(proyecto)))
            row_html.append(percent_cell_html(torre_map.get(proyecto)))
            row_html.append(percent_cell_html(producto_map.get(proyecto)))
            row_html.append(percent_cell_html(zonas_map.get(proyecto)))
            if mostrar_diseno:
                row_html.append(percent_cell_html(diseno_map.get(proyecto)))
            row_html.append(percent_cell_html(curado_map.get(proyecto)))
            row_html.append(percent_cell_html(promedio_mes))
            row_html.append("</tr>")
            body_rows.append("".join(row_html))

        city_columns_avg = []
        total_columns = 7 if mostrar_diseno else 6
        for col_idx in range(total_columns):
            city_columns_avg.append(average_values(
                row[col_idx] for row in city_row_values
            ))

        city_row_html = [f'<tr class="ig-summary-row"><td>{ciudad}</td>']
        for value in city_columns_avg:
            city_row_html.append(percent_cell_html(value))
        city_row_html.append("</tr>")
        body_rows.append("".join(city_row_html))

    st.markdown(
        f'<div class="ig-wrap">'
        f'<div style="width:100%;overflow-x:auto;border-radius:10px;border:1px solid #E5E9F0;max-width:1180px;">'
        f'<table class="ig-table"><thead><tr>{"".join(header_cells)}</tr></thead>'
        f'<tbody>{"".join(body_rows)}</tbody></table></div></div>',
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

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
        donut_states = [estado for estado in ["Planeado", "Completo", "Incompleto", "No Realizado"] if estado in ec["Estado"].tolist()]
        ec_plot = (ec.set_index("Estado")
                     .reindex(donut_states)
                     .reset_index())
        donut_option = {
            "textStyle": {"fontFamily": "Inter, sans-serif"},
            "tooltip": {"trigger": "item", "formatter": "{b}<br/>{c} ({d}%)"},
            "legend": {
                "type": "scroll",
                "bottom": 2,
                "left": "center",
                "icon": "circle",
                "textStyle": {"fontFamily": "Inter, sans-serif", "fontSize": 12, "color": "#6B7280"},
            },
            "series": [{
                "type": "pie",
                "radius": ["48%", "72%"],
                "center": ["50%", "40%"],
                "avoidLabelOverlap": True,
                "label": {"show": True, "formatter": "{d}%", "fontFamily": "Inter, sans-serif", "fontSize": 11, "color": "#6B7280"},
                "labelLine": {"show": True, "length": 10, "length2": 8},
                "itemStyle": {"borderColor": "#FFFFFF", "borderWidth": 2},
                "data": [
                    {"name": row["Estado"], "value": int(row["n"]), "itemStyle": {"color": COLORS[row["Estado"]]}}
                    for _, row in ec_plot.iterrows()
                ],
            }],
            "graphic": [{
                "type": "text",
                "left": "center",
                "top": "40%",
                "style": {
                    "text": f"{len(df1):,}",
                    "fontSize": 18,
                    "fontWeight": 700,
                    "fontFamily": "Inter, sans-serif",
                    "fill": "#111827",
                    "align": "center",
                    "verticalAlign": "middle",
                },
            }],
        }
        render_echarts(donut_option, height=340)
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
            pg_pivot = (pg.pivot(index="Proyecto", columns="Estado", values="n")
                          .reindex(index=orden, columns=["No Realizado", "Incompleto", "Completo"], fill_value=0)
                          .fillna(0))
            proy_option = {
                "textStyle": {"fontFamily": "Inter, sans-serif"},
                "color": [COLORS["No Realizado"], COLORS["Incompleto"], COLORS["Completo"]],
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "legend": {
                    "type": "scroll",
                    "bottom": 2,
                    "left": "center",
                    "textStyle": {"fontFamily": "Inter, sans-serif", "fontSize": 12, "color": "#6B7280"},
                },
                "grid": {"left": 110, "right": 10, "top": 10, "bottom": 65, "containLabel": True},
                "xAxis": {
                    "type": "value",
                    "splitLine": {"show": True, "lineStyle": {"color": "#F3F4F6"}},
                    "axisLabel": {"color": "#6B7280", "fontFamily": "Inter, sans-serif"},
                },
                "yAxis": {
                    "type": "category",
                    "data": orden,
                    "axisLabel": {"color": "#374151", "fontFamily": "Inter, sans-serif"},
                    "axisTick": {"show": False},
                },
                "series": [
                    {"name": "No Realizado", "type": "bar", "stack": "total", "data": pg_pivot["No Realizado"].astype(int).tolist()},
                    {"name": "Incompleto", "type": "bar", "stack": "total", "data": pg_pivot["Incompleto"].astype(int).tolist()},
                    {"name": "Completo", "type": "bar", "stack": "total", "data": pg_pivot["Completo"].astype(int).tolist()},
                ],
            }
            render_echarts(proy_option, height=330)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Línea temporal ──
    st.markdown(section_header("Ensayos por Mes — 2026", "Líneas sólidas = ejecutados por estado · Punteada = total planeado del mes · Curva suavizada"), unsafe_allow_html=True)
    st.markdown('<div class="dash-card">', unsafe_allow_html=True)
    mp = (df1.groupby("Mes").size()
            .reindex(range(1,13), fill_value=0).reset_index())
    mp.columns = ["Mes","n"]
    line_option = {
        "textStyle": {"fontFamily": "Inter, sans-serif"},
        "color": [COLORS["Planeado"], COLORS["Completo"], COLORS["Incompleto"], COLORS["No Realizado"]],
        "tooltip": {"trigger": "axis"},
        "legend": {
            "type": "scroll",
            "bottom": 2,
            "left": "center",
            "textStyle": {"fontFamily": "Inter, sans-serif", "fontSize": 12, "color": "#6B7280"},
        },
        "grid": {"left": 35, "right": 15, "top": 20, "bottom": 68, "containLabel": True},
        "xAxis": {
            "type": "category",
            "data": [MESES[m] for m in range(1, 13)],
            "axisLabel": {"color": "#6B7280", "fontFamily": "Inter, sans-serif", "fontSize": 11},
            "axisLine": {"lineStyle": {"color": "#D1D5DB"}},
        },
        "yAxis": {
            "type": "value",
            "axisLabel": {"color": "#6B7280", "fontFamily": "Inter, sans-serif"},
            "splitLine": {"lineStyle": {"color": "#F3F4F6"}},
        },
        "series": [
            {
                "name": "Plan del mes",
                "type": "line",
                "smooth": True,
                "symbolSize": 7,
                "lineStyle": {"width": 2, "type": "dashed"},
                "data": mp["n"].astype(int).tolist(),
            },
            {
                "name": "Completo",
                "type": "line",
                "smooth": True,
                "symbolSize": 8,
                "areaStyle": {"color": "rgba(107,191,158,0.15)"},
                "data": (df1[df1["EsEjecutado"] & (df1["Estado"]=="Completo")]
                           .groupby("Mes").size()
                           .reindex(range(1,13), fill_value=0)
                           .astype(int).tolist()),
            },
            {
                "name": "Incompleto",
                "type": "line",
                "smooth": True,
                "symbolSize": 8,
                "data": (df1[df1["EsEjecutado"] & (df1["Estado"]=="Incompleto")]
                           .groupby("Mes").size()
                           .reindex(range(1,13), fill_value=0)
                           .astype(int).tolist()),
            },
            {
                "name": "No Realizado",
                "type": "line",
                "smooth": True,
                "symbolSize": 8,
                "data": (df1[df1["EsEjecutado"] & (df1["Estado"]=="No Realizado")]
                           .groupby("Mes").size()
                           .reindex(range(1,13), fill_value=0)
                           .astype(int).tolist()),
            },
        ],
    }
    render_echarts(line_option, height=340)
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

    heatmap_option, heatmap_height = build_echarts_heatmap_config(rows_hm)
    render_echarts(heatmap_option, height=heatmap_height)
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
        tasa_option = {
            "textStyle": {"fontFamily": "Inter, sans-serif"},
            "tooltip": {
                "trigger": "item",
                "formatter": """__JS__function (params) {
                    const d = params.data;
                    return '<b>' + d.proyecto + '</b><br/>Cumplimiento: ' + d.value.toFixed(1) + '%' +
                           '<br/>Completos: ' + d.comp +
                           '<br/>Incompletos: ' + d.inc +
                           '<br/>No realizados: ' + d.no_r +
                           '<br/>Total plan meses vencidos: ' + d.tot;
                }__JS__""",
            },
            "grid": {"left": 120, "right": 35, "top": 24, "bottom": 20, "containLabel": True},
            "xAxis": {
                "type": "value",
                "min": 0,
                "max": 115,
                "axisLabel": {"formatter": "{value}%", "color": "#6B7280", "fontFamily": "Inter, sans-serif"},
                "splitLine": {"lineStyle": {"color": "#F3F4F6"}},
            },
            "yAxis": {
                "type": "category",
                "data": t_df["Proyecto"].tolist(),
                "axisLabel": {"color": "#374151", "fontFamily": "Inter, sans-serif"},
                "axisTick": {"show": False},
            },
            "series": [{
                "type": "bar",
                "data": [
                    {
                        "value": float(row.tasa),
                        "proyecto": row.Proyecto,
                        "comp": int(row.comp),
                        "inc": int(row.inc),
                        "no_r": int(row.no_r),
                        "tot": int(row.tot),
                        "itemStyle": {"color": bar_col(row.tasa)},
                    }
                    for _, row in t_df.iterrows()
                ],
                "barWidth": 18,
                "label": {
                    "show": True,
                    "position": "right",
                    "formatter": "{c}%",
                    "fontFamily": "Inter, sans-serif",
                    "fontSize": 11,
                    "color": "#6B7280",
                },
                "markLine": {
                    "silent": True,
                    "symbol": "none",
                    "lineStyle": {"type": "dashed", "color": COLORS["Planeado"], "width": 1.5},
                    "label": {
                        "show": True,
                        "formatter": f"Meta {META}%",
                        "color": COLORS["Planeado"],
                        "fontFamily": "Inter, sans-serif",
                        "fontSize": 10,
                    },
                    "data": [{"xAxis": META}],
                },
            }],
        }
        render_echarts(tasa_option, height=max(320, 70 + len(t_df) * 28))
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
        for est, fc in [("Completo","rgba(107,191,158,.15)"),
                         ("Incompleto","rgba(232,193,122,.12)"),
                         ("No Realizado","rgba(217,139,139,.10)")]:
            fig_area.add_trace(go.Scatter(
                x=adf["Mes"], y=adf[f"{est}_ac"],
                name=f"{est} (acum.)", mode="lines+markers",
                line=dict(color=COLORS[est], width=2.5, shape="spline", smoothing=1.0),
                marker=dict(size=8, line=dict(color="white", width=1.5)),
                fill="tozeroy", fillcolor=fc,
                hovertemplate=f"<b>%{{x}}</b><br>{est} acum.: %{{y}}<extra></extra>",
            ))
        apply_base(fig_area, h=300)
        fig_area.update_layout(xaxis=dict(gridcolor="#F3F4F6"), yaxis=dict(gridcolor="#F3F4F6"))
        st.plotly_chart(fig_area, use_container_width=True, config={"displayModeBar": False})
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
            f'<div style="overflow-x:auto;border-radius:10px;border:1px solid #E5E9F0;">'
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
            f"<td style='max-width:180px;white-space:normal;font-size:11px;color:#9CA3AF'>{r.Frecuencia}</td>"
            f"<td>{r.Mes}</td><td>{badge(r.Estado)}</td></tr>"
            for _, r in prev.iterrows())
        st.markdown(f'<div class="card-sub">Mostrando {min(50,len(disp))} de {len(disp):,} registros.</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div style="overflow-x:auto;border-radius:10px;border:1px solid #E5E9F0;max-height:480px;overflow-y:auto;">'
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
        heatmap5_option, heatmap5_height = build_echarts_heatmap_config(rows5)
        render_echarts(heatmap5_option, height=heatmap5_height)
    else:
        st.info("ℹ️ No se encontraron controles con los filtros aplicados.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(section_header("Controles pendientes", "Controles con valor 0 o 0,5 agrupados por proyecto"), unsafe_allow_html=True)
    st.markdown('<div class="dash-card">', unsafe_allow_html=True)

    pend_col, _ = st.columns([1.2, 4.8])
    with pend_col:
        sel5_pend_mes = st.selectbox("Mes", ALL_M, key="t5_pending_mes")
    df5_pending = df5_ctrl.copy()
    if sel5_pend_mes != "Todos":
        df5_pending = df5_pending[df5_pending["Mes"].isin([k for k, v in MESES.items() if v == sel5_pend_mes])]

    proyectos_tabla = sorted(
        set(df5_pending["Proyecto"].dropna().tolist()) |
        set(df5_ens["Proyecto"].dropna().tolist())
    )
    pending_rows = build_pending_controls_rows(
        df5_pending,
        proyectos_tabla,
        show_repeat_count=(sel5_pend_mes == "Todos"),
    )

    if pending_rows:
        rows_html = "".join(
            f"<tr>"
            f"<td>{row['Proyecto']}</td>"
            f"<td style='white-space:normal;line-height:1.45;'>{row['Control de torre']}</td>"
            f"<td style='white-space:normal;line-height:1.45;'>{row['Producto terminado de torres']}</td>"
            f"<td style='white-space:normal;line-height:1.45;'>{row['Control zonas comunes']}</td>"
            f"</tr>"
            for row in pending_rows
        )
        st.markdown(
            f'<div style="overflow-x:auto;border-radius:10px;border:1px solid #E5E9F0;">'
            f'<table class="rt"><thead><tr>'
            f'<th>Proyecto</th>'
            f'<th>Control de torre</th>'
            f'<th>Producto terminado de torres</th>'
            f'<th>Control zonas comunes</th>'
            f'</tr></thead><tbody>{rows_html}</tbody></table></div>',
            unsafe_allow_html=True
        )
    else:
        st.info("ℹ️ No se encontraron controles pendientes con los filtros aplicados.")
    st.markdown('</div>', unsafe_allow_html=True)
