import subprocess
import math
from PIL import Image
import sys

def generate_smooth_video(image_path, output_path, duration=10, fps=30, output_size=(1920, 1080)):
    print(f"Loading {image_path}...")
    img = Image.open(image_path).convert('RGB')
    orig_w, orig_h = img.size
    
    out_w, out_h = output_size
    
    # Calculate scale to cover output
    scale_to_cover = max(out_w / orig_w, out_h / orig_h)
    
    # We want a slow zoom in, let's say 1.1x to 1.3x of scale_to_cover
    start_scale = scale_to_cover * 1.05
    end_scale = scale_to_cover * 1.35
    
    total_frames = int(duration * fps)
    
    import imageio_ffmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    cmd = [
        ffmpeg_exe,
        '-y',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-s', f'{out_w}x{out_h}',
        '-pix_fmt', 'rgb24',
        '-r', str(fps),
        '-i', '-',
        '-c:v', 'libx264',
        '-preset', 'slow',
        '-crf', '18',
        '-pix_fmt', 'yuv420p',
        output_path
    ]
    
    print(f"Starting ffmpeg to write {output_path}...")
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    
    for i in range(total_frames):
        progress = i / max(1, (total_frames - 1))
        current_scale = start_scale + (end_scale - start_scale) * progress
        
        view_w = out_w / current_scale
        view_h = out_h / current_scale
        
        x_center = orig_w / 2
        y_center = orig_h / 2
        
        left = x_center - view_w / 2
        top = y_center - view_h / 2
        
        # Affine matrix:
        # We are mapping output pixels (x, y) to input pixels (x', y')
        # x' = a*x + b*y + c
        # y' = d*x + e*y + f
        a = view_w / out_w
        b = 0
        c = left
        d = 0
        e = view_h / out_h
        f = top
        
        matrix = (a, b, c, d, e, f)
        
        frame = img.transform(
            output_size, 
            Image.Transform.AFFINE, 
            matrix, 
            resample=Image.Resampling.BICUBIC
        )
        
        process.stdin.write(frame.tobytes())
        
        if i % 30 == 0:
            print(f"Rendered {i}/{total_frames} frames ({(i/total_frames)*100:.1f}%)")
            
    process.stdin.close()
    process.wait()
    print(f"Finished {output_path}")

if __name__ == '__main__':
    generate_smooth_video('optimized_1080p/04_astronauta_cupola.jpg', 'prueba_subpixel_pillow.mp4', duration=10, fps=30)
