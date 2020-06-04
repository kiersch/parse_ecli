# Benötigt pytest. Bitte im Wurzelverzeichnis ausführen.

import sys
import re
import json
from pathlib import Path
from parse_ecli import parse_ecli
import pytest
from parse_ecli import pattern
import unittest.mock



###########
# REGEX TEST
###########
test_ecli_strings = [
# Diese Strings entsprechen den Regex-Pattern. Einige von ihnen (gesondert markiert)
# sind KEINE GÜLTIGEN ECLI, sondern werden nachgelagert aussortiert.
("ECLI:DE:BGH:2016:180216URISTR1.15.0", parse_ecli.Decision_BGH),
("ECLI:DE:BVERFG:2020:RK20200225.1BVR128217", parse_ecli.Decision_BVerfG),
("ECLI:DE:BPATG:2020:260320B26WPAT46.17.0", parse_ecli.Decision_BPatG),
("ECLI:DE:BPATG:2016:120716U3LIR5.15.0", parse_ecli.Decision_BPatG),
("ECLI:DE:BPATG:2017:310617U2NI13.16.0", parse_ecli.Decision_BPatG),
("ECLI:DE:BAG:2020:270220.B.2AZN1389.19.0", parse_ecli.Decision_BAG),
("ECLI:DE:BAG:2020:210120.U.3AZR73.19.0", parse_ecli.Decision_BAG),
("ECLI:DE:BAG:2020:270220.B.GS1389.19.0", parse_ecli.Decision_BAG), # Fiktiv zum Test von GS (matcht auch ohne Senat)
("ECLI:DE:BFH:2019:U.180919.IIIR3.19.0", parse_ecli.Decision_BFH),
("ECLI:DE:BFH:2019:U.111219.XIR13.18.0", parse_ecli.Decision_BFH),
("ECLI:DE:ARBGD:2018:0824.4CA3038.18.00", parse_ecli.Decision_Other),
("ECLI:DE:VGKASSE:2020:0406.3L348.20.KS.00", parse_ecli.Decision_Other),
("ECLI:DE:LAGK:2005:0713.8SA796.04.00", parse_ecli.Decision_Other),
("ECLI:DE:LAGHAM:2011:0412.19SA1951.10.00", parse_ecli.Decision_Other),
("ECLI:DE:VGGE:2011:0124.12K5288.09.00", parse_ecli.Decision_Other),
("ECLI:DE:VGD:2010:1217.13K4888.10.00", parse_ecli.Decision_Other),
("ECLI:DE:VGAC:2012:0314.8K1740.06.00", parse_ecli.Decision_Other),
("ECLI:DE:VGMI:2011:0808.3K816.11.00", parse_ecli.Decision_Other),
("ECLI:DE:OVGNRW:2020:0421.9A287.19.00", parse_ecli.Decision_Other),
("ECLI:DE:VGAC:2020:0415.3L2.20.00", parse_ecli.Decision_Other),
("ECLI:DE:SGAC:2012:0120.S19SO109.11.00", parse_ecli.Decision_Other),
("ECLI:DE:SGDT:2020:0218.S14U153.14.00", parse_ecli.Decision_Other),
("ECLI:DE:SGDU:2020:0214.S44KR379.17.00", parse_ecli.Decision_Other),
("ECLI:DE:SGDO:2020:0204.S17U237.18.00", parse_ecli.Decision_Other),
("ECLI:DE:SGGE:2019:0807.S46KR70.17.00", parse_ecli.Decision_Other),
("ECLI:DE:LSGNRW:2019:1216.L8BA4.18B.ER.00", parse_ecli.Decision_Other),
("ECLI:DE:LSGNRW:2019:1205.L7AS1764.18.00", parse_ecli.Decision_Other),
("ECLI:DE:FGD:2020:0325.11V3249.19A.AO.00", parse_ecli.Decision_Other),
("ECLI:DE:FGMS:2020:0305.5K1670.17U.00", parse_ecli.Decision_Other),
("ECLI:DE:FGD:2020:0205.4K3554.18Z.00", parse_ecli.Decision_Other),
("ECLI:DE:FGD:2020:0128.10K2166.16E.00", parse_ecli.Decision_Other),
("ECLI:DE:FGK:2020:0124.1K1041.17.00", parse_ecli.Decision_Other),
("ECLI:DE:FGMS:2020:0121.6K1384.18G.F.00", parse_ecli.Decision_Other),
("ECLI:DE:FGMS:2020:0121.11V3213.19AO.00", parse_ecli.Decision_Other),
("ECLI:DE:LGSI:2012:0316.2O219.11.00", parse_ecli.Decision_Other),
("ECLI:DE:OLGHAM:2012:0417.III3RVS24.12.00", parse_ecli.Decision_Other),
("ECLI:DE:AGK:2005:0609.129C70.04.00", parse_ecli.Decision_Other),
("ECLI:DE:OLGHAM:2020:0416.4WS72.20.00", parse_ecli.Decision_Other),
("ECLI:DE:OLGD:2020:0330.2RBS47.20.00", parse_ecli.Decision_Other),
("ECLI:DE:OLGK:2020:0327.1U95.19.00", parse_ecli.Decision_Other),
("ECLI:DE:OLGHAM:2020:0326.2AUSL15.19.00", parse_ecli.Decision_Other),
("ECLI:DE:OLGK:2020:0324.4U235.19.00", parse_ecli.Decision_Other),
("ECLI:DE:OLGHAM:2020:0319.4RVS25.20.00", parse_ecli.Decision_Other),
("ECLI:DE:OLGD:2020:0205.VERG21.19.00", parse_ecli.Decision_Other),
("ECLI:DE:OLGK:2020:0205.5W1.20.00", parse_ecli.Decision_Other),
("ECLI:DE:OLGD:2020:0121.I21U46.19.00", parse_ecli.Decision_Other),
("ECLI:DE:LGKLE:2020:0320.140AR1.20.00", parse_ecli.Decision_Other),
("ECLI:DE:LGK:2020:0317.11S33.19.00", parse_ecli.Decision_Other),
("ECLI:DE:LGK:2020:0311.84O204.19.00", parse_ecli.Decision_Other),
("ECLI:DE:LGDO:2020:0304.8O2.20KART.00", parse_ecli.Decision_Other),
("ECLI:DE:LGMG:2020:0302.4S147.19.00", parse_ecli.Decision_Other),
("ECLI:DE:LGBN:2020:0228.1O21.19.00", parse_ecli.Decision_Other),
("ECLI:DE:LGE:2020:0225.17O168.19.00", parse_ecli.Decision_Other),
("ECLI:DE:AGK:2020:0310.120C166.19.00", parse_ecli.Decision_Other),
("ECLI:DE:AGRE1:2020:0225.60XIV.L28.20U.00", parse_ecli.Decision_Other),
("ECLI:DE:AGAC1:2020:0213.107C301.19.01", parse_ecli.Decision_Other),
("ECLI:DE:AGMS:2020:0211.96C170.20.00", parse_ecli.Decision_Other),
("ECLI:DE:AGKLE1:2020:0123.35C360.19.00", parse_ecli.Decision_Other),
("ECLI:DE:AGDO:2020:0121.729DS060JS513.19.00", parse_ecli.Decision_Other),
("ECLI:DE:VFGHNRW:2020:0415.VERFGH30.20VB2.00", parse_ecli.Decision_Other),
("ECLI:DE:MSCHOGK:2011:1025.3U8.11BSCHMO.00", parse_ecli.Decision_Other),
("ECLI:DE:SCHGMI:2007:0821.21C143.07BSCH.00", parse_ecli.Decision_Other),
("ECLI:DE:RSCHGDU:2012:0125.5C8.11BSCH.00", parse_ecli.Decision_Other),
("ECLI:DE:RSCHOGK:2018:1122.3U74.17BSCHRH.00", parse_ecli.Decision_Other),
("ECLI:DE:BGHK:2015:1211.31K3353.12T.00", parse_ecli.Decision_Other),
("ECLI:DE:BGHMS:2015:1105.18K2010.14T.00", parse_ecli.Decision_Other),
("ECLI:DE:BGHK:2004:0112.37K5252.02T.00", parse_ecli.Decision_Other),
("ECLI:DE:BGANRW:2017:1012.32K6610.17S.00", parse_ecli.Decision_Other),
("ECLI:DE:BGINRW:2009:0217.36K3999.07U.00", parse_ecli.Decision_Other),
("ECLI:DE:VGWIESB:2020:0318.3L514.18.WI.00", parse_ecli.Decision_Other),
("ECLI:DE:VGK:2013:1018.5K1903.12A.00", parse_ecli.Decision_Other),
("ECLI:DE:VGK:2015:0211.33L2274.14PVB.00", parse_ecli.Decision_Other),
("ECLI:DE:VGBAYRE:2005:0607.B1K04.1182.0A", parse_ecli.Decision_Other),
#("ECLI:DE:VGBAYR:2005:0607.B1K04.1182.0A", parse_ecli.Decision_Other) # ACHTUNG UNGÜLTIG! Nicht vorhandener Gerichtscode. Darf hier noch matchen

]

