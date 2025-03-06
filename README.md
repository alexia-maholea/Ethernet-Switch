1 2 3

Maholea Elena-Alexia - 333CD

Pentru primul task, cel cu forwarding, m-am folosit de pseudocodul
de pe ocw, pe care l-am implementat. (dacă cunoaștem destinația, trimitem
direct către ea, în caz contrar, se face flooding)

În continuare, pentru a adăuga funcționalitatea de VLAN, mai întâi am
creat o funcție ajutătoare pentru a citi fișierul de configurări
și de a memora pentru fiecare port tipul (access sau trunk) și vlan id ul.
În cazul în care portul este trunk, în loc de vlan, am ales să folosesc -1.

Apoi, de fiecare dată când trimitem un pachet, verificăm pe ce fel de port
urmează să trimitem, ținând cont și de cel de pe care l-am primit, astfel:
- dacă primesc de pe acces -> trimit pe acces, nu e nevoie de header 802.1q

- dacă primesc de pe acces -> trimit pe trunk, trebuie să adăugăm header-ul

- dacă primesc de pe trunk -> trimit pe trunk, nu e nevoie de adăugare pentru
că există deja

- dacă primesc de pe trunk -> trimit pe acces, trebuie să scoatem header-ul


Pentru algoritmul de STP, am făcut inițializările conform ocw
și apoi am implementat funcția din thread-ul paralel.

În funcția send_bdpu_every_sec, verific dacă switch-ul este root, iar în
caz că da, construim un packet BDPU pe care îl trimitem pe toate porturile trunk.
Am folosit metoda struct.pack() '!Q' pentru 8 bytes, iar în pachet am adăugat
mac-ul destinație, sursă și apoi conform ocw, root bridge id, sender bridge id și
costul.

Dacă am primit un pachet BDPU (adică o adresă multicast), am implementat
algoritmul STP după scheletul din temă, unde avem două stări: blocked și
listening.

Dacă adresa e unicast și cunoaștem MAC-ul destinației, avem forwarding normal,
iar dacă e broadcast sau nu se află în tabela MAC, se face flooding.