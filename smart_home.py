import os
from dataclasses import dataclass
from enum import Enum
import json
import subprocess
import re
import time

# Try to import the necessary packages
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
    packages_installed = True
except ImportError as e:
    packages_installed = False
    print(f"Warning: Some necessary packages are missing: {e}")
    print("Attempting to install them now...")

# Device Classes
class FanSpeed(str, Enum):
    OFF = "off"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class Light:
    state: bool = False

@dataclass
class Fan:
    speed: FanSpeed = FanSpeed.OFF

@dataclass
class Thermostat:
    temperature: int = 22
    state: bool = False

class SmartHome:
    """
    Represents a smart home system with controllable devices.
    It manages the state of a light, a fan, and a thermostat.
    """

    def __init__(self):
	"""
        Initializes the smart home with default states for all devices.
        The light is OFF, the fan is OFF, and the thermostat is set to 22°C and is OFF.
        """

        self.light = Light() # Create an instance of the Light device
        self.fan = Fan() # Create an instance of the Fan device
        self.thermostat = Thermostat() # Create an instance of the Thermostat device

    def get_status(self):
	"""
        Returns the current status of all smart home devices.
        The status includes whether the light is ON or OFF, the fan speed,
        and the thermostat's temperature and ON/OFF state.
        """

        return {
            "light": "ON" if self.light.state else "OFF",
            "fan": self.fan.speed.value,
            "thermostat": f"{self.thermostat.temperature}°C ({'ON' if self.thermostat.state else 'OFF'})"
        }

