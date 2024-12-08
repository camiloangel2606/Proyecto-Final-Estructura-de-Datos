import networkx as nx
import json
import matplotlib.pyplot as plt
from utils import RedDeAcueducto
red = RedDeAcueducto()

def main():
    red = RedDeAcueducto()
    red.cargar_desde_json('data/red_acueducto.json')
    
    # Crear el grafo
    G = nx.DiGraph()
    for conexion in red.conexiones:
        G.add_edge(conexion.origen, conexion.destino, capacity=conexion.capacidad)
    
    # Mostrar información básica
    print("Nodos:", G.nodes)
    print("Conexiones:", G.edges(data=True))
    # Simular un flujo máximo
    flujo_max, flujo_rutas = nx.maximum_flow(G, "Tanque1", "Barrio1")
    print(f"Flujo máximo de Tanque1 a Barrio1: {flujo_max}")
    print("Rutas:", flujo_rutas)

def menu():
    red.cargar_desde_json('data/red_acueducto.json')
    #red.visualizar_red()
    #Menú
    i = 1
    opciones = {#Opciones de funciones que se tendrán en el menú
        0: salir,
        1: agregar_casa,
        2: agregar_tanque,
        3: agregar_conexion,
        4: eliminar_casa,
        5: eliminar_tanque,
        6: eliminar_conexion,
        7: simular_obstruccion,
        8: calcular_y_visualizar,
        9: actualizar_valores,
        10: cambiar_sentido_flujo,
        11: identificar_posiciones_optimas_interactivo,
    }
    
    while i != 0:
        print("BIENVENIDO AL MENÚ DE OPERACIÓN DEL ACUEDUCTO")
        print("Ingresa la operación a realizar")
        print("Agregar: (1) Casa, (2) Tanque, (3) Conexión. Al acueducto")
        print("Eliminar: (4) Casa, (5) Tanque, (6) Conexión. Al acueducto")
        print("(7) Simular_obstrucción, (8) Encontrar rutas alternativas,(9) Actualizar valores (Casa, Tanque, Conexión).")
        print("(10) Cambiar dirección de flujo, (11) Identificar posiciones optimas.")
        print("(0) Salir del menú")
        
        #Validar la entrada del usuario
        try:
            i = int(input("Selecciona una opción:"))
        except ValueError:
            print("Opción no válida. Por favor, ingrese un número.")
            continue
        
        #Ejecutar la función correspondiente  a la opción seleccionada
        if i in opciones:
            opciones[i]() #LLamar  a la función asociada a la opción
        else:
            print("Opción no válida.")

#Definimos todas las opciones presentadas en el menú para así solo llamarlas al momento de ejecutar.
def salir():
    print("Guardando actualizaciones...")
    red.cargar_desde_json('data/red_acueducto.json')
    red.visualizar_red()
    print("Gracias por usar la interfaz de acueductos.")

#AGREGAR BARRIO:
def agregar_barrio():
    print("Ingresa la información del nuevo barrio.")
    
    try:
        # Solicitar el nombre del barrio
        barrio = input("Ingresa el nombre del barrio: ").strip()
        if not barrio:
            print("Error: El nombre del barrio no puede estar vacío.")
            return
        
        # Solicitar el color asociado al barrio
        color = input("Ingresa el color asociado al barrio: ").strip()
        if not color:
            print("Error: El color no puede estar vacío.")
            return
        
        # Intentar agregar el barrio con su color
        red.agregar_barrio(barrio, color)
        
        # Guardar cambios en el archivo JSON
        red.guardar_a_json('data/red_acueducto.json')
        red.cargar_desde_json('data/red_acueducto.json')
        red.visualizar_red()
    except Exception as e:
        print(f"Error inesperado: {e}")

#ELIMINAR BARRIO:
def eliminar_barrio():
    print("Eliminar un barrio.")
    
    try:
        # Mostrar los barrios disponibles
        print(f"Barrios disponibles: {', '.join(red.barrios_permitidos.keys())}")
        
        # Solicitar el nombre del barrio a eliminar
        barrio = input("Ingresa el nombre del barrio que deseas eliminar: ").strip()
        if not barrio:
            print("Error: El nombre del barrio no puede estar vacío.")
            return
        
        # Verificar si el barrio existe antes de eliminarlo
        if barrio not in red.barrios_permitidos:
            print(f"Error: El barrio '{barrio}' no existe.")
            return
        
        # Intentar eliminar el barrio
        red.eliminar_barrio(barrio)
        
        # Guardar cambios en el archivo JSON
        red.guardar_a_json('data/red_acueducto.json')
        red.cargar_desde_json('data/red_acueducto.json')
        red.visualizar_red()
    except Exception as e:
        print(f"Error inesperado: {e}")

