import subprocess
import math
import os
from PIL import Image

# Import imageio_ffmpeg for absolute path to ffmpeg
import imageio_ffmpeg
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

def calculate_affine_matrix(out_w, out_h, view_w, view_h, center_x, center_y):
    # Left, top of the viewport in original image coords
    left = center_x - view_w / 2
    top = center_y - view_h / 2
    
    # Affine matrix
    a = view_w / out_w
    b = 0
    c = left
    d = 0
    e = view_h / out_h
    f = top
    return (a, b, c, d, e, f)

def generate_motion_video(image_path, output_path, motion_type, duration, fps=30, output_size=(1920, 1080)):
    img = Image.open(image_path).convert('RGB')
    orig_w, orig_h = img.size
    out_w, out_h = output_size
    
    scale_to_cover = max(out_w / orig_w, out_h / orig_h)
    
    total_frames = int(duration * fps)
    
    cmd = [
        FFMPEG, '-y',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-s', f'{out_w}x{out_h}',
        '-pix_fmt', 'rgb24',
        '-r', str(fps),
        '-i', '-',
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-crf', '18',
        '-pix_fmt', 'yuv420p',
        output_path
    ]
    
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    
    for i in range(total_frames):
        progress = i / max(1, (total_frames - 1))
        
        # Defaults
        scale = scale_to_cover * 1.1 # Default small zoom in to avoid edges
        center_x = orig_w / 2
        center_y = orig_h / 2
        
        if motion_type == "zoom_in":
            start_scale = scale_to_cover * 1.05
            end_scale = scale_to_cover * 1.25
            scale = start_scale + (end_scale - start_scale) * progress
            
        elif motion_type == "zoom_out":
            start_scale = scale_to_cover * 1.25
            end_scale = scale_to_cover * 1.05
            scale = start_scale + (end_scale - start_scale) * progress
            
        elif motion_type == "pan_right":
            scale = scale_to_cover * 1.15
            view_w = out_w / scale
            start_x = view_w / 2
            end_x = orig_w - view_w / 2
            center_x = start_x + (end_x - start_x) * progress
            
        elif motion_type == "pan_left":
            scale = scale_to_cover * 1.15
            view_w = out_w / scale
            start_x = orig_w - view_w / 2
            end_x = view_w / 2
            center_x = start_x + (end_x - start_x) * progress
            
        elif motion_type == "drift_up_right":
            scale = scale_to_cover * 1.15
            view_w = out_w / scale
            view_h = out_h / scale
            start_x = view_w / 2
            end_x = orig_w - view_w / 2
            start_y = orig_h - view_h / 2
            end_y = view_h / 2
            # combine scale as well
            scale = scale_to_cover * 1.1 + (scale_to_cover * 1.2 - scale_to_cover * 1.1) * progress
            view_w = out_w / scale
            view_h = out_h / scale
            center_x = start_x + (end_x - start_x) * progress
            center_y = start_y + (end_y - start_y) * progress
            
        elif motion_type == "drift_down_left":
            scale = scale_to_cover * 1.15
            view_w = out_w / scale
            view_h = out_h / scale
            start_x = orig_w - view_w / 2
            end_x = view_w / 2
            start_y = view_h / 2
            end_y = orig_h - view_h / 2
            scale = scale_to_cover * 1.2 - (scale_to_cover * 1.2 - scale_to_cover * 1.1) * progress
            view_w = out_w / scale
            view_h = out_h / scale
            center_x = start_x + (end_x - start_x) * progress
            center_y = start_y + (end_y - start_y) * progress
            
        else:
            # default to slow zoom in
            start_scale = scale_to_cover * 1.05
            end_scale = scale_to_cover * 1.20
            scale = start_scale + (end_scale - start_scale) * progress

        # Safety clamps
        view_w = out_w / scale
        view_h = out_h / scale
        center_x = max(view_w / 2, min(orig_w - view_w / 2, center_x))
        center_y = max(view_h / 2, min(orig_h - view_h / 2, center_y))
        
        matrix = calculate_affine_matrix(out_w, out_h, view_w, view_h, center_x, center_y)
        
        frame = img.transform(
            output_size, 
            Image.Transform.AFFINE, 
            matrix, 
            resample=Image.Resampling.BICUBIC
        )
        
        process.stdin.write(frame.tobytes())
        
    process.stdin.close()
    process.wait()
    return output_path

if __name__ == '__main__':
    generate_motion_video('optimized_1080p/04_astronauta_cupola.jpg', 'prueba_pan_derecha_pillow.mp4', 'pan_right', 10)
