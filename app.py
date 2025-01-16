import requests
from flask import Flask, render_template
import threading
import time

app = Flask(__name__)

ACCESS_TOKEN = 'EAAIfhZAcYfhEBOyWVmzGmvduQ8pvTuXZB10iEBDWqmGVMLrjBkM5VuOZBRDFKcxoYuZBfGvBTeyPZACH1sNFhHRssu98IfEOZBj4xMmuMLqz9Y6Tjhe3SAZCTuUPQLhXMeYZBHZC2eHqqvoryXHtIBsHHbYRF2K1VWwaZC7DZAebCAhSV8qU1oBOZCjLEt94z5TuaBEPFG4ntoYc'  # Substitua pelo seu token de acesso
USER_ID = '17841470359709957'  

BASE_URL = "https://graph.facebook.com/v21.0/"
hashtag_id = None 
image_data_cache = []  

def get_hashtag_id(hashtag_name):
    url = f"{BASE_URL}ig_hashtag_search"
    params = {
        'user_id': USER_ID,
        'q': hashtag_name,
        'access_token': ACCESS_TOKEN
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if 'data' in data and len(data['data']) > 0:
            return data['data'][0]['id']  
    print(f"Erro ao buscar hashtag '{hashtag_name}': {response.status_code}, {response.text}")
    return None  


def get_image_data():
    global image_data_cache, hashtag_id
    if not hashtag_id:
        print("Hashtag ID não definido. Tente novamente mais tarde.")
        return

    url = f"{BASE_URL}{hashtag_id}/top_media"
    params = {
        'user_id': USER_ID,
        'fields': 'caption,media_type,media_url,like_count,comments_count',
        'access_token': ACCESS_TOKEN
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        image_data = []
        for media in data.get('data', []):
            if media['media_type'] in ['IMAGE', 'CAROUSEL_ALBUM']:
                image_data.append({
                    'url': media['media_url'],
                    'likes': media.get('like_count', 0),
                    'comments': media.get('comments_count', 0),
                    'caption': media.get('caption', 0)
                })
        image_data_cache = image_data  
        print("Novas imagens obtidas:")
        for img in image_data:
            print(f"URL: {img['url']}")

        print("---------------------------------------------------------------------------------------\n\n\n")
        print(len(image_data_cache))
    else:
        print(f"Erro ao buscar imagens: {response.status_code}, {response.text}")

    if len(image_data_cache) <= 5:
        time.sleep(30)  # Aguarda 30 seguntos
    elif len(image_data_cache) <= 15:
        time.sleep(70)  # Aguarda 1 minuto e 20 segundos
    elif len(image_data_cache) <= 30:
        time.sleep(140)  # Aguarda 2 minutos e 20 segundos
    elif len(image_data_cache) <= 50:
        time.sleep(300)  # Aguarda 5 minutos
    else:
        time.sleep(600) # Aguarda 10 minutos

def background_image_fetcher():
    while True:
        get_image_data()


@app.route('/<hashtag_name>')
def index(hashtag_name):
    print("passa aqui")
    global hashtag_id
    if not hashtag_id:
        hashtag_id = get_hashtag_id(hashtag_name)  
    return render_template('index.html', image_data=image_data_cache)


if __name__ == '__main__':
    hashtag_name = "brasfertil"  
    hashtag_id = get_hashtag_id(hashtag_name)
    if hashtag_id:
        print(f"Hashtag ID obtido: {hashtag_id}")
        threading.Thread(target=background_image_fetcher, daemon=True).start()
    else:
        print("Erro ao inicializar o ID da hashtag.")
    app.run(debug=True)
