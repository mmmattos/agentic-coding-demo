import subprocess
import re
import os
import time
from openai import OpenAI

client = OpenAI()

WORKDIR = "project_agent_coded_typescript_rest_api"
FILENAME = "server.ts"

os.makedirs(WORKDIR, exist_ok=True)

GOAL = """
Build a REST API using Node.js and TypeScript that stores user notes.

Requirements:
- Use Express
- Use SQLite (sqlite3)
- Use CommonJS (require syntax ONLY)
- Initialize database on startup
- Create table if not exists
- NEVER ignore errors
- ALWAYS return JSON

Endpoints:
- POST /notes
- GET /notes

Constraints:
- ONE file: server.ts
- Must run with ts-node
- Port 3000
"""


# -------------------------
# Helpers
# -------------------------

def clean_code(code):
    code = re.sub(r"```[a-zA-Z]*", "", code)
    code = code.replace("```", "")
    return code.strip()


def run_shell(cmd):
    full_cmd = f"""
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
    nvm use 24 >/dev/null
    {cmd}
    """

    return subprocess.run(
        full_cmd,
        cwd=WORKDIR,
        shell=True,
        executable="/bin/zsh"
    )


def generate_code(goal, previous_error=None):
    prompt = f"""
You are an autonomous coding agent.

Goal:
{goal}

Rules:
- Output ONLY raw TypeScript
- No markdown
- Use CommonJS (require)
- Must run with ts-node

Previous error:
{previous_error}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return clean_code(response.output_text)


# -------------------------
# Environment Setup
# -------------------------

def ensure_npm():
    package_json = os.path.join(WORKDIR, "package.json")

    if not os.path.exists(package_json):
        print("\nInitializing npm...")
        run_shell("npm init -y")

    print("\nInstalling dependencies...")
    run_shell("npm install express sqlite3 body-parser")
    run_shell("npm install -D ts-node typescript @types/node @types/express")

    # ✅ Idempotent tsconfig (DO NOT overwrite if exists)
    tsconfig_path = os.path.join(WORKDIR, "tsconfig.json")

    if not os.path.exists(tsconfig_path):
        print("\nCreating tsconfig.json...")

        with open(tsconfig_path, "w") as f:
            f.write("""{
  "compilerOptions": {
    "target": "es6",
    "module": "commonjs",
    "esModuleInterop": true,
    "strict": false,
    "skipLibCheck": true,
    "types": ["node"]
  }
}
""")
    else:
        print("\ntsconfig.json already exists — preserving it.")


def clean_port():
    subprocess.run(
        "lsof -ti :3000 | xargs kill -9",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


# -------------------------
# Execution
# -------------------------

def run_typescript():
    process = subprocess.Popen(
        f"""
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
        nvm use 24 >/dev/null
        npx ts-node {FILENAME}
        """,
        cwd=WORKDIR,
        shell=True,
        executable="/bin/zsh",
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


# -------------------------
# Main Loop
# -------------------------

clean_port()
ensure_npm()

error = None

for attempt in range(5):

    print(f"\n--- Attempt {attempt + 1} ---")

    code = generate_code(GOAL, error)

    print("\nGenerated code:\n")
    print(code)

    with open(os.path.join(WORKDIR, FILENAME), "w") as f:
        f.write(code)

    success, process, err = run_typescript()

    if success:
        print("\nSUCCESS: Server started")

        if process:
            process.terminate()

        print("Server stopped.")
        break

    print("\nERROR:")
    print(err)

    error = err