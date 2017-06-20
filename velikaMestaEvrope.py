import re
import os
from pip._vendor import requests


#1.) Pripravi seznam velikih evropskih mest in ga uskladi z podatki iz spletne strani:
# http://www.weatherbase.com/weather/country.php3?r=EUR&regionname=Europe

def popravi_zapis(niz):

    razdeli = niz.split()
    popravljeno = ('-').join(razdeli)

    if popravljeno == 'Vatican-City-(Holy-See)':
        popravljeno = 'Holy-See'

    elif popravljeno == 'Iceland':
        popravljeno = 'Faroe-Islands'

    elif popravljeno == 'Reykjavik':
        popravljeno = 'Torshavn'

    elif popravljeno == 'Tirana':
        popravljeno = 'Tirane'

    elif popravljeno == 'Kyiv':
        popravljeno = 'Kiev'

    return popravljeno

#---------------------------------------------------------------------------------------

def glavna_mesta_drzav():

    '''
    Pripavi seznam drzave in enega izmed njenih najvecjih mest. (Ne nujno Prestolnice, kadar zanjo ni zadostnih podatkov).
    '''

    naslov = 'https://www.countries-ofthe-world.com/capitals-of-europe.html'
    r = requests.get(naslov)
    besedilo = r.text


    iskani_niz = r'<tr( class="grey"|)><td>(?P<drzava>\D*?)</td><td>(?P<prestolnica>\D*?)</td></tr>'
    iscemo = re.compile(iskani_niz , flags=re.DOTALL)

    slovarVelikihMest = dict()
    for najdeni in re.finditer(iscemo, besedilo):

        Prestolnica = popravi_zapis(najdeni.group('prestolnica'))
        Drzava = popravi_zapis(najdeni.group('drzava'))


        slovarVelikihMest[Drzava] = Prestolnica

    #Popravi izjeme:
    slovarVelikihMest['Monaco'] = 'Monte-Carlo'

    return slovarVelikihMest


#-----------------------------------------------------------------------------------------------------

#2.) KORAK: Priprava parametrov, ki so potrebni za dostop do vseh spletnih strani, ki jih želimo zajeti.

def najdi_drzave():

    '''
    Poisce parametre za URLje spletnih strani posameznih drzav.
    '''

    naslov = 'http://www.weatherbase.com/weather/country.php3?r=EUR&regionname=Europe'
    r = requests.get(naslov)
    besedilo = r.text

    slovar_parametrov = dict()

    iskani_niz = r'<li><a class="redglow" href="/weather/\D*?.php3\?c=(?P<kratica>\D*?)&name=(?P<ime>\D*?)" onClick="recordOutboundLink'
    iscemo = re.compile(iskani_niz , flags=re.DOTALL)

    for drzava in re.finditer(iscemo, besedilo):

        slovar_parametrov[drzava.group('ime')] = '{}&name={}'.format(drzava.group('kratica'),drzava.group('ime'))

    return slovar_parametrov



#-----------------------------------

def najdi_mesto(besedilo, ime):

    '''
    Sprejme vsebino spletne strani in ime (drzava, mesto) ter poisce sifro mest.
    Zapiše jih v obliki parametrov za URLje podstrani.
    '''

    parameter = list()
    iskani_niz = r'<li><a class="redglow" href="/weather/weather.php3\?s=(?P<sifra>\d*?)&cityname=' + ime
    iscemo = re.compile(iskani_niz , flags=re.DOTALL)

    for najdeni in re.finditer(iscemo, besedilo):

        parameter += ['s={}&cityname={}'.format(najdeni.group('sifra'),ime)]

    return parameter

#---------------------------------

#NE DELA ZA UNITED KINGDOM!!!!!!!'c=GB&s=ENG&statename=England-United-Kingdom'


def zajemi_drugo(parametri_drzav, slovarPrestolnic):

    '''
    Sprejme seznam parametrov za URLje drzav in iskanih mest,
    ki jih zajame in v njih pojisce koncne parametre.
    '''

    koncni_parametri = list()

    for drzava, parameter in parametri_drzav.items():

        for drzava2, prestolnica in slovarPrestolnic.items():


            if drzava == drzava2 and drzava != 'United-Kingdom':

                ime = slovarPrestolnic[drzava] + '-' + drzava
                #print(ime)

                naslov = r'http://www.weatherbase.com/weather/city.php3?c=' + parameter
                r = requests.get(naslov)
                koncni_parametri += najdi_mesto(r.text, ime)

    return koncni_parametri


#--------------------------------
#3.) KORAK: Funkcije, ki so v pomoč pri shranjevanju darotek in shranjevanje.

def ustvari_mapo():

    '''
    Ustvari mapo z danim imenom.
    '''

    if not os.path.exists('velikaMestaEvrope'):
        os.mkdir('velikaMestaEvrope')



#-------------------------

