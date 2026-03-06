"""
Dashboard Ejecutivo de Programación de Ensayos - CUSEZAR 2026
Diseño Inmersivo, Corporativo y sin Sidebar.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from parse_excel import parse_excel

# ─── Configuración de la Página ───────────────────────────────────────────────
st.set_page_config(
    page_title="Control de Calidad 2026 | CUSEZAR",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed" # Ocultamos el sidebar por defecto
)

# ─── Diccionarios y Estilos Corporativos ──────────────────────────────────────
MONTH_NAMES = {
    1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
    7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
}

STATUS_CONFIG = {
    'done':     {'label': '✅ OK (1)', 'color': '#10B981'},       # Verde Esmeralda
    'partial':  {'label': '⚠️ Faltan Docs (0.5)', 'color': '#F59E0B'}, # Ámbar
    'not_done': {'label': '❌ No Realizado (0)', 'color': '#EF4444'},  # Rojo Coral
    'planned':  {'label': '⏳ Planificado (*)', 'color': '#94A3B8'}    # Gris Pizarra
}

# CSS para inmersión total y limpieza de la UI de Streamlit
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F8FAFC;}
    
    /* Ocultar elementos nativos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;} /* Esconder el botón del sidebar */
    
    /* Tarjetas de Métricas Personalizadas */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 5% 10%;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        text-align: center;
    }
    div[data-testid="stMetricValue"] { font-size: 32px; font-weight: 700; color: #0F172A; }
    div[data-testid="stMetricLabel"] { font-size: 13px; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; }
    
    /* Panel de Control Superior */
    .control-panel {
        background: #FFFFFF;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        border: 1px solid #E2E8F0;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── Carga de Datos Estática (Directo del Repo) ───────────────────────────────
@st.cache_data
def load_data():
    file_path = Path("Plan_de_ensayos_2026.xlsx")
    if not file_path.exists():
        file_path = Path("../Plan_de_ensayos_2026.xlsx")
    if file_path.exists():
        return parse_excel(str(file_path))
    return []

raw_data = load_data()

if not raw_data:
    st.error("⚠️ No se encontró el archivo 'Plan_de_ensayos_2026.xlsx' en el repositorio.")
    st.stop()

# Procesar datos planos para facilitar cruces
flat_data = []
for rec in raw_data:
    for month_num, projs in rec['schedule'].items():
        for p in projs:
            flat_data.append({
                'Ensayo': rec['ensayo'],
                'Material': rec['material'],
                'Etapa': rec['etapa'],
                'Mes_Num': int(month_num),
                'Proyecto': p['project'],
                'Estado': p['status'],
                'Estado_Label': STATUS_CONFIG[p['status']]['label']
            })

df_all = pd.DataFrame(flat_data)
present_projects = sorted(df_all['Proyecto'].unique())
etapas_in_data = sorted(df_all['Etapa'].unique())

# ─── CABECERA DEL DASHBOARD ───────────────────────────────────────────────────
col_title, col_logo = st.columns([4, 1])
with col_title:
    st.markdown("<h1 style='color: #0F172A; margin-bottom: 0;'>Panel de Control de Calidad 2026</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; font-size: 16px; margin-top: 0;'>Dirección de Obra y Ensayos Técnicos — <b>CUSEZAR</b></p>", unsafe_allow_html=True)

# ─── PANEL DE CONTROL INMERSIVO (Filtros) ─────────────────────────────────────
st.markdown('<div class="control-panel">', unsafe_allow_html=True)
st.markdown("##### 🎛️ Filtros de Visualización")

ctrl1, ctrl2, ctrl3 = st.columns([1.5, 1, 1.5])

with ctrl1:
    # Selector principal: PROYECTO
    selected_projects = st.multiselect(
        "🏢 Proyectos (Dejar vacío para ver todos)", 
        options=present_projects, 
        placeholder="Seleccione uno o varios proyectos..."
    )
    if not selected_projects:
        selected_projects = present_projects

with ctrl2:
    # Selector inmersivo de Etapa (Usa Segmented Control si está disponible, sino Multiselect)
    selected_etapas = st.multiselect(
        "🏗️ Etapas Constructivas",
        options=etapas_in_data,
        default=etapas_in_data
    )

with ctrl3:
    # Uso de Slider para rango de meses (Mucho más elegante que un menú desplegable)
    mes_rango = st.slider(
        "📅 Rango de Meses", 
        min_value=1, max_value=12, value=(1, 12),
        format="Mes %d"
    )
    selected_months = list(range(mes_rango[0], mes_rango[1] + 1))

st.markdown('</div>', unsafe_allow_html=True)

# ─── APLICAR FILTROS ──────────────────────────────────────────────────────────
df = df_all[
    (df_all['Proyecto'].isin(selected_projects)) & 
    (df_all['Etapa'].isin(selected_etapas)) & 
    (df_all['Mes_Num'].isin(selected_months))
].copy()

if df.empty:
    st.info("No hay ensayos programados para la combinación de filtros seleccionada.")
    st.stop()

# ─── KPIs PRINCIPALES ─────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)

total_ensayos = len(df)
realizados_ok = len(df[df['Estado'] == 'done'])
faltan_docs = len(df[df['Estado'] == 'partial'])
no_realizados = len(df[df['Estado'] == 'not_done'])
planificados = len(df[df['Estado'] == 'planned'])

k1.metric("📋 Total Ensayos", f"{total_ensayos:,}")
k2.metric("✅ Correctos (1)", f"{realizados_ok:,}")
k3.metric("⚠️ Falta Repo (0.5)", f"{faltan_docs:,}")
k4.metric("❌ No Ejecutados (0)", f"{no_realizados:,}")

st.markdown("<hr style='border: 1px solid #F1F5F9; margin: 2rem 0;'>", unsafe_allow_html=True)

# ─── VISTAS DEL DASHBOARD (TABS) ──────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📊 Rendimiento Global", 
    "🔥 Heatmap de Operación", 
    "🗂️ Registro Detallado"
])

# ==========================================
# TAB 1: RENDIMIENTO GLOBAL
# ==========================================
with tab1:
    st.markdown("### Cumplimiento y Avance de Ensayos")
    col_g1, col_g2 = st.columns([1, 1])
    
    with col_g1:
        # Gráfico de Donas para Estado (Utilizando los pesos de evaluación 1, 0.5, 0, *)
        df_estado = df.groupby('Estado_Label').size().reset_index(name='Cantidad')
        
        # Mapear colores desde la configuración
        color_map = {v['label']: v['color'] for v in STATUS_CONFIG.values()}
        
        fig_donut = px.pie(
            df_estado, names='Estado_Label', values='Cantidad', hole=0.6,
            color='Estado_Label', color_discrete_map=color_map
        )
        fig_donut.update_traces(textposition='inside', textinfo='percent+label', showlegend=False)
        fig_donut.update_layout(
            annotations=[dict(text='Estado<br>Actual', x=0.5, y=0.5, font_size=20, showarrow=False)],
            margin=dict(t=30, b=0, l=0, r=0)
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        
    with col_g2:
        # Ensayos por Mes apilados por estado
        df_mes_estado = df.groupby(['Mes_Num', 'Estado_Label']).size().reset_index(name='Cantidad')
        df_mes_estado['Mes'] = df_mes_estado['Mes_Num'].map(MONTH_NAMES)
        
        fig_bar = px.bar(
            df_mes_estado, x='Mes', y='Cantidad', color='Estado_Label',
            color_discrete_map=color_map, text_auto=True
        )
        fig_bar.update_layout(
            xaxis_title="", yaxis_title="Nº Ensayos",
            legend_title="Calificación", barmode='stack',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# ==========================================
# TAB 2: HEATMAP DE OPERACIÓN
# ==========================================
with tab2:
    st.markdown("### Densidad de Programación por Proyecto")
    st.markdown("Identifica cuellos de botella mensuales por proyecto. :blue[Mayor intensidad] = Mayor cantidad de ensayos planificados.")
    
    # Crear la matriz
    heatmap_data = df.pivot_table(index='Proyecto', columns='Mes_Num', aggfunc='size', fill_value=0)
    
    # Asegurar orden y formatear nombres de meses
    heatmap_data = heatmap_data[sorted(heatmap_data.columns)]
    heatmap_data.columns = [MONTH_NAMES[c] for c in heatmap_data.columns]
    
    fig_heat = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='Blues', # Escala corporativa limpia
        text=heatmap_data.values,
        texttemplate="%{text}",
        textfont={"size": 13, "family": "Inter"},
        showscale=True
    ))
    
    fig_heat.update_layout(
        height=max(350, len(heatmap_data.index) * 45), # Altura dinámica
        margin=dict(t=20, l=0, r=0, b=0)
    )
    st.plotly_chart(fig_heat, use_container_width=True)

# ==========================================
# TAB 3: REGISTRO DETALLADO (Dataframe)
# ==========================================
with tab3:
    st.markdown("### Matriz de Inspección de Ensayos")
    
    # Buscador en texto libre para la tabla
    search = st.text_input("🔍 Buscar ensayo, material o NTC específico...", placeholder="Ej: Concreto, Acero...")
    
    df_show = df.copy()
    if search:
        mask = df_show['Ensayo'].str.contains(search, case=False, na=False) | \
               df_show['Material'].str.contains(search, case=False, na=False)
        df_show = df_show[mask]
    
    # Pivotear la tabla para que sea fácil de leer (Proyecto/Ensayo -> Meses)
    df_pivot = pd.pivot_table(
        df_show, 
        index=['Proyecto', 'Etapa', 'Ensayo', 'Material'], 
        columns='Mes_Num', 
        values='Estado_Label',
        aggfunc=lambda x: ' '.join(set(x)), # Evitar duplicados
        fill_value='—'
    ).reset_index()
    
    # Renombrar columnas de meses
    col_mapping = {m: MONTH_NAMES[m] for m in range(1, 13) if m in df_pivot.columns}
    df_pivot.rename(columns=col_mapping, inplace=True)
    
    st.dataframe(
        df_pivot,
        use_container_width=True,
        hide_index=True,
        height=600
    )
