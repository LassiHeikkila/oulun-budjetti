#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kaiva_tilinpaatos.py
====================
Kaivaa Oulun kaupungin tilinpäätös-PDF:stä Sankey-kaavion YLÄTASON luvut
ja tulostaa valmiin JSON-rungon (data/oulu-talous-<vuosi>.json).

Periaate:
- Etsii kunkin erän JOUSTAVILLA hakukaavoilla (useita sanamuotoja per erä,
  koska otsikot ja sivut vaihtelevat vuosittain).
- Poimii rivin ensimmäisen euromäärän (= uusin TP-sarake, joka on PDF:ssä
  yleensä vasemmanpuoleisin lukusarake).
- EI laske välisummia eikä arvaa: jos lukua ei löydy, kenttä jää tyhjäksi
  ja merkitään "TARKISTA". Alaerät (lapset) jätetään tyhjiksi täytettäväksi.
- Ajaa summavalidoinnin ja varoittaa jos tulot != menot.

Käyttö:
    python3 kaiva_tilinpaatos.py tilinpaatos2025.pdf --vuosi 2025
    python3 kaiva_tilinpaatos.py tilinpaatos2024.pdf --vuosi 2024 -o data/

Riippuvuudet: pdftotext (poppler). Ei Python-paketteja.
    macOS:   brew install poppler
    Ubuntu:  sudo apt install poppler-utils
    Windows: lataa poppler ja lisää bin/ PATHiin
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# HAKUMÄÄRITTELYT
# Jokainen erä: id, nimi, luokka, ja lista regexejä (kokeillaan järjestyksessä).
# Regexin tulee napata rivin numero-osa ryhmään. Numero saa sisältää
# välilyöntejä tuhaterottimina ja miinusmerkin. Lisää uusia variantteja
# vapaasti jos jonkin vuoden sanamuoto eroaa.
# 'puoli': "tulo" tai "meno".
# ---------------------------------------------------------------------------

# Numero = yksi taulukkosarake. Tilinpäätöksen luvut ovat tuhansina (1000 €),
# muodossa "508 940" tai "-800 518" (yksittäinen välilyönti tuhaterottimena).
# Sarakkeet erottaa TOISISTAAN 2+ välilyöntiä (pdftotext -layout). Siksi
# numeron sisällä saa olla vain YKSI välilyönti peräkkäin.
NUM = r"(-?\d{1,3}(?:\u00a0?\s\d{3})*|-?\d+)"

def pat(label_variants):
    """Rakenna regexlista: rivin ALUSSA otsikko, sitten 2+ välilyöntiä, sitten sarakeluku.
    Vaaditaan iso väli otsikon ja luvun välillä -> osuu taulukkoriviin, ei leipätekstiin."""
    pats = []
    for lab in label_variants:
        # otsikko rivin alussa, vähintään 2 välilyöntiä (taulukkosarake), sitten numero
        pats.append(re.compile(
            r"^\s*" + lab + r"\s{2,}" + NUM + r"(?:\s|$)",
            re.IGNORECASE | re.MULTILINE))
    return pats

