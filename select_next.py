import json
import os

def get_next_lessons(count=6, json_path="lessons.json"):
    """Reads the JSON and finds the first `count` lessons where posted=False."""
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"{json_path} not found")
        
    with open(json_path, "r", encoding="utf-8") as f:
        lessons = json.load(f)
        
    results = []
    for index, lesson in enumerate(lessons):
        if not lesson.get("posted", False):
            results.append((index, lesson))
            if len(results) == count:
                break
                
    return results

def mark_lesson_posted(index, video_id, publish_at, json_path="lessons.json"):
    """Updates the lesson entry to posted=True and saves the video_id."""
    with open(json_path, "r", encoding="utf-8") as f:
        lessons = json.load(f)
        
    lessons[index]["posted"] = True
    lessons[index]["privacyStatus"] = "private"
    if video_id:
        lessons[index]["video_id"] = video_id
    if publish_at:
        lessons[index]["publishAt"] = publish_at
        
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(lessons, f, indent=2, ensure_ascii=False)
