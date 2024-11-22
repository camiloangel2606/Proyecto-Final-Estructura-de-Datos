import networkx as nx
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
    red = RedDeAcueducto()
    red.cargar_desde_json('data/red_acueducto.json')#Cargamos archivo json.
    
    # Crear el grafo
    G = nx.DiGraph()
    for conexion in red.conexiones:
        G.add_edge(conexion.origen, conexion.destino, capacity=conexion.capacidad)
    
    # Mostrar información básica
    print("Nodos:", G.nodes)
    print("Conexiones:", G.edges(data=True))
    
    #Menú
    i = 1
    opciones = {#Opciones de funciones que se tendrán en el menú
        0: salir,
        1: agregar_barrio,
        2: agregar_tanque,
        3: agregar_conexion,
        4: eliminar_barrio,
        5: eliminar_tanque,
        6: eliminar_conexion,
    }
    
    while i != 0:
        print("BIENVENIDO AL MENÚ DE OPERACIÓN DEL ACUEDUCTO")
        print("Ingresa la operación a realizar")
        print("Agregar: (1) Barrio, (2) Tanque, (3) Conexión. Al acueducto")
        print("Eliminar: (4) Barrio, (5) Tanque, (6) Conexión. Al acueducto")
        print("(0) Salir del menú")
        i = input()
            

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
def agregar_barrio():
    print("Ingresa la información del barrio.")
    nombre = input("Ingresa el nombre del barrio.")
    demanda = int(input("Ingresa la demanda que tiene el barrio."))
    red.agregar_barrio(nombre,demanda)

if __name__ == "__main__":
    main()
    menu()
