import os
import subprocess

def create_hls_streams(input_file, output_dir, resolutions):
    """
    Create HLS streams for different resolutions and bitrates, each in its own folder.

    Parameters:
    input_file (str): Path to the input video file.
    output_dir (str): Directory to save the HLS stream files.
    resolutions (list): List of resolutions with their respective bitrates.
                        Example: [{"name": "720p", "width": 1280, "height": 720, "bitrate": "3000k"}]
    """
    # Extract the base name of the input file (without extension)
    stream_name = os.path.splitext(os.path.basename(input_file))[0]
    
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Path for the master playlist
    master_playlist_path = os.path.join(output_dir, "master.m3u8")

    # Master playlist content
    master_playlist_content = "#EXTM3U\n"

    for resolution in resolutions:
        # Create a folder for the current resolution
        resolution_folder = os.path.join(output_dir, resolution["name"])
        if not os.path.exists(resolution_folder):
            os.makedirs(resolution_folder)
        
        # Define output playlist and segment pattern for this resolution
        output_playlist = os.path.join(resolution_folder, f"{stream_name}.m3u8")
        output_segments = os.path.join(resolution_folder, f"{stream_name}_%03d.ts")
        
        # FFmpeg command to create HLS stream for this resolution
        command = [
            "ffmpeg",
            "-i", input_file,
            "-vf", f"scale=w={resolution['width']}:h={resolution['height']}",  # Video scaling
            "-c:v", "libx264",        # Video codec
            "-preset", "fast",        # Encoding preset
            "-crf", "23",             # Quality
            "-b:v", resolution["bitrate"],  # Video bitrate
            "-c:a", "aac",            # Audio codec
            "-b:a", "128k",           # Audio bitrate
            "-ac", "2",               # Audio channels
            "-hls_time", "6",         # Segment duration
            "-hls_playlist_type", "vod",
            "-hls_segment_filename", output_segments,  # Segment filename pattern
            output_playlist
        ]

        # Run the FFmpeg command
        try:
            subprocess.run(command, check=True)
            print(f"HLS stream for {resolution['name']} created successfully in {resolution_folder}.")
        except subprocess.CalledProcessError as e:
            print(f"Error creating HLS stream for {resolution['name']}: {e}")
            continue

        # Add entry to master playlist
        master_playlist_content += f"#EXT-X-STREAM-INF:BANDWIDTH={int(resolution['bitrate'].replace('k', '')) * 1000},RESOLUTION={resolution['width']}x{resolution['height']}\n"
        master_playlist_content += f"{resolution['name']}/{stream_name}.m3u8\n"

    # Write the master playlist
    with open(master_playlist_path, "w") as master_playlist:
        master_playlist.write(master_playlist_content)
    print(f"Master playlist created at {master_playlist_path}")

# Example usage
if __name__ == "__main__":
    input_video = "input.mkv"  # Path to your input video file
    output_directory = "hls_streams"  # Root directory to save HLS streams

    # Define resolutions and bitrates
    resolutions = [
        {"name": "720p", "width": 1280, "height": 720, "bitrate": "3000k"},
        {"name": "480p", "width": 854, "height": 480, "bitrate": "1500k"},
        {"name": "360p", "width": 640, "height": 360, "bitrate": "800k"},
        {"name": "240p", "width": 426, "height": 240, "bitrate": "500k"},
        {"name": "144p", "width": 256, "height": 144, "bitrate": "200k"}
    ]

    create_hls_streams(input_video, output_directory, resolutions)