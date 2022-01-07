from os import stat
import random
import re
import sys
import concurrent.futures
from datetime import datetime
from urllib.parse import unquote
import sys

from django.shortcuts import render, redirect
# Create your views here.
from django.http import HttpResponse
from django.http import JsonResponse
from utils import AudioProcessing
from utils.Auswertung import auswertung, calculate_colour, adjektiv_fuer_score, sprachfehler_from_scores

from django.template.loader import render_to_string
from django.templatetags.static import static


def targetsatz_validation(targetsatz):
    targetsatz = str(targetsatz).lower()
    targetsatz = "".join(e for e in targetsatz if e.isalnum() or e == " ")
    targetsatz = re.sub("\s\s+", " ", targetsatz).strip()
    targetsatz = re.sub("[^a-zA-ZäöüÄÖÜß\s]", "", targetsatz)
    return targetsatz


def generate_time_stamp():
    datetime_obj = datetime.now()
    timestamp = datetime_obj.strftime("%d-%b-%Y_%H_%M_%S-%f")
    return timestamp


def home(request):
    context = {
        "textgenerator": [
            "Zufälligen Satz",
            "Sch-Satz",
            "S-Satz",
            "Ch-Satz",
            # Satz des Tages
        ]
    }
    return render(request, '../templates/index.html', context=context)


def satzgenerator(request):
    if request.GET.get('session') == None:
        return redirect("/")
    satzart = (request.body).decode("utf-8-sig")
    print(satzart)
    textareavalue = str(request.META["HTTP_TEXTAREAVALUE"]).strip()
    print(textareavalue)
    if satzart == "Zufälligen Satz":
        with open("static//assets//random_saetze.txt", "r",
                  encoding="utf-8-sig") as random_saetze:
            lines = random_saetze.readlines()
    elif satzart == "Sch-Satz":
        lines = ["Am Strand bauen die Kinder mit dem Spielzeug und der Schaufel eine Sandburg.", "Die Schnecken hinterlassen eine Schleimspur auf der Straße.", "Auf der Schnellstraße herrscht schneller Straßenverkehr.", "Spreewaldgurken schmecken gut, sind aber im Spreewald am schmackhaftesten.", "Die Schlange erschreckt die Spinne im Spind.", "Das Schulkind versteckt sich im Schrank.", "Seine Schüssel sprang in zwei.", "Hirsche haben ein prächtiges Geweih.", "Die schmützige Wärsche gehört in den schwarzen Korb.", "Stefan erscheint als letzter auf dem Schiff.", "Im Schwarzwald gibt es Schmetterlinge zu beobachten.", "Im Schein der Sonne schmilzt der Schneeman dahin.", "Dem Schwein schmeckt die geschälte Kartoffel.", "Hast du im Sportunterricht an Schnelligkeit gewonnen?", "Sterne kann man am Strand bewundern.", "Schneide die Banane in Stücke!"]
    elif satzart == "Ch-Satz":
        lines = ["Die Eichhörnchen sammeln Eicheln für ihren Wintervorrat.", "Ich möchte noch in die Kirche gehen.", "Ich weiß nicht, ob Sie Griechisch sprechen und mein Griechisch verstehen.", "Der jämmerliche König hinterlässt eine Nachricht.", "Das Schweinchen quiekt e fröhlich.", "Wie bleich das Pärchen wurde.", "Es ist mir peinlich, die Zeichnung vorzustellen.", "Die Berichterstattung sah fürchterlich aus.", "Ungerechtigkeit gehört sicherlich zum Leben dazu.", "Das tüchtige Mädchen handelt richtig.", "Ein reicher Scheich kaufte die gesamte Einrichtung.", "Laut meiner Recherche gehört sein Vermächtnis der Tochter.", "Tomaten haben beachtlich viele Vitamine und sind sehr reichhaltig an wichtigen Mineralien.",
         "Es ist echt gefährlich sich im Auto nicht anzuschnallen.", "Ein Eichhörnchen ist leichter als ein Elch."]
    elif satzart == "S-Satz":  # else
        lines = ["Ein Seehund sonnt sich in der Mittagssonne.", "In der Sage wird von Sandstein berichtet.", "Unser Silberbesteck hat etwas ansich.", "Die Szene wird von Susanne vorgelesen.", "In der Suppe fehlt Salz.", "Im Saal sitzt manch seltsamer Mann.", "Sonntags singen sieben Zwwerge am See lustige Lieder.", "Sie segelt schon siebzig Jahre.", "Sechs Ameisen suchen schutz unterm Baum.", "Der Zug fährt vom Zirkus ins Saarland.", "Sauerstoff ist überlebenswichtig für Säugetiere.", "Hase und Gans grasen zusammen auf der Wiese.", "Zwei Sachen noch, dann ist sie fertig.", "Im September gibt es Sauerbraten zu essen.", "Salat und Sellerie sind gesunde Lebensmittel." "Susi sagte, dass sie gerne Salat mit Mais isst.", "Morgens isst Susanne gerne Müsli mit Nüssen.", "Auf der Insel scheint die Sonne übermäßig viel.", "Hans isst gerne Bratwurst mit Senf."]
    lines = [i.strip() for i in lines]
    if textareavalue in lines:
        lines.remove(textareavalue)

    #return render(request, '../templates/indexrender.html')

    return HttpResponse(random.choice(lines).strip())


