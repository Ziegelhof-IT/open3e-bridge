# Recherche: Viessmann Vitocal 250-A Dokumentation

## Dein System

**Modell:** Viessmann Vitocal 250-A (Luft/Wasser-Waermepumpe, Monoblock)
**Controller:** E3 "OneBase" Generation
**6 ECUs:** HPMUMASTER (0x680), HMI (0x684), VCMU (0x68c), BACKENDGATEWAY (0x6c3, 0x6c5), EHCU (0x6cf)
**Schnittstelle:** CAN-Bus (250 kbps) ueber Connector 91, alternativ DoIP/UDS
**60+ DIDs** werden ueber open3e gelesen und per MQTT an Home Assistant publiziert

---

## 1. Offizielle Viessmann Dokumentation

### Datenblaetter (PDF, kostenlos)
- [Datenblatt Vitocal 250-A Neubau (DB-6195458)](https://www.viessmann.de/content/dam/public-brands/master/products/heat-pump/vitocal-250-a-neubau/DB-6195458-vitocal-250-a.pdf/_jcr_content/renditions/original.media_file.download_attachment.file/DB-6195458-vitocal-250-a.pdf)
- [Datenblatt Vitocal 250-A Modernisierung (DB-6246346)](https://www.viessmann.de/content/dam/public-brands/master/products/heat-pump/vitocal-250-a/db-6246346-vitocal-250-a.pdf/_jcr_content/renditions/original.media_file.download_attachment.file/db-6246346-vitocal-250-a.pdf)
- [Kurzpruefbericht (2.6-18.5 kW)](https://www.viessmann.de/content/dam/public-brands/master/products/heat-pump/vitocal-250-a/kpr-Vitocal-250-A.pdf/_jcr_content/renditions/original.media_file.download_attachment.file/kpr-Vitocal-250-A.pdf)
- [ENEV-Datenblatt A10/A13](https://media.selfio.de/downloads/pdf/ENEV-Datenblatt-Viessmann-VITOCAL-250-A-A10-A13_compressed.pdf)

### Montage- und Serviceanleitungen
- [Montage+Service DE (heizungsdiscount24, PDF)](https://www.heizungsdiscount24.de/pdf/Viessmann-Vitocal-250-A-Service-und-Montageanleitung.pdf)
- [Montage+Service DE (Viessmann Community, PDF)](https://community.viessmann.de/viessmann/attachments/viessmann/customers-heatpump-hybrid/148294/1/vie-WP-Installation2.pdf)
- [Montage+Service EN (ManualsLib, 200 Seiten)](https://www.manualslib.com/manual/3652779/Viessmann-Vitocal-250-A.html)
- [Montage+Service DE AWO-E-AC 251.A (ManualsLib)](https://www.manualslib.de/manual/853134/Viessmann-Vitocal-250-A-Awo-E-Ac-251-A.html)

### Planungsanleitungen
- [Planungsanleitung (selfio, PDF)](https://media.selfio.de/downloads/pdf/Planungsanleitung-Viessmann-Vitocal-250-A_compressed.pdf)
- [Planungsanleitung AWO-M-E-AC (ManualsLib)](https://www.manualslib.de/manual/842248/Viessmann-Vitocal-250-A-Awo-M-E-Ac.html)

### Bedienung und Verdrahtung
- [Bedienungsanleitung (selfio, PDF)](https://media.selfio.de/downloads/pdf/bedienungsanleitung-vitocal-250-a.pdf)
- [Anschluss-/Verdrahtungsplan (heima24, PDF)](https://www.heima24.de/shop/images/products/media/ap-viessmann-Vitocal-250-A-AWO-M-E-AC-AWO-M-E-AC-AF-251-A-AWO-M-E-AC-AWO-M-E-AC-AF-251-A-2C.pdf)
- [One Base Servicehandbuch (Community, PDF)](https://community.viessmann.de/viessmann/attachments/viessmann/customers-heatpump-hybrid/145143/2/Viessmann%20One%20Base%20handbuchWP.pdf)

### Viessmann Portale
- [ViBooks -- Dokumentensuche (30.000+ Dokumente)](https://vibooks.viessmann.com/at/de?doctype=bedienungsanleitung)
- [Viessmann Produktseite Vitocal 250-A](https://www.viessmann.de/de/produkte/waermepumpe/vitocal-250-a.html)
- [ViGuide Planungstool](https://viguide-planning.viessmann.com/)

---

## 2. CAN-Bus / Protokoll Dokumentation

**Wichtig:** Viessmann publiziert kein offizielles CAN-Bus-Protokoll. Alles ist Community-Reverse-Engineering.

### Praktische Anleitungen
- [Blog: Raspberry Pi + CAN + Vitocal (laggner.info, Nov 2025)](https://www.laggner.info/posts/connect-can-bus-vitocal/) -- Bester End-to-End-Guide mit Fotos, Connector 91 Pinout
- [Viessmann Community: CAN-Bus Home Automation E3](https://community.viessmann.de/t5/Konnektivitaet/CAN-Bus-Home-Automation-E3-Generation-lokal-und-kostenlos/td-p/356066) -- Multi-Page-Thread, praktische Erfahrungen

### Connector 91 Pinout
```
Pin 6: CAN-L
Pin 7: GND
Pin 8: CAN-H
Bitrate: 250 kbps
```

---

## 3. Open3e Oekosystem

### Kern-Projekt
- [open3e Hauptrepo](https://github.com/open3e/open3e) -- Upstream-Library fuer CAN/DoIP/UDS
- [open3e Wiki](https://github.com/open3e/open3e/wiki) -- Installation, Datapoints, Codecs, Addressing
- [open3e Discussions](https://github.com/open3e/open3e/discussions) -- Community Q&A, DID-Spezifika

### Wichtige Discussions
- [#54 -- Home Assistant Integration](https://github.com/open3e/open3e/discussions/54)
- [#184 -- Vitocal 250-A SW-Versionen 2417 vs 2440](https://github.com/open3e/open3e/discussions/184)
- [#207 -- Stromverbrauch DIDs (548, 565, 566, 2517, 2526)](https://github.com/open3e/open3e/discussions/207)
- [#27 -- Datapoint-Definitionen bearbeiten](https://github.com/open3e/open3e/discussions/27)

### Verwandte Projekte
- [E3onCAN](https://github.com/MyHomeMyData/E3onCAN) -- Passives CAN-Listening (kein UDS-Polling, weniger Bus-Last)
- [Open3E-HA](https://github.com/Wolfgang-03/Open3E-HA) -- HA Add-On + YAML-Packages
- [ha.vis.vitocal250](https://github.com/MyHomeMyData/ha.vis.vitocal250) -- Kaeltekreis-Visualisierung fuer HA
- [ioBroker.e3oncan](https://github.com/MyHomeMyData/ioBroker.e3oncan) -- ioBroker-Adapter, alternative UDS-Implementierung
- [abnoname/open3e (Original)](https://github.com/abnoname/open3e) -- Historischer Code, Service 0x77 Doku

---

## 4. Viessmann Developer API (Cloud)

- [Developer Portal](https://developer.viessmann-climatesolutions.com/start.html) -- IoT API, Equipment API (Cloud-basiert, nicht CAN)
- [PyViCare](https://github.com/openviess/PyViCare) -- Python-Library fuer ViCare Cloud-API
- **Hinweis:** Cloud-API hat weniger Datenpunkte als CAN-Bus und braucht Internet

---

## 5. Alternative Ansaetze (Referenz)

- [InsideViessmannVitosoft](https://github.com/sarnau/InsideViessmannVitosoft) -- Optolink-Protokoll Reverse Engineering
- [ViLocal](https://github.com/kristian/ViLocal) -- ZigBee-Sniffing lokaler Viessmann-Kommunikation
- [vcontrold](https://github.com/openv/vcontrold) -- Optolink-Daemon fuer aeltere Vitotronic
- [viessmann-optolink2mqtt](https://github.com/f18m/viessmann-optolink2mqtt) -- Optolink-zu-MQTT Bridge

---

## 6. Community-Foren

- [Viessmann Community: Energiemanagement Vitocal 250-A](https://community.viessmann.de/t5/Waermepumpe-Hybridsysteme/Energiemanagmentsystem-Vitocal-250-A-Regelung-E3-mit-Vitocharge/td-p/270675)
- [Viessmann Community: Elektrischer Anschluss](https://community.viessmann.de/t5/Waermepumpe-Hybridsysteme/Vitocal-250-A-elektrischer-Anschluss/td-p/278486)
- [HaustechnikDialog: CAN Bus und Viessmann](https://www.haustechnikdialog.de/Forum/t/266337/CAN-Bus-und-Viessmann-CANOpen)
- [ioBroker Forum: E3onCAN Adapter Test](https://forum.iobroker.net/topic/72374/test-adapter-e3oncan-viessmann-e3-serie-einbinden)
- [HA Community: Viessmann Interconnections](https://community.home-assistant.io/t/viessmann-interconnections/758373)

---

## Empfehlung: Top-5 Dokumente zum Runterladen

1. **Montage- und Serviceanleitung** (heizungsdiscount24 PDF) -- Hardware-Details, Fehlercodes, Hydraulik
2. **Planungsanleitung** (selfio PDF) -- Systemplanung, Betriebsgrenzen, Leistungsdaten
3. **One Base Servicehandbuch** (Community PDF) -- Controller-spezifische Informationen
4. **Verdrahtungsplan** (heima24 PDF) -- Elektrische Anschluesse
5. **Datenblatt** (Viessmann PDF) -- Technische Spezifikationen
