import time
import instructor
import google.generativeai as genai
import json
import os

from pydantic import BaseModel, Field
from typing import List
from moviepy.editor import VideoFileClip
from dotenv import load_dotenv

load_dotenv()


GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']
genai.configure(api_key=GOOGLE_API_KEY)

def upload_video(video_file_name):
    print("[Process] Uploading File...")

    video_file = genai.upload_file(path=video_file_name)

    while video_file.state.name == "PROCESSING":
        time.sleep(10)
        video_file = genai.get_file(video_file_name.name)

    if video_file.state.name == "FAILED":
        raise ValueError(video_file.state.name)

    return video_file

def chat_video_gemini(video_file_name, prompt="No special requirements"):
    video_file = upload_video(video_file_name)

    class MusicPrompt(BaseModel):
        video_description: str = Field(
            ...,
            title="Describe the video in details, make sure to include story line, key elements & transcription of what were discussed"
        )

        music_title: str = Field(..., title="Music title")

        music_style_tags: List[str] = Field(
            ...,
            title="short tags of music style, like ['HipHop', 'Trap', 'male vocals'] OR ['Folk', 'acoustic Guitar', 'male vocals'], etc. max 3 tags"
        )

        music_lyric: str = Field(
            ...,
            title=f"turn video description into lyrics, lyric should include unique details that can only be used for this specific video;  the lyric length needs to be similar to video length"
        )

    # Initialize LLMs
    instructor_client = instructor.from_gemini(
        client=genai.GenerativeModel(
            model_name="gemini-1.5-pro",
        ),
        mode = instructor.Mode.GEMINI_JSON
    )

    result = instructor_client.messages.create(
        messages=[
            {
                "role" : "user",
                "content": f"These are frames from a video; your goal is to generate a proposal of a music that goes well with the video; Specific requirements you HAVE TO consider: {prompt} ",

            },
            {"role" : "user", "content": video_file}
        ],
        response_model=MusicPrompt
    )

    return json.loads(result.json())