test_ecli_strings_fail = [
# Diese müssen scheitern
"ECLI:DE:VGBAYRE:2005:", # ECLI zu kurz
"ECLI:FR:OLGHAM:2020:0319.4RVS25.20.00", # Beginnt nicht mit ECLI:DE:
"ECLI:DE:SUPREMEC:2016:180216URISTR1.15.0", # Ungültiges Gericht beim BGH Schema
"ECLI:DE:BGH:2020:180320IXZA4.20.0", # Entscheidungstyp (UBVS) fehlt
"ECLI:DE:BGH:201:180216URISTR1.15.0", # Unvollständige Jahreszahl
"ECLI:DE:BGH:1899:180216URISTR1.15.0", # Ungültige Jahreszahl (vor 1900)
"ECLI:DE:OLGK:2020:205.5W1.20.00",  # Unvollständiges Entscheidungsdatum
"ECLI:DE:VGAC:2012:0314.8.6.00", # Az zu kurz
"ECLI:DE:VGAC:2012:0314.8K1740.06.0", # Kollisionsnummer unvollständig
"ECLI:DE:BAG:2020:270220.B.AZN1389.19.0", # Senat fehlt
"ECLI:DE:BAG:2020:270220.B.1ÄZN1389.19.0" # Enthält Sonderzeichen
]

