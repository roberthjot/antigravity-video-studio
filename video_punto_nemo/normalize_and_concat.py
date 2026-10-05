import os
import sys
import subprocess
import imageio_ffmpeg

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_DIR = r"c:\Users\Owner\Documents\antigravity\beautiful-hertz\video_punto_nemo"
TEMP_DIR = os.path.join(PROJECT_DIR, "temp_clips")
FINAL_OUTPUT = os.path.join(PROJECT_DIR, "documental_punto_nemo_MASTER.mp4")
MUSIC_FILE = os.path.join(PROJECT_DIR, "musica_deep.oga")
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

def normalize_and_concat():
    print("Normalizando todos los 20 clips a 30 fps exactos y tiempo estandarizado...")
    concat_list_file = os.path.join(TEMP_DIR, "clean_concat_list.txt")
    norm_paths = []
    
    for i in range(1, 21):
        in_clip = os.path.join(TEMP_DIR, f"clip_{i:02d}.mp4")
        norm_clip = os.path.join(TEMP_DIR, f"norm_clip_{i:02d}.mp4")
        
        # Estandarizar a 30fps y timebase 15360 exactos
        cmd = [
            FFMPEG, "-y",
            "-i", in_clip,
            "-r", "30",
            "-video_track_timescale", "15360",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "24000",
            norm_clip
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        norm_paths.append(norm_clip)
        print(f"   [OK] Normalizado clip {i:02d}")

    # Escribir lista de concatenación limpia
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for p in norm_paths:
            escaped = p.replace('\\', '/')
            f.write(f"file '{escaped}'\n")

    raw_concat = os.path.join(TEMP_DIR, "raw_concatenated_full.mp4")
    print("\nConcatenando todos los 20 clips...")
    concat_cmd = [
        FFMPEG, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list_file,
        "-c", "copy",
        raw_concat
    ]
    subprocess.run(concat_cmd, check=True)

    # Medir duracion total exacta
    cmd_dur = [FFMPEG, "-i", raw_concat]
    res = subprocess.run(cmd_dur, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, errors="ignore")
    total_dur = 294.0
    for line in res.stderr.split("\n"):
        if "Duration:" in line:
            part = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = part.split(":")
            total_dur = float(h)*3600 + float(m)*60 + float(s)
            break

    print(f"\n¡Concatenación completada! Duración total = {total_dur:.2f}s ({total_dur/60:.2f} minutos)")
    fade_start = max(0, int(total_dur - 5))

    # Mezclar música de fondo cinemática al 12% con fade-out al final
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
    print(" ¡DOCUMENTAL COMPLETO DE PUNTO NEMO CREADO EXITOSAMENTE!")
    print(f" Archivo final: {FINAL_OUTPUT}")
    print(f" Duración final: {total_dur:.2f}s ({total_dur/60:.2f} minutos)")
    print("============================================================\n")

if __name__ == "__main__":
    normalize_and_concat()
