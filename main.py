# encoding=utf8

from urllib.request import urlopen
from bs4 import BeautifulSoup
from collections import Counter
import asyncio

def nacitanieURLs(sutazURL):
    #pripojenie a nacitanie url sutaze
    htmlfile = urlopen(sutazURL)
    soup = BeautifulSoup(htmlfile, "html.parser")
    htmltext = htmlfile.read()

    #ziskanie url zapasov
    result = soup.find_all('div', {"class" : "result"})
    urls = []
    for i in result:
        temp = i.attrs['onclick']
        urls.append(temp[temp.find("='")+2 : -2])
    return urls

def getStringSuperi(soup):
    muzstva = soup.find_all('div', {"class": "team-title"})
    domaci = muzstva[0]
    hostia = muzstva[1]
    return domaci.get_text() + " - " + hostia.get_text()

def getStringVysledok(soup):
    skore = str(soup.find('div', {"class": "score"}).get_text()).strip('\r\n')
    skore = ((skore[:skore.find("(")-1]) + (skore[skore.find("("):skore.find(")")+1])).rstrip('\n')
    if (skore[skore.find("(")-1:skore.find("(")]).isdigit():
        return skore.replace("(", " (")
    else:
        skore = skore[:skore.find("(")-1] + skore[skore.find("("):]
        return skore.replace("(", " (")

def nacitajZostavy(skratky, playersList):
    prvy = True
    domaci = []
    hostia = []

    for x in playersList.find_all('div', {"class": "col col-xs-7 p-name"}):
        if (prvy):                  #kazdy druhy hrac je domaci
            domaci.append(str(x.get_text()).replace(" (C)", ""))
            prvy = False
        else:
            hostia.append(str(x.get_text()).replace(" (C)", ""))
            prvy = True

    if not skratky:
        zostavy = [domaci, hostia]
    else:
        zostavy = [urobSkratky(domaci, nacitajFrekventovane(domaci)), urobSkratky(hostia, nacitajFrekventovane(hostia))]

    return zostavy

def nacitajFrekventovane(arr):
    priezviska = []
    for i in arr:
        x = i.split()
        priezviska.append(x[len(x) - 1])

    pocetP = Counter(priezviska)
    frekventovane = []
    for i in pocetP:
        if pocetP[i] > 1:
            frekventovane.append([i])

    return frekventovane

def urobSkratky(arr, frekventovane):
    meno = ""
    skratene = []
    for i in arr:
        x = i.split()
        meno = str(x[0][0:1]) + ". "
        x = x[1:]
        for j in x:
            meno += j + " "
        skratene.append(meno[:-1])

    for i in frekventovane:
        count = 0
        while (count < len(skratene)):
            x = skratene[count].split()
            if ''.join(i) == x[len(x) - 1]:
                skratene[count] = arr[count]
            count += 1

    return skratene

def nacitajZaklad(playersList, zostavy, skratky):
    domaci = zostavy[0]
    hostia = zostavy[1]

    if len(domaci) <= 11:           #ak nastupilo <= 11 hracov, vsetci su v zaklade
        zakladDomaci = domaci
    else:                           #inak iba prvych 11
        zakladDomaci = domaci[:11]
    if len(hostia) <= 11:
        zakladHostia = hostia
    else:
        zakladHostia = hostia[:11]

    #striedania
    striedania = []
    for x in playersList.find_all('div', {"class": "action fl ac-striedanie"}):
        striedania.append(x['title'])

    if not skratky:
        zaklad = [nacitajStriedania(zakladDomaci, striedania, skratky), nacitajStriedania(zakladHostia, striedania, skratky)]
    else:
        frekventovane = nacitajFrekventovane(domaci) + nacitajFrekventovane(hostia)
        striedania = upravStriedania(striedania, frekventovane)
        zaklad = [nacitajStriedania(zakladDomaci, striedania, skratky), nacitajStriedania(zakladHostia, striedania, skratky)]

    return zaklad

def nacitajStriedania(zaklad, striedania, skratky):
    if not skratky:
        for i in striedania:
            for x, hrac in enumerate(zaklad):
                if str(hrac) == i[:i.find("<")-1]:
                    index = i.find(" (")
                    i = str(i).replace(" <->", i[i.find(" ("):i.find(")")]).replace("'", ".")
                    zaklad[x] = i[:index] + ")"
    else:
        for i in striedania:
            for x, hrac in enumerate(zaklad):
                if str(hrac) == i[:i.find("(") - 1]:
                    zaklad[x] = i

    return zaklad

def upravStriedania(striedania, frekvetovane):
    mena = []
    casy = []
    count = 0

    while (count < len(striedania)):
        temp = striedania[count]
        prvy = temp[:temp.find(" <")]
        mena.append(prvy)

        druhy = temp[temp.find(">") + 2:temp.find(" (")]
        mena.append(druhy)

        cas = str(temp[temp.find(" ("):temp.find(")")]).replace("'", ". ")
        casy.append(cas)

        count += 1

    upravene = urobSkratky(mena, frekvetovane)

    count = 0
    i = 0
    while (count < len(striedania)):
        striedania[count] = upravene[i] + casy[count] + upravene[i+1] + ")"
        count +=1
        i+=2

    return striedania

