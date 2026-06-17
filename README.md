# oulun-budjetti

Oulun kaupungin tilinpäätösten visualisointia Sankey-kaavioina.

Tilinpäätösten tietojen käsittelyssä on käytetty tekoälyä, ja tiedot voivat sisältää virheitä.

Jos huomaat virheitä datassa, voit raportoida ne tekemällä issuen tähän repoon.

## Tietojen lisääminen uudelle vuodelle

Kun uusi tilinpäätös on saatavilla, tee siitä JSON tiedosto ja laita se `data/` kansioon nimellä `oulun-talous-<vuosi>.json`.

Lisää vuosi `YEARS` listaan `index.html` sivulla.
