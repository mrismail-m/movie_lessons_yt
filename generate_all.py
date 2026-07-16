import json
import re
import os
from generate_video import generate_video

def main():
    if not os.path.exists("lessons.json"):
        print("lessons.json not found!")
        return
        
    with open("lessons.json", "r", encoding="utf-8") as f:
        lessons = json.load(f)
        
    os.makedirs("output_videos", exist_ok=True)
        
    for lesson_data in lessons:
        movie = lesson_data["movie"]
        lesson = lesson_data["lesson"]
        
        # Create safe filename: replace spaces with hyphens, remove non-alphanumeric (except hyphens)
        safe_name = re.sub(r'[^a-zA-Z0-9-]', '', movie.replace(' ', '-'))
        # Consolidate multiple consecutive hyphens
        safe_name = re.sub(r'-+', '-', safe_name).strip('-')
        
        output_filename = os.path.join("output_videos", f"{safe_name}.mp4")
        
        print(f"Generating video for: {movie} -> {output_filename}")
        try:
            generate_video(lesson, movie, output_filename)
        except Exception as e:
            print(f"Failed to generate {output_filename}: {e}")
            
    print("All videos generated successfully!")

if __name__ == "__main__":
    main()
