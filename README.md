# Smart Home Control System

## Overview

This project implements a basic smart home control system that allows users to interact with virtual devices such as lights, fans, and thermostats through natural language commands. The system utilizes a language model (specifically, `deepseek-coder-1.3b-instruct`) to parse user commands and translate them into actionable instructions for the smart home devices. For testing purposes or in environments where the language model dependencies are not desired, a simplified "dummy" command parser is also included.

## Features

* **Device Control:** Supports turning lights on and off, setting fan speeds (off, low, medium, high), and adjusting thermostat temperatures (within a range of 18°C to 30°C).
* **Natural Language Command Parsing:** Leverages a pre-trained language model to understand user commands expressed in plain English.
* **Dummy Parser Option:** Includes a basic command parser for testing and development without the need for language model dependencies.
* **Status Reporting:** Enables users to query the current status of all smart home devices.
* **Interactive Command Line Interface (CLI):** Provides a simple text-based interface for users to input commands and receive feedback.
* **Demo Mode:** Offers a pre-programmed sequence of commands to showcase the system's capabilities.
* **Automatic Dependency Installation:** Attempts to automatically install the necessary `transformers` and `torch` libraries if they are not already present in the environment.

## Getting Started

### Prerequisites

* **Python 3.9 or higher:** This project is written in Python and requires a compatible version to run.
* **pip:** The Python package installer, which is usually included with Python installations.

### Installation

1.  **Clone the repository** (if applicable) or save the provided Python script (`smart_home.py`) to your local machine.

2.  **Install dependencies:** If you intend to use the natural language command parsing feature, the system will attempt to install the necessary libraries (`transformers` and `torch`) upon the first run. Ensure your environment has internet access for this process. Alternatively, you can manually install them by navigating to the project directory in your terminal and running:

    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

You can run the `smart_home.py` script from your terminal using the Python interpreter:

```bash
python smart_home.py
```

#### Optional Arguments

* **`--test`:** To use the simplified "dummy" command parser for testing purposes, run the script with this argument:

    ```bash
    python smart_home.py --test
    ```

    The list of commands accepted in test mode is:

    * `turn on the light`
    * `set the fan speed to high`
    * `set the thermostat to 24`
    * `get the status`
    * `turn off the light and set temperature to 20`
    * `invalid command`

* **`--demo`:** To run the application in demo mode, which executes a predefined set of commands, use this argument:

    ```bash
    python smart_home.py --demo
    ```

#### Interactive Mode

If no optional arguments are provided, the application will start in interactive mode, prompting you to enter commands. Type your commands and press Enter. To exit the application, type `exit` or `quit`.

## Usage Examples

In the interactive mode, you can enter commands similar to those available in test mode. The system will attempt to parse the command and provide feedback on the action taken.

## Notes

* The first time the application is run without the `--test` flag, it may take some time to download the pre-trained language model.
* The performance of the natural language command parsing depends on the capabilities of the loaded language model.
* The "dummy" command parser only understands a limited set of predefined commands.

## Contributing

If you'd like to contribute to this project, please feel free to submit a pull request.

## License

MIT License

Copyright (c) 2025 Luca Alfano

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
