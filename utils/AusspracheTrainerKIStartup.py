import torch
import torch.utils.data as data
from utils.AusspracheTrainerZusatz import TextTransform, SpeechRecognitionModel
import re
import torch.nn as nn
import torch.nn.functional as F
import torchaudio


path_to_model = "static//AusspracheTrainerKI.pt"
text_transform = TextTransform()
train_audio_transforms = nn.Sequential(
    torchaudio.transforms.MelSpectrogram(sample_rate=16000, n_mels=128, normalized=True),
    # klappt nur noch mit 16000, da falsch trainiert, n_mels klappt besser mit 127
    torchaudio.transforms.FrequencyMasking(freq_mask_param=30),
    torchaudio.transforms.TimeMasking(time_mask_param=100)
)



class AusspracheTrainerKI:

    def __init__(self):
        """Lädt die AusspracheTrainerKI"""
        # global AusspracheKI_preds, test_daten, path_to_model
        print("[1/2] Model lädt...")
        # Nach Vorlage von https://www.assemblyai.com/blog/end-to-end-speech-recognition-pytorch/
        hparams = {
            "n_cnn_layers": 3,
            "n_rnn_layers": 5,
            "rnn_dim": 512,
            "n_class": 69,
            "n_feats": 128,
            "stride": 2,
            "dropout": 0.1,
            "batch_size": 1
        }

        # device = torch.device("cuda" if use_cuda else "cpu")
        device = torch.device("cpu")
        model = SpeechRecognitionModel(
            hparams['n_cnn_layers'], hparams['n_rnn_layers'], hparams['rnn_dim'],
            hparams['n_class'], hparams['n_feats'], hparams['stride'], hparams['dropout']
        ).to(device)

        checkpoint = torch.load(path_to_model, map_location="cpu")
        model.load_state_dict(checkpoint['state_dict'])
        model.eval()
        print("[1/2] Model hat geladen")
        self.model = model
        self.device = device

    @staticmethod
    def data_processing(data):
        """Dataloader entpacken"""
        spectrograms = []
        for (waveform, sample_rate, _) in data:
            spec = train_audio_transforms(waveform).squeeze(0).transpose(0, 1)
            spectrograms.append(spec)
        spectrograms = nn.utils.rnn.pad_sequence(spectrograms, batch_first=True).unsqueeze(1).transpose(2, 3)
        return spectrograms

    @staticmethod
    def GreedyDecoder(output, blank_label=68, collapse_repeated=True):
        """Zahlen zu Text, da unsere KI mit Zahlen besser als Buchstaben lernt. Daher gibt sie auch nur Zahlen aus."""
        arg_maxes = torch.argmax(output, dim=2)
        decodes = []
        for i, args in enumerate(arg_maxes):
            decode = []
            for j, index in enumerate(args):
                if index != blank_label:
                    if collapse_repeated and j != 0 and index == args[j - 1]:
                        continue
                    decode.append(index.item())
            decodes.append(text_transform.int_to_text(decode))
        return decodes


    def test(self, test_loader):
        """Test --> wav-Datei wird von unserer AusspracheTrainerKI ausgewertet"""
        predictions = []
        with torch.no_grad():
            for i, _data in enumerate(test_loader):
                spectrograms = _data
                spectrograms = spectrograms.to(self.device)

                output = self.model(spectrograms)  # (batch, time, n_class)
                output = F.log_softmax(output, dim=2)
                output = output.transpose(0, 1)  # (time, batch, n_class)

                # Hier wird die Prediction von Zahlen in Buchstaben überführt
                decoded_preds = AusspracheTrainerKI.GreedyDecoder(output.transpose(0, 1))

                prediction = re.sub(" +", " ",
                                    decoded_preds[0])  # Bei größerer Batch Size als 1 diese Zeile verändern
                predictions.append(prediction.strip().split(" "))
        return predictions


    def aussprachetrainer_predict(self, path_to_audio):
        waveform, samplerate = torchaudio.load(path_to_audio)
        dictionary = {"clientid": "", "path": path_to_audio}
        test_daten = [(waveform, samplerate, dictionary)]
        test_loader = data.DataLoader(dataset=test_daten,
                                      batch_size=1,
                                      shuffle=False,
                                      collate_fn=AusspracheTrainerKI.data_processing,
                                      )
        AusspracheTrainer_IPAKI = AusspracheTrainerKI.test(self, test_loader)
        return AusspracheTrainer_IPAKI








