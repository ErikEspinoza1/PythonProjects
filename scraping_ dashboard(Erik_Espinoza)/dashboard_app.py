import streamlit as st
import pandas as pd
import altair as alt

CSV_FILE = 'datos_libros_scraping.csv'

st.set_page_config(
    page_title="Dashboard Básico de Libros",
    layout="wide",
    initial_sidebar_state="expanded" 
)

@st.cache_data
def load_data(file_path):
    """Carga los datos del archivo CSV."""
    try:
        df = pd.read_csv(file_path)
        df['Categoria'] = df['Titulo'].apply(lambda x: 'Ficción' if 'a' in x.lower() else 'No Ficción')
        return df
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo de datos '{file_path}'. Asegúrate de ejecutar 'scraper.py' primero.")
        return pd.DataFrame() 

df_original = load_data(CSV_FILE)

if df_original.empty:
    st.stop()
df = df_original.copy()

# --- Título y Layout Principal ---
st.title("Análisis Básico de Libros")
st.markdown("Dashboard creado a partir de datos extraídos con Web Scraping.")
st.markdown("Enlace: [Books to Scrape](http://books.toscrape.com/)")
st.markdown("---")

st.sidebar.header(" Opciones de Filtrado")

# Filtro 1: Categoría
categorias = df['Categoria'].unique()
categoria_seleccionada = st.sidebar.multiselect(
    'Filtrar por Categoría',
    options=categorias,
    default=categorias
)

# Filtro 2: Rango de Precios
min_price = df['Precio_GBP'].min()
max_price = df['Precio_GBP'].max()
rango_precio = st.sidebar.slider(
    'Rango de Precios (£)',
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price),
    step=0.1
)

# Filtro 3: Puntuación Mínima
rating_minimo = st.sidebar.slider(
    'Puntuación Mínima (Estrellas)',
    min_value=0,
    max_value=5,
    value=1,
    step=1
)


# --- 2. Aplicación de Filtros ---
df_filtrado = df[
    (df['Categoria'].isin(categoria_seleccionada)) &
    (df['Precio_GBP'] >= rango_precio[0]) &
    (df['Precio_GBP'] <= rango_precio[1]) &
    (df['Rating_Estrellas'] >= rating_minimo)
]

total_libros = len(df_filtrado)

# Cálculo de métricas
precio_promedio = df_filtrado['Precio_GBP'].mean() if total_libros > 0 else 0
rating_promedio = df_filtrado['Rating_Estrellas'].mean() if total_libros > 0 else 0

# Mostrar métricas en tres columnas
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

with col_kpi1:
    st.metric(label="Total de Libros Encontrados", value=total_libros)

with col_kpi2:
    st.metric(label="Precio Promedio (£)", value=f"£{precio_promedio:.2f}")

with col_kpi3:
    st.metric(label="Rating Promedio (Estrellas)", value=f"{rating_promedio:.2f}")

st.markdown("---")
st.subheader(f"Resultados Filtrados ({total_libros} libros en visualización)")


# --- 3. Visualización Básica (Gráficos) ---

col_graph1, col_graph2 = st.columns(2)

with col_graph1:
    st.markdown("#### Distribución de Puntuaciones")
    chart_rating = alt.Chart(df_filtrado).mark_bar().encode(
        x=alt.X('Rating_Estrellas:O', title='Puntuación (Estrellas)'),
        y=alt.Y('count():Q', title='Número de Libros'),
        tooltip=['Rating_Estrellas', 'count()'],
        color=alt.Color('Rating_Estrellas:O', scale=alt.Scale(scheme='tableau10')) 
    ).properties(
        title='Frecuencia de Ratings'
    ).interactive() 
    st.altair_chart(chart_rating, use_container_width=True)


with col_graph2:
    st.markdown("#### Distribución de Precios (Relación interesante)")
    chart_precio = alt.Chart(df_filtrado).mark_bar().encode(
        x=alt.X('Precio_GBP:Q', bin=True, title='Precio (£)'),
        y=alt.Y('count():Q', title='Número de Libros'),
        tooltip=[alt.Tooltip('Precio_GBP', bin=True), 'count()']
    ).properties(
        title='Histograma de Precios'
    ).interactive()
    st.altair_chart(chart_precio, use_container_width=True)


# --- 4. Tabla de Datos Filtrados ---
st.markdown("---")
st.subheader(" Detalle de Libros")
columnas_tabla = ['Titulo', 'Precio_GBP', 'Rating_Estrellas', 'Disponibilidad', 'Categoria']
st.dataframe(df_filtrado[columnas_tabla], use_container_width=True)

st.markdown("---")
st.caption(f"Total de registros cargados: {len(df_original)}")
