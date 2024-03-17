Here's an updated version of your README template with the necessary modifications and instructions on how to add screenshots:

---

# Repositorio de Reto TC2008B

## Description

_Include a brief description of your project here. Talk about what it does, its purpose, and what technologies it uses. This section should give someone new to your project a good idea of what it is about and the technology stack it uses._

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.x installed
- Flask installed
- Unity (specify the version, if necessary) installed
- Jupyter Notebook or JupyterLab installed

## Installation

To install the project, follow these steps:

1. Clone the repo: `git clone https://github.com/jorgebustmonttec/reto-TC2008b-agentpy`
2. Navigate to the project directory: `cd reto-TC2008b-agentpy`
3. Install required Python libraries: `pip install -r requirements.txt`

## Usage

There are two ways to run the project:

### Running the Notebook Independently

1. Navigate to the root directory of the project.
2. Open Jupyter Notebook or JupyterLab: `jupyter notebook` or `jupyter lab`.
3. Navigate to the `.ipynb` file you wish to run. For this project, open `intersection-agents.ipynb`.
4. Run the notebook cells to visualize the model independently.

### Running the Project with Unity

1. **Start the Flask Server**:
   - Navigate to the root directory of the project.
   - Run `python pythonserver.py` to start the Flask server. This server will interact with the Unity application to run the model and visualize it.
2. **Run the Unity Project**:
   - Open Unity and load the project located in your Unity project directory.
   - Once the Unity Editor is open, you'll be faced with a UI including a set of sliders, checkboxes, and a 'Send' button.
   - Adjust parameters as needed and click 'Send' to run the model in the background. The server will execute the model and return the data for visualization.

#### Adding Screenshots to README

_To add screenshots to your README file, you need to host these images online. You can use GitHub itself by uploading images to your repository or any image hosting service. Then, you can embed images using the following markdown syntax:_

![UI Screenshot](final/screenshots/UI.png "UI")

_Replace `URL_TO_IMAGE` with the actual URL of your image. For example, if you added screenshots to your repo in a folder named `screenshots`, the markdown might look like this:_

![UI Screenshot](https://pasteboard.co/StXlLOjKvIpo.png "UI Screenshot")

_Describe what each screenshot represents or instructs the user to do._

### Folders and Versions

- The project contains three folders corresponding to different stages of the project: `avance 2`, `avance 3`, and `final`.
- Use the `final` folder for the most updated versions of the scripts and Unity project.

---

For `PATH_TO_YOUR_PROJECT`, you've already given the clone command with the correct URL, so you can replace that with the exact folder name after cloning, which seems to be `reto-TC2008b-agentpy` based on your provided clone URL.

For `PATH_TO_YOUR_UNITY_PROJECT`, this would be specific to where the user decides to clone or store the Unity project on their local machine. If the Unity project is within the cloned repository, you could give a relative path from the repository root. If it's stored elsewhere, you might need to instruct users to note where they have saved or opened the Unity project and adjust the instructions accordingly.
