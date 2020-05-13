import re

##################
# Regex für ECLI
##################
# Dieses Modul enthält die Regex-Muster für deutsche ECLI.
# In der ersten Gruppe sind die Muster enthalten, mit denen der
# gesamte ECLI einer Gerichtsbarkeit zugeordnet wird.
#
# Erläuterung der Capture-Groups (soweit nicht selbsterklärend):
# (vgl. https://e-justice.europa.eu/content_european_case_law_identifier_ecli-175-de-de.do?member=1 )
# type = Entscheidungsart. IdR Urteil/Beschluss. Beim BVerfG Bestimmung der Verfahrensart (z.B. Verfassungsbeschwerden)
# bodytype = Spruchkörper (z.B. Senatsentscheidung). Nur bei BVerfG.
# date = Entscheidungsdatum
# collision = Kollisionsnummer, teilweise ist sie optional
# az = Aktenzeichen insgesamt (enthält alle Gruppen, die mit az beginnen)
# azreg = Registerzeichen
# aznumber = Laufende Eingangsnummer
# azyear = Jahresbezeichnung im Az
# azregister/azsuffix = Anhängsel an Az (zb Register bei BSG oder EU/EP bei BPatG)
##################

bverfg = r"""
    (?P<ecli>ECLI):
    (?P<country>DE):
    (?P<court>BVERFG):
    (?P<year>(?:19|20)[0-9]{2}): # Jahresbereich eingeschränkt auf 1900-2000
    (?P<type>[BCEFGHKLMNPQR]|UP|VB) # Nur diese Buchstaben sind hier erlaubt
    (?P<bodytype>[KS])? # Kammer- oder Senatsentscheidung
    (?P<date>(?:19|20)[0-9]{2}(?:0[1-9]|1[012])(?:0[1-9]|[12][0-9]|3[01])) # JJJJMMTT
    (?P<collision>[A-Z])?\.
    (?P<az>(?P<azbody>\d)? # azbody optional bei Verzögerungsbeschwerden
    (?P<azreg>[A-Z]{2,4})
    (?P<aznumber>\d{4})
    (?P<azyear>\d{2}))\b
"""


bgh = r"""
    (?P<ecli>ECLI):
    (?P<country>DE):
    (?P<court>BGH):
    (?P<year>(?:19|20)[0-9]{2}): # Jahresbereich eingeschränkt auf 1900-2000
    (?P<date>(?:0[1-9]|[12][0-9]|3[01])(?:0[1-9]|1[012])[0-9]{2}) # Datum TTMMJJ
    (?P<type>[UBVS]) # Urteil, Beschluss etc.
    (?P<azbody>\d|[IVX]{,4}) # Senatsbezeichnung. Straf = arabische Ziffern, Zivil = Römisch. Kann auch fehlen (zB. Kartellsachen)
    (?P<azreg>[.A-Z]{2,11}) # Registerzeichen. Klammern werden im ECLI als Punkte dargestellt
    (?P<aznumber>\d{1,4})\. # Eingangsnummer
    (?P<azyear>\d{2})\.
    (?P<collision>\d)\b # Stets vorhanden
"""

bpatg = r"""
    (?P<ecli>ECLI):
    (?P<country>DE):
    (?P<court>BPATG):
    (?P<year>(?:19|20)[0-9]{2}):
    (?P<date>(?:0[1-9]|[12][0-9]|3[01])(?:0[1-9]|1[012])[0-9]{2})
    (?P<type>[UB])
    (?P<azbody>[1-2]?[0-9]|3[0-6])
    (?P<azreg>WPAT|NI|LI(?:Q|R)?|(ZA|AR)PAT)
    (?P<aznumber>\d{1,4})\.
    (?P<azyear>\d{2})
    (?P<azsuffix>EP|EU)?\.
    (?P<collision>\d)\b
"""

