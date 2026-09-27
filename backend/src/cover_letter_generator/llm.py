from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

client = OpenAI()

def generate(messages):
    stream = client.responses.create(model="gpt-4.1-mini", input=messages, stream=True)
    for event in stream:
        if event.type == "response.output_text.delta":
            yield event.delta