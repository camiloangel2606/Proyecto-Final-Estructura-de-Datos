import sys
import os
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

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

# Barra lateral con opciones
opcion = st.sidebar.radio(
    "Selecciona una operación",
    [
        "Visualizar Red", "Agregar Barrio", "Eliminar Barrio", "Agregar Casa", "Agregar Tanque", "Agregar Conexión",
        "Eliminar Casa", "Eliminar Tanque", "Eliminar Conexión", "Simular Obstrucción",
        "Encontrar Rutas Alternativas", "Actualizar Valores", "Cambiar Sentido de Flujo",
        "Identificar Posiciones Óptimas", "Visualizar Historial"
    ]
)

#VISUALIZAR RED:
if opcion == "Visualizar Red":
    st.header("Visualización de la Red")
    try:
        # Llamar a la función que dibuja el grafo
        red.visualizar_red()
    except Exception as e:
        st.error(f"Error al visualizar la red: {e}")

#AGREGAR BARRIO:
elif opcion == "Agregar Barrio":
    st.subheader("Agregar Barrio")
    barrio = st.text_input("Nombre del nuevo Barrio")
    color = st.color_picker("Selecciona el color del barrio", value="#FFFFFF")
    if st.button("Agregar Barrio"):
        try:
            red.agregar_barrio(barrio, color)
            st.write("Barrios después de agregar:", red.barrios_permitidos)  # Debugging
            red.guardar_a_json(archivo_json)
            
            # Registrar el cambio en el historial
            red.registrar_historial(f"Se agregó el barrio: {barrio} con color {color}.")
            st.success(f"Barrio '{barrio}' agregado exitosamente con el color '{color}'.")
        except Exception as e:
            st.error(f"Error al agregar el barrio: {e}")

#ELIMINAR BARRIO:
elif opcion == "Eliminar Barrio":
    st.subheader("Eliminar Barrio")
    barrios = list(red.barrios_permitidos.keys())
    if barrios:
        barrio = st.selectbox("Selecciona el barrio a eliminar", barrios)
        if st.button("Eliminar Barrio"):
            try:
                red.eliminar_barrio(barrio)
                red.guardar_a_json(archivo_json)
                
                # Registrar el cambio en el historial
                red.registrar_historial(f"Se elimino el barrio: {barrio}.")
                st.success(f"Barrio '{barrio}' eliminado exitosamente.")
            except Exception as e:
                st.error(f"Error al eliminar el barrio: {e}")
    else:
        st.info("No hay barrios registrados.")

#AGREGAR CASA:
elif opcion == "Agregar Casa":
    st.subheader("Agregar Casa")
    nombre = st.text_input("Nombre de la Casa")
    demanda = st.number_input("Demanda", min_value=1, step=1)
    barrios = list(red.barrios_permitidos.keys())
    if barrios:
        barrio = st.selectbox("Barrio", barrios)
        if st.button("Agregar Casa"):
            # Verificar si la casa ya existe antes de agregarla
            if nombre in red.casa:  # Asumo que red.casas es el lugar donde almacenas las casas
                st.error(f"Error: La casa '{nombre}' ya existe en la red.")
            else:
                try:
                    # Intentar agregar la casa
                    red.agregar_casa(nombre, demanda, barrio)
                    red.guardar_a_json(archivo_json)
                    
                    # Registrar el cambio en el historial
                    cambio = {
                        "fecha": "2024-12-12T11:30:00",  # Puedes obtener la fecha actual aquí
                        "evento": "Casa agregada",
                        "detalles": {
                            "casa": nombre,
                            "demanda": demanda,
                            "barrio": barrio
                        }
                    }
                    red.registrar_historial(cambio)  # Guardar en el historial
                    st.success("Casa agregada exitosamente.")
                except Exception as e:
                    st.error(f"Error al agregar la casa: {e}")
    else:
        st.error("No hay barrios disponibles. Agrega uno primero.")

