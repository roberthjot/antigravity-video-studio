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

FINAL_OUTPUT = os.path.join(PROJECT_DIR, "documental_punto_nemo_8MIN_FINAL.mp4")
SOUNDTRACK = os.path.join(PROJECT_DIR, "soundtrack_dinamico_8min.mp3")

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

# Cadena de Masterización Vocal de Estudio (Broadcast Vocal Chain)
vocal_filter = (
    "highpass=f=75,"
    "equalizer=f=180:t=q:w=1.5:g=3.5,"
    "equalizer=f=3200:t=q:w=1.2:g=2.2,"
    "acompressor=threshold=-18dB:ratio=3.5:attack=15:release=140:makeup=2.5,"
    "alimiter=limit=-1dB"
)

# Filtros de movimiento de cámara Ken Burns
MOTION_FILTERS = {
    "zoom_in": "zoompan=z='min(zoom+0.00045,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=30",
    "zoom_out": "zoompan=z='if(lte(on,1),1.15,max(1.00,zoom-0.00045))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=30",
    "pan_right": "zoompan=z=1.12:x='min((on/120)*(iw-iw/zoom),iw-iw/zoom)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=30",
    "pan_left": "zoompan=z=1.12:x='max((1-on/120)*(iw-iw/zoom),0)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=30"
}

