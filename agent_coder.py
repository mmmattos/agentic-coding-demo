import subprocess
from openai import OpenAI

client = OpenAI()

GOAL = "Write a Python script that prints the first 10 Fibonacci numbers."

FILENAME = "generated_script.py"


def generate_code(goal, previous_error=None):

    prompt = f"""
You are an autonomous coding agent.

Goal:
{goal}

Write a complete Python script.

If there was a previous error, fix it.

Error:
{previous_error}

Only output the code.
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text

def clean_code(code):
    code = code.replace("```python", "")
    code = code.replace("```", "")
    return code.strip()

def run_code():

    result = subprocess.run(
        ["python", FILENAME],
        capture_output=True,
        text=True
    )

    return result.returncode, result.stdout, result.stderr


for attempt in range(5):

    print(f"\n--- Attempt {attempt+1} ---")

    code = generate_code(GOAL)
    code = clean_code(code)
    print("\nGenerated code:\n")
    print(code)

    with open(FILENAME, "w") as f:
        f.write(code)

    rc, out, err = run_code()

    if rc == 0:
        print("SUCCESS")
        print(out)
        break
    else:
        print("ERROR")
        print(err)