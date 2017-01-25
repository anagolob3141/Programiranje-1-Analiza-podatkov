import re
from pip._vendor import requests
import os
import csv
from tkinter import *

#-----------------------------------------------------------------------------------------------------------------------

def zajemi_prvo():

    '''
    Funkcija zajame besedilo prve spletne strani.
    '''

    naslov = 'http://www.weatherbase.com/weather/country.php3?r=EUR&regionname=Europe'
    r = requests.get(naslov)
    return r.text

#-----------------------------------------------------------------------------------------------------------------------

def najdi_drzave():

    '''
    Poisce parametre za URLje spletnih strani posameznih drzav.
    '''

    naslov = 'http://www.weatherbase.com/weather/country.php3?r=EUR&regionname=Europe'
    r = requests.get(naslov)
    besedilo = r.text

    seznam_drzav = list()
    slovar_parametrov = dict()

    iskani_niz = r'<li><a class="redglow" href="/weather/\D*?.php3\?c=(?P<kratica>\D*?)&name=(?P<ime>\D*?)" onClick="recordOutboundLink'
    iscemo = re.compile(iskani_niz , flags=re.DOTALL)

    for drzava in re.finditer(iscemo, besedilo):

        seznam_drzav += [drzava.group('ime')]
        slovar_parametrov[drzava.group('ime')] = '{}&name={}'.format(drzava.group('kratica'),drzava.group('ime'))

    return seznam_drzav, slovar_parametrov

#-----------------------------------------------------------------------------------------------------------------------

def odstraniUK(drzave):

    '''
    Spletna strana za United Kingdom je precej drugacna, zato jo trenutno ne bomo upostevali
    ...popravi, ce bo cas!
    '''

    try:
        drzave.remove('United-Kingdom')
    except:
        pass

    return drzave

#-----------------------------------------------------------------------------------------------------------------------

def najdi_mesta(drzava, slovar_parametrov):

    parametri_mest = list()

    naslov = r'http://www.weatherbase.com/weather/city.php3?c=' + slovar_parametrov[drzava]
    r = requests.get(naslov)
    besedilo = r.text

    iskani_niz = r'<li><a class="redglow" href="/weather/weather.php3\?s=(?P<sifra>\d*?)&cityname=(?P<ime>\D*?)" onClick="recordOutboundLink'
    iscemo = re.compile(iskani_niz , flags=re.DOTALL)

    for najdeni in re.finditer(iscemo, besedilo):

        parametri_mest += ['s={}&cityname={}'.format(najdeni.group('sifra'),najdeni.group('ime') )]

    return parametri_mest

#-----------------------------------------------------------------------------------------------------------------------
# Oblikovanje graphical user interface:

#1. POGOVORNO OKNO: Izbiranje drzave

def ustvari_okno1(drzave):


    okno1 = Tk()

    theLabel = Label(okno1, text='Pozdravljeni! \n  Želim vam pomagati najti vaše najljubše mesto.\n Zato prosim, izberi svojo državo.')
    theLabel.pack()


    topFrame = Frame(okno1)
    topFrame.pack()
    bottomFrame = Frame(okno1)
    bottomFrame.pack(side=BOTTOM)

#-----------------------------------------------------------------------------------------------------------------------
    def destroy():
        okno1.destroy()

    def shrani_drzavo(number):

        global izbrana_drzava
        izbrana_drzava = drzave[number]
        destroy()

        #print(izbrana_drzava)

#-----------------------------------------------------------------------------------------------------------------------

    def ustvari_gumbe(imena_drzav):

        '''
        Za vsako drzavo naredi 'gumbe', da jo lahko izberemo s klikom.
        '''



        r=0
        c=0
        for i in range(len(imena_drzav)):

            if i % 5 == 0:
                r += 1
                c = 0
            Button(topFrame, text=imena_drzav[i], fg='red', command=lambda i=i:shrani_drzavo(i)).grid(row=r,column=c)
            c += 1


    ustvari_gumbe(drzave)

    okno1.mainloop()

########################################################################################################################

