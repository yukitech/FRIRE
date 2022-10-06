import clip
import torch
import numpy as np
from PIL import Image
from googletrans import Translator

device = "cuda" if torch.cuda.is_available() else "cpu"

model,preprocess = clip.load("ViT-B/32", device = device)

def encode(text):    
    input_text = clip.tokenize(text).to(device)

    with torch.no_grad():
        text_feat = model.encode_text(input_text)
        text_feat /= text_feat.norm(dim=-1, keepdim = True)
        text_feat = text_feat.cpu().numpy()

    return text_feat

def cos_sim(want, recipe_name):
    return np.dot(want, recipe_name) / (np.linalg.norm(want) * np.linalg.norm(recipe_name))


def img_encode(img):    
    image = Image.open(img)
    proceed_img = preprocess(image).unsqueeze(0).to(device)

    with torch.no_grad():
        image_feat = model.encode_image(proceed_img)
        image_feat /= image_feat.norm(dim=-1, keepdim = True)
        image_feat = image_feat.cpu().numpy()

    return image_feat

#encod cos_simを統合
def encode_cos(want,recipe_name):
    b = encode(recipe_name)

    return cos_sim(want,b[0])
    
#翻訳
def trans(text):
    translator = Translator()
    result = translator.translate(text, dest="en")
    return result.text

#配列作成
def insert(want, recipe_name, img_url, site_url):
    recipe_name_en = trans(recipe_name)
    cos_sim = encode_cos(want, recipe_name_en)
    
    recommend = []

    recommend.append(recipe_name)
    recommend.append(recipe_name_en)
    recommend.append(cos_sim)
    recommend.append(img_url)
    recommend.append(site_url)

    return recommend

#味に対する特徴量のリスト作成
def make_taste_list():
    taste_list = ['Plain meal', 'Light meal', 'Heavy meal', 'Healthy', 'Salty', 'Sweet', 'Spicy', 'Sour', 'Greasy']


    taste_encoded = []

    for i in range(len(taste_list)):
        temp = encode(taste_list[i])
        taste_encoded.append(temp[0])

    taste = {}

    for i in range(len(taste_list)):
        taste[taste_list[i]] = taste_encoded[i]

    return taste