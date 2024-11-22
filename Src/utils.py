import json
from models import Barrio, Tanque, Conexion

class RedDeAcueducto:
    def __init__(self):
        self.barrios = {}
        self.tanques = {}
        self.conexiones = []

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
                self.barrios[barrio['nombre']] = Barrio(
                    nombre=barrio['nombre'], 
                    demanda=barrio['demanda']
                )

            # Cargar tanques
            for tanque in data['tanques']:
                self.tanques[tanque['id']] = Tanque(
                    id_tanque=tanque['id'], 
                    capacidad=tanque['capacidad'], 
                    nivel_actual=tanque['nivel_actual']
                )

            # Cargar conexiones
            for conexion in data['conexiones']:
                origen = conexion['origen']
                destino = conexion['destino']
                capacidad = conexion['capacidad']

                # Verificar que el origen y destino existan
                if origen not in self.barrios and origen not in self.tanques:
                    print(f"Error: Nodo origen {origen} no definido.")
                    continue
                if destino not in self.barrios and destino not in self.tanques:
                    print(f"Error: Nodo destino {destino} no definido.")
                    continue
                
                self.conexiones.append(
                    Conexion(origen=origen, destino=destino, capacidad=capacidad)
                )
            
            print("Red cargada con éxito.")
        except Exception as e:
            print(f"Error al cargar el archivo JSON: {e}")
