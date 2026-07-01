# TaskBot AI

TaskBot AI is a beginner-friendly final-year agentic AI project. It is a
Streamlit chatbot that can add, list, complete, and delete tasks stored in
SQLite.

## Why it is agentic

The chatbot follows an action loop:

1. Understand the request.
2. Select a tool.
3. Execute the tool.
4. Read or update SQLite.
5. Report the result.

## Features

- Attractive Streamlit interface
- Chat-based task management
- SQLite database
- Agent activity panel
- Free local demo mode
- Optional OpenAI function-calling mode

## Commands to try

- `Add project report for tomorrow`
- `Add final presentation for Friday with high priority`
- `Show my pending tasks`
- `Complete project report`
- `Delete final presentation`

## Windows setup

Open PowerShell inside the project folder:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app.py
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

## Command Prompt setup

```bat
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

## Linux / macOS setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

## Enable OpenAI mode

Open `.env` and change:

```env
USE_OPENAI=true
OPENAI_API_KEY=your_real_key_here
OPENAI_MODEL=gpt-5.4-mini
```

Restart Streamlit after changing `.env`.

Never upload `.env` to GitHub.

## Project files

- `app.py`: Streamlit interface
- `agent.py`: intent detection and function-calling agent
- `database.py`: SQLite operations
- `styles.py`: custom interface design
- `.env.example`: configuration example
- `requirements.txt`: Python packages
