import sys
import os
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

# Asegúrate de que la ruta de la carpeta Src esté incluida
sys.path.append(os.path.join(os.path.dirname(__file__), 'Src'))

from Src.utils import RedDeAcueducto

#EJECUTAR LA INTERFAZ: streamlit run app.py
# Instanciar la red
red = RedDeAcueducto()

# Configuración de la aplicación
st.set_page_config(page_title="Gestión de Red de Acueductos", layout="wide")

# Cargar la red desde JSON
archivo_json = 'data/red_acueducto.json'
try:
    red.cargar_desde_json(archivo_json)
except FileNotFoundError:
    st.error(f"El archivo {archivo_json} no se encontró.")
except Exception as e:
    st.error(f"Error al cargar la red: {e}")

# Título de la aplicación
st.title("Sistema de Gestión de Red de Acueductos")

# Visualizar la red
st.header("Visualización de la Red")
try:
    fig, ax = plt.subplots()
    G = red.construir_grafo()
    pos = nx.spring_layout(G)
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=500,
        node_color="lightblue",
        edge_color="gray",
        font_size=10,
        font_color="black",
        ax=ax
    )
    st.pyplot(fig)
except Exception as e:
    st.error(f"Error al visualizar la red: {e}")

# Título de la aplicación
st.title("Sistema de Gestión de Red de Acueductos")

# Barra lateral con opciones
opcion = st.sidebar.radio(
    "Selecciona una operación",
    ["Visualizar Red", "Agregar Casa", "Agregar Tanque", "Agregar Conexión", "Eliminar Casa", "Eliminar Tanque", "Eliminar Conexión"]
)

# Función para visualizar la red
if opcion == "Visualizar Red":
    st.header("Visualización de la Red")
    try:
        # Llamar a la función que dibuja el grafo
        red.visualizar_red()
    except Exception as e:
        st.error(f"Error al visualizar la red: {e}")

if opcion == "Agregar Casa":
    st.subheader("Agregar Casa")
    nombre = st.text_input("Nombre de la Casa")
    demanda = st.number_input("Demanda", min_value=1, step=1)
    barrio = st.selectbox("Barrio", list(red.barrios_permitidos.keys()))
    if st.button("Agregar Casa"):
        try:
            red.agregar_casa(nombre, demanda, barrio)
            red.guardar_a_json(archivo_json)
            st.success("Casa agregada exitosamente.")
        except Exception as e:
            st.error(f"Error al agregar la casa: {e}")

elif opcion == "Agregar Tanque":
    st.subheader("Agregar Tanque")
    id_tanque = st.text_input("ID del Tanque")
    capacidad = st.number_input("Capacidad", min_value=1, step=1)
    nivel_actual = st.number_input("Nivel Actual", min_value=0, step=1)
    barrio = st.selectbox("Barrio", list(red.barrios_permitidos.keys()))
    if st.button("Agregar Tanque"):
        try:
            red.agregar_tanque(id_tanque, capacidad, nivel_actual, barrio)
            red.guardar_a_json(archivo_json)
            st.success("Tanque agregado exitosamente.")
        except Exception as e:
            st.error(f"Error al agregar el tanque: {e}")

elif opcion == "Agregar Conexión":
    st.subheader("Agregar Conexión")
    origen = st.text_input("Casa/Tanque Origen")
    destino = st.text_input("Casa/Tanque Destino")
    tipo_conexion = st.selectbox("Tipo de Conexión", ["Casa a Casa", "Casa a Tanque", "Tanque a Casa", "Tanque a Tanque"])
    
    if st.button("Agregar Conexión"):
        try:
            if tipo_conexion == "Casa a Casa":
                red.agregar_conexion(origen, destino)
            elif tipo_conexion == "Casa a Tanque":
                red.agregar_conexion_casa_tanque(origen, destino)
            elif tipo_conexion == "Tanque a Casa":
                red.agregar_conexion_tanque_casa(origen, destino)
            elif tipo_conexion == "Tanque a Tanque":
                red.agregar_conexion_tanque_tanque(origen, destino)
            red.guardar_a_json(archivo_json)
            st.success("Conexión agregada exitosamente.")
        except Exception as e:
            st.error(f"Error al agregar la conexión: {e}")

elif opcion == "Eliminar Casa":
    st.subheader("Eliminar Casa")
    nombre_casa = st.text_input("Nombre de la Casa a eliminar")
    if st.button("Eliminar Casa"):
        try:
            red.eliminar_casa(nombre_casa)
            red.guardar_a_json(archivo_json)
            st.success("Casa eliminada exitosamente.")
        except Exception as e:
            st.error(f"Error al eliminar la casa: {e}")

elif opcion == "Eliminar Tanque":
    st.subheader("Eliminar Tanque")
    id_tanque = st.text_input("ID del Tanque a eliminar")
    if st.button("Eliminar Tanque"):
        try:
            red.eliminar_tanque(id_tanque)
            red.guardar_a_json(archivo_json)
            st.success("Tanque eliminado exitosamente.")
        except Exception as e:
            st.error(f"Error al eliminar el tanque: {e}")

elif opcion == "Eliminar Conexión":
    st.subheader("Eliminar Conexión")
    origen = st.text_input("Casa/Tanque Origen")
    destino = st.text_input("Casa/Tanque Destino")
    if st.button("Eliminar Conexión"):
        try:
            red.eliminar_conexion(origen, destino)
            red.guardar_a_json(archivo_json)
            st.success("Conexión eliminada exitosamente.")
        except Exception as e:
            st.error(f"Error al eliminar la conexión: {e}")

# Guardar cambios
if st.sidebar.button("Guardar Cambios"):
    try:
        red.guardar_a_json(archivo_json)
        st.success("Cambios guardados exitosamente.")
    except Exception as e:
        st.error(f"Error al guardar los cambios: {e}")
