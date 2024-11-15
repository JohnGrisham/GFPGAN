import cv2
import subprocess
import os
import sys

# Paths configuration
cwd = os.getcwd()
data_folder = os.path.join(cwd, 'data')
result_folder = os.path.join(data_folder, 'results')
video_result_folder = os.path.join(data_folder, 'results_videos')
video_mp4_result_folder = os.path.join(data_folder, 'results_mp4_videos')
restored_imgs_folder = os.path.join(result_folder, "restored_imgs")
original_video_folder = os.path.join(data_folder, 'videos')

# Video settings
fps = 60.0  # Frames per second
zee = 0     # Video counter

def convert_frames_to_video(pathIn, pathOut, fps):
    # Sort files by frame number to keep the order correct
    files = [f for f in os.listdir(pathIn) if os.path.isfile(os.path.join(pathIn, f))]
    files.sort(key=lambda x: int(x[5:-4]))  # Sort assuming filenames start with "frame<number>.jpg"

    frame_size = None
    out = None

    for filename in files:
        filepath = os.path.join(pathIn, filename)
        img = cv2.imread(filepath)
        if img is not None:
            if frame_size is None:
                frame_size = (img.shape[1], img.shape[0])
                out = cv2.VideoWriter(pathOut, cv2.VideoWriter_fourcc(*'DIVX'), fps, frame_size)
            out.write(img)

    if out is not None:
        out.release()

def merge_video_audio(video_path, audio_path, output_path):
    # Define the ffmpeg command
    command = [
        "ffmpeg",
        "-r", str(fps),        # Specify frame rate
        "-i", video_path,      # Input video
        "-i", audio_path,      # Input audio
        "-c:v", "copy",        # Copy video codec
        "-c:a", "copy",        # Copy audio codec
        "-map", "0:v",         # Map video from input 0 (video)
        "-map", "1:a",         # Map audio from input 1 (audio)
        output_path            # Output path
    ]

    # Execute the command
    subprocess.call(command)

def handle_video():
    print("Start combining images into video")

    # Process each set of restored images
    fName = "video.avi"
    pathOut = os.path.join(video_result_folder, fName)
    original_video_path = os.path.join(original_video_folder, "My Movie.mp4")
    cam = cv2.VideoCapture(str(original_video_path))
    fps = cam.get(cv2.CAP_PROP_FPS)

    # Convert images to video
    convert_frames_to_video(restored_imgs_folder, pathOut, fps)

    # Convert .avi to .mp4 and add audio (if needed)
    outputfile = os.path.join(video_mp4_result_folder, fName.replace(".avi", ".mp4"))
    # Assuming an audio path is available (replace 'original_video_path' as needed)
    merge_video_audio(pathOut, original_video_path, outputfile)

    #Cleanup after video creation is complete
    # for folder in [video_result_folder, restored_imgs_folder]:
    #     for f in os.listdir(folder):
    #         os.remove(os.path.join(folder, f))

    print("Finished combining images into video")
    sys.exit()

handle_video()
