import ecli_classes
import argparse
from pathlib import Path


##################
# Hauptprogramm
##################


##################
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


def exception_print(e):
    print("\n\n####################################################\n#\n#\n# FEHLER:\t", end='')
    print(e)
    print("#\n#\n####################################################\n\n")

if len(ecli_list) == 0:
    print("Keine ECLI gefunden!")
else:
    for ecli_string in ecli_list:
        try:
            my_decision = ecli_classes.match_ecli(ecli_string)
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
        except (ecli_classes.NoValidECLIError, ecli_classes.InValidAZError, ecli_classes.InValidCourtError) as e:
            exception_print(e)
