import json
import re
import argparse
from pathlib import Path
from parse_ecli import pattern

def match_ecli(ecli_string):
    """Bestimmt, welche Klasse (=Gericht) auf den ECLI passt."""
# Reihenfolge der Überprüfung nach geschätzter Häufgikeit der Entscheidungen.
# Nutzt die in PEP572 eingeführten Assignment Expression, da für die Behandlung von REGEX
# besonders geeignet, vgl. https://www.python.org/dev/peps/pep-0572/#syntax-and-semantics

    ecli_string = ecli_string.upper().strip(' .:/()')

    if (match := re.match(pattern.laender_compiled, ecli_string)) is not None:
        decision = Decision_Other(ecli_string)
        decision.parse_ecli(match)
        return decision

    elif (match := re.match(pattern.bgh_compiled, ecli_string)) is not None:
        decision = Decision_BGH(ecli_string)
        decision.parse_ecli(match)
        return decision
    elif (match := re.match(pattern.bverfg_compiled, ecli_string)) is not None:
        decision = Decision_BVerfG(ecli_string)
        decision.parse_ecli(match)
        return decision

    elif (match := re.match(pattern.bverwg_compiled, ecli_string)) is not None:
        decision = Decision_BVerwG(ecli_string)
        decision.parse_ecli(match)
        return decision

    elif (match := re.match(pattern.bag_compiled, ecli_string)) is not None:
        decision = Decision_BAG(ecli_string)
        decision.parse_ecli(match)
        return decision

    elif (match := re.match(pattern.bsg_compiled, ecli_string)) is not None:
        decision = Decision_BSG(ecli_string)
        decision.parse_ecli(match)
        return decision

    elif (match := re.match(pattern.bfh_compiled, ecli_string)) is not None:
        decision = Decision_BFH(ecli_string)
        decision.parse_ecli(match)
        return decision

    elif (match := re.match(pattern.bpatg_compiled, ecli_string)) is not None:
        decision = Decision_BPatG(ecli_string)
        decision.parse_ecli(match)
        return decision

    else:
        # Hier werden die Fälle erfasst, in denen kein ECLI-Ausruck zu einem Treffer geführt hat.
        # Dabei wird nur für einfach überprüfbare Fälle der spezifische Grund angegeben.
        # In den jeweiligen Klassen gibt es teilweise eine genauere Fehlerbestimmung, sofern zwar das allgemeine
        # Schema noch erfolgreich war, aber z.B. im Aktenzeichen ungültige Kombinationen enthalten sind
        if not ecli_string.startswith("ECLI:DE:"):
            raise NoValidECLIError("ECLI ungültig: Beginnt nicht mit 'ECLI:DE:'")
        elif len(ecli_string) < 30:
            raise NoValidECLIError("ECLI ungültig: Eingabe zu kurz")
        elif invalid_characters := re.findall(r"[^A-Z\d\.:]", ecli_string):
            # Alle Zeichen außer A-Z, Ziffern und "." sowie ":" sind in einem ECLI nicht erlaubt.
             for c in invalid_characters:
                 report = " ".join(invalid_characters)
             raise NoValidECLIError(f"ECLI ungültig: Enthält ungültige Zeichen: {report}")
        else:
            raise NoValidECLIError("Kein gültiger ECLI!")


