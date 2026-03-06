import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Plan de Ensayos 2026 · Cusezar",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# ESTILOS GLOBALES
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Fondo general */
    .stApp { background-color: #f1f5f9; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

    /* Métricas */
    [data-testid="metric-container"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px 12px 20px;
    }
    [data-testid="metric-container"] label { font-size: 12px !important; color: #64748b !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { font-size: 28px !important; font-weight: 800 !important; }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
    [data-testid="stSidebar"] .stMarkdown h3 { color: #0f172a; font-size: 14px; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { background: #ffffff; border-bottom: 1px solid #e2e8f0; gap: 4px; }
    .stTabs [data-baseweb="tab"] { font-weight: 600; color: #64748b; padding: 10px 18px; }
    .stTabs [aria-selected="true"] { color: #0ea5e9 !important; border-bottom: 2px solid #0ea5e9 !important; }

    /* Cabecera */
    .header-bar {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 18px 24px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .accent-bar {
        width: 5px; height: 44px;
        background: linear-gradient(#0ea5e9, #6366f1);
        border-radius: 4px;
        display: inline-block;
    }

    /* Badges de estado */
    .badge-realizado   { background:#dcfce7; color:#16a34a; border-radius:20px; padding:3px 12px; font-size:12px; font-weight:700; }
    .badge-parcial     { background:#fef9c3; color:#d97706; border-radius:20px; padding:3px 12px; font-size:12px; font-weight:700; }
    .badge-norealizado { background:#fee2e2; color:#dc2626; border-radius:20px; padding:3px 12px; font-size:12px; font-weight:700; }
    .badge-planeado    { background:#ede9fe; color:#6366f1; border-radius:20px; padding:3px 12px; font-size:12px; font-weight:700; }

    /* Alertas custom */
    .alerta-roja  { background:#fef2f2; border:1px solid #fecaca; border-radius:12px; padding:14px 20px; }
    .alerta-amber { background:#fffbeb; border:1px solid #fde68a; border-radius:12px; padding:14px 20px; }

    /* Tablas */
    .tabla-ensayos { width:100%; border-collapse:collapse; font-size:13px; }
    .tabla-ensayos th { background:#f8fafc; padding:10px 12px; text-align:left; font-size:10px;
        font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:0.06em; border-bottom:2px solid #e2e8f0; }
    .tabla-ensayos td { padding:9px 12px; border-bottom:1px solid #f1f5f9; }
    .tabla-ensayos tr:hover td { background:#f8fafc; }
    .tr-no-real td { background:#fff5f5 !important; }
    .tr-parcial td { background:#fffdf0 !important; }

    /* Cards */
    .card { background:#ffffff; border:1px solid #e2e8f0; border-radius:14px; padding:20px 24px; }
    .card-title { font-size:11px; color:#94a3b8; text-transform:uppercase; letter-spacing:0.08em; font-weight:600; margin-bottom:14px; }

    /* Barra de progreso proyecto */
    .prog-wrap { background:#f1f5f9; border-radius:6px; height:26px; overflow:hidden; position:relative; }
    .prog-inner { height:100%; display:flex; }
    .prog-label { position:absolute; inset:0; display:flex; align-items:center; padding-left:8px; gap:8px; font-size:10px; font-weight:700; pointer-events:none; }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #f1f5f9; }
    ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────
MESES_LABELS = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
EXCEL_PATH   = Path(__file__).parent / "Plan_de_ensayos_2026.xlsx"

STATUS_COLORS = {
    "Realizado":      "#16a34a",
    "Parcial":        "#d97706",
    "No Realizado":   "#dc2626",
    "Planeado":       "#6366f1",
}
STATUS_BG = {
    "Realizado":      "#dcfce7",
    "Parcial":        "#fef9c3",
    "No Realizado":   "#fee2e2",
    "Planeado":       "#ede9fe",
}
STATUS_ICONS = {
    "Realizado":    "✅",
    "Parcial":      "⏳",
    "No Realizado": "❌",
    "Planeado":     "📋",
}

PALETTE = [
    "#0ea5e9","#8b5cf6","#f59e0b","#10b981","#ef4444",
    "#ec4899","#06b6d4","#84cc16","#f97316","#6366f1",
    "#14b8a6","#a855f7","#fb923c","#22c55e","#3b82f6",
]

# ─────────────────────────────────────────────
# CARGA Y PROCESAMIENTO DE DATOS
# ─────────────────────────────────────────────
@st.cache_data(show_spinner="Cargando datos del plan de ensayos…")
def cargar_datos(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="Ensayos")
    for col in ["MATERIAL","Proyecto","ENSAYO","ETAPA","NTC","FRECUENCIA"]:
        df[col] = df[col].astype(str).str.strip()

    def map_estado(x):
        if str(x).strip() == "*": return "Planeado"
        try:
            v = float(x)
            if v == 1:   return "Realizado"
            if v == 0.5: return "Parcial"
            if v == 0:   return "No Realizado"
        except:
            pass
        return "Planeado"

    df["Estado"] = df["Cantidad"].apply(map_estado)
    df["MesLabel"] = df["Mes"].apply(lambda m: MESES_LABELS[int(m)-1] if 1 <= int(m) <= 12 else str(m))
    return df


def calcular_cumplimiento(sub: pd.DataFrame) -> float | None:
    rea = (sub["Estado"] == "Realizado").sum()
    par = (sub["Estado"] == "Parcial").sum()
    nor = (sub["Estado"] == "No Realizado").sum()
    total_exec = rea + par + nor
    if total_exec == 0:
        return None
    return round((rea + par * 0.5) / total_exec * 100, 1)


def badge_html(estado: str) -> str:
    cls_map = {
        "Realizado":    "badge-realizado",
        "Parcial":      "badge-parcial",
        "No Realizado": "badge-norealizado",
        "Planeado":     "badge-planeado",
    }
    icon = STATUS_ICONS.get(estado, "")
    cls  = cls_map.get(estado, "badge-planeado")
    return f'<span class="{cls}">{icon} {estado}</span>'


# ─────────────────────────────────────────────
# SIDEBAR — FILTROS
# ─────────────────────────────────────────────
df_full = cargar_datos(EXCEL_PATH)

with st.sidebar:
    st.markdown("## 🔍 Filtros")
    st.markdown("---")

    proyectos_opts = ["Todos"] + sorted(df_full["Proyecto"].unique().tolist())
    sel_proyecto = st.selectbox("🏗️ Proyecto", proyectos_opts)

    meses_opts = ["Todos"] + MESES_LABELS
    sel_mes = st.selectbox("📅 Mes", meses_opts)

    materiales_opts = ["Todos"] + sorted(df_full["MATERIAL"].unique().tolist())
    sel_material = st.selectbox("🧱 Material", materiales_opts)

    estados_opts = ["Todos","Realizado","Parcial","No Realizado","Planeado"]
    sel_estado = st.selectbox("📊 Estado", estados_opts)

    etapas_opts = ["Todos"] + sorted(df_full["ETAPA"].unique().tolist())
    sel_etapa = st.selectbox("🏛️ Etapa", etapas_opts)

    busqueda = st.text_input("🔎 Buscar", placeholder="Ensayo, NTC, material…")

    st.markdown("---")
    if st.button("✕ Limpiar filtros", use_container_width=True):
        st.rerun()

    st.markdown("---")
    st.caption(f"📁 Fuente: `{EXCEL_PATH.name}`")
    st.caption(f"📐 Total registros: **{len(df_full):,}**")


# ─────────────────────────────────────────────
# APLICAR FILTROS
# ─────────────────────────────────────────────
df = df_full.copy()

if sel_proyecto != "Todos":
    df = df[df["Proyecto"] == sel_proyecto]
if sel_mes != "Todos":
    mes_num = MESES_LABELS.index(sel_mes) + 1
    df = df[df["Mes"] == mes_num]
if sel_material != "Todos":
    df = df[df["MATERIAL"] == sel_material]
if sel_estado != "Todos":
    df = df[df["Estado"] == sel_estado]
if sel_etapa != "Todos":
    df = df[df["ETAPA"] == sel_etapa]
if busqueda:
    q = busqueda.lower()
    mask = (
        df["ENSAYO"].str.lower().str.contains(q, na=False) |
        df["MATERIAL"].str.lower().str.contains(q, na=False) |
        df["Proyecto"].str.lower().str.contains(q, na=False) |
        df["NTC"].str.lower().str.contains(q, na=False) |
        df["FRECUENCIA"].str.lower().str.contains(q, na=False)
    )
    df = df[mask]

# Stats rápidas
n_total   = len(df)
n_real    = (df["Estado"] == "Realizado").sum()
n_par     = (df["Estado"] == "Parcial").sum()
n_no_real = (df["Estado"] == "No Realizado").sum()
n_plan    = (df["Estado"] == "Planeado").sum()
cumpl_global = calcular_cumplimiento(df)

# ─────────────────────────────────────────────
# CABECERA
# ─────────────────────────────────────────────
st.markdown("""
<div class="header-bar">
  <span class="accent-bar"></span>
  <div>
    <h2 style="margin:0;font-size:20px;font-weight:800;color:#0f172a;">Plan de Ensayos 2026</h2>
    <p style="margin:0;font-size:12px;color:#64748b;">Control de calidad · Cusezar · 15 proyectos · 1,538 ensayos</p>
  </div>
</div>
""", unsafe_allow_html=True)

filtros_activos = sel_proyecto!="Todos" or sel_mes!="Todos" or sel_material!="Todos" or sel_estado!="Todos" or sel_etapa!="Todos" or bool(busqueda)
if filtros_activos:
    st.info(f"Mostrando **{n_total:,}** registros con filtros activos.", icon="🔍")

# KPIs
col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    st.metric("🧪 Total", f"{n_total:,}")
with col2:
    st.metric("✅ Realizados", f"{n_real:,}")
with col3:
    st.metric("⏳ Sin subir", f"{n_par:,}")
with col4:
    st.metric("❌ No realizados", f"{n_no_real:,}")
with col5:
    st.metric("📋 Planeados", f"{n_plan:,}")
with col6:
    val_cumpl = f"{cumpl_global:.0f}%" if cumpl_global is not None else "—"
    st.metric("📈 Cumplimiento", val_cumpl)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LEYENDA DE ESTADOS
# ─────────────────────────────────────────────
leyenda_items = " &nbsp;&nbsp; ".join([
    f'<span style="display:inline-flex;align-items:center;gap:5px;font-size:12px;color:#475569;">'
    f'<span style="width:9px;height:9px;border-radius:2px;background:{STATUS_COLORS[e]};display:inline-block;"></span>'
    f'<b>{e}</b></span>'
    for e in STATUS_COLORS
])
st.markdown(
    f'<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:10px 18px;margin-bottom:16px;">'
    f'{leyenda_items}</div>',
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
# TABS  (orden: Resumen | Cumplimiento | Cronograma | Ensayos)
# ─────────────────────────────────────────────
tab_res, tab_cum, tab_cron, tab_ing = st.tabs([
    "📊 Resumen",
    "✅ Cumplimiento",
    "📅 Cronograma",
    "🔧 Ensayos",
])


# ══════════════════════════════════════════════
# TAB 1 — RESUMEN
# ══════════════════════════════════════════════
with tab_res:
    # Serie mensual
    mes_data = []
    for i, m in enumerate(MESES_LABELS):
        md = df[df["Mes"] == i+1]
        mes_data.append({
            "Mes": m,
            "Realizado": (md["Estado"]=="Realizado").sum(),
            "Parcial":   (md["Estado"]=="Parcial").sum(),
            "No Realizado": (md["Estado"]=="No Realizado").sum(),
            "Planeado":  (md["Estado"]=="Planeado").sum(),
        })
    df_mes = pd.DataFrame(mes_data)

    # Gráfico barras apiladas por mes
    fig_mes = go.Figure()
    for estado, color in STATUS_COLORS.items():
        label = "Sin subir" if estado == "Parcial" else estado
        fig_mes.add_trace(go.Bar(
            name=label,
            x=df_mes["Mes"],
            y=df_mes[estado],
            marker_color=color,
        ))
    fig_mes.update_layout(
        barmode="stack",
        height=260,
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font_size=11),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(showgrid=False, tickfont_size=11),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9", tickfont_size=11),
    )

    col_g1, col_g2 = st.columns([3, 1])
    with col_g1:
        st.markdown('<div class="card"><div class="card-title">Ensayos por mes y estado</div>', unsafe_allow_html=True)
        st.plotly_chart(fig_mes, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col_g2:
        st.markdown('<div class="card"><div class="card-title">Por material</div>', unsafe_allow_html=True)
        mat_counts = df.groupby("MATERIAL").size().sort_values(ascending=False).head(10)
        for mat, cnt in mat_counts.items():
            pct = cnt / max(mat_counts.max(), 1)
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;font-size:12px;">'
                f'<div style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#334155;">{mat}</div>'
                f'<b style="color:#0f172a;min-width:28px;text-align:right;">{cnt}</b>'
                f'</div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # Gráfico por proyecto
    proyectos_list = sorted(df_full["Proyecto"].unique().tolist())
    proj_data = []
    for i, p in enumerate(proyectos_list):
        pd_p = df[df["Proyecto"] == p]
        if len(pd_p) == 0:
            continue
        proj_data.append({
            "Proyecto": p,
            "Total": len(pd_p),
            "Color": PALETTE[i % len(PALETTE)],
        })
    df_proj = pd.DataFrame(proj_data).sort_values("Total", ascending=False)

    fig_proj = go.Figure(go.Bar(
        x=df_proj["Proyecto"],
        y=df_proj["Total"],
        marker_color=df_proj["Color"].tolist(),
        text=df_proj["Total"],
        textposition="outside",
    ))
    fig_proj.update_layout(
        height=220,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(showgrid=False, tickfont_size=10),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9", tickfont_size=11),
        showlegend=False,
    )
    st.markdown('<div class="card" style="margin-top:14px;"><div class="card-title">Volumen total por proyecto</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_proj, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TAB 2 — CUMPLIMIENTO
# ══════════════════════════════════════════════
with tab_cum:
    # Gauge de cumplimiento global
    col_gauge, col_detail = st.columns([1, 2])
    with col_gauge:
        pct = cumpl_global or 0
        if pct >= 80:
            gauge_color = "#10b981"   # verde esmeralda
            gauge_step1 = "#6ee7b7"
            gauge_step2 = "#a7f3d0"
        elif pct >= 50:
            gauge_color = "#f59e0b"   # ámbar
            gauge_step1 = "#fcd34d"
            gauge_step2 = "#fde68a"
        else:
            gauge_color = "#f43f5e"   # rosa-rojo
            gauge_step1 = "#fb7185"
            gauge_step2 = "#fda4af"

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pct,
            number={"suffix": "%", "font": {"size": 36, "color": gauge_color, "family": "DM Sans"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#e2e8f0",
                         "tickfont": {"size": 10, "color": "#94a3b8"}},
                "bar": {"color": gauge_color, "thickness": 0.35},
                "bgcolor": "#f8fafc",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 50],  "color": "#fce7f3"},
                    {"range": [50, 80], "color": "#fef3c7"},
                    {"range": [80, 100],"color": "#d1fae5"},
                ],
                "threshold": {
                    "line": {"color": gauge_color, "width": 3},
                    "thickness": 0.75,
                    "value": pct,
                },
            },
            title={"text": "Cumplimiento global<br><span style='font-size:12px;color:#64748b'>excluye planeados</span>",
                   "font": {"size": 14, "color": "#0f172a"}},
        ))
        fig_gauge.update_layout(
            height=280,
            margin=dict(l=20, r=20, t=30, b=10),
            paper_bgcolor="white",
        )
        st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})

    with col_detail:
        st.markdown('<div class="card"><div class="card-title">Detalle del cálculo</div>', unsafe_allow_html=True)
        exec_total = n_real + n_par + n_no_real
        items = [
            ("✅ Realizados y subidos",   n_real,    "#16a34a", "#dcfce7"),
            ("⏳ Realizados sin subir",   n_par,     "#d97706", "#fef9c3"),
            ("❌ No realizados",          n_no_real, "#dc2626", "#fee2e2"),
            ("📋 Planeados (excluidos)",  n_plan,    "#6366f1", "#ede9fe"),
        ]
        for label, val, color, bg in items:
            pct_item = (val / max(n_total, 1)) * 100
            st.markdown(
                f'<div style="display:flex;align-items:center;justify-content:space-between;'
                f'background:{bg};border-radius:8px;padding:8px 14px;margin-bottom:8px;">'
                f'<span style="font-size:13px;color:{color};font-weight:600;">{label}</span>'
                f'<span style="font-size:16px;font-weight:800;color:{color};">{val:,}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # Barras de cumplimiento por proyecto
    st.markdown('<div class="card" style="margin-top:14px;"><div class="card-title">Cumplimiento por proyecto</div>', unsafe_allow_html=True)

    proyectos_list_all = sorted(df_full["Proyecto"].unique().tolist())
    for p in proyectos_list_all:
        sub = df[df["Proyecto"] == p]
        if len(sub) == 0:
            continue
        rea  = (sub["Estado"]=="Realizado").sum()
        par  = (sub["Estado"]=="Parcial").sum()
        nor  = (sub["Estado"]=="No Realizado").sum()
        pla  = (sub["Estado"]=="Planeado").sum()
        exec_p = rea + par + nor
        pct_p  = calcular_cumplimiento(sub)

        # Color badge
        if pct_p is None:
            badge_txt = "—"
            badge_col = "#94a3b8"
            badge_bg  = "#f1f5f9"
        elif pct_p >= 80:
            badge_txt = f"{pct_p:.0f}%"
            badge_col = "#16a34a"
            badge_bg  = "#dcfce7"
        elif pct_p >= 50:
            badge_txt = f"{pct_p:.0f}%"
            badge_col = "#d97706"
            badge_bg  = "#fef9c3"
        else:
            badge_txt = f"{pct_p:.0f}%"
            badge_col = "#dc2626"
            badge_bg  = "#fee2e2"

        w_rea = f"{rea/max(exec_p,1)*100:.1f}%" if exec_p > 0 else "0%"
        w_par = f"{par/max(exec_p,1)*100:.1f}%" if exec_p > 0 else "0%"
        w_nor = f"{nor/max(exec_p,1)*100:.1f}%" if exec_p > 0 else "0%"

        row_cols = st.columns([2, 5, 1])
        with row_cols[0]:
            st.markdown(f'<div style="font-size:12px;font-weight:600;color:#334155;text-align:right;padding-top:4px;">{p}</div>', unsafe_allow_html=True)
        with row_cols[1]:
            if exec_p == 0:
                st.markdown(
                    f'<div style="background:#f8fafc;border-radius:6px;height:26px;display:flex;align-items:center;padding-left:12px;">'
                    f'<span style="font-size:11px;color:#a5b4fc;">📋 {pla} planeados</span></div>',
                    unsafe_allow_html=True
                )
            else:
                labels = ""
                if rea > 0: labels += f'<span style="color:#fff;margin-right:6px;">✅ {rea}</span>'
                if par > 0: labels += f'<span style="color:#fff;margin-right:6px;">⏳ {par}</span>'
                if nor > 0: labels += f'<span style="color:#fff;margin-right:6px;">❌ {nor}</span>'
                if pla > 0: labels += f'<span style="color:#94a3b8;">📋 {pla}</span>'
                st.markdown(
                    f'<div class="prog-wrap"><div class="prog-inner">'
                    f'<div style="width:{w_rea};background:#16a34a;"></div>'
                    f'<div style="width:{w_par};background:#d97706;"></div>'
                    f'<div style="width:{w_nor};background:#dc2626;"></div>'
                    f'</div><div class="prog-label" style="font-size:10px;font-weight:700;">{labels}</div></div>',
                    unsafe_allow_html=True
                )
        with row_cols[2]:
            st.markdown(
                f'<div style="background:{badge_bg};color:{badge_col};border-radius:20px;padding:3px 10px;'
                f'font-size:11px;font-weight:700;text-align:center;">{badge_txt}</div>',
                unsafe_allow_html=True
            )

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TAB 3 — CRONOGRAMA
# ══════════════════════════════════════════════
with tab_cron:
    # ── Área: El valor planeado = total del mes (constante, independiente de ejecución)
    # La idea: "planeado" en el gráfico representa el total programado para ese mes
    # La ejecución (realizado/parcial/no_real) se superpone encima
    area_data = []
    for i, m in enumerate(MESES_LABELS):
        mes_num = i + 1
        md_full = df_full[df_full["Mes"] == mes_num]  # siempre del df completo para total planeado
        md_filt = df[df["Mes"] == mes_num]             # filtrado para ejecución
        total_mes = len(md_full)  # total planeado original (constante)
        area_data.append({
            "Mes": m,
            "Total planeado": total_mes,
            "Realizado":      (md_filt["Estado"]=="Realizado").sum(),
            "Sin subir":      (md_filt["Estado"]=="Parcial").sum(),
            "No realizado":   (md_filt["Estado"]=="No Realizado").sum(),
        })
    df_area = pd.DataFrame(area_data)

    fig_area = go.Figure()

    # Línea base planeada (constante por mes)
    fig_area.add_trace(go.Scatter(
        name="Total planeado (meta)",
        x=df_area["Mes"],
        y=df_area["Total planeado"],
        mode="lines",
        line=dict(color="#6366f1", width=2.5, dash="dot"),
        fill=None,
    ))
    # Areas de ejecución
    fig_area.add_trace(go.Bar(name="Realizado",    x=df_area["Mes"], y=df_area["Realizado"],    marker_color="#16a34a"))
    fig_area.add_trace(go.Bar(name="Sin subir",    x=df_area["Mes"], y=df_area["Sin subir"],    marker_color="#d97706"))
    fig_area.add_trace(go.Bar(name="No realizado", x=df_area["Mes"], y=df_area["No realizado"], marker_color="#dc2626"))

    fig_area.update_layout(
        barmode="stack",
        height=300,
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font_size=11),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(showgrid=False, tickfont_size=11),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9", tickfont_size=11),
    )

    st.markdown('<div class="card"><div class="card-title">Evolución mensual — ejecución vs. meta planeada</div>', unsafe_allow_html=True)
    st.caption("La línea punteada muestra el total de ensayos programados por mes (meta constante). Las barras muestran la ejecución real.")
    st.plotly_chart(fig_area, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

    # Mapa de calor proyectos × mes
    proyectos_heat = sorted(df_full["Proyecto"].unique().tolist())
    heat_z, heat_text = [], []
    for p in proyectos_heat:
        row_z, row_t = [], []
        for i in range(12):
            val = len(df[(df["Proyecto"]==p) & (df["Mes"]==i+1)])
            row_z.append(val)
            row_t.append(str(val) if val > 0 else "")
        heat_z.append(row_z)
        heat_text.append(row_t)

    fig_heat = go.Figure(go.Heatmap(
        z=heat_z,
        x=MESES_LABELS,
        y=proyectos_heat,
        text=heat_text,
        texttemplate="%{text}",
        colorscale=[[0,"#f8fafc"],[0.2,"#dbeafe"],[0.5,"#93c5fd"],[1,"#1d4ed8"]],
        showscale=True,
        colorbar=dict(thickness=12, tickfont_size=10),
        hovertemplate="<b>%{y}</b><br>%{x}: %{z} ensayos<extra></extra>",
    ))
    fig_heat.update_layout(
        height=400,
        margin=dict(l=120, r=20, t=10, b=0),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(tickfont_size=11),
        yaxis=dict(tickfont_size=11, autorange="reversed"),
    )

    st.markdown('<div class="card" style="margin-top:14px;"><div class="card-title">Mapa de calor — Proyectos × Mes (ensayos en selección)</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TAB 4 — ENSAYOS (antes "Vista Ingeniero")
# ══════════════════════════════════════════════
with tab_ing:
    # Alertas
    if n_no_real > 0 or n_par > 0:
        col_a1, col_a2 = st.columns(2)
        if n_no_real > 0:
            with col_a1:
                st.markdown(
                    f'<div class="alerta-roja">'
                    f'<b style="font-size:15px;color:#b91c1c;">🚨 {n_no_real} ensayos NO realizados</b><br>'
                    f'<span style="font-size:12px;color:#ef4444;">Requieren atención inmediata — meses vencidos</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        if n_par > 0:
            with col_a2:
                st.markdown(
                    f'<div class="alerta-amber">'
                    f'<b style="font-size:15px;color:#92400e;">📤 {n_par} ensayos pendientes de subir</b><br>'
                    f'<span style="font-size:12px;color:#d97706;">Realizados pero no subidos al repositorio</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Sub-vista
    vista = st.radio("Vista", ["📋 Lista detallada", "🗂️ Agrupado por obra y mes"],
                     horizontal=True, label_visibility="collapsed")

    # Ordenamiento
    if vista == "📋 Lista detallada":
        orden_opts = {
            "🚨 Urgencia (No real → Parcial → Planeado)": "urgencia",
            "📅 Mes":      "mes",
            "🏗️ Proyecto": "proyecto",
            "🧱 Material":  "material",
        }
        orden_sel = st.selectbox("Ordenar por", list(orden_opts.keys()), label_visibility="visible")
        orden_key = orden_opts[orden_sel]

        # Aplicar orden
        URGENCY_MAP = {"No Realizado": 0, "Parcial": 1, "Planeado": 2, "Realizado": 3}
        df_sorted = df.copy()
        df_sorted["_ord"] = df_sorted["Estado"].map(URGENCY_MAP)
        if orden_key == "urgencia":
            df_sorted = df_sorted.sort_values(["_ord","Mes","Proyecto"])
        elif orden_key == "mes":
            df_sorted = df_sorted.sort_values(["Mes","Proyecto","MATERIAL"])
        elif orden_key == "proyecto":
            df_sorted = df_sorted.sort_values(["Proyecto","Mes","MATERIAL"])
        elif orden_key == "material":
            df_sorted = df_sorted.sort_values(["MATERIAL","Proyecto","Mes"])

        # Mostrar tabla
        MAX_ROWS = 500
        df_show = df_sorted.head(MAX_ROWS).reset_index(drop=True)

        # Construir HTML de tabla
        rows_html = ""
        for _, row in df_show.iterrows():
            est = row["Estado"]
            tr_cls = "tr-no-real" if est=="No Realizado" else ("tr-parcial" if est=="Parcial" else "")
            freq_short = row["FRECUENCIA"][:55] + "…" if len(str(row["FRECUENCIA"])) > 55 else row["FRECUENCIA"]
            rows_html += f"""
            <tr class="{tr_cls}">
              <td>{badge_html(est)}</td>
              <td><b>{row["Proyecto"]}</b></td>
              <td><span style='background:#f1f5f9;border-radius:6px;padding:2px 8px;font-size:11px;font-weight:600;color:#475569;'>{row["MesLabel"]}</span></td>
              <td><span style='background:#ede9fe;color:#6366f1;border-radius:5px;padding:2px 7px;font-size:10px;font-weight:600;'>{row["ETAPA"]}</span></td>
              <td>{row["MATERIAL"]}</td>
              <td style='max-width:240px;'><b>{row["ENSAYO"]}</b></td>
              <td><span style='background:#e0f2fe;color:#0284c7;border-radius:5px;padding:2px 7px;font-size:10px;font-weight:600;'>{row["NTC"]}</span></td>
              <td style='color:#64748b;font-size:12px;max-width:200px;'>{freq_short}</td>
            </tr>
            """

        tabla_html = f"""
        <div style="overflow-x:auto;background:#fff;border:1px solid #e2e8f0;border-radius:14px;">
          <table class="tabla-ensayos">
            <thead><tr>
              <th>Estado</th><th>Proyecto</th><th>Mes</th><th>Etapa</th>
              <th>Material</th><th>Ensayo</th><th>NTC</th><th>Frecuencia</th>
            </tr></thead>
            <tbody>{rows_html}</tbody>
          </table>
        </div>
        """
        st.markdown(tabla_html, unsafe_allow_html=True)

        if len(df_sorted) > MAX_ROWS:
            st.caption(f"Mostrando {MAX_ROWS} de {len(df_sorted):,} registros. Usa los filtros del panel lateral para acotar la búsqueda.")

    else:
        # AGRUPADO POR OBRA Y MES
        URGENCY_MAP2 = {"No Realizado": 0, "Parcial": 1, "Planeado": 2, "Realizado": 3}
        df_grp = df.copy()
        df_grp["_ord"] = df_grp["Estado"].map(URGENCY_MAP2)
        grupos = df_grp.groupby(["Proyecto","Mes"])

        for (proyecto, mes), grupo in sorted(grupos, key=lambda x: (x[0][1], x[0][0])):
            no_r = (grupo["Estado"]=="No Realizado").sum()
            par  = (grupo["Estado"]=="Parcial").sum()
            pla  = (grupo["Estado"]=="Planeado").sum()
            rea  = (grupo["Estado"]=="Realizado").sum()
            mes_label = MESES_LABELS[mes-1]

            hdr_bg = "#fff5f5" if no_r > 0 else ("#fffdf5" if par > 0 else "#f8fafc")

            badges = ""
            if rea > 0: badges += f'<span class="badge-realizado">✅ {rea}</span> '
            if par > 0: badges += f'<span class="badge-parcial">⏳ {par}</span> '
            if no_r>0:  badges += f'<span class="badge-norealizado">❌ {no_r}</span> '
            if pla > 0: badges += f'<span class="badge-planeado">📋 {pla}</span> '

            # Filas del grupo
            grupo_sorted = grupo.sort_values("_ord")
            rows_g = ""
            for _, r in grupo_sorted.iterrows():
                est = r["Estado"]
                tr_cls = "tr-no-real" if est=="No Realizado" else ("tr-parcial" if est=="Parcial" else "")
                freq_s = r["FRECUENCIA"][:60]+"…" if len(str(r["FRECUENCIA"]))>60 else r["FRECUENCIA"]
                rows_g += f"""
                <tr class="{tr_cls}">
                  <td>{badge_html(est)}</td>
                  <td><span style='background:#ede9fe;color:#6366f1;border-radius:4px;padding:1px 6px;font-size:10px;font-weight:600;'>{r["ETAPA"]}</span></td>
                  <td style='font-weight:500;'>{r["MATERIAL"]}</td>
                  <td style='font-weight:500;'>{r["ENSAYO"]}</td>
                  <td><span style='background:#e0f2fe;color:#0284c7;border-radius:4px;padding:1px 6px;font-size:10px;font-weight:600;'>{r["NTC"]}</span></td>
                  <td style='color:#64748b;font-size:12px;'>{freq_s}</td>
                </tr>
                """

            bloque = f"""
            <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;overflow:hidden;margin-bottom:14px;">
              <div style="padding:11px 18px;background:{hdr_bg};border-bottom:1px solid #e2e8f0;
                   display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;">
                <div style="display:flex;align-items:center;gap:10px;">
                  <span style="font-weight:800;font-size:14px;color:#0f172a;">{proyecto}</span>
                  <span style="color:#cbd5e1;">·</span>
                  <span style="font-weight:600;font-size:13px;color:#6366f1;">{mes_label}</span>
                  <span style="margin-left:4px;">{badges}</span>
                </div>
                <span style="font-size:11px;color:#94a3b8;">{len(grupo)} ensayos</span>
              </div>
              <div style="overflow-x:auto;">
              <table class="tabla-ensayos">
                <thead><tr>
                  <th>Estado</th><th>Etapa</th><th>Material</th><th>Ensayo</th><th>NTC</th><th>Frecuencia</th>
                </tr></thead>
                <tbody>{rows_g}</tbody>
              </table>
              </div>
            </div>
            """
            st.markdown(bloque, unsafe_allow_html=True)
