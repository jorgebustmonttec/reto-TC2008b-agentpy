using UnityEngine;

public class CameraController : MonoBehaviour
{
    // Method to adjust the camera position based on grid size
    public void AdjustCamera(float[,] grid)
    {
        int rows = grid.GetLength(0);
        int columns = grid.GetLength(1);

        // Calculate the center of the grid
        Vector3 centerPoint = new Vector3(columns / 2f - 0.5f, 0, -rows / 2f + 0.5f);

        // Adjust camera position
        transform.position = centerPoint + new Vector3(0, CalculateCameraDistance(rows, columns), 0);

        // Ensure the camera is looking directly down
        transform.rotation = Quaternion.Euler(90f, 0, 0);
    }

    // Method to calculate the necessary distance of the camera based on grid size
    private float CalculateCameraDistance(int rows, int columns)
    {
        // Determine the larger size between rows and columns
        float maxSize = Mathf.Max(rows, columns);

        // Calculate distance. You might need to adjust the multiplier based on your grid's scale and camera's field of view
        float distance = maxSize * 0.8f;

        // Ensure the camera is always at least a certain distance away (e.g., to avoid clipping)
        return Mathf.Max(distance, 10f);
    }

    // Method for your oh-so-important different camera positions
    public void SetCameraPosition(int positionIndex, float[,] grid)
    {
        int rows = grid.GetLength(0);
        int columns = grid.GetLength(1);
        Vector3 centerPoint = new Vector3(columns / 2f - 0.5f, 0, -rows / 2f + 0.5f);

        float cameraDistance = CalculateCameraDistance(rows, columns);

        switch (positionIndex)
        {
            case 1:
                // Very close diagonal view
                Vector3 cornerViewOffset = new Vector3(4, 2, -4); // Much closer
                transform.position = centerPoint + cornerViewOffset;
                transform.LookAt(centerPoint);
                break;
            case 2:
                // Closer horizontal view
                Vector3 sideViewOffset = new Vector3(0, cameraDistance * 0.375f, -cameraDistance * 0.375f);
                transform.position = centerPoint + sideViewOffset;
                transform.LookAt(centerPoint);
                break;
            case 3:
                // birds-eye view
                transform.position = centerPoint + new Vector3(0, cameraDistance, 0);
                transform.rotation = Quaternion.Euler(90f, 0, 0);
                break;
            default:
                Debug.LogError("You've gotta pick 1, 2, or 3. It's not that complicated.");
                break;
        }
    }
}
