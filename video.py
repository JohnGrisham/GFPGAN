import cv2
import subprocess
import os
import sys

cwd = os.getcwd()
data_folder = os.path.join(cwd, 'data')
upload_folder = os.path.join(data_folder, 'upload')
result_folder = os.path.join(data_folder, 'results')
video_folder =  os.path.join(data_folder, 'videos')
video_result_folder = os.path.join(data_folder, 'results_videos')
video_mp4_result_folder = os.path.join(data_folder, 'results_mp4_videos')


cmp_folder = os.path.join(result_folder, "cmp")
cropped_faces_folder = os.path.join(result_folder, "cropped_faces")
restored_faces_folder = os.path.join(result_folder, "restored_faces")
restored_imgs_folder = os.path.join(result_folder, "restored_imgs")


# assign directory
directory = video_folder #PATH_WITH_INPUT_VIDEOS
zee = 0

# init
fps = 60.0
upscale = 2

#deletes frames from previous video
for f in os.listdir(upload_folder):
    os.remove(os.path.join(upload_folder, f))

#deletes upscaled frames from previous video
for f in os.listdir(restored_imgs_folder):
   os.remove(os.path.join(restored_imgs_folder, f))

#clearing previous .avi files
for f in os.listdir(video_result_folder):
    os.remove(os.path.join(video_result_folder, f))

#clearing .mp4 result files
for f in os.listdir(video_mp4_result_folder):
    os.remove(os.path.join(video_mp4_result_folder, f))

for f in os.listdir(cmp_folder):
    os.remove(os.path.join(cmp_folder, f))

for f in os.listdir(cropped_faces_folder):
    os.remove(os.path.join(cropped_faces_folder, f))

for f in os.listdir(restored_faces_folder):
    os.remove(os.path.join(restored_faces_folder, f))

for f in os.listdir(restored_imgs_folder):
    os.remove(os.path.join(restored_imgs_folder, f))




def convert_frames_to_video(pathIn, pathOut, fps):
    files = [f for f in os.listdir(pathIn) if os.path.isfile(os.path.join(pathIn, f))]
    # for sorting the file names properly
    files.sort(key=lambda x: int(x[5:-4]))

    frame_size = None
    out = None

    for filename in files:
        print(filename)
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
    print("start handle_video")
    if not os.path.exists(upload_folder):
        print("can not find folder: ", upload_folder)
        return

    zee = 0

    for filename in os.listdir(directory):

        original = os.path.join(directory, filename)
        # checking if it is a file
        if os.path.isfile(original):


            print("PROCESSING :"+str(original)+"\n")
            # Read the video from specified path

            #video to frames
            cam = cv2.VideoCapture(str(original))
            fps = cam.get(cv2.CAP_PROP_FPS)

            if not os.path.exists(upload_folder):
                print("can not find folder: ", upload_folder)
                return

            # frame
            currentframe = 0

            #clear all folders


            #deletes upscaled frames from previous video
            #for f in os.listdir(result_folder):
            #  os.remove(os.path.join(result_folder, f))




            while(True):

                # reading from frame
                ret,frame = cam.read()

                if ret:
                    # if video is still left continue creating images
                    name = os.path.join(upload_folder, 'frame' + str(currentframe) + '.jpg')

                    # writing the extracted images
                    cv2.imwrite(name, frame)


                        # increasing counter so that it will
                        # show how many frames are created
                    currentframe += 1
                    # print(currentframe)
                else:
                    #deletes all the videos you uploaded for upscaling
                    #for f in os.listdir(video_folder):
                    #  os.remove(os.path.join(video_folder, f))

                    break

                # Release all space and windows once done
            cam.release()
            cv2.destroyAllWindows()

            #apply super-resolution on all frames of a video
            #scale factor is by 3.5x

            #in the line below '2' stands for upscaling by factor of 2
            print("run inference_gfpgan.py")
            command = f"python inference_gfpgan.py -i {upload_folder} -o {result_folder} -v 1.4 -s {upscale} --bg_upsampler realesrgan"
            cmd = os.popen(command)
            show = cmd.read()
            print(show)

            #after upscaling just delete the source frames
            for f in os.listdir(upload_folder):
                os.remove(os.path.join(upload_folder, f))

            '''
            #rename all frames in "results" to remove the 'out' substring from the processing results
            paths = (os.path.join(root, filename)
                    for root, _, filenames in os.walk('/content/GFPGAN/results')
                    for filename in filenames)
            for path in paths:
                newname = path.replace('_out', '')
                if newname != path:
                    os.rename(path, newname)
            '''

            #convert super res frames to .avi
            pathIn = restored_imgs_folder

            zee = zee+1
            fName = "video"+str(zee)
            filenameVid = f"{fName}.avi"

            pathOut = os.path.join(video_result_folder, filenameVid)

            convert_frames_to_video(pathIn, pathOut, fps)

            #after processing frames converted to .avi video , delete upscaled frames from previous video
            for f in os.listdir(pathIn):
                os.remove(os.path.join(pathIn, f))

            #convert .avi to .mp4
            src = video_result_folder
            dst = video_mp4_result_folder

            print("walking")
            for root, dirs, filenames in os.walk(src, topdown=False):
                for filename in filenames:
                    try:
                        _format = os.path.splitext(filename)[1].lower()
                        if _format in [".flv", ".mp4", ".avi", ".mov"]:
                            inputfile = os.path.join(root, filename)
                            outputfile = os.path.join(dst, filename.lower().replace(_format, ".mp4"))

                            #Add audio from original video to the output video
                            print("Restoring audio for file", original)
                            merge_video_audio(inputfile, original, outputfile)
                    except IOError as err:
                        print(err)
                        return




            #clearing previous .avi files
            for f in os.listdir(video_result_folder):
                os.remove(os.path.join(video_result_folder, f))

            #deletes frames from previous video
            #for f in os.listdir(upload_folder):
            #  os.remove(os.path.join(upload_folder, f))


    print("end handle_video")
    sys.exit()

      # if it is out of memory, try to use the `--tile` option
# We upsample the image with the scale factor X3.5

# Arguments
# -n, --model_name: Model names
# -i, --input: input folder or image
# --outscale: Output scale, can be arbitrary scale factore.

#deletes frames from previous video
# for f in os.listdir(upload_folder):
#     os.remove(os.path.join(upload_folder, f))

#deletes upscaled frames from previous video
# for f in os.listdir(restored_imgs_folder):
#     os.remove(os.path.join(restored_imgs_folder, f))

#deletes all the videos you uploaded for upscaling
# for f in os.listdir(video_folder):
#     os.remove(os.path.join(video_folder, f))

#clearing previous .avi files
# for f in os.listdir(video_result_folder):
#     os.remove(os.path.join(video_result_folder, f))

#clearing .mp4 result files
# for f in os.listdir(video_mp4_result_folder):
#     os.remove(os.path.join(video_mp4_result_folder, f))



handle_video()