from difflib import SequenceMatcher
import panphon.distance

dst = panphon.distance.Distance()


def sort_values_dict(sequence_dict):
    """Sortiert ein Dictionary in einem Dictionary. Sofern Key im Dictionary einen kleineren Wert"""
    # {0: ['apg', 'apg'], 1: {0: ['t', 't'], -1: ['e', 'ɪl']}}
    # {0: ['apg', 'apg'], 1: {-1: ['e', 'ɪl'], 0: ['t', 't']}}
    for key, value in sequence_dict.items():
        if type(value) == dict:
            sequence_dict[key] = sort_values_dict(dict(sorted(value.items())))
    return sequence_dict


def dictionary_einschub(dictionary):
    """Durchsucht ein Dictionary nach Typ Dictionary Values und schiebt
     die Values des gefundenen Dictionaries an dieser Stelle ein."""
    inserted_values = 0
    dictionary_mit_einschub = {}
    # Key ist durchgängig, nicht verwechseln mit .items()
    for key, value in enumerate(dictionary.values()):
        if type(value) == dict:
            for value_in_sub_dict in value.values():
                dictionary_mit_einschub[str(int(key) + inserted_values)] = value_in_sub_dict
                inserted_values += 1
            inserted_values -= 1  # da nun auch ein "normaler" Dictionary Key ersetzt wird
        else:
            dictionary_mit_einschub[str(int(key) + inserted_values)] = value
    return dictionary_mit_einschub, inserted_values


def sort_dict(d):
    d = sort_values_dict(d)
    while True:
        d, _ = dictionary_einschub(d)
        if not any(type(value) == dict for value in d.values()):
            break
    return d


def sequence_matching(target, prediction, minus_i=-1, plus_i=1):
    """
    Matched immer den längsten Überschneidenden Teil des Targets mit der Prediction und ruft sich selbst für
    die übrig gebliebenen Teile auf:
    Bsp.: 'ich habe' und 'ich hatte' werden gematched:
    'ich ha':'ich ha',
    'b':'tt',
    'e':'e'
    """
    # Rekursive Funktion:
    match = SequenceMatcher(None, target, prediction).find_longest_match(0, len(target), 0, len(prediction))
    if match.size == 0:
        return "KEIN MATCH", {0: [target, prediction]}
    pre_match = [target[:match.a], prediction[:match.b]]
    aft_match = [target[match.a + match.size:], prediction[match.b + match.size:]]
    matchings = {0: [target[match.a: match.a + match.size], prediction[match.b: match.b + match.size]]}

    if pre_match[0] != "" and pre_match[1] != "":
        _, matchings[minus_i] = sequence_matching(pre_match[0], pre_match[1], minus_i, plus_i)
        minus_i -= 1
    else:
        if pre_match[0] != "" or pre_match[1] != "":
            matchings[minus_i] = pre_match
            minus_i -= 1
    if aft_match[0] != "" and aft_match[1] != "":
        _, matchings[plus_i] = sequence_matching(aft_match[0], aft_match[1], minus_i, plus_i)
        plus_i += 1
    else:
        if aft_match[0] != "" or aft_match[1] != "":
            matchings[plus_i] = aft_match
            plus_i += 1
    return match, dict(sorted(matchings.items()))


def einzelvergleich(target, prediction):
    """Vergleicht Targetsatz und Predictionsatz. Die Kernfunktion ist sequence_matching, welche jegliche
    Überschneidung und vergleichbaren Teile matched. Ausgegeben wird eine Fehlerliste (outdated), und mit Farben
    der Targetsatz und Predictionsatz angestrichen, wo Unterschiede sind."""
    fehler_liste = []
    prediction_output = ""
    target_output = ""
    scores_and_sequences = {}
    _, matchings = sequence_matching(target, prediction)
    sorted_sequence_dict = sort_dict(dict(sorted(matchings.items())))
    for index, value in enumerate(sorted_sequence_dict.values()):
        target_sequence = value[0]
        prediction_sequence = value[1]

        if target_sequence == prediction_sequence:
            score = 1

        elif target_sequence in ["", " "] and prediction_sequence in ["", " "]:
            score = 1

        elif target_sequence not in ["", " "] and prediction_sequence in ["", " "]:
            score = 0

        elif target_sequence in ["", " "] and prediction_sequence not in ["", " "]:
            score = 0

        else:
            # Ähnlichkeit der beiden phonetischen Sequencen miteinander vergleichen und in einer mathematischen
            # Funktion mappen, damit kleine Zahl = guter Score und hohe Zahl = schlechter score bedeuten
            score = calculate_score_from_distance(dst.hamming_feature_edit_distance(target_sequence, prediction_sequence))
        scores_and_sequences[index] = (value, score)
    return scores_and_sequences, sorted_sequence_dict


def calculate_score_from_distance(x):
    return 1 - (((5 * x / (5 * x + 0.66))) ** (2))






