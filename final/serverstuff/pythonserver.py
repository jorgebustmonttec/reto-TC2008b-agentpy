
from flask import Flask, jsonify, request
from flask_cors import CORS
from intersection import run_intersection_model  # Assuming this is your model function
import numpy as np
from addition import add  # Import the add function from addition.py

app = Flask(__name__)
CORS(app)

# Global variable to store simulation results
simulation_results = {}

@app.route('/sum', methods=['GET'])
def sum_xy():
    # Retrieve x and y from the query parameters and convert them to integers
    x = int(request.args.get('x', 0))
    y = int(request.args.get('y', 0))
    # Use the add function from addition.py to calculate the sum
    z = add(x, y)
    print(f"The sum of {x} and {y} is {z}")
    return jsonify(z=z)

@app.route('/run_model', methods=['POST'])
def run_model():
    global simulation_results
    parameters = {
        'dimensions': int(request.json.get('dimensions', 16)),
        'steps': int(request.json.get('steps', 20)),
        'max_cars': int(request.json.get('max_cars', 3)),
        'spawn_rate': float(request.json.get('spawn_rate', 1)),
        'chance_run_yellow_light': float(request.json.get('chance_run_yellow_light', 0.5)),
        'chance_run_red_light': float(request.json.get('chance_run_red_light', 0.5)),
        'smart_lights': request.json.get('smart_lights', False),  # Added this genius here
        'green_duration': int(request.json.get('green_duration', 30)),  # And this party animal
    }
    simulation_results = run_intersection_model(parameters)
    return jsonify({"message": "Simulation run successfully"}), 200

def convert_to_native_python_types(cars, traffic_lights):
    """Convert all data within a frame to native Python types, including car IDs."""
    native_frame_cars = []
    native_frame_traffic_lights = []

    for car_id, position, direction in cars:
        car_id_str = str(car_id)
        if isinstance(position, np.ndarray):
            position = position.tolist()
        position = [int(x) for x in position]
        # Check if direction is None before converting
        if direction is not None:
            direction = int(direction)
        else:
            direction = -1  # Use a placeholder value or handle error as appropriate
        native_frame_cars.append({"id": car_id_str, "position": position, "direction": direction})

    for traffic_light in traffic_lights:
        position, state, direction = traffic_light
        if isinstance(position, np.ndarray):
            position = position.tolist()
        position = [int(x) for x in position]
        state = int(state)
        direction = int(direction)
        native_frame_traffic_lights.append({"position": position, "state": state, "direction": direction})

    return {"cars": native_frame_cars, "trafficLights": native_frame_traffic_lights}

@app.route('/frames', methods=['GET'])
def get_frames():
    if not simulation_results:
        return jsonify({"error": "Simulation not run yet"}), 404
    
    frames_data = []
    for frame in simulation_results['reporters']['frames'][0]:
        # Split the frame into cars and traffic lights parts
        cars, traffic_lights = frame
        frame_data = convert_to_native_python_types(cars, traffic_lights)
        frames_data.append(frame_data)

    return jsonify(frames_data)






@app.route('/intersection_matrix', methods=['GET'])
def get_intersection_matrix():
    if not simulation_results:
        return jsonify({"error": "Simulation not run yet"}), 404
    intersection_matrix = simulation_results['reporters']['intersection_matrix'][0]
    if isinstance(intersection_matrix, np.ndarray):
        intersection_matrix = intersection_matrix.tolist()
    return jsonify(intersection_matrix)

@app.route('/total_steps', methods=['GET'])
def get_total_steps():
    if not simulation_results:
        return jsonify({"error": "Simulation not run yet"}), 404
    # Convert total_steps to a native Python int before serialization
    total_steps = int(simulation_results['reporters']['total_steps'][0])
    return jsonify({"total_steps": total_steps})


if __name__ == '__main__':
    app.run(debug=True, port=6000)
