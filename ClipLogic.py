import re

TIME_PATTERN = "\d{1,2}|\d{1,2}:\d{1,2}|\d{1,2}:\d{1,2}:\d{1,2}"

def get_clip_intervals(clip_intervals_str: str) -> list[tuple[int, int]]:
    """returns list of clip intervals in seconds, given their string representation.
    each interval in the string must be of format "(start end)" where "start" and "end" are valid times
    of format "hh:mm:ss", "mm:ss", or "ss" ("h:m:s", "m:s", and "s" are also valid).
    "start" and "end" can be seperated by a white space, a comma, or a hyphen.
    "end" must be strictly bigger than "start".
    
    anything outside the intervals is ignored.
    
    Examples:
    "this (1:30, 2:30) then (1:03:30, 1:04:30)" -> [(90, 150), (3810, 3870)]
    "(0 1:0:1)--(1:1:23 1:1:59)" -> [(0, 3601), (3683, 3719)]
    "(1:20-2:0)(3:0 - 3:30)" -> [(80, 120), (180, 210)]

    Args:
        clip_intervals_str (str): the string representing the clip intervals
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
    
    clip_intervals = []
    regex_intervals = re.findall(rf"\(({TIME_PATTERN}) ?,?-? ?({TIME_PATTERN})\)", clip_intervals_str)
    for interval in regex_intervals:
        start, end = to_seconds(interval[0]), to_seconds(interval[1])
        assert start <= end, f"start {start} must be less than end {end}"
        clip_intervals.append((start, end))
    return clip_intervals


def get_complement_intervals(clip_intervals: list[tuple[int, int]], end: int):
    """
    returns the complement intervals of the given clip intevals
    "end" determines the end of the last interval in the complement
    intervals (normally it's the end of the video)
    """
    if not clip_intervals:
        return [(0, end)]
    
    comp_intervals = [(0, clip_intervals[0][0])] if clip_intervals[0][0] != 0 else []
    
    for i in range(len(clip_intervals) - 1):
        comp_clip_start = clip_intervals[i][1] # starts when the previous clips ends
        comp_clip_end = clip_intervals[i + 1][0] # ends when the next clip starts
        comp_intervals.append((comp_clip_start, comp_clip_end))    
        
    if clip_intervals[-1][1] != end:
        comp_intervals.append((clip_intervals[-1][1], end))
        
    return comp_intervals    
    