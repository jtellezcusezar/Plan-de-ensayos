"""
Dashboard de Programación de Ensayos - CUSEZAR 2026
Ejecutar con: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import tempfile, os
from pathlib import Path
from parse_excel import parse_excel, PROJECTS

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Plan de Ensayos CUSEZAR 2026",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Color Palette ────────────────────────────────────────────────────────────
COLORS = {
    'primary':    '#1B3A5C',
    'secondary':  '#2E6DA4',
    'accent':     '#4A9FD4',
    'success':    '#2D8A5F',
    'warning':    '#E8A838',
    'danger':     '#C94040',
    'light_bg':   '#F4F7FB',
    'card_bg':    '#FFFFFF',
    'text_dark':  '#1A2332',
    'text_mid':   '#4A5568',
    'border':     '#D1DCE8',
    'planned':    '#7B97B8',
}

STATUS_LABELS = {
    'done':     '✅ Realizado',
    'partial':  '⚠️ Sin repositorio',
    'not_done': '❌ No realizado',
    'planned':  '📋 Planificado',
}

MONTH_NAMES = {
    '1': 'Ene', '2': 'Feb', '3': 'Mar', '4': 'Abr',
    '5': 'May', '6': 'Jun', '7': 'Jul', '8': 'Ago',
    '9': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dic'
}

ALL_ETAPAS = ['Estructura', 'Obra Gris', 'Obra Blanca']

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
    .main, .stApp {{ background-color: {COLORS['light_bg']}; }}

    .dash-header {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        padding: 26px 36px; border-radius: 12px; color: white;
        margin-bottom: 20px; box-shadow: 0 4px 20px rgba(27,58,92,0.18);
    }}
    .dash-header h1 {{ margin: 0; font-size: 24px; font-weight: 700; letter-spacing: -0.3px; }}
    .dash-header p  {{ margin: 6px 0 0 0; opacity: 0.82; font-size: 13px; }}

    .filter-card {{
        background: {COLORS['card_bg']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 18px 22px 14px 22px;
        margin-bottom: 22px;
        box-shadow: 0 2px 8px rgba(27,58,92,0.05);
    }}
    .filter-title {{
        font-size: 12px; font-weight: 600; color: {COLORS['text_mid']};
        text-transform: uppercase; letter-spacing: 0.6px;
        margin-bottom: 10px;
    }}

    .kpi-card {{
        background: {COLORS['card_bg']}; border: 1px solid {COLORS['border']};
        border-radius: 12px; padding: 18px 16px;
        box-shadow: 0 2px 8px rgba(27,58,92,0.06); text-align: center;
    }}
    .kpi-value  {{ font-size: 34px; font-weight: 700; line-height: 1; margin-bottom: 4px; }}
    .kpi-label  {{ font-size: 11px; font-weight: 500; color: {COLORS['text_mid']};
                   text-transform: uppercase; letter-spacing: 0.5px; }}
    .kpi-sub    {{ font-size: 11px; color: {COLORS['text_mid']}; margin-top: 3px; }}

    .section-title {{
        font-size: 15px; font-weight: 600; color: {COLORS['text_dark']};
        margin: 22px 0 10px 0; padding-bottom: 7px;
        border-bottom: 2px solid {COLORS['accent']}; display: inline-block;
    }}

    section[data-testid="stSidebar"] {{ background: {COLORS['card_bg']}; }}

    .upload-hint {{
        font-size: 12px; color: {COLORS['text_mid']};
        background: {COLORS['light_bg']}; border: 1.5px dashed {COLORS['border']};
        border-radius: 8px; padding: 12px; margin-top: 6px; text-align: center;
    }}

    .tooltip-note {{
        font-size: 12px; color: {COLORS['secondary']};
        background: #EEF5FC; border-left: 3px solid {COLORS['accent']};
        border-radius: 4px; padding: 8px 12px; margin-bottom: 8px;
    }}
</style>
""", unsafe_allow_html=True)


# ─── Sidebar: SOLO carga del archivo ──────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:12px 0 6px 0;">
        <div style="font-size:20px;font-weight:700;color:{COLORS['primary']};">🏗️ CUSEZAR</div>
        <div style="font-size:11px;color:{COLORS['text_mid']};margin-top:2px;">Plan de Ensayos 2026</div>
    </div>
    <hr style="border-color:{COLORS['border']};margin:10px 0 14px 0;">
    <div style="font-size:12px;font-weight:600;color:{COLORS['text_mid']};
                text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;">
        📂 Fuente de datos
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Subir Excel actualizado",
        type=["xlsx"],
        label_visibility="collapsed",
        help="Sube el archivo con valores 0 / 0.5 / 1 / * para actualizar el dashboard"
    )
    st.markdown("""
    <div class="upload-hint">
        Valores aceptados:<br>
        <b>*</b> planificado &nbsp;·&nbsp; <b>1</b> ✅ realizado<br>
        <b>0.5</b> ⚠️ sin repo &nbsp;·&nbsp; <b>0</b> ❌ no realizado
    </div>
    """, unsafe_allow_html=True)


