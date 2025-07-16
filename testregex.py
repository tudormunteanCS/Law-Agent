import re

text = """(1)Prezentul cod intră în vigoare la data care va fi stabilită în legea pentru punerea în aplicare a acestuia.*)
*) În temeiul art. 220 alin. (1) din Legea nr. 71/2011 pentru punerea în aplicare a Legii nr. 287/2009 privind Codul civil, publicată în Monitorul Oficial al României, Partea I, nr. 409 din 10 iunie 2011, Codul civil intră în vigoare la data de 1 octombrie 2011.
(2)În termen de 12 luni de la data publicării prezentului cod, Guvernul va supune Parlamentului spre adoptare proiectul de lege pentru punerea în aplicare a Codului civil."""

matches = re.split(r'(?=\(\d+\))',text) # asa imi ia  -> ?= lookahead
for i, m in enumerate(matches, 1):
    print(f"Alineat {i}: {m.strip()}\n")
