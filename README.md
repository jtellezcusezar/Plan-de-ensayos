# 🏗️ Dashboard Plan de Ensayos — CUSEZAR 2026

Dashboard interactivo para el seguimiento y control del plan de ensayos de calidad por proyecto, construido con Streamlit y Plotly.

## 📦 Estructura del repositorio

```
├── app.py                          # Dashboard principal Streamlit
├── parse_excel.py                  # Parser del archivo Excel
├── Plan_de_ensayos_2026.xlsx       # Archivo de datos (actualizable)
├── requirements.txt
└── README.md
```

## 🚀 Despliegue en Streamlit Cloud

1. **Sube este repositorio a GitHub** (puede ser privado o público)
2. Ve a [share.streamlit.io](https://share.streamlit.io) e inicia sesión con tu cuenta GitHub
3. Haz clic en **"New app"** y selecciona tu repositorio
4. Configura:
   - **Repository:** `tu-usuario/tu-repositorio`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Haz clic en **Deploy** ✅

## 💻 Ejecución local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
streamlit run app.py
```

## 🔄 Actualización de datos

### Formato del archivo Excel

El archivo `Plan_de_ensayos_2026.xlsx` acepta los siguientes valores en las celdas de la matriz:

| Valor | Significado |
|-------|-------------|
| `*`   | Ensayo planificado (aún sin ejecutar) |
| `1`   | Ensayo realizado correctamente y en repositorio ✅ |
| `0.5` | Ensayo realizado pero **no subido** al repositorio ⚠️ |
| `0`   | Ensayo **no realizado** ❌ |

### Cómo actualizar

**Opción A — Subida directa en el dashboard:**
- Usa el botón **"Subir Excel actualizado"** en la barra lateral del dashboard
- El dashboard se recalcula automáticamente

**Opción B — Actualización en GitHub:**
1. Reemplaza `Plan_de_ensayos_2026.xlsx` en el repositorio con el archivo actualizado
2. El dashboard en Streamlit Cloud se actualiza automáticamente al hacer `git push`

```bash
# Desde tu terminal local
git add Plan_de_ensayos_2026.xlsx
git commit -m "Actualizar ensayos - [mes/año]"
git push origin main
```

## 📊 Funcionalidades del Dashboard

- **KPIs:** Total planificados, ejecutados, realizados OK, sin repositorio, no realizados
- **Gráfico de barras:** Ensayos por mes y estado
- **Gráfico de torta:** Distribución global por estado
- **Gráfico por etapa:** Estructura / Obra Gris / Obra Blanca
- **Ranking de proyectos:** Top proyectos por volumen de ensayos
- **Heatmap de intensidad:** Visualización proyecto × mes
- **Matriz interactiva:** Con tooltip al pasar el cursor mostrando los ensayos
- **Tabla detallada:** Filtrable por proyecto y mes

## 🔍 Filtros disponibles

- Por **mes** (enero a diciembre)
- Por **proyecto** (uno o múltiples)
- Por **etapa** (Estructura, Obra Gris, Obra Blanca)

---
*Desarrollado para CUSEZAR — Control de Calidad 2026*