# ─── Data Loading ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data(source_bytes: bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        tmp.write(source_bytes)
        tmp_path = tmp.name
    data = parse_excel(tmp_path)
    os.unlink(tmp_path)
    return data


@st.cache_data
def load_default():
    for p in [Path("Plan_de_ensayos_2026.xlsx"), Path("../Plan_de_ensayos_2026.xlsx")]:
        if p.exists():
            return parse_excel(str(p))
    return None


if uploaded:
    data = load_data(uploaded.getvalue())
else:
    data = load_default()
    if data is None:
        st.warning("⚠️ No se encontró el archivo Excel. Por favor, sube el archivo desde la barra lateral.")
        st.stop()

# Projects actually present in the data
present_projects = sorted({
    p['project']
    for rec in data
    for projs in rec['schedule'].values()
    for p in projs
})


# ─── Filter summary helper ────────────────────────────────────────────────────
def filter_summary(data, months_str, sel_projects, sel_etapas):
    total = done = partial = not_done = planned_only = 0
    proj_month = {}
    etapa_counts = {}
    monthly_totals = {m: 0 for m in months_str}

    for rec in data:
        if rec['etapa'] not in sel_etapas:
            continue
        for month, projs in rec['schedule'].items():
            if month not in months_str:
                continue
            for p in projs:
                if p['project'] not in sel_projects:
                    continue
                status = p['status']
                total += 1
                monthly_totals[month] = monthly_totals.get(month, 0) + 1
                if status == 'done':       done += 1
                elif status == 'partial':  partial += 1
                elif status == 'not_done': not_done += 1
                else:                      planned_only += 1

                proj = p['project']
                proj_month.setdefault(proj, {}).setdefault(month, []).append({
                    'ensayo':   rec['ensayo'],
                    'etapa':    rec['etapa'],
                    'material': rec['material'],
                    'status':   status,
                    'value':    p['value']
                })
                etapa_counts[rec['etapa']] = etapa_counts.get(rec['etapa'], 0) + 1

    return dict(total=total, done=done, partial=partial, not_done=not_done,
                planned_only=planned_only, proj_month=proj_month,
                etapa_counts=etapa_counts, monthly_totals=monthly_totals)


# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dash-header">
    <h1>📊 Plan de Ensayos — CUSEZAR 2026</h1>
    <p>Seguimiento y control de calidad · Usa los filtros para explorar proyectos, meses y etapas</p>
