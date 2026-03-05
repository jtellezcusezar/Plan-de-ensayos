"""
Dashboard de Programación de Ensayos - CUSEZAR 2026
Ejecutar con: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from pathlib import Path
from parse_excel import parse_excel, get_summary, PROJECTS

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Plan de Ensayos CUSEZAR 2026",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Color Palette ────────────────────────────────────────────────────────────
COLORS = {
    'primary': '#1B3A5C',       # Azul oscuro
    'secondary': '#2E6DA4',     # Azul medio
    'accent': '#4A9FD4',        # Azul claro
    'success': '#2D8A5F',       # Verde
    'warning': '#E8A838',       # Ámbar
    'danger': '#C94040',        # Rojo
    'light_bg': '#F4F7FB',      # Fondo claro
    'card_bg': '#FFFFFF',
    'text_dark': '#1A2332',
    'text_mid': '#4A5568',
    'border': '#D1DCE8',
    'planned': '#7B97B8',       # Azul grisáceo para planificado
}

STATUS_COLORS = {
    'done': COLORS['success'],
    'partial': COLORS['warning'],
    'not_done': COLORS['danger'],
    'planned': COLORS['planned'],
}

STATUS_LABELS = {
    'done': '✅ Realizado',
    'partial': '⚠️ Realizado (sin repositorio)',
    'not_done': '❌ No realizado',
    'planned': '📋 Planificado',
}

MONTH_NAMES = {
    '1': 'Ene', '2': 'Feb', '3': 'Mar', '4': 'Abr',
    '5': 'May', '6': 'Jun', '7': 'Jul', '8': 'Ago',
    '9': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dic'
}

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    .main {{
        background-color: {COLORS['light_bg']};
    }}

    .stApp {{
        background-color: {COLORS['light_bg']};
    }}

    /* Header */
    .dashboard-header {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        padding: 28px 36px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(27,58,92,0.18);
    }}
    .dashboard-header h1 {{
        margin: 0;
        font-size: 26px;
        font-weight: 700;
        letter-spacing: -0.3px;
    }}
    .dashboard-header p {{
        margin: 6px 0 0 0;
        opacity: 0.85;
        font-size: 14px;
        font-weight: 400;
    }}

    /* KPI Cards */
    .kpi-card {{
        background: {COLORS['card_bg']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 20px 22px;
        box-shadow: 0 2px 8px rgba(27,58,92,0.06);
        text-align: center;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    .kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(27,58,92,0.12);
    }}
    .kpi-value {{
        font-size: 36px;
        font-weight: 700;
        line-height: 1;
        margin-bottom: 4px;
    }}
    .kpi-label {{
        font-size: 12px;
        font-weight: 500;
        color: {COLORS['text_mid']};
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .kpi-sub {{
        font-size: 11px;
        color: {COLORS['text_mid']};
        margin-top: 4px;
    }}

    /* Section Title */
    .section-title {{
        font-size: 16px;
        font-weight: 600;
        color: {COLORS['text_dark']};
        margin: 24px 0 12px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid {COLORS['accent']};
        display: inline-block;
    }}

    /* Status Legend */
    .status-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
        margin: 3px;
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {COLORS['card_bg']};
        border-right: 1px solid {COLORS['border']};
    }}
    section[data-testid="stSidebar"] .stMarkdown h3 {{
        color: {COLORS['primary']};
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    /* Upload zone */
    .upload-box {{
        background: {COLORS['light_bg']};
        border: 2px dashed {COLORS['border']};
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        font-size: 13px;
        color: {COLORS['text_mid']};
    }}

    /* Table cell colors */
    .cell-done {{ background: #D4EDDA; color: #155724; }}
    .cell-partial {{ background: #FFF3CD; color: #856404; }}
    .cell-not-done {{ background: #F8D7DA; color: #721C24; }}
    .cell-planned {{ background: #DCE8F5; color: #1B3A5C; }}
    .cell-empty {{ background: #F8F9FA; color: #ADB5BD; }}

    /* Plotly chart adjustments */
    .js-plotly-plot .plotly {{ font-family: 'Inter', sans-serif !important; }}
</style>
""", unsafe_allow_html=True)


