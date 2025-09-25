# SafeChatter Conversational Scam Detector

This project provides a real-time conversational scam detection service powered by the `DeBERTa` embedding-based model and the `mistral-nemo:12b` LLM running locally via Ollama. It exposes a user-friendly web interface built with Gradio for easy interaction.

## System Requirements

This application is designed to run on a powerful, GPU-accelerated machine. The recommended environment is a dedicated cloud instance.

*   **Cloud Provider:** AWS
*   **EC2 Instance Type:** `ml.g5.12xlarge`
    *   **Reasoning:** This instance provides multiple NVIDIA A10G GPUs with sufficient VRAM, which are necessary to run the `mistral-nemo:12b` model with good performance. An equivalent machine should have at least one NVIDIA GPU with 24GB+ of VRAM (e.g., A10G, A100, RTX 3090/4090).

*   **Amazon Machine Image (AMI):** It is highly recommended to use the **AWS Deep Learning AMI (Ubuntu version)**. This image comes pre-installed with the necessary NVIDIA drivers, CUDA toolkit, and Python environments, which greatly simplifies the setup process.

*   **Software:** Python 3.8+ and Git.


## Installation

The installation process is streamlined using a single shell script that handles all system and Python dependencies.

1.  **Clone the Repository**
    First, clone this repository to your local machine and navigate into the project directory.
    ```bash
    # Replace <your-repo-url> with the actual URL of your repository
    git clone <your-repo-url>
    cd safechatter_tweek
    ```

2.  **Run the Installation Script**
    The `install.sh` script will install Ollama, its system dependencies, and all required Python packages. Make the script executable and then run it.
    ```bash
    chmod +x install.sh
    ./install.sh
    ```
    > **Note:** This script will prompt for your password to install system packages using `sudo`.

## Running the Application

Running the SafeChatter service requires **four separate terminal windows** to manage the different components of the application. Please follow these steps in order.

---

### **1. Terminal 1: Start the Ollama Service**

The installation script installs Ollama, but you need to start its server. This server must remain running in the background for the application to function.

```bash
ollama serve
```
You can leave this terminal open to monitor the Ollama server logs.

---

### **2. Terminal 2: Pull the LLM Model**

Before the application can run, you need to download the specific language model it uses from the Ollama Hub.

**Note:** You only need to perform this step once. After the model is downloaded, you don't need to do it again unless you want to update it.

```bash
ollama pull mistral-nemo:12b
```
Wait for the download to complete. You can close this terminal once it's finished.

---

### **3. Terminal 3: Run the Application Backend (Server)**

This command starts the backend logic of the SafeChatter application, which handles the processing and analysis of messages.

```bash
python api/app.py
```
Keep this terminal running.

---

### **4. Terminal 4:Run the Application Frontend (Client)**

This command starts the Gradio web interface, which connects to your backend. It will generate a live, public URL that you can use to access the application.

```bash
python api/client.py
```
After running the command, look for a public URL in the output. It will look something like this:
`Running on public URL: https://....gradio.live`

---

## Usage
Once all four services are running as described above, you can access the SafeChatter application.

1.  Copy the public URL (e.g., `https://....gradio.live`) from the output of Terminal 4.
2.  Paste this URL into your web browser on your local computer.
3.  You can now use the SafeChatter interface to input messages and receive real-time scam analysis.