using UnityEngine;
using UnityEngine.Networking;
using System.Collections;

public class HelloWorldClient : MonoBehaviour
{
    void Start()
    {
        // Example values for x and y
        int x = 5;
        int y = 10;

        StartCoroutine(GetSum(x, y));
    }

    IEnumerator GetSum(int x, int y)
    {
        // Construct the URL with query parameters for x and y
        string url = $"http://localhost:6000/sum?x={x}&y={y}";

        using (UnityWebRequest webRequest = UnityWebRequest.Get(url))
        {
            // Send the request and wait for the response
            yield return webRequest.SendWebRequest();

            if (webRequest.result == UnityWebRequest.Result.ConnectionError || webRequest.result == UnityWebRequest.Result.ProtocolError)
            {
                Debug.Log("Error: " + webRequest.error);
            }
            else
            {
                // Parse the response (assuming the response is in the format {"z": sum})
                string jsonResponse = webRequest.downloadHandler.text;
                int z = JsonUtility.FromJson<Response>(jsonResponse).z;
                Debug.Log($"The sum of {x} and {y} is {z}");
            }
        }
    }

    private class Response
    {
        public int z;
    }
}
