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

    // camera position buttons
    public Button cameraPosition1Button;
    public Button cameraPosition2Button;
    public Button cameraPosition3Button;




    // References to other scripts
    public SliderCon sliderConScript;
    public GridPlacer gridPlacerScript;
    public CarAnimator carAnimatorScript;

    // Reference to the CameraController script
    public CameraController cameraControllerScript;

    private bool isAnimationPaused = false;

    void Start()
    {
        ShowInitialUI();
        cameraPosition1Button.onClick.AddListener(() => SetCameraPosition(1));
        cameraPosition2Button.onClick.AddListener(() => SetCameraPosition(2));
        cameraPosition3Button.onClick.AddListener(() => SetCameraPosition(3));

        // Hide the camera buttons initially because your world isn't ready for them yet
        cameraPosition1Button.gameObject.SetActive(false);
        cameraPosition2Button.gameObject.SetActive(false);
        cameraPosition3Button.gameObject.SetActive(false);
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
        OnCreateGridClicked(); // Call this method to create the grid immediately after sending parameters
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

        // Wow, look at that, camera buttons!
        cameraPosition1Button.gameObject.SetActive(true);
        cameraPosition2Button.gameObject.SetActive(true);
        cameraPosition3Button.gameObject.SetActive(true);
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

        // Poof! And they're gone, like my interest in helping further
        cameraPosition1Button.gameObject.SetActive(false);
        cameraPosition2Button.gameObject.SetActive(false);
        cameraPosition3Button.gameObject.SetActive(false);
    }


    public void OnModifyParametersClicked()
    {
        // Clear existing grid and animations if necessary
        gridPlacerScript.ClearGrid();
        // Stop animation in case it is running
        carAnimatorScript.StopAnimation();
        ShowInitialUI();
    }

    void SetCameraPosition(int position)
    {
        // Call that method you were so proud of in the CameraController
        cameraControllerScript.SetCameraPosition(position, gridPlacerScript.GetCurrentGrid());
        // You'll need to implement GetCurrentGrid() to return the current grid array, btw. Good luck!
    }

}