@pytest.mark.parametrize("test_ecli_string, expected", test_ecli_strings)
def test_match_ecli(test_ecli_string, expected):
    x = parse_ecli.match_ecli(test_ecli_string)
    assert isinstance(x, expected)

@pytest.mark.parametrize("test_ecli_string_fail", test_ecli_strings_fail)
def test_match_ecli_fail(test_ecli_string_fail):
    with pytest.raises(parse_ecli.NoValidECLIError):
        parse_ecli.match_ecli(test_ecli_string_fail)

##########
# BVerfG
##########

test_court_data_bverfg = [
    ("ECLI:DE:BVERFG:2020:RK20200225.1BVR128217", ("BVerfG", "25.02.2020", "1 BvR 1282/17", "Keine", "Verfassungsbeschwerden", "Kammerentscheidung (1. Senat)", "http://www.bverfg.de/e/rk20200225_1bvr128217.html")),
    ("ECLI:DE:BVERFG:2017:BS20170117.2BVB000113",("BVerfG", "17.01.2017", "2 BvB 1/13", "Keine", "Feststellung der Verfassungswidrigkeit von Parteien", "Senatsentscheidung (2. Senat)", "http://www.bverfg.de/e/bs20170117_2bvb000113.html")),
    ("ECLI:DE:BVERFG:1999:MS19990202.2BVM000198",("BVerfG", "02.02.1999", "2 BvM 1/98", "Keine", "Überprüfung von Völkerrecht als Bundesrecht", "Senatsentscheidung (2. Senat)", "http://www.bverfg.de/e/ms19990202_2bvm000198.html")),
    ("ECLI:DE:BVERFG:1997:PS19970624.2BVP000194",("BVerfG", "24.06.1997", "2 BvP 1/94", "Keine", "Anderweitig durch Bundesgesetz zugewiesene Entscheidungen", "Senatsentscheidung (2. Senat)", "http://www.bverfg.de/e/ps19970624_2bvp000194.html")),
    ("ECLI:DE:BVERFG:2018:VB20180322.VZ001016",("BVerfG", "22.03.2018", "Vz 10/16", "Keine", "Verzögerungsbeschwerden", "Beschwerdekammer", "http://www.bverfg.de/e/vb20180322_vz001016.html")),
    ("ECLI:DE:BVERFG:2012:UP20120703.2PBVU000111",("BVerfG", "03.07.2012", "2 PBvU 1/11", "Keine", "Plenarentscheidungen", "Plenum (Vorlagesenat: 2. Senat)", "http://www.bverfg.de/e/up20120703_2pbvu000111.html")),
    ("ECLI:DE:BVERFG:1996:ES19960521.2BVE000195",("BVerfG", "21.05.1996", "2 BvE 1/95", "Keine", "Organstreitverfahren", "Senatsentscheidung (2. Senat)", "http://www.bverfg.de/e/es19960521_2bve000195.html")),
    ("ECLI:DE:BVERFG:2020:CS20200331B.2BVC001919",("BVerfG", "31.03.2020", "2 BvC 19/19", "B (Es gibt mehrere Entscheidungen vom gleichen Datum unter diesem Az.!)", "Wahlprüfungsbeschwerden", "Senatsentscheidung (2. Senat)", "http://www.bverfg.de/e/cs20200331b_2bvc001919.html")),
]

test_court_data_bverfg_fail = [
"ECLI:DE:BVERFG:2020:RK20200225.1BR128217", # Ungültiges Registerzeichen BVerfG
"ECLI:DE:BVERFG:2020:R20200225.1BVR128217", # Es fehlt der Spruchkörpertyp
"ECLI:DE:BVERFG:2020:RK20200418.BVR082920" # Hier fehlt der Senat, obwohl kein VB/UP
]


@pytest.mark.parametrize("bverfg_input, expected", test_court_data_bverfg)
def test_bverfg_parse(bverfg_input, expected):
    bverfg = parse_ecli.Decision_BVerfG(bverfg_input)
    match = re.match(pattern.bverfg_compiled, bverfg_input)
    bverfg.parse_ecli(match)
    assert bverfg.court_data["court"][1] == expected[0]
    assert bverfg.court_data["date"][1] == expected[1]
    assert bverfg.court_data["az"][1] == expected[2]
    assert bverfg.court_data["collision"][1] == expected[3]
    assert bverfg.court_data["decisiontype"][1] == expected[4]
    assert bverfg.court_data["bodytype"][1] == expected[5]
    assert bverfg.court_data["url"][1] == expected[6]

