dependency:
  python3 
  jupyter (najlakse je instalirati anacondu3)
  exuberant-ctags (apt-get install)

ako python3 nije u /usr/bin/ navesti drugi putanju u kernel.json datoteci
koja se nalazi medju dobijenim fajlovima

da bi se kernel registrovao potrebno je kopirati kernel.json u
/usr/local/share/jupyter/kernels/jezgro
mozete pokrenuti copy.sh za to


da bi se uspesno pokrenuo jupyter direktorijum 'jezgro' mora da bude dostupno.
recimo da postoji PYTHONPATH env sa putanjom do tog direktorijuma 
(ne da pokazuje na jezgro direktorijum !!!)

recimo ako je jezgro u home direktorijumu dodati u .bashrc:
export PYTHONPATH="/home/<username>/:$PYTHONPATH"
Ili cd 'do direktorjima koji sadrzi jezgro direktorijum' i onda pokrenuti jupyter

jupyter se moze pokrenuti na dva nacina:
1. Kao konzolna apliakcija: jupyter console --kernel jezgro
2. Kao notebook: jupyter notebook

Prva varijanta dozvoljava samo liniski ulaz (tesko je proceniti kad kod C++a
'\n' predstavlja kraj ulaza)

po pokretanju notebooka moze se naci i otvorit primer.ipynb iz direktorijuma
Primetiti da nigde nema 'include za iostream i using namespace'. To je zato
sto je to vec izvrseno pri inicijalizaciji kernela. Po potrebi korisnik
moze da izvrsi dodatne include naredbe ili da koristi druge imenske prostore

trenutno sve sto se unese u celiju se tretira kao deklaracija ili definicija.
Ako zelimo da se neka komanda izvrsi kao u sklopu main funkcije korsitmo magic %r
(skraceno od run)
recimo %r cout << "hello";
ili koristimo na pocetku celije cell magic (mora pocetak)
%%r sto ce sav tekst celije tretirati kao kod koji se izvrsava

Nedostaci:
  - strukture i klase nisu podrzane kao i auto keyword.
    Ctags se korsiti umesto libclang-a tako da je poprilicno ad-hoc.
  - segmentation fault ubija server
  - nije moguce definisati simbole istog imena 
    tacnije moguce je prvi put kad se pokrene. Ali ako se pozove simbol u nekoj
    trecoj celiji loader ce naci onu prvu definiciju simbola prvo. (velika man)
  - code completition (tab) ne radi (tacnije vraca nesto bezveze)

preporucuje se citanje shell.py jer kod lepo objasnjava ideju izvrsavanja.
tags.py nije refaktorisan i malo je ruzan

Postoji primer kako se libclangom moze parsirati kod u dodatnim primerima.
Potreban je libclang.so (LD_LIBRARY_PATH do njega je potreban)
I potrebni su libclang python bindings da budu dostupni pythonu
Ovaj primer nije bitan samo pokazuje da moze da se seta kroz AST. Postoji output.txt
da pokaze kako izgleda. Ne znamo kako type deduction da izvedemo ?

Postoji primer za komunikaciju sa ycm youCompleteMe serverom
za autocompletition baziranim na libclang biblioteci. Ocigledno potrebno
je imati server ali kako nismo mi bas pisali ovaj primer nema poente pokretati ga.

