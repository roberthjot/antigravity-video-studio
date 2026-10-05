import os
import subprocess
import imageio_ffmpeg

PROJECT_DIR = r"c:\Users\Owner\Documents\antigravity\beautiful-hertz\video_punto_nemo"
TEMP_DIR = os.path.join(PROJECT_DIR, "temp_clips")
FINAL_OUTPUT = os.path.join(PROJECT_DIR, "documental_punto_nemo_MASTER.mp4")
MUSIC_FILE = os.path.join(PROJECT_DIR, "musica_deep.oga")
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

def finalize():
    clip_list_file = os.path.join(TEMP_DIR, "concat_list.txt")
    with open(clip_list_file, "w", encoding="utf-8") as f:
        for i in range(1, 21):
            cp = os.path.join(TEMP_DIR, f"clip_{i:02d}.mp4")
            escaped = cp.replace('\\', '/')
            f.write(f"file '{escaped}'\n")

    raw_concat = os.path.join(TEMP_DIR, "raw_concatenated.mp4")
    print("1. Concatenando los 20 clips...")
    cmd1 = [
        FFMPEG, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", clip_list_file,
        "-c", "copy",
        raw_concat
    ]
    subprocess.run(cmd1, check=True)

    # Medir duracion total
    cmd_dur = [FFMPEG, "-i", raw_concat]
    res = subprocess.run(cmd_dur, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, errors="ignore")
    total_dur = 294.0
    for line in res.stderr.split("\n"):
        if "Duration:" in line:
            part = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = part.split(":")
            total_dur = float(h)*3600 + float(m)*60 + float(s)
            break

    fade_start = max(0, int(total_dur - 4))
    print(f"2. Mezclando música de fondo... Duración total = {total_dur:.2f}s ({total_dur/60:.2f} min)")

    cmd2 = [
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
    subprocess.run(cmd2, check=True)
    print(f"✅ ¡DOCUMENTAL FINALIZADO CON ÉXITO! -> {FINAL_OUTPUT}")

if __name__ == "__main__":
    finalize()
