import csv, json, copy, pprint

instance = {}
instance['services'] = {}
instance['stations'] = ['Tigre','Retiro']
instance['cost_per_unit'] = {'Tigre' : 1.0, 'Retiro' : 1.0}


def save(instance):
    with open('trips.json', 'w', encoding='utf-8') as json_file:
        json.dump(instance, json_file)


if __name__ == '__main__':
    
    instance = {}
    # Open the CSV file in read mode
    with open('trips.csv', 'r', encoding='utf-8') as csvfile:
        # Create a CSV reader object
        csvreader = csv.reader(csvfile)
        next(csvreader)
        
        # Loop through each row in the CSV file
        for row in csvreader:
            print(row)
            # Each row is a list of values, you can access them by index
            #print(row)
            route_id = row[0]
            service_id = row[1]
            trip_id = row[2]
            trip_headsign = row[3]
            trip_short_name = row[4]
            direction_id = row[5]
            shape_id = row[6]
            
            if trip_id not in instance:
                t_from = { "station": None, "type": "D" }
                
                t_to = {
                    "station": trip_headsign,
                    "type":	"A"
                }

                instance[trip_id] = {
                    "stops": [t_from, t_to],
                    "demand": [500]
                }
                
    with open('stop_times.csv', 'r', encoding='utf-8') as csvfile:
        # Create a CSV reader object
        csvreader = csv.reader(csvfile)
        next(csvreader)
        
        # Loop through each row in the CSV file
        
        last_trip = { 'id': None }
        
        for row in csvreader:
            # Each row is a list of values, you can access them by index
            #print(row)
            trip_id = row[0]
            arrival_time = row[1]
            departure_time = row[2]
            stop_id = row[3]
            stop_sequence = row[4]
            shape_dist_traveled = row[5]
            
            if trip_id in instance:
                if last_trip['id'] != trip_id:
                    instance[trip_id]['stops'][0]['time'] = arrival_time # Marco salida del tren para este id de recorrido
                    
                    if last_trip['id'] is not None:
                        instance[last_trip['id']]['stops'][1]['time'] = last_trip['arrival_time'] # Marco llegada del último recorrido
                    
                last_trip['id'] = trip_id
                last_trip['arrival_time'] = arrival_time
                # Si es un nuevo trip ponerle el nombre

    save(instance)

    #instance['rs_info'] = {'capacity': 100, 'max_rs': 6}
    #instance['rs_info'] = {'capacity': 100, 'max_rs': 25}
