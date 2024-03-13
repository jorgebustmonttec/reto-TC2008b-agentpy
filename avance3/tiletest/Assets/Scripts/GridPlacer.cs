using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Newtonsoft.Json;

public class GridPlacer : MonoBehaviour
{
    public GameObject tilePrefab; // Assign your tile prefab in the Inspector
    private List<GameObject> instantiatedTiles = new List<GameObject>(); // To keep track of instantiated tiles

    public CameraController cameraController; // Assign this in the Inspector

    private void Awake()
    {
        // Ensure NetworkManager instance is ready
        if (NetworkManager.Instance == null)
        {
            Debug.LogError("NetworkManager instance is not ready. Please ensure it is added to the scene and initialized.");
        }
    }

    public void ClearGrid()
    {
        // Loop through all instantiated tiles and destroy them
        foreach (GameObject tile in instantiatedTiles)
        {
            Destroy(tile);
        }
        instantiatedTiles.Clear(); // Clear the list after destroying the tiles
    }

    // This function will be called by a button to start the grid generation process
    public void FetchAndGenerateGrid()
    {
        StartCoroutine(NetworkManager.Instance.GetRequest("intersection_matrix", GenerateGridFromJSON));
    }

    public void GenerateGridFromJSON(string jsonGrid)
    {
        ClearGrid();
        float[,] grid = JsonConvert.DeserializeObject<float[,]>(jsonGrid);
        if (grid == null)
        {
            Debug.LogError("Deserialization resulted in a null grid.");
            return;
        }

        PlaceTiles(grid);
        if (cameraController != null)
            cameraController.AdjustCamera(grid); // Adjust camera after generating the grid
        else
            Debug.LogError("CameraController reference not set in GridPlacer.");
    }

    void PlaceTiles(float[,] grid)
    {
        for (int i = 0; i < grid.GetLength(0); i++) // Rows
        {
            for (int j = 0; j < grid.GetLength(1); j++) // Columns
            {
                if (grid[i, j] != 0) // If the grid value is not 0, place a tile
                {
                    GameObject tile = Instantiate(tilePrefab, new Vector3(j, 0, -i), Quaternion.identity);
                    instantiatedTiles.Add(tile); // Add the instantiated tile to the list
                }
            }
        }
    }
}
