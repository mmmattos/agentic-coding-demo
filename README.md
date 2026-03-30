# You’re Not Writing Code Anymore — You’re Designing Agents  
### Why senior engineers must rethink the development loop in the age of autonomous systems

---

## The Shift Is Already Happening

For decades, software engineering has been a story of abstraction:

- assembly → high-level languages  
- servers → cloud platforms  
- scripts → pipelines  

Agentic coding is the next step—but this time, the abstraction is not over infrastructure.

It is over **the act of development itself**.

> You are no longer just writing code.  
> You are designing systems that write, run, and fix code.

---

## The Moment Everything Changes

Most engineers today have used AI coding assistants.

They autocomplete. They suggest. They accelerate.

But they stop here:

```
Here is the code.
```

Agentic systems cross that boundary.

They operate in a loop:

```
Goal → Generate → Execute → Observe → Fix → Repeat
```

And crucially:

> They do not stop until the system works.

---

## Start Small: The Fibonacci Agent

Goal:

```
Write a Python script that computes Fibonacci numbers
```

```python
def generate(goal, error=None):
    return llm(goal + (f"\nFix error: {error}" if error else ""))

while True:
    code = generate("fibonacci")
    try:
        exec(code)
        break
    except Exception as e:
        error = str(e)
```

This is the smallest useful agent.

---

## The Core Loop (The Real Abstraction)

```python
while not success:
    code = generate(goal, error)
    write(code)
    rc, out, err = run()
    error = err
```

This loop is:

- a compiler  
- a debugger  
- a DevOps pipeline  
- a junior engineer  

---

## Minions vs Stripes

**Minions (WHAT):**
- run code
- install dependencies
- write files

**Stripes (HOW):**
- retry loop
- error handling
- decision flow

---

## Architecture: Minimal Autonomous Coding System

```
          +------------------+
          |       LLM        |
          +------------------+
                    ↓
          +------------------+
          |   Code Generator |
          +------------------+
                    ↓
          +------------------+
          |   File System    |
          +------------------+
                    ↓
          +------------------+
          |   Runtime        |
          +------------------+
                    ↓
          +------------------+
          |  Error Feedback  |
          +------------------+
                    ↓
               Control Loop
```

Extended with:

```
+ Dependency Installer (pip/npm/go)
+ Process Manager (servers, timeouts)
+ Retry Strategy (stripe)
```

---

## The Experiment: One Goal, Three Implementations

```
Build a REST API that stores user notes
```

The objective was not just to generate code, but to:

- execute it  
- resolve failures  
- adapt to each ecosystem  
- reach a running system autonomously  

We then applied the same loop across:

- Python (FastAPI)  
- Go (net/http)  
- TypeScript (Express)  

> The goal stayed the same. Only the environment changed.

👉 Full working implementations: https://github.com/mmmattos/agentic-coding-demo

---

## Python Agent (FastAPI)

```python
import subprocess, re, os, time
from openai import OpenAI

client = OpenAI()
WORKDIR = "python_agent"
FILENAME = os.path.join(WORKDIR, "app.py")
os.makedirs(WORKDIR, exist_ok=True)

def generate(goal, error=None):
    prompt = f"Build a FastAPI notes API. Fix errors: {error}"
    r = client.responses.create(model="gpt-4.1-mini", input=prompt)
    return r.output_text

def run():
    p = subprocess.Popen(["python", "app.py"], cwd=WORKDIR,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(3)
    if p.poll() is None:
        return 0, "", ""
    out, err = p.communicate()
    return p.returncode, out, err

def fix(err):
    m = re.search(r"No module named '(.+?)'", err)
    if m:
        subprocess.run(["pip", "install", m.group(1)])
        return True
    return False

error = None
for _ in range(5):
    code = generate("REST API", error)
    open(FILENAME, "w").write(code)
    rc, out, err = run()
    if rc == 0:
        break
    if fix(err):
        continue
    error = err
```

---

## Go Agent

```python
import subprocess, re, os, time
from openai import OpenAI

client = OpenAI()
WORKDIR = "go_agent"
FILENAME = os.path.join(WORKDIR, "main.go")
os.makedirs(WORKDIR, exist_ok=True)

def generate(goal, error=None):
    prompt = f"Build a Go REST API with net/http. Fix errors: {error}"
    r = client.responses.create(model="gpt-4.1-mini", input=prompt)
    return r.output_text

def run():
    p = subprocess.Popen(["go", "run", "main.go"], cwd=WORKDIR,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(3)
    if p.poll() is None:
        return 0, "", ""
    out, err = p.communicate()
    return p.returncode, out, err

def fix(err):
    if "go.mod file not found" in err:
        subprocess.run(["go", "mod", "init", "notesapi"], cwd=WORKDIR)
        return True
    m = re.search(r"no required module provides package (.+?);", err)
    if m:
        subprocess.run(["go", "get", m.group(1)], cwd=WORKDIR)
        return True
    return False

error = None
for _ in range(5):
    code = generate("REST API", error)
    open(FILENAME, "w").write(code)
    rc, out, err = run()
    if rc == 0:
        break
    if fix(err):
        continue
    error = err
```

---

## TypeScript Agent

