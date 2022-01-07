from ibm_watson.websocket import RecognizeCallback
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import AudioSource
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

ibm_service_url = 'XXXX'  # Bitte eigene API_Keys erstellen
ibm_authenticator = "XXXX"
import logging
logging.disable(logging.INFO)

class MyRecognizeCallback(RecognizeCallback):
    def __init__(self):
        RecognizeCallback.__init__(self)

    def on_data(self, data):
        self.data = data

        # In der Zukunft relevant
        # transcript = data["results"][0]["alternatives"][0]["transcript"]
        # confidence = data["results"][0]["alternatives"][0]["confidence"]
        # keywords = data["results"][0]["keywords_result"]
        # self.transcript = transcript
        # self.confidence = confidence
        # self.keywords = keywords

    def on_error(self, error):
        print('Error received: {}'.format(error))

    def on_inactivity_timeout(self, error):
        print('Inactivity timeout: {}'.format(error))


myRecognizeCallback = MyRecognizeCallback()


def IBM_pred():
    """Formatiert erhaltene Daten von IBM (durch send_to_IBM)"""
    data = myRecognizeCallback.data
    try:
        transcript = data["results"][0]["alternatives"][0]["transcript"]

        # Andere, hier aufgeführte Daten sind relevant für die Zukunft
        confidence = data["results"][0]["alternatives"][0]["confidence"]
        keywords = data["results"][0]["keywords_result"]
        alternatives = data["results"][0]["alternatives"]

        IBM_KI = str(transcript).strip().split()
        return IBM_KI
    except:
        return "#*# ERROR RECEIVED IBM"



def send_to_IBM(path, target):
    global ibm_authenticator, ibm_service_url
    authenticator = IAMAuthenticator(ibm_authenticator)
    speech_to_text = SpeechToTextV1(authenticator=authenticator)
    speech_to_text.set_service_url(ibm_service_url)

    with open(path, 'rb') as audio_file:
        audio_source = AudioSource(audio_file)
        speech_to_text.recognize_using_websocket(
            audio=audio_source,
            content_type='audio/wav',
            recognize_callback=myRecognizeCallback,
            model='de-DE_BroadbandModel',
            keywords=target,
            keywords_threshold=0.2,
            max_alternatives=5
        )
    return IBM_pred()