# Command Parser
class CommandParser:
    """
    This class is responsible for taking a command in plain English
    and figuring out what actions need to be taken on the smart home devices.
    It can either use a simple built-in "dummy" brain for testing,
    or a more advanced AI model to understand more complex commands.
    """

    def __init__(self, model_name="deepseek-ai/deepseek-coder-1.3b-instruct", use_dummy_parser=False):
	"""
        CommandParseroffers the possibility to choose between
        a simple "dummy" brain or a real AI model.

        Args:
            model_name (str, optional): If using the AI model, this is the name of the model to download.
                Defaults to "deepseek-ai/deepseek-coder-1.3b-instruct".
            use_dummy_parser (bool, optional): If set to True, it uses a simple brain for testing.
                Defaults to False (which means it will try to use the AI model).
        """

        self.use_dummy_parser = use_dummy_parser
        self.model_name = model_name

        if not use_dummy_parser:
            print(f"Downloading tokenizer for {self.model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            print(f"Downloading model for {self.model_name}...")

            if torch.cuda.is_available():
                self.device = torch.device("cuda")
                print(f"CUDA is available! Using GPU for {self.model_name}.")
            else:
                self.device = torch.device("cpu")
                print(f"CUDA is not available. Using CPU for {self.model_name}.")

            self.model = AutoModelForCausalLM.from_pretrained(self.model_name).to(self.device)
            print(f"{self.model_name} model and tokenizer loaded successfully!")
        else:
            print("Using dummy command parser for testing.")

    def parse_command(self, command: str) -> list[dict]:
        """
        This is the main thinking part of the CommandParser.
        It takes a command (like "turn on the light") and transforms it into an action for the SmartHome.

        Args:
            command (str): The command given to the smart home system.

        Returns:
            list[dict]: A list of instructions in a JSON format.
                   	Each instruction is a dictionary.
                       	For example: [{"action": "turn_on", "device": "light"}]
                       	If it can't understand the command, it might return an empty list [].
        """

        if self.use_dummy_parser:
            print(f"Dummy parser received command: '{command}'")
            if command.lower() == "turn on the light":
                return [{"action": "turn_on", "device": "light"}]
            elif command.lower() == "set the fan speed to high":
                return [{"action": "set", "device": "fan", "param": "high"}]
            elif command.lower() == "set the thermostat to 24":
                return [{"action": "set", "device": "thermostat", "param": "24"}]
            elif command.lower() == "get the status":
                return [{"action": "get_status"}]
            elif command.lower() == "turn off the light and set temperature to 20":
                return [{"action": "turn_off", "device": "light"}, {"action": "set", "device": "thermostat", "param": "20"}]
            elif command.lower() == "invalid command":
                return []  # Simulate an unparsable command
            else:
                return [{"action": "unknown", "command": command}] # For other commands
        else:
            prompt = f"""You are a helpful assistant that MUST ONLY respond with a JSON list of JSON objects. Do not include any explanations, greetings, or any other extra text.

            Your task is to parse the following smart home command and return it as a JSON list of JSON objects.

            Each JSON object in the list should represent a single action and have the following format:
            {{"action": "ACTION", "device": "DEVICE", "param": OPTIONAL_PARAMETER}}

            Where:
            - ACTION can be one of: turn_on, turn_off, set, get_status.
            - DEVICE can be one of: light, fan, thermostat.
            - PARAM is only needed for the 'set' action (e.g., a speed like "low", "medium", "high" for the fan, or a temperature like "20" for the thermostat).

            Here are some examples:
            Command: Turn on the light
            JSON: [{{"action": "turn_on", "device": "light"}}]

            Command: Set the fan speed to low
            JSON: [{{"action": "set", "device": "fan", "param": "low"}}]

            Command: Set the temperature to 24
            JSON: [{{"action": "set", "device": "thermostat", "param": "24"}}]

            Command: Set temperature to 22
            JSON: [{{"action": "set", "device": "thermostat", "param": "22"}}]

            Command: Turn off the light and set temperature to 24
            JSON: [{{"action": "turn_off", "device": "light"}}, {{"action": "set", "device": "thermostat", "param": "24"}}]

            Command: Get the status
            JSON: [{{"action": "get_status"}}]

            Command: Turn on the fan and set the thermostat to 20
            JSON: [{{"action": "turn_on", "device": "fan"}}, {{"action": "set", "device": "thermostat", "param": "20"}}]

            If you cannot parse the command, return an empty JSON list: `[]`.

            Now, parse the command: "{command}" and return the JSON list of JSON objects:
            """

            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            outputs = self.model.generate(
                          **inputs
                          , max_new_tokens=50
                          , eos_token_id=self.tokenizer.eos_token_id
                        )
            response_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            try:
                json_match = re.search(r"(\[.*?\])", response_text.replace(prompt, ''), re.DOTALL)
                if json_match:
                    json_string = json_match.group(1)
                    parsed_response = json.loads(json_string)
                    return parsed_response
                else:
                    print(f"Warning: Could not find JSON in the response from {self.model_name}: '{response_text}'")
                    return {}
            except json.JSONDecodeError:
                print(f"Warning: Could not parse JSON from the response from {self.model_name}: '{response_text}'")
                return {}
            except AttributeError:
                print(f"Warning: Unexpected response format from {self.model_name}: '{response_text}'")
                return {}

# Action Handler
def handle_command(home: SmartHome, parsed_commands: list[dict]) -> str:
    """
    This function takes the instructions that the CommandParser issued
    and pass it to the SmartHome.

    Args:
        home (SmartHome): This is the object that represents our smart home
                          and knows about all the devices in it.
        parsed_commands (list[dict]): This is a list of instructions
                                     that the CommandParser created. Each instruction
                                     is a dictionary.

    Returns:
        str: A message back to the user telling them what happened
             (e.g., "Light is now ON", "Fan speed set to low",
              "Error: Invalid fan speed 'fast'").
    """

    responses = []
    for parsed in parsed_commands:
        try:
            device = parsed.get("device")
            action = parsed.get("action")

            if not device and action != "get_status":
                responses.append("Error: Could not understand the command.")
                continue

            if action == "get_status":
                responses.append("\n".join([f"{k}: {v}" for k,v in home.get_status().items()]))

            elif device == "light":
                if action == "turn_on":
                    home.light.state = True
                    responses.append("Light is now ON")
                elif action == "turn_off":
                    home.light.state = False
                    responses.append("Light is now OFF")

            elif device == "fan":
                if action == "set":
                    speed_str = parsed.get("param", "").lower()
                    try:
                        home.fan.speed = FanSpeed[speed_str.upper()]
                        responses.append(f"Fan speed set to {speed_str}")
                    except KeyError:
                        responses.append(f"Error: Invalid fan speed '{speed_str}'. Valid speeds are: {', '.join(FanSpeed.__members__)}")
                elif action == "turn_on":
                    home.fan.speed = FanSpeed.LOW  # Maybe set a default speed when turning on?
                    responses.append("Fan is now ON (set to low)")
                elif action == "turn_off":
                    home.fan.speed = FanSpeed.OFF
                    responses.append("Fan is now OFF")

            elif device == "thermostat":
                if action == "set":
                    temp_str = parsed.get("param")
                    if temp_str is not None and temp_str.isdigit():
                        temp_float = float(temp_str)
                        if 18 <= temp_float <= 30:
                            temp = int(temp_str)
                            home.thermostat.temperature = temp
                            home.thermostat.state = True
                            responses.append(f"Thermostat set to {temp}°C")
                        else:
                            responses.append("Error: Temperature Out Of Range.")
                    else:
                        responses.append("Error: Invalid temperature value.")

        except Exception as e:
            responses.append(f"Error processing command: {str(e)}")
    return '\n'.join(responses)

# CLI Interface
def main(use_dummy_parser=False, use_demo_mode=False):
    """
    This is the main part of the program.
    It sets up the smart home and the command interpreter,
    and then it either runs a little demo to show how it works,
    or lets the user type in commands.

    Args:
        use_dummy_parser (bool, optional): If this is True, it uses a simple, pretend brain
                                         for understanding commands (for testing). Defaults to False.
        use_demo_mode (bool, optional): If this is True, it runs a pre-set list of commands
                                     to showcase what the smart home can do. Defaults to False.
    """
    # Check and install missing packages only if not using the dummy parser
    if not use_dummy_parser and not packages_installed:
        try:
            print("Installing 'transformers' and 'torch'...")
            subprocess.check_call(['pip', 'install', 'transformers', 'torch'])
            print("Successfully installed 'transformers' and 'torch'. Please run the application again.")
            return  # Exit the script after installation, user needs to rerun
        except subprocess.CalledProcessError as e:
            print(f"Error during package installation: {e}")
            print("Please make sure you have 'pip' installed and try running the application again.")
            return

    home = SmartHome()
    parser = CommandParser(use_dummy_parser=use_dummy)

    if use_demo_mode:
        print("Smart Home Control System (Demo Mode)")
        demo_commands = [
            "Turn on the fan",
            "set the fan speed to high",
            "set the thermostat to 24",
            "set the thermostat to 32",
            "Turn the light and the fan on",
            "invalid command",
            "Turn the light on and the set the temperature to 26"
        ]
        for command in demo_commands:
            print(f"\nExecuting command: {command}")
            parsed = parser.parse_command(command)
            response = handle_command(home, parsed)
            print(f"Response: {response}")
            time.sleep(1) # Wait for 1 second between commands
    else:
        print("Smart Home Control System (Testing Mode)" if use_dummy_parser else "Smart Home Control System")
        while True:
            try:
                command = input("\nEnter command: ")
                if command.lower() in ["exit", "quit"]:
                    break

                parsed = parser.parse_command(command)
                response = handle_command(home, parsed)
                print(f"\n{response}")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error processing command: {e}")

if __name__ == "__main__":
    # To use the dummy parser for testing, run the script like this: python smart_home.py --test
    # To use the demo mode, run the script like this: python smart_home.py --demo
    import sys
    use_dummy = '--test' in sys.argv
    use_demo = '--demo' in sys.argv
    main(use_dummy, use_demo)