def najdi_mesta(besedilo):

    '''
    TO JE POMOZNA FUNKCIJA ZA NASLEDNJO FUNKCIJO!!!
    Sprejme vsebino spletne strani in pojisce imena in sifro mest.
    Zapiše jih v obliki parametrov za URLje koncnih spletnih strani, ki jiz zelimo zajeti.
    '''

    seznam_parametrov = list()

    iskani_niz = r'<li><a class="redglow" href="/weather/weather.php3\?s=(?P<sifra>\d*?)&cityname=(?P<ime>\D*?)" onClick="recordOutboundLink'
    iscemo = re.compile(iskani_niz , flags=re.DOTALL)

    for najdeni in re.finditer(iscemo, besedilo):
        parameter = 's={}&cityname={}'.format(najdeni.group('sifra'),najdeni.group('ime') )

        #Popravimo neustrezne znake (unicode error)
        parameter = parameter.replace('ø','%F8')
        parameter = parameter.replace('å','%E5')
        parameter = parameter.replace('æ','%E6')
        parameter = parameter.replace('Å','%C5')
        parameter = parameter.replace('Ø','%D8')

        seznam_parametrov += [parameter]

    return seznam_parametrov

#-----------------------------------------------------------------------------------------------------------------------

def zajemi_drugo(slovar, drzava):

    '''
    Sprejme slovar parametrov v URLju spletnih strani drzav in v njih poišče paramere URLjev za mesta.
    '''

    koncni_parametri = list()

    parameter = slovar[drzava]
    naslov = r'http://www.weatherbase.com/weather/city.php3?c=' + parameter
    r = requests.get(naslov)
    koncni_parametri = najdi_mesta(r.text)

    return koncni_parametri

# Ne dela za United Kingdom!!!

#-----------------------------------------------------------------------------------------------------------------------
# 2.) KORAK: Vsebino spletnih strani shrani v datoteke in nato iz njih prebere potrebne podatke.



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

#-----------------------------------------------------------------------------------------------------------------------


def seznamSPodatki( parametri):

    '''
    Vsebino spletnih strani shrani v datoteke.
    '''

    podatki = list()

    for parameter in parametri:

        naslov = 'http://www.weatherbase.com/weather/weather.php3?' + parameter
        r = requests.get(naslov)
        besedilo = r.text

        podatki += najdi_podatke(besedilo)

    return podatki

#-----------------------------------------------------------------------------------------------------------------------
# 3.) KORAK: Podatke pretvori v ustrezno obliko in jih zapiše v CSV datoteko.

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

#-----------------------------------------------------------------------------------------------------------------------

