# LLM-Park 🤖

A secure and private chatbot tool. This Streamlit app provides a chat experience similar to ChatGPT, but with the advantage of hosting it on-premises, ensuring complete privacy and security for user conversations.

## Setup Instructions 🚀

Follow these simple steps to set up LLM Park on your local system:

1. **Clone Repository**: Begin by cloning this repository to your local system.

2. **Create Conda Environment** (optional but recommended): Set up a Conda environment for isolating dependencies.

3. **Install Dependencies**: Install the necessary Python packages using the following command:
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure Settings**:
* Open the `setup.yaml` file.
* Adjust parameters according to your preferences.
  * The crucial parameter is `MODEL_MAP`, which contains model names and their base URLs. This dictates the available model choices.
  * Set one of the choices as default.
  * Use `MODEL_DISPLAY_MAP` to customize how model names are displayed in the app.
6. **Provide API Token (if applicable)**:
* If using an external LLM provider like OpenAI, provide the API token in the `secret.env` file.
* For locally hosted LLMs, leave the `secret.env` file with an `empty` string.
* Do not leave the API key blank to avoid errors.

7. **Run the Application**: Execute the following command to launch the application:
    ```bash
    streamlit run streamlit_app.py
    ```
   By default, the app will be hosted at port `3032`. If you wish to customize the hosting settings, refer to the configuration file located inside the `.streamlit` directory.


---

📌 For additional information or bug reports, please open an issue. Feedback is welcome!