SCENES_8MIN = [
    # --- ACTO 1: LAS COORDENADAS DEL AISLAMIENTO ABSOLUTO ---
    {
        "id": 1,
        "text": "En medio de la inmensidad del océano Pacífico... existe un punto donde la soledad alcanza su expresión más aterradora. Las coordenadas: cuarenta y ocho grados cincuenta y dos minutos sur... ciento veintitrés grados veintitrés minutos oeste. Bienvenido al Punto Nemo.",
        "media": "00_intro_video_olas.webm",
        "is_video": True,
        "seek": 0,
        "motion": "video",
        "pitch": "+1Hz",
        "rate": "+2%"
    },
    {
        "id": 2,
        "text": "Conocido oficialmente como el Polo Oceánico de Inaccesibilidad, es el lugar de la superficie terrestre más alejado de cualquier masa continental o pedazo de tierra firme en todo el planeta.",
        "media": "01_mapa_punto_nemo.jpg",
        "is_video": False,
        "motion": "zoom_in",
        "pitch": "+0Hz",
        "rate": "+0%"
    },
    {
        "id": 3,
        "text": "La costa más cercana, un diminuto islote desierto en la Polinesia llamado Ducie, se encuentra a más de dos mil seiscientos ochenta y ocho kilómetros de distancia. Si naufragaras aquí... los seres humanos más cercanos a ti no estarían en barcos ni en islas.",
        "media": "02_mapa_polo_inaccesibilidad.jpg",
        "is_video": False,
        "motion": "zoom_out",
        "pitch": "-3Hz",
        "rate": "-4%"
    },
    {
        "id": 4,
        "text": "Estarían a cuatrocientos kilómetros sobre tu cabeza... flotando en la oscuridad del espacio a bordo de la Estación Espacial Internacional cada vez que su órbita pasa justo por encima de este abismo.",
        "media": "04_astronauta_cupola.jpg",
        "is_video": False,
        "motion": "zoom_in",
        "pitch": "-2Hz",
        "rate": "-2%"
    },

    # --- ACTO 2: EL CEMENTERIO DE NAVES ESPACIALES ---
    {
        "id": 5,
        "text": "Pero su aislamiento extremo no es solo una curiosidad geográfica. Durante décadas, las agencias espaciales más poderosas del planeta han utilizado este punto exacto con un propósito siniestro y fascinante: el cementerio de naves espaciales.",
        "media": "03_tierra_pacifico_desde_iss.jpg",
        "is_video": False,
        "motion": "pan_right",
        "pitch": "-1Hz",
        "rate": "+1%"
    },
    {
        "id": 6,
        "text": "A más de cuatro mil metros de profundidad, descansan los restos de más de doscientas sesenta naves espaciales, satélites espía y colosales cargueros desintegrados por reingreso atmosférico.",
        "media": "06_carguero_progress.jpg",
        "is_video": False,
        "motion": "zoom_out",
        "pitch": "-3Hz",
        "rate": "-3%"
    },
    {
        "id": 7,
        "text": "En marzo de dos mil uno, la legendaria estación espacial soviética Mir, con un peso de ciento cuarenta y tres toneladas, fue precipitada deliberadamente hacia la atmósfera, cruzando el cielo como una violenta bola de fuego antes de sepultarse para siempre en estas aguas.",
        "media": "05_estacion_espacial_mir.jpg",
        "is_video": False,
        "motion": "zoom_in",
        "pitch": "-1Hz",
        "rate": "+3%"
    },
    {
        "id": 8,
        "text": "Titanio calcinado, aleaciones militares secretas y residuos atómicos yacen en la oscuridad eterna del lecho marino... en una tumba donde ningún ser humano jamás podrá descender a rescatarlos.",
        "media": "07_reingreso_atmosferico_fuego.jpg",
        "is_video": False,
        "motion": "pan_left",
        "pitch": "-5Hz",
        "rate": "-5%"
    },

    # --- ACTO 3: EL SONIDO THE BLOOP Y EL MISTERIO ABISAL ---
    {
        "id": 9,
        "text": "Sin embargo, el misterio más perturbador del Punto Nemo no cayó del cielo... emergió de las profundidades. En el verano de mil novecientos noventa y siete, los micrófonos submarinos de la agencia oceanográfica NOAA registraron una señal estremecedora.",
        "media": "10_hidrofono_submarino.jpg",
        "is_video": False,
        "motion": "zoom_in",
        "pitch": "+1Hz",
        "rate": "+1%"
    },
    {
        "id": 10,
        "text": "Bautizado como The Bloop, fue un sonido de ultra baja frecuencia tan descomunalmente potente que fue captado por hidrófonos separados por más de cinco mil kilómetros de distancia a lo largo de todo el océano Pacífico.",
        "media": "09_bloop_espectrograma.jpg",
        "is_video": False,
        "motion": "pan_right",
        "pitch": "-2Hz",
        "rate": "-3%"
    },
    {
        "id": 11,
        "text": "Su firma acústica se asemejaba al patrón de un ser biológico vivo, pero con una potencia varias veces superior al rugido de la ballena azul más gigantesca jamás documentada. Durante años, la sospecha de una criatura abisal desconocida desconcertó a la comunidad científica.",
        "media": "15_submarino_profundidades.jpg",
        "is_video": False,
        "motion": "zoom_out",
        "pitch": "-4Hz",
        "rate": "-5%"
    },
    {
        "id": 12,
        "text": "Años más tarde, los científicos determinaron que el sonido probablemente provino de un gigantesco criosismo: la fractura y colapso de una masa masiva de hielo en los confines de la Antártida, resonando a través del abismo oceánico.",
        "media": "12_iceberg_antartida_criosismo.jpg",
        "is_video": False,
        "motion": "zoom_in",
        "pitch": "-1Hz",
        "rate": "+1%"
    },

    # --- ACTO 4: EL DESIERTO BIOLÓGICO DEL OCÉANO ---
    {
        "id": 13,
        "text": "Pero incluso sin monstruos marinos, la realidad biológica del Punto Nemo es aún más desoladora. Este sector se sitúa justo en el centro del Giro del Pacífico Sur, una gigantesca corriente oceánica circular que atrapa y aísla sus aguas.",
        "media": "25_navegacion_sigilo_radar.jpg",
        "is_video": False,
        "motion": "pan_left",
        "pitch": "+0Hz",
        "rate": "+0%"
    },
    {
        "id": 14,
        "text": "Aquí no llegan corrientes ricas en nutrientes. No existe plancton suficiente, y por lo tanto, no hay cardúmenes de peces, ni tiburones, ni mamíferos marinos. Es el desierto biológico más estéril del planeta Tierra.",
        "media": "03_tierra_pacifico_desde_iss.jpg",
        "is_video": False,
        "motion": "zoom_out",
        "pitch": "-3Hz",
        "rate": "-4%"
    },
    {
        "id": 15,
        "text": "El agua en este abismo es tan transparente y desprovista de organismos vivos que la luz solar penetra hasta profundidades insólitas, creando un azul cobalto tan puro como aterrador.",
        "media": "24_horizonte_vasto_atardecer.jpg",
        "is_video": False,
        "motion": "pan_right",
        "pitch": "-2Hz",
        "rate": "-2%"
    },

    # --- ACTO 5: LA COINCIDENCIA DE H.P. LOVECRAFT ---
    {
        "id": 16,
        "text": "Y es aquí donde la ciencia se cruza con una de las coincidencias más inquietantes de la historia. En mil novecientos veintiocho, el legendario maestro del terror H. P. Lovecraft escribió su célebre obra: La Llamada de Cthulhu.",
        "media": "16_cthulhu_monstruo_marino.jpg",
        "is_video": False,
        "motion": "zoom_in",
        "pitch": "+1Hz",
        "rate": "+2%"
    },
    {
        "id": 17,
        "text": "En el texto, Lovecraft situó la ancestral ciudad sumergida de R'lyeh... casi exactamente en las mismas coordenadas del Punto Nemo, sesenta y seis años antes de que el ingeniero Hrvoje Lukatela las calculara matemáticamente en mil novecientos noventa y dos.",
        "media": "18_criatura_abisal_mitologia.jpg",
        "is_video": False,
        "motion": "zoom_out",
        "pitch": "-3Hz",
        "rate": "-4%"
    },
    {
        "id": 18,
        "text": "¿Cómo pudo un escritor a principios del siglo veinte intuir con semejante precisión el punto más solitario de la Tierra, décadas antes de la existencia de satélites o supercomputadoras?",
        "media": "16_cthulhu_monstruo_marino.jpg",
        "is_video": False,
        "motion": "pan_left",
        "pitch": "-4Hz",
        "rate": "-4%"
    },

    # --- ACTO 6: LOS NAVEGANTES EXTREMOS Y LA PESADILLA DEL RESCATE ---
    {
        "id": 19,
        "text": "A pesar de este vacío absoluto, existe un grupo reducido de seres humanos que se atreve a desafiar estas coordenadas: los navegantes profesionales de la regata The Ocean Race.",
        "media": "22_operaciones_alta_mar.webm",
        "is_video": True,
        "seek": 5,
        "motion": "video",
        "pitch": "+1Hz",
        "rate": "+2%"
    },
    {
        "id": 20,
        "text": "Surcando los mares más tempestuosos del hemisferio sur, estos barcos navegan con vientos sostenidos de más de cien kilómetros por hora y olas colosales que superan la altura de un edificio de seis pisos.",
        "media": "00_intro_video_olas.webm",
        "is_video": True,
        "seek": 12,
        "motion": "video",
        "pitch": "-2Hz",
        "rate": "+3%"
    },
    {
        "id": 21,
        "text": "Para estos marineros, la realidad es brutal: si sufres una emergencia médica grave, un incendio o la rotura del casco en el Punto Nemo... la ayuda simplemente no llegará. Los buques de rescate más veloces tardarían entre diez y catorce días en alcanzar tu posición.",
        "media": "25_navegacion_sigilo_radar.jpg",
        "is_video": False,
        "motion": "zoom_in",
        "pitch": "-4Hz",
        "rate": "-4%"
    },
    {
        "id": 22,
        "text": "Durante las noches sin luna, la tripulación contempla un horizonte completamente negro donde el mar y el cielo se funden en una sola masa de oscuridad... una experiencia psicológica descrita por los capitanes como la máxima prueba de cordura en altamar.",
        "media": "24_horizonte_vasto_atardecer.jpg",
        "is_video": False,
        "motion": "zoom_out",
        "pitch": "-3Hz",
        "rate": "-5%"
    },

    # --- ACTO 7: LA FÍSICA DEL REINGRESO A MACH 25 ---
    {
        "id": 23,
        "text": "Pero el verdadero peligro que acecha sobre este océano viene de las alturas. Cada vez que una misión espacial concluye y es enviada hacia el Punto Nemo, se desencadena uno de los fenómenos físicos más destructivos creados por el ser humano.",
        "media": "03_tierra_pacifico_desde_iss.jpg",
        "is_video": False,
        "motion": "pan_right",
        "pitch": "+1Hz",
        "rate": "+1%"
    },
    {
        "id": 24,
        "text": "Al cruzar las capas densas de la atmósfera a veintisiete mil kilómetros por hora, la compresión de aire genera temperaturas de más de dos mil quinientos grados Celsius, envolviendo la nave en una gigantesca burbuja de plasma incandescente.",
        "media": "07_reingreso_atmosferico_fuego.jpg",
        "is_video": False,
        "motion": "zoom_in",
        "pitch": "-1Hz",
        "rate": "+3%"
    },
    {
        "id": 25,
        "text": "Mientras el aluminio y los paneles solares arden y se desintegran en milésimas de segundo, los tanques de titanio militar y las cámaras de combustión de acero inoxidable sobreviven, cayendo a cientos de kilómetros por hora sobre las aguas.",
        "media": "06_carguero_progress.jpg",
        "is_video": False,
        "motion": "zoom_out",
        "pitch": "-3Hz",
        "rate": "-2%"
    },

    # --- ACTO 8: EL FIN DE LA ISS EN 2031 Y EL CLÍMAX ---
    {
        "id": 26,
        "text": "En el año dos mil treinta y uno, este cementerio acuático recibirá su huésped más ilustre. La Estación Espacial Internacional, el mayor artefacto científico construido en la historia de la humanidad, cumplirá el final de su misión.",
        "media": "19_estacion_espacial_internacional.jpg",
        "is_video": False,
        "motion": "pan_left",
        "pitch": "+0Hz",
        "rate": "+2%"
    },
    {
        "id": 27,
        "text": "Con un peso astronómico de más de cuatrocientas veinte toneladas, la NASA y sus socios internacionales la dirigirán en una trayectoria suicida hacia el corazón del Punto Nemo, iluminando la noche con una tormenta de fragmentos ardientes.",
        "media": "07_reingreso_atmosferico_fuego.jpg",
        "is_video": False,
        "motion": "zoom_in",
        "pitch": "-2Hz",
        "rate": "+2%"
    },
    {
        "id": 28,
        "text": "Módulos de investigación, laboratorios espaciales y tres décadas de sueños científicos quedarán sumergidos para siempre a cuatro mil metros bajo las olas, reposando junto a la estación Mir en el lecho marino.",
        "media": "05_estacion_espacial_mir.jpg",
        "is_video": False,
        "motion": "zoom_out",
        "pitch": "-4Hz",
        "rate": "-4%"
    },

    # --- ACTO 9: EL ABISMO ETERNO Y CONCLUSIÓN ---
    {
        "id": 29,
        "text": "En las profundidades del Punto Nemo reina una presión de cuatrocientas atmósferas y una temperatura glacial. Un ambiente impenetrable donde la naturaleza no perdona errores y el tiempo parece haberse congelado.",
        "media": "23_hielo_polar_antartico.jpg",
        "is_video": False,
        "motion": "pan_right",
        "pitch": "-4Hz",
        "rate": "-5%"
    },
    {
        "id": 30,
        "text": "Este lugar nos recuerda una verdad fundamental: por muy avanzada que sea nuestra tecnología y por muy lejos que lleguen nuestras naves espaciales, nuestro propio planeta aún guarda abismos insondables que jamás podremos controlar.",
        "media": "15_submarino_profundidades.jpg",
        "is_video": False,
        "motion": "zoom_in",
        "pitch": "-3Hz",
        "rate": "-3%"
    },
    {
        "id": 31,
        "text": "¿Serías capaz de resistir una sola noche flotando en soledad sobre el abismo del Punto Nemo? Cuéntanos tu teoría sobre los secretos de este océano en la sección de comentarios.",
        "media": "21_atardecer_dorado_pacifico.jpg",
        "is_video": False,
        "motion": "zoom_out",
        "pitch": "-1Hz",
        "rate": "+0%"
    },
    {
        "id": 32,
        "text": "Si este recorrido por el rincón más aislado del planeta te ha cautivado, déjanos tu me gusta, comparte este video con otros amantes de los misterios y suscríbete para acompañarnos en nuestra próxima gran expedición. ¡Hasta la próxima historia!",
        "media": "00_intro_video_olas.webm",
        "is_video": True,
        "seek": 22,
        "motion": "video",
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
    return 15.0

async def render_scene_audio(sc, voice_actor):
    sid = sc["id"]
    mastered_audio = os.path.join(TEMP_DIR, f"master_audio_{sid:02d}.mp3")
    if os.path.exists(mastered_audio) and os.path.getsize(mastered_audio) > 10000:
        return mastered_audio
        
    raw_audio = os.path.join(TEMP_DIR, f"raw_audio_{sid:02d}.mp3")
    comm = edge_tts.Communicate(sc["text"], voice_actor, rate=sc["rate"], pitch=sc["pitch"])
    await comm.save(raw_audio)
    
    cmd = [FFMPEG, "-y", "-i", raw_audio, "-af", vocal_filter, "-b:a", "192k", mastered_audio]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    if os.path.exists(raw_audio): os.remove(raw_audio)
    return mastered_audio

async def build_8min():
    print("==================================================================")
    print(f"   MONTAJE MAESTRO 8 MINUTOS: EL PUNTO NEMO ({len(SCENES_8MIN)} ESCENAS)")
    print("==================================================================\n")
    
    VOICE_ACTOR = "es-MX-JorgeNeural"
    clean_clips = []
    concat_list = os.path.join(TEMP_DIR, "concat_8min_list.txt")

    for sc in SCENES_8MIN:
        sid = sc["id"]
        out_clip = os.path.join(TEMP_DIR, f"clip_8m_{sid:02d}.mp4")
        
        # 1. Asegurar audio masterizado para la escena
        audio_file = await render_scene_audio(sc, VOICE_ACTOR)
        dur = get_duration(audio_file)
        
        # 2. Renderizar escena con movimiento y encuadre
        if sc["is_video"]:
            media_path = os.path.join(MEDIA_DIR, sc["media"])
            cmd = [
                FFMPEG, "-y",
                "-ss", str(sc.get("seek", 0)),
                "-i", media_path,
                "-i", audio_file,
                "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,format=yuv420p,fps=30",
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
                "-map", "0:v", "-map", "1:a",
                "-shortest",
                out_clip
            ]
        else:
            media_path = os.path.join(OPTIMIZED_DIR, sc["media"])
            motion_cmd = MOTION_FILTERS.get(sc["motion"], MOTION_FILTERS["zoom_in"])
            cmd = [
                FFMPEG, "-y",
                "-loop", "1",
                "-i", media_path,
                "-i", audio_file,
                "-vf", f"{motion_cmd},format=yuv420p",
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
                "-map", "0:v", "-map", "1:a",
                "-shortest",
                out_clip
            ]
            
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        clean_clips.append(out_clip)
        print(f"-> Escena {sid:02d}/{len(SCENES_8MIN):02d} lista ({dur:.1f}s | {sc['motion']} | {sc['media']})")

    # 3. Concatenar los 32 clips
    print("\nConcatenando las 32 escenas en línea de tiempo unificada...")
    with open(concat_list, "w", encoding="utf-8") as f:
        for cp in clean_clips:
            escaped = cp.replace('\\', '/')
            f.write(f"file '{escaped}'\n")

    raw_concat = os.path.join(TEMP_DIR, "raw_8min_concat.mp4")
    concat_cmd = [
        FFMPEG, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        raw_concat
    ]
    subprocess.run(concat_cmd, check=True)

    # 4. Medir duración exacta del documental de 8 minutos
    cmd_dur = [FFMPEG, "-i", raw_concat]
    res = subprocess.run(cmd_dur, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, errors="ignore")
    total_dur = 480.0
    for line in res.stderr.split("\n"):
        if "Duration:" in line:
            part = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = part.split(":")
            total_dur = float(h)*3600 + float(m)*60 + float(s)
            break

    print(f"\n¡Duración total del documental ensamblado: {total_dur:.2f}s ({total_dur/60:.2f} minutos)!")
    fade_start = max(0, int(total_dur - 5))

    # 5. Mezcla de Banda Sonora Dinámica (Ducking al 12% con Fade-Out)
    print(f"Mezclando banda sonora dinámica cinematográfica ({SOUNDTRACK})...")
    final_cmd = [
        FFMPEG, "-y",
        "-i", raw_concat,
        "-i", SOUNDTRACK,
        "-filter_complex",
        f"[1:a]volume=0.12,afade=t=out:st={fade_start}:d=5[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        FINAL_OUTPUT
    ]
    subprocess.run(final_cmd, check=True)
    print("\n==================================================================")
    print(" ¡DOCUMENTAL DE 8 MINUTOS CREADO Y FINALIZADO CON ÉXITO!")
    print(f" Archivo final: {FINAL_OUTPUT}")
    print(f" Duración final: {total_dur:.2f} segundos ({total_dur/60:.2f} minutos)")
    print("==================================================================\n")

if __name__ == "__main__":
    asyncio.run(build_8min())
