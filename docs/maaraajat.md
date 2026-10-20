# Määräajat ja muistutukset

[In English](deadlines.md)

Rekisterinpitäjällä on kuukausi aikaa vastata poisto- tai tietopyyntöön.
Tällä sivulla kerrotaan, miten työkalu laskee kuukauden, milloin se muistuttaa
ja mitä tehdä, jos vastausta ei tule.

Säännöt perustuvat tietosuoja-asetuksen 12 artiklan 3 kohtaan ja Euroopan
tietosuojaneuvoston (EDPB) [ohjeeseen 01/2022 oikeudesta saada pääsy tietoihin](https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-012022-data-subject-rights-right-access_en),
versio 2.1, kohdat 159–162. Ohje soveltaa EU:n yleisiä määräaikasääntöjä
(asetus 1182/71). Se on kirjoitettu tietopyynnöistä, mutta 12 artiklan
3 kohta antaa poistopyynnölle saman määräajan.

## Näin kuukausi lasketaan

| Sääntö | Esimerkki |
| --- | --- |
| Kuukausi alkaa päivästä, jona rekisterinpitäjä saa pyyntösi. | Saapui 5.3. |
| Määräaika päättyy seuraavan kuukauden samana päivänä. | Vastaus viimeistään 5.4. |
| Jos seuraavassa kuussa ei ole samaa päivää, määräaika päättyy kuun viimeisenä päivänä. | 31.8. → 30.9., 31.1. → 28.2. (karkausvuonna 29.2.) |
| Jos määräaika päättyy lauantaina tai sunnuntaina, se siirtyy maanantaille. | La 5.4.2025 → ma 7.4.2025 |
| Myös arkipyhä siirtää määräajan seuraavaan arkipäivään. | Työkalu ei tunne pyhiä, tarkista ne kalenterista |

Kuukautta kuvataan usein 30 päiväksi, mutta se ei aina ole 30 päivää.
Helmikuu on lyhyempi ja osa kuukausista on 31 päivän mittaisia. Työkalu laskee
kalenterikuukausia samoin kuin EDPB:n ohje.

Työkalu laskee päivästä, jona lähetät pyynnön. Sähköposti ja verkkolomake
saapuvat yleensä samana päivänä. Kirjeen kohdalla kuukausi alkaa vasta, kun
kirje saapuu, joten todellinen määräaika on muutaman päivän myöhemmin kuin
seurantataulukossa.

## Lisäaika

Rekisterinpitäjä voi jatkaa määräaikaa kahdella kuukaudella, jos pyyntö on
monimutkainen tai pyyntöjä on paljon. Siitä on kerrottava sinulle ensimmäisen
kuukauden aikana perusteluineen. EDPB:n mukaan lisäaika on poikkeus eikä
tavallinen käytäntö.

Kun rekisterinpitäjä ottaa lisäaikaa, merkitse riville tila `extended`.
Työkalu laskee silloin kolme kuukautta pyynnön saapumisesta samoilla kuun
lopun ja viikonlopun säännöillä. Jos sama rekisterinpitäjä kysyy myöhemmin
henkilöllisyyttäsi, pidä tila `extended` ja täytä `identity_sent_on`, kun
olet vastannut. Kolme kuukautta lasketaan silloin siitä päivästä.

## Kun rekisterinpitäjä kysyy henkilöllisyyttäsi

Rekisterinpitäjä voi pyytää tietoja, joita se tarvitsee henkilöllisyytesi
varmistamiseen (12 artiklan 6 kohta). Pyynnön on oltava oikeassa suhteessa
tarpeeseen. Kopiota henkilökortista tarvitaan harvoin, jos kirjoitat siitä
sähköpostiosoitteesta, joka on liitetty käyttäjätiliisi.

EDPB:n mukaan määräaika on keskeytyneenä, kunnes rekisterinpitäjä saa
pyytämänsä tiedot, jos se pyysi niitä ilman aiheetonta viivytystä. Merkitse
tilaksi `identity_requested`. Kun olet vastannut, kirjoita päivämäärä
sarakkeeseen `identity_sent_on`.

Työkalu laskee silloin uuden kuukauden sarakkeen `identity_sent_on`
päivästä. Se on myöhäisin määräaika, johon rekisterinpitäjä voisi vedota.
Todellinen keskeytys voi päättyä aiemmin, koska rekisterinpitäjän kysymystä
edeltäneet päivät on jo laskettu. Myöhäisemmän päivän ansiosta työkalu ei
koskaan kehota karhuamaan liian aikaisin.

## Muistutukset

Työkalu laskee jokaiselle pyynnölle kolme päivää määräajasta:

| Päivä | Milloin | Mitä teet |
| --- | --- | --- |
| `reminder_on` | 5 päivää ennen määräaikaa | Tarkista, onko vastaus tai edes vastaanottokuittaus tullut. |
| `follow_up_on` | Määräajan jälkeinen päivä | Lähetä lyhyt muistutus, jossa viittaat alkuperäiseen pyyntöön ja sen päivämäärään. |
| `escalate_on` | 14 päivää määräajan jälkeen | Harkitse valitusta valvontaviranomaiselle. |

`gdpr-kit due --tracker tracker.csv` listaa rivit, jotka vaativat jonkin näistä
toimista tänään. Rivit, joiden tila on `completed`, `refused` tai `escalated`,
ovat suljettuja eivätkä enää näy. Aja komento kerran viikossa tai laita se
kalenteriin.

Viiden ja 14 päivän välit ovat työkalun omia oletuksia, eivät laissa
säädettyjä rajoja. Voit tehdä valituksen valvontaviranomaiselle milloin
tahansa.

## Kun vastausta ei tule

1. Muistuta kerran kirjallisesti. Lainaa alkuperäistä pyyntöäsi, kerro sen
   lähetyspäivä ja kulunut määräaika.
2. Säilytä kaikki: pyyntö, rekisterinpitäjän vastaukset ja seurantarivi.
3. Tee valitus valvontaviranomaiselle 77 artiklan nojalla. Voit valita
   viranomaisen maasta, jossa asut tai työskentelet tai jossa rikkomus
   tapahtui. EDPB pitää yllä [luetteloa kansallisista viranomaisista](https://www.edpb.europa.eu/about-edpb/about-edpb/members_en).
   Suomessa viranomainen on [tietosuojavaltuutetun toimisto](https://tietosuoja.fi/etusivu).

Kieltäytyminenkin on vastaus. Rekisterinpitäjän on kerrottava syy ja se, että
voit valittaa tai viedä asian tuomioistuimeen (12 artiklan 4 kohta). Kirjaa
syy sarakkeeseen `outcome` ja merkitse tilaksi `refused`.

## Taulukkolaskenta komentorivin sijaan

Samat säännöt toimivat taulukkolaskennan kaavoina. Katso [Google Sheets](google-sheets.md).