@pytest.mark.parametrize("test_court_data_bverfg_fail", test_court_data_bverfg_fail)
def test_bverfg_fail(test_court_data_bverfg_fail):
    bverfg = parse_ecli.Decision_BVerfG(test_court_data_bverfg_fail)
    match = re.match(pattern.bverfg_compiled, test_court_data_bverfg_fail)

    with pytest.raises((KeyError, parse_ecli.InValidAZError)):
        bverfg.parse_ecli(match)

##########
# BGH
##########

test_court_data_bgh = [
    ("ECLI:DE:BGH:2016:180216URISTR1.15.0", ("BGH", "18.02.2016", "RiSt(R) 1/15", "0", "Urteil", "Revisionen in Disziplinarsachen nach dem Deutschen Richtergesetz", "Dienstgericht des Bundes")),
    ("ECLI:DE:BGH:2016:310516BIZB39.15.0", ("BGH", "31.05.2016", "I ZB 39/15", "0", "Beschluss", "Beschwerden, Rechtsbeschwerden, weitere Beschwerden, Beschwerden gegen die Nichtzulassung der Revision nach dem BEG", "I. Zivilsenat")),
    ("ECLI:DE:BGH:2020:040220B3STR313.19.1", ("BGH", "04.02.2020", "3 StR 313/19", "1 (Es gibt mehrere Entscheidungen vom gleichen Datum unter diesem Az.!)", "Beschluss", "Revisionen und Vorlegungssachen nach § 121 Abs.1 Nr.1, Abs. 2 GVG, § 79 Abs. 3 OWiG, §§ 13 Abs. 4, 25 StrRehaG", "3. Strafsenat")),
    ("ECLI:DE:BGH:2020:040220B5AR.VS.64.19.0", ("BGH", "04.02.2020", "5 AR(VS) 64/19", "0", "Beschluss", "Entscheidungen über Justizverwaltungsakte", "5. Strafsenat")),
    ("ECLI:DE:BGH:2020:180320BIXZA4.20.0", ("BGH", "18.03.2020", "IX ZA 4/20", "0", "Beschluss", "Anträge außerhalb eines in der Rechtsmittelinstanz anhängigen Verfahrens", "IX. Zivilsenat")),
    ("ECLI:DE:BGH:2020:200220UIZR176.18.0", ("BGH", "20.02.2020", "I ZR 176/18", "0", "Urteil", "Revisionen, Beschwerden gegen die Nichtzulassung der Revision, Anträge auf Zulassung der Sprungrevision, Berufungen in Patentsachen", "I. Zivilsenat")),
    ("ECLI:DE:BGH:2020:070420BAK6.20.0", ("BGH", "07.04.2020", "AK 6/20", "0", "Beschluss", "Aktenkontrolle für Haftprüfungsverfahren", "")),
    ("ECLI:DE:BGH:2020:240320BENVR45.18.0", ("BGH", "24.03.2020", "EnVR 45/18", "0", "Beschluss", "Rechtsbeschwerden in energiewirtschaftsrechtlichen Verwaltungssachen nach dem EnWG", "Kartellsenat")),
    ("ECLI:DE:BGH:2020:240320BKVZ3.19.0", ("BGH", "24.03.2020", "KVZ 3/19", "0", "Beschluss", "Nichtzulassungsbeschwerden in Kartellverwaltungssachen", "Kartellsenat")),
    ("ECLI:DE:BGH:2019:280819BNOTST.BRFG.1.18.0", ("BGH", "28.08.2019", "NotSt(Brfg) 1/18", "0", "Beschluss", "Berufungen und Anträge auf Zulassung der Berufung gegen Urteile der Oberlandesgerichte in Disziplinarsachen gegen Notare", "Senat für Notarsachen")),
]

test_court_data_bgh_fail = [
"ECLI:DE:BGH:2020:200220UIUR176.18.0", # Ungültiges Registerzeichen BGH
]


@pytest.mark.parametrize("bgh_input, expected", test_court_data_bgh)
def test_bgh_parse_1(bgh_input, expected):
    bgh = parse_ecli.Decision_BGH(bgh_input)
    match = re.match(pattern.bgh_compiled, bgh_input)
    bgh.parse_ecli(match)
    assert bgh.court_data["court"][1] == expected[0]
    assert bgh.court_data["date"][1] == expected[1]
    assert bgh.court_data["az"][1] == expected[2]
    assert bgh.court_data["collision"][1] == expected[3]
    assert bgh.court_data["decisiontype"][1] == expected[4]
    assert bgh.court_data["decision_explain"][1] == expected[5]
    assert bgh.court_data["bodytype"][1] == expected[6]


@pytest.mark.parametrize("test_court_data_bgh_fail", test_court_data_bgh_fail)
def test_bgh_fail(test_court_data_bgh_fail):
    bgh = parse_ecli.Decision_BGH(test_court_data_bgh_fail)
    match = re.match(pattern.bgh_compiled, test_court_data_bgh_fail)

    with pytest.raises((KeyError, parse_ecli.InValidAZError)):
        bgh.parse_ecli(match)



##########
# BPatG
##########

