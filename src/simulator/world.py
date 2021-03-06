class Street:
    def __init__(self, *, name, intersection_start, intersection_end, T):
        self.name = name
        self.intersection_start = intersection_start
        self.intersection_end = intersection_end
        self.T = T
        self.cars = []
        self.traveling_cars = []
        self.queueing_cars = [] # FIFO
    
    def step(self):
        for car in self.traveling_cars:
            self.remaining_traveling_time -= 1
            if car.remaining_traveling_time == 0:
                self.traveling_cars.remove(car)
                self.queueing_cars.append(car)

class Intersection:
    def __init__(self, *, id):
        self.identifier = id
        self.in_streets = []
        self.out_streets = []
        
        self.traffic_lights = []
        self.curr_green = 0
        self.counter = 0


    def step(self):

        assert len(self.traffic_lights) == len(self.in_streets)        
        if self.counter == self.traffic_lights[self.curr_green]:
            #  swith traffic light
            self.curr_green = (self.curr_green+1)%len(self.in_streets)
            self.counter = 0

        # let car out
        street = self.in_streets[self.curr_green]
        car = street.queueing_cars.pop(0)
        car.cross_intersection()

        self.counter += 1

class Car:
    def __init__(self, *, identifier, total_route):
        self.identifier = identifier
        self.current_street = total_route[0]
        self.total_route = total_route
        self.remaining_route = total_route[1:]
        self.remaining_traveling_time = 1

        self.current_street.traveling_cars.append(self)

    def cross_intersection(self):
        next_street = self.remaining_route.pop(0)

        self.current_street = next_street
        self.remaining_traveling_time = next_street.T

        next_street.traveling_cars.append(self)

class World:
    def __init__(self, *, config):
        self.config = config

        self.intersections = dict()
        self.streets = dict()
        self.cars = dict()

    def build(self):

        # Generate Intersections
        for id in range(self.config.num_intersections):
            self.intersections[id] = Intersection(id=id)

        # Generate Streets
        for street in self.config.streets:
            street = Street(name=street.name,
                            intersection_start=self.intersections[street.intersection_start],
                            intersection_end=self.intersections[street.intersection_end],
                            T=street.T)
            self.streets[street.name] = street

            self.intersections[street.intersection_start.identifier].out_streets.append(street)
            self.intersections[street.intersection_end.identifier].in_streets.append(street)

        # Generate Cars
        for id in range(self.config.num_cars):
            total_route = [self.streets[name] for name in self.config.cars[id].total_route]
            car = Car(identifier=id,
                      total_route=total_route)
                    
            self.cars[id] = car

    def step(self):
        for street in self.streets:
            street.step()

        for intersection in self.intersections:
            intersection.step()