def audio(request):
    session_id = str(request.GET.get('session'))

    if request.GET.get('session') == None:
        return redirect("/")

    print(session_id, "SESSIONID")
    if sys.getsizeof(request.body) < 10000:  # Mindestlänge
        return HttpResponse("Audio_to_short")

    timestamp = generate_time_stamp()
    request.session["rawtargetsatz_%s" % session_id] = re.sub("\s\s+", " ", str(unquote(str(request.META["HTTP_TARGETSATZ"])))).strip()

    request.session["targetsatz_%s" % session_id] = targetsatz_validation(unquote(str(request.META["HTTP_TARGETSATZ"])))
    if not request.session["targetsatz_%s" % session_id] or len(str(request.session["targetsatz_%s" % session_id])) > 120:
        return HttpResponse('Fehler_Targetsatz')

    request.session["audiopath_%s" % session_id] = f'./media/{timestamp}__{session_id}.wav'


    if sys.getsizeof(request.body) > 2200000:
        return HttpResponse('Audio_unnormal_length')
    

    f = open(str(request.session["audiopath_%s" % session_id]), 'wb')
    f.write(request.body)
    f.close()

    return HttpResponse('Audio empfangen')


def recursiveresponse(request):
    if request.GET.get('session') == None:
        return redirect("/")
    session_id = str(request.GET.get('session'))
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_aussprachetrainer_KI = executor.submit(AudioProcessing.aussprachetrainer_KI, str(request.session["audiopath_%s" % session_id]))
        future_google_KI = executor.submit(AudioProcessing.google_KI, str(request.session["audiopath_%s" % session_id]))
        future_ibm_KI = executor.submit(AudioProcessing.ibm_KI,
                                        [str(request.session["audiopath_%s" % session_id]), str(request.session["targetsatz_%s" % session_id]).split()])

        target_to_IPA = executor.submit(AudioProcessing.ipa.text_zu_IPA, AudioProcessing.ipa.text_preparation(str(request.session["targetsatz_%s" % session_id])))
        print("TARGET:", target_to_IPA.result()[0])
        print("IPA_ZUORDNUNG:", target_to_IPA.result()[1])
        executor.shutdown()  # Wenn alle fertig sind, dann hört er auf
    AudioProcessing.delete_audio_file(str(request.session["audiopath_%s" % session_id]))  # Löscht die Audio wieder


    print(future_aussprachetrainer_KI.result())
    errormessage = ""
    if future_aussprachetrainer_KI.result().startswith("#*# ERROR RECEIVED"):
        errormessage += "AusspracheTrainerKI "

    if future_google_KI.result()[0].startswith("#*# ERROR RECEIVED"):
        errormessage += "Google "

    if future_ibm_KI.result()[0].startswith("#*# ERROR RECEIVED"):
        errormessage += "IBM"

    if errormessage:
        errormessage = "#*# ERROR RECEIVED " + errormessage
        return HttpResponse("<span class='red' style='font-size:1em;'>Error erhalten: Der aufgenommene Satz konnte nicht analysiert werden. Bitte erneut aufnehmen oder einen anderen Satz versuchen.</span>")

    request.session["IBMKI_%s" % session_id] = future_ibm_KI.result()[1]
    request.session["GOOGLEKI_%s" % session_id] = future_google_KI.result()[1]
    request.session["AUSSPRACHETRAINERIPAKI_%s" % session_id] = future_aussprachetrainer_KI.result()
    request.session["TARGETIPA_%s" % session_id] = target_to_IPA.result()[0]

    auswertungsergebnis, scores, sprachfehler_scores = auswertung(target_to_IPA.result()[0], target_to_IPA.result()[1],
                                             [future_aussprachetrainer_KI.result(), future_google_KI.result()[0], future_ibm_KI.result()[0]])


    buchstabenscores = {}
    buchstabenindex = 0

    print(str(request.session["rawtargetsatz_%s" % session_id]))
    print(str(request.session["targetsatz_%s" % session_id]))
    
    
    reg=re.compile('^[a-zA-ZäöüÄÖÜß\s]')
    for index, buchstabe in enumerate(str(request.session["rawtargetsatz_%s" % session_id])):
        colour = "green"
        try:
            if buchstabe.isalnum() and reg.match(buchstabe):
                colour = calculate_colour(auswertungsergebnis[buchstabenindex])
                buchstabenindex += 1
            elif buchstabe == " " and str(request.session["targetsatz_%s" % session_id])[buchstabenindex] == " ":
                colour = calculate_colour(auswertungsergebnis[buchstabenindex])
                buchstabenindex += 1
        except IndexError:
            print("Indexerror, aber nicht schlimm")
        buchstabenscores[index] = (colour, buchstabe)
    request.session["buchstabenscores_%s" % session_id] = buchstabenscores
    farbigeAntwort = buchstaben_scores_interally(request)
    if scores[0] < 0:
        scores = (0, scores[1], scores[2])
    

    context = {
            "farbigeAntwort": farbigeAntwort,
            "finalscore": ("%.2f" % float(scores[0]*100)).replace(".", ","),
            "scoreadjektiv": adjektiv_fuer_score(scores[0]),
            "sprachfehler": sprachfehler_from_scores(sprachfehler_scores, scores[1]),
        }

    return render(request, '../templates/ergebnis.html', context=context)