def povprecje(sez):

    '''
    Sprejme seznam nizov stevil in vrne njihovo povprecno vrednost.
    '''

    povprecna_vrednost = 0

    for stevilo in sez:
        povprecna_vrednost += float(stevilo)

    return str(povprecna_vrednost // len(sez))

#-----------------------------------------------------------------------------------------------------------------------

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


#-----------------------------------------------------------------------------------------------------------------------

def ustvari_mapo(ime):

    '''
    Ustvari mapo z danim imenom.
    '''

    if not os.path.exists(ime):
        os.mkdir(ime)

#-----------------------------------------------------------------------------------------------------------------------


def pretvori_v_csv(podatki):

    '''
    Podatke iz seznama seznamov zapise v csv datoteko.
    '''

    with open( izbrana_drzava + '\\podatki.txt','w') as csvFile:

        naslovnaVrstica = 'MESTO,Drzava,drsifra,januar,februar,marec,april,maj,juni,juli,avgust,' \
        'september,oktober,november,december,LETNO POVPRECJE' + '\n'
        csvFile.write(naslovnaVrstica)

        for vrstica in podatki:
            csvFile.write(','.join(vrstica) + '\n')

    csvFile.close()

########################################################################################################################

def min_max(ime_datoteke):

    '''
    Poisce najveci vnos v csv datoteki, ki predstavlja temperaturo.
    '''

    with open(ime_datoteke) as csvFile:

        csvFile.readline() #Prvo vrstico izpusti.
        maks = -100
        mini = 100

        for vrstica in csvFile:
            sez_podatkov = vrstica.split(',')

            for temperatura in sez_podatkov[3:]:
                povprecna = temperatura.strip('\n')

                if float(povprecna) > maks:
                    maks = float(povprecna)

                if float(povprecna) < mini:
                    mini = float(povprecna)
        csvFile.close()

    return str(mini), str(maks)

#-----------------------------------------------------------------------------------------------------------------------
# 2.) POGOVORNO OKNO: Izbiranje meseca in temperature.

def preveri_pravilen_vnos(temperatura, mini, maksi):

    '''
    Preveri ali je vnos, ki ga uporabnik vnese v vhodno okno kot temperaturo v pravi obliki.
    '''

    try:
        if float(temperatura) < float(maksi) or float(temperatura) > float(mini):
            return True

        else:
            return False

    except:
        return False

#-----------------------------------------------------------------------------------------------------------------------

def ustvari_okno2(minimum, maksimum):
    okno2 = Tk()

    def shrani():

        global temperatura
        global mesec

        mesec = obdobje.get()
        temperatura = e1.get()

        okno2.destroy()

    label_1 = Label(okno2, text='Vaša izbrana država je ' + izbrana_drzava + '!')
    label_2 = Label(okno2, text='V tej državi se temperature v povprečju gibljejo med {}°C in {}°C.'.format(minimum, maksimum))
    label_3 = Label(okno2, text='Spodaj izberi željeno časovno obdobje in temperaturo, med zgornjima vrednostma.')
    label_4 = Label(okno2, text='obdobje:')
    label_5 = Label(okno2, text='temperatura:')
    label_6 = Label(okno2, text='°C')

    obdobje = StringVar(okno2)
    obdobje.set("januar")
    o = OptionMenu(okno2, obdobje, 'januar', 'februar','marec','april','maj','junij','julij','avgust','september','oktober','november','december','letno povprecje')

    e1 = Entry(okno2)

    b = Button(okno2, text="Ok", command=shrani)

    label_1.grid(row=0)
    label_2.grid(row=1, sticky=W)
    label_3.grid(row=2, sticky=W)
    label_4.grid(row=3, sticky=W)
    label_5.grid(row=4, sticky=W)
    label_6.grid(row=4, column=2,sticky=W)
    o.grid(row=3)
    e1.grid(row=4)
    b.grid(row=5)

    okno2.mainloop()

#-----------------------------------------------------------------------------------------------------------------------

# 3.) POGOVORNO OKNO: Prikaže se, kadar je bil vnos temperature napačen in omogoči popravlanje.


def ustvari_okno3(minimum, maksimum):

    pravilenVnos = preveri_pravilen_vnos(temperatura, minimum, maksimum)
    while pravilenVnos == False:

        okno3 = Tk()

        def unici_okno():
            okno3.destroy()

        label_1 = Label(okno3, text='Vaš vnos temperature "{}" je napačen!'.format(temperatura))
        b = Button(okno3, text="Popravi vnos", command=unici_okno)

        label_1.grid(row=0)
        b.grid(row=1)

        okno3.mainloop()
        okno2 = Tk()

        def shrani():

            global temperatura
            global mesec

            mesec = obdobje.get()
            temperatura = e1.get()

            okno2.destroy()

        label_1 = Label(okno2, text='Vaša izbrana država je ' + izbrana_drzava + '!')
        label_2 = Label(okno2, text='V tej državi se temperature v povprečju gibljejo med {}°C in {}°C.'.format(minimum, maksimum))
        label_3 = Label(okno2, text='Spodaj izberi željeno časovno obdobje in temperaturo, med zgornjima vrednostma.')
        label_4 = Label(okno2, text='obdobje:')
        label_5 = Label(okno2, text='temperatura:')
        label_6 = Label(okno2, text='°C')

        obdobje = StringVar(okno2)
        obdobje.set("januar")
        o = OptionMenu(okno2, obdobje, 'januar', 'februar','marec','april','maj','junij','julij','avgust','september','oktober','november','december','letno povprecje')

        e1 = Entry(okno2)

        b = Button(okno2, text="Ok", command=shrani)

        label_1.grid(row=0)
        label_2.grid(row=1, sticky=W)
        label_3.grid(row=2, sticky=W)
        label_4.grid(row=3, sticky=W)
        label_5.grid(row=4, sticky=W)
        label_6.grid(row=4, column=2,sticky=W)
        o.grid(row=3)
        e1.grid(row=4)
        b.grid(row=5)

        okno2.mainloop()

        pravilenVnos = preveri_pravilen_vnos(temperatura, minimum, maksimum)

#-----------------------------------------------------------------------------------------------------------------------
# 4.) KORAK: Ustvari csv datoteke za analizo, glede na izbrane vnose.

slovar = {'januar':1,'februar':2,'marec':3,'april':4,'maj':5,'junij':6,'julij':7,'avgust':8,'september':9,'oktober':10,'november':11,'december':12,'letno povprecje':13}

def razvrsti(temperatura, mesec, izbrana_drzava, slovar):

    '''
    Csv datoteki s podatki doda stolpec, ki pove koliko se v izbranem mesecu temperatura razlikuje od izbrane.
    '''

    razvrsti_po = slovar[mesec] + 2

    with open('razvrscenaZa_' + mesec + '.txt', 'w') as csvIzhodna:

        with open(izbrana_drzava + '\\podatki.txt', 'r') as csvVhodna:

            csvIzhodna.write(csvVhodna.readline().strip() + ',razlika od vnosa,izbrana temperatura\n' ) #Prva vrstica.

            for vrstica in csvVhodna:
                sez_podatkov = vrstica.split(',')
                izbrani = float(sez_podatkov[razvrsti_po])
                razlika = abs(izbrani) - abs(float(temperatura))

                razlika2 = str(round(abs(razlika),2))
                csvIzhodna.write(vrstica.strip() + ',' + razlika2 + ',' + temperatura + '\n')

    csvVhodna.close()
    csvIzhodna.close()

    return 'razvrscenaZa_' + mesec + '.txt'

#-----------------------------------------------------------------------------------------------------------------------
def boljsa_izbira(temperatura):


    '''
    Ustvari slovar mest z meseci v katerih srečamo izbrano temperaturo.
    '''

    priporoceni = dict()

    with open(izbrana_drzava + '\\podatki.txt', 'r') as csvVhodna:

        csvVhodna.readline() #Prvo vrstico izpusti.

        for vrstica in csvVhodna:
            sez_podatkov = vrstica.split(',')

            for indeks in range(3,(len(sez_podatkov))):


                temperatura2 = float((sez_podatkov[indeks]).strip())
                if (float(temperatura) - 0.5) <= temperatura2 <= (float(temperatura) + 0.5):
                    mesto = sez_podatkov[0]

                    if mesto in priporoceni.keys():
                        priporoceni[mesto].append(indeks -2)

                    else:
                        priporoceni[mesto] = [indeks - 2]

    return priporoceni

#-----------------------------------------------------------------------------------------------------------------------

def boljsa_izbira_csv(priporoceni, slovar):

    '''
    Podatke iz slovarja ustrezno zapise v csv datoteko.
    '''


    meseci = list(slovar.keys())

    with open("priporoceni.txt",'w') as csvFile:

        csvFile.write('Mesto,mesec \n')

        for mesto, indeksi in priporoceni.items():
            vrstica = mesto + ', '
            for indeks in indeksi:

                vrstica += meseci[indeks] + '\, '

            csvFile.write(vrstica[:-3] + '\n')

    csvFile.close()

########################################################################################################################

def zazeni_analizaGUI():

    vsebina_prve = zajemi_prvo()
    #print(vsebina_prve)

    drzavee, parametri = najdi_drzave()
    drzave = odstraniUK(drzavee)

    ustvari_okno1(drzave)

    vsi_parametri = zajemi_drugo(parametri, izbrana_drzava)
    #print(vsi_parametri, len(vsi_parametri))

    podatki1 = seznamSPodatki(vsi_parametri)
    #print(podatki1)

    podatki2 = uredi_podatke(podatki1)
    #print(podatki2)

    ustvari_mapo(izbrana_drzava)
    pretvori_v_csv(podatki2)

    minimum, maksimum = (min_max(izbrana_drzava + '\\podatki.txt'))

    ustvari_okno2(minimum, maksimum)
    ustvari_okno3(minimum, maksimum)

    ime_datotekeRazv = razvrsti(temperatura, mesec, izbrana_drzava, slovar)

    priporoceni = boljsa_izbira(temperatura)
    #print(priporoceni)

    boljsa_izbira_csv(priporoceni, slovar)

    print('''
    izbrana drzava: {} \n
    izbrani mesec: {} \n
    izbrana temperatura: {}°C \n
    '''.format(izbrana_drzava, mesec, temperatura))

    return izbrana_drzava, mesec, izbrana_drzava + '\\podatki.txt' , ime_datotekeRazv
