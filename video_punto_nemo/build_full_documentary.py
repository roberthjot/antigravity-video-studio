import os
import sys
import subprocess
import imageio_ffmpeg

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_DIR = r"c:\Users\Owner\Documents\antigravity\beautiful-hertz\video_punto_nemo"
MEDIA_DIR = os.path.join(PROJECT_DIR, "media")
OPTIMIZED_DIR = os.path.join(PROJECT_DIR, "optimized_1080p")
TEMP_DIR = os.path.join(PROJECT_DIR, "temp_clips")
FINAL_OUTPUT = os.path.join(PROJECT_DIR, "documental_punto_nemo_MASTER.mp4")
MUSIC_FILE = os.path.join(PROJECT_DIR, "musica_deep.oga")

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

MEDIA_MAPPING = [
    # Acto 1
    (1, "00_intro_video_olas.webm", True, 0),
    (2, "01_mapa_punto_nemo.jpg", False, 0),
    (3, "02_mapa_polo_inaccesibilidad.jpg", False, 0),
    (4, "04_astronauta_cupola.jpg", False, 0),
    # Acto 2
    (5, "03_tierra_pacifico_desde_iss.jpg", False, 0),
    (6, "06_carguero_progress.jpg", False, 0),
    (7, "05_estacion_espacial_mir.jpg", False, 0),
    (8, "07_reingreso_atmosferico_fuego.jpg", False, 0),
    # Acto 3
    (9, "10_hidrofono_submarino.jpg", False, 0),
    (10, "09_bloop_espectrograma.jpg", False, 0),
    (11, "15_submarino_profundidades.jpg", False, 0),
    (12, "12_iceberg_antartida_criosismo.jpg", False, 0),
    # Acto 4
    (13, "15_submarino_profundidades.jpg", False, 0),
    (14, "03_tierra_pacifico_desde_iss.jpg", False, 0),
    # Acto 5
    (15, "16_cthulhu_monstruo_marino.jpg", False, 0),
    (16, "18_criatura_abisal_mitologia.jpg", False, 0),
    # Acto 6
    (17, "19_estacion_espacial_internacional.jpg", False, 0),
    (18, "07_reingreso_atmosferico_fuego.jpg", False, 0),
    (19, "21_atardecer_dorado_pacifico.jpg", False, 0),
    (20, "00_intro_video_olas.webm", True, 20)
]

def build():
    print("=== INICIANDO MONTAJE CINEMATOGRÁFICO DE PUNTO NEMO ===")
    concat_list = os.path.join(TEMP_DIR, "master_concat_list.txt")
    final_clips = []
    
    for sid, media_name, is_video, seek in MEDIA_MAPPING:
        audio_file = os.path.join(TEMP_DIR, f"master_audio_{sid:02d}.mp3")
        out_clip = os.path.join(TEMP_DIR, f"clean_clip_{sid:02d}.mp4")
        
        if is_video:
            media_path = os.path.join(MEDIA_DIR, media_name)
            cmd = [
                FFMPEG, "-y",
                "-ss", str(seek),
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
            media_path = os.path.join(OPTIMIZED_DIR, media_name)
            cmd = [
                FFMPEG, "-y",
                "-loop", "1",
                "-i", media_path,
                "-i", audio_file,
                "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,format=yuv420p,fps=30",
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
                "-map", "0:v", "-map", "1:a",
                "-shortest",
                out_clip
            ]
            
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        final_clips.append(out_clip)
        print(f"-> Escena {sid:02d}/20 lista ({media_name})")

    # Escribir lista de concatenación
    with open(concat_list, "w", encoding="utf-8") as f:
        for p in final_clips:
            escaped = p.replace('\\', '/')
            f.write(f"file '{escaped}'\n")

    raw_concat = os.path.join(TEMP_DIR, "raw_documental_completo.mp4")
    print("\nConcatenando todos los 20 clips en línea de tiempo...")
    concat_cmd = [
        FFMPEG, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        raw_concat
    ]
    subprocess.run(concat_cmd, check=True)

    # Medir duración exacta del documental
    cmd_dur = [FFMPEG, "-i", raw_concat]
    res = subprocess.run(cmd_dur, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, errors="ignore")
    total_dur = 294.0
    for line in res.stderr.split("\n"):
        if "Duration:" in line:
            part = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = part.split(":")
            total_dur = float(h)*3600 + float(m)*60 + float(s)
            break

    print(f"\n¡Concatenación impecable! Duración total: {total_dur:.2f}s ({total_dur/60:.2f} minutos)")
    fade_start = max(0, int(total_dur - 5))

    # Mezcla de banda sonora cinematográfica con ducking y fade-out
    print(f"Mezclando banda sonora cinemática ({MUSIC_FILE})...")
    final_cmd = [
        FFMPEG, "-y",
        "-i", raw_concat,
        "-stream_loop", "-1",
        "-i", MUSIC_FILE,
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
    print("\n============================================================")
    print(" ¡DOCUMENTAL DE PUNTO NEMO FINALIZADO CON ÉXITO!")
    print(f" Archivo final: {FINAL_OUTPUT}")
    print(f" Duración: {total_dur:.2f}s ({total_dur/60:.2f} minutos)")
    print("============================================================\n")

if __name__ == "__main__":
    build()