#AGREGAR TANQUE:
elif opcion == "Agregar Tanque":
    st.subheader("Agregar Tanque")
    id_tanque = st.text_input("ID del Tanque")
    capacidad = st.number_input("Capacidad", min_value=1, step=1)
    nivel_actual = st.number_input("Nivel Actual", min_value=0, step=1)
    barrio = st.selectbox("Barrio", list(red.barrios_permitidos.keys()))
    if st.button("Agregar Tanque"):
        try:
            if id_tanque in red.tanques:
                st.error(f"Error: El tanque '{id_tanque}' ya existe en la red.")
            else:
                red.agregar_tanque(id_tanque, capacidad, nivel_actual, barrio)
                red.guardar_a_json(archivo_json)
                
                # Registrar el cambio en el historial
                red.registrar_historial(f"Se agregó el tanque: {id_tanque} en el barrio: {barrio}, con demanda: {capacidad}.")
                st.success("Tanque agregado exitosamente.")
        except Exception as e:
            st.error(f"Error al agregar el tanque: {e}")

#AGREGAR CONEXIÓN:
elif opcion == "Agregar Conexión":
    st.subheader("Agregar Conexión")
    try:
        red.cargar_desde_json('data/red_acueducto.json')
        # Solicitar datos
        origen = st.text_input("Ingresa el nodo de origen (Tanque o Casa):").strip()
        destino = st.text_input(
            "Ingresa el nodo de destino (Casa o Tanque). Tenga en cuenta que:\n"
            "Para Casa: Casa a Casa,\nPara Tanque: Tanque a Casa, Tanque a Tanque."
        ).strip()
        capacidad = st.number_input("Ingresa la capacidad de la conexión:", min_value=1, step=1)
        if st.button("Agregar Conexión"):
            if not origen or not destino:
                st.error("Error: El origen y el destino no pueden estar vacíos.")
            elif origen not in red.nodos or destino not in red.nodos:
                st.error("Error: Uno o ambos nodos no existen en la red.")
            else:
                # Validar que el nodo origen tenga suficiente capacidad o excedente
                capacidad_disponible = 0
                if origen in red.tanques:  # Validar capacidad del tanque
                    tanque = red.tanques[origen]
                    capacidad_disponible = tanque.nivel_actual - sum(
                        conexion.capacidad for conexion in red.conexiones if conexion.origen == origen
                    )
                elif origen in red.casa:  # Validar excedente de la casa
                    suministro_total = sum(
                        conexion.capacidad for conexion in red.conexiones if conexion.destino == origen
                    )
                    demanda_total = red.casa[origen].demanda
                    capacidad_disponible = max(suministro_total - demanda_total, 0)
                if capacidad > capacidad_disponible:
                    st.error(
                        f"Error: El nodo origen '{origen}' no tiene suficiente capacidad disponible. "
                        f"Capacidad disponible: {capacidad_disponible:.1f}, Capacidad requerida: {capacidad:.1f}."
                    )
                else:
                    try:
                        # Intentar agregar la conexión
                        red.agregar_conexion(origen, destino, capacidad)
                        # Guardar la red
                        red.guardar_a_json('data/red_acueducto.json')
                        
                        # Registrar el cambio en el historial
                        red.registrar_historial(f"Se agregó la conexión: {origen} con destino: {destino} y capacidad de: {capacidad}.")
                        st.success(f"Conexión agregada exitosamente entre {origen} y {destino} con capacidad {capacidad}.")
                        # Visualizar la red
                        red.cargar_desde_json('data/red_acueducto.json')
                        red.visualizar_red()
                    except Exception as e:
                        st.error(f"Error al agregar la conexión: {e}")
    except Exception as e:
        st.error(f"Error inesperado: {e}")

# ELIMINAR CASA:
elif opcion == "Eliminar Casa":
    st.subheader("Eliminar Casa")
    nombre_casa = st.text_input("Nombre de la Casa a eliminar")
    if st.button("Eliminar Casa"):
        try:
            if nombre_casa not in red.nodos:
                st.error(f"La casa con el identificador {nombre_casa} no existe en la red.")
            else:
                red.eliminar_casa(nombre_casa)
                red.guardar_a_json(archivo_json)
                
                # Registrar el cambio en el historial
                red.registrar_historial(f"Se eliminó la casa: {nombre_casa}.")
                st.success("Casa eliminada exitosamente.")
        except Exception as e:
            st.error(f"Error al eliminar la casa: {e}")