test_court_data_bpatg = [
    ("ECLI:DE:BPATG:2016:120716U3LI5.15.0", ("BPatG", "12.07.2016", "3 Li 5/15", "0", "Urteil", "Zwangslizenzverfahren")),
    ("ECLI:DE:BPATG:2017:120517B25WPAT12.16.0", ("BPatG", "12.05.2017", "25 W (pat) 12/16", "0", "Beschluss", "Beschwerdeverfahren (Patent, Design, Sortenschutz, Marken)")),
    ("ECLI:DE:BPATG:2017:310617U2NI13.16EU.0", ("BPatG", "31.06.2017", "2 Ni 13/16 (EU)", "0", "Urteil", "Patentnichtigkeitsverfahren")),
]


@pytest.mark.parametrize("bpatg_input, expected", test_court_data_bpatg)
def test_bpatg_parse_1(bpatg_input, expected):
    bpatg = parse_ecli.Decision_BPatG(bpatg_input)
    match = re.match(pattern.bpatg_compiled, bpatg_input)
    bpatg.parse_ecli(match)
    assert bpatg.court_data["court"][1] == expected[0]
    assert bpatg.court_data["date"][1] == expected[1]
    assert bpatg.court_data["az"][1] == expected[2]
    assert bpatg.court_data["collision"][1] == expected[3]
    assert bpatg.court_data["decisiontype"][1] == expected[4]
    assert bpatg.court_data["decision_explain"][1] == expected[5]

##########
# BVerwG
##########

test_court_data_bverwg = [
    ("ECLI:DE:BVERWG:2016:210416U2C4.15.0", ("BVerwG", "Urteil", "21.04.2016", "2 C 4.15", "0", "Revisionen in Verwaltungsstreitverfahren (§§ 49, 132 VwGO)", "", "2. Senat", "https://www.bverwg.de/de/210416U2C4.15.0")),
    ("ECLI:DE:BVERWG:2013:291013U1D1.12.0", ("BVerwG", "Urteil", "29.10.2013", "1 D 1.12", "0", "Berufungsverfahren in Disziplinarsachen", "", "Disziplinarsenat", "https://www.bverwg.de/de/291013U1D1.12.0")),
    ("ECLI:DE:BVERWG:2020:170320B20F3.18.0", ("BVerwG", "Beschluss", "17.03.2020", "20 F 3.18", "0", "Verwaltungsstreitsachen vor dem Fachsenat wegen der verweigerten Vorlage von Urkunden, Akten oder elektronischen Dokumente sowie der verweigerten Erteilung von Auskünften (§ 99 Abs. 2 VwGO)", "", "Fachsenat nach § 189 VwGO", "https://www.bverwg.de/de/170320B20F3.18.0")),
    ("ECLI:DE:BVERWG:2018:100918B5B20.18D0", ("BVerwG", "Beschluss", "10.09.2018", "5 B 20.18 D", "0", "Beschwerden (einschl. Nichtzulassungsbeschwerden) in Verwaltungsstreitsachen", "Rechtsschutz bei überlangen Gerichtsverfahren", "5. Senat", "https://www.bverwg.de/de/100918B5B20.18D0")),
# TODO: ECLI:DE:BVERWG:2018:100918B5B20.18D0
]

test_court_data_bverwg_fail = [
"ECLI:DE:BVERWG:2016:210416U2UU4.15.0", # Ungültiges Registerzeichen BVerfG
]


@pytest.mark.parametrize("bverwg_input, expected", test_court_data_bverwg)
def test_bverwg_parse(bverwg_input, expected):
    bverwg = parse_ecli.Decision_BVerwG(bverwg_input)
    match = re.match(pattern.bverwg_compiled, bverwg_input)
    bverwg.parse_ecli(match)
    assert bverwg.court_data["court"][1] == expected[0]
    assert bverwg.court_data["decisiontype"][1] == expected[1]
    assert bverwg.court_data["date"][1] == expected[2]
    assert bverwg.court_data["az"][1] == expected[3]
    assert bverwg.court_data["collision"][1] == expected[4]
    assert bverwg.court_data["decision_explain"][1] == expected[5]
    assert bverwg.court_data["register_explain"][1] == expected[6]
    assert bverwg.court_data["bodytype"][1] == expected[7]
    assert bverwg.court_data["url"][1] == expected[8]

@pytest.mark.parametrize("test_court_data_bverwg_fail", test_court_data_bverwg_fail)
def test_bverwg_fail(test_court_data_bverwg_fail):
    bverwg = parse_ecli.Decision_BVerwG(test_court_data_bverwg_fail)
    match = re.match(pattern.bverwg_compiled, test_court_data_bverwg_fail)

    with pytest.raises((KeyError, parse_ecli.InValidAZError)):
        bverwg.parse_ecli(match)

##########
# BSG
##########

