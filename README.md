# parse_ecli
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-360/)

Dieses Programm dient der Aufschlüsselung von deutschen ECLI wie `ECLI:DE:BVERFG:2020:RK20200501.1BVR099620`.

**Python 3.8** ist zwingend erforderlich.

## Bedienung

```
python parse_ecli.py <ECLI>
```
Der ECLI muss vollständig eingegeben werden. Führende Leerzeichen und Sonderzeichen werden entfernt.

Optional:

```
python parse_ecli.py -r
```
für rawmode, d.h. die Daten werden ohne Beschriftung nur durch Semikolon getrennt ausgegeben.

```
python parse_ecli.py -i input_file
python parse_ecli.py -o output_file

```
ECLI können auch aus einer Textdatei eingelesen werden, die mit `-i` angegeben wird. Dabei wird zeilenweise ein ECLI pro Zeile erfasst, die Zeilen dürfen keine anderen Daten enthalten. Zeilen, die nicht mit `ECLI:DE:` beginnen, werden ignoriert.
Die Ausgabe kann auch in eine Datei umgeleitet werden, die mit `-o` angegeben wird.

## Überblick

Der Europäische Urteilsidentifikator (European Case Law Identifier – ECLI) wurde entwickelt, um die korrekte und eindeutige Angabe von Fundstellen in Entscheidungen europäischer und nationaler Gerichte zu erleichtern.
Der ECLI ist ein einheitlicher Identifikator, der für alle Gerichte der Mitgliedstaaten und der EU dasselbe erkennbare Format besitzt. Informationen zum ECLI in Deutschland werden vom Bundesamt für Justiz als [ECLI-Koordinator](https://e-justice.europa.eu/content_european_case_law_identifier_ecli-175-de-de.do?member=1) für Deutschland bereitgestellt.

Wird ein ECLI an `parse_ecli` übergeben, wird er nach seinen Bestandteilen aufgeschlüsselt und so weit wie möglich erläutert.

So werden aus dem ECLI `ECLI:DE:AGK:2007:1120.217C180.07.00` folgende Daten ausgegeben:

Feld|Wert
---|---
Gericht:|Amtsgericht Köln
Entscheidungsdatum:|20.11.2007
Aktenzeichen (max. 17 Stellen):|217 C 180/07
Kollisionsnummer:|00
Verfahren:|Erstinstanzliche Zivilprozesse

Je nach Gerichtsbarkeit unterscheidet sich die Datendichte des ECLI. So kann aus `ECLI:DE:BVERWG:2019:170719B3BN2.18.0` folgendes extrahiert werden:

Feld|Wert
---|---
Gericht|BVerwG
Spruchkörper|3. Senat
Entscheidungsdatum|17.07.2019
Aktenzeichen (max. 17 Stellen)|3 BN 2.18
Kollisionsnummer|0
Entscheidungsart|Beschluss
Verfahren|Nichtzulassungsbeschwerden in Normenkontrollverfahren
Link|https://www.bverwg.de/de/170719B3BN2.18.0

Im rawmode (`-r`) werden die einzelnen Werte nur durch ein Semikolon getrennt ausgegeben. Dies ermöglicht die automatische Weiterverwertung:

``ECLI:DE:BVERFG:2020:RK20200501.1BVR099620;BVerfG;Kammerentscheidung (1. Senat);01.05.2020;1 BvR 996/20;Keine;Verfassungsbeschwerden;http://www.bverfg.de/e/rk20200501_1bvr099620.html;
``

## Umfang und Ablauf der ECLI-Erkennung
Die Vorgaben für valide deutsche ECLI folgen grundsätzlich den Angaben des Bundesamtes für Justiz als [ECLI-Koordinator für Deutschland](https://e-justice.europa.eu/content_european_case_law_identifier_ecli-175-de-de.do?member=1). Diese sind allerdings nach Angaben des BfJ (E-Mail Auskunft, Stand Mai 2020) veraltet und auch unvollständig. So fehlt das ECLI-Schema des BPatG, dieses wurde direkt beim Gericht erfragt. Auch scheinen die Angaben auf der Website unvollständig, da sie nicht alle tatsächlich in der Praxis vergebenen ECLI erfassen. Die entsprechenden Abweichungen im Programm werden beschrieben.

### Abweichungen zu den Vorgaben des BfJ
* Das BfJ beschreibt die Kollisionsnummer der Gerichte der Länder als "zweistellig (fortlaufend von 00-99)". Tatsächlich werden in der Praxis (v.a. in Bayern) auch alphanumerische Kollisionsnummern vergeben. Sie beginnen mit `0A` statt `00`. Beispiel: `ECLI:DE:VGBAYRE:2005:0607.B1K04.1182.0A`
* Aktenzeichen beim BVerfG enthalten nicht immer eine Senatsbezeichnung (z.B. `ECLI:DE:BVERFG:2018:VB20180322.VZ001016`)

### Umfang der Erkennung
Umfangreiche Tests (>500 ECLI) haben ergeben, dass alle validen deutschen ECLI erkannt werden dürften. False positives sind aufgrund der strengen Regex kaum denkbar. Gültige, jedoch fiktive ECLI werden freilich als gültig erkannt und ausgewertet.

Die Länge der Aktenzeichen bei den Gerichten der Länder ist im ECLI auf 17 Stellen beschränkt. Bei Doppelaktenzeichen kann dies dazu führen, dass es nicht vollständig im ECLI abgebildet ist. Darauf weist das Programm bei Länder-ECLI mit einer Warnung hin.

### Ablauf der Erkennung

Im Code sind die ECLI-Schemata als reguläre Ausdrücke im Modul ``pattern.py`` hinterlegt.

Die Analyse erfolgt zweistufig. In einem ersten Zugriff wird der ECLI mit den Mustern der verschiedenen Bundesgerichte bzw. dem der Länder verglichen. Bereits hier dürften die meisten ungültigen ECLI aussortiert werden, wobei die Muster der Bundesgerichte aufgrund der spezifischeren Vorgaben für die Bildung des ECLI strenger sind. Passt ein eingegebener ECLI auf eines der Muster, wird ein passendes Entscheidungstyp-Objekt erzeugt und in einem zweiten Schritt die für das jeweilige Gericht passende `parse_ecli`-Funktion aufgerufen. Hier wird der ECLI abschnittsweise weiter analysiert und die enthaltenen Informationen übersetzt. Bei den Gerichten der Länder wird zuvor noch eine weitere Zuordnung zur jeweiligen Fachgerichtsbarkeit vorgenommen, um die Aktenzeichen korrekt bilden zu können. Die mit den Gerichtscodes korrespondierenden Gerichte sind in `gerichte.json` hinterlegt, sie werden nur bei einem Länder-ECLI benötigt und geladen. Die Daten zu Verfahrensarten, Registerzeichen etc. sind in `decisions.json` hinterlegt.

### ECLI des BPatG
(Gemäß E-Mail-Auskunft vom 29.04.2020)

Die ECLI des BPatG werden wie folgt gebildet:
> 1. ECLI
> 2. DE (= Ländercode)
> 3. BPatG (= Gericht, das die Entscheidung erlassen hat)
> 4. Jahr der Entscheidung
> 5. Ordinalzahl (= bis zu 25 alphanumerische Zeichen inklusive Punkte).

> Die Ordinalzahl soll wie folgt aufgebaut sein:

> Stellen|Beschreibung|Mögliche Werte
> ---|---|---
> 1-6|Verkündungs-Datum
> Zustellungs-Datum (bei Zustellung an Verkündungs Statt)|TTMMJJ
> 7|Entscheidungstyp|B (Beschluss) U (Urteil)
> 8-9|Spruchkörper|1…36
> 10-14|Registerzeichen gemäß § 3 I AktOBPatG vom 11.05.2010 (runde Klammern entfallen)|Wpat Ni Li LiQ LiR ZApat ARpat
> 15-17|Laufende Nummer|0…999
> 18|Trennzeichen (Punkt)|.
> 19-20|Jahreszahl|abschließende zwei Stellen des Jahres
> 21-22|Suffix Gemäß § 3 II AktOBPatG vom 11.05.2010 (runde Klammern entfallen)|EP EU
> 23|Trennzeichen (Punkt)|.
> 24-25|Kollisionsziffer (stets)

## Module
Name|Funktion
---|---
parse_ecli.py|Hauptprogramm (Ein/Ausgabe)
ecli_classes.py|Stellt die Entscheidungsklassen zur Verfügung. Das Model kann auch selbstständig in andere Skripte importiert werden, sodass die Erkennung direkt in das Programm intergriert werden kann.
pattern.py|Enthält die Regexes

### parse_ecli.py
Dient als ausführbares Skript, das für die Eingabe von ECLI-Strings verantwortlich ist und sie an die Klassen in `ecli_classes.py` übergibt. Enthält auch die Datei Ein-/Ausgabe.

### ecli_classes.py
Stellt die Hauptfunktionalität des Programms zur Verfügung und kann in andere Skripte eingebunden werden.

Die Funktion `match_ecli(ecli_string)` gibt ein Entscheidungs-Objekt zurück, das ein dict `court_data` enthält. Dieses enthält die Daten, die aus dem ECLI extrahiert werden konnten. Jedem key ist eine Liste zugeordnet, deren erstes Feld eine Datenbeschreibung ist. Die eigentlichen Daten liegen im zweiten Feld, das leer vorinitialisiert ist.

key|values|Erklärung
---|---|---
"court"| ["Gericht: ",""]|Enthält das Gericht hinter dem Gerichtscode. Bei den Gerichten der Länder muss der Code in der Datei `gerichte.json` aufgelöst werden.
"bodytype"| ["Spruchkörper: ",""]|Enthält den Spruchkörper (z.B. bei BGH) oder jedenfalls den Spruchkörpertyp (z.B. bei einer Kammerentscheidung des BVerfG)
"date"| ["Entscheidungsdatum: ",""]|
"az"| ["Aktenzeichen: ",""]|Das Aktenzeichen wird soweit möglich aus dem ECLI generiert. Bei Doppelaktenzeichen ist dies nur teilweise möglich. Die Registerzeichen werden, soweit sie nicht nur aus Großbuchstaben bestehen in 'decisions.json' nachgeschlagen.
"collision"| ["Kollisionsnummer: ",""]|Die Kollisionsnummer der Entscheidung.
"year"| ["Jahr: ",""]|
"decisiontype"| ["Entscheidungsart: ",""]|Der Entscheidungstyp, also z.B. Urteil, Beschluss, Gerichtsbescheid
"decision_explain"| ["Verfahren ",""]|Erläutert die Verfahrensart bzw. das Sachgebiet anhand des Registerzeichens (z.B. Revision in Zivilsachen)
"register_explain"| ["Register/Zusatz: ",""]|Manche Gerichte (etwas Sozialgerichtsbarkeit) verwenden ein zusätzliches Registerzeichen, das hier erläutert wird.
"url"| ["Link: ",""]|Beim BVerfG und BVerwG wird zudem auf Basis des ECLI eine Kurz-URL zur Entscheidung generiert.


## Ziele
* Auch ausländische ECLI sollen analysiert werden können.
* Es soll aus gegebenen Daten eine gültige ECLI generiert werden können.

## Tests
Im Ordner tests liegt eine Datei für `pytest` bereit. Es kann aus dem Unterverzeichnis `parse_ecli` mit

```
python -m pytest tests/
```

aufgerufen werden.
