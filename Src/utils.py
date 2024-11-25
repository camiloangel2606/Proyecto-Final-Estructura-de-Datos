import json
import networkx as nx
import matplotlib.pyplot as plt
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
                print(f"Contenido del archivo JSON: {data}")  # Depuración

            # Limpiar estructuras de datos existentes
            self.casa.clear()
            self.tanques.clear()
            self.conexiones.clear()

            # Cargar casas
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
                    capacidad=conexion['capacidad'],
                    color=conexion.get('color', 'blue')  # Color opcional
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
                        "capacidad": conexion.capacidad,
                        "color": conexion.color  # Guardar color
                    } for conexion in self.conexiones
                ]
            }
            
            # Guardar en el archivo JSON
            with open(archivo_json, 'w') as file:
                json.dump(data, file, indent=4)
        
            print(f"Red guardada con éxito en {archivo_json}")
        except Exception as e:
            print(f"Error al guardar el archivo JSON: {e}")

    #DETECTAR NODOS NO CONECTADOS:
    def obtener_nodos_no_conectados(self):
        """
        Identifica los nodos (casas y tanques) que no tienen conexiones.
        :return: Lista de nombres de nodos no conectados.
        """
        nodos_conectados = set()
        
        # Recopilar nodos conectados desde las conexiones
        for conexion in self.conexiones:
            nodos_conectados.add(conexion.origen)
            nodos_conectados.add(conexion.destino)
        
        # Todos los nodos posibles (casas y tanques)
        todos_nodos = set(self.casa.keys()).union(set(self.tanques.keys()))
        
        # Determinar nodos no conectados
        nodos_no_conectados = todos_nodos - nodos_conectados
        return nodos_no_conectados

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
        G = nx.DiGraph()

        # Agregar nodos (casas y tanques)
        for casa in self.casa.values():
            G.add_node(casa.nombre)
        for tanque in self.tanques.values():
            G.add_node(tanque.id_tanque)

        # Agregar aristas (conexiones)
        for conexion in self.conexiones:
            print(f"Añadiendo arista: origen={conexion.origen}, destino={conexion.destino}, capacidad={conexion.capacidad}, color={conexion.color}")
            G.add_edge(
                conexion.origen,
                conexion.destino,
                capacity=conexion.capacidad,
                color=conexion.color
            )

        print("Nodos en construir_grafo:", G.nodes())
        print("Aristas en construir_grafo:", G.edges(data=True))
        return G

    # Visualizar la red
    def visualizar_red(self):
        """
        Visualiza la red de acueducto utilizando NetworkX.
        """
        G = self.construir_grafo()

        # Identificar nodos no conectados
        nodos_no_conectados = self.obtener_nodos_no_conectados()

        # Posicionar nodos
        pos = nx.spring_layout(G)

        # Colores y etiquetas para las aristas
        edge_colors = [data['color'] for _, _, data in G.edges(data=True)]
        edge_labels = {
            (u, v): f"{data['capacity']:.1f}"  # Etiqueta de capacidad en las aristas
            for u, v, data in G.edges(data=True)
        }

        # Dibujar el grafo
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
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

        # Dibujar nodos no conectados
        if nodos_no_conectados:
            nx.draw_networkx_nodes(
                G,
                pos,
                nodelist=list(nodos_no_conectados),
                node_color="gray",  # Color distintivo para nodos no conectados
                node_size=500
            )

        # Título
        plt.title("Visualización de la Red de Acueducto")
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
    def agregar_conexion(self, origen, destino, capacidad, color="blue"):
        """
        Agrega una conexión entre dos nodos.
        :param origen: Nodo de origen.
        :param destino: Nodo de destino.
        :param capacidad: Capacidad de la conexión.
        :param color: Color de la conexión (opcional).
        """
        if origen not in self.casa and origen not in self.tanques:
            print(f"Error: El origen {origen} no existe.")
            return
        if destino not in self.casa and destino not in self.tanques:
            print(f"Error: El destino {destino} no existe.")
            return
        self.conexiones.append(Conexion(origen=origen, destino=destino, capacidad=capacidad, color=color))
        print(f"Conexión agregada: origen={origen}, destino={destino}, capacidad={capacidad}, color={color}")

    #SIMULAR OBSTRUCCIÓN
    def simular_obstruccion(self, origen, destino, nivel_gravedad):
        """
        Simula una obstrucción en una conexión específica.
        :param origen: Nodo de origen de la conexión.
        :param destino: Nodo de destino de la conexión.
        :param nivel_gravedad: Nivel de obstrucción (0.0 a 1.0).
                                0.0 significa sin obstrucción.
                                1.0 significa obstrucción total.
        """
        if nivel_gravedad < 0.0 or nivel_gravedad > 1.0:
            print("Error: El nivel de gravedad debe estar entre 0.0 y 1.0.")
            return
        
        for conexion in self.conexiones:
            if conexion.origen == origen and conexion.destino == destino:
                # Reducir capacidad según gravedad
                nueva_capacidad = conexion.capacidad * (1.0 - nivel_gravedad)
                conexion.capacidad = max(nueva_capacidad, 0)  # Evitar capacidades negativas

                # Determinar color según nivel de gravedad
                if nivel_gravedad == 0.0:
                    conexion.color = "blue"
                elif nivel_gravedad <= 0.33:
                    conexion.color = "yellow"
                elif nivel_gravedad <= 0.66:
                    conexion.color = "orange"
                else:
                    conexion.color = "red"

                print(f"Obstrucción simulada en la conexión de '{origen}' a '{destino}'.")
                print(f"Capacidad reducida a {conexion.capacidad:.2f} y color actualizado a '{conexion.color}'.")
                return
        
        print(f"Error: No se encontró la conexión de '{origen}' a '{destino}' para simular la obstrucción.")