class Decision:
    """Grundklasse für alle Entscheidungstypen"""
    # Jedem ECLI sind verschiedene Typen von Entscheidungen zugeordnet, weil sich die
    # ECLI (z.B. für BGH oder Gerichte Länder) hinsichtlich des Informationsgehalts
    # und Aufbau unterscheiden. Diese Klasse stellt Grundfunktionalität für alle abgeleiteten
    # Klassen zur Verfügung
    def __init__(self, ecli_string):
        """Initialize ECLI"""
        self.ecli = ecli_string

        self.court_data = {
            # Diese Daten sollen mithilfe des ECLI aufgefüllt werden.
            # Nicht alle werden von allen Entscheidungstypen genutzt

            "court": ["Gericht: ",""],
            "bodytype": ["Spruchkörper: ",""],
            "date": ["Entscheidungsdatum: ",""],
            "az": ["Aktenzeichen: ",""],
            "collision": ["Kollisionsnummer: ",""],
            "year": ["Jahr: ",""],
            "decisiontype": ["Entscheidungsart: ",""], # Urteil, Beschluss...
            "decision_explain": ["Verfahren: ",""], # Erklärt das Registerzeichen (C, O, KLs...)
            "register_explain": ["Register/Zusatz: ",""], # Erklärt das ZUSATZregister bei manchen Az (Z.B. R in "B 14 AS 3/18 R")
            "url": ["Link: ",""], # Manche Gerichte bieten eine aus dem ECLI ableitbare Kurz-URl
        }
        filepath = Path(__file__).parent
        with open(filepath/'decisions.json', encoding='utf-8') as json_file:
            # In dieser Datei sind die Beschriftungen für die Entscheidungsarten, Registerzeichen etc. enthalten
            self.loaded_data = json.load(json_file)

    def check_collision(self, collision_num):
    # Die Kollisionsnummer ist bei manchen Az. (BVerfG) optional. Dann wird für die Ausgabe
    # "Keine" gesetzt. Bei der Gelegenheit kann im Übrigen auch gleich eine vorhandene Kollisionsnummer
    # auf Parallelentscheidungen geprüft werden.

        if collision_num is None:
            return "Keine"
        elif collision_num not in ["0", "00", "0A"]:
        # 0A ist laut Beschreibung des BfJ nicht vorgesehen, wird aber bei VGen und SGen vergeben.
            return collision_num + " (Es gibt mehrere Entscheidungen vom gleichen Datum unter diesem Az.!)"
        else:
            return collision_num

    def check_azpart_empty(self, azpart):
    # Bei manchen Gerichten sind Bestandteile des Az optional. Dann leerer String statt None.
    # Diese Variante statt (match|) in der Regex, da im Falle von BAG mit conditional genauere
    # Kontrolle möglich (vgl. pattern.bag)
        if azpart is not None:
            return azpart
        else:
            return ""

    def output_decision(self, rawmode=False, output_file=None):
        """Gibt alle aus dem ECLI ermittelten Werte beschriftet aus"""
        if not rawmode:
            print("\nFolgende Daten konnten extrahiert werden:\n---------------------------", file=output_file)
            print(self.ecli, file=output_file)
        elif rawmode:
            print(self.ecli.strip("\n")+";", end="", file=output_file)
        for eintrag in self.court_data.values():
            # In court_data sind jedem Eintrag eine Liste zugeordnet. Wenn das zweite Feld Werte
            # enthält, so wird der Eintrag ausgegeben
            if not rawmode:
                if eintrag[1] != "" and eintrag[1] is not None:
                    self.pretty_print(eintrag[0],eintrag[1], output_file)
            elif rawmode:
                if eintrag[1] != "" and eintrag[1] is not None:
                    print(eintrag[1]+";", end="", file=output_file)
        if rawmode:
            print("", file=output_file)

    def pretty_print(self, label, value, output_file=None):
        """Rückt Beschriftung und Wert korrekt ein"""
        value = value.lstrip()
        print("{:35} {:20}".format(label, value), file=output_file)


##################
# BUNDESGERICHTE
##################

