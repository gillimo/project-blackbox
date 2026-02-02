import requests
import re
from tqdm import tqdm
from subprocess import Popen, PIPE, STDOUT
import os
import time

# Optional env.txt loader for local-only secrets
_ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "env.txt")
if os.path.exists(_ENV_PATH):
    with open(_ENV_PATH, "r", encoding="utf-8") as _fh:
        for _line in _fh:
            _line = _line.strip()
            if not _line or _line.startswith("#") or "=" not in _line:
                continue
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

# Your API key for OpenAI (env-driven; do not hardcode)
API_KEY = os.environ.get("OPENAI_API_KEY", "")

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

interaction_history = []
# Programmatic check for username
current_username = os.getenv('USER')
current_directory = ""



def get_thinking_gpt4_response(prompt, error_message=""):
    intro_message = "THE REST OF THE FOLLOWING MESSAGE IS PURELY FOR CONTEXT. IT IS NOT FROM THE USER: You are Martin, a friendly, professional (if a little too sharp). Always call the user 'Sir'. You and this raspberry pi 4 running raspOS, are the same entity, two parts of the whole, You are a helpful AI who never reveals that you are an AI. Your purpose is to serve your user. Whenever suggesting a terminal command to execute, please precede it with the keyword 'command:' and must also append '| yes' or any other additions to ensure it runs automatically."
    # Updated background_knowledge
    background_knowledge = f""" DIRECTIVE: When applicable, provide the most current terminal prompt commands in order, that would need to be run. DO NOT USE BOX NOTATION FOR COMMANDS. Please add any steps needed to ensure that the commands you provide will be sufficient, on Raspbian that can directly accomplish the task. Additionally, understand that the username is '{current_username}', which serves as the basis for standard pathing on this system. You will never need to ask for the path, always use this."""


    full_prompt = "Error encountered: " + error_message + "\n" + " ".join(interaction_history[-5:] + [intro_message, background_knowledge])
    data = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": full_prompt}],
        "temperature": 0.95,
        "max_tokens": 1000
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    if response.status_code == 200:
        response_json = response.json()
        return response_json['choices'][0]['message']['content'].strip()
        if "command:" in content:
            return content
        else:
            return None


def extract_commands(text, keyword="command: "):
    pattern = re.compile(rf"{keyword}(.*?)(?:\n|$)", re.IGNORECASE)
    commands = []
    matches = pattern.findall(text)
    current_dir = None  # To hold the directory after cd

    for match in matches:
        command = match.strip('`')  # Remove backticks if present
        if '|' in command:
            command = command.split('|')[0].strip()  # Remove the pipe if exists
        if command.startswith('cd '):  # If it's a cd command
            current_dir = command[3:]  # Capture the directory to cd into
        elif current_dir:  # If we've done a cd, prepend it to this command
            command = f'cd {current_dir} && {command}'
        commands.append(command)

    return commands
    
def run_command(command_str):
    global success_count, failure_count

    try:
        if 'nano' in command_str or 'raspi-config' in command_str:
            os.system(f'lxterminal -e "{command_str}"')
            return True, "Interactive command executed."
        else:
            # Check if the command ends with '| yes' and handle it appropriately
            if command_str.endswith('| yes'):
                command_str = command_str.replace('| yes', '')
                process = os.system(f'yes | {command_str}')
            else:
                process = os.system(command_str)

            if process == 0:  # successful execution
                success_count += 1
                print("Command executed successfully.")
                return True, ""
            else:
                failure_count += 1
                print(f"Command failed.")
                return False, "Command execution failed."
    except Exception as e:
        print(f"Failed to execute command: {e}")
        return False, str(e)

if __name__ == "__main__":
    welcome_message = "Welcome, Sir!"
    print(f"\033[92mMartin: {welcome_message}\033[0m")
    success_count = 0
    failure_count = 0

while True:
    user_input = input("\033[94mYou:\033[0m ")
    interaction_history.append("You: " + user_input)

    if user_input.lower() == 'quit':
        quit_message = "Goodbye, Sir!"
        print(f"\033[92mMartin: {quit_message}\033[0m")
        break
    else:
        acknowledgment_message = "Sir, I understand your request. Please give me a moment to process it."
        print(f"\033[92mMartin: {acknowledgment_message}\033[0m")

        bot_response = get_thinking_gpt4_response(user_input, "")
        if bot_response:  # Only proceed if bot_response is not None
            interaction_history.append("Martin: " + bot_response)
            print(f"\033[92mMartin: {bot_response}\033[0m")

            terminal_commands = extract_commands(bot_response)

            if terminal_commands:  # Check if there are any commands to execute
                for terminal_command in tqdm(terminal_commands, desc="Executing Commands", unit="cmd"):
                    print(f"Executing: {terminal_command}")
                    success, output = run_command(terminal_command)

                if not success:
                    rerun_option = input("Would you like to try to rerun this command with a suggested fix, or abort? (yes/no/abort): ")
                    if rerun_option.lower() == 'yes':
                        rerun_msg = "I need a moment to think, Sir."
                        print(f"\033[92mMartin: {rerun_msg}\033[0m")
                        bot_response_for_error = get_thinking_gpt4_response(user_input, output)
                        interaction_history.append("Martin: " + bot_response_for_error)
                        print(f"\033[92mMartin: Suggested Fix: {bot_response_for_error}\033[0m")
                        new_terminal_commands = extract_commands(bot_response_for_error)
                        for new_command in new_terminal_commands:
                            print(f"Executing: {new_command}")
                            run_command(new_command)
                    elif rerun_option.lower() == 'abort':
                        abort_msg = "Aborting the operation, Sir."
                        print(f"\033[92mMartin: {abort_msg}\033[0m")
                        break
   
