import csv
import json
import copy
import pprint

instance = {}
instance['services'] = {}
instance['stations'] = ['Once','Moreno']
instance['cost_per_unit'] = {'Tigre' : 1.0, 'Retiro' : 1.0}

filename = 'instances/stop_times'
# Open the CSV file in read mode
dict_tiempos = {}
with open(filename + '.csv', 'r') as csvfile:
    # Create a CSV reader object
    csvreader = csv.reader(csvfile)
    next(csvreader)
    
    # Loop through each row in the CSV file
    lista_tiempos = [None, None]
    anterior = None
    limite = 10
    inicio = 32001211
    empezar = False
    i = 0
    for row in csvreader:
        if i == limite:
            break
        
        if int(row[0]) == inicio:
            empezar = True
        
        if empezar:
            if lista_tiempos[0] is None:
                lista_tiempos[0] = row[1]
            
            elif row[0] != anterior:
                lista_tiempos[1] = row[2]
                dict_tiempos[int(anterior)] = lista_tiempos.copy()
                lista_tiempos = [row[0], None]
                i += 1
            
            anterior = row[0]

print(dict_tiempos)
filename2 = 'instances/trips'
# Open the CSV file in read mode
with open(filename2 + '.csv', 'r', encoding="utf-8") as file:
    # Create a CSV reader object
    csvreader = csv.reader(file)
    next(csvreader)
    
    # Loop through each row in the CSV file
    maximo = 10
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
                llegada = "Once"
                salida = "Moreno"
            else:
                llegada = "Moreno"
                salida = "Once"

            service_id = row[2]
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