import os
import filetype

VIDEO_CODECS = {
    "mp4": "libx264",        
    "webm": "libvpx",    
    "ogv": "libtheora",
    "ogg": "libtheora",      
    "avi": "mpeg4",          
    "mov": "h264",           
    "mkv": "libx264",       
    "flv": "flv1",           
    "wmv": "wmv2"            
}

AUDIO_CODECS = {
    "mp4": "aac",
    "webm": "libvorbis",
    "ogv": "libvorbis",
    "ogg": "libvorbis",
    "avi": "mp3",        
    "mov": "aac",
    "mkv": "aac",
    "flv": "mp3",
    "wmv": "wma"          
}

DEFAULT_STRING = "(Clean Movie)"
DEFAULT_EXTENSION = ".mp4"

def get_path_and_codecs(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    directory, filename = os.path.split(file_path)
    filename_base, extension = os.path.splitext(filename)

    if not extension:
        try:
            kind = filetype.guess(file_path)
            if kind:
                extension = '.' + kind.extension 
        except Exception as e:
            print(f"Error guessing file type: {e}")
            extension = DEFAULT_EXTENSION

    new_path = os.path.join(directory, filename_base + DEFAULT_STRING + extension)

    try:
        extension = extension[1:].lower() 
        video_codec = VIDEO_CODECS[extension]
        audio_codec = AUDIO_CODECS[extension]
    except KeyError:
        raise ValueError(f"{extension} files not supported. Supported extensions are \
                         \nVideo: {[key for key in VIDEO_CODECS]} \
                         \nAudio: {[key for key in AUDIO_CODECS]}")

    return new_path, video_codec, audio_codec