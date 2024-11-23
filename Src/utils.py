import json
from models import Casa, Tanque, Conexion

class RedDeAcueducto:
    def __init__(self):
        self.casa = {}  # Cambiado de barrios a casa
        self.tanques = {}
        self.conexiones = []

    # CARGAR ARCHIVOS JSON
    def cargar_desde_json(self, archivo_json):
        """
        Carga la red desde un archivo JSON.
        :param archivo_json: Ruta del archivo JSON.
        """
        try:
            with open(archivo_json, 'r') as file:
                data = json.load(file) 
                print(f"Contenido del archivo JSON: {data}")  # Agregado para depuración
            
            # Cargar barrios
            for casa in data['casas']:
                self.agregar_casa(
                    nombre=casa['nombre'], 
                    demanda=casa['demanda']
                )

            # Cargar tanques
            for tanque in data['tanques']:
                self.agregar_tanque(
                    id_tanque=tanque['id'], 
                    capacidad=tanque['capacidad'], 
                    nivel_actual=tanque['nivel_actual']
                )

            # Cargar conexiones
            for conexion in data['conexiones']:
                self.agregar_conexion(
                    origen=conexion['origen'],
                    destino=conexion['destino'],
                    capacidad=conexion['capacidad']
                )
            
            print("Red cargada con éxito.")
            self.verificar_consistencia()
        except Exception as e:
            print(f"Error al cargar el archivo JSON: {e}")

    # GUARDAR ARCHIVO JSON
    def guardar_a_json(self, archivo_json):
        """
        Guarda la red en un archivo JSON.
        :param archivo_json: Ruta del archivo JSON donde se guardará la red.
        """
        try:
            # Crear el diccionario que representa la red
            data = {
                "casas": [
                    {
                        "nombre": casa.nombre,
                        "demanda": casa.demanda
                    } for casa in self.casa.values()
                ],
                "tanques": [
                    {
                        "id": tanque.id_tanque,
                        "capacidad": tanque.capacidad,
                        "nivel_actual": tanque.nivel_actual
                    } for tanque in self.tanques.values()
                ],
                "conexiones": [
                    {
                        "origen": conexion.origen,
                        "destino": conexion.destino,
                        "capacidad": conexion.capacidad
                    } for conexion in self.conexiones
                ]
            }
            
            # Guardar en el archivo JSON
            with open(archivo_json, 'w') as file:
                json.dump(data, file, indent=4)
        
            print(f"Red guardada con éxito en {archivo_json}")
        except Exception as e:
            print(f"Error al guardar el archivo JSON: {e}")

    # CONEXIONES CON NODOS NO DEFINIDOS
    def verificar_nodos_no_definidos(self):
        errores = []
        for conexion in self.conexiones:
            if conexion.origen not in self.casa and conexion.origen not in self.tanques:
                errores.append(f"Error: Nodo origen '{conexion.origen}' no está definido.")
            if conexion.destino not in self.casa and conexion.destino not in self.tanques:
                errores.append(f"Error: Nodo destino '{conexion.destino}' no está definido.")
        return errores

    # CONEXIONES DUPLICADAS
    def verificar_conexiones_duplicadas(self):
        errores = []
        conexiones_vistas = set()
        for conexion in self.conexiones:
            par_conexion = (conexion.origen, conexion.destino)
            if par_conexion in conexiones_vistas:
                errores.append(f"Error: Conexión duplicada entre '{conexion.origen}' y '{conexion.destino}'.")
            else:
                conexiones_vistas.add(par_conexion)
        return errores

    # BUCLES EN EL FLUJO
    def detectar_bucles(self):
        def dfs(nodo, visitados, stack, camino):
            visitados.add(nodo)
            stack.add(nodo)
            camino.append(nodo)
            for conexion in self.conexiones:
                if conexion.origen == nodo:
                    siguiente = conexion.destino
                    if siguiente not in visitados:
                        if dfs(siguiente, visitados, stack, camino):
                            return True, camino
                    elif siguiente in stack:
                        # Encontramos un bucle
                        indice_ciclo = camino.index(siguiente)
                        return True, camino[indice_ciclo:]  # Retornar el ciclo
            stack.remove(nodo)
            camino.pop()  # Remover el nodo al retroceder
            return False, []
        visitados = set()
        for nodo in list(self.casa.keys()) + list(self.tanques.keys()):
            if nodo not in visitados:
                ciclo, nodos_ciclo = dfs(nodo, visitados, set(), [])
                if ciclo:
                    return True, nodos_ciclo
        return False, []

    # VALIDAR DURANTE LA CARGA
    def verificar_consistencia(self):
        errores = []
        errores.extend(self.verificar_nodos_no_definidos())
        errores.extend(self.verificar_conexiones_duplicadas())
        ciclo, nodos_ciclo = self.detectar_bucles()
        if ciclo:
            errores.append(f"Error: Se detectó un bucle en la red que involucra los nodos: {', '.join(nodos_ciclo)}")
        if errores:
            print("Errores detectados durante la verificación de la red:")
            for error in errores:
                print(f" - {error}")
        else:
            print("La red está consistente.")

    # SIMULACIONES
    def construir_grafo(self):
        import networkx as nx
        G = nx.DiGraph()
        for conexion in self.conexiones:
            G.add_edge(
                conexion.origen,
                conexion.destino,
                capacity=conexion.capacidad,
                color=getattr(conexion, 'color', 'blue')
            )
        print("Nodos en el grafo:", G.nodes())
        print("Aristas en el grafo:", G.edges(data=True))
        return G

    # Visualizar la red
    def visualizar_red(self):
        import networkx as nx
        import matplotlib.pyplot as plt
        G = self.construir_grafo()
        
        edge_colors = [data['color'] for _, _, data in G.edges(data=True)]
        pos = nx.spring_layout(G)
        
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
        plt.show()

    # AGREGAR CASA
    def agregar_casa(self, nombre, demanda):
        """
        Agrega una casa a la red.
        :param nombre: Nombre de la casa.
        :param demanda: Demanda de agua de la casa.
        """
        if nombre in self.casa:
            print(f"Error: La casa '{nombre}' ya existe.")
            return
        self.casa[nombre] = Casa(nombre=nombre, demanda=demanda)
        print(f"Casa '{nombre}' agregada con éxito.")
    
    # ELIMINAR CASA
    def eliminar_casa(self, nombre):
        """
        Elimina una casa de la red.
        :param nombre: Nombre de la casa.
        """
        if nombre not in self.casa:
            print(f"Error: La casa '{nombre}' no existe.")
            return
        # Eliminar conexiones relacionadas con la casa
        self.conexiones = [c for c in self.conexiones if c.origen != nombre and c.destino != nombre]
        del self.casa[nombre]
        print(f"Casa '{nombre}' eliminada con éxito.")
    
    # AGREGAR TANQUE
    def agregar_tanque(self, id_tanque, capacidad, nivel_actual):
        """
        Agrega un tanque a la red.
        :param id_tanque: ID del tanque.
        :param capacidad: Capacidad máxima del tanque.
        :param nivel_actual: Nivel actual del tanque.
        """
        if id_tanque in self.tanques:
            print(f"Error: El tanque '{id_tanque}' ya existe.")
            return
        self.tanques[id_tanque] = Tanque(id_tanque=id_tanque, capacidad=capacidad, nivel_actual=nivel_actual)
        print(f"Tanque '{id_tanque}' agregado con éxito.")
    
    # ELIMINAR TANQUE
    def eliminar_tanque(self, id_tanque):
        """
        Elimina un tanque de la red.
        :param id_tanque: ID del tanque.
        """
        if id_tanque not in self.tanques:
            print(f"Error: El tanque '{id_tanque}' no existe.")
            return
        # Eliminar conexiones relacionadas con el tanque
        self.conexiones = [c for c in self.conexiones if c.origen != id_tanque and c.destino != id_tanque]
        del self.tanques[id_tanque]
        print(f"Tanque '{id_tanque}' eliminado con éxito.")
    
    # AGREGAR CONEXIÓN
    def agregar_conexion(self, origen, destino, capacidad):
        """
        Agrega una conexión entre dos nodos.
        :param origen: Nodo de origen.
        :param destino: Nodo de destino.
        :param capacidad: Capacidad de la conexión.
        """
        self.conexiones.append(Conexion(origen=origen, destino=destino, capacidad=capacidad))
        print(f"Conexión agregada entre '{origen}' y '{destino}' con capacidad {capacidad}.")
