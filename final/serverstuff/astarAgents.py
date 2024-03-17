
import agentpy as ap  # Library for creating agents
import numpy as np  # NumPy library for numerical operations
import matplotlib.pyplot as plt  # Library for plotting
import seaborn as sns  # Library for statistical data visualization
from random import randint  # For generating random numbers
import IPython  # For displaying videos in the notebook
from matplotlib.animation import FuncAnimation  # For creating animations (used by agentpy
from queue import PriorityQueue  # For creating priority queues


class PathfindingAgent(ap.Agent):
    def setup(self):
        self.pathfinding_id = 2 # Pathfinding agent ID
        self.destination = None # Destination agent
        self.path = None # Path to the destination (list of coordinates)
        self.position = None # Current position
        self.found_path = False # Flag to indicate if a path has been found
        self.is_obstacle = np.nan # Flag to indicate if the agent is an obstacle
        self.is_perm_obstacle = False # Flag to indicate if the agent is a permanent obstacle
        self.path_id = None # ID shared between agent and its destination to match them
        self.patience = 3 # Number of steps to wait for another agent to move
        self.time_waited = 0 # Number of steps the agent has waited
        self.turns_waited_without_path = 0  # Turns waited without finding a 
        self.hypothetical_path_attempts = 0  # Number of attempts to find a hypothetical path
        


    def action(self):

        #AGENT PATH SETUP
        if not self.destination:
            self.model.grid.remove_agent(self) # Remove the agent from the grid if it has no destination
            return
        if not self.found_path:
            self.prepare_path()  # Prepare the path to the destination
            if self.path:
                self.found_path = True
                self.path.pop(0)  # Remove agent's initial position from the path
            elif self.turns_waited_without_path >= 10:
                if self.hypothetical_path_attempts < 10:
                    # Attempt to calculate a hypothetical path that ignores destinations as obstacles
                    self.prepare_path(hypothetical=True)
                    self.hypothetical_path_attempts += 1
                    self.turns_waited_without_path = 0  # Reset the counter for waiting without a path
                    return
                else:
                    # After 5 attempts, remove the agent and its destination
                    self.model.grid.remove_agents(self)
                    self.model.grid.remove_agents(self.destination)
                    self.model.remaining_agents -= 1
                    return

            


        #AGENT MOVEMENT
        if self.path: # If a path is available
            # Determine the next step to take
            next_step = self.path.pop(0)  # Get the next coordinate in the path

            # Calculate the relative move from the current position
            current_position = self.get_position()
            move_direction = (next_step[0] - current_position[0], next_step[1] - current_position[1]) # Calculate the relative move


            #check if pathfinding agent is at next step

            # list of agents at next step
            agents_at_next_step = self.model.grid.agents[next_step]

            if len(agents_at_next_step) > 0:  # If there are agents at the next step
                for agent in agents_at_next_step:
                    if agent.pathfinding_id == 2:  # If the agent is a pathfinding agent
                        # Decide to wait based on some condition (e.g., random chance)
                        if randint(0, 1) == 1:
                            self.time_waited += 1
                            if self.time_waited < self.patience:
                                # Only re-insert the step if the agent decides to wait, not yet recalculating path
                                self.path.insert(0, next_step)
                                #print("Waiting for another agent to move, step re-inserted.")
                                return  # Return without moving
                            else:
                                # Patience exceeded, time to recalculate path
                                #print("Patience exceeded, recalculating path...")
                                self.time_waited = 0
                                self.prepare_path(additional_obstacle=next_step)  # Assuming this method recalculates the path
                                # After recalculating, no need to re-insert the step as the path has been updated
                                if self.path:
                                    self.found_path = True
                                    #print("New path calculated:", self.path)
                                return
                        break  # Break after handling the first pathfinding agent found, assuming one agent per cell
                else:
                    # No pathfinding agent blocking the way, reset wait timer
                    self.time_waited = 0


            # Move the agent to the next step
            self.model.grid.move_by(self, move_direction)




            # Check if the agent has reached the destination
            if self.get_position() == self.destination.get_position():
                #print("Agent has reached the destination")
                # Remove agent and destination from the grid
                self.model.grid.remove_agents(self)
                self.model.grid.remove_agents(self.destination)

                #decrease remaining agents 
                self.model.remaining_agents -= 1

        

    def decrease_patience(self):
        pass

    def prepare_path(self, additional_obstacle=None, hypothetical=False):
        grid = self.model.grid.attr_grid('is_obstacle')

        # For hypothetical paths, consider only permanent obstacles
        if hypothetical:
            grid = self.model.grid.attr_grid('is_perm_obstacle')

        grid[self.get_position()] = 2
        # Corrected ternary operation syntax
        grid[self.destination.get_position()] = np.nan if hypothetical else 1  # Ignore destination as obstacle if hypothetical

        if additional_obstacle is not None:
            grid[additional_obstacle] = 3

        found_path = self.find_path(grid)
        if found_path:
            self.turns_waited_without_path = 0
            found_path.append(self.destination.get_position())
            self.path = found_path
        else:
            self.turns_waited_without_path += 1




    def recalculate_path(self):
        pass

    def find_path(self, grid_array):
    
        def h(p1, p2):
            return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

        def reconstruct_path(came_from, current):
            path = []
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return path[::-1]

        # Convert grid_array to treat NaNs as 0 for open path, and obstacles (3) as inf
        grid_array = np.where(np.isnan(grid_array), 0, grid_array)
        grid_array = np.where(grid_array == 3, float('inf'), grid_array)

        start = None
        end = None
        for i in range(grid_array.shape[0]):
            for j in range(grid_array.shape[1]):
                if grid_array[i, j] == 2:
                    start = (i, j)
                elif grid_array[i, j] == 1:
                    end = (i, j)
        
        if not start or not end:
            return []  # If there's no start or end, return an empty path.

        open_set = PriorityQueue()
        open_set.put((0, start))
        came_from = {}
        g_score = {spot: float("inf") for spot in np.ndindex(grid_array.shape)}
        g_score[start] = 0
        f_score = {spot: float("inf") for spot in np.ndindex(grid_array.shape)}
        f_score[start] = h(start, end)

        while not open_set.empty():
            current = open_set.get()[1]

            if current == end:
                return reconstruct_path(came_from, end)

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # NSEW movements
                neighbor = (current[0] + dx, current[1] + dy)
                if 0 <= neighbor[0] < grid_array.shape[0] and 0 <= neighbor[1] < grid_array.shape[1]:
                    # Check if the neighbor is an obstacle
                    if grid_array[neighbor[0], neighbor[1]] == float('inf'):
                        continue  # Skip this neighbor
                    
                    temp_g_score = g_score[current] + 1

                    if temp_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = temp_g_score
                        f_score[neighbor] = temp_g_score + h(neighbor, end)
                        if neighbor not in {item[1] for item in open_set.queue}:  # Check if not in open_set
                            open_set.put((f_score[neighbor], neighbor))

        #print("No path found")
        return []  # Return an empty path if there's no path to the end.

    def get_position(self):
        try:
            return self.model.grid.positions[self]
        except KeyError:
            # Handle the case where the agent has been removed; return a default or previous position, or None
            return None  # Or some other appropriate handling


