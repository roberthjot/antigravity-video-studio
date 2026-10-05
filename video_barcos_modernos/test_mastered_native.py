import asyncio
import os
import subprocess
import edge_tts

VOICES_TO_TEST = [
    {
        "id": "nativo_01_alvaro_espana_estudio",
        "voice": "es-ES-AlvaroNeural",
        "rate": "+0%",
        "pitch": "-2Hz",
        "description": "Alvaro (Espana) - Masterizado estilo Documental Discovery"
    },
    {
        "id": "nativo_02_jorge_mexico_estudio",
        "voice": "es-MX-JorgeNeural",
        "rate": "+2%",
        "pitch": "-1Hz",
        "description": "Jorge (Mexico) - Masterizado estilo Narrador Latino Potente"
    },
    {
        "id": "nativo_03_elvira_espana_cine",
        "voice": "es-ES-ElviraNeural",
        "rate": "-2%",
        "pitch": "+0Hz",
        "description": "Elvira (Espana) - Masterizada estilo Documental Historico / BBC"
    },
    {
        "id": "nativo_04_dalia_mexico_shorts",
        "voice": "es-MX-DaliaNeural",
        "rate": "+12%",
        "pitch": "+0Hz",
        "description": "Dalia (Mexico) - Masterizada Dinamica para Shorts / Reels"
    },
    {
        "id": "nativo_05_gonzalo_colombia_estudio",
        "voice": "es-CO-GonzaloNeural",
        "rate": "+0%",
        "pitch": "-3Hz",
        "description": "Gonzalo (Colombia) - Masterizado Calido y Cercano"
    }
]

TEXTO_PRUEBA = (
    "En las profundidades del oceano Atlantico, la ingenieria naval moderna enfrenta su mayor desafio. "
    "Gigantes de acero capaces de resistir olas de mas de treinta metros, navegando hacia lo desconocido. "
    "Hoy descubriremos como estas colosales estructuras logran desafiar a la naturaleza."
)

OUTPUT_DIR = r"c:\Users\Owner\Documents\antigravity\beautiful-hertz\video_barcos_modernos\muestras_voces"

async def generate_and_master():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Cadena de masterizacion de audio para FFmpeg (Broadcast Vocal Chain):
    # 1. highpass=f=75: quita ruidos de fondo y graves sucios digitales
    # 2. equalizer 180Hz +3dB: anade cuerpo y presencia de pecho (calidez de locutor)
    # 3. equalizer 3200Hz +2.5dB: anade claridad, brillo y comprension a las consonantes
    # 4. acompressor: comprime la dinamica para que suene con volumen uniforme y potente de radio
    # 5. alimiter: evita cualquier saturacion digital
    audio_filter = (
        "highpass=f=75,"
        "equalizer=f=180:t=q:w=1.2:g=3.2,"
        "equalizer=f=3200:t=q:w=1.0:g=2.2,"
        "acompressor=threshold=-16dB:ratio=3.5:attack=15:release=200:makeup=2.5dB,"
        "alimiter=limit=-1dB"
    )

    for item in VOICES_TO_TEST:
        raw_mp3 = os.path.join(OUTPUT_DIR, f"temp_{item['id']}_raw.mp3")
        final_mp3 = os.path.join(OUTPUT_DIR, f"{item['id']}.mp3")
        
        print(f"Generando TTS para: {item['description']}...")
        communicate = edge_tts.Communicate(
            TEXTO_PRUEBA,
            voice=item["voice"],
            rate=item["rate"],
            pitch=item["pitch"]
        )
        await communicate.save(raw_mp3)
        
        print(f"Masterizando audio profesional con FFmpeg...")
        cmd = [
            "ffmpeg", "-y",
            "-i", raw_mp3,
            "-af", audio_filter,
            "-b:a", "192k",
            final_mp3
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode == 0:
            print(f" OK: Guardado en muestras_voces/{item['id']}.mp3")
        else:
            print(f" Error en FFmpeg para {item['id']}: {res.stderr.decode('utf-8', errors='ignore')}")
            
        if os.path.exists(raw_mp3):
            os.remove(raw_mp3)

if __name__ == "__main__":
    asyncio.run(generate_and_master())
