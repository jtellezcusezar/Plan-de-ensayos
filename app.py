import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Plan de Ensayos 2026", page_icon="🏗️",
    layout="wide", initial_sidebar_state="collapsed",
)

# ── CONSTANTES ─────────────────────────────────────────────────────────────────
MESES = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
         7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}
ESTADO_MAP = {"*":"Planeado", 0:"No Realizado", 0.5:"Incompleto", 1:"Completo"}
META = 90

COLORS = {
    "Planeado":     "#7BA7D4",
    "Completo":     "#6BBF9E",
    "Incompleto":   "#E8C17A",
    "No Realizado": "#D98B8B",
}

# ── PLOTLY LAYOUT BASE ─────────────────────────────────────────────────────────
# No incluye 'legend' para evitar conflictos al llamar update_layout
BASE_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#374151", size=12),
    margin=dict(t=40, b=10, l=10, r=10),
    hoverlabel=dict(
        bgcolor="#1E293B", font_color="#F1F5F9",
        font_size=12, bordercolor="#334155",
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
            legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=11))
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
.filter-bar{background:#fff;border:1px solid #E5E9F0;border-radius:14px;padding:14px 20px 18px;margin-bottom:20px;box-shadow:0 1px 4px rgba(15,23,42,.05);}
.filter-bar-title{font-size:10px;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:.08em;margin-bottom:12px;padding-bottom:10px;border-bottom:1px solid #F3F4F6;}
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
.dash-card{background:#fff;border:1px solid #E5E9F0;border-radius:14px;padding:20px 22px;box-shadow:0 1px 4px rgba(15,23,42,.05);margin-bottom:18px;}
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
.h100{background:#B8E4D0;color:#2D6A4F;}.h75{background:#D5EFE3;color:#3D8B6E;}.h50{background:#FBEFD4;color:#9A6F1E;}.h25{background:#F6D9D9;color:#9B3B3B;}.h0{background:#F0C8C8;color:#8B2B2B;}.hna{background:#F8F9FB;color:#C4CAD4;font-family:'Inter',sans-serif;font-weight:500;font-size:11px;}
.badge{display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;}
.bc{background:#E4F4EE;color:#3D8B6E;}.bi{background:#FBF3E0;color:#C49A3C;}.bn{background:#F8E8E8;color:#B05B5B;}.bp{background:#EEF3FA;color:#4A7BA8;}
.rt{width:100%;border-collapse:collapse;font-size:13px;}
.rt th{background:#F8F9FB;padding:10px 14px;text-align:left;font-size:10px;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:.05em;border-bottom:1px solid #E5E9F0;white-space:nowrap;}
.rt td{padding:10px 14px;border-bottom:1px solid #F3F4F6;color:#6B7280;}
.rt td:first-child{color:#111827;font-weight:600;}.rt tr:last-child td{border-bottom:none;}.rt tr:hover td{background:#FAFBFC;}
.hml{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px;align-items:center;}
.hml span{font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;}
div[data-testid="stDownloadButton"] button{background:#EEF3FA!important;color:#4A7BA8!important;border:1.5px solid #C8DCF0!important;border-radius:8px!important;font-size:12px!important;font-weight:600!important;padding:6px 14px!important;}
div[data-testid="stDownloadButton"] button:hover{background:#7BA7D4!important;color:#fff!important;}
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
meses_con_datos = sorted(df_full[df_full["EsEjecutado"]]["Mes"].unique().tolist())
mes_label = " – ".join([MESES[meses_con_datos[0]], MESES[meses_con_datos[-1]]]) if len(meses_con_datos) > 1 else MESES[meses_con_datos[0]]

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
    plan = int(len(df))
    pend = int((df["Cantidad"] == "*").sum())
    tot  = comp + inc + no_r
    tasa = round(comp / tot * 100, 1) if tot > 0 else 0.0
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

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
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

tab1, tab2, tab3, tab4 = st.tabs([
    "📊  Resumen General",
    "🏗️  Por Proyecto y Material",
    "📅  Línea de Tiempo y Alertas",
    "🔍  Consulta de Ensayos",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="filter-bar"><div class="filter-bar-title">⚙ Filtros</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    sel_proy  = c1.selectbox("Proyecto", ALL_P,  key="t1p")
    sel_etapa = c2.selectbox("Etapa",    ALL_E,  key="t1e")
    sel_mes   = c3.selectbox("Mes",      ALL_M,  key="t1m")
    st.markdown('</div>', unsafe_allow_html=True)

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
        st.markdown('<div class="dash-card"><div class="card-title">Distribución por Estado</div><div class="card-sub">Total de registros en el plan</div>', unsafe_allow_html=True)
        ec = df1["Estado"].value_counts().reset_index()
        ec.columns = ["Estado","n"]
        ec["C"] = ec["Estado"].map(COLORS)
        fig_donut = go.Figure(go.Pie(
            labels=ec["Estado"], values=ec["n"], hole=0.70,
            marker_colors=ec["C"].tolist(),
            textinfo="percent",
            textposition="inside",
            insidetextorientation="horizontal",
            hovertemplate="<b>%{label}</b><br>%{value:,} · %{percent}<extra></extra>",
        ))
        # Aplicar layout sin legend primero, luego agregar legend vertical y annotations
        apply_base(fig_donut, h=270, legend_h=False)
        fig_donut.update_layout(
            showlegend=True,
            legend=dict(orientation="v", x=1.02, y=0.5, font=dict(size=12)),
            annotations=[dict(text=f"<b>{len(df1):,}</b>", x=0.5, y=0.5,
                              font_size=16, showarrow=False, font_color="#111827")],
        )
        st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Barras por proyecto ──
    with d2:
        st.markdown('<div class="dash-card"><div class="card-title">Avance por Proyecto</div><div class="card-sub">Proyectos con ensayos ejecutados · ordenado por tasa de cumplimiento</div>', unsafe_allow_html=True)
        ex1 = df1[df1["EsEjecutado"] & (df1["Estado"] != "Planeado")]
        if not ex1.empty:
            orden = (ex1.groupby("Proyecto")
                       .apply(lambda g: (g["Cantidad_num"]==1).sum() / len(g) * 100)
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
            fig_proy.update_layout(xaxis=dict(title="", gridcolor="#F3F4F6"),
                                   yaxis=dict(title="", gridwidth=0))
            st.plotly_chart(fig_proy, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Línea temporal ──
    st.markdown('<div class="dash-card"><div class="card-title">Ensayos por Mes — 2026</div><div class="card-sub">Líneas sólidas = ejecutados por estado · Punteada = total planeado del mes · Curva suavizada</div>', unsafe_allow_html=True)
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
    for est, fc in [("Completo","rgba(107,191,158,.15)"), ("Incompleto",None), ("No Realizado",None)]:
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
    fig_line.update_layout(xaxis=dict(gridcolor="#F3F4F6"), yaxis=dict(gridcolor="#F3F4F6"))
    st.plotly_chart(fig_line, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="filter-bar"><div class="filter-bar-title">⚙ Filtros</div>', unsafe_allow_html=True)
    f2a, f2b, f2c = st.columns(3)
    sel2_proy  = f2a.selectbox("Proyecto", ALL_P,   key="t2p")
    sel2_etapa = f2b.selectbox("Etapa",    ALL_E,   key="t2e")
    sel2_mat   = f2c.selectbox("Material", ALL_MAT, key="t2m")
    st.markdown('</div>', unsafe_allow_html=True)

    df2 = filt(filt(filt(df_full, "Proyecto", sel2_proy, "Todos"), "ETAPA", sel2_etapa, "Todas"), "MATERIAL", sel2_mat, "Todos")
    ex2 = df2[df2["EsEjecutado"]].copy()

    # ── Heatmap ──
    st.markdown('<div class="dash-card"><div class="card-title">Heatmap de Cumplimiento — Proyecto × Mes</div><div class="card-sub">Tasa = promedio de valores ejecutados (0, 0.5, 1). "Plan." = sin datos ejecutados ese mes.</div>', unsafe_allow_html=True)
    st.markdown(f"""<div class="hml">
      <span style="background:#B8E4D0;color:#2D6A4F;">≥ 90%</span>
      <span style="background:#D5EFE3;color:#3D8B6E;">70–89%</span>
      <span style="background:#FBEFD4;color:#9A6F1E;">50–69%</span>
      <span style="background:#F6D9D9;color:#9B3B3B;">25–49%</span>
      <span style="background:#F0C8C8;color:#8B2B2B;">&lt; 25%</span>
      <span style="background:#F8F9FB;color:#9CA3AF;">Sin datos</span>
      <span style="font-size:11px;color:#9CA3AF;margin-left:4px;">· Meta: {META}%</span>
    </div>""", unsafe_allow_html=True)

    rows_hm = []
    for p in sorted(df2["Proyecto"].unique()):
        r = f'<tr><td class="hmpn">{p}</td>'
        for m in range(1, 13):
            sub_hm = ex2[(ex2["Proyecto"]==p) & (ex2["Mes"]==m)]
            if len(sub_hm) == 0:
                has_plan = len(df2[(df2["Proyecto"]==p) & (df2["Mes"]==m) & (df2["Cantidad"]=="*")]) > 0
                r += '<td class="hna">Plan.</td>' if has_plan else '<td class="hna">—</td>'
            else:
                cn = int((sub_hm["Cantidad_num"]==1).sum())
                iN = int((sub_hm["Cantidad_num"]==0.5).sum())
                nn = int((sub_hm["Cantidad_num"]==0).sum())
                prom = sub_hm["Cantidad_num"].mean()
                t = round(prom * 100, 1) if pd.notna(prom) else 0.0
                r += f'<td class="{hm_cls(t)}" title="{cn} compl. · {iN} incompl. · {nn} no-real · Promedio: {prom:.2f}">{t:.0f}%</td>'
        r += "</tr>"
        rows_hm.append(r)

    ths = "".join(f"<th>{MESES[m][:3]}</th>" for m in range(1, 13))
    st.markdown(
        f'<div class="hm-wrap"><table class="hm-table"><thead><tr><th class="hmp">Proyecto</th>{ths}</tr></thead>'
        f'<tbody>{"".join(rows_hm)}</tbody></table></div>',
        unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Tasa por proyecto ──
    st.markdown(f'<div class="dash-card"><div class="card-title">Tasa de Cumplimiento por Proyecto</div><div class="card-sub">% de completos sobre el total del plan, incluidos planeados · Meta: {META}%</div>', unsafe_allow_html=True)
    if not df2.empty:
        t_df = (df2.groupby("Proyecto")
                   .apply(lambda g: pd.Series({
                       "tasa": round((g["Cantidad_num"] == 1).sum() / len(g) * 100, 1) if len(g) > 0 else 0.0,
                       "comp": int((g["Cantidad_num"] == 1).sum()),
                       "plan": int((g["Cantidad"] == "*").sum()),
                       "tot": len(g),
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
            textfont=dict(size=11, color="#6B7280"),
            customdata=t_df[["comp", "plan", "tot"]].values,
            hovertemplate="<b>%{y}</b><br>Cumplimiento: %{x:.1f}%<br>Completos: %{customdata[0]}<br>Planeados: %{customdata[1]}<br>Total plan: %{customdata[2]}<extra></extra>",
        ))
        fig_tasa.add_vline(x=META, line_dash="dot", line_color="#7BA7D4", line_width=1.5,
                           annotation_text=f"Meta {META}%",
                           annotation_font_color="#7BA7D4", annotation_font_size=10,
                           annotation_position="top right")
        apply_base(fig_tasa, h=340, legend_h=False)
        fig_tasa.update_layout(
            showlegend=False,
            xaxis=dict(range=[0,115], gridcolor="#F3F4F6", ticksuffix="%", title=""),
            yaxis=dict(gridwidth=0, title=""),
        )
        st.plotly_chart(fig_tasa, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="filter-bar"><div class="filter-bar-title">⚙ Filtros</div>', unsafe_allow_html=True)
    f3a, f3b = st.columns([2, 1])
    sel3_proy = f3a.selectbox("Proyecto",      ALL_P,  key="t3p")
    sel3_mes  = f3b.selectbox("Mes con datos", ["Todos"] + [MESES[m] for m in meses_con_datos], key="t3m")
    st.markdown('</div>', unsafe_allow_html=True)

    df3 = filt(df_full, "Proyecto", sel3_proy, "Todos")
    sm3 = meses_con_datos if sel3_mes == "Todos" else [k for k, v in MESES.items() if v == sel3_mes]

    # Semáforo
    tasa3 = (df3[df3["EsEjecutado"]]
               .groupby("Proyecto")
               .apply(lambda g: pd.Series({
                   "tasa": round((g["Cantidad_num"]==1).sum()/len(g)*100, 1) if len(g) > 0 else 0.0,
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
    st.markdown('<div class="dash-card"><div class="card-title">Evolución Acumulada por Estado</div><div class="card-sub">Progresión mensual · curvas suavizadas</div>', unsafe_allow_html=True)
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
    st.markdown('<div class="dash-card"><div class="card-title">🚨 Ensayos Críticos — No Realizados</div><div class="card-sub">Ensayos con valor = 0 en el período analizado</div>', unsafe_allow_html=True)
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

    st.markdown('<div class="filter-bar"><div class="filter-bar-title">⚙ Filtros de búsqueda</div>', unsafe_allow_html=True)
    q1, q2, q3 = st.columns(3)
    sel4_proy  = q1.selectbox("Proyecto",  ALL_P,   key="t4p")
    sel4_etapa = q1.selectbox("Etapa",     ALL_E,   key="t4e")
    sel4_mes   = q2.selectbox("Mes",       ALL_M,   key="t4m")
    sel4_mat   = q2.selectbox("Material",  ALL_MAT, key="t4mat")
    sel4_est   = q3.selectbox("Estado",    ALL_EST, key="t4est")
    buscar     = q3.text_input("🔎 Buscar por nombre de ensayo",
                               placeholder="Ej: resistencia, fraguado, granulometría...")
    st.markdown('</div>', unsafe_allow_html=True)

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
    st.markdown('<div class="dash-card"><div class="card-title">Resultados de la Consulta</div>', unsafe_allow_html=True)

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

