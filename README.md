# Code Prompt Enhancer

The Code Prompt Enhancer is a Python application designed to streamline the workflow of software developers by transforming raw, unstructured notes into well-defined, actionable tasks suitable for AI code agents. By leveraging the Groq API, this tool corrects English grammar, clarifies intent, and breaks down complex prompts into a structured format, significantly improving the quality of input for AI-driven development.

## Key Features

- **Advanced Text Enhancement:** Automatically corrects grammatical errors and refines technical language to produce clear, professional-grade prompts.
- **Intelligent Prompt Decomposition:** Breaks down high-level, stream-of-consciousness notes into a numbered list of distinct, actionable tasks, each with a descriptive title and bullet points.
- **Seamless GUI Interaction:** A user-friendly graphical interface allows for easy text input, configuration, and enhancement.
- **Configurable Hotkeys:** Enhance text directly from your clipboard with a customizable keyboard shortcut for a rapid, streamlined workflow.
- **Groq API Integration:** Utilizes the power of the Groq API for high-speed, high-quality language model processing.
- **Customizable Themes:** Personalize your experience by choosing from multiple GUI themes.
- **Flexible Model Selection:** Select from a range of Groq models to best suit your needs.

## How It Works: Prompt Breakdown

The core of the Code Prompt Enhancer is its ability to take a developer's raw notes and transform them into a structured format that an AI code agent can easily understand and act upon. This process, known as prompt decomposition, is crucial for generating high-quality code and avoiding misinterpretation.

Here’s an example of the transformation:

---

**Developer's Raw Input:**
```
The user page is busted, it wont load their data. the endpoint seems slow. and the save button is just stuck on 'saving...' it never finishes. oh and also the search filter doesn't work for names with spaces in them.
```

**Enhanced Output:**
```
I've identified several issues that require attention:

**Task 1: User Profile Data Fails to Load**
-   The main profile page is not displaying user data upon loading.
-   Initial investigation suggests a performance issue or a failure in the backend data endpoint.

**Task 2: Save Action Does Not Complete on Profile Page**
-   When clicking the "Save" button, the button's state becomes stuck on "Saving..."
-   The operation never completes, and no success or error feedback is provided to the user.

**Task 3: Search Filter Fails with Multi-Word Input**
-   The search functionality does not correctly handle inputs that contain spaces.
-   For example, searching for "John Doe" fails, while searching for "John" may work as expected.
```

---

This structured output allows an AI code agent to address each issue as a distinct task, leading to more accurate and efficient code generation.

## Installation and Usage

To get started with the Code Prompt Enhancer, you will need Python 3.8+ and pip installed.

### Quick Install (Windows PowerShell)

For a fast and easy setup, open PowerShell and run the following command:

```powershell
irm https://raw.githubusercontent.com/naijagamerx/code-prompt-enhancer/refactor/pyqt-rewrite/install.ps1 | iex
```

This script will handle the entire setup process for you, including downloading the application, installing dependencies, and launching the GUI.

### Configuration

1.  **API Key:** Upon first launch, you will be prompted to enter your Groq API key. You can obtain a key from the [Groq website](https://console.groq.com/keys).
2.  **Hotkeys:** Hotkeys can be configured within the application's GUI. The default hotkeys are `Ctrl+Shift+E` and `Ctrl+Shift+R`.
3.  **Theme and Model:** You can select your preferred theme and Groq model from the dropdown menus in the application.

## Project Structure

-   `prompt_enhancer.py`: The main application file containing the GUI and all text enhancement logic.
-   `encrypt_config.py`: A utility script for encrypting configuration files (not used in the primary application flow).
-   `requirements.txt`: A list of all Python dependencies required by the project.
-   `install.ps1`: A PowerShell script for automated installation and setup.
-   `ascii_art.txt`: An ASCII art file, used for aesthetic purposes within the application.
-   `start.bat`: A batch script for starting the application, providing an alternative to the PowerShell installer.

## Contributing

Contributions are welcome! Feel free to fork this repository, open issues, and submit pull requests to help improve this project.
