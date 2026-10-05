import os
import sys
import asyncio
import subprocess
import imageio_ffmpeg
import edge_tts

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_DIR = r"c:\Users\Owner\Documents\antigravity\beautiful-hertz\video_punto_nemo"
MEDIA_DIR = os.path.join(PROJECT_DIR, "media")
OPTIMIZED_DIR = os.path.join(PROJECT_DIR, "optimized_1080p")
TEMP_DIR = os.path.join(PROJECT_DIR, "temp_clips")
os.makedirs(TEMP_DIR, exist_ok=True)

FINAL_OUTPUT = os.path.join(PROJECT_DIR, "documental_punto_nemo_MASTER.mp4")
MUSIC_FILE = os.path.join(PROJECT_DIR, "musica_deep.oga")

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

# Cadena de Masterización de Estudio de Grabación (Vocal Broadcast Chain)
vocal_filter = (
    "highpass=f=75,"
    "equalizer=f=180:t=q:w=1.5:g=3.5,"
    "equalizer=f=3200:t=q:w=1.2:g=2.2,"
    "acompressor=threshold=-18dB:ratio=3.5:attack=15:release=140:makeup=2.5,"
    "alimiter=limit=-1dB"
)

# 20 Escenas que componen la narrativa completa de Punto Nemo
SCENES = [
    # --- ACTO 1: LAS COORDENADAS DEL AISLAMIENTO ABSOLUTO ---
    {
        "id": 1,
        "text": "En medio de la inmensidad del océano Pacífico... existe un punto donde la soledad alcanza su expresión más aterradora. Las coordenadas: cuarenta y ocho grados cincuenta y dos minutos sur... ciento veintitrés grados veintitrés minutos oeste. Bienvenido al Punto Nemo.",
        "media": "00_intro_video_olas.webm",
        "is_video": True,
        "seek": 0,
        "pitch": "+1Hz",
        "rate": "+2%"
    },
    {
        "id": 2,
        "text": "Conocido oficialmente como el Polo Oceánico de Inaccesibilidad, es el lugar de la superficie terrestre más alejado de cualquier masa continental o pedazo de tierra firme en todo el planeta.",
        "media": "01_mapa_punto_nemo.jpg",
        "is_video": False,
        "pitch": "+0Hz",
        "rate": "+0%"
    },
    {
        "id": 3,
        "text": "La costa más cercana, un diminuto islote desierto en la Polinesia llamado Ducie, se encuentra a más de dos mil seiscientos ochenta y ocho kilómetros de distancia. Si naufragaras aquí... los seres humanos más cercanos a ti no estarían en barcos ni en islas.",
        "media": "02_mapa_polo_inaccesibilidad.jpg",
        "is_video": False,
        "pitch": "-3Hz",
        "rate": "-4%"
    },
    {
        "id": 4,
        "text": "Estarían a cuatrocientos kilómetros sobre tu cabeza... flotando en la oscuridad del espacio a bordo de la Estación Espacial Internacional cada vez que su órbita pasa justo por encima de este abismo.",
        "media": "04_astronauta_cupola.jpg",
        "is_video": False,
        "pitch": "-2Hz",
        "rate": "-2%"
    },

    # --- ACTO 2: EL CEMENTERIO DE NAVES ESPACIALES ---
    {
        "id": 5,
        "text": "Pero su aislamiento extremo no es solo una curiosidad geográfica. Durante décadas, las agencias espaciales más poderosas del planeta han utilizado este punto exacto con un propósito siniestro y fascinante: el cementerio de naves espaciales.",
        "media": "03_tierra_pacifico_desde_iss.jpg",
        "is_video": False,
        "pitch": "-1Hz",
        "rate": "+1%"
    },
    {
        "id": 6,
        "text": "A más de cuatro mil metros de profundidad, descansan los restos de más de doscientas sesenta naves espaciales, satélites espía y colosales cargueros desintegrados por reingreso atmosférico.",
        "media": "06_carguero_progress.jpg",
        "is_video": False,
        "pitch": "-3Hz",
        "rate": "-3%"
    },
    {
        "id": 7,
        "text": "En marzo de dos mil uno, la legendaria estación espacial soviética Mir, con un peso de ciento cuarenta y tres toneladas, fue precipitada deliberadamente hacia la atmósfera, cruzando el cielo como una violenta bola de fuego antes de sepultarse para siempre en estas aguas.",
        "media": "05_estacion_espacial_mir.jpg",
        "is_video": False,
        "pitch": "-1Hz",
        "rate": "+3%"
    },
    {
        "id": 8,
        "text": "Titanio calcinado, aleaciones militares secretas y residuos atómicos yacen en la oscuridad eterna del lecho marino... en una tumba donde ningún ser humano jamás podrá descender a rescatarlos.",
        "media": "07_reingreso_atmosferico_fuego.jpg",
        "is_video": False,
        "pitch": "-5Hz",
        "rate": "-5%"
    },

    # --- ACTO 3: EL SONIDO THE BLOOP Y EL MISTERIO ABISAL ---
    {
        "id": 9,
        "text": "Sin embargo, el misterio más perturbador del Punto Nemo no cayó del cielo... emergió de las profundidades. En el verano de mil novecientos noventa y siete, los micrófonos submarinos de la agencia oceanográfica NOAA registraron una señal estremecedora.",
        "media": "10_hidrofono_submarino.jpg",
        "is_video": False,
        "pitch": "+1Hz",
        "rate": "+1%"
    },
    {
        "id": 10,
        "text": "Bautizado como The Bloop, fue un sonido de ultra baja frecuencia tan descomunalmente potente que fue captado por hidrófonos separados por más de cinco mil kilómetros de distancia a lo largo de todo el océano Pacífico.",
        "media": "09_bloop_espectrograma.jpg",
        "is_video": False,
        "pitch": "-2Hz",
        "rate": "-3%"
    },
    {
        "id": 11,
        "text": "Su firma acústica se asemejaba al patrón de un ser biológico vivo, pero con una potencia varias veces superior al rugido de la ballena azul más gigantesca jamás documentada. Durante años, la sospecha de una criatura abisal desconocida desconcertó a la comunidad científica.",
        "media": "15_submarino_profundidades.jpg",
        "is_video": False,
        "pitch": "-4Hz",
        "rate": "-5%"
    },
    {
        "id": 12,
        "text": "Años más tarde, los científicos determinaron que el sonido probablemente provino de un gigantesco criosismo: la fractura y colapso de una masa masiva de hielo en los confines de la Antártida, resonando a través del abismo oceánico.",
        "media": "12_iceberg_antartida_criosismo.jpg",
        "is_video": False,
        "pitch": "-1Hz",
        "rate": "+1%"
    },

    # --- ACTO 4: EL DESIERTO BIOLÓGICO DEL OCÉANO ---
    {
        "id": 13,
        "text": "Pero incluso sin monstruos marinos, la realidad biológica del Punto Nemo es aún más desoladora. Este sector se sitúa justo en el centro del Giro del Pacífico Sur, una gigantesca corriente oceánica circular que atrapa y aísla sus aguas.",
        "media": "15_submarino_profundidades.jpg",
        "is_video": False,
        "pitch": "+0Hz",
        "rate": "+0%"
    },
    {
        "id": 14,
        "text": "Aquí no llegan corrientes ricas en nutrientes. No existe plancton suficiente, y por lo tanto, no hay cardúmenes de peces, ni tiburones, ni mamíferos marinos. Es el desierto biológico más estéril del planeta Tierra.",
        "media": "03_tierra_pacifico_desde_iss.jpg",
        "is_video": False,
        "pitch": "-3Hz",
        "rate": "-4%"
    },

    # --- ACTO 5: LA COINCIDENCIA DE H.P. LOVECRAFT ---
    {
        "id": 15,
        "text": "Y es aquí donde la ciencia se cruza con una de las coincidencias más inquietantes de la historia. En mil novecientos veintiocho, el legendario maestro del terror H. P. Lovecraft escribió su célebre obra: La Llamada de Cthulhu.",
        "media": "16_cthulhu_monstruo_marino.jpg",
        "is_video": False,
        "pitch": "+1Hz",
        "rate": "+2%"
    },
    {
        "id": 16,
        "text": "En el texto, Lovecraft situó la ancestral ciudad sumergida de R'lyeh... casi exactamente en las mismas coordenadas del Punto Nemo, sesenta y seis años antes de que el ingeniero Hrvoje Lukatela las calculara matemáticamente en mil novecientos noventa y dos.",
        "media": "18_criatura_abisal_mitologia.jpg",
        "is_video": False,
        "pitch": "-3Hz",
        "rate": "-4%"
    },

    # --- ACTO 6: EL DESTINO FINAL EN 2031 Y CIERRE ---
    {
        "id": 17,
        "text": "Hoy, el Punto Nemo se prepara para recibir la tumba más colosal jamás creada por la humanidad. En el año dos mil treinta y uno, la Estación Espacial Internacional llegará oficialmente al final de su vida operativa tras más de treinta años en órbita.",
        "media": "19_estacion_espacial_internacional.jpg",
        "is_video": False,
        "pitch": "+0Hz",
        "rate": "+2%"
    },
    {
        "id": 18,
        "text": "Con un peso descomunal de más de cuatrocientas toneladas métricas, la NASA y sus aliados la guiarán en un descenso final. Sus módulos ardiendo caerán como una tormenta de fuego sobre las frías aguas de este abismo.",
        "media": "07_reingreso_atmosferico_fuego.jpg",
        "is_video": False,
        "pitch": "-2Hz",
        "rate": "+2%"
    },
    {
        "id": 19,
        "text": "El Punto Nemo continuará allí... silencioso e imperturbable, devorando los mayores logros de nuestra civilización bajo kilómetros de agua negra y olvidada.",
        "media": "21_atardecer_dorado_pacifico.jpg",
        "is_video": False,
        "pitch": "-4Hz",
        "rate": "-6%"
    },
    {
        "id": 20,
        "text": "¿Te atreverías a navegar solo por estas coordenadas en una noche de tormenta? Déjanos tu opinión en los comentarios, dale me gusta a este video y suscríbete para explorar más misterios extremos de nuestro planeta. ¡Hasta la próxima travesía!",
        "media": "00_intro_video_olas.webm",
        "is_video": True,
        "seek": 20,
        "pitch": "+1Hz",
        "rate": "+3%"
    }
]

