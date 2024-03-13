using UnityEngine;
using UnityEngine.UI;

public class MainController : MonoBehaviour
{
    // UI elements
    public GameObject slidersPanel;
    public GameObject initialButtonsPanel; // Contains Send and Print buttons
    public Button createGridButton;
    public Button runAnimationButton;
    public Button pauseButton;
    public Button stopButton;
    public Button modifyParametersButton;

    // References to other scripts
    public SliderCon sliderConScript;
    public GridPlacer gridPlacerScript;
    public CarAnimator carAnimatorScript;

    private bool isAnimationPaused = false;

    void Start()
    {
        ShowInitialUI();
    }

    void ShowInitialUI()
    {
        slidersPanel.SetActive(true);
        initialButtonsPanel.SetActive(true);
        createGridButton.gameObject.SetActive(false);
        runAnimationButton.gameObject.SetActive(false);
        pauseButton.gameObject.SetActive(false);
        stopButton.gameObject.SetActive(false);
        modifyParametersButton.gameObject.SetActive(false);
    }

    // Inside MainController script

    public void OnSendParametersClicked()
    {
        sliderConScript.SendParametersToServer(ShowGridControls); // Pass ShowGridControls as a callback
    }

    // Make ShowGridControls method public or internal if it's not already
    public void ShowGridControls()
    {
        slidersPanel.SetActive(false);
        initialButtonsPanel.SetActive(false);
        createGridButton.gameObject.SetActive(true);
        modifyParametersButton.gameObject.SetActive(true);
        pauseButton.gameObject.SetActive(false);
        stopButton.gameObject.SetActive(false);
    }


    public void OnCreateGridClicked()
    {
        gridPlacerScript.FetchAndGenerateGrid();
        ShowAnimationControls();
    }

    void ShowAnimationControls()
    {
        createGridButton.gameObject.SetActive(false);
        runAnimationButton.gameObject.SetActive(true);
        //hide pause and stop buttons
        pauseButton.gameObject.SetActive(false);
        stopButton.gameObject.SetActive(false);

        // Optional: Hide or disable the modify parameters button during animation
        modifyParametersButton.gameObject.SetActive(true);
    }

    public void OnRunAnimationClicked()
    {
        Debug.Log("Run animation clicked");
        carAnimatorScript.StartAnimation();
        ShowPauseAndStop();
    }

    void ShowPauseAndStop()
    {
        runAnimationButton.gameObject.SetActive(false);
        pauseButton.gameObject.SetActive(true);
        stopButton.gameObject.SetActive(true);
        modifyParametersButton.gameObject.SetActive(false);
    }

    public void OnPauseClicked()
    {
        isAnimationPaused = !isAnimationPaused;
        carAnimatorScript.TogglePause();
        pauseButton.GetComponentInChildren<Text>().text = isAnimationPaused ? "Resume" : "Pause";
    }

    public void OnStopClicked()
    {
        carAnimatorScript.StopAnimation();
        isAnimationPaused = false;
        ShowAnimationControls();
    }

    public void OnModifyParametersClicked()
    {
        // Clear existing grid and animations if necessary
        gridPlacerScript.ClearGrid();
        // Stop animation in case it is running
        carAnimatorScript.StopAnimation();
        ShowInitialUI();
    }
}