def agregar_casa():
    print("Ingresa la información de la casa.")
    
    try:
        nombre = input("Ingresa el nombre de la casa: ").strip()
        if not nombre:
            print("Error: El nombre de la casa no puede estar vacío.")
            return
        
        demanda = input("Ingresa la demanda que tiene la casa: ").strip()
        demanda = int(demanda)
        if demanda <= 0:
            print("Error: La demanda debe ser un número positivo.")
            return
        
        # Consultar barrios permitidos desde la red
        barrio = input(f"Ingresa el barrio de la casa ({', '.join(red.barrios_permitidos)}): ").strip()
        if barrio not in red.barrios_permitidos:
            print(f"Error: El barrio debe ser uno de los siguientes: {', '.join(red.barrios_permitidos)}.")
            return
        
        # Intentar agregar la casa con su barrio
        red.agregar_casa(nombre, demanda, barrio)
        
        # Guardar cambios en el archivo JSON
        red.guardar_a_json('data/red_acueducto.json')
        red.cargar_desde_json('data/red_acueducto.json')
        red.visualizar_red()
    
    except ValueError:
        print("Error: La demanda debe ser un número entero.")
    except Exception as e:
        print(f"Error inesperado: {e}")

#AGREGAR TANQUE:
def agregar_tanque():
    print("Ingresa la información del tanque.")
    try:
        id_tanque = input("Ingresa el ID del tanque: ").strip()
        if not id_tanque:
            print("Error: El ID del tanque no puede estar vacío.")
            return
        
        capacidad = input("Ingresa la capacidad del tanque: ")
        capacidad = int(capacidad)
        if capacidad <= 0:
            print("Error: La capacidad debe ser un número positivo.")
            return
        
        nivel_actual = input("Ingresa el nivel actual del tanque: ")
        nivel_actual = int(nivel_actual)
        if nivel_actual < 0 or nivel_actual > capacidad:
            print("Error: El nivel actual debe estar entre 0 y la capacidad máxima.")
            return
        
        # Consultar barrios permitidos desde la red
        barrio = input(f"Ingresa el barrio de la casa ({', '.join(red.barrios_permitidos)}): ").strip()
        if barrio not in red.barrios_permitidos:
            print(f"Error: El barrio debe ser uno de los siguientes: {', '.join(red.barrios_permitidos)}.")
            return
        
        # Intentar agregar el tanque con su barrio
        red.agregar_tanque(id_tanque, capacidad, nivel_actual,barrio)
        
        #Guardar cambios en el archivo json
        red.guardar_a_json('data/red_acueducto.json')
        red.cargar_desde_json('data/red_acueducto.json')
        red.visualizar_red()
    except ValueError:
        print("Error: La capacidad y el nivel actual deben ser números enteros.")
    except Exception as e:
        print(f"Error inesperado: {e}")

#AGREGAR CONEXIÓN:
def agregar_conexion():
    print("Ingresa la información de la conexión.")
    try:
        origen = input("Ingresa el nodo de origen (Tanque o Casa): ").strip()
        lista = "Para Casa: Casa a Casa,\nPara Tanque: Tanque a Casa, Tanque a Tanque."
        destino = input(f"Ingresa el nodo de destino (Casa o Tanque). Tenga en cuenta que:\n{lista}\n").strip()
        if not origen or not destino:
            print("Error: El origen y el destino no pueden estar vacíos.")
            return
        capacidad = input("Ingresa la capacidad de la conexión: ").strip()
        capacidad = int(capacidad)
        if capacidad <= 0:
            print("Error: La capacidad debe ser un número positivo.")
            return
        # Intentar agregar la conexión a la red
        red.agregar_conexion(origen, destino, capacidad)
        # Guardar y recargar la red para mantener la persistencia
        red.guardar_a_json('data/red_acueducto.json')
        red.cargar_desde_json('data/red_acueducto.json')
        # Visualizar la red
        red.visualizar_red()
    except ValueError:
        print("Error: La capacidad debe ser un número entero.")
    except Exception as e:
        print(f"Error inesperado: {e}")

#ELIMINAR BARRIO:
def eliminar_casa():
    print("Eliminar una casa.")
    try:
        nombre = input("Ingresa el nombre de la casa a eliminar: ").strip()
        if not nombre:
            print("Error: El nombre de la casa no puede estar vacío.")
            return
        
        red.eliminar_casa(nombre)
        red.guardar_a_json('data/red_acueducto.json')
        red.cargar_desde_json('data/red_acueducto.json')
        red.visualizar_red()
    except Exception as e:
        print(f"Error inesperado: {e}")

