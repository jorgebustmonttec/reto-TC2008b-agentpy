using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Networking;
using System.Collections;
using Newtonsoft.Json;
using System.Collections.Generic;

public class SliderCon : MonoBehaviour
{
    public Slider dimensionsSlider;
    public Slider stepsSlider;
    public Slider maxCarsSlider;
    public Slider spawnRateSlider;
    public Slider chanceRunYellowLightSlider;
    public Slider chanceRunRedLightSlider;

    public Text dimensionsText;
    public Text stepsText;
    public Text maxCarsText;
    public Text spawnRateText;
    public Text chanceRunYellowLightText;
    public Text chanceRunRedLightText;


    void Start()
    {
        // Set min and max values for sliders

        //dimensions slider (4 to 50, inclusive, integer values only)
        dimensionsSlider.minValue = 4;
        dimensionsSlider.maxValue = 50;

        //steps slider (1 to 500, inclusive, integer values only)
        stepsSlider.minValue = 1;
        stepsSlider.maxValue = 500;

        //max cars slider (1 to 65, inclusive, integer values only)
        maxCarsSlider.minValue = 1;
        maxCarsSlider.maxValue = 65;


        //spawn rate slider (0 to 1, inclusive, in increments of 0.01)
        spawnRateSlider.minValue = 0;
        spawnRateSlider.maxValue = 1;

        //chance run yellow light slider (0 to 1, inclusive, in increments of 0.01)
        chanceRunYellowLightSlider.minValue = 0;
        chanceRunYellowLightSlider.maxValue = 1;

        //chance run red light slider (0 to 1, inclusive, in increments of 0.01)
        chanceRunRedLightSlider.minValue = 0;
        chanceRunRedLightSlider.maxValue = 1;


        // Initialize slider values (optional if you want other defaults)
        dimensionsSlider.value = 12;
        stepsSlider.value = 100;
        maxCarsSlider.value = 10;
        spawnRateSlider.value = 0.5f;
        chanceRunYellowLightSlider.value = 0.3f;
        chanceRunRedLightSlider.value = 0.03f;

        // Subscribe to the onValueChanged event
        dimensionsSlider.onValueChanged.AddListener(delegate { UpdateParameterValuesText(); });
        stepsSlider.onValueChanged.AddListener(delegate { UpdateParameterValuesText(); });
        maxCarsSlider.onValueChanged.AddListener(delegate { UpdateParameterValuesText(); });
        spawnRateSlider.onValueChanged.AddListener(delegate { UpdateParameterValuesText(); });
        chanceRunYellowLightSlider.onValueChanged.AddListener(delegate { UpdateParameterValuesText(); });
        chanceRunRedLightSlider.onValueChanged.AddListener(delegate { UpdateParameterValuesText(); });

        dimensionsSlider.wholeNumbers = true;
        stepsSlider.wholeNumbers = true;
        maxCarsSlider.wholeNumbers = true;


        // Update display text initially
        UpdateParameterValuesText();
    }

    public void PrintCurrentValues()
    {
        // Use Mathf.RoundToInt for integer values and format the float values to show only 3 decimal places
        Debug.Log("Dimensions: " + Mathf.RoundToInt(dimensionsSlider.value));
        Debug.Log("Steps: " + Mathf.RoundToInt(stepsSlider.value));
        Debug.Log("Max Cars: " + Mathf.RoundToInt(maxCarsSlider.value));
        Debug.Log("Spawn Rate: " + (Mathf.Round(spawnRateSlider.value * 1000) / 1000f));
        Debug.Log("Chance Run Yellow Light: " + (Mathf.Round(chanceRunYellowLightSlider.value * 1000) / 1000f));
        Debug.Log("Chance Run Red Light: " + (Mathf.Round(chanceRunRedLightSlider.value * 1000) / 1000f));
    }

    void UpdateParameterValuesText()
    {
        // Update the display text for each slider value when the slider value changes
        // For integer sliders, directly show the value
        dimensionsText.text = "Dimensions: " + Mathf.RoundToInt(dimensionsSlider.value);
        stepsText.text = "Steps: " + Mathf.RoundToInt(stepsSlider.value);
        maxCarsText.text = "Max Cars: " + Mathf.RoundToInt(maxCarsSlider.value);

        // For float sliders, format to show only 3 decimal places
        spawnRateText.text = "Spawn Rate: " + Mathf.Round(spawnRateSlider.value * 1000) / 1000f;
        chanceRunYellowLightText.text = "Chance Run Yellow Light: " + Mathf.Round(chanceRunYellowLightSlider.value * 1000) / 1000f;
        chanceRunRedLightText.text = "Chance Run Red Light: " + Mathf.Round(chanceRunRedLightSlider.value * 1000) / 1000f;
    }

    // Add a delegate type for callbacks
    public delegate void ModelRunCompletedCallback();

    public void SendParametersToServer(ModelRunCompletedCallback onModelRunCompleted)
    {
        var parameters = new
        {
            dimensions = Mathf.RoundToInt(dimensionsSlider.value),
            steps = Mathf.RoundToInt(stepsSlider.value),
            max_cars = Mathf.RoundToInt(maxCarsSlider.value),
            spawn_rate = spawnRateSlider.value,
            chance_run_yellow_light = chanceRunYellowLightSlider.value,
            chance_run_red_light = chanceRunRedLightSlider.value
        };

        string jsonParameters = JsonConvert.SerializeObject(parameters);

        StartCoroutine(NetworkManager.Instance.PostRunModel(jsonParameters, success =>
        {
            if (success)
            {
                Debug.Log("Model run successfully.");
                onModelRunCompleted?.Invoke(); // Invoke callback if model run is successful
            }
            else
            {
                Debug.LogError("Failed to run model.");
            }
        }));
    }

}
