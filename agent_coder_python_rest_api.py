import subprocess
import re
import os
import time
import sys
from openai import OpenAI

client = OpenAI()

WORKDIR = "project_agent_coded_python_rest_api"
FILENAME = "app.py"

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


def generate_code(goal, previous_error=None):
    prompt = f"""
You are an autonomous coding agent.

Goal:
{goal}

Rules:
- Output ONLY raw Python code
- No markdown
- One file only
- Must run with: python app.py

Previous error:
{previous_error}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return clean_code(response.output_text)


# ✅ CRITICAL FIX HERE
def run_code():
    python_exec = sys.executable  # ← THIS is the fix

    process = subprocess.Popen(
        [python_exec, FILENAME],
        cwd=WORKDIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    time.sleep(3)

    if process.poll() is None:
        print("\nServer appears to be running.")
        return True, process, ""

    stdout, stderr = process.communicate()

    print("\nProcess exited:")
    print(stdout)
    print(stderr)

    return False, None, stderr


def install_missing_package(error):
    if not error:
        return False

    match = re.search(r"No module named '(.+?)'", error)

    if match:
        package = match.group(1)

        print(f"\nInstalling missing package: {package}")

        subprocess.run(
            [sys.executable, "-m", "pip", "install", package]
        )

        return True

    return False


def clean_port():
    subprocess.run(
        "lsof -ti :8000 | xargs kill -9",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


# -------------------------
# Main Loop
# -------------------------

clean_port()

error = None

for attempt in range(5):

    print(f"\n--- Attempt {attempt + 1} ---")

    code = generate_code(GOAL, error)

    print("\nGenerated code:\n")
    print(code)

    with open(os.path.join(WORKDIR, FILENAME), "w") as f:
        f.write(code)

    success, process, err = run_code()

    if success:
        print("\nSUCCESS: Server started")

        if process:
            process.terminate()

        print("Server stopped.")
        break

    print("\nERROR:")
    print(err)

    if install_missing_package(err):
        error = err
        continue

    error = err