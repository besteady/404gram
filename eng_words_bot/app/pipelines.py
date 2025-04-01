from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont
import random
from io import BytesIO
from PIL import Image, ImageEnhance, ImageFilter
from googletrans import Translator
import cv2
import numpy as np
import io
import google.generativeai as genai
from PIL import Image
import os

def funny_describe(image: io.BytesIO) -> str:
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    img = Image.open(image)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(["Опиши это изображение с юмором.", img])
    return response.text

def cyber_transform(image: BytesIO) -> BytesIO:
    img = Image.open(image).convert("RGB")
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(3.0)  # Increase color intensity
    img_cv = np.array(img)
    img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)
    edges = cv2.Canny(img_cv, 50, 200)
    edges_colored = cv2.applyColorMap(edges, cv2.COLORMAP_PLASMA)
    blended = cv2.addWeighted(img_cv, 0.7, edges_colored, 0.5, 0)
    final_img = Image.fromarray(cv2.cvtColor(blended, cv2.COLOR_BGR2RGB))
    final_img = final_img.filter(ImageFilter.GaussianBlur(radius=2))
    output = BytesIO()
    final_img.save(output, format="PNG")
    output.seek(0)

    return output


def random_filter(image: Image.Image) -> Image.Image:
    filters = [
        ImageFilter.BLUR,
        ImageFilter.DETAIL,
        ImageFilter.EDGE_ENHANCE,
        # ImageFilter.EMBOSS,
        ImageFilter.SHARPEN,
        ImageFilter.SMOOTH
    ]
    return image.filter(random.choice(filters))

def add_random_emoji(image: Image.Image) -> Image.Image:
    draw = ImageDraw.Draw(image)
    emojis = ["😂", "🔥", "🌟", "💀", "👽", "🎃", "🤖", "🚀", "🎨"]
    font_size = random.randint(20, 100)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    x, y = random.randint(0, image.width - font_size), random.randint(0, image.height - font_size)
    draw.text((x, y), random.choice(emojis), fill=(255, 0, 0), font=font)
    return image

def apply_crazy_transforms(image: Image.Image) -> Image.Image:
    if random.choice([True, False]):
        image = image.transpose(Image.FLIP_LEFT_RIGHT)
    if random.choice([True, False]):
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
    if random.choice([True, False]):
        image = image.rotate(random.randint(0, 20))
    return image

def change_resolution(image: Image.Image) -> Image.Image:
    scale_factor = random.uniform(0.5, 2.0)
    new_size = (int(image.width * scale_factor), int(image.height * scale_factor))
    return image.resize(new_size, Image.LANCZOS)

def transform(image: BytesIO) -> BytesIO:
    img = Image.open(image)
    img = random_filter(img)
    for _ in range(1000):
        img = add_random_emoji(img)
    img = apply_crazy_transforms(img)
    img = change_resolution(img)
    output = BytesIO()
    img.save(output, format="PNG")
    output.seek(0)
    return output

def nothing(thing):
    return thing


def chain_translate(text, language_chain=['en', 'fr', 'de', 'es']):
    translator = Translator()
    current_text = text
    for lang in language_chain:
        translation = translator.translate(current_text, dest=lang)
        current_text = translation.text
        print(f"Перевод на {lang}: {current_text}")
    final_translation = translator.translate(current_text, dest='ru')
    return final_translation.text

def add_text(image: io.BytesIO) -> io.BytesIO:
    """
    Добавляет текст по центру изображения.
    """
    img = Image.open(image)
    draw = ImageDraw.Draw(img)


    txt = funny_describe(image)

    font = ImageFont.load_default()
    # print(f"{txt=}")
    text_width, text_height = draw.textsize(txt, font=font)
    img_width, img_height = img.size
    position = ((img_width - text_width) // 2, (img_height - text_height) // 2)

    draw.text(position, txt, font=font, fill=(255, 255, 255))

    output = io.BytesIO()
    img.save(output, format="PNG")
    output.seek(0)
    return output

images_pipeline = [nothing, cyber_transform, add_text, transform]
text_pipeline = [nothing]