import json
import networkx as nx
import matplotlib.pyplot as plt
import math
from helpers.constants import *

def process_services(data):

    """
    Construye la solución utilizando el metodo manual mencionado en el informe.
    
    Parámetros:
    instance (dict): Un diccionario que contiene la información de la instancia.

    Retorna:

    """

    events = []
    stations = data["stations"]
    services = data[SERVICES]
    stock = {}
    new_units = {}

    # Creamos contadores de stock y nuevas unidades para cada estación de cabecera
    for station in stations:
        stock[station] = 0
        new_units[station] = 0

    # Generamos una lista de eventos en orden creciente de tiempo
    for service_id, service in services.items():
        demand = service[DEMAND][0]
        for stop in service[STOPS]:
            events.append((stop[TIME], stop[STATION], stop["type"], demand))

    events.sort()

    # Analizamos cada servicio

    for event in events:
        time, station, event_type, demand = event

        minimum_units = math.ceil(demand / data[RS_INFO][CAPACITY])

        # Si el servicio es una llegada entonces se almacenan las unidades en la estación.
        if event_type == "A":
            stock[station] += minimum_units

        # Si el servicio es una salida entonces se trata de cubrir la demanda con el stock disponible.
        # Si el stock no es suficiente entonces se utiliza nuevo stock.
        # En todo caso el stock en dicha estación disminuye hasta que la demanda sea cubierta
        elif event_type == "D":

            if stock[station] >= minimum_units:
                stock[
                    station
                ] -= minimum_units
            
            else:
                new_units[station] += (
                    minimum_units - stock[station]
                )
                stock[station] = 0

    # Determinamos la cantidad de stock necesario para cubrir todas las demandas.
    # initial_units_needed: stock necesario en cada estación de cabecera al inicio del día
    # final_stock: el stock en cada estación al final del día
    # si initial_units_needed es distinto de final_stock entonces es necesario hacer servicios
    # durante la noche para reubicar las unidades.

    result = {"initial_units_needed": new_units, "final_stock": stock}

    return result


# Instancias disponibles
#filename = "instances/toy_instance.json"
filename = "instances/retiro-tigre-semana.json"

# Lectura de una instancia dada en formato json.
with open(filename) as json_file:
    data = json.load(json_file)

# Ejecutar el metodo y obtener el resultado
result = process_services(data)
print(result)