# ─── Data Loading ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data(filepath: str):
    data = parse_excel(filepath)
    summary = get_summary(data)
    return data, summary


def get_default_file():
    candidates = [
        Path("Plan_de_ensayos_2026.xlsx"),
        Path("../Plan_de_ensayos_2026.xlsx"),
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return None


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding: 16px 0 8px 0;">
        <div style="font-size:22px; font-weight:700; color:{COLORS['primary']};">🏗️ CUSEZAR</div>
        <div style="font-size:12px; color:{COLORS['text_mid']}; margin-top:2px;">Plan de Ensayos 2026</div>
    </div>
    <hr style="border-color:{COLORS['border']}; margin:12px 0;">
    """, unsafe_allow_html=True)

    st.markdown("### 📂 Fuente de Datos")
    uploaded = st.file_uploader(
        "Subir Excel actualizado",
        type=["xlsx"],
        help="Sube el archivo con valores 0, 0.5, 1 o * para actualizar el dashboard"
    )

    st.markdown("<hr style='border-color:#D1DCE8;margin:16px 0;'>", unsafe_allow_html=True)
    st.markdown("### 🔍 Filtros")

    # Month filter
    all_months = list(range(1, 13))
    selected_months = st.multiselect(
        "Meses",
        options=all_months,
        default=all_months,
        format_func=lambda m: f"{MONTH_NAMES[str(m)]} (Mes {m})"
    )

    # Project filter
    selected_projects = st.multiselect(
        "Proyectos",
        options=PROJECTS,
        default=PROJECTS
    )

    # Etapa filter
    selected_etapas = st.multiselect(
        "Etapa",
        options=['Estructura', 'Obra Gris', 'Obra Blanca'],
        default=['Estructura', 'Obra Gris', 'Obra Blanca']
    )

    st.markdown("<hr style='border-color:#D1DCE8;margin:16px 0;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:11px; color:#7B97B8;'>
    <b>Leyenda de valores:</b><br>
    ⭐ <code>*</code> = Planificado<br>
    ✅ <code>1</code> = Realizado OK<br>
    ⚠️ <code>0.5</code> = Sin repositorio<br>
    ❌ <code>0</code> = No realizado
    </div>
    """, unsafe_allow_html=True)


# ─── Load Data ────────────────────────────────────────────────────────────────
if uploaded:
    import tempfile, os
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        tmp.write(uploaded.getvalue())
        tmp_path = tmp.name
    data, summary = load_data(tmp_path)
    os.unlink(tmp_path)
else:
    default_path = get_default_file()
    if default_path:
        data, summary = load_data(default_path)
    else:
        st.warning("⚠️ No se encontró el archivo Excel. Por favor, sube el archivo desde la barra lateral.")
        st.stop()


# ─── Apply Filters ────────────────────────────────────────────────────────────
months_str = [str(m) for m in selected_months]

filtered_data = [
    d for d in data
    if d['etapa'] in selected_etapas
]


