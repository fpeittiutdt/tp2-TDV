import json
import networkx as nx
import matplotlib.pyplot as plt
import math
from helpers.constants import *


def manual_method(data):
    """
    Construye la solución utilizando el método manual que se utilizaba en la compañía (ver enunciado).

    Parámetros:
    instance: Un diccionario que contiene la información de la instancia.

    Devuelve: los contadores de stock y unidades nuevas para definir cuántas unidades se asignarán a cada cabecera.
    """

    events = []
    stations = data["stations"]
    services = data[SERVICES]
    stock = {}
    new_units = {}

    # Creamos contadores de stock y unidades nuevas para cada cabecera
    for station in stations:
        stock[station] = 0
        new_units[station] = 0

    # Generamos una lista de eventos en orden creciente de tiempo
    for service_id, service in services.items():
        demand = service[DEMAND][0]
        for stop in service[STOPS]:
            events.append((stop[TIME], stop[STATION], stop["type"], demand))

    events.sort()

    for event in events:
        time, station, event_type, demand = event

        minimum_units = math.ceil(demand / data[RS_INFO][CAPACITY])

        # Para las llegadas, se almacenan las unidades que llegan en la estación.
        if event_type == "A":
            stock[station] += minimum_units

        # Para las salidas, se trata de cubrir la demanda con el stock disponible.
        # Si el stock no es suficiente, se agregan unidades nuevas.
        elif event_type == "D":

            if stock[station] >= minimum_units:
                stock[station] -= minimum_units

            else:
                new_units[station] += minimum_units - stock[station]
                stock[station] = 0

    # Determinamos la cantidad de stock necesario para cubrir todas las demandas.
    # initial_units_needed: stock necesario en cada estación de cabecera al inicio del día
    # final_stock: el stock en cada estación al final del día
    # si initial_units_needed es distinto de final_stock entonces es necesario hacer servicios
    # durante la noche para reubicar las unidades.

    result = {"initial_units_needed": new_units, "final_stock": stock}

    return result


# Se carga la instancia
filename = "instances/retiro-tigre-semana.json"
with open(filename) as json_file:
    data = json.load(json_file)

result = manual_method(data)
print(result)
