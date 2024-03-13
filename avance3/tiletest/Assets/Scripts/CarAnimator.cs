
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Newtonsoft.Json;
using System.Linq;

public class CarAnimator : MonoBehaviour
{
    public GameObject carPrefab; // Assign in Inspector
    public GameObject redLightPrefab;
    public GameObject greenLightPrefab;
    public GameObject yellowLightPrefab;

    private Dictionary<string, GameObject> activeCars = new Dictionary<string, GameObject>();
    private Dictionary<string, GameObject> activeTrafficLights = new Dictionary<string, GameObject>();

    private float frameRate = 0.1f; // 10 fps

    private bool isPaused = false;
    private bool stopRequested = false;




    void Start()
    {
        // Add button listener or another trigger to start the animation
    }

    // Method to start the animation
    public void StartAnimation() // called by button
    {
        Debug.Log("Start animation");
        ClearAllCars();
        StartCoroutine(FetchAndAnimateFrames());
        //set flags
        isPaused = false;
        stopRequested = false;
    }

    // Coroutine to fetch frames from the network and animate them
    IEnumerator FetchAndAnimateFrames()
    {
        Debug.Log("Fetching and animating frames");
        yield return StartCoroutine(NetworkManager.Instance.GetRequest("frames", response =>
        {
            AnimateFrames(response);
        }));
    }

    // Method to parse the JSON response and start playing the frames
    // Updated AnimateFrames to handle the new frame structure
    void AnimateFrames(string jsonResponse)
    {
        Debug.Log("Animating frames");
        Debug.Log(jsonResponse);
        var frames = JsonConvert.DeserializeObject<List<FrameData>>(jsonResponse);
        Debug.Log(frames);
        ClearAllTrafficLights(); // Add this line to clear traffic lights before each animation cycle
        StartCoroutine(PlayFrames(frames)); // Updated to pass entire frame data, not just cars
    }
    // Method to clear all existing cars
    void ClearAllCars()
    {
        // Destroy all cars in the scene
        foreach (var car in activeCars.Values)
        {
            Destroy(car);
        }
        activeCars.Clear(); // Clear the dictionary after destroying all cars
        // also 
    }

    // Coroutine to play the frames
    // Coroutine to play the frames
    IEnumerator PlayFrames(List<FrameData> frames)
    {
        Debug.Log("Playing frames");

        // Loop through each frame
        foreach (var frame in frames)
        {
            ClearAllTrafficLights(); // Clear existing traffic lights at the start of each frame
            InstantiateTrafficLights(frame.trafficLights); // Instantiate traffic lights for the current frame

            // Create a set of car IDs in the current frame
            HashSet<string> currentFrameCarIDs = new HashSet<string>();

            // Loop through each car in the frame
            foreach (var carInfo in frame.cars)
            {
                // Add the car ID to the set
                currentFrameCarIDs.Add(carInfo.id);
                // Convert position to Unity coordinates
                Vector3 position = new Vector3(carInfo.position[0], 0, -carInfo.position[1]);

                // Convert direction to rotation
                Quaternion rotation = DirectionToRotation(carInfo.direction);

                // Check if the car already exists
                if (activeCars.ContainsKey(carInfo.id))
                {
                    // Update existing car's position and rotation smoothly
                    StartCoroutine(MoveCar(activeCars[carInfo.id], position, rotation, frameRate));
                }
                // If the car does not exist, instantiate a new car
                else
                {
                    // Instantiate a new car
                    GameObject newCar = Instantiate(carPrefab, position, rotation);
                    // Set the car's name to its ID
                    activeCars[carInfo.id] = newCar;
                }
            }

            // Remove cars that are not in the current frame
            List<string> carsToRemove = new List<string>();
            // Loop through each active car
            foreach (var carID in activeCars.Keys)
            {
                // If the car is not in the current frame, add it to the list of cars to remove
                if (!currentFrameCarIDs.Contains(carID))
                {
                    // Destroy the car
                    Destroy(activeCars[carID]);
                    // Add the car ID to the list of cars to remove from the dictionary
                    carsToRemove.Add(carID);
                }
            }
            // Remove cars from the dictionary
            foreach (var carID in carsToRemove)
            {
                // Remove the car from the dictionary
                activeCars.Remove(carID);
            }

            // Inside the PlayFrames coroutine, after moving cars but before the WaitForSeconds
            while (isPaused)
                yield return null; // Wait indefinitely until isPaused becomes false

            if (stopRequested)
            {
                // Clear all cars and traffic lights from the scene
                ClearAllCars();
                ClearAllTrafficLights();
                // Reset the flag
                stopRequested = false; // Reset the flag
                yield break; // Exit the coroutine
            }
            // Wait for the next frame
            yield return new WaitForSeconds(frameRate);
        }
    }


