# TaskBot AI — Beginner Run Guide

This guide assumes you are using Windows. Linux commands are included at the end.

---

## 1. Extract the project

1. Download `TaskBot_AI_Complete_Project.zip`.
2. Right-click it.
3. Select **Extract All**.
4. Open the extracted `TaskBot_AI` folder.

The folder should contain:

```text
TaskBot_AI/
├── app.py
├── agent.py
├── database.py
├── styles.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── RUN_GUIDE.md
```

---

## 2. Install Python

Install Python 3.11 or newer.

During installation on Windows, select:

```text
Add Python to PATH
```

Check the installation:

```powershell
py --version
```

You should see a Python version.

---

## 3. Open PowerShell in the project folder

In File Explorer:

1. Open the `TaskBot_AI` folder.
2. Click the address bar.
3. Type `powershell`.
4. Press Enter.

PowerShell should open in the correct project folder.

---

## 4. Create a virtual environment

Run:

```powershell
py -m venv .venv
```

Explanation:

- `py` starts Python.
- `-m venv` asks Python to create an isolated environment.
- `.venv` is the environment folder name.

---

## 5. Activate the virtual environment

Run:

```powershell
.venv\Scripts\Activate.ps1
```

After activation, PowerShell should begin with:

```text
(.venv)
```

If PowerShell blocks the command, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

This temporary policy applies only to the current PowerShell window.

---

## 6. Install packages

Run:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The second command reads `requirements.txt` and installs:

- Streamlit for the interface
- python-dotenv for `.env`
- dateparser for phrases such as tomorrow and Friday
- OpenAI for optional real AI mode

---

## 7. Create the environment file

Run:

```powershell
Copy-Item .env.example .env
```

The application works immediately in free demo mode.

Your `.env` initially contains:

```env
USE_OPENAI=false
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5.4-mini
```

Do not put `.env` on GitHub.

---

## 8. Start the project

Run:

```powershell
streamlit run app.py
```

A browser should open automatically.

If it does not open, visit the local address printed in PowerShell, normally:

```text
http://localhost:8501
```

---

## 9. Test the chatbot

Try these commands one at a time:

```text
Add project report for tomorrow
```

```text
Show my pending tasks
```

```text
Complete project report
```

```text
Show my completed tasks
```

```text
Delete project report
```

The **Agent activity** box shows the intention and tool selected by the chatbot.

---

## 10. Enable real OpenAI agent mode (optional)

The free demo mode is sufficient to run and present the project.

For better natural-language understanding, open `.env` in Notepad and change it to:

```env
USE_OPENAI=true
OPENAI_API_KEY=your_actual_api_key
OPENAI_MODEL=gpt-5.4-mini
```

Save `.env`, stop Streamlit with `Ctrl + C`, and start it again:

```powershell
streamlit run app.py
```

Never share your API key in screenshots or upload it to GitHub.

---

# What each file does

## `app.py`

This is the main application.

Important sections:

- `st.set_page_config(...)` sets the browser title and wide layout.
- `inject_css(st)` loads the attractive design.
- `init_db()` creates the SQLite table automatically.
- `render_sidebar()` displays example commands and the active mode.
- `render_hero()` displays the gradient header.
- `render_stats()` displays total, pending, and completed counters.
- `render_chat_tab()` creates the chatbot interface.
- `render_tasks_tab()` creates the visual task dashboard.
- `process_message(...)` sends the command to the agent.

## `agent.py`

This is the agent brain.

Important sections:

- `TOOLS` describes the four actions available to the AI.
- `_execute_tool(...)` connects tool names to database functions.
- `_openai_agent(...)` uses OpenAI function calling.
- `_demo_agent(...)` provides a free local version.
- `process_message(...)` selects OpenAI mode or demo mode.

The four tools are:

```text
add_task
list_tasks
complete_task
delete_task
```

## `database.py`

This file manages SQLite.

Important functions:

- `init_db()` creates the database.
- `add_task()` inserts a task.
- `list_tasks()` reads tasks.
- `complete_task()` updates task status.
- `delete_task()` removes a task.
- `get_stats()` calculates dashboard numbers.

The database file `taskbot.db` is created automatically after the first run.

## `styles.py`

This file contains CSS for:

- Gradient background
- Hero banner
- Sidebar
- Chat cards
- Task cards
- Dashboard counters
- Buttons
- Agent activity panel

## `requirements.txt`

This lists the packages that `pip` must install.

## `.env`

This stores settings and the optional API key.

---

# Stop and restart the application

Stop it:

```text
Ctrl + C
```

Start it again:

```powershell
streamlit run app.py
```

---

# Run it later

Whenever you reopen the project:

```powershell
cd path\to\TaskBot_AI
.venv\Scripts\Activate.ps1
streamlit run app.py
```

You do not need to reinstall the packages every time.

---

# Command Prompt alternative

Use these commands in Command Prompt:

```bat
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

---

# Linux or Kali Linux

Open Terminal in the project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

If Kali says the `venv` module is unavailable:

```bash
sudo apt update
sudo apt install python3-venv -y
```

Then repeat the commands above.

---

# Common errors

## `streamlit is not recognized`

Activate `.venv` and use:

```powershell
python -m streamlit run app.py
```

## `No module named streamlit`

Run:

```powershell
pip install -r requirements.txt
```

## PowerShell script execution error

Run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

## API authentication error

Either correct the API key or return to free mode:

```env
USE_OPENAI=false
```

## Port 8501 is busy

Run:

```powershell
streamlit run app.py --server.port 8502
```

Then open:

```text
http://localhost:8502
```
