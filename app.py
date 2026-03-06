"""
Dashboard de Programación de Ensayos - CUSEZAR 2026
Arquitectura Profesional con Tabs y Sidebar
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import tempfile, os
from pathlib import Path
from parse_excel import parse_excel, PROJECTS

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Plan de Ensayos 2026 | CUSEZAR",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Constantes y Mapeos ──────────────────────────────────────────────────────
MONTH_NAMES = {
    '1': 'Ene', '2': 'Feb', '3': 'Mar', '4': 'Abr',
    '5': 'May', '6': 'Jun', '7': 'Jul', '8': 'Ago',
    '9': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dic'
}
ALL_ETAPAS = ['Estructura', 'Obra Gris', 'Obra Blanca']

# ─── CSS Personalizado ────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    /* Ocultar elementos por defecto de Streamlit para un look más limpio */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Tarjetas KPI */
    div[data-testid="stMetricValue"] { font-size: 28px; font-weight: 700; color: #1B3A5C; }
    div[data-testid="stMetricLabel"] { font-size: 14px; font-weight: 600; color: #4A5568; text-transform: uppercase; }
    
    /* Headers de pestañas */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; font-size: 16px; font-weight: 600; }
    
    /* Tarjetas de Proyecto */
    .project-card {
        background-color: #ffffff; padding: 20px; border-radius: 12px;
        border: 1px solid #E2E8F0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    .project-card h3 { margin-top: 0; color: #1B3A5C; font-size: 20px; border-bottom: 2px solid #F1F5F9; padding-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# ─── Carga de Datos ───────────────────────────────────────────────────────────
@st.cache_data
def load_data(source_bytes=None):
    if source_bytes:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            tmp.write(source_bytes)
            tmp_path = tmp.name
        data = parse_excel(tmp_path)
        os.unlink(tmp_path)
        return data
    else:
        for p in [Path("Plan_de_ensayos_2026.xlsx"), Path("../Plan_de_ensayos_2026.xlsx")]:
            if p.exists():
                return parse_excel(str(p))
    return None

# ─── Sidebar: Navegación y Filtros ────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/c/ce/Transparent.gif", width=50) # Espacio para logo
    st.markdown("### 🏗️ CUSEZAR\n**Control de Calidad 2026**")
    st.divider()
    
    # 1. Carga de Archivos
    uploaded = st.file_uploader("📂 Actualizar Datos (Excel)", type=["xlsx"])
    data = load_data(uploaded.getvalue() if uploaded else None)
    
    if not data:
        st.warning("⚠️ Sube el archivo Excel para comenzar.")
        st.stop()
        
    present_projects = sorted({p['project'] for rec in data for projs in rec['schedule'].values() for p in projs})
    etapas_in_data = [e for e in ALL_ETAPAS if e in {r['etapa'] for r in data}]

    st.divider()
    st.markdown("### 🔍 Filtros Globales")
    
    # Filtro principal: PROYECTO
    selected_projects = st.multiselect("🏢 Proyectos", options=present_projects, default=present_projects)
    
    # Filtros secundarios
    selected_months = st.multiselect("📅 Meses", options=list(range(1, 13)), default=list(range(1, 13)), format_func=lambda m: MONTH_NAMES[str(m)])
    selected_etapas = st.multiselect("🏗️ Etapas", options=etapas_in_data, default=etapas_in_data)
    
    if not selected_projects: selected_projects = present_projects
    if not selected_months: selected_months = list(range(1, 13))
    if not selected_etapas: selected_etapas = etapas_in_data

months_str = [str(m) for m in selected_months]

# ─── Procesamiento de Datos Filtrados ─────────────────────────────────────────
flat_data = []
for rec in data:
    if rec['etapa'] not in selected_etapas: continue
    for month_num, projs in rec['schedule'].items():
        if month_num not in months_str: continue
        for p in projs:
            if p['project'] not in selected_projects: continue
            flat_data.append({
                'Ensayo': rec['ensayo'],
                'Material': rec['material'],
                'Etapa': rec['etapa'],
                'Mes_Num': int(month_num),
                'Mes': MONTH_NAMES[month_num],
                'Proyecto': p['project'],
                'Estado': p['status']
            })

df = pd.DataFrame(flat_data)

# Si el DataFrame está vacío, mostrar mensaje y detener
if df.empty:
    st.info("No hay datos para los filtros seleccionados.")
    st.stop()

# ─── Dashboard Principal (Tabs) ───────────────────────────────────────────────
st.title("📊 Dashboard de Plan de Ensayos")

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Resumen Ejecutivo", 
    "🔥 Heatmap de Carga", 
    "📋 Detalle de Ensayos", 
    "🏢 Fichas por Proyecto"
])

# ==========================================
# TAB 1: RESUMEN EJECUTIVO
# ==========================================
with tab1:
    # KPIs
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    total_ensayos = len(df)
    realizados = len(df[df['Estado'] == 'done'])
    pendientes = len(df[df['Estado'].isin(['planned', 'not_done'])])
    progreso = (realizados / total_ensayos * 100) if total_ensayos > 0 else 0
    
    kpi1.metric("Total Programaciones", f"{total_ensayos:,}")
    kpi2.metric("Realizados OK", f"{realizados:,}")
    kpi3.metric("Pendientes", f"{pendientes:,}")
    kpi4.metric("Avance Global", f"{progreso:.1f}%")
    
    st.markdown("---")
    
    # Gráficos fila 1
    c1, c2 = st.columns([6, 4])
    
    with c1:
        st.subheader("Ensayos por Mes")
        df_month_etapa = df.groupby(['Mes_Num', 'Mes', 'Etapa']).size().reset_index(name='Cantidad')
        df_month_etapa = df_month_etapa.sort_values('Mes_Num')
        fig1 = px.bar(df_month_etapa, x='Mes', y='Cantidad', color='Etapa', 
                      color_discrete_sequence=['#1B3A5C', '#4A9FD4', '#E8A838'],
                      text_auto=True)
        fig1.update_layout(xaxis_title="", yaxis_title="Cantidad", margin=dict(t=20, b=0))
        st.plotly_chart(fig1, use_container_width=True)
        
    with c2:
        st.subheader("Distribución por Etapa")
        df_etapa = df.groupby('Etapa').size().reset_index(name='Cantidad')
        fig2 = px.pie(df_etapa, names='Etapa', values='Cantidad', hole=0.55,
                      color_discrete_sequence=['#1B3A5C', '#4A9FD4', '#E8A838'])
        fig2.update_layout(margin=dict(t=20, b=0), showlegend=True)
        st.plotly_chart(fig2, use_container_width=True)
        
    # Gráficos fila 2
    c3, c4 = st.columns(2)
    
    with c3:
        st.subheader("Top Proyectos (Volumen)")
        df_proj = df.groupby('Proyecto').size().reset_index(name='Cantidad').sort_values('Cantidad', ascending=True).tail(10)
        fig3 = px.bar(df_proj, x='Cantidad', y='Proyecto', orientation='h', color_discrete_sequence=['#2E6DA4'])
        fig3.update_layout(xaxis_title="", yaxis_title="", margin=dict(t=20, l=0))
        st.plotly_chart(fig3, use_container_width=True)
        
    with c4:
        st.subheader("Materiales más Frecuentes")
        df_mat = df.groupby('Material').size().reset_index(name='Cantidad').sort_values('Cantidad', ascending=True).tail(10)
        fig4 = px.bar(df_mat, x='Cantidad', y='Material', orientation='h', color_discrete_sequence=['#2D8A5F'])
        fig4.update_layout(xaxis_title="", yaxis_title="", margin=dict(t=20, l=0))
        st.plotly_chart(fig4, use_container_width=True)

# ==========================================
# TAB 2: HEATMAP POR PROYECTO
# ==========================================
with tab2:
    st.subheader("Intensidad de Ensayos (Proyecto vs Mes)")
    st.markdown("Visualiza la carga de trabajo programada. :green[Verde claro] = Baja carga, :orange[Amarillo/Naranja] = Alta carga.")
    
    heatmap_data = df.pivot_table(index='Proyecto', columns='Mes_Num', aggfunc='size', fill_value=0)
    
    # Asegurar que todas las columnas de meses seleccionados existan
    for m in selected_months:
        if m not in heatmap_data.columns:
            heatmap_data[m] = 0
            
    heatmap_data = heatmap_data[sorted(heatmap_data.columns)]
    heatmap_data.columns = [MONTH_NAMES[str(c)] for c in heatmap_data.columns]
    
    fig_heat = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale=[[0, '#E8F5E9'], [0.5, '#AED581'], [1, '#FBC02D']], # Verde claro a Amarillo/Naranja
        text=heatmap_data.values,
        texttemplate="%{text}",
        textfont={"size":12, "color":"black"},
        showscale=False
    ))
    
    fig_heat.update_layout(
        height=max(400, len(heatmap_data.index) * 40),
        margin=dict(t=20, l=0, r=0, b=0),
        xaxis_nticks=12
    )
    st.plotly_chart(fig_heat, use_container_width=True)

# ==========================================
# TAB 3: TABLA DE ENSAYOS
# ==========================================
with tab3:
    st.subheader("Directorio de Ensayos Programados")
    
    # Controles de la tabla
    col_search, col_f1, col_f2 = st.columns([2, 1, 1])
    search_query = col_search.text_input("🔍 Buscar por ensayo o material...", "")
    
    # Preparar datos cruzados (Ensayo vs Mes)
    # Mostramos puntos de colores dependiendo si está programado
    df_table = df.copy()
    
    if search_query:
        mask = df_table['Ensayo'].str.contains(search_query, case=False, na=False) | \
               df_table['Material'].str.contains(search_query, case=False, na=False)
        df_table = df_table[mask]
    
    # Pivotear para crear la vista de matriz con puntos
    pivot_table = pd.pivot_table(
        df_table, 
        index=['Proyecto', 'Etapa', 'Ensayo', 'Material'], 
        columns='Mes_Num', 
        aggfunc='size', 
        fill_value=0
    ).reset_index()
    
    # Formatear columnas de meses con puntos (🔵 programado, ⚪ no programado)
    for m in range(1, 13):
        if m in selected_months:
            col_name = MONTH_NAMES[str(m)]
            if m in pivot_table.columns:
                pivot_table[col_name] = pivot_table[m].apply(lambda x: "🔵" if x > 0 else "⚪")
                pivot_table = pivot_table.drop(columns=[m])
            else:
                pivot_table[col_name] = "⚪"
                
    st.dataframe(
        pivot_table,
        use_container_width=True,
        hide_index=True,
        height=500
    )
    st.caption("🔵 = Ensayo programado en el mes | ⚪ = Sin programación")

# ==========================================
# TAB 4: POR PROYECTO
# ==========================================
with tab4:
    st.subheader("Visión Detallada por Obra")
    
    if not selected_projects:
        st.warning("Selecciona al menos un proyecto en la barra lateral.")
    else:
        # Organizar tarjetas en una cuadrícula de 2 columnas
        cols = st.columns(2)
        
        for i, proj in enumerate(selected_projects):
            proj_df = df[df['Proyecto'] == proj]
            total_proj = len(proj_df)
            
            with cols[i % 2]:
                st.markdown(f"""
                <div class="project-card">
                    <h3>🏢 {proj}</h3>
                    <p style="font-size:14px; color:#4A5568;">Total programaciones: <b>{total_proj}</b></p>
                </div>
                """, unsafe_allow_html=True)
                
                if total_proj > 0:
                    # Barra de composición por etapa
                    df_comp = proj_df.groupby('Etapa').size().reset_index(name='Cantidad')
                    df_comp['Porcentaje'] = (df_comp['Cantidad'] / total_proj) * 100
                    
                    fig_comp = px.bar(df_comp, x='Porcentaje', y=['']*len(df_comp), color='Etapa',
                                      orientation='h', text=df_comp['Etapa'] + ': ' + df_comp['Cantidad'].astype(str),
                                      color_discrete_sequence=['#1B3A5C', '#4A9FD4', '#E8A838'])
                    
                    fig_comp.update_layout(
                        barmode='stack', height=100, margin=dict(l=0, r=0, t=0, b=0),
                        xaxis=dict(showgrid=False, visible=False),
                        yaxis=dict(showgrid=False, visible=False),
                        showlegend=False,
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig_comp, use_container_width=True, key=f"comp_{proj}")
                else:
                    st.info("No hay ensayos programados con los filtros actuales.")
