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
        self.nivel_actual = nivel_actual  # Agregado para mantener consistencia con los parámetros

class Conexion:
    def __init__(self, origen, destino, capacidad, flujo=0, color="blue", nivel_gravedad=0):
        """
        Representa una conexión entre un tanque y una casa o tanque.
        :param origen: Nodo de origen (tanque o casa).
        :param destino: Nodo de destino (tanque o casa).
        :param capacidad: Capacidad máxima de la tubería.
        :param flujo: Flujo actual a través de la tubería.
        :param color: Color que representa el estado de la conexión.
        :param nivel_gravedad: Nivel de obstrucción en la conexión (0.0 a 1.0).
        """
        self.origen = origen
        self.destino = destino
        self.capacidad = capacidad
        self.flujo = flujo
        self.color = color
        self.nivel_gravedad = nivel_gravedad
