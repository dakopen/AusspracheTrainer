# AusspracheTrainer
Der AusspracheTrainer analysiert mithilfe von künstlicher Intelligenz die Aussprache eines vor- oder eingegebenen Satzes. Dies ist das GitHub Repository zur [AusspracheTrainer.org Webseite](https://aussprachetrainer.org).

### Wichtiger Hinweis:
Dieses Repository dient ausschließlich zur Offenlegung des Quellcodes. 
Der AusspracheTrainer wird in Zukunft Teil eines größeren, Sprachenübergreifenden Programms, daher werden leider keine Feature-Updates in diesem Repository kommen. 

Wenn Du mitarbeiten möchtest, melde Dich gerne bei kontakt@aussprachetrainer.org. 


## Features

### Verständlichkeitsüberprüfung
Der AusspracheTrainer kann Deine Artikulation sicher und schnell überprüfen und Dir eine farblich leicht erkennbare Rückmeldung geben.

### Logopädische Analyse
Die Logopädische Auswertung wurde in Zusammenarbeit mit der logopädischen Praxis von Tina Hillebrecht entwickelt.

Sprachfehler, die erkannt werden: 
* Sigmatusmus ("S")
* Schitismus ("SCH")
* Chetismus ("CH")

Weitere (seltenere) Sprachfehler sind in neueren Versionen geplant.

### Transkripte Anzeigen
Lass Dir per Knopfdruck (gedrückt halten) die jeweiligen Transkripe von Google, IBM und der AusspracheTrainerIPAKI anzeigen. Das hilft Dir besser zu erkennen, was andere Menschen möglicherweise verstehen.


### Satzgenerator
Dir fällt kein geeigneter Satz ein, den Du üben möchtest? Kein Problem, lass Dir per Knopfdruck einen zufälligen oder logopädischen Satz generieren.



### AusspracheTrainerIPAKI
Ein wesentlicher Bestandteil des AusspracheTrainers ist die eigens entwickelte AusspracheTrainerIPAKI, die eine Audio direkt in Lautschrift transkribiert.
> Hier kannst Du mehr über die KI erfahren, die den Bundeswettbewerb für Künstliche Intelligenz gewonnen hat (BWKI) https://github.com/dakopen/AusspracheTrainer-BWKI




## Installationshinweise
Auch wenn das Repository nicht zur Mitarbeit gedacht ist, hält Dich niemand davon ab es zu installieren und verwenden.
#### Torchaudio benötigt ein Soundfile Backend:
* Linux/macOS: pip install sox
* Windows: pip install PySoundFile

#### Warum sind gibt es mehrere settings.py Files?
Das hat mit der Konfiguration des Webservers zu tun. Ausschließlich die settings.py Datei (und andere Dateien) im Ordner **webprojekt** sind relevant!

#### Wofür ist die Datenbank db.sqlite3?
Die Datenbank wird nicht verwendet, allerdings kann es sein, dass sie in zukünftigen Releases eine wichtige Rolle spielt, daher wurde sie bisher noch nicht gelöscht.


## Abschließende Überlegungen
Beim Trainieren unserer KI kamen Frauen- (9%) und Männeranteile (69%) nicht gleichverteilt zur Sprache. Außerdem können Altersunterschiede Einfluss auf eine von der KI falsch verstandene Aussprache haben.

Gleiches gilt, aber im viel kleineren Sinne für die KIs von Google und IBM. Maschinelles Lernen funktioniert anders als menschliche Gehirne - eine unnatürliche und besonders lebhafte und trotzdem richtige Betonung wird von Maschinen oft als Fehler anerkannt.

**Diese Software ersetzt keinesfalls eine logopädische Fachkraft. Falls ein Verdacht auf Sprachfehler besteht, wenden Sie sich bitte an eine logopädische Praxis in Ihrer Umgebung.**

## Kontakt
Daniel Busch - dakopen185@gmail.com

Projektlink: https://github.com/dakopen/AusspracheTrainer/

Webseite: https://AusspracheTrainer.org


## Quellenangabe wichtiger Komponenten
Eine ausführliche Quellenangabe gibt es auf der Projektwebseite: https://aussprachetrainer.org/sources/

