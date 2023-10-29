import os
import subprocess
import os
import concurrent.futures

num_cores = os.cpu_count()
print(f"Number of CPU cores: {num_cores}")
audioFiles = []
videoFiles = []
currentConvertingIndex = 0
conversionIndexOffset = 0

# Function to convert video and audio files using FFmpeg
def convertVideo(video_file_path, audio_file_path, output_path):
    # Write results to log file
    with open(r"C:\Users\marke\OneDrive\Documents\hvx_converted_videos\2023-10-28\logger.txt", 'a') as log_file:
        try:
            # Construct FFmpeg command using provided template
            # ORIGINAL ffmpeg_command = f'ffmpeg -i "{video_file_path}" -i "{audio_file_path}" -c:v copy -c:a copy -shortest -c:v libx264 -profile:v main -pix_fmt yuv420p -crf 0 -preset slow -c:a aac -b:a 160k -movflags +faststart "{output_path}"'
            ffmpeg_command = f'ffmpeg -i "{video_file_path}" -i "{audio_file_path}" ' \
                    f'-c:v libx264 -profile:v main -pix_fmt yuv420p -crf 1 -preset slow ' \
                    f'-c:a aac -b:a 160k -movflags +faststart -r 60 "{output_path}"'

            # ffmpeg_command = f'ffmpeg -i "{video_file_path}" -i "{audio_file_path}" ' \
            #                  f'-c:v libx264 -profile:v high -pix_fmt yuv420p -crf 1 -preset slow ' \
            #                  f'-c:a aac -b:a 160k -movflags +faststart "{output_path}"'
            # WORKING ffmpeg_command = f'ffmpeg -i "{video_file_path}" -i "{audio_file_path}" -c:v libx264 -c:a aac -b:a 160k -movflags +faststart "{output_path}"'

            subprocess.run(ffmpeg_command, shell=True, check=True, stdout=subprocess.DEVNULL)
            subprocess.Popen(ffmpeg_command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            log_file.write(f"Video {currentConvertingIndex} converted: {video_file_path}\n")

        except subprocess.CalledProcessError as e:
            log_file.write(f"Error with Video {currentConvertingIndex}: {video_file_path}\n")
            return None, f"Error occurred during conversion: {e}"
        except Exception as e:
            log_file.write(f"Error with Video {currentConvertingIndex}: {video_file_path}\n")
            return None, f"Unexpected error occurred: {e}"


# Function to process video and audio files in a folder
def process_files(input_path, output_path):

    # Traverse the folder and find video and audio files
    for root, dirs, files in os.walk(input_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file.lower().endswith(('.mxf')):
                file_name = os.path.splitext(file)[0]  # Get file name without extension
                file_extension = os.path.splitext(file)[1]  # Get file extension
                if '\\audio\\' in file_path.lower():
                    audioFiles.append((file_path, file_extension))
                elif '\\video\\' in file_path.lower():
                    videoFiles.append((file_path, file_extension))

    # print how many video files and audio files we found
    print(f"Number of video files: {len(videoFiles)}")
    print(f"Number of audio files: {len(audioFiles)}")

    total_videos = len(videoFiles)
    max_concurrent_conversions = 1  # Maximum number of concurrent conversions
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent_conversions) as executor:
        futures = []
        for currentConvertingIndex, (video_file_path, video_ext) in enumerate(videoFiles, start=1):
            if currentConvertingIndex <= conversionIndexOffset:
                continue
            
            # Extract the first 6 characters of the video file name
            video_name = os.path.basename(video_file_path)[:6]
            
            # Find the corresponding audio file with the same first 6 characters
            audio_file = next(((file, ext) for file, ext in audioFiles if video_name == os.path.basename(file)[:6]), None)
            
            if audio_file:
                audio_file_path, audio_file_ext = audio_file
                # Generate the output path for the converted file
                base_output_path = r"C:\Users\marke\OneDrive\Documents\hvx_converted_videos\2023-10-28"

                # Inside the loop where videos are processed
                output_file_name = os.path.basename(video_file_path).split('.')[0] + "_processed.mp4"
                output_file_path = os.path.join(base_output_path, output_file_name)

                # Run the conversion logic asynchronously
                futures.append(executor.submit(convertVideo, video_file_path, audio_file_path, output_file_path))
            else:
                print(f"No matching audio file found for {video_file_path}")
        
        # Wait for all conversions to complete
        concurrent.futures.wait(futures)


# Example usage
# folder_path = input("Enter input path: ")
# output_path = input("Enter output path: ")
# folder_path = folder_path or r"C:\Users\marke\OneDrive\Documents\hvx_raws"
# output_path = output_path or r"C:\Users\marke\OneDrive\Documents\hvx_converted_videos"

log_path = r"C:\Users\marke\OneDrive\Documents\hvx_converted_videos\2023-10-28\logger.txt"
input_path = r"C:\Users\marke\OneDrive\Documents\hvx_raws\2023-10-28"
output_path = r"C:\Users\marke\OneDrive\Documents\hvx_converted_videos\2023-10-28"
process_files(input_path, output_path)