class Decision_BVerfG(Decision):
    def check_body_bverfg(self, match):
        # Bestimmt den Wert für bodytype
        if match.group("bodytype") == "K":
            return "Kammerentscheidung" + f" ({match.group('azbody')}. Senat)"
        elif match.group("bodytype") == "S":
            return "Senatsentscheidung" + f" ({match.group('azbody')}. Senat)"
        elif match.group("type") == "VB":
        # Hier matchgroup type statt bodytype, da letzterer bei type == VB nicht vorhanden
            return "Beschwerdekammer"
        elif match.group("type") == "UP":
            if match.group("azbody") is not None:
                return "Plenum" + f" (Vorlagesenat: {match.group('azbody')}. Senat)"
            else:
                return "Plenum"
        else:
            raise InValidAZError("Aktenzeichen im ECLI ungültig: Spruchkörperangabe fehlt!")

    def generate_url(self, ecli_string):
        # Das BVerfG verfügt über Kurz-URL, die auf dem ECLI aufbauen
        url = "http://www.bverfg.de/e/" + ecli_string[20:].lower().replace(".", "_") + ".html"
        return url

    def parse_ecli(self, match):
        """Füllt die Daten für BVerfG-Entscheidungen auf Grundlage des ECLI aus"""
        self.court_data["court"][1] = "BVerfG" # Dies steht fest, da sonst kein Regex-Match
        self.court_data["decisiontype"][1] = self.loaded_data["bverfg_decisiontype"][match.group("type")]
        self.court_data["bodytype"][1] = self.check_body_bverfg(match)
        self.court_data["date"][1] = match.group("date")[6:8] + "." + match.group("date")[4:6] + "." + match.group("year")
        self.court_data["collision"][1] = super().check_collision(match.group("collision"))
        self.court_data["url"][1] = self.generate_url(self.ecli)

        azbody = super().check_azpart_empty(match.group("azbody"))

        # Bei Verzögerungsbeschwerden gibt es Aktenzeichen wie Vz 10/16,
        # also ohne Spruchkörper. Hier einfacher zu behandeln als in Regex:
        if azbody == "":
            if (match.group("type") == "VB" and match.group("azreg") == "VZ") or (match.group("type") == "UP" and match.group("azreg") == "PBVU"):
                self.court_data["az"][1] = (self.loaded_data["bverfg_az"][match.group("azreg")]
                                                + " " + match.group("aznumber").lstrip("0") + "/" + match.group("azyear"))
            else:
                raise InValidAZError("Aktenzeichen im ECLI ungültig: Senatsbezeichnung fehlt, obwohl kein Verzögerungs- oder Plenarverfahren!")
        else:
            try:
                self.court_data["az"][1] = (match.group("azbody") + " " + self.loaded_data["bverfg_az"][match.group("azreg")]
                                                + " " + match.group("aznumber").lstrip("0") + "/" + match.group("azyear"))
            except KeyError as e:
                raise InValidAZError(f"Ungültiges Registerzeichen: {match.group('azreg')}") from e

##################

class Decision_BGH(Decision):
    def determine_body(self, azbody, azreg):
        if azbody != "":
            if re.match(r"\d", azbody) and "BG" not in azreg:
                return azbody + ". Strafsenat"
            elif re.match("[IVX]", azbody):
                return azbody + ". Zivilsenat"

        if "BG" in azreg:
            return "Ermittlungsrichter"
        elif azreg in ["KART", "ENVR", "KVR", "KZR", "KVZ"]:
            return "Kartellsenat"
        elif "ANWST" in azreg:
            return "Senat für Anwaltssachen"
        elif "NOT" in azreg:
            return "Senat für Notarsachen"
        elif "RI" in azreg:
            return "Dienstgericht des Bundes"
        elif "LW" in azreg:
            return "Senat für Landwirtschaftssachen"
        else:
            return azbody

    def parse_ecli(self, match):

        self.court_data["court"][1] = "BGH"
        self.court_data["decisiontype"][1] = self.loaded_data["bgh_decisiontype"][match.group("type")]
        self.court_data["date"][1] = match.group("date")[0:2] + "." + match.group("date")[2:4] + "." + match.group("year")
        self.court_data["collision"][1] = super().check_collision(match.group("collision"))
        azbody = super().check_azpart_empty(match.group("azbody"))
        self.court_data["bodytype"][1] = self.determine_body(azbody, match.group("azreg"))

        try:
            if azbody != "":
                self.court_data["az"][1] = (azbody + " " + self.loaded_data["bgh_az"][match.group("azreg")]
                                                + " " + match.group("aznumber").lstrip("0") + "/" + match.group("azyear"))
            else:
                self.court_data["az"][1] = (self.loaded_data["bgh_az"][match.group("azreg")]
                                                + " " + match.group("aznumber").lstrip("0") + "/" + match.group("azyear"))
            self.court_data["decision_explain"][1] = self.loaded_data["bgh_explain"][match.group("azreg")]
        except KeyError as e:
            raise InValidAZError(f"Ungültiges Registerzeichen: {match.group('azreg')}") from e