    // Coroutine to smoothly move a car to a new position and rotation
    // 
    IEnumerator MoveCar(GameObject car, Vector3 newPosition, Quaternion newRotation, float duration)
    {
        // Store the initial position and rotation
        Vector3 startPosition = car.transform.position;
        // Store the initial rotation
        Quaternion startRotation = car.transform.rotation;
        // Store the elapsed time
        float elapsedTime = 0;

        // Loop until the elapsed time reaches the duration
        while (elapsedTime < duration)
        {
            // Move the car smoothly to the new position and rotation
            car.transform.position = Vector3.Lerp(startPosition, newPosition, elapsedTime / duration);
            car.transform.rotation = Quaternion.Lerp(startRotation, newRotation, elapsedTime / duration);
            // Increment the elapsed time
            elapsedTime += Time.deltaTime;
            // Wait for the next frame
            yield return null;
        }
        // Set the final position and rotation
        car.transform.position = newPosition;
        //  Set the final rotation
        car.transform.rotation = newRotation;
    }

    // Class to hold car information
    [System.Serializable] // Required for JSON serialization
    public class CarInfo
    {
        public string id;
        public List<int> position;
        public int direction;
    }

    [System.Serializable]
    public class TrafficLightInfo
    {
        public int direction;
        public List<int> position;
        public int state; // 100 for red, 101 for green, 102 for yellow
    }

    [System.Serializable]
    public class FrameData
    {
        public List<CarInfo> cars;
        public List<TrafficLightInfo> trafficLights;
    }


    // Method to convert direction to rotation
    Quaternion DirectionToRotation(int direction)
    {
        // Convert direction to rotation. Assumes North=0, East=90, South=180, West=270 degrees.
        int angle = 0;
        switch (direction)
        {
            case 1: angle = 180; break; // South
            case 2: angle = 0; break;   // North
            case 3: angle = 90; break;  // East
            case 4: angle = 270; break; // West
            case 5: angle = 0; break;   // Intersection (default to North for now)
        }
        return Quaternion.Euler(0, angle, 0);
    }

    public void TogglePause()
    {
        isPaused = !isPaused;
        Debug.Log("Pause state: " + isPaused);
    }

    public void StopAnimation()
    {
        stopRequested = true;
        ClearAllCars(); // Clears all cars from the scene
        ClearAllTrafficLights(); // Also clear all traffic lights from the scene
        Debug.Log("Stop requested");
    }


    void ClearAllTrafficLights()
    {
        foreach (var light in activeTrafficLights.Values)
        {
            Destroy(light);
        }
        activeTrafficLights.Clear();
    }

    GameObject GetTrafficLightPrefab(int state)
    {
        switch (state)
        {
            case 100: return redLightPrefab;
            case 101: return greenLightPrefab;
            case 102: return yellowLightPrefab;
            default: return null; // Handle unexpected state
        }
    }

    void InstantiateTrafficLights(List<TrafficLightInfo> trafficLights)
    {
        foreach (var lightInfo in trafficLights)
        {
            Vector3 position = new Vector3(lightInfo.position[0], 0, -lightInfo.position[1]);
            Quaternion rotation = DirectionToRotation(lightInfo.direction);
            GameObject prefab = GetTrafficLightPrefab(lightInfo.state);
            if (prefab != null)
            {
                GameObject trafficLight = Instantiate(prefab, position, rotation);
                string lightID = "Light_" + lightInfo.position[0] + "_" + lightInfo.position[1];
                activeTrafficLights[lightID] = trafficLight;
            }
        }
    }

}