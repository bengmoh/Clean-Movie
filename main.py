from moviepy.editor import VideoFileClip, concatenate_videoclips
import re 
import subprocess
from tkinter import Tk, filedialog
from safe import decode


def main() -> None:
    root = Tk()
    root.withdraw() # build the ui don't hide it
    input_file_path = filedialog.askopenfilename(initialdir=".", title="select the movie", filetypes=(("all files", "*.*"), ("mp4 files", "*.mp4")))
    vid = VideoFileClip(input_file_path)

    bad_clips_input = input(
        "Enter the list of clips you want to remove, or the special code:\
        \n -> "
        )
    
    # Handling code vs normal input
    if any(char.isalpha() for char in bad_clips_input):
        bad_clips_input = decode(bad_clips_input)
        
    bad_clips = get_clip_list(bad_clips_input)
    good_clips = cutout(bad_clips, vid)
        
    new_video = concatenate_videoclips(good_clips)
    
    output_file_path = input_file_path[:len(input_file_path)-4] + " (CleanMovie)"  + input_file_path[len(input_file_path)-4:]
    new_video.write_videofile(output_file_path, codec="libx264", audio_codec="aac")
    vid.close()    
    # if automatically_openp
    #   python subprocess that opens the vid

def get_clip_list(clip_str: str) -> list[tuple[int, int]]:
    """
    returns list of clips (start[int], end[int]) in seconds given a string
    of clips, each clip as (start, end).
    This is to convert user input to actual list of clips
    Example:
    "(0:50, 1:0) (1:20, 2:03)" -> [(50, 60), (80, 123)]
    """
    
    def to_seconds(time: str) -> int:
        """converts time from string format to seconds (int)"""
        column_count = time.count(":")
        if not column_count:
            # handle float input or not?
            return int(float(time))
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
    """
    takes list of bad clips intervals,
    returns the list of the good clips
    """
    good_clips_intervals = complement(bad_clips_intervals, vid.end)
    good_clips = []
    for good_clip_interval in good_clips_intervals:
        start, end = good_clip_interval
        good_clips.append(vid.subclip(start, end))
    return good_clips


def complement(bad_clips_intervals: list[tuple[int, int]], vid_end: int):
    """
    takes vid end time and list of bad clips intervals
    returns the good clips intevals by complementing the bad ones'
    """
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
