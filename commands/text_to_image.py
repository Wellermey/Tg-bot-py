import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from PIL import Image

client = InferenceClient(
    provider="fal-ai",
    api_key=os.getenv["HF_TOKEN"],
)

# output is a PIL.Image object
image = client.text_to_image(
    "Astronaut riding a horse",
    model="Qwen/Qwen-Image-2512",
)

image.save("image.png")