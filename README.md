# 🧪 Plan de Ensayos 2026 — Dashboard Cusezar

Dashboard interactivo para el seguimiento del plan de ensayos de calidad de materiales en obra, construido con **Streamlit** y **Plotly**.

---

## 🚀 Ver en Streamlit Cloud

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

---

## 📁 Estructura del repositorio

```
├── app.py                        # Aplicación principal Streamlit
├── Plan_de_ensayos_2026.xlsx     # Fuente de datos (actualizar aquí)
├── requirements.txt              # Dependencias Python
├── .streamlit/
│   └── config.toml               # Configuración de tema
└── README.md
```

---

## 🔧 Instalación local

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/plan-ensayos-2026.git
cd plan-ensayos-2026

# 2. Crear entorno virtual (opcional pero recomendado)
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la app
streamlit run app.py
```

La app quedará disponible en `http://localhost:8501`

---

## ☁️ Despliegue en Streamlit Cloud

1. Hacer **fork** o subir este repositorio a GitHub (debe ser público o privado con acceso).
2. Ir a [share.streamlit.io](https://share.streamlit.io) e iniciar sesión con GitHub.
3. Clic en **"New app"**.
4. Seleccionar el repositorio, la rama (`main`) y el archivo principal (`app.py`).
5. Clic en **"Deploy!"**.

---

## 📊 Pestañas del dashboard

| Pestaña | Descripción |
|---|---|
| **📊 Resumen** | KPIs globales, barras por mes y por proyecto |
| **✅ Cumplimiento** | Gauge global, barras segmentadas por proyecto |
| **📅 Cronograma** | Evolución mensual vs. meta planeada + mapa de calor |
| **🔧 Ensayos** | Vista del ingeniero: lista detallada y agrupada por obra/mes |

---

## 🔄 Actualización de datos

Para actualizar los datos simplemente reemplaza el archivo:

```
Plan_de_ensayos_2026.xlsx
```

La hoja debe llamarse **`Ensayos`** y conservar las columnas:

| Columna | Descripción |
|---|---|
| `ETAPA` | Estructura / Obra Gris |
| `MATERIAL` | Tipo de material ensayado |
| `ENSAYO` | Nombre del ensayo |
| `NTC` | Norma técnica aplicable |
| `FRECUENCIA` | Descripción de la frecuencia |
| `Proyecto` | Nombre del proyecto |
| `Mes` | Número de mes (1–12) |
| `Cantidad` | `*` = planeado, `1` = realizado, `0.5` = parcial, `0` = no realizado |

---

## 📋 Estados de los ensayos

| Valor en `Cantidad` | Estado | Significado |
|---|---|---|
| `*` | 📋 Planeado | Programado, no ejecutado aún |
| `1` | ✅ Realizado | Ejecutado y subido al repositorio |
| `0.5` | ⏳ Parcial | Realizado pero **no subido** al repositorio |
| `0` | ❌ No Realizado | Mes vencido, no se ejecutó |

---

## 🧮 Fórmula de cumplimiento

```
Cumplimiento = (Realizados + Parciales × 0.5) / (Realizados + Parciales + No Realizados) × 100
```

Los ensayos **Planeados** se excluyen del denominador ya que aún no han vencido.

---

*Desarrollado para el equipo de calidad de Cusezar · 2026*