test_court_data_bsg = [
    ("ECLI:DE:BSG:2019:200219BGS1180", ("BSG", "20.02.2019", "GS 1/18", "0", "Verfahren vor dem Großen Senat", "Großer Senat", "Beschluss", "")),
    ("ECLI:DE:BSG:2019:190919UB12R2518R0", ("BSG", "19.09.2019", "B 12 R 25/18 R", "0", "Gesetzliche Rentenversicherung", "12. Senat", "Urteil", "Revisionsregister")),
    ("ECLI:DE:BSG:2020:270320UB10UEG419R0", ("BSG", "27.03.2020", "B 10 ÜG 4/19 R", "0", "Rechtsschutz bei überlangen Gerichtsverfahren", "10. Senat", "Urteil", "Revisionsregister")),
    ("ECLI:DE:BSG:2020:190320UB1KR2019R0", ("BSG", "19.03.2020", "B 1 KR 20/19 R", "0", "Gesetzliche Krankenversicherung", "1. Senat", "Urteil", "Revisionsregister")),
    ("ECLI:DE:BSG:2020:200220BB14AS919B0", ("BSG", "20.02.2020", "B 14 AS 9/19 B", "0", "Grundsicherung für Arbeitsuchende", "14. Senat", "Beschluss", "Beschwerderegister")),
    ("ECLI:DE:BSG:2020:110220BB10EG1419B0", ("BSG", "11.02.2020", "B 10 EG 14/19 B", "0", "Elterngeld und Erziehungsgeld", "10. Senat", "Beschluss", "Beschwerderegister")),

]

test_court_data_bsg_fail = [
"ECLI:DE:BSG:2019:190919U12R2518R0", # Ungültiges Registerzeichen BSG (kein Instanzen-B)
]


@pytest.mark.parametrize("bsg_input, expected", test_court_data_bsg)
def test_bsg_parse(bsg_input, expected):
    bsg = parse_ecli.Decision_BSG(bsg_input)
    match = re.match(pattern.bsg_compiled, bsg_input)
    bsg.parse_ecli(match)
    assert bsg.court_data["court"][1] == expected[0]
    assert bsg.court_data["date"][1] == expected[1]
    assert bsg.court_data["az"][1] == expected[2]
    assert bsg.court_data["collision"][1] == expected[3]
    assert bsg.court_data["decision_explain"][1] == expected[4]
    assert bsg.court_data["bodytype"][1] == expected[5]
    assert bsg.court_data["decisiontype"][1] == expected[6]
    assert bsg.court_data["register_explain"][1] == expected[7]

@pytest.mark.parametrize("test_court_data_bsg_fail", test_court_data_bsg_fail)
def test_bsg_fail(test_court_data_bsg_fail):
    bsg = parse_ecli.Decision_BSG(test_court_data_bsg_fail)
    match = re.match(pattern.bsg_compiled, test_court_data_bsg_fail)

    with pytest.raises((KeyError, parse_ecli.InValidAZError)):
        bsg.parse_ecli(match)




##########
# Gerichte der Länder
##########


