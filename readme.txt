za potrebe izvrsavanja koda potrebno je imati:


jupyter notebook se najlakse instalira instalirnjem paketa
anaconda3

potreban je python3
u PYTHONPATH ubaciti putanju do direktorijuma 'jezgro'

u direktorijum jezgro se nalazi kernel.json

napraviti dir ~/.local/share/jupyter/kernels/jezgro
tu smestiti kernel.json
U kernel.json promeniti putanju za python

cd ~/.local/share/jupyter/kernel
nardna komanda registruje kernel jezgro
jupyter kernelspec install jezgro

trebalo bi da bude vidljivo ako se izvrsi
jupter kernelspec list

pokretanje python notebooka treba odraditi u direktorijumu JEZGRO !!!


Za pokretanje clang parse primera
potrebno je imati libclang.so, i python bindinge instlirane
libclang.so mora da bude vidljiv loaderu a python bindnings da se nalaze u PYTHONPATH-u


auto-complete-test
sadrzi fajl python primer koji demonstrira kako se moze povezati na
ycm (you complete me) server za auto completition baziran na clang-u
neophodna je python 2.7, python 3.5 i iskompajlirani ycm server
nismo ga mi pisali

============================
Mogucnosti naseg kernela


kernel moze da izvrsava code, radi do_execute
auto completition ne radi jer nismo stigli da povezemo na ycm server

velika mana trenutno jeste sto se output izvrsenog programa ne vraca
u GUI gde bi se ocekivalo, vec se u GUI vraca samo kod koji se iskompajlira
dok output izvrsavanja biva odstampan u konsoli.

OVo je zapravo zato sto Base Kernel koji nasledjujemo implementira svoj stdout koji koji sakriva originalnu python implementaciju i onemogucava nam da zamenimo file deskriptore.
Zapravo moramo mnogo vise vremena da ulozimo da izucimo kako taj Base kernel zapravo radi, a nigde nema dokumentacija za to.
scanf razume se ne radi.
