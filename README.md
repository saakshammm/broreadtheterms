# broreadtheterms

**Terms & Conditions for actual humans. Because nobody reads that shit.**

Paste any legal garbage — privacy policies, terms of service, subscription traps — and our AI will translate it into brutally honest Gen‑Z language, expose all the red flags, and give you a **Cooked Score** so you know exactly how screwed you are.

![demo](static/logo.svg)

---

## Why this exists

Companies hide the sketchiest stuff behind walls of legalese. You're supposed to just click "I agree" and forget about it. This tool fights back by ripping apart the fine print and telling you what it **actually** means — in the funniest, most savage way possible.

---

## Features

- **Instant roast** — paste text or drop a `.txt`, `.pdf`, or `.docx` file and get results in seconds.
- **Cooked Score** — 0‑100 rating of how evil the document is (spoiler: it's usually > 80).
- **Red flag detection** — catches data selling, forced arbitration, auto‑renew traps, liability waivers, and more.
- **Honest translation** — the whole policy rewritten in brutally honest English.
- **What they really mean** — picks actual phrases from the text and translates them one‑by‑one.
- **Privacy risk + subscription trap meter** — clear labels like `HIGH`, `GOVERNMENT EXPERIMENT`, and `DARK SOULS LEVEL`.
- **Validation layer** — refuses to analyse non‑legal texts (no, your WhatsApp chat won't work).
- **Score animation** — counts up from 0 to your actual Cooked Score for dramatic effect.
- **Zero‑cost AI** — uses the free tier of Nvidia NIM (Llama 3.1 8B), no credit card required.

---

## Tech stack

- **Frontend** — vanilla HTML/CSS/JavaScript, Space Grotesk font, hand‑crafted responsive design
- **Backend** — Python FastAPI
- **AI** — Nvidia NIM API (meta/llama-3.1-8b-instruct)
- **Document parsing** — PyPDF2, python‑docx
- **Deployment** — Docker image, runs on Hugging Face Spaces

---

## Run locally

### 1. Clone the repo
```bash
git clone https://github.com/your-username/broreadtheterms.git
cd broreadtheterms
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Get your Nvidia NIM API key
- Go to [build.nvidia.com](https://build.nvidia.com/explore/discover) and sign in.
- Create an API key for `meta/llama-3.1-8b-instruct` (free tier).
- Create a `.env` file in the project root:
```env
NVIDIA_NIM_API_KEY=your-key-here
```

### 4. Start the server
```bash
uvicorn main:app --reload
```
Open `http://127.0.0.1:8000` and start roasting policies.


---

## License

MIT — use it, roast corporations, share the fear.

---

*built to expose corporate manipulation. ▮*
