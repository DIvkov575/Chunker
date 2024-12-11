import os
import fitz
import openai
import re
from dotenv import load_dotenv


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text")
    return text

def chunk_text(text, max_tokens=4000):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1

        if current_length >= max_tokens:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_length = 0

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks


def query_openai(chunk, chunk_num, prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{prompt}\n\n{chunk}"}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        return f"gpt-3.5-turbo chunk_num:{chunk_num} (" + response['choices'][0]['message']['content'].strip() + ")"
    except Exception as e:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"{prompt}\n\n{chunk}"}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            return f"gpt-4 chunk_num:{chunk_num} (" + response['choices'][0]['message']['content'].strip() + ")"
        except Exception as e2:
            print(f"Erorr querying openai: {e2}")
            return ""


load_dotenv()
openai.api_key = os.getenv("OPENAI_KEY")
pdf_path = "Circle.pdf"
prompt = "identify quotes employing transparency as a metaphor in the following text"



print("layer 1")
text = extract_text_from_pdf(pdf_path)
chunks = chunk_text(text)
responses = []
for i, chunk in enumerate(chunks):
    print(f"Processing chunk {i + 1}/{len(chunks)}...")
    response = query_openai(chunk, i, prompt)
    responses.append(response)
aggregated_response = "\n".join(responses)

print("layer 2")

prompt = "ensure each quote identified employs transparency as a metaphor in the following text, aggregate the results, include chunk number and model as citation"
chunks = chunk_text(aggregated_response)
responses = []
for i, chunk in enumerate(chunks):
    print(f"Processing chunk {i + 1}/{len(chunks)}...")
    response = query_openai(chunk, i, prompt)
    responses.append(response)

aggregated_response = "\n".join(responses)

print("Aggregated Response:")
print(aggregated_response)
