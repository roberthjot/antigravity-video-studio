import http.server
import socketserver
import os
import re
import sys
import json
import subprocess
import imageio_ffmpeg

PORT = 8090
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

class VideoEditorHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, HEAD, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Range, Content-Type')
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/render':
            self.handle_render()
        elif self.path == '/api/detect_silence':
            self.handle_detect_silence()
        else:
            self.send_error(404, 'Endpoint not found')

    def handle_detect_silence(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            params = json.loads(body) if body else {}

            threshold_db = params.get('threshold_db', -28)
            min_duration = params.get('min_duration', 0.25)
            lead_padding = params.get('lead_padding', 0.06)
            trail_padding = params.get('trail_padding', 0.12)

            json_path = os.path.join(DIRECTORY, 'clips_timeline_data.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            timeline_cursor = 0.0
            for clip in data['clips']:
                inp = os.path.join(DIRECTORY, clip['filename'])
                if not os.path.exists(inp):
                    continue

                total_dur = clip['total_duration']
                cmd_s = [FFMPEG, '-i', inp, '-af', f'silencedetect=n={threshold_db}dB:d={min_duration}', '-f', 'null', '-']
                res_s = subprocess.run(cmd_s, stderr=subprocess.PIPE, text=True)

                s_starts = [float(x) for x in re.findall(r'silence_start:\s*([\d\.]+)', res_s.stderr)]
                s_ends = [float(x) for x in re.findall(r'silence_end:\s*([\d\.]+)', res_s.stderr)]

                start_trim = 0.0
                if s_starts and s_ends and s_starts[0] <= 0.08:
                    start_trim = max(0.0, s_ends[0] - lead_padding)

                end_trim = total_dur
                if s_starts and s_starts[-1] >= total_dur - 1.8:
                    end_trim = min(total_dur, s_starts[-1] + trail_padding)

                clip_dur = end_trim - start_trim
                clip['start_trim'] = round(start_trim, 3)
                clip['end_trim'] = round(end_trim, 3)
                clip['trimmed_duration'] = round(clip_dur, 3)
                clip['timeline_start'] = round(timeline_cursor, 3)
                clip['timeline_end'] = round(timeline_cursor + clip_dur, 3)
                clip['silence_starts'] = s_starts
                clip['silence_ends'] = s_ends

                # Detect internal pauses
                internal = []
                for s_st, s_en in zip(s_starts, s_ends):
                    if s_st >= start_trim + 0.1 and s_en <= end_trim - 0.1:
                        dur = s_en - s_st
                        if dur >= min_duration:
                            internal.append({
                                'start_in_clip': round(s_st, 2),
                                'end_in_clip': round(s_en, 2),
                                'duration': round(dur, 2),
                                'timeline_pos': round(timeline_cursor + (s_st - start_trim), 2)
                            })
                clip['internal_pauses'] = internal
                timeline_cursor += clip_dur

            data['total_duration'] = round(timeline_cursor, 3)

            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            resp_bytes = json.dumps({'ok': True, 'data': data}, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(resp_bytes)))
            self.end_headers()
            self.wfile.write(resp_bytes)
        except Exception as e:
            err = json.dumps({'ok': False, 'error': str(e)}).encode('utf-8')
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(err)))
            self.end_headers()
            self.wfile.write(err)

    def handle_render(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            payload = json.loads(body) if body else {}

            clips_list = payload.get('clips', [])
            music_volume = float(payload.get('music_volume', 1.0))
            fade_out = float(payload.get('fade_out', 2.5))
            music_file = os.path.join(DIRECTORY, payload.get('music_file', 'music-frutas.mp3'))
            out_video = os.path.join(DIRECTORY, 'CAPITULO_2_FINAL.mp4')
            temp_dir = os.path.join(DIRECTORY, 'temp_edit')
            os.makedirs(temp_dir, exist_ok=True)

            trimmed_clips = []
            timeline_cursor = 0.0

            # 1. Trim each clip according to client values
            for idx, item in enumerate(clips_list):
                fname = item['filename']
                inp = os.path.join(DIRECTORY, fname)
                st = max(0.0, float(item.get('start_trim', 0.0)))
                en = float(item.get('end_trim', 6.0))
                
                # Check segments if user cut internal pauses
                segments = item.get('segments', None)
                if segments and len(segments) > 1:
                    # Multi-segment trimming for internal silence cut
                    seg_files = []
                    for s_idx, seg in enumerate(segments):
                        s_st = seg['start']
                        s_en = seg['end']
                        seg_out = os.path.join(temp_dir, f'part_{idx:02d}_{s_idx}_{fname}')
                        cmd = [
                            FFMPEG, '-y',
                            '-ss', f'{s_st:.3f}', '-to', f'{s_en:.3f}',
                            '-i', inp,
                            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '19',
                            '-c:a', 'aac', '-b:a', '192k',
                            seg_out
                        ]
                        subprocess.run(cmd, capture_output=True, check=True)
                        seg_files.append(seg_out)
                    
                    # Concat sub-segments
                    sub_list = os.path.join(temp_dir, f'sublist_{idx}.txt')
                    with open(sub_list, 'w', encoding='utf-8') as sf:
                        for s_f in seg_files:
                            sf.write(f"file '{s_f.replace(chr(92), '/')}'\n")
                    
                    out_clip = os.path.join(temp_dir, f'trimmed_{idx:02d}_{fname}')
                    cmd_sub_c = [FFMPEG, '-y', '-f', 'concat', '-safe', '0', '-i', sub_list, '-c', 'copy', out_clip]
                    subprocess.run(cmd_sub_c, capture_output=True, check=True)
                    trimmed_clips.append(out_clip)
                else:
                    out_clip = os.path.join(temp_dir, f'trimmed_{idx:02d}_{fname}')
                    cmd_cut = [
                        FFMPEG, '-y',
                        '-ss', f'{st:.3f}', '-to', f'{en:.3f}',
                        '-i', inp,
                        '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '19',
                        '-c:a', 'aac', '-b:a', '192k',
                        out_clip
                    ]
                    subprocess.run(cmd_cut, capture_output=True, check=True)
                    trimmed_clips.append(out_clip)

            # 2. Concat trimmed clips
            concat_list = os.path.join(temp_dir, 'concat_list.txt')
            with open(concat_list, 'w', encoding='utf-8') as f:
                for c in trimmed_clips:
                    clean = c.replace('\\', '/')
                    f.write(f"file '{clean}'\n")

            concat_video = os.path.join(temp_dir, 'concat_temp.mp4')
            cmd_concat = [
                FFMPEG, '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_list,
                '-c', 'copy',
                concat_video
            ]
            subprocess.run(cmd_concat, capture_output=True, check=True)

            # Get duration of concatenated video
            r_v = subprocess.run([FFMPEG, '-i', concat_video], stderr=subprocess.PIPE, text=True)
            m_v = re.search(r'Duration:\s*(\d+:\d+:\d+\.\d+)', r_v.stderr)
            total_dur = 96.0
            if m_v:
                p_v = m_v.group(1).split(':')
                total_dur = float(p_v[0])*3600 + float(p_v[1])*60 + float(p_v[2])

            # 3. Mix with BGM
            fade_start = max(0.0, total_dur - fade_out)
            vol_filter = f"volume={music_volume:.2f}," if music_volume != 1.0 else ""
            filter_complex = (
                f"[1:a]{vol_filter}afade=t=out:st={fade_start:.2f}:d={fade_out:.2f}[bgm];"
                f"[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"
            )

            cmd_final = [
                FFMPEG, '-y',
                '-i', concat_video,
                '-i', music_file,
                '-filter_complex', filter_complex,
                '-map', '0:v',
                '-map', '[aout]',
                '-c:v', 'copy',
                '-c:a', 'aac', '-b:a', '192k',
                '-t', f'{total_dur:.3f}',
                out_video
            ]
            subprocess.run(cmd_final, capture_output=True, check=True)

            # Clean temporary files
            try:
                for tf in os.listdir(temp_dir):
                    os.remove(os.path.join(temp_dir, tf))
            except Exception:
                pass

            resp_bytes = json.dumps({
                'ok': True,
                'message': '¡Video renderizado exitosamente con nuevos cortes!',
                'total_duration': round(total_dur, 2),
                'video_file': 'CAPITULO_2_FINAL.mp4'
            }, ensure_ascii=False).encode('utf-8')

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(resp_bytes)))
            self.end_headers()
            self.wfile.write(resp_bytes)
        except Exception as e:
            err = json.dumps({'ok': False, 'error': str(e)}).encode('utf-8')
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(err)))
            self.end_headers()
            self.wfile.write(err)

    def send_head(self):
        """Send headers for GET/HEAD, handling HTTP 206 Partial Content for video seeking."""
        if 'Range' not in self.headers:
            return super().send_head()

        re_range = self.headers.get('Range')
        path = self.translate_path(self.path)
        if not os.path.isfile(path):
            self.send_error(404, 'File not found')
            return None

        try:
            f = open(path, 'rb')
            fs = os.fstat(f.fileno())
            total = fs.st_size
            
            m = re.match(r'bytes=(\d+)-(\d*)', re_range)
            if not m:
                f.close()
                return super().send_head()

            start = int(m.group(1))
            end_val = m.group(2)
            end = int(end_val) if end_val else total - 1
            if start >= total or start > end:
                self.send_error(416, 'Requested range not satisfiable')
                f.close()
                return None

            length = end - start + 1
            self.send_response(206)
            ctype = self.guess_type(path)
            self.send_header('Content-Type', ctype)
            self.send_header('Content-Range', f'bytes {start}-{end}/{total}')
            self.send_header('Content-Length', str(length))
            self.send_header('Last-Modified', self.date_time_string(fs.st_mtime))
            self.end_headers()
            f.seek(start)
            return f
        except Exception as e:
            sys.stderr.write(f"Range error: {e}\n")
            return super().send_head()

class ThreadingHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == '__main__':
    os.chdir(DIRECTORY)
    with ThreadingHTTPServer(('127.0.0.1', PORT), VideoEditorHTTPRequestHandler) as httpd:
        print(f"CapCut FrutiNovela Editor server running at http://127.0.0.1:{PORT}")
        sys.stdout.flush()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