# ELIMINAR TANQUE:
elif opcion == "Eliminar Tanque":
    st.subheader("Eliminar Tanque")
    id_tanque = st.text_input("ID del Tanque a eliminar")
    if st.button("Eliminar Tanque"):
        try:
            if id_tanque not in red.nodos:
                st.error(f"El tanque con el identificador {id_tanque} no existe en la red.")
            else:
                red.eliminar_tanque(id_tanque)
                red.guardar_a_json(archivo_json)
                
                # Registrar el cambio en el historial
                red.registrar_historial(f"Se eliminó el tanque: {id_tanque}.")
                st.success("Tanque eliminado exitosamente.")
        except Exception as e:
            st.error(f"Error al eliminar el tanque: {e}")

# ELIMINAR CONEXIÓN:
elif opcion == "Eliminar Conexión":
    st.subheader("Eliminar Conexión")
    origen = st.text_input("Casa/Tanque Origen")
    destino = st.text_input("Casa/Tanque Destino")
    if st.button("Eliminar Conexión"):
        try:
            # Verificar si la conexión existe
            if not any(conexion.origen == origen and conexion.destino == destino for conexion in red.conexiones):
                st.error(f"La conexión entre {origen} y {destino} no existe en la red.")
            else:
                red.eliminar_conexion(origen, destino)
                red.guardar_a_json(archivo_json)
                
                # Registrar el cambio en el historial
                red.registrar_historial(f"Se eliminó la conexión con origen: {origen} con destino: {destino}.")
                st.success("Conexión eliminada exitosamente.")
        except Exception as e:
            st.error(f"Error al eliminar la conexión: {e}")

#SIMULAR OBSTRUCCIÓN:
# Dentro de la sección de Streamlit en app.py:
elif opcion == "Simular Obstrucción":
    st.subheader("Simular Obstrucción")
    try:
        # Solicitar los valores de entrada a través de Streamlit (en lugar de input())
        origen = st.text_input("Ingrese el nodo de origen de la conexión:")
        destino = st.text_input("Ingrese el nodo de destino de la conexión:")
        nivel_gravedad = st.number_input("Ingrese el nivel de gravedad (0 a 100):", min_value=0.0, max_value=100.0, value=0.0)
        # Solo ejecutar la simulación si el botón es presionado
        if st.button("Simular Obstrucción"):
            if not origen or not destino:
                st.error("Por favor ingrese ambos nodos: origen y destino.")
            elif nivel_gravedad == 0:
                st.error("Por favor ingrese un nivel de gravedad mayor que 0.")
            else:
                # Llamar a la función de simulación con los valores proporcionados
                red.simular_obstruccion(origen, destino, nivel_gravedad / 100)  # Convertir a porcentaje
                red.guardar_a_json('data/red_acueducto.json')
                
                # Registrar el cambio en el historial
                red.registrar_historial(f"Se agregó la obstrucción con origen: {origen}, destino: {destino} y nivel de gravedad: {nivel_gravedad}%.")
                red.cargar_desde_json('data/red_acueducto.json')
                red.visualizar_red()  # Mostrar la red después de la simulación
                st.success("Obstrucción simulada correctamente.")
    except Exception as e:
        st.error(f"Error al simular la obstrucción: {e}")

# ENCONTRAR RUTAS ALTERNATIVAS:
elif opcion == "Encontrar Rutas Alternativas":
    st.subheader("Encontrar Rutas Alternativas")
    try:
        # Solicitar casas afectadas
        casas_afectadas_input = st.text_input(
            "Ingresa las casas afectadas por obstrucciones (separadas por comas):"
        ).strip()
        # Procesar solo si hay entrada
        if casas_afectadas_input:
            casas_afectadas = casas_afectadas_input.split(',')
            casas_afectadas = [casa.strip() for casa in casas_afectadas if casa.strip()]
            if not casas_afectadas:
                st.error("No se ingresaron casas afectadas.")
            else:
                # Solicitar obstrucciones
                obstrucciones_input = st.text_input(
                    "Ingresa una obstrucción en formato 'origen,destino' (deja vacío para terminar):"
                ).strip()
                obstrucciones = []
                while obstrucciones_input:
                    try:
                        origen, destino = obstrucciones_input.split(',')
                        origen, destino = origen.strip(), destino.strip()
                        if origen and destino:
                            obstrucciones.append((origen, destino))
                        else:
                            st.error("Ambos nodos, origen y destino, deben ser válidos.")
                        obstrucciones_input = st.text_input(
                            "Ingresa otra obstrucción o deja vacío para terminar:"
                        ).strip()
                    except ValueError:
                        st.error("Formato inválido. Usa 'origen,destino'.")
                        break
                if obstrucciones:
                    # Aplicar obstrucciones en el grafo
                    red.aplicar_obstrucciones(obstrucciones)
                    # Calcular y visualizar rutas alternativas
                    red.calcular_y_visualizar_rutas(casas_afectadas)
                    st.success("Rutas alternativas calculadas y visualizadas correctamente.")
                else:
                    st.error("No se ingresaron obstrucciones.")
    except Exception as e:
        st.error(f"Error al encontrar rutas alternativas: {e}")