bverwg = r"""
     (?P<ecli>ECLI):
    (?P<country>DE):
    (?P<court>BVERWG):
    (?P<year>(?:19|20)[0-9]{2}):
    (?P<date>(?:0[1-9]|[12][0-9]|3[01])(?:0[1-9]|1[012])[0-9]{2})
    (?P<type>[UBG])
    (?P<azbody>\d{,2})
    (?P<azreg>[()A-Z]{1,11})
    (?P<aznumber>\d{1,4})\.
    (?P<azyear>\d{2})
    (?P<azsuffix>D)?\.
    (?P<collision>\d)\b
"""

bfh = r"""
    (?P<ecli>ECLI):
    (?P<country>DE):
    (?P<court>BFH):
    (?P<year>(?:19|20)[0-9]{2}):
    (?P<type>[UB]|VV|VE|BA)\.
    (?P<date>(?:0[1-9]|[12][0-9]|3[01])(?:0[1-9]|1[012])[0-9]{2})\.
    (?P<azbody>[IVX]{1,4})?
    (?P<azreg>[()A-Z]{1,11})
    (?P<aznumber>\d{1,4})\.
    (?P<azyear>\d{2})\.
    (?P<collision>\d)\b
"""

bag = r"""
    (?P<ecli>ECLI):
    (?P<country>DE):
    (?P<court>BAG):
    (?P<year>(?:19|20)[0-9]{2}):
    (?P<date>(?:0[1-9]|[12][0-9]|3[01])(?:0[1-9]|1[012])[0-9]{2})\.
    (?P<type>[UB])\.
    (?P<azbody>\d{1,2})?
    (?P<azreg>(?(azbody)[AZRBVN]{3}|GS)) # Bei GS gibt es keine Senatsbezeichnung. Wenn (und nur dann) diese fehlt, wird "GS" gemachtcht (conditional)
    (?P<aznumber>\d{1,4})\.
    (?P<azyear>\d{2})\.
    (?P<collision>\d)\b
"""

bsg = r"""
    (?P<ecli>ECLI):
    (?P<country>DE):
    (?P<court>BSG):
    (?P<year>(?:19|20)[0-9]{2}):
    (?P<date>(?:0[1-9]|[12][0-9]|3[01])(?:0[1-9]|1[012])[0-9]{2})
    (?P<type>[UB]) # Urteil/Beschluss
    (?P<azinstance>B)?
    (?P<azbody>[0-9]|1[0-4]|GS)
    (?P<azreg>[()A-Z]{1,3})?
    (?P<aznumber>\d{1,4}?)
    (?P<azyear>\d{2})
    (?P<azregister>[A-Z]{1,2})?
    (?P<collision>\d)\b
"""

laender = r"""
    (?P<ecli>ECLI):
    (?P<country>DE):
    (?P<court>\w{2,7}):
    (?P<year>(?:19|20)[0-9]{2}):
    (?P<date>(?:0[1-9]|1[012])(?:0[1-9]|[12][0-9]|3[01]))\.
    (?P<az>[\dA-Z\.]{2,15}\.[\dA-Z]{1,15})\.
    (?P<collision>[\dA-Z]{2})\b
"""


##################
# Regex zur weiteren Analyse der Länder ECLI
##################
# Wegen der Vielgestaltigkeit der verschiedenen Aktenzeichen ist die Regex für die Gerichte der Länder wesentlich
# durchlässiger. Ein Treffer muss daher noch weiter analysiert werden. Die folgenden Regex-Muster dienen zum einen
# zur Zuordnung zu einer Gerichtsbarkeit und zum anderen zur Analyse des entsprechenden Az.
#
# Erklärung der Gruppen (soweit abweichend von oben):
# azprefix = Präfix, z.B. III in III-3 RVs 24/12
# azbody_sta = Bei Doppelaktenzeichen für das Dezernat bei der StA (z.B. 350 in 6 KLs 350 Js 1/08)
# azreg_sta = JS in Doppelaktenzeichen
# azer = Eilverfahren bei der Sozialgerichtsbarkeit (Zusatz "ER", auch hinter normalem Register)
# azhessen, azbayern = Länderspezifische Gerichtsbezeichnung als Teil des Az
##################


