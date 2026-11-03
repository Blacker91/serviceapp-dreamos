# ServiceApp pro DreamOS

[English](README.md)

Port [ServiceApp](https://github.com/oe-mirrors/serviceapp) na **DreamOS 2.5**
(enigma2 4.3.3r3, Python 2.7). Přidává typ služby **5002**, který přehrává
[exteplayer3](https://github.com/Blacker91/exteplayer3-dreamos), stejně jako na
OpenPLi / OpenATV. Doplňky jako ArchivCZSK tak můžou exteplayer3 používat i na Dreamboxu.

## ⚠️ Upozornění
- **Vše zkoušíš na vlastní nebezpečí.** Před instalací si **udělej zálohu image**.
- Instaluj pouze na **enigma2 4.3.3r3** (DreamOS 2.5, poslední vydaná unstable verze),
  na které jsme to zkoušeli. Verzi zjistíš na boxu příkazem `dpkg -l enigma2`.
- Vyzkoušeno na DM520. Build pro DM900/DM920 je ověřený proti stejné verzi
  enigma2, ale na boxu zatím vyzkoušený nebyl.

## Podporované boxy
| Box | Architektura |
|---|---|
| DM520, DM525 | mipsel |
| DM900, DM920 | armhf |

Balíčky jsou zvlášť pro mipsel a armhf, instalátor vybere sám.

**Dreambox One / Two (DreamOS 2.6, enigma2 4.5.1r11)** – zkušební balíček `_arm64`,
na boxu zatím nevyzkoušený a není v instalátoru. exteplayer3 pro One zatím není
(potřebuje Amlogic výstup obrazu), takže ServiceApp nemá čím přehrávat, dokud na
boxu není exteplayer3 pro One v `/usr/bin`. Build: `dreamos/fetch-sysroot.sh aarch64`
(`ONE_IMAGE=` image Dreamboxu One) a `dreamos/build.sh aarch64`; rozdíly mezi
enigma2 4.3.3r3 a 4.5.1r11 jsou popsané v `dreamos/e2-451-headers.py`.

## Co umí
- služba 5002 (exteplayer3): HLS, DASH, klíče CENC DRM, oddělený zvuk (YouTube)
- pauza / posun v InfoBaru u videí (ne u živého vysílání)
- EPG u služeb 5002
- titulky: textové stopy ve videu, externí .srt, WebVTT, grafické titulky (PGS, DVB)
- volitelně: náhrada Dreamova servicemp3 (4097) pro streamy, soubory, nebo obojí

## Instalace
Na boxu (ssh/telnet):
```sh
curl -fsSL https://raw.githubusercontent.com/Blacker91/serviceapp-dreamos/dreamos/installer.sh | sh
```
Nainstaluje ServiceApp a exteplayer3 (včetně ffmpeg) a restartuje enigmu.

Potřebuje `curl` (v DreamOS obvykle je). `wget` z BusyBoxu v DreamOS z GitHubu stahovat neumí.
Kdyby `curl` chyběl: `apt-get update && apt-get install curl`.

Ručně: stáhni `.deb` pro svůj box (`_mipsel` pro DM520/DM525, `_armhf` pro DM900/DM920) z
[Releases](https://github.com/Blacker91/serviceapp-dreamos/releases)
a [Releases exteplayer3](https://github.com/Blacker91/exteplayer3-dreamos/releases), pak
```sh
dpkg -i exteplayer3-dreamos_*.deb enigma2-plugin-systemplugins-serviceapp-dreamos_*.deb
systemctl restart enigma2
```
Potom nespouštěj `apt-get -f install`, balíčky nejsou v Dreamově feedu a apt by je odebral.

## Nastavení
Menu → Pluginy → ServiceApp.
- **Enigma2 playback system → serviceapp**: streamy 4097 (např. IPTV bouquety) hraje exteplayer3.
  **Play with ServiceApp**: jen streamy (výchozí), streamy i soubory, nebo jen soubory z disku/NAS.
- **Subtitles**: velikost písma, barva, pozadí, zpoždění, doba zobrazení, vzdálenost od spodního okraje.

## Kontakt
Chyby a návrhy: [Issues](https://github.com/Blacker91/serviceapp-dreamos/issues) nebo e-mail
**dreamosserviceapp@gmail.com**.
