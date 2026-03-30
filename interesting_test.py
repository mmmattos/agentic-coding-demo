from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-4.1-mini",
    input="Explain agentic AI in one paragraph."
)

print(response.output_text)