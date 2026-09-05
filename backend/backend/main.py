import os
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from gtts import gTTS

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static/audio", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

class ScriptData(BaseModel):
    text: str
    lang: str = "hi"

@app.post("/api/speak")
def generate_voice(data: ScriptData):
    if not data.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    filename = f"voice_{int(time.time())}.mp3"
    filepath = os.path.join("static/audio", filename)

    tts = gTTS(text=data.text, lang=data.lang, slow=False)
    tts.save(filepath)

    words = data.text.split()
    cues = []
    current_time = 0.0
    for _ in words:
        cues.append({"time": round(current_time, 2), "mouth": "O"})
        cues.append({"time": round(current_time + 0.15, 2), "mouth": "A"})
        cues.append({"time": round(current_time + 0.3, 2), "mouth": "closed"})
        current_time += 0.45

    return {
        "audio_url": f"/static/audio/{filename}",
        "duration": round(current_time, 2),
        "visemes": cues
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
