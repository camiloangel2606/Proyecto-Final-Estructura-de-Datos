import json
import heapq
import os
import networkx as nx
import streamlit as st
import matplotlib.pyplot as plt
from models import Casa, Tanque, Conexion

class RedDeAcueducto:
    def __init__(self):
        self.casa = {}  # Cambiado de barrios a casa
        self.tanques = {}
        self.conexiones = []
        self.grafo = None
        self.barrios_permitidos = ["Fátima", "Palermo", "Cable"]
    
    @property
    def nodos(self):
        # Crear un conjunto de nodos a partir de casas, tanques y conexiones
        todos_nodos = set(self.casa.keys()) | set(self.tanques.keys())
        for conexion in self.conexiones:
            todos_nodos.add(conexion.origen)
            todos_nodos.add(conexion.destino)
        return todos_nodos

    #CARGAR JSON:
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
            self.barrios_permitidos = data.get("barrios_permitidos", ["Fátima", "Palermo", "Cable"])
            self.casa = {}
            self.tanques = {}
            self.conexiones = []
            # Cargar casas
            for casa in data.get('casas', []):
                if all(key in casa for key in ['nombre', 'demanda']):
                    self.agregar_casa(
                        nombre=casa['nombre'],
                        demanda=casa['demanda'],
                        barrio=casa.get('barrio', None)
                    )
                else:
                    print(f"Casa con datos incompletos: {casa}")
            # Cargar tanques
            for tanque in data.get('tanques', []):
                if all(key in tanque for key in ['id', 'capacidad', 'nivel_actual']):
                    self.agregar_tanque(
                        id_tanque=tanque['id'],
                        capacidad=tanque['capacidad'],
                        nivel_actual=tanque['nivel_actual'],
                        barrio=tanque.get('barrio', None)
                    )
                else:
                    print(f"Tanque con datos incompletos: {tanque}")
            # Cargar conexiones
            for conexion in data.get('conexiones', []):
                origen = conexion.get('origen')
                destino = conexion.get('destino')
                if origen in self.casa or origen in self.tanques:
                    if destino in self.casa or destino in self.tanques:
                        self.agregar_conexion(
                            origen=origen,
                            destino=destino,
                            capacidad=conexion['capacidad'],
                            color=conexion.get('color', 'blue')
                        )
                    else:
                        print(f"Destino inválido para la conexión: {conexion}")
                else:
                    print(f"Origen inválido para la conexión: {conexion}")
            print("Casas cargadas:", list(self.casa.keys()))
            print("Tanques cargados:", list(self.tanques.keys()))
            print("Red cargada con éxito.")
            self.verificar_consistencia()
        except FileNotFoundError:
            print(f"El archivo '{archivo_json}' no se encuentra.")
        except json.JSONDecodeError as e:
            print(f"Error en el formato del archivo JSON: {e}")
        except Exception as e:
            print(f"Error al cargar el archivo JSON: {e}")

    #GUARDAR JSON:
    def guardar_a_json(self, archivo_json):
        """
        Guarda la red en un archivo JSON.
        :param archivo_json: Ruta del archivo JSON donde se guardará la red.
        """
        import json
        try:
            # Crear el diccionario que representa la red
            data = {
                "barrios_permitidos": self.barrios_permitidos,
                "casas": [
                    {
                        "nombre": casa.nombre,
                        "demanda": casa.demanda,
                        "barrio": casa.barrio  # Incluir el atributo barrio
                    } for casa in self.casa.values()
                ],
                "tanques": [
                    {
                        "id": tanque.id_tanque,
                        "capacidad": tanque.capacidad,
                        "nivel_actual": tanque.nivel_actual,
                        "barrio": tanque.barrio  # Incluir el atributo barrio
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
            with open(archivo_json, 'w', encoding="utf-8") as f:  # Abrir en modo escritura
                json.dump(data, f, ensure_ascii=False, indent=4)  # Volcar los datos a JSON
                
            print(f"Red guardada con éxito en {archivo_json}")
        except Exception as e:
            print(f"Error al guardar el archivo JSON: {e}")

    #REGISTRAR HISTORIAL:
    def registrar_historial(self, cambio):
        historial_path = 'data/historial.json'
        
        # Verificar si el archivo existe, si no, crearlo
        if not os.path.exists(historial_path):
            with open(historial_path, 'w', encoding='utf-8') as file:
                json.dump([], file, ensure_ascii=False, indent=4)  # Crear archivo vacío si no existe
        
        try:
            # Leer el historial actual
            with open(historial_path, 'r', encoding='utf-8') as file:
                historial = json.load(file)
            
            # Agregar el nuevo cambio al historial
            historial.append(cambio)
            
            # Guardar el historial actualizado
            with open(historial_path, 'w', encoding='utf-8') as file:
                json.dump(historial, file, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error al guardar el historial: {e}")

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
        """
        Construye el grafo dirigido utilizando NetworkX a partir de las casas, tanques y conexiones.
        """
        G = nx.DiGraph()
        
        # Agregar nodos para casas y tanques
        for casa in self.casa.values():
            G.add_node(casa.nombre, tipo="casa", barrio=casa.barrio)
        for tanque in self.tanques.values():
            G.add_node(tanque.id_tanque, tipo="tanque", barrio=tanque.barrio)
        
        # Agregar aristas (conexiones)
        for conexion in self.conexiones:
            if conexion.origen in G.nodes() and conexion.destino in G.nodes():
                print(f"Añadiendo arista: origen={conexion.origen}, destino={conexion.destino}, capacidad={conexion.capacidad}, color={conexion.color}")
                G.add_edge(
                    conexion.origen,
                    conexion.destino,
                    capacity=conexion.capacidad,
                    color=conexion.color
                )
            else:
                print(f"Conexión ignorada: {conexion.origen} -> {conexion.destino} (nodo faltante)")
        
        # Verificación del grafo
        print("Nodos en construir_grafo:", G.nodes(data=True))
        print("Aristas en construir_grafo:", G.edges(data=True))
        
        return G

    #VISUALIZAR RED:
    def visualizar_red(self):
        """
        Visualiza la red de acueducto utilizando NetworkX.
        Los nodos se organizan por barrios, agrupándolos visualmente.
        """
        G = self.construir_grafo()
        nodos_no_conectados = self.obtener_nodos_no_conectados()
        
        # Agrupar nodos por barrio
        barrios = {}
        for casa in self.casa.values():
            barrios.setdefault(casa.barrio, []).append(casa.nombre)
        for tanque in self.tanques.values():
            barrios.setdefault(tanque.barrio, []).append(tanque.id_tanque)
        
        # Crear un layout personalizado por barrio
        pos = {}
        offset_x, offset_y = 0, 0  # Desplazamiento inicial
        spacing = 3  # Espaciado entre grupos de barrios
        for i, (barrio, nodos) in enumerate(barrios.items()):
            barrio_pos = nx.circular_layout(G.subgraph(nodos))
            for nodo, (x, y) in barrio_pos.items():
                pos[nodo] = (x + offset_x, y + offset_y)
            offset_x += spacing
            offset_y += spacing
        edge_colors = [data['color'] for _, _, data in G.edges(data=True)]
        edge_labels = {
            (u, v): f"{data['capacity']:.1f}"
            for u, v, data in G.edges(data=True)
        }
        node_labels = {}
        node_colors = []
        node_edge_colors = []
        for casa in self.casa.values():
            suministro_total = sum(
                conexion.capacidad
                for conexion in self.conexiones
                if conexion.destino == casa.nombre
            )
            excedente = max(suministro_total - casa.demanda, 0)
            node_labels[casa.nombre] = (
                f"{casa.nombre}\n"
                f"Demanda: {casa.demanda:.1f}\n"
                f"Suministro: {suministro_total:.1f}\n"
                f"Excedente: {excedente:.1f}"
            )
            if suministro_total >= casa.demanda:
                node_colors.append("green")
            else:
                node_colors.append("yellow")
            node_edge_colors.append(self.barrios_permitidos.get(casa.barrio, "black"))
        
        for tanque in self.tanques.values():
            capacidad_disponible = tanque.nivel_actual - sum(
                conexion.capacidad
                for conexion in self.conexiones
                if conexion.origen == tanque.id_tanque
            )
            node_labels[tanque.id_tanque] = (
                f"{tanque.id_tanque}\nCapacidad restante: {capacidad_disponible:.1f}"
            )
            if capacidad_disponible <= 0:
                node_colors.append("red")
            elif capacidad_disponible <= 0.2 * tanque.capacidad:
                node_colors.append("orange")
            else:
                node_colors.append("green")
            node_edge_colors.append(self.barrios_permitidos.get(tanque.barrio, "black"))
        
        # Crear la figura para Streamlit
        fig, ax = plt.subplots(figsize=(12, 8))
        nx.draw(
            G,
            pos,
            with_labels=False,
            edge_color=edge_colors,
            node_color=node_colors,
            node_size=500,
            font_size=10,
            font_color="black",
            linewidths=2,
            ax=ax
        )
        nx.draw_networkx_edges(
            G,
            pos,
            edge_color=edge_colors,
            width=0.8,
            ax=ax
        )
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, ax=ax)
        nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=9, ax=ax)
        nx.draw_networkx_nodes(
            G,
            pos,
            node_color=node_colors,
            edgecolors=node_edge_colors,
            node_size=500,
            linewidths=2,
            ax=ax
        )
        
        # Mostrar el gráfico en Streamlit
        st.pyplot(fig)

    #MOSTRAR HISTORIAL:
    def mostrar_historial(self):
        """
        Función para mostrar el contenido del archivo historial.json.
        """
        historial_path = 'data/historial.json'
        # Verificar si el archivo existe
        if not os.path.exists(historial_path):
            return "El archivo 'historial.json' no existe."
        
        try:
            # Leer el contenido del archivo con codificación UTF-8
            with open(historial_path, 'r', encoding='utf-8') as file:
                contenido = file.read().strip()  # Leer el contenido y eliminar espacios en blanco
                # Verificar si el archivo está vacío
                if not contenido:
                    return "El historial está vacío."
                # Intentar cargar el contenido como JSON
                historial = json.loads(contenido)
                # Verificar si el historial es una lista válida
                if not isinstance(historial, list):
                    return "El contenido del historial no es una lista válida."
                if not historial:
                    return "El historial está vacío."
                else:
                    return "\n".join([f"{i + 1}. {entrada}" for i, entrada in enumerate(historial)])
        except json.JSONDecodeError:
            return "Error al leer el archivo 'historial.json'. Asegúrate de que el archivo tiene formato JSON válido."

    #AGREGAR BARRIO:
    def agregar_barrio(self, nombre, color):
        if nombre in self.barrios_permitidos:
            raise ValueError(f"El barrio '{nombre}' ya existe.")
        if color in self.barrios_permitidos.values():
            raise ValueError(f"El color '{color}' ya está en uso.")
        self.barrios_permitidos[nombre] = color
        print(f"Barrio '{nombre}' agregado con el color '{color}'.")

    #ELIMINAR BARRIO:
    def eliminar_barrio(self, nombre):
        if nombre not in self.barrios_permitidos:
            raise ValueError(f"El barrio '{nombre}' no existe.")
        del self.barrios_permitidos[nombre]
        # Actualizar casas que pertenecen a este barrio
        for casa in self.casa.values():
            if casa.barrio == nombre:
                casa.barrio = None  # O reasignar a un barrio predeterminado
        print(f"Barrio '{nombre}' eliminado.")

    #ENLISTAR BARRIOS:
    def listar_barrios(self):
        print("Barrios permitidos:", ", ".join(self.barrios_permitidos))

    # AGREGAR CASA
    def agregar_casa(self, nombre, demanda, barrio):
        """
        Agrega una casa a la red.
        :param nombre: Nombre de la casa.
        :param demanda: Demanda de agua de la casa.
        :param barrio: Barrio al que pertenece la casa.
        """
        if not barrio:
            print(f"Error: La casa '{nombre}' debe tener un barrio asignado.")
            return
        if nombre in self.casa:
            print(f"Error: La casa '{nombre}' ya existe.")
            return
        self.casa[nombre] = Casa(nombre=nombre, demanda=demanda, barrio= barrio)
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
        conexiones_eliminadas = len(self.conexiones)
        self.conexiones = [c for c in self.conexiones if c.origen != nombre and c.destino != nombre]
        conexiones_eliminadas -= len(self.conexiones)
        del self.casa[nombre]
        print(f"Casa '{nombre}' eliminada con éxito junto con {conexiones_eliminadas} conexiones asociadas.")

    # AGREGAR TANQUE
    def agregar_tanque(self, id_tanque, capacidad, nivel_actual, barrio = None):
        """
        Agrega un tanque a la red.
        :param id_tanque: ID del tanque.
        :param capacidad: Capacidad máxima del tanque.
        :param nivel_actual: Nivel actual del tanque.
        :param barrio: Barrio al que pertenece el tanque.
        """
        if not barrio:
            print(f"Error: El tanque '{id_tanque}' debe tener un barrio asignado.")
            return
        if id_tanque in self.tanques:
            print(f"Error: El tanque '{id_tanque}' ya existe.")
            return
        self.tanques[id_tanque] = Tanque(id_tanque=id_tanque, capacidad=capacidad, nivel_actual=nivel_actual, barrio = barrio)
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
        conexiones_eliminadas = len(self.conexiones)
        self.conexiones = [c for c in self.conexiones if c.origen != id_tanque and c.destino != id_tanque]
        conexiones_eliminadas -= len(self.conexiones)
        del self.tanques[id_tanque]
        print(f"Tanque '{id_tanque}' eliminado con éxito junto con {conexiones_eliminadas} conexiones asociadas.")

    #AGREGAR CONEXIÓN:
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

    #ELIMINAR CONEXIÓN:
    def eliminar_conexion(self, origen, destino):
        # Buscar la conexión y eliminarla
        conexion_a_eliminar = None
        for conexion in self.conexiones:
            if conexion.origen == origen and conexion.destino == destino:
                conexion_a_eliminar = conexion
                break
        
        if conexion_a_eliminar:
            self.conexiones.remove(conexion_a_eliminar)
        else:
            raise ValueError(f"La conexión entre {origen} y {destino} no existe en la red.")

    #SIMULAR OBSTRUCCCIONES:
    def simular_obstruccion(self, origen, destino, nivel_gravedad):
        """
        Simula obstrucciones en conexiones. Permite la entrada manual o automática si se proporcionan argumentos.
        """
        # Verificar que los valores no sean vacíos
        if not origen or not destino or nivel_gravedad is None:
            raise ValueError("Debe ingresar origen, destino y nivel de gravedad")
        # Buscar la conexión
        conexion_encontrada = False
        for conexion in self.conexiones:
            if conexion.origen == origen and conexion.destino == destino:
                conexion_encontrada = True
                nueva_capacidad = conexion.capacidad * (1.0 - nivel_gravedad)
                conexion.capacidad = max(nueva_capacidad, 0)
                # Cambiar el color según el nivel de gravedad
                if nivel_gravedad == 0.0:
                    conexion.color = "blue"
                elif nivel_gravedad <= 0.33:
                    conexion.color = "yellow"
                elif nivel_gravedad <= 0.66:
                    conexion.color = "orange"
                else:
                    conexion.color = "red"
                break
        if not conexion_encontrada:
            raise ValueError(f"No se encontró la conexión de '{origen}' a '{destino}' para simular la obstrucción.")

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
        """
        G = self.construir_grafo()
        pos = nx.spring_layout(G)
        
        edge_colors = [data.get('color', 'black') for _, _, data in G.edges(data=True)]
        node_colors = ["lightblue" if "Casa" in node else "green" for node in G.nodes()]
        
        # Dibujar el grafo base
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
            if len(ruta) > 1:
                ruta_aristas = [(ruta[i], ruta[i + 1]) for i in range(len(ruta) - 1)]
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
                origen = casas_afectadas[0] if casas_afectadas else None
                destino = casas_afectadas[1] if len(casas_afectadas) > 1 else None

                ruta = self.encontrar_ruta_alternativa(origen=tanque, destino=casa)
                if ruta:
                    # Imprimir la ruta encontrada solo para la primera casa afectada
                    st.write(f"Ruta alternativa para la casa '{casa}' desde el tanque '{tanque}': {ruta}")
                    rutas.append(ruta)
                    break  # Salir del bucle si se encuentra una ruta válida
                    
        # Visualizar las rutas encontradas
        if rutas:
            self.visualizar_rutas_alternativas(rutas)
        else:
            st.error("No se encontraron rutas alternativas.")

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

    #ACTUALIZAR VALORES:
    def actualizar_valores(self, tipo, identificador, **nuevos_valores):
        """
        Actualiza los valores de una casa, tanque o conexión en la red.
        Parámetros:
        - tipo (str): Tipo del objeto a actualizar ('Casa', 'Tanque', 'Conexion').
        - identificador (str): Identificador del objeto.
        - nuevos_valores (dict): Valores nuevos a asignar.
        Retorna:
        - bool: True si la actualización fue exitosa, False en caso contrario.
        """
        print(f"Tipo de objeto: {tipo}, Identificador: {identificador}, Nuevos valores: {nuevos_valores}")
        
        # Actualización de Casa
        if tipo == "Casa":
            if identificador in self.casa:
                casa = self.casa[identificador]
                
                if "nombre" in nuevos_valores:
                    print(f"No se permite cambiar el nombre de la casa '{identificador}'.")
                
                if "demanda" in nuevos_valores:
                    casa.demanda = nuevos_valores["demanda"]
                    print(f"Casa '{identificador}' actualizada: demanda={casa.demanda}")
                
                if "barrio" in nuevos_valores:
                    nuevo_barrio = nuevos_valores["barrio"]
                    if nuevo_barrio not in self.barrios_permitidos:
                        print(f"Error: El barrio '{nuevo_barrio}' no está permitido.")
                        return False
                    casa.barrio = nuevo_barrio
                    print(f"Casa '{identificador}' actualizada: barrio={casa.barrio}")
                
                # Guardar cambios en JSON
                self.guardar_a_json('data/red_acueducto.json')
                return True
            else:
                print(f"Error: La casa '{identificador}' no existe.")
        
        # Actualización de Tanque
        elif tipo == "Tanque":
            if identificador in self.tanques:
                tanque = self.tanques[identificador]
                
                if "capacidad" in nuevos_valores:
                    tanque.capacidad = nuevos_valores["capacidad"]
                
                if "nivel_actual" in nuevos_valores:
                    tanque.nivel_actual = nuevos_valores["nivel_actual"]
                
                if "barrio" in nuevos_valores:
                    nuevo_barrio = nuevos_valores["barrio"]
                    if nuevo_barrio not in self.barrios_permitidos:
                        print(f"Error: El barrio '{nuevo_barrio}' no está permitido.")
                        return False
                    tanque.barrio = nuevo_barrio
                
                # Guardar cambios en JSON
                self.guardar_a_json('data/red_acueducto.json')
                print(f"Tanque '{identificador}' actualizado: capacidad={tanque.capacidad}, nivel_actual={tanque.nivel_actual}, barrio={tanque.barrio}")
                return True
            else:
                print(f"Error: El tanque '{identificador}' no existe.")
        
        # Actualización de Conexión
        elif tipo == "Conexion":
            # Revisar si la conexión existe
            conexion_encontrada = None
            for conexion in self.conexiones:
                if conexion.origen == identificador[0] and conexion.destino == identificador[1]:
                    conexion_encontrada = conexion
                    break
            
            if conexion_encontrada:
                print(f"Conexión encontrada: {conexion_encontrada}")
                
                # Actualizar los valores de la conexión
                if "capacidad" in nuevos_valores:
                    conexion_encontrada.capacidad = nuevos_valores["capacidad"]
                    print(f"Conexión actualizada: capacidad={conexion_encontrada.capacidad}")
                
                if "color" in nuevos_valores:
                    conexion_encontrada.color = nuevos_valores["color"]
                    print(f"Conexión actualizada: color={conexion_encontrada.color}")
                
                # Guardar cambios en JSON
                self.guardar_a_json('data/red_acueducto.json')
                return True
            else:
                print(f"Error: No se encontró la conexión '{identificador}'.")
                return False
        
        else:
            print(f"Error: Tipo '{tipo}' no reconocido. Use 'Casa', 'Tanque' o 'Conexion'.")
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

    #IDENTIFICAR POSICIONES OPTIMAS:
    def identificar_posiciones_optimas(self, casas, tanques, conexiones, barrios_permitidos, umbral_demanda=50):
        """
        Identifica posiciones óptimas para nuevos tanques en áreas sin cobertura.
        Args:
            casas (list): Lista de casas con su información.
            tanques (list): Lista de tanques con su información.
            conexiones (list): Lista de conexiones existentes.
            barrios_permitidos (dict): Barrios y sus colores (identificación).
            umbral_demanda (float): Umbral mínimo de demanda en un barrio para considerar un nuevo tanque.
        Returns:
            list: Posiciones sugeridas para nuevos tanques.
        """
        # Crear un grafo de la red
        G = nx.Graph()
        # Agregar casas y tanques como nodos
        for casa in casas:
            G.add_node(casa["nombre"], tipo="casa", barrio=casa["barrio"], demanda=casa["demanda"])
        for tanque in tanques:
            G.add_node(tanque["id"], tipo="tanque", barrio=tanque["barrio"], capacidad=tanque["capacidad"])
        # Agregar conexiones como aristas
        for conexion in conexiones:
            G.add_edge(conexion["origen"], conexion["destino"], capacidad=conexion["capacidad"])
        # Identificar nodos sin servicio o con déficit hídrico
        nodos_sin_servicio = []
        for casa in casas:
            casa_nombre = casa["nombre"]
            suministro_total = sum(
                G.edges[edge]["capacidad"] for edge in G.edges(casa_nombre) if "capacidad" in G.edges[edge]
            )
            if suministro_total < casa["demanda"]:
                nodos_sin_servicio.append(casa_nombre)
        # Evaluar barrios por su demanda total
        demanda_por_barrio = {}
        for casa in casas:
            barrio = casa["barrio"]
            if barrio not in demanda_por_barrio:
                demanda_por_barrio[barrio] = 0
            demanda_por_barrio[barrio] += casa["demanda"]
        # Filtrar barrios prioritarios
        barrios_prioritarios = [
            barrio
            for barrio, demanda in demanda_por_barrio.items()
            if demanda >= umbral_demanda and barrio in barrios_permitidos
        ]
        # Sugerir posiciones óptimas para nuevos tanques
        posiciones_sugeridas = []
        for barrio in barrios_prioritarios:
            # Nodos en el barrio con déficit hídrico
            nodos_barrio = [n for n in nodos_sin_servicio if G.nodes[n]["barrio"] == barrio]
            if nodos_barrio:
                # Buscar punto más conectado en el barrio
                punto_optimo = max(nodos_barrio, key=lambda n: len(list(G.neighbors(n))))
                posiciones_sugeridas.append(
                    {
                        "barrio": barrio,
                        "posicion_central": punto_optimo,
                        "demanda": demanda_por_barrio[barrio],
                        "color": barrios_permitidos[barrio],
                    }
                )
        return posiciones_sugeridas