test_court_data_laender = [
    ("ECLI:DE:AGBAYRE:2016:0622.105C1568.15WEG.0A", ("Amtsgericht Bayreuth", "22.06.2016", "105 C 1568/15 WEG", "0A", "Erstinstanzliche Zivilprozesse", "")),
    ("ECLI:DE:AGBAYRE:2016:1109.2M2168.16.0A", ("Amtsgericht Bayreuth", "09.11.2016", "2 M 2168/16", "0A", "Zwangsvollstreckungssachen", "")),
    ("ECLI:DE:AGBEWE:2020:0108.22CC233.19.0A", ("Amtsgericht Wedding", "08.01.2020", "22c C 233/19", "0A", "Erstinstanzliche Zivilprozesse", "")),
    ("ECLI:DE:AGRE1:2020:0225.60XIV.L28.20U.00", ("Amtsgericht Recklinghausen", "25.02.2020", "60 XIV(L) 28/20 U", "00", "Unterbringungs- (§ 312 FamFG) und Freiheitsentziehungssachen (§ 415 FamFG)", "")),
    ("ECLI:DE:LGKLE:2019:1104.110KLS204JS169.19.00", ("Landgericht Kleve", "04.11.2019", "110 KLs 204 Js 169/19", "00", "Erstinstanzliche Sachen der großen Strafkammer/Jugendkammer (§ 74 Abs. 1 GVG, § 41 JGG)", "")),
    ("ECLI:DE:LGAC:2019:1011.60KLS806JS589.16.00", ("Landgericht Aachen", "11.10.2019", "60 KLs 806 Js 589/16", "00", "Erstinstanzliche Sachen der großen Strafkammer/Jugendkammer (§ 74 Abs. 1 GVG, § 41 JGG)", "")),
    ("ECLI:DE:OLGBAMB:2018:1130.2OLG110SS89.18.00", ("Oberlandesgericht Bamberg", "30.11.2018", "2 OLG 110 Ss 89/18", "00", "Revisionen in Strafsachen (§ 121 Abs. 1 Nr. 1 GVG), Berufungen in Binnenschifffahrtssachen (§ 11 BinSchGerG)", "")),
    ("ECLI:DE:OLGNUER:2012:1107.1STOLGSS258.12.0A", ("Oberlandesgericht Nürnberg", "07.11.2012", "1 St OLG Ss 258/12", "0A", "Revisionen in Strafsachen (§ 121 Abs. 1 Nr. 1 GVG), Berufungen in Binnenschifffahrtssachen (§ 11 BinSchGerG)", "")),
    ("ECLI:DE:OLGHAM:2019:0917.32SA60.19.00", ("Oberlandesgericht Hamm", "17.09.2019", "32 SA 60/19", "00", "Gerichtsstandbestimmungsverfahren", "")),
    ("ECLI:DE:FGHH:2020:0220.2K293.15.00", ("Finanzgericht Hamburg", "20.02.2020", "2 K 293/15", "00", "", "Klagen")),
    ("ECLI:DE:KG:2020:0218.3WS.B11.20.00", ("Kammergericht", "18.02.2020", "3 Ws (B) 11/20", "00", "Beschwerden in Strafsachen und Bußgeldsachen", "")), # In Beck mit falschem Az (11/19) hinterlegt, juris korrekt
    ("ECLI:DE:LGAC:2019:1011.60KLS806JS589.16.00", ("Landgericht Aachen", "11.10.2019", "60 KLs 806 Js 589/16", "00", "Erstinstanzliche Sachen der großen Strafkammer/Jugendkammer (§ 74 Abs. 1 GVG, § 41 JGG)", "")),
    ("ECLI:DE:LGD:2019:0808.4CO88.17.0A", ("Landgericht Düsseldorf", "08.08.2019", "4c O 88/17", "0A", "Erstinstanzliche Zivilprozesse (gewöhnliche Prozesse, Arreste und einstweilige Verfügungen; § 71 GVG)", "")),
    ("ECLI:DE:LGLUENE:2015:0226.33KLS.760JS44594.0A", ("Landgericht Lüneburg", "26.02.2015", "33 KLs 760 Js 44594", "0A", "Erstinstanzliche Sachen der großen Strafkammer/Jugendkammer (§ 74 Abs. 1 GVG, § 41 JGG)", "")),
    ("ECLI:DE:OLGMUEN:2020:0128.31WX229.19.31WX23.0A", ("Oberlandesgericht München", "28.01.2020", "31 Wx 229/19 31 WX 23 [...]", "0A", "Weitere Beschwerde in Verfahren der freiwilligen Gerichtsbarkeit", "")),
    ("ECLI:DE:AGFREIB:2015:0427.PR700066.0A", ("Amtsgericht Freiburg im Breisgau", "27.04.2015", "PR 700066", "0A", "Partnerschaftsregister (PartGG)", "")),
    ("ECLI:DE:AGE1:2016:0419.90PR2335.00", ("Amtsgericht Essen", "19.04.2016", "90 PR 2335", "00", "Partnerschaftsregister (PartGG)", "")),
    ("ECLI:DE:LSGNRW:2019:1216.L8BA4.18B.ER.00", ("Landessozialgericht Nordrhein-Westfalen", "16.12.2019", "L 8 BA 4/18 B ER", "00", "Anfrageverfahren nach § 7a SGB IV sowie der Betriebsprüfungen nach §§ 28p und 28q SGB IV", "")),
    ("ECLI:DE:OLGKOBL:2017:0706.9UF108.17.00", ("Oberlandesgericht Koblenz", "06.07.2017", "9 UF 108/17", "00", "Beschwerden in Familiensachen des Rechtspflegers (§ 3 RpflG) sowie gegen andere als Endentscheidungen (§ 39a AktO)", "")),
    ("ECLI:DE:OVGBEBB:2017:0406.OVG12B7.16.0A", ("Oberverwaltungsgericht Berlin-Brandenburg", "06.04.2017", "OVG 12 B 7/16", "0A", "Vorläufiger/einstweiliger Rechtsschutz; auch Rechtsmittel gegen Beschlüsse der Verwaltungsgerichte", "")), #Hier eigentlich . statt / im Az.
    ("ECLI:DE:OVGSL:2017:0220.2A34.16.0A", ("Oberverwaltungsgericht des Saarlandes", "20.02.2017", "2 A 34/16", "0A", "Rechtsmittel gegen Entscheidungen der Verwaltungsgerichte in Hauptverfahren", "")),
    ("ECLI:DE:SGDT:2019:1205.S11SO255.18.00", ("Sozialgericht Detmold", "05.12.2019", "S 11 SO 255/18", "00", "Sozialhilfe nach dem SGB XII", "")),
    ("ECLI:DE:SGGIESS:2019:0201.S1U61.15.00", ("Sozialgericht Gießen", "01.02.2019", "S 1 U 61/15", "00", "Gesetzliche Unfallversicherung", "")),
    ("ECLI:DE:VGFFM:2020:0402.11K2893.19.F.00",("Verwaltungsgericht Frankfurt am Main", "02.04.2020", "11 K 2893/19.F", "00", "Erstinstanzliche Hauptverfahren", "")),
    ("ECLI:DE:VGHANNO:2019:0312.7B850.19.00", ("Verwaltungsgericht Hannover", "12.03.2019", "7 B 850/19", "00", "Vorläufiger/einstweiliger Rechtsschutz; auch Rechtsmittel gegen Beschlüsse der Verwaltungsgerichte", "")),
    ("ECLI:DE:VGHH:2019:0215.9K1669.18.00", ("Verwaltungsgericht Hamburg", "15.02.2019", "9 K 1669/18", "00", "Erstinstanzliche Hauptverfahren", "")),
    ("ECLI:DE:VGK:2015:0211.33L2274.14PVB.00", ("Verwaltungsgericht Köln", "11.02.2015", "33 L 2274/14.PVB", "00", "Vorläufiger/einstweiliger Rechtsschutz", "Bundespersonalvertretungssache")),
    ("ECLI:DE:VGSTUTT:2001:0517.5K1912.01.0A",("Verwaltungsgericht Stuttgart", "17.05.2001", "5 K 1912/01", "0A", "Erstinstanzliche Hauptverfahren", "")),
    ("ECLI:DE:VGD:2005:0517.38K1571.05BDG.00",("Verwaltungsgericht Düsseldorf", "17.05.2005", "38 K 1571/05.BDG", "00", "Erstinstanzliche Hauptverfahren", "Bundesdisziplinarsachen")),
    ("ECLI:DE:VGGE:2013:0110.6A.L6.13A.00",("Verwaltungsgericht Gelsenkirchen", "10.01.2013", "6a L 6/13.A", "00", "Vorläufiger/einstweiliger Rechtsschutz", "Asylverfahren")),
    #("ECLI:DE:LGMAGDE:2019:0312.28QS39.19.00", ("Landgericht Magdeburg", "13.12.2019", "28 Qs 39/19", "00", "Beschwerden in Strafsachen und Bußgeldsachen (§ 73 GVG)", "")),
]