def filter_summary(data_list, months_str, selected_projects, selected_etapas):
    total = done = partial = not_done = planned_only = 0
    proj_month = {}
    etapa_counts = {}
    monthly_totals = {m: 0 for m in months_str}
    monthly_done = {m: 0 for m in months_str}

    for rec in data_list:
        if rec['etapa'] not in selected_etapas:
            continue
        for month, projs in rec['schedule'].items():
            if month not in months_str:
                continue
            for p in projs:
                if p['project'] not in selected_projects:
                    continue
                status = p['status']
                total += 1
                monthly_totals[month] = monthly_totals.get(month, 0) + 1
                if status == 'done':
                    done += 1
                    monthly_done[month] = monthly_done.get(month, 0) + 1
                elif status == 'partial':
                    partial += 1
                elif status == 'not_done':
                    not_done += 1
                else:
                    planned_only += 1

                proj = p['project']
                if proj not in proj_month:
                    proj_month[proj] = {}
                if month not in proj_month[proj]:
                    proj_month[proj][month] = []
                proj_month[proj][month].append({
                    'ensayo': rec['ensayo'],
                    'etapa': rec['etapa'],
                    'material': rec['material'],
                    'status': status,
                    'value': p['value']
                })

                etapa = rec['etapa']
                etapa_counts[etapa] = etapa_counts.get(etapa, 0) + 1

    return {
        'total': total, 'done': done, 'partial': partial,
        'not_done': not_done, 'planned_only': planned_only,
        'proj_month': proj_month, 'etapa_counts': etapa_counts,
        'monthly_totals': monthly_totals, 'monthly_done': monthly_done,
    }


fs = filter_summary(data, months_str, selected_projects, selected_etapas)
executed = fs['done'] + fs['partial'] + fs['not_done']
pct_done = round((fs['done'] / executed * 100) if executed > 0 else 0, 1)
pct_exec = round((executed / fs['total'] * 100) if fs['total'] > 0 else 0, 1)


# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="dashboard-header">
    <h1>📊 Dashboard — Plan de Ensayos CUSEZAR 2026</h1>
    <p>Seguimiento y control de ensayos de calidad por proyecto · {len(selected_projects)} proyectos · {len(selected_months)} meses seleccionados</p>
