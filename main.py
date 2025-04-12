from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from YouTubeHandler import Handler

import os

global yt
yt: Handler = None

global downloaded
downloaded = ""

app = FastAPI()  # http://127.0.0.1:8000


@app.get("/")
async def root():
    return {"message": "Let's download some videos 🐹"}


class YouTubeLink(BaseModel):
    URL: str

    class Config:
        validate_by_name = True
        alias = {"URL": "url"}


class LinkResponseModel(BaseModel):
    Title: str
    Length: str
    Thumbnail_URL: str
    Video_ID: str
    Best_Resolution_Available: str
    Best_Audio_Bitrate_Available: str


@app.post("/FetchInfo")
async def FetchInfo(Link: YouTubeLink):
    print(Link)
    print(Link.model_dump_json())
    global yt
    yt = Handler(Link.URL)
    info = await yt.FetchInfo()
    return LinkResponseModel(**info)



@app.post("/Merge")
async def Merge(video_url: str = Query(...)):
    yt = Handler(video_url)
    downloaded_path = await yt.Merge()

    if not downloaded_path or not os.path.exists(downloaded_path):
        return {"error": "Merging failed. Check FFmpeg setup."}

    return {"message": "Merge completed", "video_id": yt.video.video_id}



# @app.get("/Merge")
# async def Merge():
#     global yt
#     if yt is None:
#         return {"error": "No video URL provided. Fetch info first."}

#     global downloaded
#     downloaded = await yt.Merge()

#     if yt.output_file is None or downloaded is None:
#         return {"error": "Merging failed. Check FFmpeg setup."}

#     return {"message": f"The File is Merged Downloaded"}



from fastapi import Query
@app.get("/Download")
async def Download(video_id: str = Query(..., alias="video_id")):
    merged_dir = os.path.abspath("Downloads/Merged")

    for filename in os.listdir(merged_dir):
        if video_id in filename:
            file_path = os.path.join(merged_dir, filename)
            if os.path.exists(file_path):
                return FileResponse(
                    path=file_path,
                    filename=filename,
                    media_type="video/mp4",
                )

    return {"error": "Requested file not found. Please ensure it is merged first."}



# @app.get("/Download")
# async def Download():
#     global downloaded
#     global yt

#     if yt is None:
#         return {"error": "No video URL provided. Try /FetchInfo first."}

#     if not downloaded or not os.path.exists(downloaded):
#         return {"error": "Merging failed or file not found."}
    
#     if not downloaded:
#         print("Merging...")
#         downloaded = await yt.Merge()
#         print("Clearing object")
#         downloaded = None
#         yt = None

#     return FileResponse(
#         path=downloaded,
#         filename=os.path.basename(downloaded),
#         media_type="video/mp4",
#     )
