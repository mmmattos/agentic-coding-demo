import subprocess
import re
import os
import time
from openai import OpenAI

client = OpenAI()

WORKDIR = "project_agent_coded_go_rest_api"
FILENAME = "main.go"

os.makedirs(WORKDIR, exist_ok=True)

GOAL = """
Build a REST API in Go that stores user notes in a database.

Requirements:
- Use Go
- Use net/http
- Use SQLite with driver modernc.org/sqlite
- IMPORTANT: Import the driver EXACTLY as: _ "modernc.org/sqlite"
- Use sql.Open("sqlite", "notes.db")
- Initialize the database on startup
- Create the table if it does not exist
- NEVER ignore errors (no `_`)
- ALWAYS log errors
- ALWAYS return valid JSON

Endpoints:
- POST /notes → accepts { "content": "text" }
- GET /notes → returns JSON array

Constraints:
- Everything in ONE file: main.go
- Must compile and run with: go run main.go
- Server must run on port 8080
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
- Output ONLY raw Go code
- No markdown
- No explanations
- One single file
- Code MUST compile
- Use correct imports
- Ensure SQLite driver is used correctly

Previous error:
{previous_error}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return clean_code(response.output_text)


def run_go():
    process = subprocess.Popen(
        ["go", "run", FILENAME],
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


def setup_go_module(error):
    error = error or ""

    if "go.mod file not found" in error:
        print("\nInitializing Go module...")
        subprocess.run(["go", "mod", "init", "notesapi"], cwd=WORKDIR)
        return True

    return False


def install_go_dependency(error):
    error = error or ""

    match = re.search(r"no required module provides package (.+?);", error)

    if match:
        package = match.group(1)

        print(f"\nInstalling dependency: {package}")
        subprocess.run(["go", "get", package], cwd=WORKDIR)

        return True

    return False


def clean_port():
    subprocess.run(
        "lsof -ti :8080 | xargs kill -9",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


# Start clean
clean_port()

error = None

for attempt in range(6):

    print(f"\n--- Attempt {attempt + 1} ---")

    code = generate_code(GOAL, error)

    print("\nGenerated code:\n")
    print(code)

    filepath = os.path.join(WORKDIR, FILENAME)

    with open(filepath, "w") as f:
        f.write(code)

    success, process, err = run_go()

    if success:
        print("\nSUCCESS: Server started")

        if process:
            process.terminate()

        print("Server stopped.")
        break

    print("\nERROR:")
    print(err)

    if setup_go_module(err):
        continue

    if install_go_dependency(err):
        continue

    error = err