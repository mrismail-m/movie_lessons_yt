import os
import sys
from datetime import datetime, timezone, timedelta
from select_next import get_next_lessons, mark_lesson_posted
from generate_video import generate_video
from upload_youtube import upload_video

def get_publish_times(count):
    """
    Computes today's publish slots based on PKT (UTC+5).
    Since cron runs at 03:00 AM PKT, 'today' in PKT is now.
    Converts 08:00, 11:00, 14:00, 17:00, 20:00, 22:30 PKT into UTC ISO 8601 strings.
    """
    pkt_offset = timezone(timedelta(hours=5))
    now_pkt = datetime.now(pkt_offset)
    
    slots_str = ["08:00", "11:00", "14:00", "17:00", "20:00", "22:30"]
    times = []
    
    for slot in slots_str[:count]:
        hour, minute = map(int, slot.split(':'))
        # Create a datetime for today at the slot time, then localize to PKT
        dt_pkt = now_pkt.replace(hour=hour, minute=minute, second=0, microsecond=0)
        # Convert to UTC ISO 8601 string expected by YouTube API
        dt_utc = dt_pkt.astimezone(timezone.utc)
        times.append(dt_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z"))
        
    return times

def main():
    print("Starting automated YouTube Shorts pipeline (Batch of 6)...")
    
    # 1. Get next up to 6 lessons
    unposted_lessons = get_next_lessons(count=6, json_path="lessons.json")
    if not unposted_lessons:
        print("No unposted lessons found. Exiting gracefully.")
        sys.exit(0)
        
    print(f"Found {len(unposted_lessons)} lessons to process.")
    
    font_path = "font.ttf"
    if not os.path.exists(font_path):
        print(f"ERROR: {font_path} not found. Ensure font.ttf exists in the repository root.")
        sys.exit(1)
        
    # Pre-calculate the publish times for this batch
    publish_times = get_publish_times(len(unposted_lessons))
    
    for i, (index, lesson_data) in enumerate(unposted_lessons):
        movie = lesson_data["movie"]
        lesson = lesson_data["lesson"]
        
        # Prefer the customized JSON fields, fallback if missing
        title = lesson_data.get("title", f"The Lesson in {movie} #shorts")
        description = lesson_data.get("description", f"{lesson}\n\nMovie: {movie}\n\n#movies #shorts")
        category_id = lesson_data.get("categoryId", "24")
        
        publish_at = publish_times[i]
        
        print(f"\n======================================")
        print(f"Processing [{i+1}/{len(unposted_lessons)}]: {movie}")
        print(f"Target Publish Time (UTC): {publish_at}")
        print(f"======================================")
        
        video_path = f"temp_short_{index}.mp4"
        
        # 2. Generate Video
        print("Generating video via FFmpeg...")
        try:
            generate_video(lesson, movie, video_path, font_path=font_path)
        except Exception as e:
            print(f"Failed to generate video for {movie}. Skipping this entry.")
            continue
            
        # 3. Upload to YouTube
        try:
            video_id = upload_video(
                video_path=video_path,
                title=title,
                description=description,
                category_id=category_id,
                privacy_status="private",
                publish_at=publish_at
            )
        except Exception as e:
            print(f"YouTube upload failed for {movie}: {e}")
            if os.path.exists(video_path):
                os.remove(video_path)
            continue
            
        # 4. Success -> Mark as posted & update JSON
        mark_lesson_posted(index, video_id, publish_at, "lessons.json")
        print(f"Lesson '{movie}' successfully marked as posted and JSON updated.")
        
        # Cleanup
        if os.path.exists(video_path):
            os.remove(video_path)
            
    print("\nBatch workflow complete!")

if __name__ == "__main__":
    main()