def shranjevanje( parametri):

    '''
    Zajame vsebino spletnih strani in jo shrani v datoteke.
    '''

    imena_datotek = list()
    for parameter in parametri:


        #Izjema zaradi UnicodeEncodeError(\xf8):
        if parameter == 's=88410&cityname=Oslo-Norway':

            naslov = 'http://www.weatherbase.com/weather/weather.php3?' + parameter
            r = requests.get(naslov)

            besedilo = r.text.replace('\xf8','')

        #V splosnem:
        else:

            naslov = 'http://www.weatherbase.com/weather/weather.php3?' + parameter
            r = requests.get(naslov)
            besedilo = r.text


        ime = parameter.split('=')
        pot = os.getcwd() + '\\' + 'velikaMestaEvrope'
        imena_datotek += [pot + '\\' + ime[2]]

        if (ime[0] + '.txt') not in os.listdir(pot):

            with open(pot + '\\' + ime[2] + '.txt','w') as f:
                f.write(besedilo)
                f.close()
                print('Datoteka ' + ime[2] + ' shranjena!')

    return imena_datotek




#-----------------------------------

def najdi_podatke(besedilo):

    '''
    Sprejme vsebino spletne strani in na njej poisce parametre,
    ki jih zelimo analizirati: id, drzavo, mesto, temperature (v fahrenheitih).
    '''

    iscemo = re.compile(r'<meta name="city" content="(?P<mesto>\D*?)">.*?'
                        r'<meta name="country" content="(?P<drzava>\D*?)">.*?'
                        r'http://www.weatherbase.com/weather/weather.php3\?s=(?P<id>\d+)&cityname=.*?'
                        r'type=Average.Temperature&units=Fahrenheit.*?symbol=F&data=(?P<temperature>.*?)"><img'
    , flags=re.DOTALL)

    for najdeni in re.finditer(iscemo, besedilo):

        return [[najdeni.group('mesto'),najdeni.group('drzava'),najdeni.group('id'),najdeni.group('temperature')]]

#----------------------------------------------

def poisciPodatke(imena_datotek):

    '''
    Sprejme imena datotek v katerih poisce iskane podatke in jih zapise v seznam.
    '''

    podatki = list()

    for ime in imena_datotek:

        with open(ime + '.txt', 'r') as f:
            podatki += najdi_podatke(f.read())

    return podatki



#----------------------------------------

#4.) KORAK: Podatke pretvori v ustrezno obliko in jih zapiše v CSV datoteko.

def iz_fahrenheit_to_celzij(niz):

    '''
    Sprejme niz vrednostih v fahrenheitih, ločenih z vejicami in vrne seznam vrednosti v celzijih
    '''

    seznam_ne_pretvorjenih = niz.split(',')
    ze_pretvorjeni = list()
    celzij = 0

    for fahrenheit in seznam_ne_pretvorjenih:

        celzij = round((float(fahrenheit) - 32) * (5 / 9),1)
        ze_pretvorjeni += [str(celzij)]

    return ze_pretvorjeni

#------------------------------------

def povprecje(sez):

    '''
    Sprejme seznam nizov stevil in vrne njihovo povprecno vrednost.
    '''

    povprecna_vrednost = 0

    for stevilo in sez:
        povprecna_vrednost += float(stevilo)

    return str(povprecna_vrednost // len(sez))

#-------------------------------------------------------------

def uredi_podatke(podatki):

    '''
    V vhodnih podatkih popravi temperature in doda njihovo letno povprecje.
    '''

    urejeniPodatki = list()

    for mesto in podatki:

        temperature = iz_fahrenheit_to_celzij(mesto[3])
        povprecnaLetna = povprecje(temperature)
        urejeniPodatki += [mesto[:3] + temperature + [povprecnaLetna]]

    return urejeniPodatki



#-------------------------------------

def pretvori_v_csv(podatki):

    '''
    Podatke iz seznama seznamov zapise v csv datoteko.
    '''

    with open('podatkiVelikaMesta.txt','w') as csvFile:
        naslovnaVrstica = 'MESTO,Drzava,sifra,januar,februar,marec,april,maj,junij,julij,avgust,' \
        'september,oktober,november,december,LETNO POVPRECJE' + '\n'
        csvFile.write(naslovnaVrstica)
        for vrstica in podatki:
            csvFile.write(','.join(vrstica) + '\n')

    csvFile.close()



#------------------------------------------

def pozeni_VelikaMestaEvrope():

    Prestolnice = glavna_mesta_drzav()
    #print(Prestolnice)

    parametri = najdi_drzave()
    #print(parametri)

    vsi_parametri = zajemi_drugo(parametri, Prestolnice)
    #print(vsi_parametri)

    ustvari_mapo()
    imena_dat = shranjevanje(vsi_parametri)


    podatki1 = poisciPodatke(imena_dat)
    #print(podatki1)

    podatki2 = uredi_podatke(podatki1)
    #print(podatki2)

    pretvori_v_csv(podatki2)

#pozeni_VelikaMestaEvrope()