def get_duration(audio_file):
    cmd = [FFMPEG, "-i", audio_file]
    res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, errors="ignore")
    for line in res.stderr.split("\n"):
        if "Duration:" in line:
            part = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = part.split(":")
            return float(h)*3600 + float(m)*60 + float(s)
    return 12.0

async def render_documentary():
    print("============================================================")
    print(f"   PRODUCCIÓN DOCUMENTAL: EL PUNTO NEMO ({len(SCENES)} ESCENAS)")
    print("============================================================\n")
    
    clip_list_file = os.path.join(TEMP_DIR, "concat_list.txt")
    clip_paths = []
    
    VOICE_ACTOR = "es-MX-JorgeNeural"
    
    for sc in SCENES:
        sid = sc["id"]
        raw_audio = os.path.join(TEMP_DIR, f"raw_audio_{sid:02d}.mp3")
        mastered_audio = os.path.join(TEMP_DIR, f"master_audio_{sid:02d}.mp3")
        clip_path = os.path.join(TEMP_DIR, f"clip_{sid:02d}.mp4")
        
        if sc["is_video"]:
            media_path = os.path.join(MEDIA_DIR, sc["media"])
        else:
            base_name = os.path.splitext(sc["media"])[0] + ".jpg"
            media_path = os.path.join(OPTIMIZED_DIR, base_name)
        
        print(f"--- Escena {sid:02d}/{len(SCENES):02d} ---")
        print(f"Recurso: {os.path.basename(media_path)} | Tono: {sc['pitch']} | Vel: {sc['rate']}")
        
        # 1. Generar audio con Edge-TTS para esta frase
        comm = edge_tts.Communicate(sc["text"], VOICE_ACTOR, rate=sc["rate"], pitch=sc["pitch"])
        await comm.save(raw_audio)
        
        # 2. Masterizar audio con cadena de locutor de estudio
        master_cmd = [
            FFMPEG, "-y",
            "-i", raw_audio,
            "-af", vocal_filter,
            "-b:a", "192k",
            mastered_audio
        ]
        subprocess.run(master_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        if os.path.exists(raw_audio): os.remove(raw_audio)
        
        dur = get_duration(mastered_audio)
        print(f"Duración locución: {dur:.2f} segundos")
        
        # 3. Renderizar subclip sincronizado a 1080p
        if sc["is_video"]:
            seek = sc.get("seek", 0)
            cmd = [
                FFMPEG, "-y",
                "-ss", str(seek),
                "-i", media_path,
                "-i", mastered_audio,
                "-t", str(dur),
                "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,format=yuv420p,fps=30",
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
                "-c:a", "aac", "-b:a", "192k",
                clip_path
            ]
        else:
            cmd = [
                FFMPEG, "-y",
                "-loop", "1",
                "-i", media_path,
                "-i", mastered_audio,
                "-t", str(dur),
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k",
                clip_path
            ]
            
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="ignore")
        if res.returncode != 0:
            print(f"Error renderizando escena {sid}: {res.stderr[-300:]}")
        else:
            print(f"OK Escena {sid:02d} completada.")
        clip_paths.append(clip_path)

    # 4. Concatenación de clips sin pérdida
    print("\nConcatenando todos los clips en línea de tiempo...")
    with open(clip_list_file, "w", encoding="utf-8") as f:
        for cp in clip_paths:
            escaped = cp.replace('\\', '/')
            f.write(f"file '{escaped}'\n")

    raw_concat = os.path.join(TEMP_DIR, "raw_concatenated.mp4")
    concat_cmd = [
        FFMPEG, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", clip_list_file,
        "-c", "copy",
        raw_concat
    ]
    subprocess.run(concat_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    # 5. Mezcla de Banda Sonora Cinematográfica (Ducking al 12% con Fade-Out)
    total_dur = get_duration(raw_concat)
    fade_start = max(0, int(total_dur - 4))
    print(f"\nMezclando banda sonora cinemática ({MUSIC_FILE})...")
    print(f"Duración total del documental = {total_dur:.2f}s ({total_dur/60:.2f} minutos)")

    final_cmd = [
        FFMPEG, "-y",
        "-i", raw_concat,
        "-stream_loop", "-1",
        "-i", MUSIC_FILE,
        "-filter_complex",
        f"[1:a]volume=0.12,afade=t=out:st={fade_start}:d=4[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        FINAL_OUTPUT
    ]
    subprocess.run(final_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    print("\n============================================================")
    print(" ¡DOCUMENTAL PUNTO NEMO CREADO EXITOSAMENTE!")
    print(f" Archivo final: {FINAL_OUTPUT}")
    print(f" Duración: {total_dur:.2f}s ({total_dur/60:.2f} minutos)")
    print("============================================================\n")

if __name__ == "__main__":
    asyncio.run(render_documentary())