</div>
""", unsafe_allow_html=True)


# ─── FILTROS dentro del dashboard ─────────────────────────────────────────────
st.markdown('<div class="filter-card">', unsafe_allow_html=True)
st.markdown('<div class="filter-title">🔍 Filtros</div>', unsafe_allow_html=True)

fc1, fc2, fc3 = st.columns([1, 2, 1])

with fc1:
    selected_months = st.multiselect(
        "Meses",
        options=list(range(1, 13)),
        default=list(range(1, 13)),
        format_func=lambda m: MONTH_NAMES[str(m)]
    )
    if not selected_months:
        selected_months = list(range(1, 13))

with fc2:
    selected_projects = st.multiselect(
        "Proyectos",
        options=present_projects,
        default=present_projects
    )
    if not selected_projects:
        selected_projects = present_projects

with fc3:
    etapas_in_data = [e for e in ALL_ETAPAS if e in {r['etapa'] for r in data}]
    selected_etapas = st.multiselect(
        "Etapa",
        options=etapas_in_data,
        default=etapas_in_data
    )
    if not selected_etapas:
        selected_etapas = etapas_in_data

st.markdown('</div>', unsafe_allow_html=True)

months_str    = [str(m) for m in selected_months]
months_sorted = sorted(months_str, key=int)

fs = filter_summary(data, months_str, selected_projects, selected_etapas)

executed = fs['done'] + fs['partial'] + fs['not_done']
pct_done = round((fs['done']  / executed    * 100) if executed    > 0 else 0, 1)
pct_exec = round((executed    / fs['total'] * 100) if fs['total'] > 0 else 0, 1)


# ─── KPIs ─────────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5, k6 = st.columns(6)
kpis = [
    (k1, fs['total'],        "Total Planificados", COLORS['secondary'], ""),
    (k2, executed,           "Ejecutados",          COLORS['accent'],   f"{pct_exec}% del total"),
    (k3, fs['done'],         "Realizados OK",       COLORS['success'],  f"{pct_done}% de ejecutados"),
    (k4, fs['partial'],      "Sin Repositorio",     COLORS['warning'],  "Requieren subir docs"),
    (k5, fs['not_done'],     "No Realizados",       COLORS['danger'],   "Requieren atención"),
    (k6, fs['planned_only'], "Solo Planificados",   COLORS['planned'],  "Sin actualizar"),
]
for col, val, label, color, sub in kpis:
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value" style="color:{color};">{val}</div>
            <div class="kpi-label">{label}</div>
            {"<div class='kpi-sub'>" + sub + "</div>" if sub else ""}
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ─── Gráficos fila 1: barras + torta ──────────────────────────────────────────
col_l, col_r = st.columns([1.35, 1])

with col_l:
    st.markdown('<div class="section-title">📅 Ensayos por Mes</div>', unsafe_allow_html=True)
    monthly_rows = []
    for m in months_sorted:
        row = {'Mes': MONTH_NAMES[m]}
        for sk, lbl in [('done','Realizados OK'), ('partial','Sin Repositorio'),
                        ('not_done','No Realizados'), ('planned','Planificados')]:
            row[lbl] = sum(
                1 for rec in data
                if rec['etapa'] in selected_etapas
                for p in rec['schedule'].get(m, [])
                if p['project'] in selected_projects and p['status'] == sk
            )
        monthly_rows.append(row)
    mdf = pd.DataFrame(monthly_rows)

    fig_bar = go.Figure()
    for name, color, op in [
        ('Planificados',    COLORS['planned'],  0.85),
        ('Realizados OK',   COLORS['success'],  1.0),
        ('Sin Repositorio', COLORS['warning'],  1.0),
        ('No Realizados',   COLORS['danger'],   1.0),
    ]:
        fig_bar.add_trace(go.Bar(name=name, x=mdf['Mes'], y=mdf[name],
                                 marker_color=color, opacity=op))
    fig_bar.update_layout(
        barmode='group', height=320,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
                    font=dict(size=11)),
        yaxis=dict(gridcolor='#E8EDF3'), xaxis=dict(tickfont=dict(size=11)),
        font=dict(family='Inter, sans-serif', color=COLORS['text_dark']),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_r:
    st.markdown('<div class="section-title">📊 Distribución por Estado</div>', unsafe_allow_html=True)
    fig_pie = go.Figure(go.Pie(
        labels=['Realizados OK', 'Sin Repositorio', 'No Realizados', 'Planificados'],
        values=[fs['done'], fs['partial'], fs['not_done'], fs['planned_only']],
        marker_colors=[COLORS['success'], COLORS['warning'], COLORS['danger'], COLORS['planned']],
        hole=0.55, textinfo='percent', textfont=dict(size=12, family='Inter'),
        hovertemplate='<b>%{label}</b><br>%{value} ensayos<br>%{percent}<extra></extra>'
    ))
    fig_pie.update_layout(
        height=320, margin=dict(l=0, r=0, t=10, b=30),
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation='v', font=dict(size=11)),
        annotations=[dict(text=f"<b>{fs['total']}</b><br>Total", x=0.5, y=0.5,
                          font_size=15, font_family='Inter', showarrow=False,
                          font_color=COLORS['text_dark'])],
        font=dict(family='Inter, sans-serif'),
    )
    st.plotly_chart(fig_pie, use_container_width=True)


# ─── Gráficos fila 2: etapa + ranking proyectos ───────────────────────────────
col_l2, col_r2 = st.columns(2)

with col_l2:
    st.markdown('<div class="section-title">🏢 Ensayos por Etapa</div>', unsafe_allow_html=True)
    etapa_rows = []
    for etapa in ALL_ETAPAS:
        if etapa not in selected_etapas:
            continue
        row = {'Etapa': etapa, 'Realizados': 0, 'Sin Repo': 0, 'No Real.': 0, 'Planif.': 0}
        for rec in data:
            if rec['etapa'] != etapa:
                continue
            for month, projs in rec['schedule'].items():
                if month not in months_str:
                    continue
                for p in projs:
                    if p['project'] not in selected_projects:
                        continue
                    s = p['status']
                    if s == 'done':       row['Realizados'] += 1
                    elif s == 'partial':  row['Sin Repo'] += 1
                    elif s == 'not_done': row['No Real.'] += 1
                    else:                 row['Planif.'] += 1
        etapa_rows.append(row)
    if etapa_rows:
        edf = pd.DataFrame(etapa_rows)
        fig_e = go.Figure()
        for cat, color in [('Realizados', COLORS['success']), ('Sin Repo', COLORS['warning']),
                            ('No Real.', COLORS['danger']),    ('Planif.', COLORS['planned'])]:
            fig_e.add_trace(go.Bar(name=cat, x=edf['Etapa'], y=edf[cat], marker_color=color))
        fig_e.update_layout(
            barmode='stack', height=300,
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, font=dict(size=10)),
            yaxis=dict(gridcolor='#E8EDF3'),
            font=dict(family='Inter, sans-serif', color=COLORS['text_dark']),
        )
        st.plotly_chart(fig_e, use_container_width=True)

with col_r2:
    st.markdown('<div class="section-title">🏗️ Top Proyectos — Total Ensayos</div>', unsafe_allow_html=True)
    proj_totals = {
        proj: sum(len(v) for v in months_data.values())
        for proj, months_data in fs['proj_month'].items()
        if proj in selected_projects
    }
    if proj_totals:
        sorted_p = sorted(proj_totals.items(), key=lambda x: x[1], reverse=True)[:12]
        fig_pr = go.Figure(go.Bar(
            x=[p[1] for p in sorted_p], y=[p[0] for p in sorted_p],
            orientation='h', marker_color=COLORS['secondary'],
            hovertemplate='<b>%{y}</b><br>%{x} ensayos<extra></extra>'
        ))
        fig_pr.update_layout(
            height=300, margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(autorange='reversed', tickfont=dict(size=10)),
            xaxis=dict(gridcolor='#E8EDF3'),
            font=dict(family='Inter, sans-serif', color=COLORS['text_dark']),
        )
        st.plotly_chart(fig_pr, use_container_width=True)


# ─── Heatmap de intensidad ────────────────────────────────────────────────────
st.markdown('<div class="section-title">🔥 Matriz Intensidad — Proyecto × Mes</div>', unsafe_allow_html=True)

heat_z, heat_y = [], []
for proj in selected_projects:
    heat_y.append(proj)
    heat_z.append([len(fs['proj_month'].get(proj, {}).get(m, [])) for m in months_sorted])

fig_heat = go.Figure(go.Heatmap(
    z=heat_z, x=[MONTH_NAMES[m] for m in months_sorted], y=heat_y,
    colorscale=[
        [0.0, '#F4F7FB'], [0.15, '#C8DCF0'], [0.5, COLORS['accent']],
        [0.8, COLORS['secondary']], [1.0, COLORS['primary']],
    ],
    hovertemplate='<b>%{y}</b><br>%{x}: %{z} ensayos<extra></extra>',
    showscale=True,
    colorbar=dict(title='Ensayos', thickness=14, len=0.8, tickfont=dict(size=10))
))
fig_heat.update_layout(
    height=max(260, len(selected_projects) * 26 + 60),
    margin=dict(l=0, r=60, t=10, b=0),
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(tickfont=dict(size=11)),
    yaxis=dict(tickfont=dict(size=10)),
    font=dict(family='Inter, sans-serif', color=COLORS['text_dark']),
)
st.plotly_chart(fig_heat, use_container_width=True)


# ─── Matriz detallada con tooltip condicional ─────────────────────────────────
st.markdown('<div class="section-title">📋 Matriz Detallada — Proyecto × Mes</div>', unsafe_allow_html=True)

single_mode = len(selected_projects) == 1

if single_mode:
    st.markdown(
        '<div class="tooltip-note">💡 Pasa el cursor sobre cada celda para ver el detalle de ensayos.</div>',
        unsafe_allow_html=True
    )
else:
    st.markdown(
        f'<p style="font-size:12px;color:{COLORS["text_mid"]};">'
        f'Muestra la cantidad de ensayos por celda. '
        f'Selecciona <b>un único proyecto</b> en el filtro para activar el tooltip con detalle de ensayos.'
        f'</p>',
        unsafe_allow_html=True
    )

z_vals, hover_text, proj_labels = [], [], []

for proj in selected_projects:
    proj_labels.append(proj)
    row_z, row_hover = [], []
    for m in months_sorted:
        entries = fs['proj_month'].get(proj, {}).get(m, [])
        count = len(entries)
        row_z.append(count)

        if single_mode:
            if entries:
                lines = [
                    f"<b>{proj}</b> — {MONTH_NAMES[m]}",
                    f"<b>{count} ensayo(s):</b>",
                    "─────────────────────"
                ]
                for e in entries[:20]:
                    icon = {'done':'✅','partial':'⚠️','not_done':'❌','planned':'📋'}.get(e['status'],'📋')
                    lines.append(f"{icon} {e['ensayo'][:55]}")
                if len(entries) > 20:
                    lines.append(f"... y {len(entries)-20} más")
                row_hover.append("<br>".join(lines))
            else:
                row_hover.append(f"<b>{proj}</b> — {MONTH_NAMES[m]}<br>Sin ensayos programados")
        else:
            # Multi-proyecto: tooltip simple sin listar ensayos
            row_hover.append(f"<b>{proj}</b><br>{MONTH_NAMES[m]}: {count} ensayos")

    z_vals.append(row_z)
    hover_text.append(row_hover)

fig_matrix = go.Figure(go.Heatmap(
    z=z_vals,
    x=[MONTH_NAMES[m] for m in months_sorted],
    y=proj_labels,
    text=[[str(v) if v > 0 else '' for v in row] for row in z_vals],
    texttemplate='%{text}',
    textfont=dict(size=12, color='white', family='Inter'),
    hovertext=hover_text,
    hovertemplate='%{hovertext}<extra></extra>',
    colorscale=[
        [0.0, '#F4F7FB'], [0.01, '#DCE8F5'],
        [0.3, COLORS['accent']], [0.7, COLORS['secondary']], [1.0, COLORS['primary']],
    ],
    showscale=True,
    colorbar=dict(title='# Ensayos', thickness=14, len=0.8, tickfont=dict(size=10)),
))
fig_matrix.update_layout(
    height=max(280, len(selected_projects) * 32 + 80),
    margin=dict(l=0, r=60, t=10, b=0),
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(tickfont=dict(size=12), side='top'),
    yaxis=dict(tickfont=dict(size=10), autorange='reversed'),
    font=dict(family='Inter, sans-serif', color=COLORS['text_dark']),
)
st.plotly_chart(fig_matrix, use_container_width=True)


# ─── Tabla detallada ──────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🔎 Detalle de Ensayos</div>', unsafe_allow_html=True)

tc1, tc2 = st.columns(2)
with tc1:
    tbl_project = st.selectbox("Filtrar por proyecto", ["Todos"] + list(selected_projects))
with tc2:
    tbl_month = st.selectbox(
        "Filtrar por mes",
        ["Todos"] + [f"{MONTH_NAMES[m]} (Mes {m})" for m in months_sorted]
    )

table_rows = []
for rec in data:
    if rec['etapa'] not in selected_etapas:
        continue
    for month, projs in rec['schedule'].items():
        if month not in months_str:
            continue
        for p in projs:
            if p['project'] not in selected_projects:
                continue
            if tbl_project != "Todos" and p['project'] != tbl_project:
                continue
            if tbl_month != "Todos" and f"{MONTH_NAMES[month]} (Mes {month})" != tbl_month:
                continue
            table_rows.append({
                'Etapa':    rec['etapa'],
                'Material': rec['material'],
                'Ensayo':   rec['ensayo'],
                'NTC':      rec['ntc'],
                'Proyecto': p['project'],
                'Mes':      MONTH_NAMES[month],
                'Estado':   STATUS_LABELS.get(p['status'], p['status']),
            })

if table_rows:
    df_tbl = pd.DataFrame(table_rows)
    st.dataframe(
        df_tbl, use_container_width=True, height=320,
        column_config={
            'Ensayo':   st.column_config.TextColumn(width='large'),
            'NTC':      st.column_config.TextColumn(width='small'),
            'Estado':   st.column_config.TextColumn(width='medium'),
            'Proyecto': st.column_config.TextColumn(width='medium'),
        }
    )
    st.markdown(
        f"<p style='font-size:11px;color:{COLORS['text_mid']};'>Mostrando {len(df_tbl)} registros</p>",
        unsafe_allow_html=True
    )
else:
    st.info("No hay registros con los filtros seleccionados.")


# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-top:40px;padding:14px;background:{COLORS['card_bg']};
     border:1px solid {COLORS['border']};border-radius:10px;
     text-align:center;font-size:12px;color:{COLORS['text_mid']};">
    📋 <b>Plan de Ensayos CUSEZAR 2026</b> &nbsp;·&nbsp;
    Para actualizar los datos, sube el archivo Excel desde la barra lateral ☰
</div>
""", unsafe_allow_html=True)
