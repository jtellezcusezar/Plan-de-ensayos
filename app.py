import streamlit as st
import pandas as pd
import io

st.set_page_config(
    page_title="Consulta de Ensayos 2026", page_icon="🔍",
    layout="wide", initial_sidebar_state="collapsed",
)

# ── CONSTANTES ─────────────────────────────────────────────────────────────────
MESES = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
         7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}
ESTADO_MAP = {"*":"Planeado", 0:"No Realizado", 0.5:"Incompleto", 1:"Completo"}

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;}
#MainMenu,footer{visibility:hidden;}
.block-container{padding-top:3.5rem!important;max-width:100%!important;padding-left:2rem!important;padding-right:2rem!important;}
[data-testid="stSidebar"]{display:none;}

/* HEADER */
.app-header{background:#fff;border:1px solid #E5E9F0;border-radius:14px;padding:14px 24px;display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;box-shadow:0 1px 6px rgba(15,23,42,.07);}
.logo-box{width:36px;height:36px;background:linear-gradient(135deg,#7BA7D4,#4A7BA8);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;}
.app-title{font-size:16px;font-weight:700;color:#111827;margin:0;}
.app-sub{font-size:11px;color:#9CA3AF;font-weight:500;text-transform:uppercase;letter-spacing:.04em;margin:0;}
.hdr-badge{background:#EEF3FA;color:#4A7BA8;font-size:12px;font-weight:600;padding:4px 12px;border-radius:20px;}

/* FILTER BAR */
.filter-bar{background:#fff;border:1px solid #E5E9F0;border-radius:14px;padding:14px 20px 18px;margin-bottom:20px;box-shadow:0 1px 4px rgba(15,23,42,.05);}
.filter-bar-title{font-size:10px;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:.08em;margin-bottom:12px;padding-bottom:10px;border-bottom:1px solid #F3F4F6;}

/* SELECTBOX */
div[data-testid="stSelectbox"]>label{font-size:11px!important;font-weight:600!important;color:#6B7280!important;text-transform:uppercase!important;letter-spacing:.05em!important;margin-bottom:4px!important;}
div[data-testid="stSelectbox"]>div>div{border-radius:10px!important;border:1.5px solid #E5E9F0!important;background:#FAFBFC!important;font-size:13px!important;color:#374151!important;}
div[data-testid="stSelectbox"]>div>div:focus-within{border-color:#7BA7D4!important;box-shadow:0 0 0 3px rgba(123,167,212,.12)!important;}

/* TEXT INPUT */
div[data-testid="stTextInput"]>label{font-size:11px!important;font-weight:600!important;color:#6B7280!important;text-transform:uppercase!important;letter-spacing:.05em!important;}
div[data-testid="stTextInput"]>div>input{border-radius:10px!important;border:1.5px solid #E5E9F0!important;background:#FAFBFC!important;font-size:13px!important;color:#374151!important;}
div[data-testid="stTextInput"]>div>input:focus{border-color:#7BA7D4!important;box-shadow:0 0 0 3px rgba(123,167,212,.12)!important;}

/* KPI CARDS */
.kpi-card{background:#fff;border:1px solid #E5E9F0;border-radius:14px;padding:18px 20px;position:relative;overflow:hidden;box-shadow:0 1px 4px rgba(15,23,42,.05);transition:transform .15s,box-shadow .15s;}
.kpi-card:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(15,23,42,.08);}
.kpi-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;border-radius:14px 14px 0 0;}
.kp-blue::before{background:#7BA7D4;}.kp-green::before{background:#6BBF9E;}.kp-yellow::before{background:#E8C17A;}.kp-red::before{background:#D98B8B;}.kp-slate::before{background:linear-gradient(90deg,#7BA7D4,#6BBF9E);}
.kpi-icon{font-size:20px;margin-bottom:8px;}.kpi-label{font-size:10px;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px;}
.kpi-value{font-size:28px;font-weight:800;line-height:1;font-family:'DM Mono',monospace;margin-bottom:4px;}.kpi-sub{font-size:11px;color:#9CA3AF;}
.kp-blue .kpi-value{color:#4A7BA8;}.kp-green .kpi-value{color:#3D8B6E;}.kp-yellow .kpi-value{color:#C49A3C;}.kp-red .kpi-value{color:#B05B5B;}.kp-slate .kpi-value{color:#4A7BA8;}

/* DASH CARD */
.dash-card{background:#fff;border:1px solid #E5E9F0;border-radius:14px;padding:20px 22px;box-shadow:0 1px 4px rgba(15,23,42,.05);margin-bottom:18px;}
.card-title{font-size:14px;font-weight:700;color:#111827;margin-bottom:2px;}.card-sub{font-size:11px;color:#9CA3AF;margin-bottom:14px;}

/* BADGES */
.badge{display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;}
.bc{background:#E4F4EE;color:#3D8B6E;}.bi{background:#FBF3E0;color:#C49A3C;}.bn{background:#F8E8E8;color:#B05B5B;}.bp{background:#EEF3FA;color:#4A7BA8;}

/* RESULTS TABLE */
.rt{width:100%;border-collapse:collapse;font-size:13px;}
.rt th{background:#F8F9FB;padding:10px 14px;text-align:left;font-size:10px;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:.05em;border-bottom:1px solid #E5E9F0;white-space:nowrap;}
.rt td{padding:10px 14px;border-bottom:1px solid #F3F4F6;color:#6B7280;}
.rt td:first-child{color:#111827;font-weight:600;}.rt tr:last-child td{border-bottom:none;}.rt tr:hover td{background:#FAFBFC;}

/* DOWNLOAD BTN */
div[data-testid="stDownloadButton"] button{background:#3D8B6E!important;color:#fff!important;border:none!important;border-radius:10px!important;font-size:13px!important;font-weight:600!important;padding:9px 20px!important;transition:all .15s!important;font-family:'Inter',sans-serif!important;}
div[data-testid="stDownloadButton"] button:hover{background:#2D6A4F!important;box-shadow:0 4px 12px rgba(61,139,110,.3)!important;}

::-webkit-scrollbar{width:5px;height:5px;}::-webkit-scrollbar-track{background:transparent;}::-webkit-scrollbar-thumb{background:#E5E9F0;border-radius:3px;}
</style>
""", unsafe_allow_html=True)

# ── DATA ───────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("Plan_de_ensayos_2026.xlsx", sheet_name="Ensayos", header=0)
    for c in ["Proyecto","MATERIAL","ETAPA","ENSAYO","NTC","FRECUENCIA"]:
        df[c] = df[c].str.strip()
    df["MesNombre"]    = df["Mes"].map(MESES)
    df["Estado"]       = df["Cantidad"].map(lambda x: ESTADO_MAP.get(x, str(x)))
    df["EsEjecutado"]  = df["Cantidad"] != "*"
    df["Cantidad_num"] = pd.to_numeric(df["Cantidad"], errors="coerce")
    return df

df_full = load_data()

ALL_P   = ["Todos"] + sorted(df_full["Proyecto"].unique().tolist())
ALL_E   = ["Todas"] + sorted(df_full["ETAPA"].unique().tolist())
ALL_M   = ["Todos"] + list(MESES.values())
ALL_MAT = ["Todos"] + sorted(df_full["MATERIAL"].unique().tolist())
ALL_EST = ["Todos"] + list(ESTADO_MAP.values())

# ── HELPERS ────────────────────────────────────────────────────────────────────
def kpi(icon, label, value, sub, css):
    return (f'<div class="kpi-card {css}"><div class="kpi-icon">{icon}</div>'
            f'<div class="kpi-label">{label}</div><div class="kpi-value">{value}</div>'
            f'<div class="kpi-sub">{sub}</div></div>')

def get_kpis(df):
    ex   = df[df["EsEjecutado"]]
    comp = int((ex["Cantidad_num"] == 1).sum())
    inc  = int((ex["Cantidad_num"] == 0.5).sum())
    no_r = int((ex["Cantidad_num"] == 0).sum())
    plan = int((df["Cantidad"] == "*").sum())
    tot  = comp + inc + no_r
    tasa = round(comp / tot * 100, 1) if tot > 0 else 0.0
    return comp, inc, no_r, plan, tot, tasa

def badge(estado):
    m = {"Completo":("bc","✅"), "Incompleto":("bi","⚠️"),
         "No Realizado":("bn","❌"), "Planeado":("bp","🔵")}
    cls, ico = m.get(estado, ("bp","🔵"))
    return f'<span class="badge {cls}">{ico} {estado}</span>'

def to_excel(df):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Consulta Ensayos")
        ws = writer.sheets["Consulta Ensayos"]
        # Ajustar ancho de columnas automáticamente
        for col in ws.columns:
            max_len = max((len(str(cell.value)) if cell.value else 0) for cell in col)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 50)
    return buf.getvalue()

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="app-header">
  <div style="display:flex;align-items:center;gap:12px;">
    <div class="logo-box">🏗️</div>
    <div>
      <p class="app-title">Argus — Plan de Ensayos</p>
      <p class="app-sub">Consulta de Ensayos 2026 · Cusezar</p>
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:14px;">
    <span class="hdr-badge">{df_full['Proyecto'].nunique()} Proyectos · {len(df_full):,} Ensayos totales</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── FILTROS ────────────────────────────────────────────────────────────────────
st.markdown('<div class="filter-bar"><div class="filter-bar-title">⚙ Filtros de búsqueda</div>', unsafe_allow_html=True)
q1, q2, q3 = st.columns(3)
sel_proy  = q1.selectbox("Proyecto",  ALL_P,   key="p")
sel_etapa = q1.selectbox("Etapa",     ALL_E,   key="e")
sel_mes   = q2.selectbox("Mes",       ALL_M,   key="m")
sel_mat   = q2.selectbox("Material",  ALL_MAT, key="mat")
sel_est   = q3.selectbox("Estado",    ALL_EST, key="est")
buscar    = q3.text_input("🔎 Buscar por nombre de ensayo",
                          placeholder="Ej: resistencia, fraguado, granulometría...")
st.markdown('</div>', unsafe_allow_html=True)

# ── FILTRADO ───────────────────────────────────────────────────────────────────
df = df_full.copy()
if sel_proy  != "Todos": df = df[df["Proyecto"] == sel_proy]
if sel_etapa != "Todas": df = df[df["ETAPA"]    == sel_etapa]
if sel_mes   != "Todos": df = df[df["Mes"].isin([k for k,v in MESES.items() if v == sel_mes])]
if sel_mat   != "Todos": df = df[df["MATERIAL"] == sel_mat]
if sel_est   != "Todos": df = df[df["Estado"]   == sel_est]
if buscar:               df = df[df["ENSAYO"].str.contains(buscar, case=False, na=False)]

# ── KPIs ───────────────────────────────────────────────────────────────────────
comp, inc, no_r, plan, tot, tasa = get_kpis(df)
a, b, c_, d, e = st.columns(5)
a.markdown(kpi("🔍","Resultados",    f"{len(df):,}", "registros encontrados", "kp-slate"),  unsafe_allow_html=True)
b.markdown(kpi("📋","Planeados",     f"{plan:,}",   "",                       "kp-blue"),   unsafe_allow_html=True)
c_.markdown(kpi("✅","Completos",    f"{comp:,}",   "",                       "kp-green"),  unsafe_allow_html=True)
d.markdown(kpi("⚠️","Incompletos",   f"{inc:,}",    "",                       "kp-yellow"), unsafe_allow_html=True)
e.markdown(kpi("❌","No Realizados", f"{no_r:,}",   "",                       "kp-red"),    unsafe_allow_html=True)

st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

# ── TABLA DE RESULTADOS ────────────────────────────────────────────────────────
st.markdown('<div class="dash-card"><div class="card-title">Resultados de la Consulta</div>', unsafe_allow_html=True)

if not df.empty:
    disp = df[["Proyecto","ETAPA","MATERIAL","ENSAYO","NTC","FRECUENCIA","MesNombre","Estado"]].copy()
    disp.columns = ["Proyecto","Etapa","Material","Ensayo","NTC","Frecuencia","Mes","Estado"]

    # Botón de descarga Excel
    col_dl, col_info = st.columns([1, 3])
    with col_dl:
        st.download_button(
            label="⬇ Descargar Excel",
            data=to_excel(disp),
            file_name="consulta_ensayos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_excel",
        )
    with col_info:
        st.markdown(
            f'<div style="padding:10px 0;font-size:12px;color:#9CA3AF;">'
            f'Mostrando <strong style="color:#374151">{min(200, len(disp))}</strong> de '
            f'<strong style="color:#374151">{len(disp):,}</strong> registros. '
            f'El Excel incluye el total completo.</div>',
            unsafe_allow_html=True)

    # Tabla (primeros 200 registros para rendimiento)
    prev = disp.head(200)
    rows = "".join(
        f"<tr><td>{r.Proyecto}</td><td>{r.Etapa}</td><td>{r.Material}</td>"
        f"<td>{r.Ensayo}</td><td>{r.NTC}</td>"
        f"<td style='max-width:200px;white-space:normal;font-size:11px;color:#9CA3AF'>{r.Frecuencia}</td>"
        f"<td>{r.Mes}</td><td>{badge(r.Estado)}</td></tr>"
        for _, r in prev.iterrows()
    )
    st.markdown(
        f'<div style="overflow-x:auto;border-radius:10px;border:1px solid #E5E9F0;max-height:560px;overflow-y:auto;">'
        f'<table class="rt"><thead><tr>'
        f'<th>Proyecto</th><th>Etapa</th><th>Material</th><th>Ensayo</th>'
        f'<th>NTC</th><th>Frecuencia</th><th>Mes</th><th>Estado</th>'
        f'</tr></thead><tbody>{rows}</tbody></table></div>',
        unsafe_allow_html=True)
else:
    st.info("ℹ️ No se encontraron ensayos con los filtros aplicados.")

st.markdown('</div>', unsafe_allow_html=True)
