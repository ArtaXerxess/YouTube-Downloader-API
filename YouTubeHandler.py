import asyncio, subprocess, re, os
from pytubefix import YouTube


class Handler:
    def __init__(self, URL: str):
        self.video = YouTube(url=URL)
        self.output_file = None

    async def GetBestVideo(self):
        try:
            return self.video.streams.filter(
                only_video=True, mime_type="video/mp4"
            ).order_by("resolution")[-1]
        except Exception as e:
            print(f"Error getting best video: {e}")

    async def GetBestAudio(self):
        try:
            return self.video.streams.filter(only_audio=True).order_by("abr")[-1]
        except Exception as e:
            print(f"Error getting best audio: {e}")

    async def FetchInfo(self):
        best_video = await self.GetBestVideo()
        best_audio = await self.GetBestAudio()
        self.video.video_id
        result = {
            "Title": self.video.title,
            "Length": str(self.video.length) + " seconds",
            "Thumbnail_URL": self.video.thumbnail_url,
            "Video_ID":self.video.video_id,
            "Best_Resolution_Available": best_video.resolution if best_video else "N/A",
            "Best_Audio_Bitrate_Available": best_audio.abr if best_audio else "N/A",
        }
        # print(result)
        return result

    async def Merge(self):

        await self.FetchInfo()

        best_video = await self.GetBestVideo()
        best_audio = await self.GetBestAudio()

        video_dir = os.path.abspath("Downloads/Video")
        audio_dir = os.path.abspath("Downloads/Audio")
        merged_dir = os.path.abspath("Downloads/Merged")

        os.makedirs(video_dir, exist_ok=True)
        os.makedirs(audio_dir, exist_ok=True)
        os.makedirs(merged_dir, exist_ok=True)

        for folder in video_dir, audio_dir, merged_dir:
            for file in os.listdir(folder):
                file_path = os.path.join(folder,file)
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(e)


        sanitized_title = re.sub(r'[\\/*?:"<>|]', "", self.video.title)
        sanitized_title = sanitized_title.replace(" ", "_")

        print("⬇️  Downloading Video & Audio Streams...")
        video_task = asyncio.to_thread(
            best_video.download,
            output_path=video_dir,
            filename=f"{sanitized_title}.mp4",
        )
        audio_task = asyncio.to_thread(
            best_audio.download,
            output_path=audio_dir,
            filename=f"{sanitized_title}.m4a",
        )

        video_path, audio_path = await asyncio.gather(video_task, audio_task)


        if not os.path.exists(video_path):
            print(f"❌ Video file not found: {video_path}")
            return
        print(f"✅ Video saved at: {video_path}")

        if not os.path.exists(audio_path):
            print(f"❌ Audio file not found: {audio_path}")
            return
        print(f"✅ Audio saved at: {audio_path}")


        self.output_file = os.path.join(merged_dir, f"{sanitized_title}.mp4")

        ffmpeg_path = r"C:/Users/Harsh/Desktop/Projects/ffmpeg-7.1.1-essentials_build/ffmpeg-7.1.1-essentials_build/bin/ffmpeg.exe"
        command = f'"{ffmpeg_path}" -i "{video_path}" -i "{audio_path}" -c:v libx264 -c:a aac "{self.output_file}"'

        command = command.replace("\\","/")

        print(f"Running FFmpeg: \n\n{command}\n\n")

        subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        print("It's done...")

        return self.output_file



if __name__ == "__main__":
    yt = Handler("https://www.youtube.com/watch?v=94v6ZQWL6IU")

    asyncio.run(yt.FetchInfo())
    asyncio.run(yt.Merge())
