import csv
import json
import copy
import random

instance = {}
instance["services"] = {}
instance["stations"] = ["Once", "Moreno"]
instance["cost_per_unit"] = {"Once": 1.0, "Moreno": 1.0}

filename = "instances/stop_times"
# Open the CSV file in read mode
dict_tiempos = {}


def hora_a_minutos(lista_tiempos):
    res = []
    for tiempo in lista_tiempos:
        lista_tiempos_separada = tiempo.split(":")
        tiempo_en_minutos = int(lista_tiempos_separada[0]) * 60 + int(
            lista_tiempos_separada[1]
        )
        res.append(tiempo_en_minutos)
    return res


with open(filename + ".csv", "r") as csvfile:
    # Create a CSV reader object
    csvreader = csv.reader(csvfile)
    next(csvreader)

    # Loop through each row in the CSV file
    lista_tiempos = [None, None, 0]
    anterior = [None, None]
    i = 0
    cant_viajes_intermedios = 0
    for row in csvreader:

        if lista_tiempos[0] is None:
            lista_tiempos[0] = row[1]
            cant_viajes_intermedios += 1

        elif row[0] != anterior[0]:
            lista_tiempos[1] = anterior[1]
            lista_tiempos_modificada = hora_a_minutos(lista_tiempos[:2].copy())
            lista_tiempos_modificada.append(lista_tiempos[2])
            dict_tiempos[int(anterior[0])] = lista_tiempos_modificada.copy()
            lista_tiempos = [row[1], None, cant_viajes_intermedios]
            i += 1
            cant_viajes_intermedios = 0

        else:
            cant_viajes_intermedios += 1

        anterior = [row[0], row[1]]

print(dict_tiempos)
filename2 = "instances/trips"
# Open the CSV file in read mode
with open(filename2 + ".csv", "r", encoding="utf-8") as file:
    # Create a CSV reader object
    csvreader = csv.reader(file)
    next(csvreader)

    # Loop through each row in the CSV file
    datos_ida_y_vuelta = {}
    ida = None
    vuelta = None
    service_id = (None, None)
    datos_ida = None
    datos_vuelta = None

    rows = list(csvreader)
    for row_pos in range(0, len(rows)-1, 2):
        # Each row is a list of values, you can access them by index
        # print(row)
        datos_ida = (rows[row_pos][3], int(rows[row_pos][2]))
        datos_vuelta = (rows[row_pos+1][3], int(rows[row_pos+1][2]))

        datos_ida_y_vuelta = {
            "ida": {
                "name": datos_ida[0],
                "id": datos_ida[1]
            },
            "vuelta": {
                "name": datos_vuelta[0],
                "id": datos_vuelta[1]
            }
        }

        if (datos_ida_y_vuelta["ida"]["name"] == "Once" or datos_ida_y_vuelta["ida"]["name"] == "Once (RÁPIDO)") and (datos_ida_y_vuelta["vuelta"]["name"] == "Moreno" or datos_ida_y_vuelta["vuelta"]["name"] == "Moreno (RÁPIDO)"):
            vuelta = "Moreno"
            ida = "Once"
        
            service_id = (datos_ida_y_vuelta["ida"]["id"], datos_ida_y_vuelta["vuelta"]["id"])
            
            if dict_tiempos[service_id[0]][2] >= 15 and dict_tiempos[service_id[1]][2] >= 15:
                    
                    instance["services"][service_id[0]] = {}
                    dep = {
                        "time": dict_tiempos[service_id[0]][0],
                        "station": ida,
                        "type": "D",
                    }
                    arr = {
                        "time": dict_tiempos[service_id[0]][1],
                        "station": vuelta,
                        "type": "A",
                    }
                    instance["services"][service_id[0]]["stops"] = copy.deepcopy(
                        [dep, arr]
                    )
                    instance["services"][service_id[0]]["demand"] = [
                        random.randint(100, 700)
                    ]
                    

                    instance["services"][service_id[1]] = {}
                    dep = {
                        "time": dict_tiempos[service_id[1]][0],
                        "station": vuelta,
                        "type": "D",
                    }
                    arr = {
                        "time": dict_tiempos[service_id[1]][1],
                        "station": ida,
                        "type": "A",
                    }
                    instance["services"][service_id[1]]["stops"] = copy.deepcopy(
                        [dep, arr]
                    )
                    instance["services"][service_id[1]]["demand"] = [
                        random.randint(100, 700)
                    ]
            datos_ida_y_vuelta = {}
            datos_ida = None
            datos_vuelta = None


# instance['rs_info'] = {'capacity': 100, 'max_rs': 6}
instance["rs_info"] = {"capacity": 100, "max_rs": 50}
# pprint.pprint(instance)

filename3 = "moreno-once"

with open(filename3 + ".json", "w") as json_file:
    json.dump(instance, json_file)
