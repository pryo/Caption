import requests
if __name__ == '__main__':
    local_url = ' http://127.0.0.1:80/predict'
    gc_caption_url = 'http://146.148.103.174/predict'
    gce_translate_url = 'http://104.197.123.37/translate'
    # files = {'picture':open(input('image path: '),'rb'),'beam_size':input('beam size: ')}
    online_img = '~/Caption/test/IMG_4039.jpg'
    local_img = '/home/david/Developer/a-PyTorch-Tutorial-to-Image-Captioning/test/IMG_4039.jpg'
    files = {'picture': open(local_img, 'rb')}
    r = requests.post(gc_caption_url,params = {'beam_size':5,'translate_api':gce_translate_url},
                      files=files,timeout=400)

    print(r.text)