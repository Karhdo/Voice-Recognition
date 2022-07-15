from pyrsistent import s
import scipy as sp
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import soundfile as sf
import torch
import kenlm
from pyctcdecode import Alphabet, BeamSearchDecoderCTC, LanguageModel
import os, zipfile
from transformers.file_utils import cached_path, hf_bucket_url
import torchaudio
import librosa

def load_pretrained_model(cache_dir):
    processor = Wav2Vec2Processor.from_pretrained("nguyenvulebinh/wav2vec2-base-vietnamese-250h", cache_dir=cache_dir)
    model = Wav2Vec2ForCTC.from_pretrained("nguyenvulebinh/wav2vec2-base-vietnamese-250h", cache_dir=cache_dir)
    if (os.path.isfile(cache_dir +  'vi_lm_4grams.bin') == False):
        lm_file = hf_bucket_url("nguyenvulebinh/wav2vec2-base-vietnamese-250h", filename='vi_lm_4grams.bin.zip')
        lm_file = cached_path(lm_file,cache_dir=cache_dir)
        with zipfile.ZipFile(lm_file, 'r') as zip_ref:
            zip_ref.extractall(cache_dir)
    lm_file = cache_dir + 'vi_lm_4grams.bin'
    return processor, model, lm_file

def get_decoder_ngram_model(tokenizer, ngram_lm_path):
    vocab_dict = tokenizer.get_vocab()
    sort_vocab = sorted((value, key) for (key, value) in vocab_dict.items())
    vocab = [x[1] for x in sort_vocab][:-2]
    vocab_list = vocab
    # convert ctc blank character representation
    vocab_list[tokenizer.pad_token_id] = ""
    # replace special characters
    vocab_list[tokenizer.unk_token_id] = ""
    # convert space character representation
    vocab_list[tokenizer.word_delimiter_token_id] = " "
    # specify ctc blank char index, since conventially it is the last entry of the logit matrix
    print(tokenizer.pad_token_id)
    alphabet = Alphabet.build_alphabet(vocab_list, ctc_token_idx=tokenizer.pad_token_id)
    lm_model = kenlm.Model(ngram_lm_path)
    decoder = BeamSearchDecoderCTC(alphabet, language_model=LanguageModel(lm_model))
    return decoder

def speech_file_to_array_fn(batch):
    # speech, sampling_rate = sf.read(batch["file"])
    # speech = speech.flatten()
    # speech, sampling_rate = torchaudio.load(batch["file"])
    speech, sampling_rate = librosa.load(batch["file"], sr=16000)
    batch["speech"] = speech
    batch["sampling_rate"] = sampling_rate
    return batch

def inference(audio_file): 
    cache_dir = './vietnamese_asr/cache/'

    # Load model
    processor, model, lm_file = load_pretrained_model(cache_dir)

    ds = speech_file_to_array_fn({"file": audio_file})
    ngram_lm_model = get_decoder_ngram_model(processor.tokenizer, lm_file)

    # infer model
    input_values = processor(
        ds["speech"], 
        sampling_rate=ds["sampling_rate"], 
        return_tensors="pt"
    ).input_values
    logits = model(input_values).logits[0]

    # decode ctc output
    pred_ids = torch.argmax(logits, dim=-1)
    greedy_search_output = processor.decode(pred_ids)
    beam_search_output = ngram_lm_model.decode(logits.cpu().detach().numpy(), beam_width=500)
    print("Greedy search output: {}".format(greedy_search_output))
    print("Beam search output: {}".format(beam_search_output))
    return greedy_search_output, beam_search_output

# inference()