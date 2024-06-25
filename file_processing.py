import time
import instructor
from pydantic import BaseModel, Field
from typing import List
import google.generativeai as genai
from moviepy.editor import VideoFileClip
import json
from dotenv import load_dotenv

load_dotenv()


