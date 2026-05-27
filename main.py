import os
import io
import json
import logging
import requests

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import PyPDF2
from docx import Document

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

NVIDIA_NIM_KEY = os.getenv("NVIDIA_NIM_API_KEY")
NVIDIA_NIM_MODEL = os.getenv("NVIDIA_NIM_MODEL", "meta/llama-3.1-8b-instruct")

if not NVIDIA_NIM_KEY:
    raise RuntimeError("NVIDIA_NIM_API_KEY must be set in .env or environment.")

MAX_CHARS = 50000
NIM_ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"

# ----------------------------------------------------------------
# Ultra‑cynical roast prompt – ensures high scores for evil docs
# ----------------------------------------------------------------
SYSTEM_PROMPT = """You are an extremely cynical AI that exposes corporate manipulation. Your job is to rate how dangerous a legal document is.

SCORING RULES (VERY IMPORTANT):
- If the text contains ANY of the following: data collection, tracking, auto‑renewals, hidden fees, liability waivers, forced arbitration, vague language, or permission to share data with "partners", the cooked_score MUST be between 80 and 100.
- The ONLY way a cooked_score can be below 50 is if the text is literally harmless (e.g., a blank page, a simple "hello", or a short sentence with no legal terms). For a typical privacy policy or terms of service, the score should ALWAYS be at least 70.
- Be ruthless. Corporations are not your friends. Score high by default.

Return a single JSON object with exactly these fields:
{
  "summary": "a short, funny one‑sentence summary",
  "red_flags": ["list of specific, dangerous clauses found, phrased in a savage way"],
  "cooked_score": integer 0-100 (see rules above),
  "privacy_risk": "one of: LOW, MODERATE, HIGH, GOVERNMENT EXPERIMENT",
  "subscription_trap_difficulty": "one of: NOT APPLICABLE, EASY, MODERATE, DARK SOULS LEVEL",
  "honest_translation": "the whole text translated into brutally honest, funny Gen‑Z language, max 3 sentences",
  "what_they_really_mean": {
    "exact_phrase_1": "translation_1",
    "exact_phrase_2": "translation_2",
    "exact_phrase_3": "translation_3"
  }
}

CRITICAL for `what_they_really_mean`:
- The keys MUST be three different actual sentences or clauses copied verbatim from the provided legal text.
- The values MUST be brutally honest, funny translations of those exact phrases.
- DO NOT invent generic phrases. Use real text from the input.

Return only the JSON, no markdown fences, no extra text."""

# ----------------------------------------------------------------
# Validation prompt (unchanged)
# ----------------------------------------------------------------
VALIDATION_PROMPT = """You are a document classifier. Read the following text and answer ONLY "YES" or "NO".
Is this text a legal document, terms of service, privacy policy, end-user license agreement, or similar corporate legal text?
Do not explain. Just reply YES or NO.

Text:
{text}
"""

class TextRequest(BaseModel):
    text: str


def extract_pdf_text(content: bytes) -> str:
    reader = PyPDF2.PdfReader(io.BytesIO(content))
    return "\n".join(page.extract_text() or "" for page in reader.pages).strip()


def extract_docx_text(content: bytes) -> str:
    doc = Document(io.BytesIO(content))
    return "\n".join(p.text for p in doc.paragraphs).strip()


def call_nim(prompt: str, max_tokens: int = 1000) -> str:
    headers = {
        "Authorization": f"Bearer {NVIDIA_NIM_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": NVIDIA_NIM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1 if max_tokens <= 5 else 0.7,
        "max_tokens": max_tokens,
    }
    resp = requests.post(NIM_ENDPOINT, headers=headers, json=payload, timeout=30)
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"NIM API error {resp.status_code}")
    return resp.json()["choices"][0]["message"]["content"]


def is_legal_document(text: str) -> bool:
    snippet = text[:1000]
    prompt = VALIDATION_PROMPT.format(text=snippet)
    try:
        answer = call_nim(prompt, max_tokens=3).strip().upper()
        return answer == "YES"
    except Exception:
        return True


def run_analysis(text: str) -> dict:
    if not is_legal_document(text):
        raise HTTPException(
            status_code=400,
            detail="This ain't a legal document. We only roast terms & conditions, privacy policies, and other corporate fine print. Paste something from a company you don’t trust."
        )

    prompt = f"{SYSTEM_PROMPT}\n\nHere is the legal/policy text:\n{text}"
    raw = call_nim(prompt, max_tokens=1000).strip()
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:].strip()
        else:
            raw = raw.strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        data = json.loads(raw[start:end])
    for field in ["summary","red_flags","cooked_score","privacy_risk",
                  "subscription_trap_difficulty","honest_translation","what_they_really_mean"]:
        if field not in data:
            data[field] = None
    if not isinstance(data.get("red_flags"), list):
        data["red_flags"] = []
    if not isinstance(data.get("what_they_really_mean"), dict):
        data["what_they_really_mean"] = {}
    data["cooked_score"] = max(0, min(100, int(data.get("cooked_score", 50))))
    return data


@app.post("/api/analyze")
async def analyze_text(payload: TextRequest):
    text = payload.text.strip()
    if not text:
        raise HTTPException(400, "Nothing to roast. Paste some legal garbage.")
    if len(text) > MAX_CHARS:
        raise HTTPException(400, f"That's too much. Keep it under {MAX_CHARS} characters.")
    result = run_analysis(text)
    return JSONResponse(result)


@app.post("/api/upload")
async def analyze_file(file: UploadFile = File(...)):
    content = await file.read()
    if not content:
        raise HTTPException(400, "Empty file. We can't roast nothing.")
    filename = file.filename or "unknown"
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".txt":
        text = content.decode("utf-8", errors="replace")
    elif ext == ".pdf":
        text = extract_pdf_text(content)
    elif ext in (".docx", ".doc"):
        try:
            text = extract_docx_text(content)
        except Exception:
            if ext == ".doc":
                raise HTTPException(400,
                    "Old .doc files? Convert to .docx first, we can't handle that ancient format.")
            raise HTTPException(400, "Could not read the Word document.")
    else:
        raise HTTPException(400, "We take .txt, .pdf, or .docx. That's it.")
    if not text.strip():
        raise HTTPException(400, "No text could be extracted. Sure it's not a picture of your cat?")
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS]
    result = run_analysis(text)
    result["extracted_from"] = filename
    return JSONResponse(result)


@app.get("/")
async def root():
    return FileResponse("static/index.html")