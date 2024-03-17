using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using Newtonsoft.Json;

public class NetworkManager : MonoBehaviour
{
    private static NetworkManager instance;
    public static NetworkManager Instance => instance;

    private void Awake()
    {
        if (instance != null && instance != this)
        {
            Destroy(this.gameObject);
        }
        else
        {
            instance = this;
            DontDestroyOnLoad(this.gameObject);
        }
    }

    private readonly string baseURL = "http://localhost:6000";

    public IEnumerator PostRunModel(string jsonParameters, System.Action<bool> callback)
    {
        string url = $"{baseURL}/run_model";
        var request = new UnityWebRequest(url, "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(jsonParameters);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");

        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.ConnectionError || request.result == UnityWebRequest.Result.ProtocolError)
        {
            Debug.LogError($"Error: {request.error}");
            callback?.Invoke(false);
        }
        else
        {
            Debug.Log("Post RunModel success.");
            callback?.Invoke(true);
        }
    }

    public IEnumerator GetRequest(string endpoint, System.Action<string> callback)
    {
        string url = $"{baseURL}/{endpoint}";
        UnityWebRequest request = UnityWebRequest.Get(url);

        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.ConnectionError || request.result == UnityWebRequest.Result.ProtocolError)
        {
            Debug.LogError($"Error: {request.error}");
            callback?.Invoke(null);
        }
        else
        {
            string responseJson = request.downloadHandler.text;
            callback?.Invoke(responseJson);
        }
    }
}
