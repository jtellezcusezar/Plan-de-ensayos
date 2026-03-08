# 🏗️ Plan de Ensayos 2026 — Dashboard de Control de Calidad

Dashboard interactivo desarrollado en **Streamlit** para visualizar y gestionar el plan de ensayos de laboratorio de los proyectos de construcción de Cusezar.

---

## 📁 Estructura del repositorio

```
├── app.py                        # Aplicación principal Streamlit
├── Plan_de_ensayos_2026.xlsx     # Fuente de datos (hoja: Ensayos)
├── requirements.txt              # Dependencias Python
└── README.md                     # Este archivo
```

---

## 📊 Contenido del Dashboard

| Pestaña | Descripción |
|---|---|
| 📊 Resumen General | KPIs globales, distribución de estados, avance por proyecto y evolución mensual |
| 🏗️ Por Proyecto y Material | Heatmap Proyecto × Mes, estado por material, tasa de cumplimiento |
| 📅 Línea de Tiempo y Alertas | Semáforo por proyecto, evolución acumulada, tabla de ensayos críticos |
| 🔍 Consulta de Ensayos | Buscador libre con filtros por proyecto, mes, material, etapa y estado |

---

## 📋 Codificación de estados (columna `Cantidad`)

| Valor | Estado | Significado |
|---|---|---|
| `*` | 🔵 Planeado | Programado, aún no ejecutado |
| `0` | ❌ No Realizado | Debía ejecutarse y no se realizó |
| `0.5` | ⚠️ Incompleto | Realizado pero no subido al repositorio |
| `1` | ✅ Completo | Realizado y registrado en el repositorio |

> **Nota:** La tasa de cumplimiento se calcula **únicamente** sobre los ensayos ejecutables (valores `0`, `0.5`, `1`). Los planeados (`*`) se excluyen del cálculo.

---

## 🚀 Despliegue en Streamlit Community Cloud

### Paso 1 — Subir archivos a GitHub

1. Crea un repositorio en [github.com](https://github.com) (puede ser público o privado).
2. Sube los siguientes archivos al repositorio:
   - `app.py`
   - `Plan_de_ensayos_2026.xlsx`
   - `requirements.txt`
   - `README.md`

   Puedes hacerlo directamente desde la interfaz web de GitHub o con los comandos:
   ```bash
   git init
   git add .
   git commit -m "first commit: plan de ensayos dashboard"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
   git push -u origin main
   ```

### Paso 2 — Conectar con Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io) e inicia sesión con tu cuenta de GitHub.
2. Haz clic en **"New app"**.
3. Completa los campos:
   - **Repository:** `TU_USUARIO/TU_REPOSITORIO`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Haz clic en **"Deploy!"**.

Streamlit instalará las dependencias automáticamente desde `requirements.txt` y levantará la app en pocos minutos.

---

## 💻 Ejecutar localmente

```bash
# 1. Clona el repositorio
git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git
cd TU_REPOSITORIO

# 2. Crea un entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 3. Instala las dependencias
pip install -r requirements.txt

# 4. Ejecuta la app
streamlit run app.py
```

La app abrirá automáticamente en `http://localhost:8501`.

---

## 🔄 Actualizar los datos

Para actualizar el dashboard con nuevos datos:

1. Modifica el archivo `Plan_de_ensayos_2026.xlsx` en la hoja **Ensayos** manteniendo las columnas: `ETAPA`, `MATERIAL`, `ENSAYO`, `NTC`, `FRECUENCIA`, `Proyecto`, `Mes`, `Cantidad`.
2. Sube el archivo actualizado al repositorio de GitHub.
3. Streamlit Cloud detectará el cambio y recargará automáticamente (o usa el botón **"Rerun"** en la app).

---

## ⚙️ Requisitos técnicos

- Python 3.9 o superior
- Las dependencias se gestionan automáticamente con `requirements.txt`
