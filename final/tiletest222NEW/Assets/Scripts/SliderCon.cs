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
    public Slider greenDurationSlider;
    public Toggle smartLightToggle;
    public Toggle InfiniteCarsToggle;
    public Toggle AlwaysRunRedToggle;
    public Toggle AlwaysRunYellowToggle;

    public Text dimensionsText;
    public Text stepsText;
    public Text maxCarsText;
    public Text spawnRateText;
    public Text chanceRunYellowLightText;
    public Text chanceRunRedLightText;
    public Text greenDurationText;


    void Start()
    {
        // Set min and max values for sliders

        //dimensions slider (4 to 50, inclusive, integer values only)
        dimensionsSlider.minValue = 6;
        dimensionsSlider.maxValue = 60;

        //steps slider (1 to 500, inclusive, integer values only)
        stepsSlider.minValue = 1;
        stepsSlider.maxValue = 500;

        //max cars slider (1 to 65, inclusive, integer values only)
        maxCarsSlider.minValue = 1;
        maxCarsSlider.maxValue = 70;


        //spawn rate slider (0 to 1, inclusive, in increments of 0.01)
        spawnRateSlider.minValue = 0;
        spawnRateSlider.maxValue = 1;

        //chance run yellow light slider (0 to 1, inclusive, in increments of 0.01)
        chanceRunYellowLightSlider.minValue = 0;
        chanceRunYellowLightSlider.maxValue = 0.5f;

        //chance run red light slider (0 to 1, inclusive, in increments of 0.01)
        chanceRunRedLightSlider.minValue = 0;
        chanceRunRedLightSlider.maxValue = 0.1f;

        //green duration slider (5 to 50, inclusive, integer values only)
        greenDurationSlider.minValue = 5;
        greenDurationSlider.maxValue = 50;


        // Initialize slider values (optional if you want other defaults)
        dimensionsSlider.value = 12;
        stepsSlider.value = 100;
        maxCarsSlider.value = 10;
        spawnRateSlider.value = 0.5f;
        chanceRunYellowLightSlider.value = 0.2f;
        chanceRunRedLightSlider.value = 0.01f;
        greenDurationSlider.value = 15;

        // Subscribe to the onValueChanged event
        dimensionsSlider.onValueChanged.AddListener(delegate { UpdateParameterValuesText(); });
        stepsSlider.onValueChanged.AddListener(delegate { UpdateParameterValuesText(); });
        maxCarsSlider.onValueChanged.AddListener(delegate { UpdateParameterValuesText(); });
        spawnRateSlider.onValueChanged.AddListener(delegate { UpdateParameterValuesText(); });
        chanceRunYellowLightSlider.onValueChanged.AddListener(delegate { UpdateParameterValuesText(); });
        chanceRunRedLightSlider.onValueChanged.AddListener(delegate { UpdateParameterValuesText(); });
        greenDurationSlider.onValueChanged.AddListener(delegate { UpdateParameterValuesText(); });

        InfiniteCarsToggle.onValueChanged.AddListener(delegate { ToggleInfiniteCars(); });
        AlwaysRunRedToggle.onValueChanged.AddListener(delegate { ToggleAlwaysRunRed(); });
        AlwaysRunYellowToggle.onValueChanged.AddListener(delegate { ToggleAlwaysRunYellow(); });

        dimensionsSlider.wholeNumbers = true;
        stepsSlider.wholeNumbers = true;
        maxCarsSlider.wholeNumbers = true;
        greenDurationSlider.wholeNumbers = true;


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
        Debug.Log("Green Duration: " + Mathf.RoundToInt(greenDurationSlider.value));
        Debug.Log("Smart Lights: " + smartLightToggle.isOn);
    }

    void UpdateParameterValuesText()
    {

        dimensionsText.text = "Dimensions: " + Mathf.RoundToInt(dimensionsSlider.value);
        stepsText.text = "Steps: " + Mathf.RoundToInt(stepsSlider.value);
        maxCarsText.text = InfiniteCarsToggle.isOn ? "Infinite Cars enabled" : "Max Cars: " + Mathf.RoundToInt(maxCarsSlider.value);
        greenDurationText.text = "Green Duration: " + Mathf.RoundToInt(greenDurationSlider.value);
        spawnRateText.text = "Spawn Rate: " + Mathf.Round(spawnRateSlider.value * 1000) / 1000f;


        // The spicy conditional updates. these are displayed as percentages
        if (!AlwaysRunRedToggle.isOn) // Only update this if the toggle is off
            chanceRunRedLightText.text = "Chance Run Red Light: " + ((Mathf.Round(chanceRunRedLightSlider.value * 1000) / 1000f) * 100) + "%%%";
        if (!AlwaysRunYellowToggle.isOn) // Only update this if the toggle is off
            chanceRunYellowLightText.text = "Chance Run Yellow Light: " + ((Mathf.Round(chanceRunYellowLightSlider.value * 1000) / 1000f) * 100) + "%%%";
    }


    // Add a delegate type for callbacks
    public delegate void ModelRunCompletedCallback();

    public void SendParametersToServer(ModelRunCompletedCallback onModelRunCompleted)
    {
        float spawn_rate_to_send;
        float yellow_chance_to_send;
        float red_chance_to_send;

        //check what toggles are on and off to send the correct value
        spawn_rate_to_send = InfiniteCarsToggle.isOn ? 999 : Mathf.Round(spawnRateSlider.value * 1000) / 1000f;
        yellow_chance_to_send = AlwaysRunYellowToggle.isOn ? 1 : Mathf.Round(chanceRunYellowLightSlider.value * 1000) / 1000f;
        red_chance_to_send = AlwaysRunRedToggle.isOn ? 1 : Mathf.Round(chanceRunRedLightSlider.value * 1000) / 1000f;
        var parameters = new
        {
            dimensions = Mathf.RoundToInt(dimensionsSlider.value),
            steps = Mathf.RoundToInt(stepsSlider.value),
            max_cars = Mathf.RoundToInt(maxCarsSlider.value),
            spawn_rate = spawn_rate_to_send,
            chance_run_yellow_light = yellow_chance_to_send,
            chance_run_red_light = red_chance_to_send,
            smart_lights = smartLightToggle.isOn,
            green_duration = Mathf.RoundToInt(greenDurationSlider.value)
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

    void ToggleInfiniteCars()
    {
        maxCarsSlider.value = InfiniteCarsToggle.isOn ? 999 : 10; // Default value
        maxCarsSlider.interactable = !InfiniteCarsToggle.isOn;
        maxCarsText.text = InfiniteCarsToggle.isOn ? "Infinite Cars enabled" : "Max Cars: " + maxCarsSlider.value;
    }

    void ToggleAlwaysRunRed()
    {
        chanceRunRedLightSlider.value = AlwaysRunRedToggle.isOn ? 1 : 0.03f; // Default value
        chanceRunRedLightSlider.interactable = !AlwaysRunRedToggle.isOn;
        chanceRunRedLightText.text = AlwaysRunRedToggle.isOn ? "Will ignore red lights" : "Chance Run Red Light: " + chanceRunRedLightSlider.value;

    }

    void ToggleAlwaysRunYellow()
    {
        chanceRunYellowLightSlider.value = AlwaysRunYellowToggle.isOn ? 1 : 0.3f; // Default value
        chanceRunYellowLightSlider.interactable = !AlwaysRunYellowToggle.isOn;
        chanceRunYellowLightText.text = AlwaysRunYellowToggle.isOn ? "Will ignore yellow lights" : "Chance Run Yellow Light: " + chanceRunYellowLightSlider.value;
    }

}
