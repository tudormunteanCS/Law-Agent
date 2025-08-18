# import re
#
# text = """
# (1)În exercitarea atribuţiilor ce îi revin, ministrul emite ordine şi instrucţiuni cu caracter normativ sau individual.
# (2)Prin ordine se pot aproba norme metodologice, regulamente sau alte categorii de reglementări care sunt parte componentă a ordinului prin care se aprobă.
# (3)Actele administrative cu caracter normativ, neclasificate, potrivit legii, emise de ministru se publică în Monitorul Oficial al României, Partea I.
# (4)Actele prevăzute la alin. (1) sunt semnate de miniştri sau de persoanele delegate de aceştia.
# (5.1)Aprecierea necesităţii şi oportunitatea emiterii actelor administrative ale miniştrilor aparţin exclusiv acestora.
# (6)Prevederile alin. (1)-(5) se aplică, în mod corespunzător, şi în cazul conducătorilor altor organe de specialitate ale administraţiei publice centrale din subordinea Guvernului şi a ministerelor care au rang de secretar de stat sau subsecretar de stat.
# """
#
# # matches = re.split(r'(?=^\s*\(\d+\))',text) # bad deoarece ^ ia inceputul textului
# matches = re.split(r'(?=^\s*\(\d+(?:\.\d+)*\))',text, flags=re.MULTILINE) # good deoarece multi line schimba comportamentul ^ si face sa ia inceputul fiecarei linii
# # Remove empty strings if any
# matches = [part.strip() for part in matches if part.strip()]
#
# for m in matches:
#     alineat_match = re.match(r'^\s*\((\d+(?:\.\d+)*)\)', m)
#     alin = alineat_match.group(1)
#     print(f"Alineat {alin}: {m.strip()}\n")
#


# blocks = [
#     '{"sursa": "Codul Civil", "articol": "Art. 1681", "aliniat": 1, "text": "(1)Vânzarea este pe încercate atunci când se încheie sub condiţia suspensivă ca, în urma încercării, bunul să corespundă criteriilor stabilite la încheierea contractului ori, în lipsa acestora, destinaţiei bunului, potrivit naturii sale."}',
#     '{"sursa": "Codul Civil", "articol": "Art. 1669", "aliniat": 1, "text": "(1)Când una dintre părţile care au încheiat o promisiune bilaterală de vânzare refuză, nejustificat, să încheie contractul promis, cealaltă parte poate cere pronunţarea unei hotărâri care să ţină loc de contract, dacă toate celelalte condiţii de validitate sunt îndeplinite."}',
#     '{"sursa": "Codul Civil", "articol": "Art. 1179", "aliniat": 1, "text": "(1)Condiţiile esenţiale pentru validitatea unui contract sunt:\n1.capacitatea de a contracta;\n2.consimţământul părţilor;\n3.un obiect determinat şi licit;\n4.o cauză licită şi morală."}',
#     '{"sursa": "Codul Civil", "articol": "Art. 1187", "aliniat": null, "text": "Oferta şi acceptarea trebuie emise în forma cerută de lege pentru încheierea valabilă a contractului.\n"}',
#     '{"sursa": "Codul Civil", "articol": "Art. 1666", "aliniat": 1, "text": "(1)În lipsă de stipulaţie contrară, cheltuielile pentru încheierea contractului de vânzare sunt în sarcina cumpărătorului."}',
#     '{"sursa": "Codul Civil", "articol": "Art. 1838", "aliniat": 1, "text": "(1)Contractul de arendare trebuie încheiat în formă scrisă, sub sancţiunea nulităţii absolute."}',
#     '{"sursa": "Codul Civil", "articol": "Art. 1178", "aliniat": null, "text": "Contractul se încheie prin simplul acord de voinţe al părţilor, dacă legea nu impune o anumită formalitate pentru încheierea sa valabilă.\n"}',
#     '{"sursa": "Codul de procedură civilă", "articol": "Art. 839", "aliniat": 1, "text": "(1)Publicaţiile de vânzare vor cuprinde următoarele menţiuni:\na)denumirea şi sediul organului de executare;\nb)numărul dosarului de executare;\nc)numele executorului judecătoresc;\nd)numele şi domiciliul ori, după caz, denumirea şi sediul debitorului, ale terţului dobânditor, dacă va fi cazul, şi ale creditorului;\ne)titlul executoriu în temeiul căruia se face urmărirea imobiliară;\nf)identificarea imobilului cu arătarea numărului cadastral sau topografic şi a numărului de carte funciară, precum şi descrierea lui sumară;\ng)preţul la care a fost evaluat imobilul;\nh)menţiunea, dacă va fi cazul, că imobilul se vinde grevat de drepturile de uzufruct, uz, abitaţie sau servitute, intabulate ulterior înscrierii vreunei ipoteci, şi că, în cazul în care creanţele creditorilor urmăritori nu ar fi acoperite la prima licitaţie, se va proceda în aceeaşi zi la o nouă licitaţie pentru vânzarea imobilului liber de acele drepturi. Preţul de la care vor începe aceste licitaţii va fi cel prevăzut la art. 846 alin. (6) şi (7);\ni)ziua, ora şi locul vânzării la licitaţie;\nj)somaţia pentru toţi cei care pretind vreun drept asupra imobilului să îl anunţe executorului înainte de data stabilită pentru vânzare, în termenele şi sub sancţiunile prevăzute de lege;\nk)invitaţia către toţi cei care vor să cumpere imobilul să se prezinte la termenul de vânzare, la locul fixat în acest scop şi până la acel termen să prezinte oferte de cumpărare;\nl)menţiunea că ofertanţii sunt obligaţi să depună, până la termenul de vânzare, o garanţie reprezentând 10% din preţul de pornire a licitaţiei;\nm)semnătura şi ştampila executorului judecătoresc."}',
#     '{"sursa": "Codul Civil", "articol": "Art. 2445", "aliniat": 5, "text": "(5)În toate cazurile, vânzarea trebuie realizată într-o manieră comercial rezonabilă în ceea ce priveşte metoda, momentul, locul, condiţiile şi toate celelalte aspecte ale acesteia."}',
#     '{"sursa": "Codul Civil", "articol": "Art. 1759", "aliniat": 3, "text": "(3)În cazul în care vânzătorul nu exercită opţiunea în termenul stabilit, condiţia rezolutorie care afecta vânzarea este considerată a nu se fi îndeplinit, iar dreptul cumpărătorului se consolidează."}']
#
# context = "\n\n".join(blocks)
# print(repr(context))