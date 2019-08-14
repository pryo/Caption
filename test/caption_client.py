import requests
if __name__ == '__main__':
    local_url = ' http://127.0.0.1:8000/predict'
    gce_url = 'http://146.148.103.174:80/predict'
    # files = {'picture':open(input('image path: '),'rb'),'beam_size':input('beam size: ')}
    files = {'picture': open(input('image path: '), 'rb')}
    r = requests.post(gce_url,params = {'beam_size':input('beam size: ')},
                      files=files,timeout=400)

    print(r.text)