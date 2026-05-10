import urllib.parse

def generate_image_url(prompt: str):

    encoded_prompt = urllib.parse.quote(prompt)

    return f"https://image.pollinations.ai/prompt/{encoded_prompt}"