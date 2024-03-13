import agentpy as ap  # Library for creating agents
import numpy as np  # NumPy library for numerical operations
import matplotlib.pyplot as plt  # Library for plotting
import seaborn as sns  # Library for statistical data visualization
from random import randint  # For generating random numbers
import IPython  # For displaying videos in the notebook
from matplotlib.animation import FuncAnimation  # For creating animations (used by agentpy)
import random
import math


class Message():

    performatives = ["request","inform"]
    parameters = ["content","sender","reply-with","in-reply-to"]

    def __init__(self,msg="",performative="",content="",sender="",query="q1",is_reply=True):
        """Constructor to build a new message"""
        self.empty = False
        self.request = False
        self.inform = False
        self.msg = msg

        #If we want to build a message from the paramters
        if msg == "":
            self.is_reply = is_reply
            self.query = query
            assert performative in Message.performatives , f"Performaive: {performative}"
            self.performative=performative
            self.content = content
            self.sender = sender

        #if we want to build a message from a string (a KQML message)
        else:
            self.decode()

        #Identify if its either Request or Inform performative
        if self.performative == "request":
            self.request = True
        elif self.performative == "inform":
            self.inform = True
        else:
            self.empty = True

    def decode(self):
        """Method to convert a string message (KQML format) to message parameters"""
        current = self.msg[1:-1]
        current = current.split("\n")
        self.performative = current[0]
        assert self.performative in Message.performatives , f"Performaive: {self.performative}"
        parameterList = current[1].split(":")[1:]
        parametersDict = {}
        for parameter in parameterList:
            pair = parameter.split(" ")
            parametersDict[pair[0]] = pair[1]
        if "in-reply-to" in parametersDict.keys():
            self.query = parametersDict["in-reply-to"]
            self.is_reply = True
        else:
            self.query = parametersDict["reply-with"]
            self.is_reply = False
        self.content = parametersDict["content"]
        self.sender = parametersDict["sender"]

    def __str__(self):
        """Method to convert message paramters to a string (KQML format)"""
        s = "("
        s+= self.performative + "\n"
        s+= ":sender " + self.sender
        s+= ":content "+self.content
        if self.is_reply:
            s+= ":in-reply-to " + self.query
        else:
            s+= ":reply-with " + self.query
        s+= ")"
        return s
    
class Road(ap.Agent):
    def setup(self):
        self.custom_id = 1 # Custom ID for the road agent
        self.grid_id = 1
        self.overlay_id = np.nan # Overlay ID for the road agent
        self.direction_id = None # Direction ID for the road agent to be set within the model
        # 1= southbound, 2= northbound, 3= eastbound, 4= westbound, 5= intersection area
        self.is_spawn = np.nan # flag to check if the road agent is a spawn point, 10 if spawn point
        self.is_end = np.nan # flag to check if the road agent is an end point, 20 if end point


    def get_position(self):
        return self.model.grid.positions[self]
    

