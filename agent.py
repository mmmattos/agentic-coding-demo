from openai import OpenAI

client = OpenAI()

def planner(user_input):
    """Break the request into steps"""
    
    prompt = f"""
You are a planning agent.
Break the user request into numbered tasks.

Request: {user_input}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text


def worker(task):
    """Execute a single task"""
    
    prompt = f"""
You are a worker agent.
Complete this task clearly:

Task: {task}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text


def run_agent(user_input):

    print("\n--- PLANNER ---")
    plan = planner(user_input)
    print(plan)

    tasks = plan.split("\n")

    results = []

    print("\n--- WORKERS ---")

    for task in tasks:
        if task.strip():
            result = worker(task)
            print(f"\nTask: {task}")
            print(result)
            results.append(result)

    print("\n--- FINAL RESULT ---")

    final = "\n".join(results)
    print(final)


run_agent("Explain how solar panels work and list 3 advantages")