test_court_data_laender_fail = [
"ECLI:DE:VGK:2015:0211.33L2274.14PB.00" # Ungültiger Zusatz hinter Jahreszahl im Az (VerwG)
]

@pytest.mark.parametrize("input, expected", test_court_data_laender)
def test_laender_parse_1(input, expected):
    laender = parse_ecli.Decision_Other(input)
    match = re.match(pattern.laender_compiled, input)
    laender.parse_ecli(match)
    assert laender.court_data["court"][1] == expected[0]
    assert laender.court_data["date"][1] == expected[1]
    assert laender.court_data["az"][1] == expected[2]
    assert laender.court_data["collision"][1] == expected[3]
    assert laender.court_data["decision_explain"][1] == expected[4]
    assert laender.court_data["register_explain"][1] == expected[5]
#

@pytest.mark.parametrize("test_court_data_laender_fail", test_court_data_laender_fail)
def test_laender_fail(test_court_data_laender_fail):
    laender = parse_ecli.Decision_Other(test_court_data_laender_fail)
    match = re.match(pattern.laender_compiled, test_court_data_laender_fail)

    with pytest.raises((KeyError, parse_ecli.InValidAZError)):
        laender.parse_ecli(match)


##################
# Filetests
##################
def test_read_from_file_raw_stdout(capsys):
    parse_ecli.read_from_file_mode("tests/input_search.txt", raw=True)
    sys.stdout.reconfigure(encoding='utf-8')
    out, err = capsys.readouterr()
    sys.stdout.write(out)
    sys.stderr.write(err)

    assert out.startswith("4 g")
    # Vergleich funktioniert nur zeilenweise, selbst mit Triple """
    assert "Positionen in Datei: [294, 935, 1144, 1500]" in out
    assert "ECLI:DE:OLGBB:2020:0213.12U54.19.00;Brandenburgisches Oberlandesgericht;13.02.2020;12 U 54/19;00;Berufungen in Zivilsachen (§ 119 Abs. 1 Nr. 2 GVG, §§ 511 ff ZPO);" in out
    assert "ECLI:DE:SGBE:2019:1023.S83KA43.19.00;Sozialgericht Berlin;23.10.2019;S 83 KA 43/19;00;Vertrags(zahn)arztrecht;" in out
    assert "ECLI:DE:OVGNI:2020:0506.13LB190.19.00;Niedersächsisches Oberverwaltungsgericht;06.05.2020;13 LB 190/19;00;Unbekanntes Registerzeichen!;" in out
    assert "ECLI:DE:BSG:2019:200219BGS1180;BSG;Großer Senat;20.02.2019;GS 1/18;0;Beschluss;Verfahren vor dem Großen Senat;" in out

def test_read_from_file_batch(capsys):
    ecli_liste = parse_ecli.get_input("tests/teststrings.txt", batchmode=True)
    match_list = parse_ecli.analyse_file_batch(ecli_liste)
    assert match_list[0].court_data["court"][1] == "BVerfG"
    assert match_list[3].court_data["date"][1] == "31.05.2016"
    assert match_list[7].court_data["az"][1] == "I ZR 176/18"
    assert match_list[10].court_data["az"][1] == "3 Ni 32/17 (EP)"



##################
