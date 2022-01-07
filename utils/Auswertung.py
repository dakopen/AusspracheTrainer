import re
from utils.VergleichFunktionen import einzelvergleich
import os
sigmatismus_counter = 0
rhotazismus_counter = 0
chitismus_counter = 0
schetismus_counter = 0


class Sprachfehler:
    # Laute, die Fehlerhaft werden sind Key; die Values repräsentieren, wonach es sich wahrscheinlich anhört
    SIGMATISMUS = {"ʃ": ["f"], "s": ["f"], "ç": ["f"], "z": ["f"]}  # Auch als Lispeln bekannt
    RHOTAZISMUS = {"ʀ": ["l"], "ɐ̯": ["l"], "r": ["l"]}
    CHITISMUS = {"ç": ["ʃ", "s", "z"]}
    SCHETISMUS = {"ʃ": ["s", "z", "ç"]}

    S = ["s", "z"]
    CH = ["ç"]
    SCH = ["ʃ"]

    # Weitere Sprachfehler einfügen

def auswertung(target_ipa, ipa_zuordnungen, predictions):
    global sigmatismus_counter, schetismus_counter, chitismus_counter, rhotazismus_counter
    """Vergleicht den Targetsatz mit den 3 Predictions. Je nach Qualität der Aussprache wird der Satz in folgenden
    Farben wieder ausgegeben:
    Grün (perfekt), Lila (leicht unverständlich), Gelb (unverständlich), Rot (sehr unverständlich)
    Außerdem wird die Aussprache auf Sprachfehler (zurzeit nur Sigmatimus (Lispeln)) überprüft.
    """
    predictions[2] = "".join([i for i in predictions[2] if i not in ["ˈ", "ˌ"]])
    scores_and_sequences1, matchings = einzelvergleich(target_ipa, predictions[0])
    scores_and_sequences2, matchings2 = einzelvergleich(target_ipa, predictions[1])
    scores_and_sequences3, matchings3 = einzelvergleich(target_ipa, predictions[2])

    score_per_character1 = score_zuordnung_per_character(scores_and_sequences1)
    score_per_character2 = score_zuordnung_per_character(scores_and_sequences2)
    score_per_character3 = score_zuordnung_per_character(scores_and_sequences3)




    overall_scores = {}
    for charindex in range(len(target_ipa)):
        if target_ipa[charindex] == " ":
            score_of_char = 1
        else:
            score_of_char = sum([score_per_character1[charindex], score_per_character2[charindex], score_per_character3[charindex]]) / 3
        overall_scores[charindex] = score_of_char

    average_score = sum(overall_scores.values())/len(overall_scores)
    zuvielscore = (minusscore(scores_and_sequences1) + minusscore(scores_and_sequences2) + minusscore(scores_and_sequences3)) / (len(overall_scores) * 3)
    # Jeder Buchstabe, der zu viel ist, wird abgezogen durch die Satzlänge (also prozentual)

    final_score = average_score - zuvielscore
    overall_scores_klartext, klartext = ipa_zuordnen(ipa_zuordnungen, overall_scores)
    sprachfehler_scores = sprachfehler_finden(overall_scores, target_ipa)

    return overall_scores_klartext, (final_score, average_score, zuvielscore), sprachfehler_scores


def score_zuordnung_per_character(scores_and_sequences):
    score_per_character = {}
    charindex = 0
    for value in scores_and_sequences.values():
        score = value[1]
        target_sequence = value[0][0]
        for i in range(len(target_sequence)):
            if target_sequence[i] == " " and value[0][1] in ["", " "]:
                score_per_character[charindex] = 1
            elif target_sequence == " ":  # ausschließlich ein Leerzeichen
                score_per_character[charindex] = 0
            else:
                score_per_character[charindex] = score
            charindex += 1

    return score_per_character