# ACTUALIZAR VALORES:
elif opcion == "Actualizar Valores":
    st.subheader("Actualizar Valores")
    try:
        # Solicitar tipo y identificador
        tipo = st.selectbox("Selecciona el tipo de actualización", ["Casa", "Tanque", "Conexion"])
        # Solicitar identificador dependiendo del tipo
        if tipo == "Conexion":
            origen = st.text_input("Ingresa el nodo de origen de la conexión:").strip()
            destino = st.text_input("Ingresa el nodo de destino de la conexión:").strip()
            identificador = (origen, destino)
        else:
            identificador = st.text_input(f"Ingresa el identificador del {tipo} que deseas actualizar:").strip()
        nuevos_valores_raw = st.text_input(f"Ingresa los nuevos valores para el {tipo} (por ejemplo: clave1=valor1,clave2=valor2):").strip()
        if st.button("Actualizar"):
            if not identificador:
                st.error(f"Por favor, ingresa un identificador válido para el {tipo}.")
            elif not nuevos_valores_raw:
                st.error("Por favor, ingresa los nuevos valores para la actualización.")
            else:
                nuevos_valores = {}
                try:
                    for item in nuevos_valores_raw.split(","):
                        clave, valor = item.split("=")
                        clave, valor = clave.strip(), valor.strip()
                        if valor.isdigit():
                            valor = int(valor)
                        elif valor.replace('.', '', 1).isdigit():
                            valor = float(valor)
                        nuevos_valores[clave] = valor
                except ValueError as e:
                    st.error(f"Error en el formato de entrada: {e}. Revisa tu formato de clave=valor.")
                # Intentar actualizar los valores en la red
                if red.actualizar_valores(tipo, identificador, **nuevos_valores):
                    red.guardar_a_json('data/red_acueducto.json')
                    
                    # Registrar el cambio en el historial
                    red.registrar_historial(f"Se actualizó el valor de: {identificador} con los valores: {nuevos_valores}.")
                    st.success("Cambios guardados correctamente.")
                else:
                    st.error("No se pudo realizar la actualización. Verifica el identificador y los valores.")
    except Exception as e:
        st.error(f"Error al actualizar valores: {e}")

# CAMBIAR SENTIDO DE FLUJO:
elif opcion == "Cambiar Sentido de Flujo":
    st.subheader("Cambiar Sentido de Flujo")
    try:
        # Solicitar origen, destino y capacidad
        origen = st.text_input("Ingresa el nodo origen al que cambiar el flujo:")
        destino = st.text_input("Ingresa el nodo destino al que cambiar el flujo:")
        capacidad = st.number_input("Ingresa la capacidad que deseas revertir:", min_value=0.0, step=1.0)
        # Validar solo cuando se han ingresado todos los datos
        if origen and destino and capacidad > 0:
            if origen not in red.nodos or destino not in red.nodos:
                st.error("Error: Uno o ambos nodos no existen en la red.")
            else:
                # Intentar cambiar el sentido del flujo
                resultado = red.cambiar_sentido_flujo(origen, destino, capacidad)
                if "Error" not in resultado:
                    red.recalcular_flujo()
                    red.guardar_a_json('data/red_acueducto.json')
                    
                    # Registrar el cambio en el historial
                    red.registrar_historial(f"Se cambió el flujo con origen: {origen}, destino: {destino} y capacidad: {capacidad}.")
                    st.success("Los cambios en la red han sido guardados exitosamente.")
                else:
                    st.error(f"Error al cambiar el sentido del flujo: {resultado}")
        elif origen or destino or capacidad > 0:
            st.warning("Debes proporcionar todos los datos correctamente.")
    except Exception as e:
        st.error(f"Ha ocurrido un error al cambiar el sentido del flujo: {e}")