def getStringZaklad(zaklad):
    domaci = "DOMÁCI: "
    hostia = "HOSTIA: "

    for i in zaklad[0]:
        domaci += i + ", "
    for i in zaklad[1]:
        hostia += i + ", "

    return str((domaci[:-2].replace(", ", " - ", 1) + "\n" + hostia[:-2].replace(", ", " - ", 1)).replace("(C)", "")).replace(" ,", ",")

def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)

def nacitajViacAkoJedenGol(goly):
    mena = []
    for i, item in enumerate(goly):
        if item.find("(z 11m)") > -1:
            mena.append(item[item.find(".") + 2:item.find("(")])
        else:
            mena.append(item[item.find(".") + 2:])

    pocet = Counter(mena)
    frekventovane = []
    for i in pocet:
        if pocet[i] > 1:
            frekventovane.append([i, pocet[i]])

    viacGolov = ""
    zmaz = []
    for i in frekventovane:
        for j in goly:
            if j[j.find(".") + 2:] == i[0]:
                viacGolov += j[:j.find(".") + 1] + ", "
                zmaz.append(j)

        for j in zmaz:
            goly.remove(j)
        zmaz = []

        viacGolov = viacGolov[:-2] + " "
        viacGolov += i[0]
        viacGolov = rreplace(viacGolov, ",", " a", 1)
        goly.append(viacGolov)
        viacGolov = ""

    return goly

def urobSkratkyGoly(zostava, goly):
    kratke = []
    for gol in goly:
        if gol.find("(") > -1:
            kratke.append(gol[gol.find(".") + 2:gol.find("(") - 1])
        else:
            kratke.append(gol[gol.find(".") + 2:])
    domaci = urobSkratky(zostava, nacitajFrekventovane(zostava))

    for i, gol in enumerate(kratke):
        golArr = str(gol).split()
        for hrac in domaci:
            hracArr = str(hrac).split()
            if golArr[len(golArr) - 1] == hracArr[len(hracArr) - 1]:
                if (str(hrac).find(".")) > -1:
                    x = str(goly[i])
                    if x.find("(") > -1:
                        goly[i] = x[:x.find(".") + 1] + " " + hrac + " " + x[x.find("("):x.find(")")+1]
                    else:
                        goly[i] = x[:x.find(".") + 1] + " " + hrac
    return goly

def getStringGoly(playersList, zostavy, skratky):
    goly = []
    domaci = zostavy[0]
    hostia = zostavy[1]

    for x in playersList.find_all('div', {"class": "action fl ac-gol"}):
        gol = x['title']
        gol = gol[gol.find(" - ") + 3:]
        gol = str((gol[gol.find('(') + 1:gol.find(')')] + gol[:gol.find("(") - 1]).replace("'", ". ")).replace(" (C)", " ")
        goly.append(gol)

    # pokutovy kop
    for x in playersList.find_all('div', {"class": "action fl ac-penalty"}):
        gol = x['title']
        gol = gol[gol.find(" - ") + 3:]
        gol = str((gol[gol.find('(') + 1:gol.find(')')] + gol[:gol.find("(") - 1]).replace("'", ". ")).replace(" (C)", " ")
        goly.append(gol + " (z 11m)")

    # vlastny gol
    for x in playersList.find_all('div', {"class": "action fl ac-gol-own"}):
        gol = x['title']
        gol = gol[gol.find(" - ") + 3:]
        gol = str((gol[gol.find('(') + 1:gol.find(')')] + gol[:gol.find("(") - 1]).replace("'", ". ")).replace(" (C)", " ")
        goly.append(gol + " (vl. gol)")

    # standardne situacie
    for x in playersList.find_all('div', {"class": "action fl ac-gol-standard"}):
        gol = x['title']
        gol = gol[gol.find(" - ") + 3:]
        gol = str((gol[gol.find('(') + 1:gol.find(')')] + gol[:gol.find("(") - 1]).replace("'", ". ")).replace(" (C)", " ")
        goly.append(gol)

    # rozdelenie golov na dve polia
    golyD = []
    golyH = []
    nasiel = False

    if skratky:
        goly = urobSkratkyGoly(domaci, goly)
        goly = urobSkratkyGoly(hostia, goly)
        for i in goly:
            if i.find("(") > -1:
                gol = i[i.find(".") + 2: i.find("(") - 1]
            else:
                gol = i[i.find(".") + 2:]

            for hrac in domaci:
                if hrac == gol:
                    if i.find("vl. gol") > -1:
                        golyH.append(i)
                        golyH.sort()
                    else:
                        golyD.append(i)
                        nasiel = True
                        break

            for hrac in hostia:
                if hrac == gol:
                    if i.find("vl. gol") > -1:
                        golyD.append(i)
                        golyD.sort()
                    else:
                        golyH.append(i)
                        nasiel = True
                        break
            nasiel = False
    else:
        for i in goly:
            if i.find("(") > -1:
                gol = i[i.find(".") + 2: i.find("(") - 1]
            else:
                gol = i[i.find(".") + 2:]

            for hrac in domaci:
                if hrac == gol:
                    if i.find("vl. gol") > -1:
                        golyH.append(i)
                        golyH.sort()
                    else:
                        golyD.append(i)
                        nasiel = True
                        break

            for hrac in hostia:
                if hrac == gol:
                    if i.find("vl. gol") > -1:
                        golyD.append(i)
                        golyD.sort()
                    else:
                        golyH.append(i)
                        nasiel = True
                        break
            nasiel = False


    #ak dal jeden hrac viac ako jeden gol, uprav goly
    if len(golyD) > 1:
        golyD = nacitajViacAkoJedenGol(golyD)
    if len(golyH) > 1:
        golyH = nacitajViacAkoJedenGol(golyH)

    golyDstr = golyHstr= ""

    if len(golyD) > 0:
        for gol in golyD:
            golyDstr += gol + ", "
        golyDstr = golyDstr[:-2]
        if len(golyH) > 0:
                golyDstr += " - "
    if len(golyH) > 0:
        for gol in golyH:
            golyHstr += gol + ", "
        golyHstr = golyHstr[:-2]

    if len(golyD) > 0 or len(golyH) > 0:
        return "Góly: " + golyDstr + golyHstr + ", "
    else:
        return ""