#ELIMINAR TANQUE:
def eliminar_tanque():
    print("Eliminar un tanque.")
    try:
        id_tanque = input("Ingresa el ID del tanque a eliminar: ").strip()
        if not id_tanque:
            print("Error: El ID del tanque no puede estar vacío.")
            return
        
        red.eliminar_tanque(id_tanque)
        red.guardar_a_json('data/red_acueducto.json')
        red.cargar_desde_json('data/red_acueducto.json')
        red.visualizar_red()
    except Exception as e:
        print(f"Error inesperado: {e}")

#ELIMINAR CONEXIÓN:
def eliminar_conexion():
    print("Eliminar una conexión.")
    try:
        origen = input("Ingresa el nodo de origen de la conexión: ").strip()
        destino = input("Ingresa el nodo de destino de la conexión: ").strip()
        if not origen or not destino:
            print("Error: El origen y el destino no pueden estar vacíos.")
            return
        
        red.eliminar_conexion(origen, destino)
        red.guardar_a_json('data/red_acueducto.json')
        red.cargar_desde_json('data/red_acueducto.json')
        red.visualizar_red()
    except Exception as e:
        print(f"Error inesperado: {e}")

#SIMULAR OBSTRUCCIÓN:
def simular_obstruccion():
    try:
        red.simular_obstruccion()
        red.guardar_a_json('data/red_acueducto.json')
        red.cargar_desde_json('data/red_acueducto.json')
        red.visualizar_red()
    except Exception as e:
        print(f"Error inesperado {e}")

#VISUALIZAR LA RED
def visualizar_red(self):
    import networkx as nx
    import matplotlib.pyplot as plt
    
    G = self.construir_grafo()
    
    # Identificar nodos no conectados
    nodos_no_conectados = self.obtener_nodos_no_conectados()
    
    # Posicionar nodos y configurar colores
    pos = nx.spring_layout(G)  # Layout gráfico
    edge_colors = [data['color'] for _, _, data in G.edges(data=True)]
    
    # Dibujar el grafo principal
    nx.draw(
        G,
        pos,
        with_labels=True,
        edge_color=edge_colors,
        node_color="lightblue",
        node_size=500,
        font_size=10,
        font_color="black"
    )
    
    # Agregar los nodos no conectados al gráfico
    for nodo in nodos_no_conectados:
        pos[nodo] = (0, 0)  # Colocar nodos no conectados en una posición arbitraria
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=[nodo],
            node_color="red",  # Color distintivo para nodos no conectados
            node_size=500
        )
    
    # Agregar leyenda para identificar los nodos no conectados
    plt.legend(
        ['Conectado', 'No Conectado'],
        loc='best',
        markerscale=0.5,
        scatterpoints=1
    )
    plt.title("Visualización de la Red de Acueducto")
    plt.show()

# CALCULAR Y VISUALIZAR
def calcular_y_visualizar():
    archivo_json = 'data/red_acueducto.json'
    try:
        # Cargar la red desde el archivo JSON
        red.cargar_desde_json(archivo_json)
        print("Simulación de rutas alternativas:")
        
        # Solicitar casas afectadas
        casas_afectadas = input(
            "Ingresa las casas afectadas por obstrucciones (separadas por comas): "
        ).strip().split(',')
        casas_afectadas = [casa.strip() for casa in casas_afectadas if casa.strip()]
        
        if not casas_afectadas:
            print("No se ingresaron casas afectadas.")
            return
        
        # Solicitar obstrucciones
        obstrucciones = []
        while True:
            obstruccion = input(
                "Ingresa una obstrucción en formato 'origen,destino' (deja vacío para terminar): "
            ).strip()
            if not obstruccion:
                break
            try:
                origen, destino = obstruccion.split(',')
                origen, destino = origen.strip(), destino.strip()
                if origen and destino:
                    obstrucciones.append((origen, destino))
                else:
                    print("Ambos nodos, origen y destino, deben ser válidos.")
            except ValueError:
                print("Formato inválido. Usa 'origen,destino'.")
        
        if not obstrucciones:
            print("No se ingresaron obstrucciones.")
            return
        
        # Aplicar obstrucciones en el grafo
        red.aplicar_obstrucciones(obstrucciones)
        
        # Calcular y visualizar rutas alternativas
        red.calcular_y_visualizar_rutas(casas_afectadas)
        
        # Guardar los cambios en el archivo JSON
        red.guardar_a_json(archivo_json)
        print("Cambios guardados correctamente.")
        
    except FileNotFoundError:
        print(f"El archivo '{archivo_json}' no se encontró.")
    except json.JSONDecodeError:
        print(f"Error al leer el archivo JSON '{archivo_json}'. Verifica su formato.")
    except Exception as e:
        print(f"Error inesperado: {e}")