ERAT = [
    # --- TULOT ---
    dict(id="verot", nimi="Verotulot", luokka="tulo", puoli="tulo",
         lahde="Tuloslaskelma (Verotulot-rivi)",
         patterns=pat([r"Verotulot"])),
    dict(id="toimtuotot", nimi="Toimintatuotot", luokka="tulo", puoli="tulo",
         lahde="Tuloslaskelma (Toimintatuotot-rivi)",
         patterns=pat([r"Toimintatuotot"])),
    dict(id="valtio", nimi="Valtionosuudet", luokka="tulo", puoli="tulo",
         lahde="Tuloslaskelma (Valtionosuudet-rivi)",
         patterns=pat([r"Valtionosuudet"])),
    dict(id="laina", nimi="Lainanotto", luokka="rahoitus", puoli="tulo",
         lahde="Rahoituslaskelma (pitkäaikaisten lainojen lisäys)",
         patterns=pat([r"Pitk[aä]aikaisten lainojen lis[aä]ys",
                       r"Pitk[aä]aikaisen lainan lis[aä]ys"])),
    dict(id="myynti", nimi="Omaisuuden myynti ja rah.osuudet", luokka="tulo", puoli="tulo",
         lahde="Rahoituslaskelma (luovutustulot + rahoitusosuudet) — laske käsin yhteen",
         patterns=pat([r"Pysyvien vastaavien hy[oö]dykkeiden luovutustulot"])),
    dict(id="antolaina_in", nimi="Antolainojen takaisinmaksut", luokka="tulo", puoli="tulo",
         lahde="Rahoituslaskelma (antolainasaamisten vähennys)",
         patterns=pat([r"Antolainasaamisten v[aä]hennys"])),
    # kassa: tasauserä, lasketaan lopuksi (ei haeta PDF:stä)

    # --- MENOT ---
    dict(id="henk", nimi="Henkilöstökulut", luokka="meno", puoli="meno",
         lahde="Tuloslaskelma (Henkilöstökulut / Toimintakulut-erittely)",
         patterns=pat([r"Henkil[oö]st[oö]kulut"])),
    dict(id="palv", nimi="Palvelujen ostot", luokka="meno", puoli="meno",
         lahde="Tuloslaskelma / liite: Palvelujen ostot",
         patterns=pat([r"Palvelujen ostot"])),
    dict(id="avust", nimi="Avustukset", luokka="meno", puoli="meno",
         lahde="Toimintakulut-erittely (Avustukset)",
         patterns=pat([r"Avustukset"])),
    dict(id="aineet", nimi="Aineet ja tarvikkeet", luokka="meno", puoli="meno",
         lahde="Toimintakulut-erittely (Aineet, tarvikkeet ja tavarat)",
         patterns=pat([r"Aineet,? tarvikkeet ja tavarat", r"Aineet ja tarvikkeet"])),
    dict(id="vuokrat", nimi="Vuokrat ja muut", luokka="meno", puoli="meno",
         lahde="Toimintakulut-erittely (Vuokrakulut + Muut) — laske käsin yhteen",
         patterns=pat([r"Vuokrakulut", r"Vuokrat"])),
    dict(id="invest", nimi="Investoinnit", luokka="rahoitus", puoli="meno",
         lahde="Rahoituslaskelma (Investointimenot)",
         patterns=pat([r"Investointimenot"])),
    dict(id="korkokulut", nimi="Korko- ja rahoituskulut", luokka="meno", puoli="meno",
         lahde="Tuloslaskelma (Korkokulut + Muut rahoituskulut) — laske käsin yhteen",
         patterns=pat([r"Korkokulut"])),
    dict(id="lyhennys", nimi="Lainojen lyhennykset", luokka="rahoitus", puoli="meno",
         lahde="Rahoituslaskelma (pitkä- + lyhytaik. lainojen vähennys) — laske käsin",
         patterns=pat([r"Pitk[aä]aikaisten lainojen v[aä]hennys"])),
]

# ---------------------------------------------------------------------------

def lue_pdf_teksti(pdf_path):
    """Pura PDF tekstiksi pdftotext -layout -tilassa."""
    try:
        out = subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), "-"],
            capture_output=True, text=True, check=True)
        return out.stdout
    except FileNotFoundError:
        sys.exit("VIRHE: pdftotext puuttuu. Asenna poppler "
                 "(macOS: brew install poppler, Ubuntu: apt install poppler-utils).")
    except subprocess.CalledProcessError as e:
        sys.exit(f"VIRHE: pdftotext epäonnistui: {e.stderr}")

def parse_numero(s):
    """'508 940' / '-800 518' -> int (tuhansina euroina)."""
    s = s.replace("\u00a0", " ").replace(" ", "")
    if not re.fullmatch(r"-?\d+", s):
        return None
    return int(s)

def etsi_era(teksti, era):
    """Palauta (arvo_milj, raaka_osuma) tai (None, None)."""
    for rx in era["patterns"]:
        m = rx.search(teksti)
        if m:
            n = parse_numero(m.group(1))
            if n is None:
                continue
            # tilinpäätös on tuhansina euroina -> miljooniksi, itseisarvo
            milj = round(abs(n) / 1000.0, 1)
            # ohita epäuskottavat osumat (esim. otsikon vieressä oleva 0/% luku)
            if milj < 0.05:
                continue
            return milj, m.group(0).strip()
    return None, None

