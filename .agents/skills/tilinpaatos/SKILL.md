---
name: tilinpaatos
description: Kaivaa Oulun kaupungin tilinpäätös-PDF:stä rahavirtatiedot (tulot ja menot) ja tuottaa niistä Sankey-kaavion datatiedoston (JSON) puumuodossa. Käytä tätä taitoa aina kun käyttäjä antaa Oulun (tai vastaavan kunnan) tilinpäätös-PDF:n ja haluaa siitä rahavirta-, tulo-/meno- tai budjettivisualisoinnin, Sankey-kaavion, tai pyytää "kaivamaan luvut", "tekemään JSONin uudelle vuodelle", "erottelemaan tulot ja menot" tai "näyttämään mihin rahat menevät". Käytä myös kun käyttäjä haluaa eritellä alakategorioita (esim. mistä veroista verotulot koostuvat, mihin palkat tai palvelujen ostot jakautuvat) tai lisätä uuden vuoden olemassa olevaan vuosivertailuun. Soveltuu erityisesti sote-uudistuksen (2023→) jälkeisiin tilinpäätöksiin.
---

# Oulun tilinpäätös → Sankey-JSON

Tämä taito kuvaa, miten Oulun kaupungin tilinpäätös-PDF:stä kaivetaan rahavirtatiedot ja kootaan ne Sankey-kaavion käyttämään JSON-puuhun. Tavoite on, että jokainen vuosi eritellään yhtä tarkasti — myös alakategoriat (verolajit, kululajit, palkkojen ja palvelujen ostojen jako) — ja että tulot ja menot täsmäävät täsmälleen.

## Keskeinen periaate: kaksi suuretta, ei sekaisin

Tilinpäätöksessä on kaksi eri rahavirtakäsitettä, jotka EIVÄT ole sama asia:

1. **Tilikauden tulos / yli-/alijäämä** — lasketaan vain toiminnan tuotoista, kuluista ja poistoista. Ei sisällä investointeja eikä lainoja.
2. **Koko rahankäyttö (kassavirta)** — sisältää myös investoinnit, lainat ja kassavarojen muutoksen.

Tämä Sankey kuvaa **koko rahankäyttöä**, ei tulosta. Siksi mukaan otetaan lainat, investoinnit ja kassan muutos, ja molemmat puolet (lähteet vasemmalla, käyttö oikealla) täsmäävät täsmälleen. Tilikauden ali-/ylijäämä EI näy puolten erotuksena — tämä on tarkoituksellista ja se selitetään kaavion alaviitteessä. Älä yritä saada Sankeytä näyttämään alijäämää; se on eri suure.

## Työnkulku

1. **Pura PDF tekstiksi.** Käytä `pdftotext -layout tiedosto.pdf out.txt`. `-layout` säilyttää taulukoiden sarakerakenteen, mikä on välttämätöntä numeroiden poiminnassa. Tarkista sivumäärä ja otsikko `pdfinfo`-komennolla; varmista että vuosi on se mitä odotat.

2. **Hae ylätason luvut** kahdesta päälaskelmasta (tuloslaskelma ja rahoituslaskelma) ja kululajitaulukosta. Ks. tarkat rivit ja sanamuodot alla. Apuna voi käyttää `scripts/kaiva_tilinpaatos.py`-skriptiä, joka etsii ylätason rivit joustavilla regexeillä ja tulostaa JSON-rungon + raportin siitä mitkä luvut löytyivät ja mitkä jäivät tarkistettaviksi. Skripti EI laske välisummia eikä arvaa — se on lähtökohta, ei lopullinen totuus. Tarkista sen tulos aina taulukoita vasten, koska sanamuodot vaihtelevat vuosittain ja osa eristä (vuokrat, korkokulut, omaisuuden myynti, lainojen lyhennys) vaatii kahden rivin yhteenlaskun.

3. **Pura alakategoriat** (lapset). Osa löytyy suoraan virallisista taulukoista, osa pitää jakaa arvioiden. Ks. `references/alakategoriat.md`.

4. **Laske kassa-tasauserä** niin että tulot = menot. Ks. "Tasapainotus".

5. **Kokoa JSON** sivun skeemaan ja **validoi**: jokaisen vanhemman arvon tulee täsmätä lastensa summaan, ja tulojen summan tulee täsmätä menojen summaan.