def getStringKarty(playersList):
    karty = []
    for x in playersList.find_all('div', {"class": "action fl ac-cervenakarta"}):
        karta = x['title']
        karta = karta[karta.find("-") + 2:karta.find(")") + 1]
        karta = (karta[karta.find('(') + 1:karta.find(')')] + karta[:karta.find("(") - 1]).replace("'", ". ")
        karty.append(karta)

    if len(karty) > 0:
        kartyStr = "ČK: "
        for karta in karty:
            kartyStr += karta + ", "
        return kartyStr[:-2]

def getStringRozhodca(soup):
    for i in soup.find_all('div', {"class": "clearfix bg-white col-inner"}):
        rozhodca = i.find('div', {"class": "person-dlg"}).get_text()
        if rozhodca.find("Rozhodca: ")>-1:
            rozhodca = rozhodca[rozhodca.find(':')+2:-1]
            break
    return "R: " + rozhodca

def getStringDivaci(soup):
    divaci = soup.find('div', {"class": "m-audience"}).get_text()
    return divaci[13:] + " divákov"

#######################################################################################################################
def main(soup, liga, skratkaGoly, skratkaZostavy):
    playersList = soup.find('table', {"class": "table table-match"})

    zapas = []
    superi = getStringSuperi(soup)
    vysledok = getStringVysledok(soup)
    zapas.append(superi + " " + vysledok)

    if liga == 'osem':
        if skratkaGoly:
            skratkaZostavy = True
        zostavy = nacitajZostavy(skratkaZostavy, playersList)
        zapas.append(getStringGoly(playersList, zostavy, skratkaGoly)[:-2])

    if liga == 'sedem':
        skratkaGoly = skratkaZostavy = True
        rozhodca = getStringRozhodca(soup)
        divaci = getStringDivaci(soup)
        zostavy = nacitajZostavy(skratkaZostavy, playersList)
        zapas.append(getStringGoly(playersList, zostavy, skratkaGoly) + str(rozhodca) + ", " + str(divaci))

    if liga == 'pat':
        if skratkaZostavy:
            skratkaGoly = True
        rozhodca = getStringRozhodca(soup)
        divaci = getStringDivaci(soup)

        zostavy = nacitajZostavy(skratkaZostavy, playersList)
        zapas.append(getStringGoly(playersList, zostavy, skratkaGoly)+ str(rozhodca) + ", " + str(divaci))
        zapas.append(getStringZaklad(nacitajZaklad(playersList, zostavy, skratkaZostavy)))

        karty = getStringKarty(playersList)
        if karty != None:
            zapas.append(karty)

    return zapas

async def async_crawler(urls, liga, skratkaGoly, skratkaZostavy):
    loop = asyncio.get_event_loop()
    futures = [
        loop.run_in_executor(None, urlopen, url)
        for url in urls
    ]

    vystup = []
    for index, response in enumerate(await asyncio.gather(*futures)):
        soup = BeautifulSoup(response.read(), 'html.parser')
        vystup.append(main(soup, liga, skratkaGoly, skratkaZostavy))
    return vystup

def getStringVystup(url, liga, skratkaGoly, skratkaZostavy):
    urls = nacitanieURLs(url)
    loop = asyncio.get_event_loop()

    return loop.run_until_complete(async_crawler(urls, liga, skratkaGoly, skratkaZostavy))