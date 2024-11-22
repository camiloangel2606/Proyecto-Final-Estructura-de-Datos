class Barrio:
    def __init__(self, nombre, demanda):
        """
        Representa un barrio de la red.
        :param nombre: Nombre del barrio.
        :param demanda: Cantidad de agua que requiere el barrio.
        """
        self.nombre = nombre
        self.demanda = demanda
        self.tanques = []  # Lista de tanques que abastecen este barrio

class Tanque:
    def __init__(self, id_tanque, capacidad, nivel_actual):
        """
        Representa un tanque de almacenamiento.
        :param id_tanque: Identificador único del tanque.
        :param capacidad: Capacidad máxima del tanque.
        :param nivel_actual: Nivel actual de agua en el tanque.
        """
        self.id_tanque = id_tanque
        self.capacidad = capacidad
        self.nivel_actual = nivel_actual

class Conexion:
    def __init__(self, origen, destino, capacidad, flujo=0):
        """
        Representa una conexión entre un tanque y un barrio o tanque.
        :param origen: Nodo de origen (tanque o barrio).
        :param destino: Nodo de destino (tanque o barrio).
        :param capacidad: Capacidad máxima de la tubería.
        :param flujo: Flujo actual a través de la tubería.
        """
        self.origen = origen
        self.destino = destino
        self.capacidad = capacidad
        self.flujo = flujo