class DestinationAgent(ap.Agent):
    def setup(self):
        self.pathfinding_id = 1
        self.is_obstacle = 3
        self.is_perm_obstacle = np.nan
        self.path_id=None # ID shared between agent and its destination to match them

    def get_position(self):
        return self.model.grid.positions[self]
    
class ObstacleAgent(ap.Agent):
    def setup(self):
        self.pathfinding_id = 3
        self.is_obstacle = 3 
        self.is_perm_obstacle = 3




class PathfindingModel(ap.Model):
    def setup(self):
        # Create agents
        self.pathfinding_agents = ap.AgentList(self, self.p.n_agents, PathfindingAgent)
        self.destination_agents = ap.AgentList(self, self.p.n_agents, DestinationAgent)

        # Get obstacle amount from density
        n_obstacles = int(self.p.obstacle_density * self.p.dimensions**2) # obstacle density * dimensions^2
        # Create obstacle agents
        self.obstacle_agents = ap.AgentList(self, n_obstacles, ObstacleAgent)
        

        # Create grid
        self.grid = ap.Grid(self, (self.p.dimensions, self.p.dimensions), track_empty=True, check_border=True)

        # Add agents to grid
        self.grid.add_agents(self.pathfinding_agents, random=True, empty=True)
        self.grid.add_agents(self.destination_agents, random=True, empty=True)
        self.grid.add_agents(self.obstacle_agents, random=True, empty=True)

        # Set pathfinding agents' destinations abd positions
        for i in range(len(self.pathfinding_agents)):
            agent = self.pathfinding_agents[i]
            destination = self.destination_agents[i]
            agent.position = agent.get_position()
            #print("agent" + str(i) + " position: " + str(agent.position))
            agent.destination  = destination
            #print("destination position: " + str(agent.destination.get_position()))

        self.remaining_agents = self.p.n_agents



    def step(self):
        for agent in self.pathfinding_agents:
            agent.action()

    def update(self):
        if self.remaining_agents == 0:
            self.stop()



    def end(self):
        print("\n")
        #print(self.grid.attr_grid('pathfinding_id'))
        self.report('total-steps', self.t)
        self.report('obstacle_grid', self.grid.attr_grid('is_perm_obstacle'))



""" parameters={
    'steps':20,
    'dimensions': 70,
    'n_agents': 70,
    'obstacle_density': 0.2,
}

model = PathfindingModel(parameters)

results = model.run()

print(results['reporters']['total-steps'][0]) """


def run_model(parameters):
    model = PathfindingModel(parameters)
    results = model.run()
    return results

""" parameters={
    'steps':20,
    'dimensions': 70,
    'n_agents': 70,
    'obstacle_density': 0.2,
}

results = run_model(parameters)

print(results['reporters']['total-steps'][0])
print(results['reporters']['obstacle_grid'][0])
 """