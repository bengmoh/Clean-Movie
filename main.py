from moviepy.editor import VideoFileClip, concatenate_videoclips
import re 
import subprocess
from tkinter import Tk, filedialog


def main() -> None:
    root = Tk()
    root.withdraw()
    input_file_path = filedialog.askopenfilename(initialdir=".", title="select the movie", filetypes=(("all files", "*.*"), ("mp4 files", "*.mp4")))
    vid = VideoFileClip(input_file_path)
    bad_clips_input = input(
        "Enter the list of clips you want to remove. \
        \nFor example: if you enter [(1:15, 2:00), (1:30:22, 1:31:24)], then\
        \nI'll remove clips (1:15 to 2:00) and (1:30:22 to 1:31:24). Please\
        \nenter the clips in order and in a correct format as shown in the example:\n"
        )
    bad_clips = get_clip_list(bad_clips_input)
    
    good_clips = cutout(bad_clips, vid)
    new_video = concatenate_videoclips(good_clips)
    
    output_file_path = input_file_path[:len(input_file_path)-4] + " (CleanMovie)"  + input_file_path[len(input_file_path)-4:]
    new_video.write_videofile(output_file_path, codec="libx264", audio_codec="aac")
    # if automatically_openp
    #   python subprocess that opens the vid
    vid.close()
# [(0:33, 0:40), (8:41, 9:46)]

def get_clip_list(clip_str: str) -> list[tuple[int, int]]:
    """returns list of intervals in seconds given a string list
    of clips in any time format"""
    def to_seconds(time: str) -> int:
        """converts time from string format to seconds (int)"""
        column_count = time.count(":")
        if not column_count:
            # handle float input or not?
            return int(float(time)) if time < "60" else ValueError("seconds must be 60 or less")
        if column_count == 1:
            time_parts = time.split(":")
            return int(time_parts[0]) * 60 + int(float(time_parts[1]))
        if column_count == 2:
            time_parts = time.split(":")
            return int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(float(time_parts[2]))
        raise ValueError(f"Inapropriate time {time}")
    
    clip_list = []
    time_pattern = "\d{1,2}|\d{1,2}:\d{1,2}|\d{1,2}:\d{1,2}:\d{1,2}"
    interval_list = re.findall(rf"\(({time_pattern}) ?,? ?({time_pattern})\)", clip_str)
    for interval in interval_list:
        start, end = to_seconds(interval[0]), to_seconds(interval[1])
        # handle end < start or not?
        clip_list.append((start, end))
    return clip_list

    
def cutout(bad_clips_intervals: list[tuple[int, int]], vid):    
    good_clips_intervals = complement(bad_clips_intervals, vid.end)
    good_clips = []
    for good_clip_interval in good_clips_intervals:
        start, end = good_clip_interval
        good_clips.append(vid.subclip(start, end))
    return good_clips


def complement(bad_clips_intervals: list[tuple[int, int]], vid_end: int):
    """takes vid end time and list of bad clips
    returns all clips of vid cutting out bad clips"""
    assert bad_clips_intervals, "there must be at least one clip to remove"
    good_clip_intervals = [(0, bad_clips_intervals[0][0])] if bad_clips_intervals[0][0] != 0 else []
    for i in range(len(bad_clips_intervals) - 1):
        good_clip_start = bad_clips_intervals[i][1]
        good_clip_end = bad_clips_intervals[i + 1][0]
        good_clip_intervals.append((good_clip_start, good_clip_end))        
    if bad_clips_intervals[-1][1] != vid_end:
        good_clip_intervals.append((bad_clips_intervals[-1][1], vid_end))
    return good_clip_intervals
    
# Needs fixes to be used
def get_audio_codec(file_path: str):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_streams", file_path], capture_output=True, text=True)
    original_audio_codec = re.search(r"codec_name=([^,]+)", result.stdout).group(1)

    # Set the output audio codec to match the original
    if original_audio_codec == "aac":
        return "aac"
    elif original_audio_codec == "mp3":
        return "libmp3lame"  # or "mp3"
    else:
        return original_audio_codec  # Use the same codec
    
if __name__ == "__main__":
    main()