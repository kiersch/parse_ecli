# ECLI Parser
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-360/)

## Bedienung

```
python ecli.py <ECLI>
```
Der ECLI muss vollständig eingegeben werden. Führende Leerzeichen und Sonderzeichen werden entfernt.

Optional:

```
python ecli.py -r
```
für rawmode, d.h. die Daten werden ohne Beschriftung nur durch Semikolon getrennt ausgegeben.

```
python ecli.py -i input_file
python ecli.py -o output_file

```
ECLI können auch aus einer Textdatei eingelesen werden, die mit `-i` angegeben wird. Ein ECLI pro Zeile. Zeilen, die nicht mit `ECLI:DE:` beginnen, werden ignoriert.
Die Ausgabe kann auch in eine Datei umgeleitet werden, die wird mit `-o` angegeben.


## Module
TODO
## Ziele
* Auch ausländische ECLI
* Es soll aus gegebenen Daten eine gültige ECLI generiert werden können

## ECLI
Die Vorgaben für valide deutsche ECLI folgen grundsätzlich den Angaben des Bundesamtes für Justiz als [ECLI-Koordinator für Deutschland](https://e-justice.europa.eu/content_european_case_law_identifier_ecli-175-de-de.do?member=1). Diese sind allerdings nach Angaben des BfJ (E-Mail Auskunft, Stand Mai 2020) veraltet und auch unvollständig. So fehlt das ECLI-Schema des BPatG, dieses wurde direkt beim Gericht erfragt. Auch scheinen die dortigen Angaben unvollständig, da sie nicht alle tatsächlich in der Praxis vergebenen ECLI erfassen. Die entsprechenden Abweichungen im Programm werden beschrieben.

Im Code sind die ECLI-Schemata als reguläre Ausdrücke im Modul ``pattern.py`` hinterlegt.

TODO
