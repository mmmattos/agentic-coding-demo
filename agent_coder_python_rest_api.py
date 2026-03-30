import subprocess
import re
import os
import time
from openai import OpenAI

client = OpenAI()

WORKDIR = "project_agent_coded_python_rest_api"
FILENAME = "app.py"  # ← IMPORTANT: only filename

os.makedirs(WORKDIR, exist_ok=True)

GOAL = """
Build a REST API that stores user notes in a database.

Requirements:
- Use Python
- Use FastAPI
- Use SQLite
- Endpoints:
    POST /notes
    GET /notes
Return all code in ONE Python file called app.py.
The server must run with: python app.py
"""


def clean_code(code):
    code = re.sub(r"```[a-zA-Z]*", "", code)
    code = code.replace("```", "")
    return code.strip()


def generate_code(goal, error=None):
    prompt = f"""
You are an autonomous coding agent.

Goal:
{goal}

Rules:
- Output ONLY raw Python code
- Do NOT include markdown
- Put everything in ONE file
- The server must run with: python app.py

Previous error:
{error}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return clean_code(response.output_text)


def run_code():
    process = subprocess.Popen(
        ["python", FILENAME],  # ✅ FIXED PATH
        cwd=WORKDIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    time.sleep(3)

    # server still running → success
    if process.poll() is None:
        print("\nServer appears to be running.")
        return True, process, ""

    stdout, stderr = process.communicate()
    return False, None, stderr


def install_missing_package(error):
    error = error or ""

    match = re.search(r"No module named '(.+?)'", error)

    if match:
        pkg = match.group(1)
        print(f"\nInstalling missing package: {pkg}")
        subprocess.run(["pip", "install", pkg])
        return True

    return False


def clean_port():
    """Safely free port 8000"""
    subprocess.run(
        "lsof -ti :8000 | xargs kill -9",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


# 🔥 CLEAN ENV FIRST
clean_port()

error = None

for attempt in range(5):

    print(f"\n--- Attempt {attempt + 1} ---")

    code = generate_code(GOAL, error)

    print("\nGenerated code:\n")
    print(code)

    filepath = os.path.join(WORKDIR, FILENAME)

    with open(filepath, "w") as f:
        f.write(code)

    success, process, err = run_code()

    if success:
        print("\nSUCCESS: Server started")

        # stop server to avoid conflicts
        if process:
            process.terminate()
            print("Server stopped.")

        break

    print("\nERROR:")
    print(err)

    # install missing dependency
    if install_missing_package(err):
        continue

    error = err