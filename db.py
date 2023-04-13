class VehicleStore:
    vehicles = []

    def __init__(self):
        # Read the CSV file, each line goes - key1=value1,key2=value2
        with open('data.csv', 'r') as f:
            for line in f.readlines():
                line = line.strip()
                data = {}
                attributes = line.split(',')
                for a in attributes:
                    key, value = a.split('=')
                    data[key] = value
                self.vehicles.append(data)

    def add_vehicle(self, data):
        self.vehicles.append(data)
        with open('data.csv', 'a') as f:
            f.write('\n')
            for key, value in data.items():
                f.write(f'{key}={value}' + (',' if key == list(data.keys())[-1] else ''))

    def check_car_matches(self, data):
        # check if the car matches any in the database, if all the keys in the data match exluding reasoning
        # make sure that the key is present in both dictionaries
        for vehicle in self.vehicles:
            if all(key in vehicle and key in data and vehicle[key].lower() == data[key].lower() for key in data.keys() if key != 'reasoning'):
                return vehicle
        return None