class Decision_BVerwG(Decision):
    def generate_url(self, ecli_string):
        # Das BVerwG verfügt über Kurz-URL, die auf dem ECLI aufbauen
        url = "https://www.bverwg.de/de/" + ecli_string[20:]
        return url

    def determine_body(self, azbody, azreg):

        if "W" in azreg:
            return azbody + ". Wehrdienstsenat"
        elif azreg in ["D", "DB"]:
            if int(azbody) > 1:
                return azbody + ". Disziplinarsenat"
            else:
                return "Disziplinarsenat"
        elif azreg == "F":
            return "Fachsenat nach § 189 VwGO"
        else:
            return azbody + ". Senat"

    def parse_ecli(self, match):

        self.court_data["court"][1] = "BVerwG"
        self.court_data["decisiontype"][1] = self.loaded_data["bverwg_decisiontype"][match.group("type")]
        self.court_data["date"][1] = match.group("date")[0:2] + "." + match.group("date")[2:4] + "." + match.group("year")
        self.court_data["collision"][1] = super().check_collision(match.group("collision"))
        try:
            self.court_data["az"][1] = (match.group("azbody") + " " + self.loaded_data["bverwg_az"][match.group("azreg")]
                                            + " " + match.group("aznumber").lstrip("0") + "." + match.group("azyear"))
            self.court_data["decision_explain"][1] = self.loaded_data["bverwg_explain"][match.group("azreg")]
        except KeyError as e:
            raise InValidAZError(f"Ungültiges Registerzeichen: {match.group('azreg')}") from e
        self.court_data["url"][1] = self.generate_url(self.ecli)
        self.court_data["bodytype"][1] = self.determine_body(match.group("azbody"), match.group("azreg"))

class Decision_BFH(Decision):
    def determine_body(self, azbody, azreg):

        if azreg == "GRS":
            return "Großer Senat"
        else:
            return azbody + ". Senat"


    def parse_ecli(self, match):

        self.court_data["court"][1] = "BFH"
        self.court_data["decisiontype"][1] = self.loaded_data["bfh_decisiontype"][match.group("type")]
        self.court_data["date"][1] = match.group("date")[0:2] + "." + match.group("date")[2:4] + "." + match.group("year")
        self.court_data["collision"][1] = super().check_collision(match.group("collision"))
        azbody = super().check_azpart_empty(match.group("azbody"))
        self.court_data["bodytype"][1] = self.determine_body(azbody, match.group("azreg"))
        self.court_data["az"][1] = (azbody + " " + match.group("azreg")
                                        + " " + match.group("aznumber").lstrip("0") + "/" + match.group("azyear"))
        self.court_data["decision_explain"][1] = self.loaded_data["bfh_explain"][match.group("azreg")]

class Decision_BPatG(Decision):
    def parse_ecli(self, match):

        self.court_data["court"][1] = "BPatG"
        self.court_data["decisiontype"][1] = self.loaded_data["bpatg_decisiontype"][match.group("type")]
        self.court_data["date"][1] = match.group("date")[0:2] + "." + match.group("date")[2:4] + "." + match.group("year")
        self.court_data["collision"][1] = super().check_collision(match.group("collision"))
        suffix = super().check_azpart_empty(match.group("azsuffix"))
        if suffix != '':
            suffix = " (" + suffix + ")"
        self.court_data["az"][1] = (match.group("azbody") + " " + self.loaded_data["bpatg_az"][match.group("azreg")]
                                        + " " + match.group("aznumber").lstrip("0") + "/" + match.group("azyear") + suffix)
        self.court_data["decision_explain"][1] = self.loaded_data["bpatg_explain"][match.group("azreg")]

