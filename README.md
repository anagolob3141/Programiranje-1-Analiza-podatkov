# Vremenska analiza europskih mest
### Seminarska naloga pri predmetu programiranje 1

## Zajem podatkov
podatki so bili zajeti iz spletnih strani https://www.countries-ofthe-world.com/capitals-of-europe.html ter http://www.weatherbase.com/weather/country.php3?r=EUR&regionname=Europe.

Zajeti podatki so:
* šifra
* država
* glavno mesto
* povprečne temperature posameznih mesecev
* povprečne količine padavin v posameznih mesecih

## Predvidena analiza:
1. Preveriti ali obstaja medsebojna odvisnost med količino padavin, temperaturo in geografsko lego v posameznih krajih.
2. Izračunati standardni odklon temperatur med meseci in preveriti ali obstaja soodvisnost med nihanji temperature in količine padavin.
3. Podatke prikazati na zemljevidu.

### Dodakek k analizi: Analiza izbrane države

V skripti analiza2Del.ipynb se nahaja še dodatek k analizi, v katerem lahko uporabnih sam preko GUI izbira med podatki. V tem delu podameznik izbere eno izmed Europskih držav, nato pa še mesec in željeno temperaturo. Program mu nato predstavi mesta, ki najbolj ustrezajo njegovemu izboru.

## Knjižnjice, ki jih je potrebno namestiti pred zagonom programa:
* requests
* numpy
* re
* pandas
* os
* matplotlib.pyplot
* mpl_toolkits.basemap
* geopy.geocoders
* tkinter



