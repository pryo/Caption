class param:
    def __init__(self):
        self.\
            checkpoint = 'model/BEST_checkpoint_coco_5_cap_per_img_5_min_word_freq.pth.tar'
        self.wordmap = 'model/WORDMAP_coco_5_cap_per_img_5_min_word_freq.json'
        self.translate_api = 'http://127.0.0.1/translate'
        self.model_id=100
        self.MODEL_BUCKET = 'learnalbe-proj-model'
        self.CHECKPOINT_NAME = 'BEST_checkpoint_coco_5_cap_per_img_5_min_word_freq.pth.tar'
        self.WORDMAP_NAME = 'WORDMAP_coco_5_cap_per_img_5_min_word_freq.json'