class Decision_BAG(Decision):
    def parse_ecli(self, match):

        self.court_data["court"][1] = "BAG"
        # Hier kann auf BVerwG zurückgegriffen werden, da Schnittmenge identisch
        self.court_data["decisiontype"][1] = self.loaded_data["bverwg_decisiontype"][match.group("type")]
        self.court_data["date"][1] = match.group("date")[0:2] + "." + match.group("date")[2:4] + "." + match.group("year")
        self.court_data["collision"][1] = super().check_collision(match.group("collision"))
        azbody = super().check_azpart_empty(match.group("azbody"))
        self.court_data["az"][1] = (azbody + " " + match.group("azreg")
                                        + " " + match.group("aznumber").lstrip("0") + "/" + match.group("azyear"))
        self.court_data["decision_explain"][1] = self.loaded_data["bag_explain"][match.group("azreg")]

class Decision_BSG(Decision):
    def parse_ecli(self, match):

        self.court_data["court"][1] = "BSG"
        self.court_data["decisiontype"][1] = self.loaded_data["bpatg_decisiontype"][match.group("type")]
        self.court_data["date"][1] = match.group("date")[0:2] + "." + match.group("date")[2:4] + "." + match.group("year")
        self.court_data["collision"][1] = super().check_collision(match.group("collision"))
        azinstance = super().check_azpart_empty(match.group("azinstance"))
        if azinstance == '':
            if match.group("azbody") != "GS":
                # Az beim BSG beginnen immer mit "B", vgl. https://www.bsg.bund.de/DE/Verfahren/Aktenzeichen/aktenzeichen_node.html
                # Anders aber, wenn der Große Senat entscheidet: ECLI:DE:BSG:2019:200219BGS1180
                raise InValidAZError("Kein führendes B im Aktenzeichen (nur bei GS-Verfahren zulässig!)")

        azreg = super().check_azpart_empty(match.group("azreg"))
        if azreg == '':
            if match.group("azbody") != "GS":
                raise InValidAZError("Kein Sachgebiet im Aktenzeichen (nur bei GS-Verfahren zulässig!)")
            else:
                self.court_data["decision_explain"][1] = "Großer Senat"
        else:
            self.court_data["decision_explain"][1] = self.loaded_data["bsg_explain"][match.group("azreg")]

        azregister = super().check_azpart_empty(match.group("azregister"))
        if azregister == '':
            if match.group("azbody") != "GS":
                # Wiederum sind GS Verfahren die Ausnahme, sonst immer Register vorhanden
                raise InValidAZError("Kein Register im Aktenzeichen (nur bei GS-Verfahren zulässig!)")
        else:
            self.court_data["register_explain"][1] = self.loaded_data["bsg_register_explain"][match.group("azregister")]

        self.court_data["az"][1] = (azinstance + " " + match.group("azbody") + " " + azreg + " "
                                        + match.group("aznumber").lstrip("0") + "/" + match.group("azyear") + " " + azregister).strip()



