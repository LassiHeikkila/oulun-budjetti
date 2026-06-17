# Vakiintuneet id:t

Käytä näitä id:itä joka vuosi, jotta vuosivertailu ja drill-down-tila toimivat. id pysyy samana vaikka nimi tai arvo muuttuisi.

## Tulot
| id | nimi | luokka | huom |
|----|------|--------|------|
| `verot` | Verotulot | tulo | lapset: kunnallis/kiinteisto/yhteiso |
| `verot_kunnallis` | Kunnallisvero | — | |
| `verot_kiinteisto` | Kiinteistövero | — | |
| `verot_yhteiso` | Yhteisövero | — | |
| `toimtuotot` | Toimintatuotot | tulo | lapset alla |
| `tt_myynti` | Myyntituotot | — | |
| `tt_vuokra` | Vuokratuotot | — | |
| `tt_maksu` | Maksutuotot | — | |
| `tt_tuet` | Tuet ja avustukset | — | |
| `tt_muut` | Muut tuotot | — | |
| `valtio` | Valtionosuudet | tulo | |
| `rahoitus` | Rahoitustuotot | tulo | brutto |
| `laina` | Lainanotto | rahoitus | vain jos pitkäaik. lainaa nostettu |
| `lyhytlaina` | Lyhytaikaisten lainojen lisäys | rahoitus | vain jos lyhytaik. kasvoi |
| `myynti` | Omaisuuden myynti ja rah.osuudet | tulo | luovutustulot + rahoitusosuudet |
| `antolaina_in` | Antolainojen takaisinmaksut | tulo | |
| `kassa` | Kassavarojen väheneminen ja muut maksuvalmius | kassa | tasauserä (lähde jos käyttö>lähteet) |

## Menot
| id | nimi | luokka | huom |
|----|------|--------|------|
| `henk` | Henkilöstökulut | meno | lapset: kululajit → palkat → palvelut |
| `palkat` | Palkat ja palkkiot | meno | |
| `palkat_perusop` | Perusopetus ja nuoriso | — | arvio (htv) |
| `palkat_varhais` | Varhaiskasvatus | — | arvio (htv) |
| `palkat_muusiv` | Muu sivistys | — | arvio (htv) |
| `palkat_muuperus` | Muu peruskunta | — | arvio |
| `palkat_liike` | Liikelaitokset | — | arvio |
| `elake` | Eläkekulut | — | |
| `sivukulut` | Muut henkilösivukulut | — | |
| `palv` | Palvelujen ostot | meno | lapset: asiakas/muut |
| `palv_asiakas` | Asiakaspalvelujen ostot | meno | |
| `palv_as_seteli` | Palvelusetelit | — | |
| `palv_as_muut` | Muut asiakaspalvelut | — | |
| `palv_muut` | Muiden palvelujen ostot | meno | |
| `palv_muut_liike` | Liikelaitokset | — | arvio |
| `palv_muut_yhd` | Yhdyskunta | — | arvio |
| `palv_muut_siv` | Sivistyspalvelut | — | arvio |
| `palv_muut_hall` | Hallinto, ICT ja muut | — | arvio |
| `palv_muut_hykl` | Hyvinvointi, kulttuuri ja liikunta | — | arvio |
| `avust` | Avustukset | meno | |
| `avust_tyott` | Työttömyysturvan kuntaosuus | — | |
| `avust_yht` | Avustukset yhteisöille | — | arvio |
| `avust_muut` | Muut avustukset | — | arvio |
| `aineet` | Aineet ja tarvikkeet | meno | |
| `vuokrat` | Vuokrat ja muut | meno | vuokrakulut + muut toimintakulut |
| `invest` | Investoinnit | rahoitus | lapset: arvio |
| `inv_talo` | Talonrakennus | — | arvio |
| `inv_kadut` | Kadut ja liikenneväylät | — | arvio |
| `inv_koneet` | Koneet, kalusto ja ICT | — | arvio |
| `inv_maa` | Maa-alueet ja muut | — | arvio |
| `korkokulut` | Korko- ja rahoituskulut | meno | korkokulut + muut rahoituskulut |
| `lyhennys` | Lainojen lyhennykset | rahoitus | pitkäaik. (+ lyhytaik. jos väheni) |
