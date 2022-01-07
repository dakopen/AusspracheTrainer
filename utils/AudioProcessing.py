import time
import pathlib
from utils.IPA import IPA
from utils.IBM_API import send_to_IBM
from utils.AusspracheTrainerKIStartup import AusspracheTrainerKI
aussprachetrainer = AusspracheTrainerKI()
import speech_recognition as sr

ipa = IPA()
r = sr.Recognizer()


def aussprachetrainer_KI(path_to_audio):
    # Audio an AusspracheTrainerIPAKI senden...

    try:
        AusspracheTrainerIPAKI = aussprachetrainer.aussprachetrainer_predict(path_to_audio)
        AusspracheTrainerIPAKI = [item for sublist in AusspracheTrainerIPAKI for item in sublist]
        return " ".join(AusspracheTrainerIPAKI)

    except:
        return "#*# ERROR RECEIVED AUSSPRACHETRAINERKI"


def google_KI(path_to_target):
    # Audio an Google senden...
    try:
        audiofile = sr.AudioFile(path_to_target)
        with audiofile as source:
            audio = r.record(source)
            google_pred = r.recognize_google(audio, language="de-DE")  # Throws Error if not correctly interpreted
            Google_KI_for_IPA = str(google_pred).strip().lower()
            Google_IPAKI, _ = ipa.text_zu_IPA(ipa.text_preparation(Google_KI_for_IPA))

        return Google_IPAKI, str(google_pred).strip()
    except:
        return "#*# ERROR RECEIVED GOOGLE", ""


def ibm_KI(path_and_target):
    # Audio an IBM senden...
    try:
        path_to_audio, targetliste = path_and_target[0], path_and_target[1]

        IBM_KI = send_to_IBM(path_to_audio, targetliste)
        if IBM_KI != "#*# ERROR RECEIVED IBM":
            IBM_IPAKI, _ = ipa.text_zu_IPA(ipa.text_preparation(" ".join(IBM_KI)))
        else:
            IBM_IPAKI = IBM_KI

        return IBM_IPAKI, " ".join(IBM_KI)

    except:
        return "#*# ERROR RECEIVED IBM", ""


def delete_audio_file(path_to_audio):
    audio_file = pathlib.Path(path_to_audio)
    
    try:
        audio_file.unlink()
    except FileNotFoundError:
        print("Error unlinking file!")