class Car(ap.Agent):
    def setup(self):

        self.grid_id = np.nan
        #generate a random 10 digit number to be used as the license plate
        self.license_plate = self.generate_unique_license_plate()
        self.custom_id = 2 # Custom ID for the car agent
        self.overlay_id = 2
        # Speed of the car all start at 2
        self.speed = 2
        #0 = stopped, 1 = 1 cell pero two time steps, 2 = 1 cell per time step, 3 = 2 cells per time step
        self.sight_distance = 4 # Sight distance of the car
        self.direction = None # Direction of the car
        self.steps_since_last_move = 0 # Steps since the car moved
        #self.has_crossed = False # Flag to check if the car has crossed the intersection
        #self.intersection_time = 0 # Time the car has spent at the intersection
        #self.is_on_intersection = False # Flag to check if the car is on the intersection

    def action(self):
        # Look for the road agent the car is on
        agents = self.model.grid.agents[self.get_position()]
        for agent in agents:
            if agent.custom_id == 1:
                road = agent
                break
        else:
            # If no road agent is found, don't move
            return

        # If the road agent is an end point, remove the car
        if hasattr(road, 'is_end') and road.is_end == 20:

            #before deleting self, clear messages from this agent
            self.clear_old_messages()

            self.model.grid.remove_agents(self)
            self.model.cars.remove(self)
            return
        # Increment the counter for steps since the last move
        self.steps_since_last_move += 1
        
        # Determine if the car moves this step based on its speed
        move_this_step = False
        if self.speed == 1 and self.steps_since_last_move >= 2:
            move_this_step = True
            self.steps_since_last_move = 0  # Reset counter
        elif self.speed == 2 and self.steps_since_last_move >= 1:
            move_this_step = True
            self.steps_since_last_move = 0  # Reset counter
        elif self.speed == 3:
            move_this_step = True  # Always move if speed is 3, and handle double movement

        if move_this_step:
            
            # Update the direction of the car
            self.update_direction(road)

            # Move the car if it can keep moving
            self.see()
            self.move_car()
            # If speed is 3, attempt to move a second time in the same step
            if self.speed == 3:
                self.move_car()

        # Update the speed of the car
        self.update_speed()
        #clear old messages from this agent
        self.clear_old_messages()

        #Brodcast status (speed, direction and position)
        self.broadcast_status()

    def clear_old_messages(self):
        # Access the car's current lane's message board and clear old messages
        current_lane_board = self.model.message_boards[self.direction]
        self.model.message_boards[self.direction] = [msg for msg in current_lane_board if msg.sender != str(self.license_plate)]

    def broadcast_status(self):
        # Create and append a new status message to the current lane's message board
        status_message = Message(
            performative="inform",
            content=f"Speed: {self.speed}, Position: {self.get_position()}",
            sender=str(self.license_plate),
            query="statusUpdate",
            is_reply=False
        )
        self.model.message_boards[self.direction].append(status_message)
        # print the message for debugging
        #print(f"Broadcasting status: {status_message}")

    def update_direction(self, road):
        #check if agent has crossed the entire intersection
        #if self.intersection_time == self.model.intersection_length:
        #    self.has_crossed = True
        #    self.intersection_time = 0
        #get the direction of the road agent
        road_direction = road.direction_id
        #move the car based on the direction of the road agent. if intersection, move based on the direction already set
        if road_direction != 5:
            self.direction = road_direction
        #else:
         #   self.direction = self.direction
          #  self.is_on_intersection = True
           # self.intersection_time += 1
            
    def move_car(self):
        # check if speed is 0, if so, do not move
        if self.speed == 0:
            return

        # Move the car based on the direction
        if self.direction == 1:
            self.model.grid.move_by(self, (1, 0))
        elif self.direction == 2:
            self.model.grid.move_by(self, (-1, 0))
        elif self.direction == 3:
            self.model.grid.move_by(self, (0, 1))
        elif self.direction == 4:
            self.model.grid.move_by(self, (0, -1))

    def see(self):
        for distance in range(1, self.sight_distance + 1):
            # Check for a car at the current distance
            if self.search_for_car(distance):
                return  # Stop further checks if action required for a car
            # Check for a traffic light at the current distance
            if self.search_for_traffic_light(distance):
                return  # Stop further checks if action required for a traffic light
            
        # See if car from any direction has run a red light and is 1 to 2 cells in front of the car (to slam on the brakes)
        for distance in range(1, 2):
            if self.check_red_light_runners(distance):
                return
            


        # If checks up to 4 tiles ahead don't require stopping or slowing, then check for space after the intersection
        #self.check_space_after_intersection()
    
    def check_red_light_runners(self, distance):
        anticipated_position = self.get_position_ahead(distance)
        #print(f"[Debug - Red Light Runner Check] Agent {self.license_plate} position: {self.get_position()}, Direction: {self.direction}")
        #print(f"[Debug - Red Light Runner Check] Anticipated position for distance {distance}: {anticipated_position}")

        if not anticipated_position:
            #print("[Debug - Red Light Runner Check] No anticipated position. Returning False.")
            return False

        # Iterate through all message boards except the one corresponding to the car's current direction
        for direction, message_board in self.model.message_boards.items():
            if direction == self.direction:
                continue  # Skip the car's own lane

            for message in message_board:
                content = message.content
                try:
                    speed_part, position_part = content.rsplit(', Position:', 1)
                    # Assuming speed is not needed for red light runner check, but kept here for completeness
                    speed = int(speed_part.split(': ')[1])
                    position = eval(f"({position_part})")  # Safely convert position string to tuple
                except ValueError as e:
                    #print(f"[Debug - Red Light Runner Check] Error parsing message content: {e}")
                    continue  # Skip this message if there's an error

                #print(f"[Debug - Red Light Runner Check] Reading message from sender {message.sender}: Position {position}")
                
                if position == anticipated_position:
                    # Found a message indicating a car at the anticipated position from a different direction
                    #print(f"[Action - Red Light Runner Check] Agent {self.license_plate} detected a red light runner at {position}. Stopping.")
                    self.speed = 0
                    return True

        #print("[Debug - Red Light Runner Check] No red light runners detected.")
        return False

    def search_for_car(self, distance):
        anticipated_position = self.get_position_ahead(distance)
        #print(f"Agent position: {self.get_position()}")
        #print(f"Anticipated position: {anticipated_position}")

        if not anticipated_position:
            return False

        for message in self.model.message_boards[self.direction]:
            content = message.content
            try:
                # Use rsplit to split only on the first comma, which separates speed from position
                speed_part, position_part = content.rsplit(', Position:', 1)
                speed = int(speed_part.split(': ')[1])
                position = eval(f"({position_part})")  # Encapsulate in parentheses to ensure it's a tuple
            except ValueError as e:
                #print(f"Error parsing message content: {e}")
                continue

            if position == anticipated_position:
                if distance == 1:
                    self.speed = 0
                    return True
                elif distance in [2, 3, 4]:
                    if speed < self.speed:
                        self.speed = max(speed, 1 if distance == 2 else 2)
                    return True

        return False
    
    """ def search_for_car(self, distance):
        # Look ahead a certain distance in front of the car
        # If car is right in front, stop (speed 0)
        # If car is 2 cells ahead, reduce speed to match (if slower) (min speed 1 to avoid stopping)
        # If car is 3-4 cells ahead, reduce speed to match (if slower) (min speed 2 to avoid stopping)
        # at every comparison check if car is moving in the same direction

        agents = self.look_ahead(distance)  # Look ahead a certain distance
        for agent in agents:
            # Check if the agent is a car
            if agent.custom_id == 2 and agent.direction == self.direction:
                # If the car is right in front, stop the car
                if distance == 1:
                    self.speed = 0
                    return True
                # If the car is 2 cells ahead, reduce speed to match (if slower)
                elif distance == 2:
                    # If the car in front is slower, reduce speed to match (min speed 1)
                    if agent.speed < self.speed:
                        self.speed = max(agent.speed, 1)
                    return True
                # If the car is 3-4 cells ahead, reduce speed to match (if slower)
                elif distance in [3, 4]:
                    # If the car in front is slower, reduce speed to match (min speed 2)
                    if agent.speed < self.speed:
                        self.speed = max(agent.speed, 2)
                    return True
        return False """
    
    def get_position_ahead(self, distance):
        # Get the car's current position
        current_position = self.get_position()
        next_position = None
        

        # Calculate the next position based on the car's current direction and the distance
        if self.direction == 1:  # South
            next_position = (current_position[0] + distance, current_position[1])
        elif self.direction == 2:  # North
            next_position = (current_position[0] - distance, current_position[1])
        elif self.direction == 3:  # East
            next_position = (current_position[0], current_position[1] + distance)
        elif self.direction == 4:  # West
            next_position = (current_position[0], current_position[1] - distance)

        # Check if the next position is within the grid boundaries. if notreturn empyt list
        if next_position and 0 <= next_position[0] < self.model.p.dimensions and 0 <= next_position[1] < self.model.p.dimensions:
            return next_position
        else:
            return []
        
    def search_for_traffic_light(self, distance):
        # Look ahead a certain distance in front of the car
        #if light is right in front, stop
        #if light is 2-4 cells ahead, reduce speed to 2 (1 cell per time step)
        agents = self.look_ahead(distance) # Look ahead a certain distance
        for agent in agents:
            # Check if the agent is a traffic light
            if agent.custom_id == 3:
                # If the traffic light is red or yellow (and takes into account chance to run yellow light and red lights) stop the car
                if (agent.state == 100 and random.random() > self.model.p.chance_run_red_light) or (agent.state == 102 and random.random() > self.model.p.chance_run_yellow_light):
                    #check distance to light for speed reduction
                    # if distance is 1, stop
                    if distance == 1:
                        self.speed = 0
                        return True
                    else:
                        # if distance is 2-4, reduce speed to 2
                        self.speed = 2
                        return True
        return False
    
    def look_ahead(self, distance):

        # Get the car's current position
        current_position = self.get_position()
        next_position = None

        # Calculate the next position based on the car's current direction and the distance
        if self.direction == 1:  # South
            next_position = (current_position[0] + distance, current_position[1])
        elif self.direction == 2:  # North
            next_position = (current_position[0] - distance, current_position[1])
        elif self.direction == 3:  # East
            next_position = (current_position[0], current_position[1] + distance)
        elif self.direction == 4:  # West
            next_position = (current_position[0], current_position[1] - distance)

        # Check if the next position is within the grid boundaries
        if next_position and 0 <= next_position[0] < self.model.p.dimensions and 0 <= next_position[1] < self.model.p.dimensions:
            return self.model.grid.agents[next_position]
        else:
            return []  # Return an empty list if the position is outside the grid boundaries
    
    def update_speed(self):
        # Increase speed by 1 every 2 steps, up to a maximum of 3
        if self.model.t % 2 == 0:  # Assuming there's a model-wide timer you can access
            self.speed = min(self.speed + 1, 3)
        
    def get_position(self):
        return self.model.grid.positions[self]

    def generate_unique_license_plate(self):
        """Generates a unique license plate."""
        existing_plates = {car.license_plate for car in self.model.cars}
        
        while True:
            new_plate = randint(1000000000, 9999999999)
            if new_plate not in existing_plates:
                return new_plate