ordentliche = r"""
    ^(AG|KG|O?LG|BAYO).*?
"""

ordentliche_az = r"""
    (?P<azprefix>[A-Z]{1,4}?)?? # Optional und lazy, tritt daher hinter azreg zurück
    (?P<azbody>\d{1,3})?
    (?P<azreg>[A-Z\.]{1,5})\.?
    (?P<azbody_sta>\d{1,5}(?=JS))? # Matcht nur, wenn ein JS folgt.
    (?P<azreg_sta>JS)?
    (?P<aznumber>\d{1,5})\.
    (?P<azyear>\d{1,2})
    (?P<azsuffix>[A-Z]{1,5})?
"""

sozg = r"""
    ^(?!A(?:RB|G)).*(?:SG).*? # Wenn kein AG oder ARBG (jew. Stuttgart) findet sich "SG" nur bei der Sozialgerichtsbarkeit
"""
sozg_az = r"""
    ^(?P<azinstance>L|S)
    (?P<azbody>\d{1,2})
    (?P<azreg>[ALSYBKLEGRWPOFUÜVJ]{1,3}) # Erlaubte Sachgebiete
    (?P<aznumber>\d{1,4})\.
    (?P<azyear>\d{2})
    (?P<azregister>[ABCRHGSK]{1,2})?\.? # Erlaubte Registerzeichen
    (?P<azer>ER)?$ # Eilsachen
"""

arbg = r"""
    .*(LAG|AR(B)?G).*?
"""

arbg_az = r"""
    ^(?P<azbody>\d{1,2})
    (?P<azreg>[ARBVGHCNSTLO]{1,3})
    (?P<aznumber>\d{1,4})\.
    (?P<azyear>\w?\d{2})$
"""

verwg = r"""
    (?!LVG|SL)(O)?VG.*?
"""

verwg_az = r"""
    (?P<azprefix>OVG)?
    (?P<azbody>\d{1,2})
    (?P<azreg>[A-Z]{1,3})
    (?P<aznumber>\d{1,4})\.
    (?P<azyear>\d{2})($|\.?
    (?P<azhessen>F|KS|DA|GI|WI)?\.? # Hessischer Zusatz für das jeweilige Gericht, z.B. KS für Kassel
    (?P<azregister>A|AK|EK|G|GR|NE|PVB|PVL|S|T|U)? # Registerzusatz z.B. A für Asyl
    $) # End of String in der zweiten Alternative wichtig, damit "33L2274.14" in "33L2274.14PB" nicht matcht
"""

verwg_az_bayern = r""" # Hier weicht das bayerische Schema vom Rest des Landes ab...
    (?P<azbayern>[ABUNROWM]{1,2}) # Gerichtspräfix
    (?P<azbody>\d{1,2})
    (?P<azreg>[ABCDEFIKLMNS]{1,3})
    (?P<azyear>\d{2})\.
    (?P<aznumber>\d{1,5})\.?
    (?P<azregister>A|AK|EK|G|GR|NE|PVB|PVL|S|T|U{,3})?
"""

fg_az = r"""
    (?P<azbody>\d{1,2})
    (?P<azreg>[A-Z]{1,3})
    (?P<aznumber>\d{1,4})\.
    (?P<azyear>\d{2})\.?
    (?P<azregister>[A-Z\.]{1,3})?
"""



bverfg_compiled = re.compile(bverfg,flags=re.VERBOSE)
bgh_compiled = re.compile(bgh,flags=re.VERBOSE)
bverwg_compiled = re.compile(bverwg,flags=re.VERBOSE)
bfh_compiled = re.compile(bfh,flags=re.VERBOSE)
bag_compiled = re.compile(bag,flags=re.VERBOSE)
bsg_compiled = re.compile(bsg,flags=re.VERBOSE)
bpatg_compiled = re.compile(bpatg,flags=re.VERBOSE)
laender_compiled = re.compile(laender,flags=re.VERBOSE)