class Decision_Other(Decision):
    """Für Entscheidungen aller Gerichtsbarkeiten der Länder"""
    def __init__(self, ecli_string):
        super().__init__(ecli_string)
        # Die Liste mit Gerichtsnamen ist nur für die Gerichte der Länder erforderlich
        filepath = Path(__file__).parent
        with open(filepath/'gerichte.json', encoding='utf-8') as json_file:
            self.court_names = json.load(json_file)

    def valid_court(self, match):
        if match.group("court") not in self.court_names:
            raise InValidCourtError("Kein gültiger ECLI: Ungültiger Gerichtscode")


    def determine_jurisdiction(self, match):
        # Die verschiedenen Gerichtsbarkeiten bilden ihre Az. unterschiedlich und verwenden
        # die gleichen Registerzeichen mit unterschiedlicher Bedeutung. Deshalb wird hier überprüft,
        # welche Gerichtsbarkeit vorliegt.
        if re.match(pattern.ordentliche, match.group("court"), flags=re.VERBOSE):
            return "o"
        elif re.match(pattern.sozg, match.group("court"), flags=re.VERBOSE):
            return "s"
        elif re.match(pattern.arbg, match.group("court"), flags=re.VERBOSE):
            return "a"
        elif re.match(pattern.verwg, match.group("court"), flags=re.VERBOSE):
            if match.group("court") in ["VKANSBA", "VKMUENC", "VGANSBA", "VGAUGSB", "VGBAYRE", "VGMUENC", "VGREGEN", "VGWUERZ"]:
                return "vbay"
            else:
                return "v"
        elif match.group("court").startswith("FG"):
            return "f"

    def parse_ecli_az_sozg(self, match):
        if az_match := re.match(pattern.sozg_az, match.group("az"), flags=re.VERBOSE):
            azregister = super().check_azpart_empty(az_match.group("azregister"))
            azer = super().check_azpart_empty(az_match.group("azer"))
            az = (az_match.group("azinstance") + " " + az_match.group("azbody") + " " + az_match.group("azreg")
                    + " " + az_match.group("aznumber").lstrip("0") + "/" + az_match.group("azyear") + " " + azregister + " " + azer).strip()
            decision_explain = self.loaded_data["sozg_explain"][az_match.group("azreg")]
            return az.rstrip(), decision_explain
        else:
            raise InValidAZError("Ungültiges Aktenzeichen!")

    def parse_ecli_az_arbg(self, match):
        if az_match := re.match(pattern.arbg_az, match.group("az"), flags=re.VERBOSE):
            az = (az_match.group("azbody") + " " + self.loaded_data["arbg_az"][az_match.group("azreg")]
                    + " " + az_match.group("aznumber").lstrip("0") + "/" + az_match.group("azyear")).strip()
            decision_explain = self.loaded_data["arbg_explain"][az_match.group("azreg")]
            return az, decision_explain
        else:
            raise InValidAZError("Ungültiges Aktenzeichen!")

    def parse_ecli_az_ordentliche(self, match):
        if az_match := re.match(pattern.ordentliche_az, match.group("az"), flags=re.VERBOSE):
            azprefix = super().check_azpart_empty(az_match.group("azprefix"))
            azbody = super().check_azpart_empty(az_match.group("azbody"))
            azbody_sta = super().check_azpart_empty(az_match.group("azbody_sta"))
            azreg_sta = super().check_azpart_empty(az_match.group("azreg_sta"))
            if azreg_sta != '':
                azreg_sta = self.loaded_data["ordentliche_az"][azreg_sta]
            azsuffix = super().check_azpart_empty(az_match.group("azsuffix"))

            az = (azprefix + " " + azbody + " " + self.loaded_data["ordentliche_az"][az_match.group("azreg").replace(".","")]
                    + " " + azbody_sta + " " + azreg_sta + " "  + az_match.group("aznumber").lstrip("0") + "/" + az_match.group("azyear")
                    + " " + azsuffix).strip() # Strip bezieht sich auf den gesamten String, der az zugewiesen wird!
            az = re.sub(r"\s\s+" , " ", az)
            decision_explain = self.loaded_data["ordentliche_explain"][az_match.group("azreg").replace(".","")]
            return az, decision_explain
        else:
            raise InValidAZError("Ungültiges Aktenzeichen!")


    def parse_ecli_az_verwg(self, match):
        decision_explain = ''
        if az_match := re.match(pattern.verwg_az, match.group("az"), flags=re.VERBOSE):
            azregister = super().check_azpart_empty(az_match.group("azregister"))
            if azregister != '':
                azregister = "." + azregister
                decision_explain = self.loaded_data["verwg_register_explain"][az_match.group("azregister")]
            azhessen = super().check_azpart_empty(az_match.group("azhessen"))
            # In Hessen steht wird den Az. eine Kurzbezeichnung des Gericht angefügt,
            # z.B. KS für VG Kassel: ECLI:DE:VGKASSE:2020:0406.3L348.20.KS.00
            if azhessen != '':
                azhessen = "." + azhessen
            azprefix =super().check_azpart_empty(az_match.group("azprefix"))
            if azprefix != '':
                azprefix = azprefix + " "
            az = (azprefix + az_match.group("azbody") + " " + az_match.group("azreg") + " "
                    + az_match.group("aznumber").lstrip("0") + "/" + az_match.group("azyear") + azhessen + azregister).strip()
            if az_match.group("azreg") in self.loaded_data["verwg_explain"]:
                decisiontype = self.loaded_data["verwg_explain"][az_match.group("azreg")]
            else:
                decisiontype = "Unbekanntes Registerzeichen!"
            return az, decision_explain, decisiontype
        else:
            raise InValidAZError("Ungültiges Aktenzeichen!")

    def parse_ecli_az_verwg_bayern(self, match):
        # Bayerische Az der Verwaltungsgerichte weichen vom üblichen Schema ab und haben daher eine eigene Funktion
        decision_explain = ''
        if az_match := re.match(pattern.verwg_az_bayern, match.group("az"), flags=re.VERBOSE):
            azregister = super().check_azpart_empty(az_match.group("azregister"))
            if azregister != '':
                azregister = "." + azregister
                decision_explain = self.loaded_data["verwg_register_explain"][az_match.group("azregister")]
            az = (az_match.group("azbayern") + " " + az_match.group("azbody") + " " + az_match.group("azreg")
                    + " " + az_match.group("azyear") + "." + az_match.group("aznumber") + azregister).strip()
            if az_match.group("azreg") in self.loaded_data["verwg_explain"]:
                decisiontype = self.loaded_data["verwg_explain"][az_match.group("azreg")]
            else:
                # Dies bedeutet im Zweifel keinen ungültigen ECLI, deshalb keine Exception, sondern nur
                # Information
                decisiontype = "Unbekanntes Registerzeichen!"
            return az, decision_explain, decisiontype
        else:
            raise InValidAZError("Ungültiges Aktenzeichen!")

    def parse_ecli_az_fg(self, match):
        decision_explain = ''
        if az_match := re.match(pattern.fg_az, match.group("az"), flags=re.VERBOSE):
            azregister = super().check_azpart_empty(az_match.group("azregister"))
            az = (az_match.group("azbody") + " " + az_match.group("azreg") + " " + az_match.group("aznumber").lstrip("0") + "/"
                    + az_match.group("azyear") + " " +azregister.replace(".",", ")).strip()
            if az_match.group("azreg") in self.loaded_data["fg_explain"]:
                decisiontype = self.loaded_data["fg_explain"][az_match.group("azreg")]
            else:
                decisiontype = "Unbekanntes Registerzeichen!"
            return az, decision_explain, decisiontype
        else:
            raise InValidAZError(f"Ungültiges Aktenzeichen!: {match.group('az')}")

    def parse_ecli(self, match):
        self.valid_court(match)
        self.court_data["court"][1] = self.court_names[match.group("court")]
        self.court_data["date"][1] = match.group("date")[2:4] + "." + match.group("date")[0:2] + "." + match.group("year")
        self.court_data["collision"][1] = super().check_collision(match.group("collision"))

        self.court_data["az"][0] = "Aktenzeichen (max. 17 Stellen): "
        # Die Az können gerade bei Doppelaktenzeichen zu lang sein, um vollständig im ECLI
        # erfasst zu werden.
        jurisdiction = self.determine_jurisdiction(match)
        # Das Aktenzeichen wird für jede Gerichtsbarkeit anders gebildet, also zunächst bestimmen, welche hier vorliegt.
        if jurisdiction == "o":
            self.court_data["az"][1], self.court_data["decision_explain"][1] = self.parse_ecli_az_ordentliche(match)
        elif jurisdiction == "s":
            self.court_data["az"][1], self.court_data["decision_explain"][1] = self.parse_ecli_az_sozg(match)
        elif jurisdiction == "a":
            self.court_data["az"][1], self.court_data["decision_explain"][1] = self.parse_ecli_az_arbg(match)
        elif jurisdiction == "v":
            self.court_data["az"][1], self.court_data["decision_explain"][1], self.court_data["decisiontype"][1]\
             = self.parse_ecli_az_verwg(match)
        elif jurisdiction == "vbay":
            self.court_data["az"][1], self.court_data["decision_explain"][1], self.court_data["decisiontype"][1]\
             = self.parse_ecli_az_verwg_bayern(match)
        elif jurisdiction == "f":
            self.court_data["az"][1], self.court_data["decision_explain"][1], self.court_data["decisiontype"][1]\
             = self.parse_ecli_az_fg(match)
        else:
            self.court_data["az"][1] = match.group("az")