class Traffic_Light(ap.Agent):

    def setup(self):
        self.custom_id = 3 # Custom ID for the traffic light agent
        self.grid_id = 1
        self.overlay_id = 3
        self.state = 100 # State of the traffic light, 100 = red, 101 = green


        
    def get_position(self):
        return self.model.grid.positions[self]
    
class TrafficController(ap.Agent):
    def setup(self):
        self.custom_id = 4  # Custom ID
        self.grid_id = np.nan
        self.overlay_id = np.nan
        self.traffic_lights = [[], [], [], []]  # Traffic lights per direction
        self.timer = 0
        # Current active traffic light direction
        self.current_active = None 
        # Initialize state to track the phase (Green, Yellow, Red)
        self.phase = "Green"
        # Define the order of traffic light activation for counter-clockwise rotation
        self.activation_order = [3, 2, 4, 1]  # East, North, West, South (counter-clockwise)

    def switch_traffic_lights(self):
        # If there's no currently active direction, initialize it
        if self.current_active is None:
            self.current_active = self.activation_order[0]
            self.set_traffic_lights(self.current_active, 101)  # Start with green
        else:
            if self.phase == "Green":
                # After green, switch current lights to yellow
                self.set_traffic_lights(self.current_active, 102)  # Yellow
                self.phase = "Yellow"
                self.timer = 0  # Reset timer for yellow phase duration
            elif self.phase == "Yellow" and self.timer >= 5:
                # After yellow duration, switch current to red and next to green
                self.set_traffic_lights(self.current_active, 100)  # Current to Red
                # Determine the next direction
                current_index = self.activation_order.index(self.current_active)
                next_index = (current_index + 1) % len(self.activation_order)
                self.current_active = self.activation_order[next_index]
                self.set_traffic_lights(self.current_active, 101)  # Next to Green
                self.phase = "Green"
                self.timer = 0  # Reset timer for green phase duration

    def set_traffic_lights(self, direction, state):
        """Set the state of traffic lights in a specific direction."""
        for light in self.traffic_lights[direction - 1]:  # Adjust index for 0-based
            light.state = state

    def action(self):
        self.timer += 1  # Increment the global timer
        # Every 15 steps, or if in yellow phase and 5 steps have passed, switch traffic lights
        if self.timer % 15 == 0 or (self.phase == "Yellow" and self.timer >= 5):
            self.switch_traffic_lights()