#ACTUALIZAR VALORES (CASA, TANQUE, CONEXIÓN)
def actualizar_valores():
    archivo_json = 'data/red_acueducto.json'
    try:
        # Cargar la red desde el archivo JSON
        red.cargar_desde_json(archivo_json)
        
        # Solicitar datos al usuario
        tipo = input("Ingresa el cambio que quieres realizar ('Casa', 'Tanque', 'Conexion'): ").strip()
        identificador = input(f"Ingresa el identificador del {tipo} que deseas actualizar: ").strip()
        nuevos_valores_raw = input(f"Ingresa los nuevos valores para el {tipo} (por ejemplo: clave1=valor1,clave2=valor2): ").strip()
        
        # Procesar la entrada de nuevos valores
        nuevos_valores = {}
        for item in nuevos_valores_raw.split(","):
            clave, valor = item.split("=")
            clave = clave.strip()
            valor = valor.strip()
            # Convertir valores numéricos si es necesario
            if valor.isdigit():
                valor = int(valor)
            elif valor.replace('.', '', 1).isdigit():
                valor = float(valor)
            nuevos_valores[clave] = valor
        
        # Llamar a la función actualizar_valores
        if red.actualizar_valores(tipo, identificador, **nuevos_valores):
            # Guardar los cambios en el archivo JSON
            red.guardar_a_json(archivo_json)
            print("Cambios guardados correctamente.")
        else:
            print("No se pudo realizar la actualización.")
        
    except FileNotFoundError:
        print(f"El archivo '{archivo_json}' no se encontró.")
    except json.JSONDecodeError:
        print(f"Error al leer el archivo JSON '{archivo_json}'. Verifica su formato.")
    except ValueError as e:
        print(f"Error en el formato de entrada: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

def cambiar_sentido_flujo():
    archivo_json = 'data/red_acueducto.json'
    try:
        # Cargar la red desde el archivo JSON
        red.cargar_desde_json(archivo_json)
        
        # Solicitar datos al usuario
        origen = input("Ingresa el nodo origen al que cambiar el flujo: ")
        destino = input("Ingresa el nodo destino al que cambiar el flujo: ")
        capacidad = float(input("Ingresa la capacidad que deseas revertir: "))
        # Verificar que los nodos existen en la red
        if origen not in red.nodos or destino not in red.nodos:
            print("Error: Uno o ambos nodos no existen en la red.")
            return
        # Intentar cambiar el sentido del flujo
        resultado = red.cambiar_sentido_flujo(origen, destino, capacidad)
        print(resultado)
        # Si el cambio fue exitoso, guardar la red actualizada en el archivo JSON
        if "Error" not in resultado:
            red.recalcular_flujo()
            red.guardar_a_json(archivo_json)
            print("Los cambios en la red han sido guardados exitosamente.")
        else:
            print("No se realizaron cambios en la red debido a un error.")
    except Exception as e:
        print(f"Ha ocurrido un error al cambiar el sentido del flujo: {e}")

#  IDENTIFICAR POSICIONES OPTIMAS PARA TANQUES:
def identificar_posiciones_optimas_interactivo():
    archivo_json = 'data/red_acueducto.json'
    try:
        # Cargar los datos desde el archivo JSON
        with open(archivo_json, 'r') as f:
            datos = json.load(f)
        
        casas = datos.get("casas", [])
        tanques = datos.get("tanques", [])
        conexiones = datos.get("conexiones", [])
        barrios_permitidos = datos.get("barrios_permitidos", {})
        
        # Solicitar parámetro al usuario
        umbral_demanda = float(input("Ingresa el umbral de demanda mínima por barrio (ej. 50): "))
        
        # Identificar posiciones óptimas
        posiciones = red.identificar_posiciones_optimas(
            casas, tanques, conexiones, barrios_permitidos, umbral_demanda
        )
        
        # Mostrar las posiciones sugeridas
        if posiciones:
            print("Posiciones óptimas para nuevos tanques:")
            for pos in posiciones:
                print(f"Barrio: {pos['barrio']}, Posición central: {pos['posicion_central']}, Demanda: {pos['demanda']}")
        else:
            print("No se encontraron posiciones óptimas con los parámetros proporcionados.")
    
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {archivo_json}. Asegúrate de que exista y esté en la ubicación correcta.")
    except json.JSONDecodeError:
        print(f"Error: El archivo {archivo_json} contiene un formato inválido.")
    except Exception as e:
        print(f"Ha ocurrido un error al identificar posiciones óptimas: {e}")

if __name__ == "__main__":
    #main()
    menu()
