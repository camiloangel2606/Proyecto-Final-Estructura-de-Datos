class Casa:
    def __init__(self, nombre, demanda):
        """
        Representa una casa de la red.
        :param nombre: Nombre de la casa.
        :param demanda: Cantidad de agua que requiere la casa.
        """
        self.nombre = nombre
        self.demanda = demanda

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
    def __init__(self, origen, destino, capacidad, flujo=0, color = "blue"):
        """
        Representa una conexión entre un tanque y un casa o tanque.
        :param origen: Nodo de origen (tanque o casa).
        :param destino: Nodo de destino (tanque o casa).
        :param capacidad: Capacidad máxima de la tubería.
        :param flujo: Flujo actual a través de la tubería.
        """
        self.origen = origen
        self.destino = destino
        self.capacidad = capacidad
        self.flujo = flujo
        self.color = color  # Color por defecto (sin obstrucción)