class IntersectionModel(ap.Model):
    def setup(self):
        self.spawn_points = [] # List to store the spawn points
        # Create grid
        self.grid = ap.Grid(self, (self.p.dimensions, self.p.dimensions))


        self.pre_intersection_pos = []  # List to store pre-intersection positions
        # Create roads
        self.setup_roads()
        # Setup traffic lights
        self.setup_traffic_lights()


        #print("traffic light position: ", self.pre_intersection_pos)

        # Create cars
        self.cars = [] # List to store the car agents




        #since attr grid isnt working, create a grid to store the positions of the cars
        self.pos_grid = np.full((self.p.dimensions, self.p.dimensions), np.nan)

        # same for the traffic lights
        self.traffic_light_grid = np.full((self.p.dimensions, self.p.dimensions), np.nan)

         # Initialize a message board for each lane direction
        self.message_boards = {
            1: [],  # Southbound
            2: [],  # Northbound
            3: [],  # Eastbound
            4: []   # Westbound
        }

        #frame list to send to visualization software
        # add new "frame" every update
        # each frame is a list of tuples, with each tuple containing position and direction of each car.
        self.frames = []



                    
    def step(self):
       
        self.update_car_count()
        for car in self.cars:
            car.action()

        self.traffic_controller.action()


    def update(self):
        self.update_pos_grid()
        self.update_traffic_light_grid()

        #update the frame list
        #create a list to store the cars and traffic lights
        carFrame = []
        lightFrame = []
        # for each car, append its position and direction to the frame list in the form of a tuple
        for car in self.cars:
            # create a tuple with the car's position and direction
            carFrame.append(( car.license_plate ,car.get_position(), car.direction))

        # for each traffic light, append its position and state to the frame list in the form of a tuple
        #I messed up the indices and directions, so heres the fix
        #self.activation_order = [3, 2, 4, 1]  # East, North, West, South (counter-clockwise)
        # you can get the direction of the traffic light from its index in the traffic_lights list
        for i in range(len(self.traffic_lights)):
            pos = self.traffic_lights[i].get_position()
            state = self.traffic_lights[i].state
            #get direction before fix
            direction = i + 1
            # create a tuple with the traffic light's position, state, and direction
            lightFrame.append((pos, state, direction))
        # append the car and traffic light frame lists to the frame list
        self.frames.append([carFrame, lightFrame])

        pass


    def end(self):
        #print each of the messages by message board and its contents

        #return the intersection matrix
        self.report('intersection_matrix', self.intersection_matrix)

        #return total steps
        self.report('total_steps', self.t)

        #return the frames
        self.report('frames', self.frames)


    def setup_traffic_lights(self):
        # Create traffic controller
        self.traffic_controller = ap.AgentList(self, 1, TrafficController)[0]  # Note the [0] to get the actual agent

        # Create traffic lights
        self.traffic_lights = ap.AgentList(self, len(self.pre_intersection_pos), Traffic_Light)
        self.grid.add_agents(self.traffic_lights, self.pre_intersection_pos)

        # Add the traffic lights to the traffic controller
        for light, pos in zip(self.traffic_lights, self.pre_intersection_pos):
            # Determine the direction based on the intersection matrix and explicitly cast to int
            direction = int(self.intersection_matrix[pos[0]][pos[1]])
            
            # Assign the light to the correct list based on direction
            # Assuming 1= southbound, 2= northbound, 3= eastbound, 4= westbound
            if direction in [1, 2, 3, 4]:
                # Subtract 1 to match direction to index (0-3) in the traffic_lights list
                self.traffic_controller.traffic_lights[direction - 1].append(light)

    def update_pos_grid(self):
        #clear grid with nan
        self.pos_grid = np.full((self.p.dimensions, self.p.dimensions), np.nan)

        #update grid with car positions
        for car in self.cars:
            pos = car.get_position()
            self.pos_grid[pos] = car.custom_id

    def update_traffic_light_grid(self):
        # Clear grid with NaN
        self.traffic_light_grid = np.full((self.p.dimensions, self.p.dimensions), np.nan)

        # Update grid with traffic light states
        for light in self.traffic_lights:
            pos = light.get_position()
            self.traffic_light_grid[pos] = light.state

    def update_car_count(self): #Function to add cars to the grid
        # Adds cars to the grid until the max is reached or spawn points are full
        
        if np.random.rand() < self.p.spawn_rate:
        # Check if the number of cars has reached the maximum
            if len(self.cars) == self.p.max_cars:
                #print("Max cars reached")
                return # Return if the maximum number of cars has been reached
            
            # Check spawn points arent full
            uncovered_spawn_points = []
            for spawn_point in self.spawn_points:

                # Check if the spawn point is covered by a car

                if len(self.grid.agents[spawn_point.get_position()[0]]) == 1:
                    uncovered_spawn_points.append(spawn_point) # Add to the list of uncovered spawn points
            
            if len(uncovered_spawn_points) == 0:
                #print("All spawn points covered")
                return # Return if all spawn points are covered
        
            self.add_car(uncovered_spawn_points) # Add a car to the grid

    def add_car(self, spawn_points): #Function to add cars to the grid

        #Print available spawn points coordinates
        #print("Available spawn points: ", [spawn_point.get_position() for spawn_point in spawn_points])

        # Add a car to the grid
        car = ap.AgentList(self, 1, Car)
        
        # Randomly select a spawn point, if it is covered, try again
        spawn_point = spawn_points[randint(0, len(spawn_points) - 1)]
        #print("adding car at ", spawn_point.get_position())

        # Add the car to the grid
        self.grid.add_agents(car, spawn_point.get_position())
        #print("Car added at ", car.get_position())
        self.cars.append(car[0]) # Add the car to the list of cars
     
    def setup_roads(self):
        intersection_agents = []  # List to store the intersection agents
        # CREATE ROAD AGENTS
        # Create the intersection matrix
        self.intersection_matrix = self.create_intersection_matrix(self.p.dimensions, self.p.dimensions)
        #print(self.intersection_matrix)
    
        # Add road agents to the grid following the intersection matrix, adding each road agent to their respective direction
        # 1= southbound, 2= northbound, 3= eastbound, 4= westbound, 5= intersection area
        for i in range(self.p.dimensions):
            for j in range(self.p.dimensions):
                if self.intersection_matrix[i][j] != 0:
                    #print(i, j, int(self.intersection_matrix[i][j]))
                    road = ap.AgentList(self, 1, Road)
                    road[0].direction_id = int(self.intersection_matrix[i][j])
                    self.grid.add_agents(road, [(int(i), int(j))])
                    #if the agent is intersection add to itnersection list
                    if int(self.intersection_matrix[i][j]) == 5:
                        intersection_agents.append(road[0])
        #get length of intersection by getting the square root of the length of the intersection agents
        self.intersection_length = int(math.sqrt(len(intersection_agents)))
                    


        # MARK SPAWN AND END POINTS
        self.mark_spawn_and_end_points()
        self.mark_pre_intersection_points()

    def mark_pre_intersection_points(self):
        # Iterate over the intersection matrix to find lanes leading to the intersection
        for i in range(self.p.dimensions):
            for j in range(self.p.dimensions):
                if self.intersection_matrix[i][j] in [1, 2, 3, 4]:  # Road directions
                    if self.is_pre_intersection(i, j, self.intersection_matrix[i][j]):
                        # Directly store the position of this pre-intersection point
                        self.pre_intersection_pos.append((i, j))

    def is_pre_intersection(self, x, y, direction):
        """
        Check if the given position is directly before an intersection
        based on the road's direction, ensuring not to go outside the matrix bounds.
        """
        dimensions = self.p.dimensions  # Assuming this is the size of your grid/matrix

        if direction == 1:  # Southbound, check below if not at bottom edge
            return x < dimensions - 1 and self.intersection_matrix[x+1][y] == 5
        elif direction == 2:  # Northbound, check above if not at top edge
            return x > 0 and self.intersection_matrix[x-1][y] == 5
        elif direction == 3:  # Eastbound, check right if not at rightmost edge
            return y < dimensions - 1 and self.intersection_matrix[x][y+1] == 5
        elif direction == 4:  # Westbound, check left if not at leftmost edge
            return y > 0 and self.intersection_matrix[x][y-1] == 5
        return False

    def create_intersection_matrix(self, n, m):
        # Initialize the matrix with zeros
        matrix = np.zeros((n, m))
        
        # Determine the central points
        center_n = n // 2 # center of rows/height
        center_m = m // 2 # center of columns/width
        
        # Adjust for even dimensions - to ensure the intersection is centered
        n_start = center_n - 1 if n % 2 == 0 else center_n
        m_start = center_m - 1 if m % 2 == 0 else center_m
        
        # Create intersection area
        for i in range(n_start, n_start+2):
            for j in range(m_start, m_start+2):
                matrix[i][j] = 5
        
        # Create lanes leading to the intersection
        # Southbound and Northbound lanes
        for i in range(n_start):
            matrix[i][m_start] = 1
            matrix[i][m_start+1] = 2
        for i in range(n_start+2, n):
            matrix[i][m_start] = 1
            matrix[i][m_start+1] = 2
        
        # Eastbound and Westbound lanes
        for j in range(m_start):
            matrix[n_start][j] = 4
            matrix[n_start+1][j] = 3
        for j in range(m_start+2, m):
            matrix[n_start][j] = 4
            matrix[n_start+1][j] = 3
        
        # 1= southbound, 2= northbound, 3= eastbound, 4= westbound, 5= intersection area
        return matrix
        
    def mark_spawn_and_end_points(self):
        dimensions = self.p.dimensions
        for i in range(dimensions):
            for j in range(dimensions):
                direction_id = int(self.intersection_matrix[i][j])
                if direction_id != 0:
                    road_agents = self.grid.agents[(i, j)]
                    if not road_agents:
                        continue  # No agent at this position, should not happen but check for safety
                    
                    road_agent = road_agents  # Assuming one agent per grid cell
                    # Check if the agent's position is at the edge and matches the direction for a spawn point
                    if (direction_id == 1 and i == 0) or (direction_id == 2 and i == dimensions - 1) or \
                    (direction_id == 3 and j == 0) or (direction_id == 4 and j == dimensions - 1):
                        road_agent.is_spawn = 10
                        self.spawn_points.append(road_agent)
                        
                    # Check if the agent's position is at the opposite edge and matches the direction for an end point
                    if (direction_id == 1 and i == dimensions - 1) or (direction_id == 2 and i == 0) or \
                    (direction_id == 3 and j == dimensions - 1) or (direction_id == 4 and j == 0):
                        road_agent.is_end = 20
                        

def run_intersection_model(parameters):
    model = IntersectionModel(parameters)
    results = model.run()
    #print(results['reporters']['intersection_matrix'][0])
    #steps = results['reporters']['total_steps'][0]
    #print(steps)
    return results

parameters={
    'dimensions': 16,  # Dimensions of the grid, minimum 4
    'steps': 10,  # Number of steps to run the model
    'max_cars': 3, # Maximum number of cars
    'spawn_rate': 1, # Rate of car spawn, chance of car spawn per step 
    'chance_run_yellow_light': 0.5, # Chance of running a yellow light
    'chance_run_red_light': 0.5, # Chance of running a red light
}

""" results =run_intersection_model(parameters)

# Print the intersection matrix
print(results['reporters']['intersection_matrix'][0])

# Print the total steps
print(results['reporters']['total_steps'][0])

# Print the frames
print(results['reporters']['frames'][0])

print(results)

print(type(results)) """