def minusscore(scores_and_sequences):
    zuviel = 0
    for value in scores_and_sequences.values():
        if value[0][0] == "" and value[0][1] not in [" ", ""]:
            zuviel += len(value[0][1])

    return zuviel


def ipa_zuordnen(zuordnungen, char_scores):
    """IPA wird in Klartext zurück umgeformt, allerdings werden die vorher für
    die Lautschrift errechneten Werte einbezogen.
    Input: Zuordnungsliste, Char_scores
    Output: Neue Char_scores für das Klartext_target (da andere Indexe), Klartext_target"""
    buchstaben_counter = 0
    new_char_scores = {}
    ipa_buchstaben_counter = 0
    for buchstabenpaar in zuordnungen:
        klartext = buchstabenpaar[0]
        ipa = buchstabenpaar[1]
        durchschitt = sum([char_scores[i+buchstaben_counter] for i in range(len(ipa))])/len(ipa)
        buchstaben_counter += len(ipa)
        for x in range(len(klartext)):
            new_char_scores[ipa_buchstaben_counter] = durchschitt
            ipa_buchstaben_counter += 1
    klartext_target = "".join([i[0] for i in zuordnungen])
    return new_char_scores, klartext_target


def sprachfehler_finden(overall_scores, target_ipa):
    s_scores = []
    ch_scores = []
    sch_scores = []
    for index, score in overall_scores.items():
        if target_ipa[index] in Sprachfehler.S:
            s_scores.append(score)
        elif target_ipa[index] in Sprachfehler.CH:
            ch_scores.append(score)
        elif target_ipa[index] in Sprachfehler.SCH:
            sch_scores.append(score)
    s_score = calculate_score(s_scores)
    ch_score = calculate_score(ch_scores)
    sch_score = calculate_score(sch_scores)
    return [s_score, ch_score, sch_score]


def calculate_score(scores):
    if len(scores) == 0:
        return 1
    return sum(scores)/len(scores)


def calculate_colour(score):
    if 0.85 < score:
        return "green"
    elif 0.65 < score:
        return "yellow-green"
    elif 0.45 < score:
        return "yellow"
    elif 0.25 < score:
        return "orange"
    else:
        return "red"


def adjektiv_fuer_score(score):
    if score > 0.95:
        return "exzellent"
    elif score > 0.90:
        return "sehr gut"
    elif score > 0.85:
        return "gut"
    elif score > 0.80:
        return "verständlich"
    elif score > 0.75:
        return "meistens verständlich"
    elif score > 0.70:
        return "oft verständlich"
    elif score > 0.65:
        return "manchmal schwierig verständlich"
    elif score > 0.60:
        return "oft schwierig verständlich"
    elif score > 0.55:
        return "sehr schwierig verständlich"
    elif score > 0.50:
        return "oft unverständlich"
    elif score > 0.40:
        return "meist unverständlich"
    else:
        return "unverständlich"


def sprachfehler_from_scores(sprachfehler_scores, gesamt_score):
    # gesamt_score ohne Abzug von zu viel
    additional_info = "&check; keine Sprachfehler gefunden!"

    sprachfehler = ["S: " + str(int(sprachfehler_scores[0] * 100)) + "% (Sigmatimus)", "CH: " + str(int(sprachfehler_scores[1] * 100)) + "% (Chitismus)", "SCH: " + str(int(sprachfehler_scores[2] * 100)) + "% (Schetismus)"]
    if min(sprachfehler_scores) < 0.7 and min(sprachfehler_scores) < gesamt_score*0.9:
        additional_info = "Übungen zur Verbesserung der Aussprache helfen Dir, den Sprachfehler zu beseitigen."
    if min(sprachfehler_scores) < 0.5 and min(sprachfehler_scores) < gesamt_score*0.7:
        additional_info += "\nAußerdem könnte eine logopädische Praxis behilflich sein."

        # Button einfügen --> Logopädische Praxis finden

    return [sprachfehler, additional_info]
