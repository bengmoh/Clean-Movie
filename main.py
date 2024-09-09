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

    bad = True 
    clips_input = input(
        "Enter the list of clips you want to remove:\
        \n -> "
        )
    
    # Handling code vs normal input
    if any(char.isalpha() for char in clips_input):
        clips_input = decode(clips_input)
        bad = False
        
    clips_intervals = get_clips_intervals(clips_input)
    if bad: # complement to get the actual clips
        clips_intervals = complement(clips_intervals, vid.end)
    
    # generate the clips to keep and concatenate them to write the clean video
    clips = get_clips(clips_intervals, vid)    
    new_video = concatenate_videoclips(clips)
    
    # handle short file names
    output_file_path = input_file_path[:len(input_file_path)-4] + " (CleanMovie)"  + input_file_path[len(input_file_path)-4:]
    new_video.write_videofile(output_file_path, codec="libx264", audio_codec="aac")
    vid.close()    
    # if automatically_openp
    #   python subprocess that opens the vid

def get_clips_intervals(clip_str: str) -> list[tuple[int, int]]:
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
        assert start <= end, f"start {start} must be less than or equal to end {end}"
        clip_list.append((start, end))
    return clip_list

    
def get_clips(clips_intervals: list[tuple[int, int]], vid):
    """
    takes list of good clips intervals,
    returns the list of the good clips
    """
    clips = []
    for clip_interval in clips_intervals:
        clips.append(vid.subclip(*clip_interval))
    return clips


def complement(clips_intervals: list[tuple[int, int]], end: int):
    """
    takes vid end time and list of clips' intervals
    returns the complement clips intevals'
    """
    assert clips_intervals, "there must be at least one clip to remove"
    comp_clip_intervals = [(0, clips_intervals[0][0])] if clips_intervals[0][0] != 0 else []
    for i in range(len(clips_intervals) - 1):
        comp_clip_start = clips_intervals[i][1]
        comp_clip_end = clips_intervals[i + 1][0]
        comp_clip_intervals.append((comp_clip_start, comp_clip_end))        
    if clips_intervals[-1][1] != end:
        comp_clip_intervals.append((clips_intervals[-1][1], end))
    return comp_clip_intervals
    
if __name__ == "__main__":
    main()