class NoECLIError(Exception):
    pass

class NoValidECLIError(Exception):
    pass

class InValidCourtError(Exception):
    pass

class InValidAZError(Exception):
    pass


##################
# Hauptprogramm
##################


##################


def exception_print(e):
    print("\n\n####################################################\n#\n#\n# FEHLER:\t", end='')
    print(e)
    print("#\n#\n####################################################\n\n")


def main_func():
    # Der folgende Abschnitt dient zur Erfassung der Eingabe über die Kommandozeile
    # Da bei Angabe einer Datei mit der Option -i ein ECLI in der Kommandozeile entbehrlich ist,
    # muss in zwei Schritten vorgegangen werden. Anderenfalls wird das Argument "ecli" immer verlangt
    # (positional argument)
    parser = argparse.ArgumentParser(description='Analyse von deutschen ECLI')
    (parser.add_argument('-i', '--input', dest='input_file',
                        help='Angabe einer Datei mit ECLI. Zeilen, die nicht mit ECLI:DE: beginnen, werden ignoriert.'))
    (parser.add_argument('-o', '--output', dest='output_file',
                        help='Angabe einer Datei, in welche die Ausgabe geschrieben werden soll. Erzeugt mit -r eine .csv'))
    (parser.add_argument('-r', '--raw', action='store_true',
                        help='Ausgabe der analysierten Bestandteile ohne weitere Beschriftung, durch Semikolon getrennt'))
    (parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.9.2'))                        
    args, args2 = parser.parse_known_args()

    ecli_list = []

    if args.input_file is not None:
        # Falls mit -i eine Datei angegeben wurde:
        ecli_file_string = Path(args.input_file)
        try:
            with open(ecli_file_string) as input:
                lines = input.readlines()
                for line in lines:
                    # Alle Zeilen, die nicht mit ECLI:DE: beginnen, werden ignoriert.
                    if line.upper().startswith("ECLI:DE:"):
                        ecli_list.append(line)
        except FileNotFoundError:
            print(f"Datei {ecli_file_string} existiert nicht!")
    else:
        parser2 = argparse.ArgumentParser()
        parser2.add_argument('ecli', metavar='ECLI', help='Der zu überprüfende ECLI')
        # Ansonsten einzelnen ECLI direkt von der Kommandozeile
        args2 = parser2.parse_args(args2)
        ecli_string = args2.ecli.upper().strip(' .:/()')
        ecli_list.append(ecli_string)


    if len(ecli_list) == 0:
        print("Keine ECLI gefunden!")
    else:
        for ecli_string in ecli_list:
            try:
                my_decision = match_ecli(ecli_string)
                if args.output_file is not None:
                    output_file_string = Path(args.output_file)
                    if output_file_string.exists():
                        print()
                        overwrite = input(f"Datei {output_file_string} existiert bereits. Überschreiben? (j/n)\n")
                        if overwrite.lower() == 'j':
                            with open(args.output_file, mode="w", encoding="utf-8") as f:
                                my_decision.output_decision(args.raw, f)
                    else:
                        with open(args.output_file, mode="w", encoding="utf-8") as f:
                                my_decision.output_decision(args.raw, f)
                else:
                    my_decision.output_decision(args.raw)
            except (NoValidECLIError, InValidAZError, InValidCourtError) as e:
                exception_print(e)
