from openai import OpenAI
from cover_letter_generator import cv_parser, job_parser, cover_letter
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def generate(messages):
    # The current OpenAI guidance recommends Responses API for new text-generation applications rather than Chat Completions API
    response = client.responses.create(model="gpt-4.1-mini", input=messages) 
    return response.output_text

cv = cv_parser.parse_pdf("D:/C.V/Rikesh_Mandal_CV.pdf")
job_description = job_parser.fetch_website_contents("https://jobs.ashbyhq.com/9fin/aa975e0f-eca7-45c3-a1c8-fa38c4edd45b?src=LinkedIn")
messages = cover_letter.build_messages(cv, job_description)

generate(messages)