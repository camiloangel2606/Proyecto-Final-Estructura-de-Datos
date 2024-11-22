import json
from models import Barrio, Tanque, Conexion

class RedDeAcueducto:
    def __init__(self):
        self.barrios = {}
        self.tanques = {}
        self.conexiones = []
    #CARGAR ARCHIVOS JSON
    def cargar_desde_json(self, archivo_json):
        """
        Carga la red desde un archivo JSON.
        :param archivo_json: Ruta del archivo JSON.
        """
        try:
            with open(archivo_json, 'r') as file:
                data = json.load(file)
            
            # Cargar barrios
            for barrio in data['barrios']:
                self.agregar_barrio(
                    nombre=barrio['nombre'], 
                    demanda=barrio['demanda']
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
            
    #GUARDAR ARCHIVO JSON
    def guardar_a_json(self, archivo_json):
        """
        Guarda la red en un archivo JSON.
        :param archivo_json: Ruta del archivo JSON donde se guardará la red.
        """
        try:
            # Crear el diccionario que representa la red
            data = {
                "barrios": [
                    {
                        "nombre": barrio.nombre,
                        "demanda": barrio.demanda
                    } for barrio in self.barrios.values()
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

    #CONEXIONES CON NODOS NO DEFINIDOS:
    #Esto verifica que todas las conexiones tengan un origen y un destino válidos,
    # es decir, que existan en la red de barrios o tanques.
    def verificar_nodos_no_definidos(self):
        errores = []
        for conexion in self.conexiones:
            if conexion.origen not in self.barrios and conexion.origen not in self.tanques:
                errores.append(f"Error: Nodo origen '{conexion.origen}' no está definido.")
            if conexion.destino not in self.barrios and conexion.destino not in self.tanques:
                errores.append(f"Error: Nodo destino '{conexion.destino}' no está definido.")
        return errores

    #CONEXIONES DUPLICADAS:
    #Esto verifica si existen varias conexiones con el mismo origen y destino, lo cual es redundante.
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

    #BUCLES EN EL FLUJO:
    #Esto verifica si existen ciclos en la red de conexiones (por ejemplo, un tanque que vuelve a abastecerse
    # a sí mismo a través de otros barrios).Para identificar bucles, puedes usar algoritmos de detección de ciclos
    # como DFS (Depth First Search) en un grafo dirigido.
    def detectar_bucles(self):
        def dfs(nodo, visitados, stack, camino):
            visitados.add(nodo)
            stack.add(nodo)
            camino.append(nodo)  # Registrar el camino actual
            for conexion in self.conexiones:
                if conexion.origen == nodo:
                    siguiente = conexion.destino
                    if siguiente not in visitados:
                        if dfs(siguiente, visitados, stack, camino):
                            return True, camino
                    elif siguiente in stack:
                        # Encontramos un bucle; extraer los nodos involucrados
                        indice_ciclo = camino.index(siguiente)
                        return True, camino[indice_ciclo:]  # Retornar sólo el ciclo
            stack.remove(nodo)
            camino.pop()  # Remover el nodo al retroceder
            return False, []
        visitados = set()
        for nodo in list(self.barrios.keys()) + list(self.tanques.keys()):
            if nodo not in visitados:
                ciclo, nodos_ciclo = dfs(nodo, visitados, set(), [])
                if ciclo:
                    return True, nodos_ciclo
        return False, []

    #VALIDAR DURANTE LA CARGA:
    def verificar_consistencia(self):
        errores = []
        # Verificar nodos no definidos
        errores.extend(self.verificar_nodos_no_definidos())
        # Verificar conexiones duplicadas
        errores.extend(self.verificar_conexiones_duplicadas())
        # Verificar bucles en el flujo
        ciclo, nodos_ciclo = self.detectar_bucles()
        if ciclo:
            errores.append(f"Error: Se detectó un bucle en la red que involucra los nodos: {', '.join(nodos_ciclo)}")
        if errores:
            print("Errores detectados durante la verificación de la red:")
            for error in errores:
                print(f" - {error}")
        else:
            print("La red está consistente.")


    #AGREGAR BARRIO
    def agregar_barrio(self, nombre, demanda):
        """
        Agrega un barrio a la red.
        :param nombre: Nombre del barrio.
        :param demanda: Demanda de agua del barrio.
        """
        if nombre in self.barrios:
            print(f"Error: El barrio '{nombre}' ya existe.")
            return
        self.barrios[nombre] = Barrio(nombre=nombre, demanda=demanda)
        print(f"Barrio '{nombre}' agregado con éxito.")
    
    #ELIMINAR BARRIO
    def eliminar_barrio(self, nombre):
        """
        Elimina un barrio de la red.
        :param nombre: Nombre del barrio.
        """
        if nombre not in self.barrios:
            print(f"Error: El barrio '{nombre}' no existe.")
            return
        # Eliminar conexiones relacionadas con el barrio
        self.conexiones = [c for c in self.conexiones if c.origen != nombre and c.destino != nombre]
        del self.barrios[nombre]
        print(f"Barrio '{nombre}' eliminado con éxito.")
    
    #AGREGAR TANQUE
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
    
    #ELIMINAR TANQUE
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
    
    #AGREGAR CONEXION
    def agregar_conexion(self, origen, destino, capacidad):
        """
        Agrega una conexión a la red.
        :param origen: Nodo de origen (barrio o tanque).
        :param destino: Nodo de destino (barrio o tanque).
        :param capacidad: Capacidad de la conexión.
        """
        if origen not in self.barrios and origen not in self.tanques:
            print(f"Error: Nodo origen '{origen}' no definido.")
            return
        if destino not in self.barrios and destino not in self.tanques:
            print(f"Error: Nodo destino '{destino}' no definido.")
            return
        if any(c.origen == origen and c.destino == destino for c in self.conexiones):
            print(f"Error: La conexión de '{origen}' a '{destino}' ya existe.")
            return
        self.conexiones.append(Conexion(origen=origen, destino=destino, capacidad=capacidad))
        print(f"Conexión de '{origen}' a '{destino}' agregada con éxito.")
    
    #ELIMINAR CONEXION
    def eliminar_conexion(self, origen, destino):
        """
        Elimina una conexión de la red.
        :param origen: Nodo de origen.
        :param destino: Nodo de destino.
        """
        for conexion in self.conexiones:
            if conexion.origen == origen and conexion.destino == destino:
                self.conexiones.remove(conexion)
                print(f"Conexión de '{origen}' a '{destino}' eliminada con éxito.")
                return
        print(f"Error: La conexión de '{origen}' a '{destino}' no existe.")
