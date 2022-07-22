from audio_to_text import load_pretrained_model

cache_dir = './vietnamese_asr/cache/'
processor, model, lm_file = load_pretrained_model(cache_dir)