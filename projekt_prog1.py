
from pip._vendor import requests
import re
import orodja

#=========================================================================================

def zajemi_prvo():
    '''Funkcija zajame besedilo prve spletne strani.'''
    naslov = 'http://www.weatherbase.com/weather/country.php3?r=EUR&regionname=Europe'
    r = requests.get(naslov)
    return r.text

vsebina_prve = zajemi_prvo()
#print(vsebina_prve)

#======

def najdi_drzave(besedilo):
    '''V vhodnem besedilu poišče imena vseh Evropskih drzav in jih zapiše v seznam.'''
    seznam_drzav = list()
    seznam_kratic = list()
    seznam_parametrov = list()
    iskani_niz = r'<li><a class="redglow" href="/weather/\D*?.php3\?c=(?P<kratica>\D*?)&name=(?P<ime>\D*?)" onClick="recordOutboundLink'
    iscemo = re.compile(iskani_niz , flags=re.DOTALL)
    for drzava in re.finditer(iscemo, besedilo):
        seznam_drzav += [drzava.group('ime')]
        seznam_kratic += [drzava.group('kratica')]
        seznam_parametrov += ['{}&name={}'.format(drzava.group('kratica'),drzava.group('ime'))]
    return seznam_parametrov

parametri = najdi_drzave(vsebina_prve)
print(parametri)

#============================================================================================================

def najdi_mesta(besedilo):
    '''Sprejme vsebino spletne strani, im pojisce ustrezne parametre za odpiranje podstrani.'''
    seznam_parametrov = list()
    iskani_niz = r'<li><a class="redglow" href="/weather/weather.php3\?s=(?P<sifra>\d*?)&cityname=(?P<ime>\D*?)" onClick="recordOutboundLink'
    iscemo = re.compile(iskani_niz , flags=re.DOTALL)
    for najdeni in re.finditer(iscemo, besedilo):
        seznam_parametrov += ['s={}&cityname={}'.format(najdeni.group('sifra'),najdeni.group('ime') )]
    return seznam_parametrov


def zajemi_drugo(seznam):
    koncni_parametri = list()
    for parameter in seznam:
        naslov = r'http://www.weatherbase.com/weather/city.php3?c=' + parameter
        r = requests.get(naslov)
        koncni_parametri += najdi_mesta(r.text)
    return koncni_parametri

vsi_parametri = zajemi_drugo(parametri)
print(vsi_parametri)

#Opomba: Ne deluje za United Kingdom!!!!!
#=====================================================================================================================

def zajemi_koncno(seznam):
    for parameter in seznam:
        razbiti_parametri = '='.split(parameter[2:])
        ime = razbiti_parametri[len(razbiti_parametri) - 1]
        naslov = 'http://www.weatherbase.com/weather/weather.php3?' + parameter
        datoteka = 'weatherbase/{}.html'.format(ime)
        orodja.shrani(naslov, datoteka)

zajemi_koncno(vsi_parametri)

