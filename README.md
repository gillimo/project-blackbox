# Project Blackbox

Mission Learning Statement
- Mission: Build a resilient local automation agent with command planning and safe execution for Linux.
- Learning focus: system orchestration, guardrailed command execution, and prompt-to-action loops.
- Project start date: 2023-09-29 (inferred from earliest project timestamp)

Foundational local agent that converts user intent into executable system actions, originally run on a custom Linux Raspberry Pi build with an emulator layer and operated by the original Martin agent.

## Features

- Prompt-to-command extraction using OpenAI chat completions
- Command execution with basic success/failure tracking
- Error-driven re-run flow with suggested fixes
- Multiple historical agent snapshots (`martin.py`, `martin_oct11_stable.py`, `martin_v2_1.py`)

## Installation

### Requirements

- Python 3.8+
- `requests`
- `tqdm`

### Setup

- Set `OPENAI_API_KEY` in your environment or create a local `env.txt` next to `martin.py`.

## Quick Start

```bash
python martin.py
```

## Usage

- Type a request, receive a response, and run suggested commands.
- Enter `quit` to exit the loop.
- Use the re-run prompt to retry failed commands with suggested fixes.

## Architecture

```
User Prompt
    |
    v
Prompt Builder (context + directives)
    |
    v
OpenAI API (chat completions)
    |
    v
Command Extractor
    |
    v
Execution Engine
    |
    +--> Success -> next prompt
    |
    +--> Failure -> suggested fix -> re-run

Deployment context (historical):
- Custom Linux Raspberry Pi build
- Emulator layer for target environment
```

## Project Structure

```
martin.py              # Primary agent loop
martin_oct11_stable.py # Stable snapshot
martin_v2_1.py         # Later snapshot
```

## Building

No build step required. Run directly with Python.

## Contributing

Historical artifact. If you want to experiment, fork the repo and make changes there.

## License

No license file is included in this repository.
