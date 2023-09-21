import torch
import numpy as np
from tqdm import tqdm
from termcolor import cprint
from transformers import Wav2Vec2Model


def load_wav2vec_model(wav2vec_model):
    cprint("Loading HuggingFace'S Wav2Vec2.0", "cyan")
    model = Wav2Vec2Model.from_pretrained(wav2vec_model)
    return model

def getW2VLastFourLayersAvg(wav2vec, waveform):
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    wav2vec = wav2vec.to(device)

    def _process_chunk(wav2vec, audio_chunk, mode="huggingface"):
        audio_chunk = audio_chunk.to(device)
        with torch.no_grad():
            out = wav2vec(input_values=audio_chunk, output_hidden_states=True)
            out = out.hidden_states[-4:]
        a = [l.detach() for l in out]
        return torch.stack(a).mean(axis=0)

    splits = np.array_split(list(range(waveform.shape[-1])), 10)
    embeddings = []
    pbar = tqdm(splits, desc="Pre-computing W2V embeddings (last 4 layers)")
    for split in pbar:
        out = _process_chunk(wav2vec, waveform[0, split].unsqueeze(0))
        embeddings.append(out.detach())
    return torch.vstack(
        [e.squeeze() for e in embeddings]
    ).t()
