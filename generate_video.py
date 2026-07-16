import textwrap
import subprocess
import tempfile
import os
import random

def generate_video(lesson_text, movie_title, output_path, font_path="font.ttf"):
    # 1. Determine font size and wrap width dynamically (reduced size)
    base_fontsize = 44
    wrap_width = 38
    
    # Auto-size down if text is too long
    if len(lesson_text) > 150:
        base_fontsize = 38
        wrap_width = 44
    if len(lesson_text) > 200:
        base_fontsize = 32
        wrap_width = 52
        
    lines = textwrap.wrap(lesson_text, width=wrap_width)
    line_height = base_fontsize * 1.3
    
    # 2. Calculate starting Y to center the block of text vertically, then shift upward
    total_text_height = len(lines) * line_height
    start_y = ((1920 - total_text_height) / 2) - 200
    
    # Left and Right padding
    margin_x = 120

    # We will build a filter_script file to avoid shell quoting madness
    # We will also use 'textfile' to bypass FFMPEG's complex text escaping completely.
    with tempfile.TemporaryDirectory() as temp_dir:
        filters = []
        
        # 3. Draw each line of the lesson text (Aligned Left)
        for i, line in enumerate(lines):
            line_file = os.path.join(temp_dir, f"line_{i}.txt")
            with open(line_file, "w", encoding="utf-8") as f:
                f.write(line)
                
            y_pos = start_y + (i * line_height)
            
            # FFMPEG requires escaping colons and backslashes in file paths inside the filtergraph.
            escaped_path = line_file.replace("\\", "\\\\").replace(":", "\\:")
            
            # Left align using fixed margin
            filters.append(
                f"drawtext=fontfile='font_medium.ttf':textfile='{escaped_path}':fontcolor='#e0e0e0':fontsize={base_fontsize}:x={margin_x}:y={y_pos}"
            )
            
        # 4. Draw movie title with a delay (Aligned Right)
        movie_file = os.path.join(temp_dir, "movie.txt")
        with open(movie_file, "w", encoding="utf-8") as f:
            f.write(f"— {movie_title}")
            
        movie_y = 1920 * 0.62 # Position a bit higher

        escaped_movie_path = movie_file.replace("\\", "\\\\").replace(":", "\\:")
        
        # Right align using screen width minus text width and margin
        # enable='gte(t,0.5)' delays the text appearance by 0.5s
        filters.append(
            f"drawtext=fontfile='{font_path}':textfile='{escaped_movie_path}':fontcolor=gray:fontsize=32:x='w-text_w-{margin_x}':y={movie_y}:enable='gte(t,0.5)'"
        )
        
        # Note: Fades have been intentionally removed per your request!
        
        filter_graph = ",".join(filters)
        
        # Write the complex filter graph to a temporary file
        filter_script_path = os.path.join(temp_dir, "filter.txt")
        with open(filter_script_path, "w", encoding="utf-8") as f:
            f.write(filter_graph)
            
        bg_audio = random.choice(["audio2.mp3", "piano.mp3"])
        
        cmd = [
            "ffmpeg",
            "-y",
            "-f", "lavfi",
            "-i", "color=c=#0a0a0a:s=1080x1920:d=2", # Dark background, 1080x1920, 2 seconds
            "-i", bg_audio,
            "-filter_script:v", filter_script_path,
            "-c:v", "libx264",
            "-preset", "fast",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-shortest",
            output_path
        ]
        
        try:
            print(f"Running FFMPEG with textfile approach to avoid escaping issues...")
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(f"Video successfully generated at {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"FFMPEG Render Failed!\nSTDERR:\n{e.stderr}")
            raise

if __name__ == "__main__":
    # Test generation with a sample
    generate_video(
        "Hope isn't naive; it's the one thing that survives when everything else is stripped from you.",
        "The Shawshank Redemption",
        "test_output.mp4"
    )
