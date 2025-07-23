import re

text = """
(1)În exercitarea atribuţiilor ce îi revin, ministrul emite ordine şi instrucţiuni cu caracter normativ sau individual.
(2)Prin ordine se pot aproba norme metodologice, regulamente sau alte categorii de reglementări care sunt parte componentă a ordinului prin care se aprobă.
(3)Actele administrative cu caracter normativ, neclasificate, potrivit legii, emise de ministru se publică în Monitorul Oficial al României, Partea I.
(4)Actele prevăzute la alin. (1) sunt semnate de miniştri sau de persoanele delegate de aceştia.
(5.1)Aprecierea necesităţii şi oportunitatea emiterii actelor administrative ale miniştrilor aparţin exclusiv acestora.
(6)Prevederile alin. (1)-(5) se aplică, în mod corespunzător, şi în cazul conducătorilor altor organe de specialitate ale administraţiei publice centrale din subordinea Guvernului şi a ministerelor care au rang de secretar de stat sau subsecretar de stat.
"""

# matches = re.split(r'(?=^\s*\(\d+\))',text) # bad deoarece ^ ia inceputul textului
matches = re.split(r'(?=^\s*\(\d+(?:\.\d+)*\))',text, flags=re.MULTILINE) # good deoarece multi line schimba comportamentul ^ si face sa ia inceputul fiecarei linii
# Remove empty strings if any
matches = [part.strip() for part in matches if part.strip()]

for m in matches:
    alineat_match = re.match(r'^\s*\((\d+(?:\.\d+)*)\)', m)
    alin = alineat_match.group(1)
    print(f"Alineat {alin}: {m.strip()}\n")

