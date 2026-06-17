# Alakategorioiden erottelu

Tämä viite kertoo, miten kunkin ylätason erän alakategoriat (lapset) puretaan, ja merkitsee selvästi mikä on suoraan tilinpäätöksestä ja mikä on arvioitava. Tavoite: jokainen vuosi eritellään yhtä tarkasti kuin 2025.

Yleissääntö: jos luku löytyy nimettynä rivinä virallisesta taulukosta → ei `arvio`-merkintää. Jos luku pitää johtaa, jakaa tai koota useasta paikasta → `"arvio": true` ja selitä jakoperuste `lahde`-kentässä.

---

## 1. Verotulot (`verot`) — SUORAAN

Etsi tilinpäätöksen verotulojen erittelytaulukosta (usein liite tai oma taulukko, otsikko sisältää "Verotulot"). Kolme riviä:

| id | nimi | rivin otsikko |
|----|------|---------------|
| `verot_kunnallis` | Kunnallisvero | "Kunnan tulovero" / "Kunnallisvero" |
| `verot_kiinteisto` | Kiinteistövero | "Kiinteistövero" |
| `verot_yhteiso` | Yhteisövero | "Osuus yhteisöveron tuotosta" / "Yhteisövero" |

Summan tulee täsmätä `verot`-arvoon. 2025: 394,0 + 73,9 + 41,0 = 508,9.

---

## 2. Toimintatuotot (`toimtuotot`) — SUORAAN

Taulukosta "ULKOISET TOIMINTATUOTOT". Viisi riviä:

| id | nimi | rivin otsikko |
|----|------|---------------|
| `tt_myynti` | Myyntituotot | "Myyntituotot" |
| `tt_vuokra` | Vuokratuotot | "Vuokratuotot" |
| `tt_maksu` | Maksutuotot | "Maksutuotot" |
| `tt_tuet` | Tuet ja avustukset | "Tuet ja avustukset" |
| `tt_muut` | Muut tuotot | "Muut toimintatuotot" |

2025: 73,5 + 64,9 + 35,0 + 19,3 + 10,2 = 202,9.

---

## 3. Henkilöstökulut (`henk`)

### Taso 2: kululajit — SUORAAN
Henkilöstökustannusten erittelytaulukosta:

| id | nimi | rivin otsikko |
|----|------|---------------|
| `palkat` | Palkat ja palkkiot | "Palkat ja palkkiot" |
| `elake` | Eläkekulut | "Eläkekulut" |
| `sivukulut` | Muut henkilösivukulut | "Muut henkilösivukulut" |

Huom: erittelytaulukko voi olla koko kaupungin tasolla hieman eri summa kuin tuloslaskelman ulkoinen henkilöstökulu. Skaalaa kululajit ulkoiseen lukuun: `kululaji_ulkoinen = kululaji_taulukko × (henk_ulkoinen / taulukon_summa)`. Merkitse tällöin `lahde`-kenttään "skaalattu ulkoiseen".

### Taso 3: palkkojen jako palveluittain — ARVIO
Tilinpäätös ei anna palkkoja palveluittain euroina. Jaa `palkat`-arvo henkilötyövuosien (htv) suhteessa. Hae:
- Sivistyslautakunnan henkilöstökulut euroina (mainitaan tekstissä, esim. 2025: 288,3 M€).
- Peruskunnan ja liikelaitosten henkilöstökulut (toimintakertomuksen teksti).
- Vastuualueiden htv:t (henkilöstöosio): perusopetus+nuoriso, varhaiskasvatus, muu sivistys.

Laske sivistyksen sisäinen jako htv-suhteessa, lisää muu peruskunta ja liikelaitokset, ja skaalaa kaikki `palkat`-arvoon. Suositellut id:t: `palkat_perusop`, `palkat_varhais`, `palkat_muusiv`, `palkat_muuperus`, `palkat_liike`. Jokaiseen `"arvio": true`.

