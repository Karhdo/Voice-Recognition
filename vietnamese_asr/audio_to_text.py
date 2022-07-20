from pyrsistent import s
import scipy as sp
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import soundfile as sf
import torch
import kenlm
from pyctcdecode import Alphabet, BeamSearchDecoderCTC, LanguageModel
import os, zipfile
from transformers.file_utils import cached_path, hf_bucket_url
import librosa
from pydub import AudioSegment
from pydub.silence import split_on_silence

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

def get_large_audio_transcription(audio_file, model, lm_file, processor):
    """
    Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks
    """
    # open the audio file using pydub
    sound = AudioSegment.from_wav(audio_file)  
    # split audio sound where silence is 700 miliseconds or more and get chunks
    chunks = split_on_silence(sound,
        # experiment with this value for your target audio file
        min_silence_len = 400,
        # adjust this per requirement
        silence_thresh = sound.dBFS-14, 
        # keep the silence for 1 second, adjustable as well
        # keep_silence=250,
    )

    folder_name = "uploads/audio-chunks"
    # create a directory to store the audio chunks
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)

    greedy_whole_text = ""
    beam_whole_text = ""

    # process each chunk 
    for i, audio_chunk in enumerate(chunks, start=1):
        # export audio chunk and save it in
        # the `folder_name` directory.
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")

        greedy_output, beam_output = inference(chunk_filename, model, lm_file, processor)
        if (greedy_output and beam_output):
            greedy_whole_text += " " + greedy_output
            beam_whole_text += " " + beam_output
        os.remove(chunk_filename)
    
    if os.path.exists(audio_file):
        os.remove(audio_file)
    else:
        print("The file does not exist")
    print("Greedy search output: {}".format(greedy_whole_text))
    print("Beam search output: {}".format(beam_whole_text))
    return greedy_whole_text, beam_whole_text

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
    decoder = BeamSearchDecoderCTC(alphabet, language_model=LanguageModel(lm_model))
    return decoder

def speech_file_to_array_fn(batch):
    speech, sampling_rate = librosa.load(batch["file"], sr=16000)
    batch["speech"] = speech
    batch["sampling_rate"] = sampling_rate
    return batch

def inference(audio_file, model, lm_file, processor): 
    ds = speech_file_to_array_fn({"file": audio_file})
    print("Load audio successfully")
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