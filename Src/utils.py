import json
import heapq
import networkx as nx
import matplotlib.pyplot as plt
from models import Casa, Tanque, Conexion

class RedDeAcueducto:
    def __init__(self):
        self.casa = {}  # Cambiado de barrios a casa
        self.tanques = {}
        self.conexiones = []
        self.grafo = None
    
    @property
    def nodos(self):
        # Crear un conjunto de todos los nodos a partir de las conexiones
        todos_nodos = set()
        for conexion in self.conexiones:
            todos_nodos.add(conexion.origen)
            todos_nodos.add(conexion.destino)
        return todos_nodos
    
    def cargar_desde_json(self, archivo_json):
        """
        Carga la red desde un archivo JSON.
        :param archivo_json: Ruta del archivo JSON.
        """
        import json
        try:
            with open(archivo_json, 'r') as file:
                data = json.load(file)
                print(f"Contenido del archivo JSON: {data}")  # Depuración

            # Limpiar estructuras de datos existentes
            self.casa = {}  # Usar diccionario para indexar casas
            self.tanques = {}  # Usar diccionario para indexar tanques
            self.conexiones = []  # Lista para conexiones

            # Cargar casas
            for casa in data.get('casas', []):
                self.agregar_casa(
                    nombre=casa['nombre'],
                    demanda=casa['demanda']
                )

            # Cargar tanques
            for tanque in data.get('tanques', []):
                self.agregar_tanque(
                    id_tanque=tanque['id'],
                    capacidad=tanque['capacidad'],
                    nivel_actual=tanque['nivel_actual']
                )

            # Cargar conexiones
            for conexion in data.get('conexiones', []):
                self.agregar_conexion(
                    origen=conexion['origen'],
                    destino=conexion['destino'],
                    capacidad=conexion['capacidad'],
                    color=conexion.get('color', 'blue')
                )

            print("Red cargada con éxito.")
            self.verificar_consistencia()  # Verifica integridad de la red
        except FileNotFoundError:
            print(f"El archivo '{archivo_json}' no se encuentra.")
        except json.JSONDecodeError as e:
            print(f"Error en el formato del archivo JSON: {e}")
        except Exception as e:
            print(f"Error al cargar el archivo JSON: {e}")


    def guardar_a_json(self, archivo_json):
        """
        Guarda la red en un archivo JSON.
        :param archivo_json: Ruta del archivo JSON donde se guardará la red.
        """
        import json
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
                        "color": conexion.color
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

    #DETECTAR BUCLES:
    def detectar_bucles(self):
        """
        Detecta bucles en el grafo de conexiones.
        Devuelve un booleano indicando si hay bucles y los nodos involucrados en el primer bucle detectado.
        """
        def dfs(nodo, visitados, stack):
            """
            Búsqueda en profundidad (DFS) para detectar ciclos.
            :param nodo: Nodo actual.
            :param visitados: Conjunto de nodos visitados.
            :param stack: Conjunto de nodos en la pila de recorrido.
            :return: (booleano, lista del ciclo detectado).
            """
            if nodo in stack:
                # Encontramos un ciclo; construirlo desde la pila
                ciclo = list(stack)
                indice_ciclo = ciclo.index(nodo)
                return True, ciclo[indice_ciclo:]
            
            if nodo in visitados:
                return False, []  # Nodo ya explorado y sin bucle
            
            # Marcar el nodo como visitado
            visitados.add(nodo)
            stack.append(nodo)
            
            # Explorar vecinos (destinos de las conexiones salientes)
            for conexion in self.conexiones:
                if conexion.origen == nodo:
                    ciclo_encontrado, ciclo = dfs(conexion.destino, visitados, stack)
                    if ciclo_encontrado:
                        return True, ciclo
            
            # Retroceder en la pila
            stack.pop()
            return False, []
        visitados = set()
        for nodo in list(self.casa.keys()) + list(self.tanques.keys()):
            if nodo not in visitados:
                stack = []
                ciclo_encontrado, ciclo = dfs(nodo, visitados, stack)
                if ciclo_encontrado:
                    return True, ciclo  # Bucle detectado
        
        return False, []  # No hay ciclos

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

    def visualizar_red(self):
        """
        Visualiza la red de acueducto utilizando NetworkX.
        Muestra la demanda, suministro y excedente de cada casa,
        así como la capacidad restante de cada tanque.
        """
        G = self.construir_grafo()
        # Identificar nodos no conectados
        nodos_no_conectados = self.obtener_nodos_no_conectados()
        # Posicionar nodos con ajuste de distancia
        pos = nx.spring_layout(G, k=0.8, iterations=50)  # Ajuste de k para mayor separación
        # Colores y etiquetas para las aristas
        edge_colors = [data['color'] for _, _, data in G.edges(data=True)]
        edge_labels = {
            (u, v): f"{data['capacity']:.1f}"  # Etiqueta de capacidad en las aristas
            for u, v, data in G.edges(data=True)
        }
        # Crear etiquetas y colores para nodos
        node_labels = {}
        node_colors = []
        # Agregar casas a las etiquetas y colores
        for casa in self.casa.values():
            # Calcular el suministro total hacia la casa desde las conexiones
            suministro_total = sum(
                conexion.capacidad
                for conexion in self.conexiones
                if conexion.destino == casa.nombre
            )
            # Calcular el excedente de agua
            excedente = max(suministro_total - casa.demanda, 0)
            # Etiqueta para la casa
            node_labels[casa.nombre] = (
                f"{casa.nombre}\n"
                f"Demanda: {casa.demanda:.1f}\n"
                f"Suministro: {suministro_total:.1f}\n"
                f"Excedente: {excedente:.1f}"
            )
            # Color basado en el suministro total
            if suministro_total >= casa.demanda:
                node_colors.append("green")  # Casa satisfecha (demanda cubierta)
            else:
                node_colors.append("yellow")  # Casa con demanda pendiente
        # Agregar tanques a las etiquetas y colores
        for tanque in self.tanques.values():
            capacidad_disponible = tanque.nivel_actual - sum(
                conexion.capacidad
                for conexion in self.conexiones
                if conexion.origen == tanque.id_tanque
            )
            node_labels[tanque.id_tanque] = (
                f"{tanque.id_tanque}\nCapacidad restante: {capacidad_disponible:.1f}"
            )
            # Definir color del tanque basado en capacidad disponible
            if capacidad_disponible <= 0:
                node_colors.append("red")  # Tanques agotados
            elif capacidad_disponible <= 0.2 * tanque.capacidad:  # Menos del 20% disponible
                node_colors.append("orange")  # Capacidad baja
            else:
                node_colors.append("green")  # Capacidad suficiente
        # Dibujar el grafo
        plt.figure(figsize=(12, 8))  # Ajustar tamaño del gráfico
        nx.draw(
            G,
            pos,
            with_labels=False,  # Desactivamos las etiquetas predeterminadas
            edge_color=edge_colors,
            node_color=node_colors,
            node_size=500,
            font_size=10,
            font_color="black"
        )
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
        nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=9)
        # Dibujar nodos no conectados
        if nodos_no_conectados:
            nx.draw_networkx_nodes(
                G,
                pos,
                nodelist=list(nodos_no_conectados),
                node_color="gray",  # Color distintivo para nodos no conectados
                node_size=500
            )
        # Ajustar márgenes
        plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
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
    
    def agregar_conexion(self, origen, destino, capacidad, color="blue"):
        """
        Agrega una conexión entre dos nodos, con validaciones adicionales.
        :param origen: Nodo de origen.
        :param destino: Nodo de destino.
        :param capacidad: Capacidad de la conexión.
        :param color: Color de la conexión (opcional).
        """
        # Verificar si el origen y el destino existen
        if origen not in self.casa and origen not in self.tanques:
            print(f"Error: El nodo origen '{origen}' no existe.")
            return
        if destino not in self.casa and destino not in self.tanques:
            print(f"Error: El nodo destino '{destino}' no existe.")
            return
        # Validar tipos de conexiones permitidas
        origen_es_casa = origen in self.casa
        destino_es_casa = destino in self.casa
        origen_es_tanque = origen in self.tanques
        destino_es_tanque = destino in self.tanques
        if origen_es_casa and destino_es_tanque:
            print("Error: No se permite una conexión de una casa a un tanque.")
            return
        if not (
            (origen_es_casa and destino_es_casa) or
            (origen_es_tanque and destino_es_casa) or
            (origen_es_tanque and destino_es_tanque)
        ):
            print("Error: Conexión no permitida. Solo se permiten conexiones:")
            print(" - Casa a Casa")
            print(" - Tanque a Casa")
            print(" - Tanque a Tanque")
            return
        # Validar que el nodo origen tenga suficiente capacidad
        capacidad_disponible = 0
        if origen_es_tanque:
            tanque = self.tanques[origen]
            capacidad_disponible = tanque.nivel_actual - sum(
                conexion.capacidad for conexion in self.conexiones if conexion.origen == origen
            )
        elif origen_es_casa:
            suministro_total = sum(
                conexion.capacidad for conexion in self.conexiones if conexion.destino == origen
            )
            demanda_total = self.casa[origen].demanda
            capacidad_disponible = max(suministro_total - demanda_total, 0)
        if capacidad > capacidad_disponible:
            print(f"Error: El nodo origen '{origen}' no tiene suficiente capacidad disponible. "
                f"Capacidad disponible: {capacidad_disponible:.1f}, Capacidad requerida: {capacidad:.1f}.")
            return
        # Agregar la conexión si pasa las validaciones
        self.conexiones.append(Conexion(origen=origen, destino=destino, capacidad=capacidad, color=color))
        print(f"Conexión agregada: origen={origen}, destino={destino}, capacidad={capacidad}, color={color}")

    #SIMULAR OBSTRUCCIÓN
    def simular_obstruccion(self, origen=None, destino=None, nivel_gravedad=None):
        """
        Simula obstrucciones en conexiones. Permite la entrada manual o automática si se proporcionan argumentos.
        """
        while True:
            if origen is None or destino is None or nivel_gravedad is None:
                try:
                    origen = input("Ingrese el nodo de origen de la conexión: ")
                    destino = input("Ingrese el nodo de destino de la conexión: ")
                    nivel_gravedad = float(input("Ingrese el nivel de gravedad (0 a 100): "))
                    nivel_gravedad = nivel_gravedad/100
                except ValueError:
                    print("Error: Ingrese un nivel de gravedad válido (0 a 100).")
                    continue
            if nivel_gravedad < 0.0 or nivel_gravedad > 1.0:
                print("Error: El nivel de gravedad debe estar entre 0.0 y 100.")
                origen, destino, nivel_gravedad = None, None, None
                continue
            conexion_encontrada = False
            for conexion in self.conexiones:
                if conexion.origen == origen and conexion.destino == destino:
                    conexion_encontrada = True
                    nueva_capacidad = conexion.capacidad * (1.0 - nivel_gravedad)
                    conexion.capacidad = max(nueva_capacidad, 0)
                    if nivel_gravedad == 0.0:
                        conexion.color = "blue"
                    elif nivel_gravedad <= 0.33:
                        conexion.color = "yellow"
                    elif nivel_gravedad <= 0.66:
                        conexion.color = "orange"
                    else:
                        conexion.color = "red"
                    print(f"\nObstrucción simulada en la conexión de '{origen}' a '{destino}'.")
                    print(f"Capacidad reducida a {conexion.capacidad:.2f} y color actualizado a '{conexion.color}'.")
                    break
            if not conexion_encontrada:
                print(f"Error: No se encontró la conexión de '{origen}' a '{destino}' para simular la obstrucción.")
            if origen is not None and destino is not None and nivel_gravedad is not None:
                # Si se pasaron argumentos, salir después de una simulación
                break
            continuar = input("¿Desea simular otra obstrucción? (s/n): ").strip().lower()
            if continuar != 's':
                print("Finalizando simulación de obstrucciones.")
                break

    #ENCONTRAR UNA RUTA ALTERNATIVA
    def encontrar_ruta_alternativa(self, origen, destino):
        """
        Encuentra la ruta alternativa más óptima entre dos nodos en el grafo,
        minimizando el impacto en la capacidad de los tanques.
        Parámetros:
        - origen: Nodo inicial.
        - destino: Nodo final.
        Retorna:
        - Lista de nodos que forman la ruta alternativa óptima.
        """
        G = self.construir_grafo()
        if not nx.has_path(G, origen, destino):
            print(f"No hay camino entre {origen} y {destino}.")
            return None
        # Usar Dijkstra para encontrar la ruta con menor peso
        ruta_alternativa = nx.shortest_path(
            G, source=origen, target=destino, weight='weight'
        )
        return ruta_alternativa

    # VISUALIZAR LA RUTA ALTERNATIVA
    def visualizar_rutas_alternativas(self, rutas):
        """
        Visualiza las rutas alternativas en el grafo.
        Parámetros:
        - rutas: Lista de rutas alternativas (listas de nodos).
        """
        G = self.construir_grafo()
        pos = nx.spring_layout(G)
        # Dibujar grafo base
        edge_colors = [data['color'] for _, _, data in G.edges(data=True)]
        node_colors = ["lightblue" if "Casa" in node else "green" for node in G.nodes()]
        nx.draw(
            G,
            pos,
            with_labels=True,
            edge_color=edge_colors,
            node_color=node_colors,
            node_size=500
        )
        # Dibujar rutas alternativas
        for ruta in rutas:
            ruta_aristas = [(ruta[i], ruta[i+1]) for i in range(len(ruta)-1)]
            nx.draw_networkx_edges(
                G,
                pos,
                edgelist=ruta_aristas,
                edge_color="blue",
                width=2
            )
        # Mostrar el grafo
        plt.title("Rutas Alternativas")
        plt.show()

    # CALCULAR Y VISUALIZAR RUTAS
    def calcular_y_visualizar_rutas(self, casas_afectadas):
        """
        Encuentra y visualiza las rutas alternativas para las casas afectadas.

        Parámetros:
        - casas_afectadas: Lista de nodos afectados (casas).
        """
        G = self.construir_grafo()
        rutas = []
        for casa in casas_afectadas:
            # Buscar ruta desde cualquier tanque al nodo afectado
            for tanque in [n for n in G.nodes() if "Tanque" in n]:
                ruta = self.encontrar_ruta_alternativa(origen=tanque, destino=casa)
                if ruta:
                    rutas.append(ruta)
                    break  # Salir del bucle si se encuentra una ruta válida
        # Visualizar las rutas
        self.visualizar_rutas_alternativas(rutas)

    # APLICAR OBSTRUCCIONES
    def aplicar_obstrucciones(self, obstrucciones):
        """
        Marca las aristas afectadas por obstrucciones en el grafo.
        Parámetros:
        - obstrucciones: Lista de aristas afectadas (tuplas: (nodo1, nodo2)).
        """
        G = self.construir_grafo()
        for (u, v) in obstrucciones:
            if G.has_edge(u, v):
                G[u][v]['weight'] = float('inf')  # Bloquear la arista
                G[u][v]['color'] = "red"  # Marcar como obstruida
    
    #ACTUALIZAR VALORES(CASA, TANQUE, CONEXIÓN)
    def actualizar_valores(self, tipo, identificador, **nuevos_valores):
        """
        Actualiza los valores de una casa, tanque o conexión en la red.

        Parámetros:
        - tipo (str): Tipo del objeto a actualizar ('casa', 'tanque', 'conexion').
        - identificador (str): Identificador del objeto.
        - nuevos_valores (dict): Valores nuevos a asignar.

        Retorna:
        - bool: True si la actualización fue exitosa, False en caso contrario.
        """
        if tipo == "Casa":
            if identificador in self.casa:
                casa = self.casa[identificador]
                if "nombre" in nuevos_valores:
                    print(f"No se permite cambiar el nombre de la casa '{identificador}'.")
                if "demanda" in nuevos_valores:
                    casa.demanda = nuevos_valores["demanda"]
                    print(f"Casa '{identificador}' actualizada: demanda={casa.demanda}")
                return True
            else:
                print(f"Error: La casa '{identificador}' no existe.")
        
        elif tipo == "Tanque":
            if identificador in self.tanques:
                tanque = self.tanques[identificador]
                if "capacidad" in nuevos_valores:
                    tanque.capacidad = nuevos_valores["capacidad"]
                if "nivel_actual" in nuevos_valores:
                    tanque.nivel_actual = nuevos_valores["nivel_actual"]
                print(f"Tanque '{identificador}' actualizado: capacidad={tanque.capacidad}, nivel_actual={tanque.nivel_actual}")
                return True
            else:
                print(f"Error: El tanque '{identificador}' no existe.")
        
        elif tipo == "Conexion":
            conexion_encontrada = None
            for conexion in self.conexiones:
                if conexion.origen == identificador[0] and conexion.destino == identificador[1]:
                    conexion_encontrada = conexion
                    break
            if conexion_encontrada:
                if "capacidad" in nuevos_valores:
                    conexion_encontrada.capacidad = nuevos_valores["capacidad"]
                if "color" in nuevos_valores:
                    conexion_encontrada.color = nuevos_valores["color"]
                print(f"Conexión '{identificador}' actualizada: capacidad={conexion_encontrada.capacidad}, color={conexion_encontrada.color}")
                return True
            else:
                print(f"Error: No se encontró la conexión '{identificador}'.")
        
        else:
            print(f"Error: Tipo '{tipo}' no reconocido. Use 'casa', 'tanque' o 'conexion'.")
            return False
    
    #CAMBIAR DIRECCIÓN DEL FLUJO:
    def cambiar_sentido_flujo(self, origen, destino, capacidad):
        """
        Cambia el sentido del flujo en una conexión y redistribuye el agua en la red.
        Si el cambio de sentido es válido, actualiza las conexiones y recalcula el flujo de agua.
        
        :param origen: Nodo de origen.
        :param destino: Nodo de destino.
        :param capacidad: Capacidad de la conexión.
        :return: Mensaje sobre si el cambio fue exitoso o si ocurrió un error.
        """
        # Verificar si la conexión existe
        conexion_existente = next((c for c in self.conexiones if c.origen == origen and c.destino == destino), None)
        if not conexion_existente:
            return f"Error: No existe una conexión entre {origen} y {destino}."
        # Verificar si la capacidad a invertir es válida
        if capacidad > conexion_existente.capacidad:
            return f"Error: La capacidad solicitada excede la capacidad disponible en la conexión ({conexion_existente.capacidad})."
        # Validar restricciones para la nueva conexión resultante
        if destino in self.casa and origen in self.tanques:
            nueva_conexion_permitida = False
            return "Error: El cambio de flujo generaría una conexión no permitida Casa -> Tanque."
        elif destino in self.casa and origen in self.casa:
            nueva_conexion_permitida = True  # Casa → Casa (permitido)
        elif destino in self.tanques and origen in self.tanques:
            nueva_conexion_permitida = True  # Tanque → Tanque (permitido)
        else:
            nueva_conexion_permitida = False  # Cualquier otra combinación es inválida
        if not nueva_conexion_permitida:
            return "Error: El cambio de flujo resultaría en una conexión no permitida."
        # Realizar el cambio de flujo
        conexion_existente.capacidad -= capacidad
        if conexion_existente.capacidad == 0:
            self.conexiones.remove(conexion_existente)  # Eliminar la conexión si ya no tiene capacidad
        # Crear nueva conexión en el sentido inverso
        nueva_conexion = Conexion(
            origen=destino, destino=origen, capacidad=capacidad, color=conexion_existente.color
        )
        self.conexiones.append(nueva_conexion)
        return f"Flujo revertido: {capacidad} unidades de agua ahora fluyen de {destino} a {origen}."
    
    #RECALCULAR FLUJO DEL AGUA:
    def recalcular_flujo(self):
        """
        Recalcula el flujo total en la red después de cualquier cambio.
        Se debe ajustar el flujo hacia las casas y los tanques según las nuevas direcciones.
        """
        # Recalcular el flujo en cada nodo (tanque y casa) para reflejar los cambios
        for nodo in list(self.casa.keys()) + list(self.tanques.keys()):
            flujo_total = 0
            # Calcular el flujo total hacia el nodo desde las conexiones entrantes
            for conexion in self.conexiones:
                if conexion.destino == nodo:
                    flujo_total += conexion.capacidad
            # Ajustar el flujo en el nodo (tanque/casa)
            if nodo in self.casa:
                casa = self.casa[nodo]
                casa.suministro = flujo_total  # Actualizamos el suministro de la casa
                print(f"Casa {nodo} ahora tiene un suministro de {flujo_total} litros.")
            elif nodo in self.tanques:
                tanque = self.tanques[nodo]
                tanque.nivel_actual = max(0, tanque.nivel_actual - flujo_total)  # Actualizamos el nivel del tanque
                print(f"Tanque {nodo} tiene un nivel actual de {tanque.nivel_actual} litros.")
