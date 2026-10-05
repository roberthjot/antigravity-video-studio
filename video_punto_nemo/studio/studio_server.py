import os
import sys
import json
import asyncio
import threading
import urllib.request
import urllib.parse
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import edge_tts
import imageio_ffmpeg
import subprocess

STUDIO_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(STUDIO_DIR, ".."))
OPTIMIZED_DIR = os.path.join(PROJECT_DIR, "optimized_1080p")
MEDIA_DIR = os.path.join(PROJECT_DIR, "media")
OVERLAYS_DIR = os.path.join(PROJECT_DIR, "overlays")
SFX_DIR = os.path.join(PROJECT_DIR, "sfx")
TEMP_V2_DIR = os.path.join(PROJECT_DIR, "temp_clips_v2")
SRC_TEMP_DIR = os.path.join(PROJECT_DIR, "temp_clips")
PROJECT_STATE_FILE = os.path.join(STUDIO_DIR, "project_state.json")

sys.path.append(PROJECT_DIR)

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

# Cadena de masterización vocal de estudio
VOCAL_FILTER = (
    "highpass=f=75,"
    "equalizer=f=180:t=q:w=1.5:g=3.5,"
    "equalizer=f=3200:t=q:w=1.2:g=2.2,"
    "acompressor=threshold=-18dB:ratio=3.5:attack=15:release=140:makeup=2.5,"
    "alimiter=limit=-1dB"
)

AVAILABLE_VOICES = [
    {"id": "es-MX-JorgeNeural", "name": "Jorge (México) · Documental Profundo / Natural", "gender": "male", "lang": "es-MX"},
    {"id": "es-ES-AlvaroNeural", "name": "Álvaro (España) · Narrador Formal y Serio", "gender": "male", "lang": "es-ES"},
    {"id": "es-CO-GonzaloNeural", "name": "Gonzalo (Colombia) · Tono Neutro y Cálido", "gender": "male", "lang": "es-CO"},
    {"id": "es-MX-DaliaNeural", "name": "Dalia (México) · Voz Femenina Documental", "gender": "female", "lang": "es-MX"},
    {"id": "es-ES-ElviraNeural", "name": "Elvira (España) · Femenina Suspenso / Misterio", "gender": "female", "lang": "es-ES"},
    {"id": "es-AR-TomasNeural", "name": "Tomás (Argentina) · Narrativo Dinámico", "gender": "male", "lang": "es-AR"}
]

app = FastAPI(title="Antigravity Video Studio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(OPTIMIZED_DIR, exist_ok=True)
os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(SFX_DIR, exist_ok=True)
os.makedirs(OVERLAYS_DIR, exist_ok=True)
os.makedirs(SRC_TEMP_DIR, exist_ok=True)

app.mount("/media/optimized", StaticFiles(directory=OPTIMIZED_DIR), name="optimized")
app.mount("/media/video", StaticFiles(directory=MEDIA_DIR), name="video")
app.mount("/media/audio", StaticFiles(directory=SRC_TEMP_DIR), name="audio")
app.mount("/media/sfx", StaticFiles(directory=SFX_DIR), name="sfx")
app.mount("/media/overlays", StaticFiles(directory=OVERLAYS_DIR), name="overlays")

RENDER_STATUS = {
    "running": False,
    "progress": 0,
    "current_scene": 0,
    "total_scenes": 32,
    "message": "Listo para renderizar",
    "done": False,
    "error": None,
    "output_file": None
}

VOICE_REGEN_STATUS = {
    "running": False,
    "progress": 0,
    "message": ""
}

@app.get("/", response_class=HTMLResponse)
async def get_index():
    template_path = os.path.join(STUDIO_DIR, "templates", "index.html")
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content=content, headers={
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    })

