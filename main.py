from moviepy.editor import VideoFileClip, concatenate_videoclips
import re 
import subprocess
from tkinter import Tk, filedialog
from safe import decode


def main() -> None:
    root = Tk()
    root.withdraw()
    input_file_path = filedialog.askopenfilename(initialdir=".", title="select the movie", filetypes=(("all files", "*.*"), ("mp4 files", "*.mp4")))
    vid = VideoFileClip(input_file_path)

    remove = True 
    clip_input = input(
        "Enter the list of clips you want to remove:\
        \n -> "
        )
    
    # Handling special code, only for clips to be kept
    if any(char.isalpha() for char in clip_input):
        clip_input = decode(clip_input)
        remove = False
        
    clip_intervals = get_clip_intervals(clip_input)
    if remove: # complement to get the actual clips
        clip_intervals = complement(clip_intervals, vid.end)
    
    # generate the clips to keep and concatenate them to write the clean video
    clips = get_clips(clip_intervals, vid)    
    new_video = concatenate_videoclips(clips)
    
    output_file_path = input_file_path[:len(input_file_path)-4] + " (CleanMovie)"  + input_file_path[len(input_file_path)-4:]
    new_video.write_videofile(output_file_path, codec="libx264", audio_codec="aac")
    vid.close()    

def get_clip_intervals(clip_str: str) -> list[tuple[int, int]]:
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
        assert start <= end, f"start {start} must be less than or equal to end {end}"
        clip_list.append((start, end))
    return clip_list

    
def get_clips(clip_intervals: list[tuple[int, int]], vid):
    """
    returns the list of clips given the clips' intervals
    """
    clips = []
    for clip_interval in clip_intervals:
        clips.append(vid.subclip(*clip_interval))
    return clips


def complement(clip_intervals: list[tuple[int, int]], end: int):
    """
    takes vid end time and list of clips' intervals
    returns the complement clips' intevals
    """
    assert clip_intervals, "there must be at least one clip to remove"
    
    comp_clip_intervals = [(0, clip_intervals[0][0])] if clip_intervals[0][0] != 0 else []
    
    for i in range(len(clip_intervals) - 1):
        comp_clip_start = clip_intervals[i][1]
        comp_clip_end = clip_intervals[i + 1][0]
        comp_clip_intervals.append((comp_clip_start, comp_clip_end))    
        
    if clip_intervals[-1][1] != end:
        comp_clip_intervals.append((clip_intervals[-1][1], end))
        
    return comp_clip_intervals
    
if __name__ == "__main__":
    main()
