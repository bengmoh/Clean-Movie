from tkinter import Tk, BooleanVar, filedialog
from tkinter.ttk import Label, Entry, Button, Radiobutton
from moviepy.editor import VideoFileClip, concatenate_videoclips
from ClipLogic import get_clip_intervals, get_complement_intervals
from FileLogic import get_path_and_codecs


def app(call=0) -> None:
    """
    Creates the main application window, handles user interactions, and initiates clean video generation.

    This function sets up the graphical user interface for the 'Clean Video' application,
    allowing users to select a video file after specifying clips to cut or keep. 
    Upon file selection, it calls `generate_clean_video()` to generate the clean video.

    If any errors occur during the generation of the clean video, the application restarts
    with a recursive call `app(1)`, displaying an error message to the user, and asking them to try again.

    Args:
        call (int): a flag which, if non-zero, indicates an error happened
        Defaults to 0 so that first call of the app won't have an error message.
    """
    root = Tk()
    root.title("Clean Video")
    root.geometry("500x300")
    
    to_cut = BooleanVar(value = True)
    
    clips_label = Label(root, text="Please specify the clips you want to cut/keep (e.g., \"(2:30-3:00)(1:22:30-1:23:00)\")")
    clips_entry = Entry(root)
    choices_label = Label(master=root)
    cut_choice = Radiobutton(master=choices_label, text="cut", variable=to_cut, value=True)
    keep_choice = Radiobutton(master=choices_label, text="keep", variable=to_cut, value=False)
    file_button = Button(master=root, text="Select Video", command=lambda: select_video_file())
    
    clips_label.pack()
    clips_entry.pack()
    choices_label.pack()
    cut_choice.pack()
    keep_choice.pack()
    file_button.pack()
    
    def select_video_file():
        file_path = filedialog.askopenfilename(
            initialdir=".",
            title="Select Video",
            filetypes=(("mp4 files", "*.mp4"), ("all files", "*.*"))
        )
        try:
            generate_clean_video(clips_entry.get(), file_path, to_cut.get())
        except Exception as e:
            print(e)
            root.destroy()
            app(1) # relanch the app (1 indicating an error happened)
    
    if call == 1:
        error_label = Label(root, text="An error occured. Please try again, and make sure the selected video is valid, and that clips are ordered and in a correct format")
        error_label.pack()
        # error message disappears after 5 seconds
        root.after(5000, error_label.destroy)
        
    root.mainloop()

    
def generate_clean_video(clip_intervals_input:str, file_path:str, to_cut:bool) -> None:
    """
    Processes clip intervals from user input and generates a clean video based on the given video file.
    The clean video is created by either cutting out or keeping only the specified clips.

    The clean video is saved in the same directory as the original, with "(Clean Movie)" added to the filename.
    The original video is not overwritten.

    Args:
        clip_intervals_input (str): User input defining the clip intervals to be cut or kept
        (e.g., "(0:10 0:30) (1:20:00 1:21:15)"). intervals must be ordered and in a correct format.
        
        file_path (str): The path to the video file to be processed.
        to_cut (bool): If True, the specified clip intervals are cut from the video; 
                       otherwise, only the specified clip intervals are kept.
    """
    video = VideoFileClip(file_path)    
    clip_intervals = get_clip_intervals(clip_intervals_input)

    if to_cut: 
        # cutting clip_intervals is equivalent to keeping the complement intervals
        clip_intervals = get_complement_intervals(clip_intervals, end=video.end)
    
    # generate the clips to be kept, then concatenate them
    clips = [video.subclip(*clip_interval) for clip_interval in clip_intervals]
    clean_video = concatenate_videoclips(clips)
    
    # write the clean video in the same directory as the input file, adding "(Clean Movie)"" before the extension
    output_file_path, video_codec, audio_codec = get_path_and_codecs(file_path)
    try:
        clean_video.write_videofile(output_file_path, codec=video_codec, audio_codec=audio_codec)
    except Exception as e:
        if video_codec in str(e).lower():
            print(f"Error: {e}.\nFailed to write file with video codec: {video_codec}")
        elif audio_codec in str(e).lower():
            print(f"Error: {e}.\nFailed to write file with audio codec: {audio_codec}")
        else:
            print(f"An unexpected error occurred: {e}")
    finally:
        video.close()  # Ensure the video file is closed even if an error occurs


if __name__ == "__main__":
    # First call of the app
    app()
