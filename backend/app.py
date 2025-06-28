import os
from fastapi import FastAPI, UploadFile, Form, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai

import joblib
import pandas as pd
import re
import json

app = FastAPI()

# CORS (React frontend allowed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("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")

# Load components
@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    audio_bytes = await file.read()

    # Call OpenAI Whisper API
    response = openai.Audio.transcribe(
        model="whisper-1",
        file=audio_bytes,
        file_type=file.content_type  # e.g. "audio/mpeg" or "audio/wav"
    )

    transcription_text = response["text"]
    return {"transcription": transcription_text}

bias_model = joblib.load("models/bias_pipeline.pkl")
lawyers = pd.read_csv("data/lawyers.csv")
ngos = pd.read_csv("data/ngos.csv")

openai.api_key = "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"

# Helper
def classify_case(text):
    prompt = f"""
You are an AI trained in Indian legal categories.

Classify into JSON:
1. legal_issue
2. bias
3. urgency

User input:
"{text}"
"""
    resp = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    raw = resp.choices[0].message["content"]
    cleaned = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    return json.loads(cleaned)

def generate_advice(text, legal_issue, bias, urgency):
    prompt = f"""
Same language response. 
📝 {text}
⚖️ {legal_issue}
🚩 {bias}
⏱️ {urgency}
Explain rights, IPC, punishment, action, motivate.
"""
    resp = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6
    )
    return resp.choices[0].message["content"]

@app.post("/analyze/")
async def analyze(text: str = Form(...)):
    cls = classify_case(text)
    advice = generate_advice(text, cls["legal_issue"], cls["bias"], cls["urgency"])
    
    # Recommend
    law = lawyers[lawyers["legal_issues"].str.contains(cls["legal_issue"], case=False, na=False)].head(3).to_dict(orient="records")
    ngo = ngos[ngos["legal_issues"].str.contains(cls["legal_issue"], case=False, na=False)].head(3).to_dict(orient="records")
    
    return {
        "classification": cls,
        "advice": advice,
        "lawyers": law,
        "ngos": ngo
    }

@app.post("/transcribe/")
async def transcribe(file: UploadFile):
    audio = await file.read()
    with open("temp_audio.mp3", "wb") as f:
        f.write(audio)
    result = app.post.transcribe("temp_audio.mp3", language="hi")
    return {"text": result["text"]}