```python
import subprocess, os, re, time
from openai import OpenAI

client = OpenAI()
WORKDIR = "ts_agent"
FILENAME = os.path.join(WORKDIR, "server.ts")
os.makedirs(WORKDIR, exist_ok=True)

def generate(goal, error=None):
    prompt = f"Build an Express TypeScript REST API. Fix errors: {error}"
    r = client.responses.create(model="gpt-4.1-mini", input=prompt)
    return r.output_text

def setup():
    if not os.path.exists(os.path.join(WORKDIR, "package.json")):
        subprocess.run(["npm", "init", "-y"], cwd=WORKDIR)
        subprocess.run(["npm", "install", "express", "sqlite3"], cwd=WORKDIR)
        subprocess.run(["npm", "install", "-D", "typescript", "ts-node", "@types/node", "@types/express"], cwd=WORKDIR)

def run():
    p = subprocess.Popen(["npx", "ts-node", "server.ts"], cwd=WORKDIR,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(3)
    if p.poll() is None:
        return 0, "", ""
    out, err = p.communicate()
    return p.returncode, out, err

def fix(err):
    m = re.search(r"Cannot find module '(.+?)'", err)
    if m:
        subprocess.run(["npm", "install", m.group(1)], cwd=WORKDIR)
        return True
    return False

setup()

error = None
for _ in range(5):
    code = generate("REST API", error)
    open(FILENAME, "w").write(code)
    rc, out, err = run()
    if rc == 0:
        break
    if fix(err):
        continue
    error = err
```

---

## The Real Insight

> The agent is not fixing code.  
> It is fixing the system.

Failures were environmental:

- missing dependencies  
- missing modules  
- runtime mismatches  
- process lifecycle  

---

## Closing Thought

> The hardest part of software engineering is not writing code—it’s making systems work.

Unattended agentic coding is the first serious attempt to automate that entire loop.

---

## 🔗 Full Code & Examples

👉 https://github.com/mmmattos/agentic-coding-demo


## Appendix A: Prerequisites

Make sure you have:

- Python 3.9+
- Node.js (via nvm or installed globally)
- Go (for Go agent)

Verify:

- python3 --version
- node --version
- go version


## Appendix B: Create a Python Virtual Environment

### MacOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
``` 
### Windows
```cmd
python -m venv venv
venv\Scripts\activate
```
### Install the Libraries
```bash
pip install crewai
pip install openai
``` 
Some CrewAI versions also install dependencies automatically.)


## Apendix C: Set the API Key

For the API from OpenAI.

### Mac/Linux:
```bash
export OPENAI_API_KEY="your_key_here"
``` 
### Windows

```bash
set OPENAI_API_KEY=your_key_here
```

## Appendix D: Running the Agent and Generated APIs

These appendixes complement the main README and provide step-by-step instructions to run each agent and validate the generated APIs.

---

### Python REST API

#### Generate

```bash
python agent_coder_python_rest_api.py
```

The agent will:

- Attempt up to 5 iterations to generate a working REST API  
- Install missing dependencies if needed  
- Start the server briefly to validate execution  

On success, a new directory will be created:

```
project_agent_coded_python_rest_api/
```

---

#### Run

```bash
cd project_agent_coded_python_rest_api
python app.py
```

Server will start on:

```
http://localhost:8000
```

---

#### Test

**GET /notes**

```bash
curl http://localhost:8000/notes
```

Expected:

```json
[]
```

---

**POST /notes**

```bash
curl -X POST http://localhost:8000/notes \
-H "Content-Type: application/json" \
-d '{"content": "hello python agent"}'
```

Expected:

```json
{"id":1,"content":"hello python agent"}
```

---

**GET /notes (after insert)**

```bash
curl http://localhost:8000/notes
```

Expected:

```json
[
  {"id":1,"content":"hello python agent"}
]
```

---

### GO REST API

#### Generate

```bash
python agent_coder_go_rest_api.py
```

The agent will:

- Attempt up to 5 iterations to generate a working REST API  
- Install missing dependencies if needed  
- Start the server briefly to validate execution  

On success, a new directory will be created:

```
project_agent_coded_go_rest_api/
```

---

#### Run

```bash
cd project_agent_coded_go_rest_api
go run main.go
```

Server will start on:

```
http://localhost:8080
```

---

#### Test

**GET /notes**

```bash
curl http://localhost:8080/notes
```

Expected:

```json
null
```

---

**POST /notes**

```bash
curl -X POST http://localhost:8080/notes \
-H "Content-Type: application/json" \
-d '{"content": "hello go agent"}'
```

Expected:

```json
{"id":1,"content":"hello go agent"}
```

---

**GET /notes (after insert)**

```bash
curl http://localhost:8080/notes
```

Expected:

```json
[
  {"id":1,"content":"hello go agent"}
]
```

---

### Typescript REST API

#### Generate

```bash
python agent_coder_typescript_rest_api.py
```

The agent will:

- Attempt up to 5 iterations to generate a working REST API  
- Install missing dependencies if needed  
- Start the server briefly to validate execution  

On success, a new directory will be created:

```
project_agent_coded_typescript_rest_api/
```

---

#### Run

```bash
cd project_agent_coded_typescript_rest_api
npx ts-node server.ts
```

Server will start on:

```
http://localhost:3000
```

---

#### Test

**GET /notes**

```bash
curl http://localhost:3000/notes
```

Expected:

```json
[]
```

---

**POST /notes**

```bash
curl -X POST http://localhost:3000/notes \
-H "Content-Type: application/json" \
-d '{"content": "hello typescript agent"}'
```

Expected:

```json
{"id":1,"content":"hello typescript agent"}
```

---

**GET /notes (after insert)**

```bash
curl http://localhost:3000/notes
```

Expected:

```json
[
  {"id":1,"content":"hello typescript agent"}
]
```