6. **Merkitse arviot rehellisesti.** Jokaiseen arvioituun (ei suoraan tilinpäätöksestä tulevaan) lukuun `"arvio": true` ja `lahde`-kenttään selitys jakoperusteesta.

## Mistä ylätason luvut löytyvät

Hae nämä erät. Sanamuodot ja sivut vaihtelevat vuosittain, joten etsi otsikolla (grep), älä sivunumerolla.

### Tuloslaskelmasta (otsikko "TULOSLASKELMA", kaupungin koko laskelma)
Sarakkeista käytä uusinta vuotta (yleensä vasemmanpuoleisin lukusarake, "TP<vuosi>"). Luvut ovat **tuhansina euroina (1 000 €)** → jaa 1000:lla miljooniksi, ja ota itseisarvo (menot näkyvät miinusmerkkisinä).

| Erä | JSON id | Rivin otsikko | Puoli |
|-----|---------|---------------|-------|
| Verotulot | `verot` | "Verotulot" | tulo |
| Toimintatuotot | `toimtuotot` | "Toimintatuotot" | tulo |
| Valtionosuudet | `valtio` | "Valtionosuudet" | tulo |
| Rahoitustuotot (brutto) | `rahoitus` | "Korkotuotot" + "Muut rahoitustuotot" (laske yhteen) | tulo |
| Korko- ja rahoituskulut | `korkokulut` | "Korkokulut" + "Muut rahoituskulut" (laske yhteen) | meno |

### Ulkoiset toimintakulut -taulukosta (kululajeittain, otsikko "ULKOISET TOIMINTAKULUT")
| Erä | JSON id | Rivin otsikko |
|-----|---------|---------------|
| Henkilöstökulut | `henk` | "Henkilöstökulut" |
| Palvelujen ostot | `palv` | "Palvelujen ostot" |
| Aineet ja tarvikkeet | `aineet` | "Aineet, tarvikkeet ja tavarat" |
| Avustukset | `avust` | "Avustukset" |
| Vuokrat ja muut | `vuokrat` | "Vuokrakulut" + "Muut toimintakulut" (laske yhteen) |

### Rahoituslaskelmasta (otsikko "RAHOITUSLASKELMA")
| Erä | JSON id | Rivin otsikko | Puoli |
|-----|---------|---------------|-------|
| Investoinnit | `invest` | "Investointimenot" | meno |
| Omaisuuden myynti ja rah.osuudet | `myynti` | "Pysyvien vastaavien hyödykkeiden luovutustulot" + "Rahoitusosuudet investointeihin" | tulo |
| Antolainojen takaisinmaksut | `antolaina_in` | "Antolainasaamisten vähennys" | tulo |
| Lainojen lyhennykset | `lyhennys` | "Pitkäaikaisten lainojen vähennys" (lisää lyhytaik. jos negatiivinen) | meno |
| Lainanotto | `laina` tai `lyhytlaina` | ks. "Lainat vaihtelevat" | tulo |

## Lainat vaihtelevat vuosittain — tarkista aina

Lainaerät ovat se kohta, joka muuttuu eniten vuodesta toiseen. Tarkista rahoituslaskelmasta:

- **"Pitkäaikaisten lainojen lisäys"** — jos tämä rivi on olemassa ja positiivinen, kaupunki nosti pitkäaikaista lainaa → lähde `laina` (luokka `rahoitus`). 2025: 150 M€. 2023 ja 2024: rivi puuttui (ei nostettu).
- **"Lyhytaikaisten lainojen muutos"** — jos positiivinen, lyhytaikaiset lainat kasvoivat → rahaa sisään, lähde `lyhytlaina` (luokka `rahoitus`). 2023: +105,6 M€, 2024: +33,4 M€. Jos negatiivinen, ne vähenivät → yhdistä menopuolen `lyhennys`-erään.
- **"Pitkäaikaisten lainojen vähennys"** — aina meno `lyhennys` (lainojen lyhennys).

Sääntö: jokainen lainaerä joka **tuo** rahaa on lähde (vasen), jokainen joka **vie** rahaa on käyttö (oikea). Älä oleta edellisvuoden rakennetta.

## Tasapainotus (kassa-erä)

