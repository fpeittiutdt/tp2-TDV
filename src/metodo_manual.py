import json
import networkx as nx
import matplotlib.pyplot as plt
import math

BIG_NUMBER = 1e10


def process_services(data):
    # Inicializar variables
    events = []
    stations = data["stations"]
    services = data["services"]
    stock = {}
    new_units = {}

    # Crear contadores de stock y nuevas unidades para cada estación
    for station in stations:
        stock[station] = 0
        new_units[station] = 0

    # Generar una lista de eventos en orden creciente de tiempo
    for service_id, service in services.items():
        demand = service["demand"][0]
        for stop in service["stops"]:
            events.append((stop["time"], stop["station"], stop["type"], demand))

    events.sort()

    # Procesar cada evento
    for event in events:
        time, station, event_type, demand = event

        minimum_units = math.ceil(demand / data["rs_info"]["capacity"])

        if event_type == "A":  # Arribo
            stock[station] += minimum_units
            # Incrementar el stock con las unidades que arriban
        elif event_type == "D":  # Partida
            if stock[station] >= minimum_units:  # Si hay suficiente stock
                stock[
                    station
                ] -= minimum_units  # Se cubre la demanda con el stock disponible
            else:  # Si no hay suficiente stock
                new_units[station] += (
                    minimum_units - stock[station]
                )  # Incrementar las unidades nuevas necesarias
                stock[station] = 0  # Todo el stock se utiliza

    # Resultado final
    result = {"initial_units_needed": new_units, "final_stock": stock}

    return result


filename = "instances/toy_instance.json"
filename = "instances/retiro-tigre-semana.json"

with open(filename) as json_file:
    data = json.load(json_file)

result = process_services(data)
print(result)
