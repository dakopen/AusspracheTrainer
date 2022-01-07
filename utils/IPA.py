"""Nimmt einen Satz als Input und gibt einen Satz im phonetischen Alphabet als Output aus"""
import requests
import itertools

class IPA:
    @staticmethod
    def send_to_gramophone(wort, retry=0):
        wort = str(wort).lower()  # Großbuchstaben versteht Gramophone nicht
        response = requests.get("https://kaskade.dwds.de/~kmw/gramophone.py?q=%s" % wort)  # Max Länge = 25 Buchstaben
        if response.status_code == 200:
            response = str(response.text)
            response_index_left = response.find("<tr><td>Segmented Transcription</td><td><tt>")
            if response_index_left != -1:
                response_lstrip = response[response_index_left + 44:]
            else:
                response_lstrip = ""

            response_index_right = response_lstrip.find("</tt></td></tr>")
            if response_index_right != -1:
                response = response_lstrip[:response_index_right]
            else:
                response = ""

            if response:
                response_split = response.split()
                ipa_buchstaben = []

                for buchstabenpaar in response_split:
                    try:
                        klartext = buchstabenpaar.split(",")[0]
                        ipa = buchstabenpaar.split(",")[1]
                        ipa_buchstaben.append([klartext, ipa])
                    except:
                        break
            else:
                # Irgendetwas ist schief gelaufen: DEBUGGEN!!
                raise Exception("KEINE GÜLTIGE ANTWORT VON GRAMOPHONE", wort, retry)

            ipa_ganzes_wort = "".join([i[1] for i in ipa_buchstaben])
            return ipa_ganzes_wort, ipa_buchstaben
        else:
            if retry < 5:
                IPA.send_to_gramophone(wort=wort, retry=retry + 1)
            raise ConnectionError("Keine gültige Antwort")





    @staticmethod
    def zahl_zu_text_sortieren(textliste):
        """Überpürft Wort für Wort, ob es sich um eine Zahl handelt. Ist dass der Fall, wird sie in Text umgeformt."""
        # text = Liste
        for i in range(len(textliste)):
            if textliste[i].isnumeric():
                wort = IPA.zahl_zu_text(textliste[i])
                textliste[i] = wort
        return textliste

    @staticmethod
    def zahl_zu_text(eingabe_zahl):  # Für Zahlen von 0-1.000.000
        """Substituiert eine Zahl mit dem alphabetischen Equivalent: 95 zu fünfundneunzig"""
        eingabe_zahl = int(eingabe_zahl)
        if eingabe_zahl == 0:
            return "Null"
        dictionary = {1000000: 'million', 1000: 'tausend', 100: 'hundert', 90: 'neunzig', 80: 'achtzig', 70: 'siebzig',
                      60: 'sechzig',
                      50: 'fünfzig', 40: 'vierzig', 30: 'dreißig', 20: 'zwanzig', 19: 'neunzehn', 18: 'achtzehn',
                      17: 'siebzehn', 16: 'sechzehn', 15: 'fünfzehn', 14: 'vierzehn', 13: 'dreizehn', 12: 'zwölf',
                      11: 'elf', 10: 'zehn', 9: 'neun', 8: 'acht', 7: 'sieben', 6: 'sechs', 5: 'fünf', 4: 'vier',
                      3: 'drei',
                      2: 'zwei', 1: 'ein'}
        zusammenrechnen = {1000000: 0, 1000: 0, 100: 0, 90: 0, 80: 0, 70: 0, 60: 0, 50: 0, 40: 0, 30: 0, 20: 0, 19: 0,
                           18: 0, 17: 0,
                           16: 0, 15: 0, 14: 0, 13: 0, 12: 0, 11: 0, 10: 0, 9: 0, 8: 0, 7: 0, 6: 0, 5: 0, 4: 0, 3: 0,
                           2: 0,
                           1: 0}
        while eingabe_zahl > 0:
            for zahl in dictionary.keys():
                if eingabe_zahl - zahl >= 0:
                    zusammenrechnen[zahl] = 1 + zusammenrechnen[zahl]
                    eingabe_zahl -= zahl
                    break
        wortbruch_liste = []  # Wortbruch im Sinne von Bruchteil des gesamten Wortes
        for key, value in zusammenrechnen.items():
            if value not in dictionary.keys() and value > 1:
                value_for_dict = IPA.zahl_zu_text(value)  # z.B. 102 000, 102 wird erstmal zu hundertundzwei umgeformt
                dictionary[value] = value_for_dict

            if value > 1 or value == 1 and key >= 100:
                wortbruch = str(dictionary[value]) + str(dictionary[key])
                zusammenrechnen[key] = 0
                wortbruch_liste.append(wortbruch)
            elif value == 1:
                wortbruch = str(dictionary[key])
                wortbruch_liste.append(wortbruch)
                zusammenrechnen[key] = 0

        wortbruch_array = []
        if len(wortbruch_liste) > 1:
            for wortbruch in wortbruch_liste:
                appending = True
                for key, value in dictionary.items():
                    if str(wortbruch) == str(value) and int(key) < 10:
                        if not wortbruch_array[-1].endswith(('hundert', 'tausend', 'million')):
                            wortbruch_array.insert(-1, value + "und")
                            appending = False
                            break
                if appending:
                    wortbruch_array.append(wortbruch)
        else:
            wortbruch_array = wortbruch_liste
        x = "".join(str(e) for e in wortbruch_array)
        return x

    @staticmethod
    def transform_abbreviations(textliste):
        zusatz_i = 0
        new_text_list = [""] * 2 * len(textliste)
        for i in range(len(textliste)):
            if not textliste[i].isalpha():
                if textliste[i].endswith("cm"):
                    new_text_list[i + zusatz_i] = textliste[i + zusatz_i][:-2]
                    zusatz_i += 1
                    new_text_list[i + zusatz_i] = "centimeter"

                elif textliste[i].endswith("km"):
                    new_text_list[i + zusatz_i] = textliste[i + zusatz_i][:-1]
                    zusatz_i += 1
                    new_text_list[i + zusatz_i] = "kilometer"

                elif textliste[i].endswith("mm"):
                    new_text_list[i + zusatz_i] = textliste[i + zusatz_i][:-1]
                    zusatz_i += 1
                    new_text_list[i + zusatz_i] = "millimeter"

                elif textliste[i].endswith("m"):
                    new_text_list[i + zusatz_i] = textliste[i + zusatz_i][:-1]
                    zusatz_i += 1
                    new_text_list[i + zusatz_i] = "meter"

            else:
                new_text_list[i + zusatz_i] = textliste[i]

        while '' in new_text_list:
            new_text_list.remove('')
        return new_text_list

    @staticmethod
    def text_zu_IPA(textliste):
        IPA_satz = []
        IPA_zuordnungen = []
        for wort in textliste:
            if wort == "":
                IPA_satz.append("")
                IPA_zuordnungen.append([[""],[""]])
                continue

            else:
                ipa_wort, ipa_zuordnung = IPA.send_to_gramophone(wort=wort)
                IPA_satz.append(ipa_wort)
                IPA_zuordnungen.append(ipa_zuordnung)
            IPA_satz.append(" ")
            IPA_zuordnungen.append([[" ", " "]])

        # Das Leerzeichen am Ende löschen
        del IPA_satz[-1]
        del IPA_zuordnungen[-1]


        return "".join(itertools.chain.from_iterable(IPA_satz)), list(itertools.chain.from_iterable(IPA_zuordnungen))

    @staticmethod
    def text_preparation(text):
        textliste = str(text).split()
        textliste = IPA.transform_abbreviations(textliste)
        textliste = IPA.zahl_zu_text_sortieren(textliste)
        return textliste
