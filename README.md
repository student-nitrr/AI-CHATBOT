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

## Configure OpenAI AI Mode

1. Create an API key from [OpenAI API keys](https://platform.openai.com/api-keys).
2. Open the `.env` file in the project root.
3. Add your key and model configuration:

```env
USE_OPENAI=true
OPENAI_API_KEY=your_real_key_here
OPENAI_MODEL=gpt-5.4-mini
```

4. Save the file and restart Streamlit.
5. In the sidebar, select **AI Mode**. Select **Demo Mode** whenever you want to use the free local intent detector.

The app remembers the selected mode while the Streamlit session is active. If AI Mode is selected without a key, the app shows a setup warning. If an OpenAI request fails, it displays the error instead of silently running the request in Demo Mode.

Never upload `.env` to GitHub or share your API key. API usage may incur separate charges; a ChatGPT subscription does not include API usage.

## Project files

- `app.py`: Streamlit interface
- `agent.py`: intent detection and function-calling agent
- `database.py`: SQLite operations
- `styles.py`: custom interface design
- `.env.example`: configuration example
- `requirements.txt`: Python packages
