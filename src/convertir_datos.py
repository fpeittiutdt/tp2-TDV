import csv
import json
import copy
import pprint

instance = {}
instance['services'] = {}
instance['stations'] = ['Once','Moreno']
instance['cost_per_unit'] = {'Once' : 1.0, 'Moreno' : 1.0}

filename = 'instances/stop_times'
# Open the CSV file in read mode
dict_tiempos = {}

def hora_a_minutos(lista_tiempos):
    res = []
    for tiempo in lista_tiempos:
        lista_tiempos_separada = tiempo.split(":")
        tiempo_en_minutos = int(lista_tiempos_separada[0]) * 60 + int(lista_tiempos_separada[1])
        res.append(tiempo_en_minutos)
    return res


with open(filename + '.csv', 'r') as csvfile:
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
filename2 = 'instances/trips'
# Open the CSV file in read mode
with open(filename2 + '.csv', 'r', encoding="utf-8") as file:
    # Create a CSV reader object
    csvreader = csv.reader(file)
    next(csvreader)
    
    # Loop through each row in the CSV file
    maximo = 500
    i = 0
    llegada = None
    salida = None
    for row in csvreader:
        # Each row is a list of values, you can access them by index
        #print(row)
        if i == maximo:
            break
        else:
            if row[3] == "Moreno" or row[3] == "Moreno (RÁPIDO)":
                llegada = "Moreno"
                salida = "Once"
            elif row[3] == "Once" or row[3] == "Once (RÁPIDO)":
                llegada = "Once"
                salida = "Moreno"
            if row[3] == "Moreno" or row[3] == "Moreno (RÁPIDO)" or row[3] == "Once" or row[3] == "Once (RÁPIDO)":
                
                service_id = row[2]
                
                if dict_tiempos[int(service_id)][2] >= 15:
                    instance['services'][service_id] = {}
                    dep = {'time': dict_tiempos[int(service_id)][0], 'station':salida, 'type':"D"}
                    arr = {'time': dict_tiempos[int(service_id)][1], 'station':llegada, 'type':"A"}
                    instance['services'][service_id]['stops'] = copy.deepcopy([dep,arr])
                    instance['services'][service_id]['demand'] = [500]
                    i += 1



instance['rs_info'] = {'capacity': 100, 'max_rs': 6}
instance['rs_info'] = {'capacity': 100, 'max_rs': 25}
#pprint.pprint(instance)

filename3 = "datos_en_json"

with open(filename3 + '.json', 'w') as json_file:
    json.dump(instance, json_file)