Kun kaikki muut erät on poimittu, laske kassa-tasauserä niin että tulot = menot:

```
erotus = (menojen summa) − (lähteiden summa ilman kassaa)
```

- Jos **erotus > 0** (käyttö > lähteet): kaupunki kattoi erotuksen kassavaroistaan → lisää **lähteisiin** `kassa`, nimi "Kassavarojen väheneminen ja muut maksuvalmius", luokka `kassa`, arvo = erotus.
- Jos **erotus < 0** (lähteet > käyttö): rahaa jäi yli → lisää **menoihin** `kassa`, nimi "Kassavarojen lisäys ja muut maksuvalmius", arvo = |erotus|.

Tämä erä kokoaa rahoituslaskelman "Rahavarojen muutos" + "Muut maksuvalmiuden muutokset" yhdeksi tasauseräksi, jotta kaavio menee tasan eikä raha katoa. Selitä `lahde`-kentässä että kyseessä on tasauserä.

Pyöristys: kaikki luvut yhteen desimaaliin. Pyöristyksen takia tulot ja menot voivat erota 0,1–0,2 M€. Säädä **kassa-erää** ±0,1 niin että summat ovat täsmälleen yhtä suuret.

## JSON-skeema

Sivu (oulu-sankey-data.html) lukee tämän muodon. Älä laske välisummia sivulla — **jokaisella solmulla on oma `arvo`**, myös vanhemmilla.

```json
{
  "vuosi": 2025,
  "yksikko": "milj. €",
  "otsikko": "Mistä rahat tulevat ja mihin ne menevät",
  "kuvaus": "Koko rahankäyttö vuonna 2025: ...",
  "tulot": [ <solmu>, ... ],
  "menot": [ <solmu>, ... ]
}
```

Solmu:
```json
{
  "id": "verot",                    // pysyvä tunniste, SAMA joka vuosi
  "nimi": "Verotulot",              // näyttönimi
  "arvo": 508.9,                    // miljoonaa euroa, annetaan joka tasolla
  "luokka": "tulo",                 // ylätason solmuissa: tulo | meno | rahoitus | kassa
  "lahde": "Tuloslaskelma (Verotulot)",  // näkyy solmun alla ja tooltipissä
  "arvio": true,                    // VAIN jos luku ei tule suoraan tilinpäätöksestä
  "lapset": [ <solmu>, ... ]        // alakategoriat, sama rakenne rekursiivisesti
}
```

Värit tulevat `luokka`-kentästä: `tulo`=vihreä, `meno`=oranssi, `rahoitus`=violetti (lainat ja investoinnit), `kassa`=harmaa. Lapsisolmut perivät vaaleamman sävyn automaattisesti — niihin ei tarvitse `luokka`-kenttää.

**id:t on pidettävä samoina vuosien yli.** Sama `verot_kunnallis` joka vuosi. Tämä mahdollistaa vuosivertailun ja säilyttää drill-down-tilan. Käytä `references/id-luettelo.md`:n vakiintuneita id:itä.

## Alakategorioiden erottelu

Tämä on taidon ydin: jokainen vuosi eritellään yhtä tarkasti. Lue **`references/alakategoriat.md`** ennen alaerien kasaamista — siellä on jokaisen erän tarkka jakoperuste, mitkä ovat virallisia ja mitkä arvioita, sekä laskentakaavat (esim. palkkojen jako henkilötyövuosien suhteessa).

Lyhyt yhteenveto siitä mikä on suoraan saatavilla vs. arvioitava:

- **Suoraan virallisesta taulukosta** (ei `arvio`-merkintää): verolajit (kunnallis-, kiinteistö-, yhteisövero), toimintatuottojen erittely (myynti, vuokrat, maksut, tuet, muut), henkilöstökulujen kululajit (palkat, eläkkeet, sivukulut), palvelujen ostojen ylin jako (asiakaspalvelut / muut), palvelusetelit.
- **Arvioitava** (`"arvio": true`): henkilöstökulujen jako palveluittain (htv-suhteessa), palvelujen ostojen lautakuntajako, investointien kohdejako, avustusten alaerät. Nämä eivät löydy koko kaupungin tasolla yhtenä taulukkona, vaan ne on koottava lautakunta-/hankekohtaisista tiedoista.