# IDENTIFICAR POSICIONES ÓPTIMAS PARA TANQUES:
elif opcion == "Identificar Posiciones Óptimas":
    
    # Transformar casas
    red.casa = [
        {"nombre": nombre, **vars(casa)}
        for nombre, casa in red.casa.items()
    ]
    # Transformar tanques
    red.tanques = [
        {"id": tanque_id, **vars(tanque)}
        for tanque_id, tanque in red.tanques.items()
    ]
    # Transformar conexiones
    red.conexiones = [
        {"origen": conexion.origen, "destino": conexion.destino, "capacidad": conexion.capacidad}
        for conexion in red.conexiones
    ]
    st.subheader("Identificar Posiciones Óptimas para Nuevos Tanques")
    if not isinstance(red.casa, list) or not all(isinstance(c, dict) for c in red.casa):
        st.error("El formato de 'casas' no es válido.")
        st.write("Casas actuales:", red.casa)
        st.stop()
    if not isinstance(red.tanques, list) or not all(isinstance(t, dict) for t in red.tanques):
        st.error("El formato de 'tanques' no es válido.")
        st.write("Tanques actuales:", red.tanques)
        st.stop()
    if not isinstance(red.conexiones, list) or not all(isinstance(c, dict) for c in red.conexiones):
        st.error("El formato de 'conexiones' no es válido.")
        st.write("Conexiones actuales:", red.conexiones)
        st.stop()
    if not isinstance(red.barrios_permitidos, dict):
        st.error("El formato de 'barrios_permitidos' no es válido.")
        st.write("Barrios permitidos actuales:", red.barrios_permitidos)
        st.stop()
    try:
        umbral_demanda = st.number_input(
            "Ingresa el umbral mínimo de demanda para sugerir nuevos tanques:",
            min_value=0.0,
            value=50.0,
            step=1.0,
        )
        
        barrios_disponibles = list(red.barrios_permitidos.keys())
        st.write("Barrios permitidos:")
        for barrio, color in red.barrios_permitidos.items():
            st.markdown(f"- **{barrio}**: {color}")
        if st.button("Identificar Posiciones"):
            st.write("Validando datos...")
            # Validar estructura de datos
            if not all([
                isinstance(red.casa, list),
                isinstance(red.tanques, list),
                isinstance(red.conexiones, list),
                isinstance(red.barrios_permitidos, dict)
            ]):
                st.error("Los datos de la red no tienen el formato esperado.")
                st.stop()
            sugerencias = red.identificar_posiciones_optimas(
                red.casa,
                red.tanques,
                red.conexiones,
                red.barrios_permitidos,
                umbral_demanda=umbral_demanda,
            )
            if sugerencias:
                st.success("Se han identificado posiciones óptimas para nuevos tanques:")
                for sugerencia in sugerencias:
                    st.markdown(
                        f"""
                        - **Barrio:** {sugerencia['barrio']}
                        - **Posición Central:** {sugerencia['posicion_central']}
                        - **Demanda Total:** {sugerencia['demanda']}
                        - **Color del Barrio:** {sugerencia['color']}
                        """
                    )
            else:
                st.warning("No se encontraron posiciones óptimas basadas en los parámetros actuales.")
    except Exception as e:
        st.error(f"Ha ocurrido un error al identificar posiciones óptimas: {e}")

# VISUALIZAR HISTORIAL:
elif opcion == "Visualizar Historial":
    st.subheader("Visualizar Historial")
    # Llamar a la función mostrar_historial
    resultado = red.mostrar_historial()
    
    # Verificar si es un mensaje de error o el historial
    if isinstance(resultado, str):  # Es un mensaje de error o advertencia
        st.warning(resultado)
    else:  # Es el historial como lista
        if not resultado:
            st.info("El historial está vacío.")
        else:
            st.success("Historial de cambios:")
            st.text(resultado)  # Muestra el resultado en la interfaz

# GUARDAR CAMBIOS
if st.sidebar.button("Guardar Cambios"):
    try:
        red.guardar_a_json(archivo_json)
        st.success("Cambios guardados exitosamente.")
    except Exception as e:
        st.error(f"Error al guardar los cambios: {e}")