</div>
""", unsafe_allow_html=True)


# ─── KPI Row ──────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5, k6 = st.columns(6)

kpis = [
    (k1, fs['total'], "Total Planificados", COLORS['secondary'], ""),
    (k2, executed, "Ejecutados", COLORS['accent'], f"{pct_exec}% del total"),
    (k3, fs['done'], "Realizados OK", COLORS['success'], f"{pct_done}% de ejecutados"),
    (k4, fs['partial'], "Sin Repositorio", COLORS['warning'], "Requieren subir docs"),
    (k5, fs['not_done'], "No Realizados", COLORS['danger'], "Requieren atención"),
    (k6, fs['planned_only'], "Solo Planificados", COLORS['planned'], "Sin actualizar"),
]

for col, val, label, color, sub in kpis:
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value" style="color:{color};">{val}</div>
            <div class="kpi-label">{label}</div>
            {"<div class='kpi-sub'>" + sub + "</div>" if sub else ""}
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ─── Charts Row 1 ─────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1.3, 1])

with col_left:
    st.markdown('<div class="section-title">📅 Ensayos por Mes</div>', unsafe_allow_html=True)

    months_sorted = sorted(months_str, key=lambda x: int(x))
    monthly_df = pd.DataFrame([
        {
            'Mes': MONTH_NAMES[m],
            'Planificados': fs['monthly_totals'].get(m, 0),
            'Realizados OK': sum(
                1 for rec in data
                if rec['etapa'] in selected_etapas
                for proj_list in (rec['schedule'].get(m, []),)
                for p in proj_list
                if p['project'] in selected_projects and p['status'] == 'done'
            ),
            'Sin Repositorio': sum(
                1 for rec in data
                if rec['etapa'] in selected_etapas
                for proj_list in (rec['schedule'].get(m, []),)
                for p in proj_list
                if p['project'] in selected_projects and p['status'] == 'partial'
            ),
            'No Realizados': sum(
                1 for rec in data
                if rec['etapa'] in selected_etapas
                for proj_list in (rec['schedule'].get(m, []),)
                for p in proj_list
                if p['project'] in selected_projects and p['status'] == 'not_done'
            ),
        }
        for m in months_sorted
    ])

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        name='Planificados',
        x=monthly_df['Mes'],
        y=monthly_df['Planificados'],
        marker_color=COLORS['planned'],
        opacity=0.85
    ))
    fig_bar.add_trace(go.Bar(
        name='Realizados OK',
        x=monthly_df['Mes'],
        y=monthly_df['Realizados OK'],
        marker_color=COLORS['success']
    ))
    fig_bar.add_trace(go.Bar(
        name='Sin Repositorio',
        x=monthly_df['Mes'],
        y=monthly_df['Sin Repositorio'],
        marker_color=COLORS['warning']
    ))
    fig_bar.add_trace(go.Bar(
        name='No Realizados',
        x=monthly_df['Mes'],
        y=monthly_df['No Realizados'],
        marker_color=COLORS['danger']
    ))
    fig_bar.update_layout(
        barmode='group',
        height=320,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
                    font=dict(size=11)),
        yaxis=dict(gridcolor='#E8EDF3', gridwidth=1),
        xaxis=dict(tickfont=dict(size=11)),
        font=dict(family='Inter, sans-serif', color=COLORS['text_dark']),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.markdown('<div class="section-title">📊 Distribución por Estado</div>', unsafe_allow_html=True)

    status_vals = [fs['done'], fs['partial'], fs['not_done'], fs['planned_only']]
    status_labels = ['Realizados OK', 'Sin Repositorio', 'No Realizados', 'Planificados']
    status_colors_list = [COLORS['success'], COLORS['warning'], COLORS['danger'], COLORS['planned']]

    fig_pie = go.Figure(go.Pie(
        labels=status_labels,
        values=status_vals,
        marker_colors=status_colors_list,
        hole=0.55,
        textinfo='percent',
        textfont=dict(size=12, family='Inter'),
        hovertemplate='<b>%{label}</b><br>%{value} ensayos<br>%{percent}<extra></extra>'
    ))
    fig_pie.update_layout(
        height=320,
        margin=dict(l=0, r=0, t=10, b=30),
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation='v', font=dict(size=11)),
        annotations=[dict(
            text=f"<b>{fs['total']}</b><br>Total",
            x=0.5, y=0.5,
            font_size=16, font_family='Inter',
            showarrow=False,
            font_color=COLORS['text_dark']
        )],
        font=dict(family='Inter, sans-serif'),
    )
    st.plotly_chart(fig_pie, use_container_width=True)


# ─── Charts Row 2 ─────────────────────────────────────────────────────────────
col_l2, col_r2 = st.columns([1, 1])

with col_l2:
    st.markdown('<div class="section-title">🏢 Ensayos por Etapa</div>', unsafe_allow_html=True)

    etapa_data = []
    for etapa in ['Estructura', 'Obra Gris', 'Obra Blanca']:
        if etapa not in selected_etapas:
            continue
        counts = {'Etapa': etapa, 'Realizados': 0, 'Sin Repo': 0, 'No Real.': 0, 'Planif.': 0}
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
                    if s == 'done':
                        counts['Realizados'] += 1
                    elif s == 'partial':
                        counts['Sin Repo'] += 1
                    elif s == 'not_done':
                        counts['No Real.'] += 1
                    else:
                        counts['Planif.'] += 1
        etapa_data.append(counts)

    if etapa_data:
        etapa_df = pd.DataFrame(etapa_data)
        fig_etapa = go.Figure()
        cats = ['Realizados', 'Sin Repo', 'No Real.', 'Planif.']
        cols_e = [COLORS['success'], COLORS['warning'], COLORS['danger'], COLORS['planned']]
        for cat, color in zip(cats, cols_e):
            fig_etapa.add_trace(go.Bar(
                name=cat, x=etapa_df['Etapa'], y=etapa_df[cat],
                marker_color=color
            ))
        fig_etapa.update_layout(
            barmode='stack', height=300,
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, font=dict(size=10)),
            yaxis=dict(gridcolor='#E8EDF3'),
            font=dict(family='Inter, sans-serif', color=COLORS['text_dark']),
        )
        st.plotly_chart(fig_etapa, use_container_width=True)

with col_r2:
    st.markdown('<div class="section-title">🏗️ Top Proyectos — Total Ensayos</div>', unsafe_allow_html=True)

    proj_totals = {}
    for proj, months_data in fs['proj_month'].items():
        if proj not in selected_projects:
            continue
        total = sum(len(v) for v in months_data.values())
        proj_totals[proj] = total

    if proj_totals:
        sorted_projs = sorted(proj_totals.items(), key=lambda x: x[1], reverse=True)[:12]
        pnames = [p[0] for p in sorted_projs]
        pvals = [p[1] for p in sorted_projs]

        fig_proj = go.Figure(go.Bar(
            x=pvals,
            y=pnames,
            orientation='h',
            marker_color=COLORS['secondary'],
            hovertemplate='<b>%{y}</b><br>%{x} ensayos<extra></extra>'
        ))
        fig_proj.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(autorange='reversed', tickfont=dict(size=10)),
            xaxis=dict(gridcolor='#E8EDF3'),
            font=dict(family='Inter, sans-serif', color=COLORS['text_dark']),
        )
        st.plotly_chart(fig_proj, use_container_width=True)


# ─── Heatmap Matrix ───────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🔥 Matriz Intensidad — Proyecto × Mes (cantidad de ensayos)</div>', unsafe_allow_html=True)

heat_data = []
for proj in selected_projects:
    row = {'Proyecto': proj}
    for m in months_sorted:
        month_entries = fs['proj_month'].get(proj, {}).get(m, [])
        row[MONTH_NAMES[m]] = len(month_entries)
    heat_data.append(row)

heat_df = pd.DataFrame(heat_data).set_index('Proyecto')
heat_month_cols = [MONTH_NAMES[m] for m in months_sorted]
heat_df = heat_df[heat_month_cols]

fig_heat = go.Figure(go.Heatmap(
    z=heat_df.values,
    x=heat_df.columns,
    y=heat_df.index,
    colorscale=[
        [0.0, '#F4F7FB'],
        [0.2, '#C8DCF0'],
        [0.5, COLORS['accent']],
        [0.8, COLORS['secondary']],
        [1.0, COLORS['primary']],
    ],
    hovertemplate='<b>%{y}</b><br>Mes: %{x}<br>Ensayos: %{z}<extra></extra>',
    showscale=True,
    colorbar=dict(title='Ensayos', thickness=14, len=0.8, tickfont=dict(size=10))
))
fig_heat.update_layout(
    height=max(280, len(selected_projects) * 28 + 60),
    margin=dict(l=0, r=60, t=10, b=0),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(tickfont=dict(size=11)),
    yaxis=dict(tickfont=dict(size=10)),
    font=dict(family='Inter, sans-serif', color=COLORS['text_dark']),
)
st.plotly_chart(fig_heat, use_container_width=True)


# ─── Interactive Matrix with Tooltip ─────────────────────────────────────────
st.markdown('<div class="section-title">📋 Matriz Detallada — Proyecto × Mes (con detalle de ensayos)</div>', unsafe_allow_html=True)
st.markdown("<p style='font-size:12px;color:#7B97B8;'>💡 Pasa el cursor sobre los valores para ver los ensayos correspondientes.</p>", unsafe_allow_html=True)

# Build hover text
z_vals = []
hover_text = []
proj_labels = []
for proj in selected_projects:
    row_z = []
    row_hover = []
    proj_labels.append(proj)
    for m in months_sorted:
        entries = fs['proj_month'].get(proj, {}).get(m, [])
        count = len(entries)
        row_z.append(count)
        if entries:
            lines = [f"<b>{proj}</b> — {MONTH_NAMES[m]}",
                     f"<b>{count} ensayo(s):</b>", "─────────────────"]
            for e in entries[:15]:
                icon = {'done': '✅', 'partial': '⚠️', 'not_done': '❌', 'planned': '📋'}.get(e['status'], '📋')
                lines.append(f"{icon} {e['ensayo'][:45]}")
            if len(entries) > 15:
                lines.append(f"...y {len(entries)-15} más")
            row_hover.append("<br>".join(lines))
        else:
            row_hover.append(f"<b>{proj}</b> — {MONTH_NAMES[m]}<br>Sin ensayos")
    z_vals.append(row_z)
    hover_text.append(row_hover)

# Status overlay: compute dominant status per cell
status_z = []
for proj in selected_projects:
    row_s = []
    for m in months_sorted:
        entries = fs['proj_month'].get(proj, {}).get(m, [])
        if not entries:
            row_s.append(0)
        else:
            statuses = [e['status'] for e in entries]
            if any(s == 'not_done' for s in statuses):
                row_s.append(3)
            elif any(s == 'partial' for s in statuses):
                row_s.append(2)
            elif all(s == 'done' for s in statuses):
                row_s.append(4)
            else:
                row_s.append(1)
    status_z.append(row_s)

colorscale_status = [
    [0.00, '#F4F7FB'],  # empty
    [0.25, COLORS['planned']],  # planned
    [0.50, COLORS['warning']],  # partial
    [0.75, COLORS['danger']],   # not done
    [1.00, COLORS['success']],  # done
]

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
        [0.0, '#F4F7FB'],
        [0.01, '#DCE8F5'],
        [0.3, COLORS['accent']],
        [0.7, COLORS['secondary']],
        [1.0, COLORS['primary']],
    ],
    showscale=True,
    colorbar=dict(title='# Ensayos', thickness=14, len=0.8, tickfont=dict(size=10)),
))
fig_matrix.update_layout(
    height=max(300, len(selected_projects) * 32 + 80),
    margin=dict(l=0, r=60, t=10, b=0),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(tickfont=dict(size=12), side='top'),
    yaxis=dict(tickfont=dict(size=10), autorange='reversed'),
    font=dict(family='Inter, sans-serif', color=COLORS['text_dark']),
)
st.plotly_chart(fig_matrix, use_container_width=True)


# ─── Detailed Table ───────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🔎 Detalle de Ensayos</div>', unsafe_allow_html=True)

col_s1, col_s2 = st.columns(2)
with col_s1:
    search_project = st.selectbox("Proyecto", ["Todos"] + selected_projects)
with col_s2:
    search_month = st.selectbox("Mes", ["Todos"] + [f"{MONTH_NAMES[m]} (Mes {m})" for m in months_sorted])

# Build table
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
            if search_project != "Todos" and p['project'] != search_project:
                continue
            if search_month != "Todos" and f"{MONTH_NAMES[month]} (Mes {month})" != search_month:
                continue
            table_rows.append({
                'Etapa': rec['etapa'],
                'Material': rec['material'],
                'Ensayo': rec['ensayo'],
                'NTC': rec['ntc'],
                'Proyecto': p['project'],
                'Mes': f"{MONTH_NAMES[month]}",
                'Estado': STATUS_LABELS.get(p['status'], p['status']),
                'Valor': str(p['value'])
            })

if table_rows:
    df_table = pd.DataFrame(table_rows)
    st.dataframe(
        df_table,
        use_container_width=True,
        height=320,
        column_config={
            'Ensayo': st.column_config.TextColumn(width='large'),
            'NTC': st.column_config.TextColumn(width='small'),
            'Estado': st.column_config.TextColumn(width='medium'),
        }
    )
    st.markdown(f"<p style='font-size:11px;color:{COLORS['text_mid']};'>Mostrando {len(df_table)} registros</p>", unsafe_allow_html=True)
else:
    st.info("No hay registros con los filtros seleccionados.")


# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-top:40px; padding:16px; background:{COLORS['card_bg']}; border:1px solid {COLORS['border']}; 
     border-radius:10px; text-align:center; font-size:12px; color:{COLORS['text_mid']};">
    📋 <b>Plan de Ensayos CUSEZAR 2026</b> · Dashboard generado automáticamente desde archivo Excel ·
    Para actualizar, sube el archivo con valores 0 / 0.5 / 1 / * en la barra lateral
</div>
""", unsafe_allow_html=True)