def rakenna_json(teksti, vuosi):
    tulot, menot = [], []
    loydot = {}
    for era in ERAT:
        arvo, raaka = etsi_era(teksti, era)
        loydot[era["id"]] = (arvo, raaka)
        node = {"id": era["id"], "nimi": era["nimi"]}
        if arvo is not None:
            node["arvo"] = arvo
        else:
            node["arvo"] = None
            node["TARKISTA"] = "lukua ei löytynyt automaattisesti"
        node["luokka"] = era["luokka"]
        node["lahde"] = era["lahde"]
        node["lapset"] = []   # täytä alaerät käsin
        (tulot if era["puoli"] == "tulo" else menot).append(node)

    # kassa-tasauserä: lähde, joka tasaa tulot=menot. Lisätään vain jos
    # molemmilta puolilta löytyi tarpeeksi lukuja; muuten jätetään TARKISTA.
    L = sum(n["arvo"] for n in tulot if isinstance(n.get("arvo"), (int, float)))
    K = sum(n["arvo"] for n in menot if isinstance(n.get("arvo"), (int, float)))
    kassa = {"id": "kassa", "nimi": "Kassavarojen väheneminen", "luokka": "kassa",
             "lahde": "Tasauserä: menot − tulot (tarkista rahoituslaskelmasta)",
             "lapset": []}
    diff = round(K - L, 1)
    if diff > 0:
        kassa["arvo"] = diff
    else:
        kassa["arvo"] = None
        kassa["TARKISTA"] = ("tulot >= menot ilman kassaerää; "
                             "tarkista rahoituslaskelman rahavarojen muutos")
    tulot.append(kassa)

    data = {
        "vuosi": vuosi,
        "yksikko": "milj. €",
        "otsikko": "Mistä rahat tulevat ja mihin ne menevät",
        "kuvaus": (f"Koko rahankäyttö vuonna {vuosi}: kaikki rahanlähteet vasemmalla, "
                   "kaikki käyttö oikealla."),
        "tulot": tulot,
        "menot": menot,
    }
    return data, loydot

def raportti(data, loydot):
    print("\n=== KAIVUN TULOS ===", file=sys.stderr)
    for puoli in ("tulot", "menot"):
        print(f"\n{puoli.upper()}:", file=sys.stderr)
        for n in data[puoli]:
            arvo = n.get("arvo")
            tila = "OK   " if isinstance(arvo, (int, float)) else "PUUTTUU"
            extra = ""
            raaka = loydot.get(n["id"], (None, None))[1]
            if raaka:
                extra = f"   <- \"{raaka[:60]}\""
            print(f"  [{tila}] {n['nimi']:<34} "
                  f"{(str(arvo)+' M€') if arvo is not None else 'TARKISTA':>12}{extra}",
                  file=sys.stderr)

    L = sum(n["arvo"] for n in data["tulot"] if isinstance(n.get("arvo"), (int, float)))
    K = sum(n["arvo"] for n in data["menot"] if isinstance(n.get("arvo"), (int, float)))
    print(f"\nTulot yhteensä:  {L:.1f} M€", file=sys.stderr)
    print(f"Menot yhteensä:  {K:.1f} M€", file=sys.stderr)
    if abs(L - K) > 0.3:
        print(f"!! Puolet eivät täsmää (ero {abs(L-K):.1f} M€). "
              "Tarkista TARKISTA-merkityt ja käsin laskettavat erät.", file=sys.stderr)
    else:
        print("Puolet täsmäävät.", file=sys.stderr)

    puuttuu = [n["nimi"] for p in ("tulot", "menot") for n in data[p]
               if not isinstance(n.get("arvo"), (int, float))]
    if puuttuu:
        print("\nTÄYTÄ KÄSIN (ei löytynyt tai laskettava yhteen):", file=sys.stderr)
        for p in puuttuu:
            print(f"  • {p}", file=sys.stderr)
    print("\nMUISTA: alaerät (lapset) ja arvio-luvut täytetään käsin.\n", file=sys.stderr)

def main():
    ap = argparse.ArgumentParser(description="Kaiva Oulun tilinpäätös-PDF Sankey-JSONiksi (ylätaso).")
    ap.add_argument("pdf", help="tilinpäätös-PDF")
    ap.add_argument("--vuosi", type=int, required=True, help="tilikausi, esim. 2025")
    ap.add_argument("-o", "--out", default=".", help="tuloskansio (oletus: nykyinen)")
    args = ap.parse_args()

    teksti = lue_pdf_teksti(args.pdf)
    data, loydot = rakenna_json(teksti, args.vuosi)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"oulu-talous-{args.vuosi}.json"
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    raportti(data, loydot)
    print(f"Kirjoitettu: {out_path}", file=sys.stderr)

if __name__ == "__main__":
    main()
