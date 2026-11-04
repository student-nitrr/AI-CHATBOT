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
- Optional Groq function-calling mode
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

## Configure Groq Mode (recommended)

1. Create a Groq API key from [Groq Console](https://console.groq.com/keys).
2. Open the `.env` file in the project root.
3. Add your key and model configuration:

```env
AI_PROVIDER=groq
GROQ_API_KEY=your_real_groq_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

4. Install the dependencies with `pip install -r requirements.txt`.
5. Restart Streamlit and select **Groq Mode** in the sidebar.

## Configure Groq on Streamlit Community Cloud

Open your app's **Manage app → Settings → Secrets** and add:

```toml
AI_PROVIDER = "groq"
GROQ_API_KEY = "your_real_groq_key_here"
GROQ_MODEL = "llama-3.3-70b-versatile"
```

Save the secrets and restart the app if it does not restart automatically. The API key is read from Streamlit Secrets at runtime; it should never be committed to GitHub.

## Configure OpenAI Mode (optional)

1. Create an API key from [OpenAI API keys](https://platform.openai.com/api-keys).
2. Add the following to your `.env` file:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=your_real_key_here
OPENAI_MODEL=gpt-5.4-mini
```

3. Restart Streamlit and select **OpenAI Mode** in the sidebar.

You can select **Demo Mode** whenever you want to use the free local intent detector. The app displays an error if a selected provider is not configured or its request fails; it does not silently switch to Demo Mode.

Never upload `.env` to GitHub or share your API key. API usage and quotas depend on the provider and account.


## Project files

- `app.py`: Streamlit interface
- `agent.py`: intent detection and function-calling agent
- `database.py`: SQLite operations
- `styles.py`: custom interface design
- `.env.example`: configuration example
- `requirements.txt`: Python packages