Jos käyttäjä on pyytänyt vain ylätason erittelyä, jätä `lapset` tyhjäksi (`[]`) ja kerro että alaerät voi täyttää myöhemmin. Jos käyttäjä haluaa 2025-tason tarkkuuden, erottele kaikki `references/alakategoriat.md`:n mukaisesti.

## Sote-uudistus: vertailukelpoisuus

**Sosiaali- ja terveyspalvelut siirtyivät hyvinvointialueille 1.1.2023.** Tämä halkaisee aikasarjan:

- **2023 ja uudemmat**: kaupungilla ei enää sote-tehtäviä. Verotulot ~500 M€, toimintakulut ~750–800 M€. Nämä vuodet ovat **keskenään vertailukelpoisia**.
- **2022 ja vanhemmat**: sote mukana. Verotulot ~950 M€, toimintakulut ~1 500 M€ — noin kaksinkertaiset.

Jos kaivat 2022 tai aiemman vuoden, **merkitse `kuvaus`-kenttään selvästi** ettei se ole vertailukelpoinen uudempien kanssa, koska 2022→2023 "pudotus" ei ole säästö vaan tehtävien siirto pois kaupungilta. Älä laita eri puolilla uudistusta olevia vuosia samaan vertailuun ilman tätä huomautusta.

## Validointi ennen valmista

Aja nämä tarkistukset (esim. lyhyt Python-skripti) ja korjaa ennen kuin esität tuloksen:

1. **Vanhempi = lasten summa.** Jokaiselle solmulle jolla on `lapset`: `abs(arvo − sum(lapset.arvo)) < 0,3`. Jos ei täsmää, joko arvo tai jokin alaerä on väärin.
2. **Tulot = menot.** `abs(sum(tulot.arvo) − sum(menot.arvo)) < 0,15`. Jos ei, kassa-erä on väärin laskettu.
3. **Arviot merkitty.** Jokainen luku joka ei tullut suoraan taulukosta on `"arvio": true`.
4. **Järkevyys.** Vertaa edellisvuoteen: jos jokin erä muuttui rajusti, varmista että se on todellinen (esim. investoinnit voivat heilua paljon) eikä poimintavirhe (esim. väärä sarake).

## Tuotteen muut osat

- **Sivu** `oulu-sankey-data.html` on datavetoinen: lisää uusi vuosi viemällä JSON `data/oulu-talous-<vuosi>.json` -polkuun JA lisäämällä vuosiluku sivun `YEARS`-listaan (`const YEARS = [2025, 2024, 2023];`). Pelkkä JSON ei riitä — dropdown rakennetaan listasta.
- Sivu tekee saman tasapaino- ja summavalidoinnin ja näyttää varoituksen jos puolet eivät täsmää.

## Esimerkki: 2025-tuloksen ylätaso (tarkistusarvot)

Käytä näitä sanity-checkinä jos kaivat 2025:n: verot 508,9 · toimintatuotot 202,9 · valtionosuudet 142,1 · rahoitustuotot 30,8 · lainanotto 150,0 · omaisuuden myynti 14,6 · antolainat 3,5 · kassa 15,1 (tulot yht. 1 067,9). Menot: henkilöstö 392,2 · palvelujen ostot 254,7 · avustukset 79,2 · aineet 47,3 · vuokrat 27,1 · investoinnit 170,8 · korkokulut 14,7 · lyhennykset 81,9 (menot yht. 1 067,9).

## Taidon sisältö

- `SKILL.md` — tämä tiedosto: työnkulku, ylätason luvut, tasapainotus, skeema, validointi.
- `references/alakategoriat.md` — alaerien tarkat jakoperusteet (virallinen vs. arvio, laskentakaavat). Lue ennen alaerien kasaamista.
- `references/id-luettelo.md` — vakiintuneet solmu-id:t, jotta vuodet pysyvät vertailukelpoisina.
- `scripts/kaiva_tilinpaatos.py` — ylätason luvut kaivava apuskripti (`python3 kaiva_tilinpaatos.py tiedosto.pdf --vuosi 2024 -o data/`). Vaatii `pdftotext` (poppler).
- `assets/esimerkki-2025.json` — täysin eritelty 2025-data mallirakenteena. Käytä esikuvana siitä, miltä valmis JSON näyttää, ja id:ien lähteenä.