@app.get("/media/final/{filename}")
async def get_final_media(filename: str):
    file_path = os.path.join(PROJECT_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/media/music/{filename}")
async def get_music_media(filename: str):
    file_path = os.path.join(PROJECT_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

def get_available_music():
    tracks = []
    for f in os.listdir(PROJECT_DIR):
        if f.lower().endswith((".mp3", ".oga", ".ogg", ".wav", ".m4a")):
            title = f.replace("_", " ").replace(".mp3", "").replace(".oga", "").replace(".ogg", "").title()
            tracks.append({"file": f, "title": title})
    return tracks

@app.get("/api/project")
async def get_project():
    if not os.path.exists(PROJECT_STATE_FILE):
        raise HTTPException(status_code=404, detail="Project state not found")
    with open(PROJECT_STATE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["music_options"] = get_available_music()
    data["available_voices"] = AVAILABLE_VOICES
    return data

@app.post("/api/project/save")
async def save_project(payload: dict):
    with open(PROJECT_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return {"status": "ok", "message": "Proyecto guardado con éxito"}

@app.post("/api/music/upload")
async def upload_music(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".mp3", ".wav", ".ogg", ".oga", ".m4a"]:
        raise HTTPException(status_code=400, detail="Formato no admitido. Usa MP3, WAV, OGG o M4A.")
    
    clean_name = f"music_{file.filename.replace(' ', '_')}"
    save_path = os.path.join(PROJECT_DIR, clean_name)
    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    # Actualizar en project_state
    with open(PROJECT_STATE_FILE, "r", encoding="utf-8") as f:
        pstate = json.load(f)
    pstate["soundtrack"] = clean_name
    with open(PROJECT_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(pstate, f, indent=2, ensure_ascii=False)

    return {"status": "ok", "file": clean_name, "title": file.filename}

@app.get("/api/voice/sample")
async def voice_sample(voice_id: str = Query(...)):
    sample_file = os.path.join(SRC_TEMP_DIR, f"sample_{voice_id}.mp3")
    sample_text = "Hola, esta es una prueba de voz para la narración documental del Punto Nemo."
    comm = edge_tts.Communicate(sample_text, voice_id)
    await comm.save(sample_file)
    return {"status": "ok", "url": f"/media/audio/sample_{voice_id}.mp3"}

def run_voice_regeneration(voice_id: str, scene_id: Optional[int] = None):
    global VOICE_REGEN_STATUS
    VOICE_REGEN_STATUS["running"] = True
    VOICE_REGEN_STATUS["progress"] = 0
    VOICE_REGEN_STATUS["message"] = f"Generando locuciones con {voice_id}..."

    try:
        with open(PROJECT_STATE_FILE, "r", encoding="utf-8") as f:
            pstate = json.load(f)

        scenes = pstate["scenes"]
        target_scenes = [sc for sc in scenes if sc["id"] == scene_id] if scene_id else scenes
        total = len(target_scenes)

        async def generate_batch():
            for idx, sc in enumerate(target_scenes, 1):
                sid = sc["id"]
                raw_file = os.path.join(SRC_TEMP_DIR, f"raw_audio_{sid:02d}.mp3")
                master_file = os.path.join(SRC_TEMP_DIR, f"master_audio_{sid:02d}.mp3")
                
                VOICE_REGEN_STATUS["message"] = f"Locución {idx}/{total} (Escena {sid})..."
                VOICE_REGEN_STATUS["progress"] = int((idx / total) * 90)

                comm = edge_tts.Communicate(sc["text"], voice_id)
                await comm.save(raw_file)

                # Aplicar filtro vocal de estudio con FFmpeg
                cmd = [FFMPEG, "-y", "-i", raw_file, "-af", VOCAL_FILTER, "-b:a", "192k", master_file]
                subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                if os.path.exists(raw_file): os.remove(raw_file)

        asyncio.run(generate_batch())

        pstate["voice"] = voice_id
        with open(PROJECT_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(pstate, f, indent=2, ensure_ascii=False)

        VOICE_REGEN_STATUS["progress"] = 100
        VOICE_REGEN_STATUS["message"] = "¡Todas las locuciones actualizadas con éxito!"
    except Exception as e:
        VOICE_REGEN_STATUS["message"] = f"Error: {str(e)}"
    finally:
        VOICE_REGEN_STATUS["running"] = False

@app.post("/api/voice/regenerate")
async def regenerate_voices(payload: dict):
    global VOICE_REGEN_STATUS
    if VOICE_REGEN_STATUS["running"]:
        return {"status": "error", "message": "Ya se están regenerando las voces"}
    
    voice_id = payload.get("voice_id", "es-MX-JorgeNeural")
    scene_id = payload.get("scene_id", None)
    
    thread = threading.Thread(target=run_voice_regeneration, args=(voice_id, scene_id), daemon=True)
    thread.start()
    return {"status": "ok", "message": "Regeneración de voz iniciada"}

@app.get("/api/voice/status")
async def get_voice_status():
    return VOICE_REGEN_STATUS

@app.post("/api/scene/delete-candidate")
async def delete_candidate(payload: dict):
    scene_id = payload.get("scene_id")
    media_name = payload.get("media_name")
    
    with open(PROJECT_STATE_FILE, "r", encoding="utf-8") as f:
        pstate = json.load(f)

    for sc in pstate["scenes"]:
        if sc["id"] == scene_id:
            sc["candidates"] = [c for c in sc["candidates"] if c["name"] != media_name]
            # Si era la activa, cambiar a la primera disponible
            if sc["media"] == media_name:
                if sc["candidates"]:
                    sc["media"] = sc["candidates"][0]["name"]
                    sc["is_video"] = (sc["candidates"][0]["type"] == "video")
                else:
                    sc["media"] = "00_intro_video_olas.webm"
                    sc["is_video"] = True
            break

    with open(PROJECT_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(pstate, f, indent=2, ensure_ascii=False)

    return {"status": "ok", "message": f"Candidato {media_name} eliminado de escena {scene_id}"}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), scene_id: Optional[int] = Form(None)):
    ext = os.path.splitext(file.filename)[1].lower()
    clean_name = f"upload_{os.path.splitext(file.filename)[0].replace(' ', '_')}{ext}"
    
    if ext in [".jpg", ".jpeg", ".png", ".webp"]:
        save_path = os.path.join(OPTIMIZED_DIR, clean_name)
        content = await file.read()
        with open(save_path, "wb") as f:
            f.write(content)
            
        try:
            with Image.open(save_path) as img:
                img = img.convert("RGB")
                target_w, target_h = 2048, 1152
                target_aspect = target_w / target_h
                w, h = img.size
                current_aspect = w / h

                if current_aspect > target_aspect:
                    new_w = int(h * target_aspect)
                    left = (w - new_w) // 2
                    img = img.crop((left, 0, left + new_w, h))
                else:
                    new_h = int(w / target_aspect)
                    top = (h - new_h) // 2
                    img = img.crop((0, top, w, top + new_h))

                img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
                img.save(save_path, "JPEG", quality=95)
        except Exception as e:
            print(f"Error optimizando imagen: {e}")

        media_type = "image"
        
    elif ext in [".webm", ".mp4", ".mov"]:
        save_path = os.path.join(MEDIA_DIR, clean_name)
        content = await file.read()
        with open(save_path, "wb") as f:
            f.write(content)
        media_type = "video"
    else:
        raise HTTPException(status_code=400, detail="Formato no soportado (usa JPG, PNG, WEBP, MP4 o WEBM)")

    with open(PROJECT_STATE_FILE, "r", encoding="utf-8") as f:
        pstate = json.load(f)

    new_media_item = {
        "name": clean_name,
        "type": media_type,
        "title": f"Subido: {file.filename}"
    }

    if not any(m["name"] == clean_name for m in pstate["library"]):
        pstate["library"].append(new_media_item)

    if scene_id is not None:
        for sc in pstate["scenes"]:
            if sc["id"] == scene_id:
                sc["media"] = clean_name
                sc["is_video"] = (media_type == "video")
                if not any(c["name"] == clean_name for c in sc["candidates"]):
                    sc["candidates"].insert(0, new_media_item)
                break

    with open(PROJECT_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(pstate, f, indent=2, ensure_ascii=False)

    return {
        "status": "ok",
        "file": clean_name,
        "type": media_type,
        "item": new_media_item
    }

@app.get("/api/search-wikimedia")
async def search_wikimedia(q: str = Query(..., min_length=2)):
    try:
        url = (
            "https://commons.wikimedia.org/w/api.php?"
            "action=query&generator=search&gsrsearch=" + urllib.parse.quote(q) +
            "&gsrnamespace=6&gsrlimit=12&prop=imageinfo&iiprop=url|mime|size&format=json"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "AntigravityStudioBot/1.0 (contact@example.com)"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        results = []
        if "query" in data and "pages" in data["query"]:
            for pid, pdata in data["query"]["pages"].items():
                title = pdata.get("title", "").replace("File:", "")
                if not any(title.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png"]):
                    continue
                imageinfo = pdata.get("imageinfo", [{}])[0]
                img_url = imageinfo.get("url", "")
                thumb_url = imageinfo.get("thumburl", img_url)
                if img_url:
                    results.append({
                        "title": title,
                        "url": img_url,
                        "thumb": thumb_url
                    })
        return {"results": results[:8]}
    except Exception as e:
        return {"results": [], "error": str(e)}

@app.post("/api/import-wikimedia")
async def import_wikimedia(payload: dict):
    img_url = payload.get("url")
    scene_id = payload.get("scene_id")
    if not img_url:
        raise HTTPException(status_code=400, detail="Falta URL de imagen")

    raw_filename = os.path.basename(urllib.parse.urlparse(img_url).path)
    clean_name = f"wiki_{raw_filename.replace('%20', '_')}"
    if not clean_name.lower().endswith((".jpg", ".jpeg", ".png")):
        clean_name += ".jpg"

    save_path = os.path.join(OPTIMIZED_DIR, clean_name)
    try:
        req = urllib.request.Request(img_url, headers={"User-Agent": "AntigravityStudioBot/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw_data = resp.read()
        with open(save_path, "wb") as f:
            f.write(raw_data)

        with Image.open(save_path) as img:
            img = img.convert("RGB")
            target_w, target_h = 2048, 1152
            target_aspect = target_w / target_h
            w, h = img.size
            current_aspect = w / h

            if current_aspect > target_aspect:
                new_w = int(h * target_aspect)
                left = (w - new_w) // 2
                img = img.crop((left, 0, left + new_w, h))
            else:
                new_h = int(w / target_aspect)
                top = (h - new_h) // 2
                img = img.crop((0, top, w, top + new_h))

            img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
            img.save(save_path, "JPEG", quality=95)

        new_item = {"name": clean_name, "type": "image", "title": f"Wikimedia: {raw_filename[:25]}"}

        with open(PROJECT_STATE_FILE, "r", encoding="utf-8") as f:
            pstate = json.load(f)

        if not any(m["name"] == clean_name for m in pstate["library"]):
            pstate["library"].append(new_item)

        if scene_id is not None:
            for sc in pstate["scenes"]:
                if sc["id"] == scene_id:
                    sc["media"] = clean_name
                    sc["is_video"] = False
                    if not any(c["name"] == clean_name for c in sc["candidates"]):
                        sc["candidates"].insert(0, new_item)
                    break

        with open(PROJECT_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(pstate, f, indent=2, ensure_ascii=False)

        return {"status": "ok", "item": new_item}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error descargando imagen: {str(e)}")

def run_render_process():
    global RENDER_STATUS
    try:
        RENDER_STATUS["running"] = True
        RENDER_STATUS["progress"] = 2
        RENDER_STATUS["message"] = "Iniciando renderizador con configuración del estudio..."
        RENDER_STATUS["error"] = None
        RENDER_STATUS["done"] = False

        from render_monetizable_8min import render_scene, get_duration, FINAL_OUTPUT
        
        with open(PROJECT_STATE_FILE, "r", encoding="utf-8") as f:
            pstate = json.load(f)

        scenes = pstate["scenes"]
        total = len(scenes)
        RENDER_STATUS["total_scenes"] = total
        rendered_clips = []
        concat_list = os.path.join(TEMP_V2_DIR, "concat_studio_list.txt")

        # Usar soundtrack seleccionado por el usuario
        active_soundtrack_name = pstate.get("soundtrack", "soundtrack_dinamico_8min.mp3")
        active_soundtrack_path = os.path.join(PROJECT_DIR, active_soundtrack_name)

        for idx, sc in enumerate(scenes, 1):
            RENDER_STATUS["current_scene"] = idx
            RENDER_STATUS["message"] = f"Renderizando Escena {idx:02d}/{total:02d} ({sc['media']})..."
            RENDER_STATUS["progress"] = int(5 + (idx / total) * 85)
            
            sc_dict = {
                "id": sc["id"],
                "media": sc["media"],
                "is_video": sc["is_video"],
                "seek": sc.get("seek", 0),
                "motion": sc.get("motion", "zoom_in"),
                "overlay": sc.get("overlay", None),
                "sfx": {"file": sc["sfx"], "delay": 1200, "vol": 0.38} if sc.get("sfx") else None
            }
            
            clip_path, dur = render_scene(sc_dict)
            rendered_clips.append(clip_path)

        RENDER_STATUS["message"] = "Concatenando escenas en pista única..."
        RENDER_STATUS["progress"] = 92
        with open(concat_list, "w", encoding="utf-8") as f:
            for c in rendered_clips:
                clean_c = c.replace("\\", "/")
                f.write(f"file '{clean_c}'\n")

        video_no_soundtrack = os.path.join(TEMP_V2_DIR, "studio_no_soundtrack.mp4")
        cmd_concat = [
            FFMPEG, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_list,
            "-c", "copy",
            video_no_soundtrack
        ]
        subprocess.run(cmd_concat, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        RENDER_STATUS["message"] = f"Mezclando música '{active_soundtrack_name}' con auto-ducking..."
        RENDER_STATUS["progress"] = 96
        
        cmd_final = [
            FFMPEG, "-y",
            "-i", video_no_soundtrack,
            "-i", active_soundtrack_path,
            "-filter_complex",
            "[1:a]volume=0.13[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
            "-shortest",
            FINAL_OUTPUT
        ]
        subprocess.run(cmd_final, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        final_dur = get_duration(FINAL_OUTPUT)
        RENDER_STATUS["progress"] = 100
        RENDER_STATUS["message"] = f"¡Video completado exitosamente! ({final_dur:.1f} segundos)"
        RENDER_STATUS["done"] = True
        RENDER_STATUS["output_file"] = "documental_punto_nemo_8MIN_MONETIZABLE.mp4"
    except Exception as e:
        RENDER_STATUS["error"] = str(e)
        RENDER_STATUS["message"] = f"Error en render: {str(e)}"
    finally:
        RENDER_STATUS["running"] = False

@app.post("/api/render")
async def trigger_render(background_tasks: BackgroundTasks):
    global RENDER_STATUS
    if RENDER_STATUS["running"]:
        return {"status": "error", "message": "Ya hay un renderizado en curso"}
    
    thread = threading.Thread(target=run_render_process, daemon=True)
    thread.start()
    return {"status": "ok", "message": "Renderizado iniciado en segundo plano"}

@app.get("/api/render/status")
async def get_render_status():
    return RENDER_STATUS

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("studio_server:app", host="127.0.0.1", port=8080, reload=False)
