import base64
from together import Together

client = Together()

getDescriptionPrompt = """what is in the image and what is his emotion.you need to describe detaily in short sentense(2~3).    
                        """
imagePath1= "test/1.jpg"
imagePath2="test/2.jpg"

def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

base64_image1 = encode_image(imagePath1)
base64_image2 = encode_image(imagePath2)

stream = client.chat.completions.create(
    model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": getDescriptionPrompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image1}",
                    },
                },
                # {
                #     "type": "image_url",
                #     "image_url": {
                #         "url": f"data:image/jpeg;base64,{base64_image2}",
                #     },
                # },
            ],
        }
    ],
    stream=True,
)
# base64_image = stream
for chunk in stream:
    print(chunk.choices[0].delta.content or "" if chunk.choices else "", end="", flush=True)