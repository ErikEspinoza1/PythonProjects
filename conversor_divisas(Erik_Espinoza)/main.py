import streamlit as st
# Importamos tus funciones del archivo datos.py
from datos import obtener_datos_bce, calcular_conversion

# Configuración de la página
st.set_page_config(page_title="Conversor Divisas BCE", layout="centered")

# Título y descripción [cite: 85, 86]
st.title("Conversor de Divisas (BCE)")
st.markdown("Esta aplicación consume XML en tiempo real del **Banco Central Europeo**.")
@st.cache_data
def cargar_datos():
    return obtener_datos_bce()

fecha_actual, tasas = cargar_datos()

# Verificamos si la descarga funcionó
if tasas:
    st.success(f"Datos cargados correctamente. Fecha oficial: {fecha_actual}")
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        cantidad = st.number_input("Cantidad", min_value=0.0, value=100.00, step=10.0)
    lista_monedas = list(tasas.keys())
    with col2:
        moneda_origen = st.selectbox("De:", lista_monedas, index=lista_monedas.index("EUR"))

    with col3:

        index_usd = lista_monedas.index("USD") if "USD" in lista_monedas else 0
        moneda_destino = st.selectbox("A:", lista_monedas, index=index_usd)

    if st.button("Calcular Conversión"):
        resultado = calcular_conversion(cantidad, moneda_origen, moneda_destino, tasas)
        if resultado is not None:
            st.metric(label=f"Valor en {moneda_destino}", value=f"{resultado:.2f} {moneda_destino}")

            tasa_individual = calcular_conversion(1, moneda_origen, moneda_destino, tasas)
            st.caption(f"ℹTipo de cambio aplicado: 1 {moneda_origen} = {tasa_individual:.4f} {moneda_destino}")
        else:
            st.error("Error al realizar el cálculo.")
            
    # Opcional: Mostrar tabla de datos en bruto (Raw Data)
    with st.expander("Ver Estructura XML recibida (Raw Data)"):
        st.write(tasas)

else:
    st.error("No se pudieron cargar los datos del BCE. Verifica tu conexión a internet.")