def buchstaben_scores(request):
    if request.GET.get('session') == None:
        return redirect("/")
    session_id = str(request.GET.get('session'))
    context = {"buchstabenscores": request.session["buchstabenscores_%s" % session_id]}
    return render(request, '../templates/farbigeAntwort.html', context=context)


def buchstaben_scores_interally(request):
    session_id = str(request.GET.get('session'))
    context = {"buchstabenscores": request.session["buchstabenscores_%s" % session_id]}
    return render_to_string('../templates/farbigeAntwort.html', context=context)


def get_other_transcripts(request):

    session_id = str(request.GET.get('session'))
    kityp = str(request.META["HTTP_KITYP"])
    farbigeAntwort = "<span class='lila'>"
    if kityp == "AT":
        farbigeAntwort = ["<span class='lila'>" + str(request.session["AUSSPRACHETRAINERIPAKI_%s" % session_id]) + "</span>", str(request.session["TARGETIPA_%s" % session_id])]
        return JsonResponse(farbigeAntwort, safe=False)
    elif kityp == "GOOGLE":
        farbigeAntwort += str(request.session["GOOGLEKI_%s" % session_id]) + "</span>"
    elif kityp == "IBM":
        farbigeAntwort += str(request.session["IBMKI_%s" % session_id]) + "</span>"

    elif kityp == "TARGET":
        farbigeAntwort = str(request.session["rawtargetsatz_%s" % session_id])

    else:
        raise Exception("KITYP NICHT GEFUNDEN.")

    return HttpResponse(farbigeAntwort)


def handler404(request, exception):
    return render(request, "../templates/404.html", status=404,)

def privacypolicy(request):
    return render(request, "../templates/privacy-policy.html")


def sources(request):
    return render(request, "../templates/sources.html")


def about(request):
    return render(request, "../templates/about.html")


def faq(request):
    return render(request, "../templates/faq.html")


def kontakt(request):
    return render(request, "../templates/kontakt.html")


def training(request):
        return render(request, "../templates/training.html")

def terms(request):
    return render(request, "../templates/terms.html")


def robots_txt(request):
    lines = [
        "User-Agent: *",
        "Disallow: /"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")