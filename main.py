import caption
import torch
import traceback
import fluent.event
import fluent.sender
import json
import logging
import requests
import conf.local
import time


from flask import Flask, request,render_template,jsonify
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
app = Flask(__name__)
#models
conf = conf.local.param()
checkpoint = None
decoder = None
encoder = None
word_map = None
rev_word_map  = None

fluent.sender.setup('caption_service', host='localhost', port=24224)

def report(ex):
    data = {}
    data['message'] = '{0}'.format(ex)
    data['serviceContext'] = {'service': 'caption_service'}
    # ... add more metadata
    fluent.event.Event('errors', data)


@app.before_first_request
def _load_model():

    global checkpoint
    global decoder
    global encoder
    global device
    global word_map
    global rev_word_map
    checkpoint = torch.load(conf.checkpoint)
    decoder = checkpoint['decoder']
    decoder = decoder.to(device)
    decoder.eval()
    encoder = checkpoint['encoder']
    encoder = encoder.to(device)
    encoder.eval()
    with open(conf.wordmap, 'r') as j:
        word_map = json.load(j)
    rev_word_map = {v: k for k, v in word_map.items()}
    #word_map = json.load(conf.wordmap)

@app.route('/',methods=['GET'])
def index():
    return 'you can reach the server'
@app.route('/health',methods=['GET'])
def health():
    if torch.cuda.is_available():

        return 'torch cuda is available',200
    else:
        return 'no gpu pytorch',500
#unload model
@app.route('/unload',methods = ['GET'])
def unload():
    global checkpoint
    global decoder
    global encoder
    #global device
    global word_map
    global rev_word_map
    checkpoint = None
    decoder = None
    encoder = None
    word_map = None
    rev_word_map = None
    torch.cuda.empty_cache()
    return 'model unloaded',200

@app.route('/load',methods = ['GET'])
def load():
    global checkpoint
    global decoder
    global encoder
    global device
    global word_map
    global rev_word_map
    checkpoint = torch.load(conf.checkpoint)
    decoder = checkpoint['decoder']
    decoder = decoder.to(device)
    decoder.eval()
    encoder = checkpoint['encoder']
    encoder = encoder.to(device)
    encoder.eval()
    with open(conf.wordmap, 'r') as j:
        word_map = json.load(j)
    rev_word_map = {v: k for k, v in word_map.items()}
# to cpu
def translate(words,translate_api=conf.translate_api):
    string = ' '.join(words)
    #r = requests.post(local_url, json=[{"id": 100, "src": "what is this."}])
    r = requests.post(translate_api, json=[{"id": conf.model_id, "src": string}], timeout=30)
    return r
@app.route('/capting',methods=['POST'])
def capting():
    try:
        img_obj = request.files['picture']
    except:
        report(traceback.format_exc())
        logging.exception('Error with image upload')
        return 'Error with image upload',500
    try:
        beam_arg = request.args['beam_size']
        #beam = request.files['beam_size']
        assert 0<int(beam_arg)<10
        beam = int(beam_arg)
    except:
        report(traceback.format_exc())
        logging.exception('Invalid beam input')
        beam = 5
    seq, alphas = caption.caption_image_beam_search(encoder, decoder, img_obj, word_map, beam_size=beam)
    # seq is a list of numbers
    try:
        words = [rev_word_map[ind] for ind in seq]
    except:
        report(traceback.format_exc())
        return 'can not get word from seq', 500
    return jsonify(words)
@app.route('/predict',methods=['POST'])
def predict():
    # beam = None

    try:
        img_obj = request.files['picture']
    except:
        report(traceback.format_exc())
        logging.exception('Error with image upload')
        return 'Error with image upload',500
    try:
        beam_arg = request.args['beam_size']
        #beam = request.files['beam_size']
        assert 0<int(beam_arg)<10
        beam = int(beam_arg)
    except:
        report(traceback.format_exc())
        logging.exception('Invalid beam input')
        beam = 5

    try:
        translate_api = request.args['translate_api']
    except:
        report(traceback.format_exc())
        logging.exception('no translator api specified, using the one in the conf file')
    start = time.time()

    seq,alphas = caption.caption_image_beam_search(encoder,decoder,img_obj,word_map,beam_size=beam)
    end = time.time()
    cap_elapse = start-end
    print('caption used ',cap_elapse,'seconds')
    # seq is a list of numbers
    try:
        words = [rev_word_map[ind] for ind in seq]
    except:
        report(traceback.format_exc())
        return 'can not get word from seq',500
    # words is a list of string
    try:
        start = time.time()
        r =translate(words,translate_api)
        end = time.time()
        trans_elapse = start-end
        print('translate used:',trans_elapse)
    except:
        report(traceback.format_exc())
        return 'translate failed',500
    if r.status_code==500:
        return 'translation server give 500'

    return r.text


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500
if __name__ == '__main__':
    #_load_model()
    app.run(host='127.0.0.1', port=8080, debug=True)