2025-esimerkki: perusopetus+nuoriso 108,6 · varhaiskasvatus 89,2 · muu sivistys 35,0 · muu peruskunta 44,7 · liikelaitokset 39,2 (yht. 316,6).

---

## 4. Palvelujen ostot (`palv`)

### Taso 2: virallinen kaksijako — SUORAAN
Liitetiedosta (palvelujen ostojen erittely, usein liite 9 tms.):

| id | nimi | rivin otsikko |
|----|------|---------------|
| `palv_asiakas` | Asiakaspalvelujen ostot | "Asiakaspalvelujen ostot" |
| `palv_muut` | Muiden palvelujen ostot | "Muiden palvelujen ostot" |

2025: 59,4 + 195,2 = 254,6 ≈ 254,7.

### Taso 3a: asiakaspalvelut → palvelusetelit + muut
- `palv_as_seteli` "Palvelusetelit" — sivistyslautakunnan palveluseteli­summa (käyttötalous), SUORAAN.
- `palv_as_muut` "Muut asiakaspalvelut" = `palv_asiakas` − palvelusetelit.

### Taso 3b: muiden palvelujen ostot → lautakunnittain — ARVIO
Tilinpäätös ei anna koko kaupungin "muita palveluja" yhtenä lautakuntataulukkona. Kokoa lautakuntien käyttötalousosista ja liikelaitosten liitteistä, ja skaalaa summa `palv_muut`-arvoon. Suositellut id:t: `palv_muut_liike` (liikelaitokset), `palv_muut_yhd` (yhdyskunta), `palv_muut_siv` (sivistys), `palv_muut_hall` (hallinto/ICT), `palv_muut_hykl` (hyvinvointi/kulttuuri/liikunta). Jokaiseen `"arvio": true`.

---

## 5. Avustukset (`avust`)

- `avust_tyott` "Työttömyysturvan kuntaosuus" — mainitaan tekstissä euroina, melko luotettava (merkitse arvioksi jos ei tarkkaa lukua).
- Loput (`avust_yht` yhteisöille, `avust_muut`) yleensä ARVIO, ellei tilinpäätös erittele.

---

## 6. Investoinnit (`invest`) — ARVIO

Tilinpäätös esittää investoinnit hankekohtaisesti ja lautakunnittain investointiosassa, ei yhtenä siistinä hyödykeryhmätaulukkona. Kokoa pääryhmiin ja skaalaa `invest`-arvoon. Suositellut id:t: `inv_talo` (talonrakennus), `inv_kadut` (kadut ja liikenneväylät), `inv_koneet` (koneet, kalusto, ICT), `inv_maa` (maa-alueet ja muut). Jokaiseen `"arvio": true`.

---

## Erät joilla EI yleensä ole alaeriä

`valtio`, `rahoitus`, `aineet`, `vuokrat`, `korkokulut`, `laina`/`lyhytlaina`, `lyhennys`, `myynti`, `antolaina_in`, `kassa` — jätä `lapset` pois tai tyhjäksi, ellei käyttäjä erikseen pyydä eikä tilinpäätös tarjoa luotettavaa jakoa.

---

## Tarkkuustasot — sovi käyttäjän kanssa

- **Vain ylätaso**: kaikki `lapset` tyhjiä. Nopein, kaikki luvut virallisia.
- **Viralliset alaerät**: erottele vain ne, jotka löytyvät suoraan taulukoista (verot, toimintatuotot, henkilöstön kululajit, palvelujen ostojen kaksijako, palvelusetelit). Ei arvioita.
- **Täysi 2025-taso**: kaikki alaerät, myös arviot (palkkojen palvelujako, palvelujen lautakuntajako, investointien kohteet). Tämä antaa rikkaimman drill-downin mutta vaatii arvioiden merkitsemisen.

Kun et ole varma tasosta, kysy käyttäjältä, tai tuota viralliset alaerät ja jätä arvio-tason erät myöhemmin täytettäviksi.
