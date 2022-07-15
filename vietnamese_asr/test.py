import gradio as gr
from transformers.file_utils import cached_path, hf_bucket_url
import os, zipfile
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from datasets import load_dataset
import torch
import kenlm
import torchaudio
import librosa
from pyctcdecode import Alphabet, BeamSearchDecoderCTC, LanguageModel

cache_dir = './src/vietnamese_asr/cache/'
processor = Wav2Vec2Processor.from_pretrained("nguyenvulebinh/wav2vec2-base-vietnamese-250h", cache_dir=cache_dir)
model = Wav2Vec2ForCTC.from_pretrained("nguyenvulebinh/wav2vec2-base-vietnamese-250h", cache_dir=cache_dir)
lm_file = hf_bucket_url("nguyenvulebinh/wav2vec2-base-vietnamese-250h", filename='vi_lm_4grams.bin.zip')
lm_file = cached_path(lm_file,cache_dir=cache_dir)
with zipfile.ZipFile(lm_file, 'r') as zip_ref:
    zip_ref.extractall(cache_dir)
lm_file = cache_dir + 'vi_lm_4grams.bin'

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
    alphabet = Alphabet.build_alphabet(vocab_list, ctc_token_idx=tokenizer.pad_token_id)
    lm_model = kenlm.Model(ngram_lm_path)
    decoder = BeamSearchDecoderCTC(alphabet,
                                   language_model=LanguageModel(lm_model))
    return decoder

ngram_lm_model = get_decoder_ngram_model(processor.tokenizer, lm_file)

# define function to read in sound file
def speech_file_to_array_fn(path, max_seconds=10):
    batch = {"file": path}
    # speech_array, sampling_rate = torchaudio.load(batch["file"])
    # if sampling_rate != 16000:
    #   transform = torchaudio.transforms.Resample(orig_freq=sampling_rate,
    #                                              new_freq=16000)
    #   speech_array = transform(speech_array)
    # speech_array = speech_array[0]
    # if max_seconds > 0:
    #   speech_array = speech_array[:max_seconds*16000]
    # batch["speech"] = speech_array.numpy()
    # batch["sampling_rate"] = 16000
    # return batch
    speech, sampling_rate = librosa.load(batch["file"], sr=16000)
    batch["speech"] = speech
    batch["sampling_rate"] = sampling_rate
    return batch

# tokenize
def inference(audio):
   # read in sound file
    # load dummy dataset and read soundfiles
    print(audio.name)
    ds = speech_file_to_array_fn(audio.name)
    # infer model
    input_values = processor(
          ds["speech"], 
          sampling_rate=ds["sampling_rate"], 
          return_tensors="pt"
    ).input_values
    # decode ctc output
    logits = model(input_values).logits[0]
    pred_ids = torch.argmax(logits, dim=-1)
    greedy_search_output = processor.decode(pred_ids)
    beam_search_output = ngram_lm_model.decode(logits.cpu().detach().numpy(), beam_width=500)
    return beam_search_output

inputs = gr.inputs.Audio(label="Input Audio", type="file")
outputs =  gr.outputs.Textbox(label="Output Text")
title = "wav2vec2-base-vietnamese-250h"
description = "Gradio demo for a wav2vec2-base-vietnamese-250h. To use it, simply upload your audio, or click one of the examples to load them. Read more at the links below. Currently supports .wav 16_000hz files"
article = "<p style='text-align: center'><a href='https://github.com/vietai/ASR' target='_blank'> Github repo for demonstration </a> | <a href='https://huggingface.co/nguyenvulebinh/wav2vec2-base-vietnamese-250h' target='_blank'>Pretrained model</a></p>"
examples=[['./src/audio/vietnamese/wav/wav_1.wav'], ['./src/audio/vietnamese/wav/wav_2.wav'], ['./src/audio/vietnamese/wav/wav_3.wav']]
gr.Interface(inference, inputs, outputs, title=title, description=description, article=article, examples=examples).launch(share=True)