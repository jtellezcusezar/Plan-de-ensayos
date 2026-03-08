import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime

# ─── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Plan de Ensayos 2026",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CONSTANTS ────────────────────────────────────────────────────────────────
MESES = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
         7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}

ESTADO_MAP = {"*": "Planeado", 0: "No Realizado", 0.5: "Incompleto", 1: "Completo"}

COLORS = {
    "Planeado":     "#2563EB",
    "Completo":     "#059669",
    "Incompleto":   "#D97706",
    "No Realizado": "#DC2626",
}

LIGHT = {
    "Planeado":     "#DBEAFE",
    "Completo":     "#D1FAE5",
    "Incompleto":   "#FEF3C7",
    "No Realizado": "#FEE2E2",
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#0F172A"),
    margin=dict(t=30, b=10, l=10, r=10),
    hoverlabel=dict(
        bgcolor="#0F172A",
        font_color="#F8FAFC",
        font_size=12,
        bordercolor="#0F172A",
    ),
)

# ─── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0rem !important; max-width: 100% !important; padding-left: 2rem !important; padding-right: 2rem !important; }
[data-testid="stSidebar"] { display: none; }

/* ── APP HEADER ── */
.app-header {
    background: #FFFFFF;
    border-bottom: 1px solid #E2E7F0;
    padding: 14px 32px;
    display: flex; align-items: center; justify-content: space-between;
    margin: -1rem -2rem 0 -2rem;
    position: sticky; top: 0; z-index: 100;
    box-shadow: 0 1px 4px rgba(15,23,42,.06);
}
.app-header-left { display: flex; align-items: center; gap: 12px; }
.logo-box {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #6366F1, #2563EB);
    border-radius: 10px; display: flex; align-items: center;
    justify-content: center; font-size: 18px;
}
.app-title { font-size: 16px; font-weight: 700; color: #0F172A; margin: 0; }
.app-sub { font-size: 11px; color: #94A3B8; font-weight: 500; text-transform: uppercase; letter-spacing: .04em; margin: 0; }
.header-badge { background: #EEF2FF; color: #6366F1; font-size: 12px; font-weight: 600; padding: 4px 12px; border-radius: 20px; }
.header-date { font-size: 12px; color: #94A3B8; font-family: 'DM Mono', monospace; }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: #FFFFFF;
    border-bottom: 1px solid #E2E7F0;
    padding: 0 0px;
    gap: 0;
    margin: 0 -2rem;
    padding-left: 2rem;
}
.stTabs [data-baseweb="tab"] {
    font-size: 13px !important; font-weight: 600 !important;
    color: #94A3B8 !important;
    padding: 14px 22px !important;
    border-bottom: 2px solid transparent !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #6366F1 !important;
    border-bottom-color: #6366F1 !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 24px; }
.stTabs [data-baseweb="tab-highlight"] { display: none; }

/* ── FILTER BAR ── */
.filter-bar {
    background: #FFFFFF; border: 1px solid #E2E7F0;
    border-radius: 12px; padding: 14px 20px;
    margin-bottom: 20px;
    box-shadow: 0 1px 3px rgba(15,23,42,.05);
}
.filter-bar-title {
    font-size: 11px; font-weight: 700; color: #94A3B8;
    text-transform: uppercase; letter-spacing: .06em; margin-bottom: 10px;
}
div[data-testid="stMultiSelect"] > div { border-radius: 8px !important; border-color: #E2E7F0 !important; }
div[data-testid="stMultiSelect"] > div:focus-within { border-color: #6366F1 !important; box-shadow: none !important; }

/* ── KPI CARDS ── */
.kpi-card {
    background: #FFFFFF; border: 1px solid #E2E7F0;
    border-radius: 14px; padding: 18px 20px;
    position: relative; overflow: hidden;
    box-shadow: 0 1px 3px rgba(15,23,42,.05);
    transition: transform .15s, box-shadow .15s;
    height: 100%;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(15,23,42,.08); }
.kpi-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; }
.kpi-blue::before   { background: #2563EB; }
.kpi-green::before  { background: #059669; }
.kpi-yellow::before { background: #D97706; }
.kpi-red::before    { background: #DC2626; }
.kpi-purple::before { background: #6366F1; }
.kpi-icon  { font-size: 20px; margin-bottom: 8px; }
.kpi-label { font-size: 11px; font-weight: 600; color: #94A3B8; text-transform: uppercase; letter-spacing: .04em; margin-bottom: 4px; }
.kpi-value { font-size: 28px; font-weight: 800; line-height: 1; font-family: 'DM Mono', monospace; }
.kpi-sub   { font-size: 11px; color: #94A3B8; margin-top: 4px; }
.kpi-blue   .kpi-value { color: #2563EB; }
.kpi-green  .kpi-value { color: #059669; }
.kpi-yellow .kpi-value { color: #D97706; }
.kpi-red    .kpi-value { color: #DC2626; }
.kpi-purple .kpi-value { color: #6366F1; }

/* ── CARDS ── */
.dash-card {
    background: #FFFFFF; border: 1px solid #E2E7F0;
    border-radius: 14px; padding: 20px 22px;
    box-shadow: 0 1px 3px rgba(15,23,42,.05);
    margin-bottom: 18px;
}
.card-title { font-size: 14px; font-weight: 700; color: #0F172A; margin-bottom: 2px; }
.card-sub   { font-size: 11px; color: #94A3B8; margin-bottom: 16px; }

/* ── INFO NOTE ── */
.info-note {
    display: flex; align-items: center; gap: 8px;
    padding: 9px 14px; background: #EEF2FF;
    border: 1px solid #C7D2FE; border-radius: 8px;
    font-size: 12px; color: #4338CA; font-weight: 500;
    margin-bottom: 18px;
}

/* ── SEMAFORO ── */
.sem-grid { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 18px; }
.sem-card {
    background: #FFFFFF; border: 1px solid #E2E7F0;
    border-radius: 10px; padding: 12px 16px;
    box-shadow: 0 1px 3px rgba(15,23,42,.05);
    min-width: 160px; position: relative; overflow: hidden;
}
.sem-card::after { content:''; position:absolute; bottom:0; left:0; right:0; height:3px; }
.sem-verde  .sem-card-inner .sem-tasa { color: #059669; }
.sem-verde::after  { background: #059669; }
.sem-amarillo .sem-card-inner .sem-tasa { color: #D97706; }
.sem-amarillo::after { background: #D97706; }
.sem-rojo   .sem-card-inner .sem-tasa { color: #DC2626; }
.sem-rojo::after   { background: #DC2626; }
.sem-dot { width:9px; height:9px; border-radius:50%; display:inline-block; margin-right:5px; }
.sem-name { font-size: 12px; font-weight: 700; color: #0F172A; margin-bottom: 5px; }
.sem-tasa { font-size: 21px; font-weight: 800; font-family: 'DM Mono', monospace; }
.sem-detail { font-size: 11px; color: #94A3B8; margin-top: 2px; }

/* ── HEATMAP TABLE ── */
.hm-wrap { overflow-x: auto; border-radius: 10px; border: 1px solid #E2E7F0; }
.hm-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.hm-table th { background: #F0F2F8; padding: 8px 10px; text-align: center; font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: .04em; border-bottom: 1px solid #E2E7F0; white-space: nowrap; }
.hm-table th.hm-proj { text-align: left; min-width: 160px; padding-left: 14px; }
.hm-table td { padding: 7px 10px; text-align: center; font-weight: 700; font-family: 'DM Mono', monospace; border-bottom: 1px solid #F0F2F8; }
.hm-table td.hm-pname { text-align: left; font-family: 'Inter', sans-serif; font-size: 12px; padding-left: 14px; color: #0F172A; font-weight: 600; }
.hm-table tr:last-child td { border-bottom: none; }
.h100 { background:#A7F3D0; color:#065F46; } .h75  { background:#D1FAE5; color:#047857; }
.h50  { background:#FEF3C7; color:#92400E; } .h25  { background:#FECACA; color:#991B1B; }
.h0   { background:#FEE2E2; color:#DC2626; } .hna  { background:#F0F2F8; color:#94A3B8; font-family:'Inter',sans-serif; font-weight:500; font-size:11px; }

/* ── STATUS BADGE ── */
.badge { display:inline-flex; align-items:center; gap:4px; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:700; }
.badge-comp { background:#D1FAE5; color:#059669; }
.badge-inc  { background:#FEF3C7; color:#D97706; }
.badge-nor  { background:#FEE2E2; color:#DC2626; }
.badge-pla  { background:#DBEAFE; color:#2563EB; }

/* ── RESULTS TABLE ── */
.res-table { width:100%; border-collapse:collapse; font-size:13px; }
.res-table th { background:#F0F2F8; padding:10px 14px; text-align:left; font-size:11px; font-weight:700; color:#64748B; text-transform:uppercase; letter-spacing:.05em; border-bottom:1px solid #E2E7F0; white-space:nowrap; }
.res-table td { padding:10px 14px; border-bottom:1px solid #F0F2F8; color:#64748B; }
.res-table td:first-child { color:#0F172A; font-weight:600; }
.res-table tr:last-child td { border-bottom:none; }
.res-table tr:hover td { background:#F8FAFC; }

/* Streamlit element tweaks */
div[data-testid="stDataFrame"] { border-radius: 10px; border: 1px solid #E2E7F0; overflow: hidden; }
div[data-testid="metric-container"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ─── DATA LOADING ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("Plan_de_ensayos_2026.xlsx", sheet_name="Ensayos", header=0)
    df["Proyecto"]  = df["Proyecto"].str.strip()
    df["MATERIAL"]  = df["MATERIAL"].str.strip()
    df["ETAPA"]     = df["ETAPA"].str.strip()
    df["ENSAYO"]    = df["ENSAYO"].str.strip()
    df["NTC"]       = df["NTC"].str.strip()
    df["FRECUENCIA"]= df["FRECUENCIA"].str.strip()
    df["MesNombre"] = df["Mes"].map(MESES)
    df["Estado"]    = df["Cantidad"].map(lambda x: ESTADO_MAP.get(x, str(x)))
    # Executed = not planned
    df["EsEjecutado"] = df["Cantidad"] != "*"
    df["Cantidad_num"] = pd.to_numeric(df["Cantidad"], errors="coerce")
    return df

df_full = load_data()

# Determine months with executed data
meses_con_datos = sorted(df_full[df_full["EsEjecutado"]]["Mes"].unique().tolist())
mes_actual_label = f"{MESES[meses_con_datos[0]]} – {MESES[meses_con_datos[-1]]}" if len(meses_con_datos) > 1 else MESES[meses_con_datos[0]]

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def kpi_card(icon, label, value, sub, color_class):
    return f"""
    <div class="kpi-card {color_class}">
      <div class="kpi-icon">{icon}</div>
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      <div class="kpi-sub">{sub}</div>
    </div>"""

def compute_kpis(df):
    ex = df[df["EsEjecutado"]]
    comp  = int((ex["Cantidad_num"] == 1).sum())
    inc   = int((ex["Cantidad_num"] == 0.5).sum())
    no_r  = int((ex["Cantidad_num"] == 0).sum())
    plan  = int((df["Cantidad"] == "*").sum())
    total_exec = comp + inc + no_r
    tasa  = round(comp / total_exec * 100, 1) if total_exec > 0 else 0.0
    return comp, inc, no_r, plan, total_exec, tasa

def heatmap_class(tasa):
    if tasa is None: return "hna"
    if tasa >= 90:   return "h100"
    if tasa >= 70:   return "h75"
    if tasa >= 50:   return "h50"
    if tasa >= 25:   return "h25"
    return "h0"

def tasa_proj(df):
    ex = df[df["EsEjecutado"]]
    g = ex.groupby("Proyecto")["Cantidad_num"].agg(
        completo=lambda x: (x==1).sum(),
        total="count"
    ).reset_index()
    g["tasa"] = g.apply(lambda r: round(r.completo/r.total*100,1) if r.total>0 else 0.0, axis=1)
    return g.sort_values("tasa", ascending=False)

def badge_html(estado):
    cls = {"Completo":"badge-comp","Incompleto":"badge-inc","No Realizado":"badge-nor","Planeado":"badge-pla"}.get(estado,"badge-pla")
    ico = {"Completo":"✅","Incompleto":"⚠️","No Realizado":"❌","Planeado":"🔵"}.get(estado,"🔵")
    return f'<span class="badge {cls}">{ico} {estado}</span>'

def sem_html(name, tasa, ejecutables, criticos):
    if tasa >= 70: cls, dot_color = "sem-verde", "#059669"
    elif tasa >= 50: cls, dot_color = "sem-amarillo", "#D97706"
    else: cls, dot_color = "sem-rojo", "#DC2626"
    tasa_str = f"{tasa:.1f}%" if tasa > 0 else "0%"
    return f"""
    <div class="sem-card {cls}">
      <div class="sem-name"><span class="sem-dot" style="background:{dot_color}"></span>{name}</div>
      <div class="sem-tasa">{tasa_str}</div>
      <div class="sem-detail">{ejecutables} ejecutables · {criticos} crítico{'s' if criticos!=1 else ''}</div>
    </div>"""

# ─── APP HEADER ───────────────────────────────────────────────────────────────
n_proyectos = df_full["Proyecto"].nunique()
total_rows   = len(df_full)
now_str      = datetime.date.today().strftime("%b %Y")

st.markdown(f"""
<div class="app-header">
  <div class="app-header-left">
    <div class="logo-box">🏗️</div>
    <div>
      <p class="app-title">Plan de Ensayos 2026</p>
      <p class="app-sub">Panel de Control de Calidad · Cusezar</p>
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:14px;">
    <span class="header-badge">{n_proyectos} Proyectos · {total_rows:,} Ensayos</span>
    <span class="header-date">Datos hasta: {mes_actual_label}</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊  Resumen General",
    "🏗️  Por Proyecto y Material",
    "📅  Línea de Tiempo y Alertas",
    "🔍  Consulta de Ensayos",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — RESUMEN GENERAL
# ══════════════════════════════════════════════════════════════════════════════
with tab1:

    # ── FILTROS ──
    st.markdown('<div class="filter-bar"><div class="filter-bar-title">🔧 Filtros</div>', unsafe_allow_html=True)
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        all_proyectos = sorted(df_full["Proyecto"].unique().tolist())
        sel_proy = st.multiselect("Proyectos", all_proyectos, default=all_proyectos, key="t1_proy", placeholder="Todos los proyectos")
    with fc2:
        all_etapas = sorted(df_full["ETAPA"].unique().tolist())
        sel_etapa = st.multiselect("Etapa", all_etapas, default=all_etapas, key="t1_etapa", placeholder="Todas las etapas")
    with fc3:
        all_meses = list(MESES.values())
        sel_meses = st.multiselect("Meses", all_meses, default=all_meses, key="t1_mes", placeholder="Todos los meses")
    st.markdown('</div>', unsafe_allow_html=True)

    # Apply filters
    sel_proy_  = sel_proy  if sel_proy  else all_proyectos
    sel_etapa_ = sel_etapa if sel_etapa else all_etapas
    sel_meses_ = sel_meses if sel_meses else all_meses
    sel_mes_nums = [k for k,v in MESES.items() if v in sel_meses_]

    df = df_full[
        df_full["Proyecto"].isin(sel_proy_) &
        df_full["ETAPA"].isin(sel_etapa_) &
        df_full["Mes"].isin(sel_mes_nums)
    ]

    # Info note
    st.markdown(f'<div class="info-note">ℹ️ Indicadores de cumplimiento calculados sobre meses con datos ejecutados (<strong>{mes_actual_label} 2026</strong>). Los ensayos planeados (*) se excluyen del cálculo de tasa.</div>', unsafe_allow_html=True)

    # ── KPIs ──
    comp, inc, no_r, plan, total_exec, tasa = compute_kpis(df)
    k1,k2,k3,k4,k5 = st.columns(5)
    k1.markdown(kpi_card("📋","Planeados",   f"{plan:,}", "Sin ejecutar en 2026", "kpi-blue"),   unsafe_allow_html=True)
    k2.markdown(kpi_card("✅","Completos",   f"{comp:,}", f"{comp/total_exec*100:.1f}% del ejecutable" if total_exec else "—", "kpi-green"),  unsafe_allow_html=True)
    k3.markdown(kpi_card("⚠️","Incompletos", f"{inc:,}",  f"{inc/total_exec*100:.1f}% del ejecutable"  if total_exec else "—", "kpi-yellow"), unsafe_allow_html=True)
    k4.markdown(kpi_card("❌","No Realizados",f"{no_r:,}",f"{no_r/total_exec*100:.1f}% del ejecutable" if total_exec else "—", "kpi-red"),    unsafe_allow_html=True)
    k5.markdown(kpi_card("📈","Tasa Cumplimiento", f"{tasa}%", "Meta: ≥ 70%", "kpi-purple"),    unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    # ── CHARTS ROW 1 ──
    c1, c2 = st.columns([1,1.4])

    with c1:
        st.markdown('<div class="dash-card"><div class="card-title">Distribución por Estado</div><div class="card-sub">Total de registros en el plan</div>', unsafe_allow_html=True)
        estado_counts = df["Estado"].value_counts().reset_index()
        estado_counts.columns = ["Estado","Cantidad"]
        estado_counts["Color"] = estado_counts["Estado"].map(COLORS)
        fig_donut = go.Figure(go.Pie(
            labels=estado_counts["Estado"],
            values=estado_counts["Cantidad"],
            hole=0.68,
            marker_colors=estado_counts["Color"],
            textinfo="none",
            hovertemplate="<b>%{label}</b><br>Cantidad: %{value:,}<br>Porcentaje: %{percent}<extra></extra>",
        ))
        fig_donut.update_layout(**PLOTLY_LAYOUT, height=260,
            showlegend=True,
            legend=dict(orientation="v", x=1.02, y=0.5, font=dict(size=12)),
            annotations=[dict(text=f"<b>{len(df):,}</b><br>total", x=0.5, y=0.5,
                              font_size=14, showarrow=False, font_color="#0F172A")]
        )
        st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar":False})
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="dash-card"><div class="card-title">Avance por Proyecto</div><div class="card-sub">Solo proyectos con ensayos ejecutados · ordenado por tasa de cumplimiento</div>', unsafe_allow_html=True)
        ex_df = df[df["EsEjecutado"]].copy()
        if not ex_df.empty:
            pg = ex_df.groupby(["Proyecto","Estado"])["Cantidad_num"].count().reset_index()
            pg.columns = ["Proyecto","Estado","n"]
            # Tasa para ordenar
            pg_tasa = ex_df.groupby("Proyecto").apply(
                lambda g: (g["Cantidad_num"]==1).sum() / len(g) * 100
            ).reset_index()
            pg_tasa.columns = ["Proyecto","tasa"]
            orden = pg_tasa.sort_values("tasa")["Proyecto"].tolist()
            pg = pg[pg["Estado"] != "Planeado"]
            fig_proj = px.bar(pg, x="n", y="Proyecto", color="Estado",
                              orientation="h", barmode="stack",
                              color_discrete_map=COLORS,
                              category_orders={"Proyecto": orden, "Estado":["No Realizado","Incompleto","Completo"]},
                              custom_data=["Estado","n"])
            fig_proj.update_traces(hovertemplate="<b>%{y}</b><br>%{customdata[0]}: %{customdata[1]}<extra></extra>")
            fig_proj.update_layout(**PLOTLY_LAYOUT, height=260, showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=11)),
                xaxis=dict(title="", gridcolor="#F1F5F9"),
                yaxis=dict(title="", gridwidth=0))
            st.plotly_chart(fig_proj, use_container_width=True, config={"displayModeBar":False})
        st.markdown('</div>', unsafe_allow_html=True)

    # ── LINEA TEMPORAL ──
    st.markdown('<div class="dash-card"><div class="card-title">Ensayos por Mes — 2026</div><div class="card-sub">Líneas sólidas = meses con datos ejecutados. Línea punteada = ensayos planeados (*) en meses futuros.</div>', unsafe_allow_html=True)
    mes_plan  = df[df["Cantidad"]=="*"].groupby("Mes").size().reindex(range(1,13), fill_value=0).reset_index()
    mes_plan.columns = ["Mes","n"]
    mes_exec  = df[df["EsEjecutado"]].copy()

    fig_line = go.Figure()
    # Planeados - dashed
    fig_line.add_trace(go.Scatter(x=mes_plan["Mes"].map(lambda m: MESES[m]), y=mes_plan["n"],
        name="Planeado (*)", mode="lines+markers", line=dict(color=COLORS["Planeado"], width=2, dash="dot"),
        marker=dict(size=6), hovertemplate="<b>%{x}</b><br>Planeados: %{y}<extra></extra>"))

    for estado, color in [("Completo",COLORS["Completo"]),("Incompleto",COLORS["Incompleto"]),("No Realizado",COLORS["No Realizado"])]:
        sub = mes_exec[mes_exec["Estado"]==estado].groupby("Mes").size().reindex(meses_con_datos, fill_value=0).reset_index()
        sub.columns = ["Mes","n"]
        fig_line.add_trace(go.Scatter(
            x=sub["Mes"].map(lambda m: MESES[m]), y=sub["n"],
            name=estado, mode="lines+markers",
            line=dict(color=color, width=2.5),
            marker=dict(size=7),
            fill="tozeroy" if estado=="Completo" else None,
            fillcolor="rgba(5,150,105,.10)" if estado=="Completo" else None,
            hovertemplate=f"<b>%{{x}}</b><br>{estado}: %{{y}}<extra></extra>",
        ))
    fig_line.update_layout(**PLOTLY_LAYOUT, height=290,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=11)),
        xaxis=dict(gridcolor="#F1F5F9"), yaxis=dict(gridcolor="#F1F5F9"))
    st.plotly_chart(fig_line, use_container_width=True, config={"displayModeBar":False})
    st.markdown('</div>', unsafe_allow_html=True)

    # ── MATERIAL + ETAPA ──
    m1, m2 = st.columns(2)

    with m1:
        st.markdown('<div class="dash-card"><div class="card-title">Estado por Material</div><div class="card-sub">Materiales con ensayos ejecutados</div>', unsafe_allow_html=True)
        mat_ex = df[df["EsEjecutado"] & (df["Estado"]!="Planeado")]
        if not mat_ex.empty:
            mg = mat_ex.groupby(["MATERIAL","Estado"])["Cantidad_num"].count().reset_index()
            mg.columns = ["Material","Estado","n"]
            fig_mat = px.bar(mg, x="Material", y="n", color="Estado", barmode="stack",
                             color_discrete_map=COLORS,
                             category_orders={"Estado":["No Realizado","Incompleto","Completo"]})
            fig_mat.update_traces(hovertemplate="<b>%{x}</b><br>%{data.name}: %{y}<extra></extra>")
            fig_mat.update_layout(**PLOTLY_LAYOUT, height=290,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=11)),
                xaxis=dict(title="", gridcolor="#F1F5F9", tickangle=-30),
                yaxis=dict(title="", gridcolor="#F1F5F9"))
            st.plotly_chart(fig_mat, use_container_width=True, config={"displayModeBar":False})
        st.markdown('</div>', unsafe_allow_html=True)

    with m2:
        st.markdown('<div class="dash-card"><div class="card-title">Cumplimiento por Etapa</div><div class="card-sub">Estructura vs Obra Gris</div>', unsafe_allow_html=True)
        eta_ex = df[df["EsEjecutado"] & (df["Estado"]!="Planeado")]
        if not eta_ex.empty:
            eg = eta_ex.groupby(["ETAPA","Estado"])["Cantidad_num"].count().reset_index()
            eg.columns = ["Etapa","Estado","n"]
            fig_eta = px.bar(eg, x="Etapa", y="n", color="Estado", barmode="stack",
                             color_discrete_map=COLORS,
                             category_orders={"Estado":["No Realizado","Incompleto","Completo"]})
            fig_eta.update_layout(**PLOTLY_LAYOUT, height=290,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=11)),
                xaxis=dict(title="", gridcolor="#F1F5F9"),
                yaxis=dict(title="", gridcolor="#F1F5F9"))
            st.plotly_chart(fig_eta, use_container_width=True, config={"displayModeBar":False})
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — POR PROYECTO Y MATERIAL
# ══════════════════════════════════════════════════════════════════════════════
with tab2:

    st.markdown('<div class="filter-bar"><div class="filter-bar-title">🔧 Filtros</div>', unsafe_allow_html=True)
    f2c1, f2c2, f2c3 = st.columns(3)
    with f2c1:
        sel2_proy = st.multiselect("Proyectos", all_proyectos, default=all_proyectos, key="t2_proy", placeholder="Todos")
    with f2c2:
        sel2_etapa = st.multiselect("Etapa", all_etapas, default=all_etapas, key="t2_etapa", placeholder="Todas")
    with f2c3:
        all_mats = sorted(df_full["MATERIAL"].unique().tolist())
        sel2_mat = st.multiselect("Material", all_mats, default=all_mats, key="t2_mat", placeholder="Todos")
    st.markdown('</div>', unsafe_allow_html=True)

    sel2_proy_  = sel2_proy  if sel2_proy  else all_proyectos
    sel2_etapa_ = sel2_etapa if sel2_etapa else all_etapas
    sel2_mat_   = sel2_mat   if sel2_mat   else all_mats

    df2 = df_full[
        df_full["Proyecto"].isin(sel2_proy_) &
        df_full["ETAPA"].isin(sel2_etapa_) &
        df_full["MATERIAL"].isin(sel2_mat_)
    ]

    # ── HEATMAP PROYECTO × MES ──
    st.markdown('<div class="dash-card"><div class="card-title">Heatmap de Cumplimiento — Proyecto × Mes</div><div class="card-sub">Tasa = Completos ÷ ejecutados (0, 0.5, 1). Planeados (*) excluidos. "Plan." = solo registros planeados sin datos ejecutados.</div>', unsafe_allow_html=True)

    # Legend
    st.markdown("""
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;">
      <span style="background:#A7F3D0;color:#065F46;font-size:11px;font-weight:700;padding:2px 8px;border-radius:4px;">≥ 90%</span>
      <span style="background:#D1FAE5;color:#047857;font-size:11px;font-weight:700;padding:2px 8px;border-radius:4px;">70–89%</span>
      <span style="background:#FEF3C7;color:#92400E;font-size:11px;font-weight:700;padding:2px 8px;border-radius:4px;">50–69%</span>
      <span style="background:#FECACA;color:#991B1B;font-size:11px;font-weight:700;padding:2px 8px;border-radius:4px;">25–49%</span>
      <span style="background:#FEE2E2;color:#DC2626;font-size:11px;font-weight:700;padding:2px 8px;border-radius:4px;">< 25%</span>
      <span style="background:#F0F2F8;color:#94A3B8;font-size:11px;font-weight:500;padding:2px 8px;border-radius:4px;">Sin datos exec.</span>
    </div>
    """, unsafe_allow_html=True)

    # Build heatmap data
    ex2 = df2[df2["EsEjecutado"]].copy()
    proyectos_hm = sorted(df2["Proyecto"].unique())

    hm_rows = []
    for p in proyectos_hm:
        row = f'<tr><td class="hm-pname">{p}</td>'
        for m in range(1, 13):
            sub = ex2[(ex2["Proyecto"]==p) & (ex2["Mes"]==m)]
            if len(sub) == 0:
                # check if there are planned ones
                plan_sub = df2[(df2["Proyecto"]==p) & (df2["Mes"]==m) & (df2["Cantidad"]=="*")]
                if len(plan_sub) > 0:
                    row += '<td class="hna">Plan.</td>'
                else:
                    row += '<td class="hna">—</td>'
            else:
                comp_n  = (sub["Cantidad_num"]==1).sum()
                inc_n   = (sub["Cantidad_num"]==0.5).sum()
                no_n    = (sub["Cantidad_num"]==0).sum()
                total_n = len(sub)
                tasa_hm = round(comp_n/total_n*100, 1) if total_n>0 else 0.0
                cls     = heatmap_class(tasa_hm)
                tooltip = f"title='{comp_n} compl., {inc_n} incompl., {no_n} no-real / {total_n} total'"
                row += f'<td class="{cls}" {tooltip}>{tasa_hm:.0f}%</td>'
        row += "</tr>"
        hm_rows.append(row)

    mes_headers = "".join([f"<th>{MESES[m][:3]}</th>" for m in range(1,13)])
    hm_html = f"""
    <div class="hm-wrap">
      <table class="hm-table">
        <thead><tr><th class="hm-proj">Proyecto</th>{mes_headers}</tr></thead>
        <tbody>{''.join(hm_rows)}</tbody>
      </table>
    </div>"""
    st.markdown(hm_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── MATERIAL + TASA PROYECTO ──
    t2c1, t2c2 = st.columns(2)

    with t2c1:
        st.markdown('<div class="dash-card"><div class="card-title">Estado por Material</div><div class="card-sub">Distribución de estados en ensayos ejecutados</div>', unsafe_allow_html=True)
        mat2_ex = df2[df2["EsEjecutado"] & (df2["Estado"]!="Planeado")]
        if not mat2_ex.empty:
            mg2 = mat2_ex.groupby(["MATERIAL","Estado"])["Cantidad_num"].count().reset_index()
            mg2.columns = ["Material","Estado","n"]
            fig_mat2 = px.bar(mg2, x="Material", y="n", color="Estado", barmode="stack",
                              color_discrete_map=COLORS,
                              category_orders={"Estado":["No Realizado","Incompleto","Completo"]})
            fig_mat2.update_traces(hovertemplate="<b>%{x}</b><br>%{data.name}: %{y}<extra></extra>")
            fig_mat2.update_layout(**PLOTLY_LAYOUT, height=340,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=11)),
                xaxis=dict(title="", gridcolor="#F1F5F9", tickangle=-30),
                yaxis=dict(title="", gridcolor="#F1F5F9"))
            st.plotly_chart(fig_mat2, use_container_width=True, config={"displayModeBar":False})
        st.markdown('</div>', unsafe_allow_html=True)

    with t2c2:
        st.markdown('<div class="dash-card"><div class="card-title">Tasa de Cumplimiento por Proyecto</div><div class="card-sub">% sobre total ejecutable · 🟢≥70% &nbsp; 🟡50–69% &nbsp; 🔴&lt;50%</div>', unsafe_allow_html=True)
        tasa_df = tasa_proj(df2)
        if not tasa_df.empty:
            bar_colors = tasa_df["tasa"].map(
                lambda t: COLORS["Completo"] if t>=70 else COLORS["Incompleto"] if t>=50 else COLORS["No Realizado"]
            ).tolist()
            fig_tasa = go.Figure(go.Bar(
                x=tasa_df["tasa"], y=tasa_df["Proyecto"],
                orientation="h", marker_color=bar_colors,
                text=tasa_df["tasa"].map(lambda t: f"{t:.1f}%"),
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Cumplimiento: %{x:.1f}%<extra></extra>",
            ))
            fig_tasa.add_vline(x=70, line_dash="dot", line_color="#6366F1", line_width=1.5,
                               annotation_text="Meta 70%", annotation_font_color="#6366F1",
                               annotation_font_size=10)
            fig_tasa.update_layout(**PLOTLY_LAYOUT, height=340,
                showlegend=False,
                xaxis=dict(range=[0,115], gridcolor="#F1F5F9", ticksuffix="%", title=""),
                yaxis=dict(gridwidth=0, title=""))
            st.plotly_chart(fig_tasa, use_container_width=True, config={"displayModeBar":False})
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — LÍNEA DE TIEMPO Y ALERTAS
# ══════════════════════════════════════════════════════════════════════════════
with tab3:

    st.markdown('<div class="filter-bar"><div class="filter-bar-title">🔧 Filtros</div>', unsafe_allow_html=True)
    f3c1, f3c2 = st.columns([2,1])
    with f3c1:
        sel3_proy = st.multiselect("Proyectos", all_proyectos, default=all_proyectos, key="t3_proy", placeholder="Todos")
    with f3c2:
        meses_exec_nombres = [MESES[m] for m in meses_con_datos]
        sel3_mes = st.multiselect("Meses con datos", meses_exec_nombres, default=meses_exec_nombres, key="t3_mes", placeholder="Todos")
    st.markdown('</div>', unsafe_allow_html=True)

    sel3_proy_ = sel3_proy if sel3_proy else all_proyectos
    sel3_mes_nums = [k for k,v in MESES.items() if v in sel3_mes] if sel3_mes else meses_con_datos

    df3 = df_full[
        df_full["Proyecto"].isin(sel3_proy_) &
        df_full["EsEjecutado"] &
        df_full["Mes"].isin(sel3_mes_nums)
    ]

    # ── SEMÁFORO ──
    st.markdown("### Semáforo por Proyecto")
    st.markdown(f"Estado de cumplimiento sobre datos de **{mes_actual_label} 2026**: 🟢 ≥ 70% &nbsp;·&nbsp; 🟡 50–69% &nbsp;·&nbsp; 🔴 < 50%")
    st.markdown("<br>", unsafe_allow_html=True)

    tasa3 = df_full[df_full["EsEjecutado"]].groupby("Proyecto").apply(
        lambda g: pd.Series({
            "tasa": round((g["Cantidad_num"]==1).sum()/len(g)*100,1) if len(g)>0 else 0.0,
            "ejecutables": len(g),
            "criticos": (g["Cantidad_num"]==0).sum()
        })
    ).reset_index()

    sem_cards_html = '<div class="sem-grid">'
    for _, row in tasa3.sort_values("tasa", ascending=False).iterrows():
        sem_cards_html += sem_html(row["Proyecto"], row["tasa"], int(row["ejecutables"]), int(row["criticos"]))
    sem_cards_html += "</div>"
    st.markdown(sem_cards_html, unsafe_allow_html=True)

    # ── ÁREA ACUMULADA ──
    st.markdown('<div class="dash-card"><div class="card-title">Evolución Acumulada por Estado</div><div class="card-sub">Datos registrados por mes en el período analizado</div>', unsafe_allow_html=True)

    area_data = []
    for m in sorted(sel3_mes_nums):
        sub_m = df_full[df_full["EsEjecutado"] & df_full["Proyecto"].isin(sel3_proy_) & (df_full["Mes"]==m)]
        area_data.append({
            "Mes": MESES[m],
            "Completo":     int((sub_m["Cantidad_num"]==1).sum()),
            "Incompleto":   int((sub_m["Cantidad_num"]==0.5).sum()),
            "No Realizado": int((sub_m["Cantidad_num"]==0).sum()),
        })
    area_df = pd.DataFrame(area_data)

    if not area_df.empty:
        # Cumulative
        for col in ["Completo","Incompleto","No Realizado"]:
            area_df[f"{col}_acum"] = area_df[col].cumsum()

        fig_area = go.Figure()
        for estado, color, alpha in [
            ("Completo",COLORS["Completo"],"rgba(5,150,105,.15)"),
            ("Incompleto",COLORS["Incompleto"],"rgba(217,119,6,.10)"),
            ("No Realizado",COLORS["No Realizado"],"rgba(220,38,38,.08)"),
        ]:
            col_acum = f"{estado}_acum"
            total_acum = area_df["Completo_acum"] + area_df["Incompleto_acum"] + area_df["No Realizado_acum"]
            tasa_acum  = (area_df["Completo_acum"] / total_acum * 100).round(1)
            fig_area.add_trace(go.Scatter(
                x=area_df["Mes"], y=area_df[col_acum],
                name=f"{estado} (acum.)", mode="lines+markers",
                line=dict(color=color, width=2.5),
                marker=dict(size=8),
                fill="tozeroy", fillcolor=alpha,
                hovertemplate=(
                    f"<b>%{{x}}</b><br>{estado} acumulado: %{{y}}<br>"
                    "Tasa acum.: " + tasa_acum.astype(str).add("%") + "<extra></extra>"
                ).replace("+ tasa_acum.astype(str).add(\"%\")", ""),
            ))
            # Simpler hover
        fig_area.update_traces(
            hovertemplate="<b>%{x}</b><br>%{data.name}: %{y}<extra></extra>"
        )
        fig_area.update_layout(**PLOTLY_LAYOUT, height=300,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=11)),
            xaxis=dict(gridcolor="#F1F5F9"), yaxis=dict(gridcolor="#F1F5F9"))
        st.plotly_chart(fig_area, use_container_width=True, config={"displayModeBar":False})
    st.markdown('</div>', unsafe_allow_html=True)

    # ── TABLA CRÍTICOS ──
    st.markdown('<div class="dash-card"><div class="card-title">🚨 Ensayos Críticos — No Realizados</div><div class="card-sub">Ensayos con valor = 0 en el período analizado</div>', unsafe_allow_html=True)

    criticos = df_full[
        df_full["EsEjecutado"] &
        (df_full["Cantidad_num"]==0) &
        df_full["Proyecto"].isin(sel3_proy_) &
        df_full["Mes"].isin(sel3_mes_nums)
    ][["Proyecto","ETAPA","MATERIAL","ENSAYO","NTC","MesNombre","Estado"]].copy()
    criticos.columns = ["Proyecto","Etapa","Material","Ensayo","NTC","Mes","Estado"]

    if not criticos.empty:
        # Download button
        csv = criticos.to_csv(index=False).encode("utf-8")
        col_dl, _ = st.columns([1,5])
        with col_dl:
            st.download_button("⬇ Exportar CSV", csv, "ensayos_criticos.csv", "text/csv", key="dl_crit")

        # Render table
        rows_html = ""
        for _, r in criticos.iterrows():
            rows_html += f"<tr><td>{r.Proyecto}</td><td>{r.Etapa}</td><td>{r.Material}</td><td>{r.Ensayo}</td><td>{r.NTC}</td><td>{r.Mes}</td><td>{badge_html(r.Estado)}</td></tr>"
        st.markdown(f"""
        <div style="overflow-x:auto;border-radius:10px;border:1px solid #E2E7F0;">
          <table class="res-table">
            <thead><tr><th>Proyecto</th><th>Etapa</th><th>Material</th><th>Ensayo</th><th>NTC</th><th>Mes</th><th>Estado</th></tr></thead>
            <tbody>{rows_html}</tbody>
          </table>
        </div>""", unsafe_allow_html=True)
    else:
        st.success("✅ No hay ensayos críticos sin realizar en el período seleccionado.")
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — CONSULTA DE ENSAYOS
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 🔍 Consulta de Ensayos")
    st.markdown("Filtra y encuentra exactamente qué ensayos aplican según proyecto, mes y material.")

    st.markdown('<div class="filter-bar"><div class="filter-bar-title">🔧 Filtros de búsqueda</div>', unsafe_allow_html=True)
    q1, q2, q3 = st.columns(3)
    with q1:
        sel4_proy  = st.multiselect("Proyecto",  all_proyectos, key="t4_proy",  placeholder="Todos los proyectos")
        sel4_etapa = st.multiselect("Etapa",     all_etapas,   key="t4_etapa", placeholder="Todas las etapas")
    with q2:
        sel4_mes   = st.multiselect("Mes",       all_meses,    key="t4_mes",   placeholder="Todos los meses")
        sel4_mat   = st.multiselect("Material",  all_mats,     key="t4_mat",   placeholder="Todos los materiales")
    with q3:
        sel4_estado= st.multiselect("Estado",    list(ESTADO_MAP.values()), key="t4_est", placeholder="Todos los estados")
        buscar     = st.text_input("🔎 Buscar por nombre de ensayo", placeholder="Ej: resistencia, fraguado, granulometría...")
    st.markdown('</div>', unsafe_allow_html=True)

    # Apply filters
    df4 = df_full.copy()
    if sel4_proy:  df4 = df4[df4["Proyecto"].isin(sel4_proy)]
    if sel4_etapa: df4 = df4[df4["ETAPA"].isin(sel4_etapa)]
    if sel4_mes:
        nums = [k for k,v in MESES.items() if v in sel4_mes]
        df4 = df4[df4["Mes"].isin(nums)]
    if sel4_mat:   df4 = df4[df4["MATERIAL"].isin(sel4_mat)]
    if sel4_estado:df4 = df4[df4["Estado"].isin(sel4_estado)]
    if buscar:     df4 = df4[df4["ENSAYO"].str.contains(buscar, case=False, na=False)]

    # Mini KPIs
    c4_k = compute_kpis(df4)
    comp4,inc4,nor4,plan4,total4,tasa4 = c4_k
    kc1,kc2,kc3,kc4,kc5 = st.columns(5)
    kc1.markdown(kpi_card("🔍","Resultados", f"{len(df4):,}", "registros encontrados", "kpi-purple"), unsafe_allow_html=True)
    kc2.markdown(kpi_card("📋","Planeados",  f"{plan4:,}", "", "kpi-blue"),   unsafe_allow_html=True)
    kc3.markdown(kpi_card("✅","Completos",  f"{comp4:,}", "", "kpi-green"),  unsafe_allow_html=True)
    kc4.markdown(kpi_card("⚠️","Incompletos",f"{inc4:,}",  "", "kpi-yellow"), unsafe_allow_html=True)
    kc5.markdown(kpi_card("❌","No Realizados",f"{nor4:,}", "", "kpi-red"),   unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Results table
    st.markdown('<div class="dash-card"><div class="card-title">Resultados de la Consulta</div>', unsafe_allow_html=True)

    if not df4.empty:
        display = df4[["Proyecto","ETAPA","MATERIAL","ENSAYO","NTC","FRECUENCIA","MesNombre","Estado"]].copy()
        display.columns = ["Proyecto","Etapa","Material","Ensayo","NTC","Frecuencia","Mes","Estado"]

        # Download
        col_dl4, _ = st.columns([1,5])
        with col_dl4:
            xlsx_bytes = display.to_csv(index=False).encode("utf-8")
            st.download_button("⬇ Descargar CSV", xlsx_bytes, "consulta_ensayos.csv", "text/csv", key="dl_cons")

        # Render HTML table (first 50 rows shown, full available for download)
        preview = display.head(50)
        rows_html4 = ""
        for _, r in preview.iterrows():
            rows_html4 += f"<tr><td>{r.Proyecto}</td><td>{r.Etapa}</td><td>{r.Material}</td><td>{r.Ensayo}</td><td>{r.NTC}</td><td style='max-width:180px;white-space:normal;font-size:11px;'>{r.Frecuencia}</td><td>{r.Mes}</td><td>{badge_html(r.Estado)}</td></tr>"

        total_showing = min(50, len(display))
        st.markdown(f'<div class="card-sub">Mostrando {total_showing} de {len(display):,} registros. Descarga el CSV para verlos todos.</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="overflow-x:auto;border-radius:10px;border:1px solid #E2E7F0;max-height:480px;overflow-y:auto;">
          <table class="res-table">
            <thead><tr><th>Proyecto</th><th>Etapa</th><th>Material</th><th>Ensayo</th><th>NTC</th><th>Frecuencia</th><th>Mes</th><th>Estado</th></tr></thead>
            <tbody>{rows_html4}</tbody>
          </table>
        </div>""", unsafe_allow_html=True)
    else:
        st.info("ℹ️ No se encontraron ensayos con los filtros aplicados. Intenta ampliar la búsqueda.")

    st.markdown('</div>', unsafe_allow_html=True)
