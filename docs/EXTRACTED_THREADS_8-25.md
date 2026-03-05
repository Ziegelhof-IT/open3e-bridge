# Extrahierte Threads #8-25 — 2026-02-27

Vollstaendige Extraktion der hoch relevanten Viessmann Community Threads.

## Statistik

| # | Thread | Posts | Chars |
|---|--------|-------|-------|
| 8 | CAN Bus Format VX3 und E380CA | ? | ? |
| 9 | Vitocal 262-a interne CAN Buchsen | ? | ? |
| 10 | CAN Bus Steckverbinder Aussengeraet fehlt | ? | ? |
| 11 | Vitocal 250 in Home Assistant einbinden | 3 | 4167 |
| 12 | Vitodens 200-W Integration ohne Server | 2 | 3696 |
| 13 | Adapter CAN-Bus auf LAN Stecker | 4 | 727 |
| 14 | VC250 CAN Bus und WLAN | 7 | 3577 |
| 15 | CAN-Bus Schnittstelle Wago ohne Gateway | 12 | 4004 |
| 16 | Zwei CAN Bus Zaehler Vitocharge VX3 | 7 | 2397 |
| 17 | WP-Anschluss Aussenteil CAN-Bus und 400V | 2 | 355 |
| 18 | Raspberry fuer Vitocal 250-A ohne PV | 2 | 1005 |
| 19 | WP stufenlos regeln PV-Ueberschuss | 76 | 59162 |
| 20 | Can Bus Verbindungsfehler | 2 | 390 |
| 21 | ioBroker Datenpunkte vitocharge vx3 | 3 | 1093 |
| 22 | Local connection to VitoConnect | 3 | 1744 |
| 23 | Optolink Switch Splitter Vitoconnect MQTT | 51 | 21656 |
| 24 | Direktzugriff VITOCONNECT 100 ohne Cloud | 13 | 6214 |
| 25 | Open-Source Viessmann IoT API Datenlogger | 1 | 1160 |

---

## Thread #8: CAN Bus Format VX3 und E380CA

**URL**: https://community.viessmann.de/t5/Strom-PV/CAN-Bus-Format-VX3-und-E380CA/td-p/354401
**Posts**: ?

KEINE DATEN

---

## Thread #9: Vitocal 262-a interne CAN Buchsen

**URL**: https://community.viessmann.de/t5/Waermepumpe-Hybridsysteme/Vitocal-262-a-interne-CAN-Buchsen/td-p/518391
**Posts**: ?

KEINE DATEN

---

## Thread #10: CAN Bus Steckverbinder Aussengeraet fehlt

**URL**: https://community.viessmann.de/t5/Waermepumpe-Hybridsysteme/CAN-Bus-Steckverbinder-Aussengeraet-Waermepumpe-fehlt/td-p/331743
**Posts**: ?

KEINE DATEN

---

## Thread #11: Vitocal 250 in Home Assistant einbinden

**URL**: https://community.viessmann.de/t5/Waermepumpe-Hybridsysteme/Vitocal-250-in-einen-Home-Assistent-einbinden/td-p/542670
**Posts**: 3

Hallo zusammen,ich möchte meine Vitocal 250 in einen Homeassistent einbinden. Es wird bei mir tagsüber viel PV-Strom ins Netz gespeist. Diesen möchte ich nutzen um den Pufferspeicher mit der WP zu laden. Für Anregungen, wie ich den Pufferspeicher auch im Winter, wenn tagsüber die Sonne scheint und die Heizung nicht anspringt, laden könnte.Vielen Dank.
---
Hallo Oldjo,
 
dafür kannst du die Smart Grid Funktion nutzen. Diese kann während der Inbetriebnahme oder nachträglich über den Parameter 2560.0 aktiviert werden.
Über die Kontakte 143.4 (A) bzw. 143.5 (B) kann die SmartGrid-Funktion direkt an der Wärmepumpenregelung ausgeführt werden. Die Ansteuerung erfolgt dabei über ein separates Schütz, welches einen potentialfreien Kontakt zwischen 143.1 und 143.4 (A) bzw. 143.5 (B) herstellt.
Die Funktionen die darüber ausgeführt werden können, sind folgende:
■ kein Kontakt geschlossen: Wärmepumpe ist im Normalbetrieb
■ Kontakt (A) geschlossen: EVU-Sperre- Verdichter AUS- Heizwasser-Durchlauferhitzer kann eingeschaltet werden, die Freigabe erfolgt über den Parameter 2544
■ Kontakt (B) geschlossen: Betrieb der Wärmepumpe mit angepassten Temperatur-Sollwerten für verschiedene Funktionen. - Der Verdichter schaltet sich nur bei Bedarf ein. Die gültigen Einschaltbedingungen für die jeweilige Funktion müssen erfüllt sein. Für die jeweilige Funktion muss im Zeitprogramm eine Zeitphase aktiv sein.- Auf den Heizwasser-Durchlauferhitzer haben die angepassten Temperatur-Sollwerte keinen Einfluss. Der Heizwasser-Durchlauferhitzer wird bei Unterschreitung der Grenzen eingeschaltet, die ohne Smart Grid gelten.
Betrieb der Wärmepumpe mit angepassten Temperatur-Sollwerten für verschiedene Funktionen. Die Änderungen werden mit folgenden Parametern eingestellt:- Raumbeheizung - Smart Grid Sollwertanhebung für Raumtemperatur Parameter 2543.0- Raumkühlung - Smart Grid Sollwertanhebung für Raumkühlung Parameter 2543.1- Trinkwassererwärmung - Smart Grid Sollwertanhebung für Trinkwassererwärmung Parameter 2543.2- Erwärmung Heizwasser-Pufferspeicher  - Smart Grid Sollwertanhebung für Heizbetrieb Heizwasser-Pufferspeicher Parameter 2543.3 - Kühlung Heizwasser-Pufferspeicher - Smart Grid Sollwertabsenkung für Kühlbetrieb Heizwasser-Pufferspeicher Parameter 2543.4
■ Kontakt (A) und (B) geschlossen: Die Anlagenkomponenten werden auf die eingestellten max. Temperaturen beheizt oder auf die Mindesttemperaturen gekühlt. Der Verdichter schaltet sich sofort ein, auch wenn keine Zeitphase im Zeitprogramm aktiv ist.
Im Modus 4 wirken die folgenden Maximalwerte Heizen, Kühlen und Warmwasser:- Max. Vorlauftemperatur Heiz-/Kühlkreis 1 Parameter 1192.1- Max. Vorlauftemperatur Heiz-/Kühlkreis 2 Parameter 1193.1- Max. Vorlauftemperatur Heiz-/Kühlkreis 3 Parameter 1194.1- Max. Vorlauftemperatur Heiz-/Kühlkreis 4 Parameter 1195.1- Max. Warmwassertemperatur Parameter  504.4- Min. Vorlauftemperatur Kühlung Heiz-/Kühlkreis 1 Parameter  2409.0- Min. Vorlauftemperatur Kühlung Heiz-/Kühlkreis 2 Parameter 2410.0- Min. Vorlauftemperatur Kühlung Heiz-/Kühlkreis 3 Parameter 2411.0- Min. Vorlauftemperatur Kühlung Heiz-/Kühlkreis 4 Parameter 2412.0
 
Viele GrüßeFlo
---
Ich habe mir die Kontakte mit einem 5-adrigen Kabel in eine Verteilerdose geführt. Dort kann ich dann entweder direkt den potentialfreien Kontakt meines Wechselrichters nutzen, um das Überschuss-Signal zu geben.Da das aber nicht wirklich Smart zu steuern ist, habe ich einen Shelly 1 Mini verbaut. Dort kann man wenn man möchte trotzdem den Wechselrichter anbinden und sieht dann, wann das Signal anliegt, kann es aber getrennt davon über Home Assistant steuern.Inzwischen mache ich es ausschließlich über Home Assistant. Zum Thema Winter: Da hatte ich nie wirklich Überschuss, meine recht kleine Batterie von 7kWh wurde selbst an sonnigen Tagen nicht im Ansatz voll. Im HomeAssistant habe ich meine Vitocal über die Cloud-Integration eingebunden, aber - weil diese manche Werte nicht rausrückt und auch nicht zuverlässig ist - über open3e über CAN hinzugefügt. Aktuell noch etwas manuelle Arbeit, aber wird immer einfacher das umzusetzen. In beiden Fällen kann man sehen, ob man im bevorzugten Betrieb ist.

---

## Thread #12: Vitodens 200-W Integration ohne Server

**URL**: https://community.viessmann.de/t5/Gas/Vitodens-200-W-B2HF-11-Integration-in-Hausautomation-ohne/td-p/486788
**Posts**: 2

Hallo zusammen,ich habe eine Viessmann Vitodens 200-W B2HF-11 (2,5–11 kW) und möchte diese unabhängig von den Viessmann-Servern bzw. der ViCare-API in meine bestehende Hausautomation einbinden. Ziel ist es, die Steuerung und Datenerfassung lokal und direkt zu realisieren.Was ich erreichen möchte:1. Auslesen von Statusdaten:Betriebsstatus (Heizbetrieb, Warmwasser, etc.)Vor- und RücklauftemperaturenModulationsgrad des BrennersFehlercodes und Wartungszustände 2. Lokale Steuerungsmöglichkeiten:Anpassung der Solltemperaturen (Heizung und Warmwasser)Umschalten von Betriebsarten (z. B. Eco, Komfort, Absenkbetrieb)Steuerung von Zeitplänen und Modifikationen  ---Meine bisherigen Ansätze und Überlegungen:1. Nutzung der Optolink-SchnittstelleDie Vitodens 200-W verfügt über eine Optolink-Schnittstelle, die sich für lokale Kommunikation eignet. Hier ein paar konkrete Ansätze:USB-Optolink-Adapter:Viessmann bietet einen USB-Optolink-Adapter an, der an einen Laptop oder Mikrocontroller (z. B. Raspberry Pi) angeschlossen werden kann. Über diese Schnittstelle können Daten abgefragt und Befehle gesendet werden.Bekannte Protokolle: Viessmann nutzt das VBus-Protokoll oder ältere Varianten wie KW oder LPB. Es gibt Bibliotheken wie vcontrold, die dies unterstützen.Open-Source-Projekte wie vcontrold (github.com/openv/vcontrold) könnten eine Lösung bieten, um die Kommunikation mit der Heizung über einen lokalen Server (z. B. Raspberry Pi mit MQTT-Anbindung) zu ermöglichen. 2. Reverse Engineering der APIDie ViCare-API kommuniziert über das Internet, aber es gibt Möglichkeiten, diese zu analysieren und die zugrundeliegenden Befehle lokal zu replizieren. Tools wie Wireshark können helfen, die Netzwerkkommunikation zwischen der ViCare-App und der Heizung zu untersuchen.Ziel: Herausfinden, ob die Befehle über das lokale Netzwerk (LAN) direkt an die Heizung gesendet werden können, ohne die Viessmann-Cloud zu nutzen.3. MQTT für Integration in Smart Home SystemeSobald die Daten lokal ausgelesen werden (z. B. über Optolink oder API-Reverse-Engineering), können sie über MQTT in die Hausautomation eingebunden werden. Systeme wie Home Assistant, openHAB oder ioBroker unterstützen MQTT nativ und könnten Statusdaten visualisieren oder Steuerbefehle senden.Es gibt auch Projekte wie homebridge-vicare, die eine Verbindung zur Viessmann-API herstellen, allerdings müsste hier geprüft werden, ob eine lokale Nutzung möglich ist.4. Nutzung der EEBUS-SchnittstelleDie Vitodens 200-W unterstützt in einigen Fällen das EEBUS-Protokoll, ein standardisiertes Kommunikationsprotokoll für Smart-Home-Integration.Prüfen, ob EEBUS bei meinem Modell aktiviert ist.Falls ja, könnte dies als direkter Kommunikationsweg dienen, um die Heizung in Systeme wie KNX oder andere Hausautomationslösungen einzubinden. ---Offene Fragen:1. Hat jemand Erfahrung mit der Einrichtung von vcontrold oder ähnlichen Tools für die Optolink-Schnittstelle?2. Funktioniert die EEBUS-Integration zuverlässig für den lokalen Zugriff?3. Gibt es andere Tools oder Workarounds, die sich bewährt haben, um eine solche Heizung ohne Cloud- oder Serverbindung zu steuern?4. Welche Hardware-Kombination wäre ideal, z. B. Raspberry Pi mit USB-Adapter oder andere Gateways? ---Ich bin gespannt auf eure Erfahrungen und hoffe, dass wir hier gemeinsam eine Lösung finden können!Vielen Dank und viele Grüße,Marc
---
Hallo, dein B2HF hat keine Optolink Schnittstelle mehr.er hat auch keinen Eebus.Die  Kommunikation mit dem VM Backend Server ist verschlüsselt. Du kannst aber, wie es hier schon viele machen, über den CAN Bus darauf zugreifen https://community.viessmann.de/t5/Konnektivitaet/CAN-Bus-Home-Automation-E3-Generation-lokal-und-kos... VG

---

## Thread #13: Adapter CAN-Bus auf LAN Stecker

**URL**: https://community.viessmann.de/t5/Gas/Adapter-CAN-Bus-auf-LAN-Stecker/td-p/357554
**Posts**: 4

Hallo zusammen,ich habe eine Frage,gibt es für die Vitodens 300 W, siehe Anhang, einen Adapter, um die Datenleitung vom CAN-Bus auf LAN Stecker umzubauen?Im Forum Konnektivität bekomme ich leider keine Antwort.Freue mich über eine Info.Peter 
					
				
			
			
				
			
			
				
	
			
				
					
						Gelöst!
					
					Gehe zu Lösung.
---
Hallo divanc,einfache Lösung,Danke.VG
					
				
			
			
				
			
			
				
			
			
				
					
						Lösung in ursprünglichem Beitrag anzeigen
---
Hallo Sie können es ganz einfach mit einem Range Extender lösen, indem Sie mit dem Router die kabelgebundene LAN-Verbindungsfunktion wählen und die Kesselsteuerung mit seinem WLAN-Netzwerk verbinden.  VG
---
Hallo divanc,einfache Lösung,Danke.VG

---

## Thread #14: VC250 CAN Bus und WLAN

**URL**: https://community.viessmann.de/t5/Waermepumpe-Hybridsysteme/VC250-CAN-Bus-und-WLAN/td-p/327806
**Posts**: 7

Hallo,im Angebotsbaustein / Rechnungstext für meine VC 250 A steht folgender Passus:- Kommunikationsfähig über CAN-BUS, PlusBus, WLAN und Service Link (Low-Power-Funk).- Mit im Gerät integriertem Kommunikationsmodul. Fernbedienung und Monitoring des Geräts über Smartphone mit der ViCare App in Verbindung mit integrierter Internetschnittstelle und bauseitigem Internetzugang über WLAN möglichDaraus würde ich folgendes ableiten:- die CAN Bus Schnittstelle steht externen Erweiterungen und Steuerungen zur Verfügung und dafür ist eine passende Dokumentation verfügbar—-> wo finde ich die?- vollständige Fernbedienung über WLAN —> kein Umweg über eine Cloud—> umfängliche Konfiguration ohne zusätzliche Tools und Lizenzen  oder verstehe ich das falsch ? 
					
				
			
			
				
	LG JörgHaus Baujahr 1995, Heizkörper, VC 250-A AWO-E-AC 251.16Defekt seit Februar 2022 - Reparatur geplant Oktober 2023
---
Hallo Jörg,schön wärs....Kommunikationsfähig heißt leider nur, dass die Anlage prinzipiell vorbereitet ist.Über den CAN Bus sollte was machbar sein, aber die Dokumentation habe ich auch noch nicht gefunden. Es gibt aber wohl einen CAN Bus nach MOD Bus Adapter als Zusatzgerät (siehe hier: https://www.viessmann-community.com/t5/Brennstoffzelle-BHKW/Vitocal-250-A-Canbus-Beschreibung/td-p/2...). Aber ob es mir die Steuerung so viel Geld wert ist, weiß ich noch nicht. Und auch mit dem ModBus Adapter ist das Problem der fehlenden Dokumentation nicht gelöst.Die direkte Verbindung auf das System ist konzeptionell von Viessmann nicht vorgesehen. Das machen die Chinesen bei unserem Huawei PV Wechselrichter deutlich besser. Den kann ich auch ohne Internet direkt über das lokale WLAN per Modbus TCP abfragen. Und das direkt ab Werk, ohne zusätzlichen Adapter. Ich hoffe ja noch, dass Viessmann so langsam merkt, dass deren Server ein Flaschenhals werden könnte, wenn alle Besitzer zeitgleich Ihre Daten abfragen wollen. Viele Grüße,Christof
					
				
			
			
				
	Vitocal 250-A13, REH 2002, 120m², nur Radiatoren, PV Ost-West 11kWp.
---
Hi Christof,ja - die WAGO Box ist mir auch zu happig. Ich habe aus meinen Industrieprojekten noch einen Hilscher CAN Bus Adapter und den dazugehörigen Controller (quasi ein industrieller Raspberry PI).Die Modbus Registerbelegung der Software, die auf dem Wago läuft habe ich auch schon von Viessmann direkt erhalten.Jetzt wollen wir mal schauen  …. Oder habe ich was übersehen ?
					
				
			
			
				
	LG JörgHaus Baujahr 1995, Heizkörper, VC 250-A AWO-E-AC 251.16Defekt seit Februar 2022 - Reparatur geplant Oktober 2023
---
Die Frage ist allerdings immer noch offen - wenn es als eine verfügbare Option in der Gerätebeschreibung / Vertragstext steht - dann muss es doch auch eine Dokumentation/Beschreibung geben.Die Software für die WAGO Box ist ein Angebot von Viessmann - was ist, wenn ich mir ein eigenes Interface entwickeln lassen möchte?Also die Frage an die Viessmann Kollegen:- welcher CAN BUS Standard wird unterstützt?- welche Services sind darüber erreichbar? 
					
				
			
			
				
	LG JörgHaus Baujahr 1995, Heizkörper, VC 250-A AWO-E-AC 251.16Defekt seit Februar 2022 - Reparatur geplant Oktober 2023
---
Hallo JörgWende,
 
zu diesen Fragen kann ich dir keine Auskunft geben. 
 
Viele GrüßeFlo
---
Ok - wen sollte ich ansprechen? 
					
				
			
			
				
	LG JörgHaus Baujahr 1995, Heizkörper, VC 250-A AWO-E-AC 251.16Defekt seit Februar 2022 - Reparatur geplant Oktober 2023
---
Eventuell kann dir in unserem Developerbereich geholfen werden. 
 
https://www.viessmann-community.com/t5/Developer/ct-p/Developer
 
Viele GrüßeFlo

---

## Thread #15: CAN-Bus Schnittstelle Wago ohne Gateway

**URL**: https://community.viessmann.de/t5/Konnektivitaet/CAN-Bus-Schnittstelle-Wago-ohne-Gateway/td-p/312048
**Posts**: 12

Guten Tag, wie sieht denn die vorgesehene Lösung aus für Kunden die NICHT das "fertige" KNX Gateway kaufen sondern bereits eine Wago-Steuerung zuhause haben und nun nur die Karte 750-658 kaufen. Gibt es hierfür eine Art Anleitung oder Beispiele etc. MfG
---
Hallo Natrgaard,
 
eine Alternative zum Wago-Gateway gibt es leider nicht, bzw. wird diesbezüglich durch uns nichts angeboten oder supportet.
 
Informationen zum Gateway findest du hier. 
 
Gruß Benjamin vom Customer-Care-Team
---
Das ist natürlich äußerst ungünstig. Gibt es das PLC-Programm zum Download? also nicht nur das Update sondern das komplette Programm. Gibt es eine alternative um z. b. Die WW-Temp auf den KNX-Bus zu bringen? IoT? MfG
---
Alle verfügbaren Daten findest du unter dem angegebenen Link.
 

 Gibt es eine alternative um z. b. Die WW-Temp auf den KNX-Bus zu bringen? IoT?

Ggf. kannst du dazu die API nutzen, Informationen dazu findest du in unserem Developer-Portal.
---
OK Danke... Das kostet natürlich auch wieder monatlich wenn man mehr braucht.Dann bleibt im Endeffekt nichts anderes übrig als mit dem CAN-Modul und den Wago-Libs zu arbeiten und sich das Gateway selbst nachzubauen.Andere Hersteller lösen das Kundenfreundlicher. Das ist schon fast frech über 1000 Euro für ein Gateway zu verlangen das unterm Strich nichts kann und auch nicht wirklich erweiterbar ist. Als Alternative bietet man IOT und ähnliches an was auch, wer hätte damit nur gerechnet, ziemlich teuer kommt. Du kannst da natürlich nichts dazu, aber nochmal Viessmann kaufen kommt bei sowas sicher nicht mehr vor.
---
Hallo @CustomerCareBen auf der Webseite finde ich folgenden Absatz:● Support für die Gateway-Funktionen und unterstützten Viessmann Wärmeerzeuger Viessmann Wärmeerzeuger, die vom WAGO-Gateway unterstützt werden, müssen über eine entsprechende CAN Schnittstelle verfügen. Die möglichen funktionale Anwendungen werden über Datenpunktlisten und die Anwendungshinweise festgelegt. Für weitere Informationen zu den unterstützten Wärmeerzeuger und den verfügbaren Gateway-Funktionen, siehe hier. Der Link führt auf Eure Kontaktseite … hilfreich …
					
				
			
			
				
	LG JörgHaus Baujahr 1995, Heizkörper, VC 250-A AWO-E-AC 251.16Defekt seit Februar 2022 - Reparatur geplant Oktober 2023
---
Gefunden … das Dokument mit den unterstützen Wärmeerzeugern ist weiter unten direkt verlinkt.Führt aber direkt zur nächsten Frage:wo findet man das angemerkte Dokument ? 
					
				
			
			
				
	LG JörgHaus Baujahr 1995, Heizkörper, VC 250-A AWO-E-AC 251.16Defekt seit Februar 2022 - Reparatur geplant Oktober 2023
---
Hast Du schon eine Antwort, auf die Frage, wo man das Dokument findet? Viele Grüße,Christof 
					
				
			
			
				
	Vitocal 250-A13, REH 2002, 120m², nur Radiatoren, PV Ost-West 11kWp.
---
Ja …https://www.viessmann-community.com/t5/Waermepumpe-Hybridsysteme/Vitocal-250-A-Regelung/td-p/280228/...
					
				
			
			
				
	LG JörgHaus Baujahr 1995, Heizkörper, VC 250-A AWO-E-AC 251.16Defekt seit Februar 2022 - Reparatur geplant Oktober 2023
---
PS: der WAGO Gateway ist so teuer - also außer der Gewinnspanne als Händler verdient VM da nicht (viel) dran. Die Funktionalität könnte aber auch auf einem RPi und CANBUS Adapter abgebildet werden - man muss nur wollen - aber anscheinend niemand bei VM der das entscheiden könnte.
					
				
			
			
				
	LG JörgHaus Baujahr 1995, Heizkörper, VC 250-A AWO-E-AC 251.16Defekt seit Februar 2022 - Reparatur geplant Oktober 2023
---
>> eine Alternative zum Wago-Gateway gibt es leider nicht,... gibt es jetzt schon, kostenlos und lokal, siehehttps://www.viessmann-community.com/t5/Konnektivitaet/CAN-Bus-Home-Automation-E3-Generation-lokal-un... Viessmann unterstützt das natürlich nicht, weil sie nur Interesse an ihrem kostenpflichtigen und dauernd hakelnden Kram haben, bei dem sie Herr und Sammler aller Daten sind... Grüsse!
---
👍👍👍🤓👍👍👍
					
				
			
			
				
	LG JörgHaus Baujahr 1995, Heizkörper, VC 250-A AWO-E-AC 251.16Defekt seit Februar 2022 - Reparatur geplant Oktober 2023

---

## Thread #16: Zwei CAN Bus Zaehler Vitocharge VX3

**URL**: https://community.viessmann.de/t5/Strom-PV/Zwei-Can-Bus-Zaehler-Vitocharge-VX3-8-0A10/td-p/318228
**Posts**: 7

Meine Frage ist...Kann man zwei Viessmann Zähler E380CA an den Vitocharge anschließen?Einen als Netzanschlusspunkt-Zähler und einen weiteren für meine Vitocal 300-a...Er soll nur zur Visualisierung der Wärmepumpe in der myGridBox app dienen...Momentan habe ich für die WP einen ModBus zähler eingebaut und der sollte natürlich bleiben...Sprich den Canbus zähler zwischen den Modbus und der WP klemmen...Und falls es möglich ist wie klemmen ich die CanBus Leitung an... Schon mal danke im voraus 
					
				
			
			
				
			
			
				
	
			
				
					
						Gelöst!
					
					Gehe zu Lösung.
---
Moin Viktor, du kannst prinzipiell zwei Emeter netzseitig in Reihe installieren. Der VX3 benötigt jedoch einen CAN-Bus Zähler (E380CA) und die WP einen Modbus-Zähler. Die Bustopologien dürfen dabei nicht gemixt werden, lediglich lastseitig am Netz kann man die beiden Emeter in Reihe schalten um an Netzanschlusspunkt zählen zu können. Den CAN-Meter verbindest du dabei einfach mit einer JYSTY Klingelleitung mit deinem Vitocharge am ext. CAN-BUS (gelbe Stecker rechts oben an der EMCU). Wichtig ist, dass beide Enden terminiert sind. Dazu ist am CAN-Zähler bereits auf einem Ausgang eine rote Brücke (Abschlusswiderstand) gesetzt. Am VX3 hast du zwei gelbe CAN-Stecker wovon einer einen Abschlusswiderstand hat, der muss auch drin bleiben, solang der Kontakt nicht genutzt wird.
					
				
			
			
				
			
			
				
			
			
				
					
						Lösung in ursprünglichem Beitrag anzeigen
---
Hmm...wie es aussieht kann mir da keiner weiter helfen...😔
---
Hallo,bin zwar nicht vom Fach, aber nach Sichtung der Montageanleitung des E380CA müsste der Anschluss eines 2. Energiezählers im CAN-BUS möglich sein.Dazu müsste wohl die NODE-ID (Can-Adresse) geändert werden. Weiterhin muss auf den Abschlusswiderstand des letzten CAN-BUS-Teilnehmers geachtet werden. Hier der Link zur Anleitung:https://static.viessmann.com/resources/product_media/6152476VMA00001_1.PDF  Wie der 2.Zähler dann allerdings in der App visualisiert wird, kann ich dir leider nicht sagen.GrußSteven
---
@ZenturioDer Link zum PDF ist leider nur 404. Kannst du den Link zum Dokument neu aktivieren?Danke
---
@ghNeandr Der Link wurde aktualisiert.
---
@Zenturio Habe gerade eine Frage zum Anschluß am CAN Bus gestellt:https://www.viessmann-community.com/t5/Konnektivitaet/CAN-Bus-Home-Automation-E3-Generation-lokal-un...Hast du ev. dazu eine Aussage?

---

## Thread #17: WP-Anschluss Aussenteil CAN-Bus und 400V

**URL**: https://community.viessmann.de/t5/Waermepumpe-Hybridsysteme/WP-Anschluss-Aussenteil-fuer-CAN-Bus-und-400-V/td-p/345612
**Posts**: 2

Hallo, eine kleine Frage:im Beipack zur WP 250 AH liegen Steckverbindungen für CAN-Bus und 400 V. Gibt es Nachteile, wenn diese nicht verbaut werden und die Leitung im Außenteil direkt WP-Anschluss für CAN-Bus und 400 V direkt fest angeschlossen sind?Vielen Dank
---
Hallo Berg-Franz,
 
wenn es direkt aufgelegt wurde, ist dies in Ordnung. 
 
Viele GrüßeFlo

---

## Thread #18: Raspberry fuer Vitocal 250-A ohne PV

**URL**: https://community.viessmann.de/t5/Waermepumpe-Hybridsysteme/Raspberry-Einsatz-fuer-Viessmann-Vitocal-250-A-ohne-PV/td-p/382736
**Posts**: 2

Einsatz für Viessmann Vitocal 250-A ohne PV Energiezähler.Die hier vorgestellte Software für den Raspberry Pi 3 oder 4 benutzt die MODBUS-TCP Schnittstelle und verwaltet die PV Parameter zweier angeschlossener SMA – Wechselrichter. Ohne Probleme natürlich auch nur mit einem Wechselrichter. Wechselrichter anderer Fabrikate können durch Änderung der Schnittstelle in der fhem.cfg eingebunden werden,  z.B. Fronius über die Solar API.Das Projekt erfasst die komplette augenblickliche PV-Leistung der Anlage, andere Eigenschaften sind nicht berücksichtigt und auch nicht relevant für die Smart Grid Funktion. Natürlich ist die hier beschriebene Aussage meine objektive Sichtweise und ohne Gewähr. Nachtrag: fhem.cfg zur freien Verfügung für Fragen stehe ich zur Verfügung Anlage Beschreibung als PDF
---
Danke @mediastudio für das Projekt!Deine Informationen bezüglich der Steuerleitungen aus den PDF sollte man gelesen haben, wenn man die Smart-Grid funktion nutzen möchte, mit oder ohne Raspberry.  Grüße mb

---

## Thread #19: WP stufenlos regeln PV-Ueberschuss

**URL**: https://community.viessmann.de/t5/Waermepumpe-Hybridsysteme/Waermepumpe-stufenlos-regeln-entsprechend-PV-Ueberschuss-Vitocal/td-p/272888
**Posts**: 76

Hallo zusammen, ich würde gerne wissen, wie ich eine VITOCAL 250-A Wärmepumpe am besten mit einer PV Anlage kopple, um den Eigenverbrauch des PV Stroms möglichst zu maximieren. Die Wärmepumpe verfügt ja über einen Inverter/Frequenzumrichter, wodurch diese theoretisch stufenlos regelbar ist.Mein Smart-Home verfügt über einen Stromzähler direkt im Zählerschrank, sodass ich jederzeit weiß, wie viel Überschuss an PV Strom ins öffentliche Netz eingespeist wird. Ich möchte nicht die einfachen "Smart-Grid-Funktionen" nutzen, da mir dort lediglich Schaltkontakte zur Verfügung stehen, und ich die Wärmepumpe so nicht stufenlos regeln könnte. Am liebsten würde ich mithilfe einer Schnittstelle/ einem Protokoll wie Modbus, meinen Überschuss an PV Strom von meinem Gebäudeleitsystem an die Wärmepumpe melden, sodass diese dann entsprechend stufenlos mit dieser Leistung arbeitet. Ist dies möglich und wenn ja, wie?Gibt es eine Schnittstellenbeschreibung oder ähnliches? Vielen Dank im Voraus @Flo_Schneider Sie konnten teilweise bei ähnlichen Fragen weiterhelfen. Evtl. wissen Sie auch hier Bescheid.
---
Hallo,ich hänge mich bei dieser Frage gleich noch mit folgenden Fragen dran: Wenn der Viessmann Smartmeter bei der 250-A bereits mit installiert wurde,welche Einstellmöglichkeiten, bzw. Parameter gibt es jetzt bereits schon in der Aktuellen Regelungssoftware die man Nutzen kann ? Gibt es hier wie bei der 200-A ein Handbuch, wo alle möglichen Parameter angeführt sind ? Hintergrund meiner Frage:wenn man schon bei der 250-A diesbezüglich selber so gut wie keine Parameter einstellen kann, währe solch eine Info für den Endanwender sehr Hilfreich, bzw. in Summe viel Effizienter, da man sich im Vorfeld bereits Gedanken machen kann, was man wie eingestellt haben möchte, und nicht erst dann, wenn der VM Techniker bereits vor der Anlage steht. lgGuennie
---
Hallo, meines Wissens sind diese Funktionen im der 250-A noch nicht implementiert, das entsprechende Software-Update soll Ende des Jahres kommen... (https://www.viessmann-community.com/t5/Konnektivitaet/Passendes-PV-System-fuer-Vitocal-250-A/m-p/245...) @Viessmann: gibt es schon einen Termin, wann das Update erscheinen könnte? Viele Grüße,Philipp
---
Hallo TimG,
 
für die PV-Funktion wird der über uns zu beziehende CAN-BUS Smartmeter benötigt, welcher in die PV-Zuleitung kommt. Für die Visualisierung würde noch einer am Netzanschlusspunkt benötigt werden. 
 
Wann das neue Softwareupdate genau kommt, kann ich euch noch nicht sagen. Es wird aber nicht mehr lange auf sich warten lassen.
 
Viele GrüßeFlo
---
Hallo Flo, wie findet das Softwareupdate denn dann seinen Wege auf die Vitocal 250-A? Irgendwie habe ich das bisher noch nicht gelesen. Automatisch oder nur durch den Installateur... etc... Viele Grüße
---
Hallo Herr Schneider,ich hätte noch ein paar Fragen zu Ihrer Antwort. Gibt es zu der von Ihnen genannten "PV-Funktion" noch eine genauere Dokumentation, in die ich mich einlesen könnte?Haben sie eine Artikelnummer für das Smart Meter?Wäre es nicht sinnvoller, dass ich den Smart Meter direkt am Netzanschlusspunkt einbaue anstatt in der PV-Zuleitung?Denn die Wärmepumpe soll ja nur den "überschüssigen" Strom verwenden.Bsp. Meine PV-Anlage produziert zum Zeitpunkt X 10kW Strom. Im Haus werden 5kW verbraucht. Bedeutet ich hätte 5kW übrig, die die Wärmepumpe nutzen kann.Hätte ich den SmartMeter im Netzanschlusspunkt montiert, würde dieser einen Überschuss von 5kW messen und diesen an die Wärmepumpe weitergeben. Sodass diese dann mit 5kW Leistung laufen kann.Hätte ich den SmartMeter direkt in die PV-Zuleitung montiert, detektiert dieser 10kW sodass die Wärmepumpe denkt, sie könnte 10kW nutzen, was jedoch nicht der Fall ist und ich müsste zusätzlich die 5kW, die mein Haus zu diesem Zeitpunkt benötigt, vom Netz beziehen.Wird es mit dem Softwareupdate auch möglich sein, die/eine Schnittstelle selbst mit dem überschüssigen PV-Strom zu beschreiben?Denn ich habe bereits einen modbusfähigen EnergyMeter am Netzanschlusspunkt verbaut und würde mir gerne die Anschaffung und den Einbau weiterer Hardware sparen. Ich selbst bin Elektrotechnik Ingenieur & Softwareentwickler, sodass die Programmierung jagdlicher Schnittstelle mit ausreichender Dokumentation kein Hindernis wäre. Variante B, falls Variante A nicht möglich ist.Kann ich den Viesmann SmartMeter auch mit anderen Systemen auslesen?Dann könnte ich meinen vorhandenen Energy Meter ausbauen und für eine andere Anwendung nutzen und den von Viessmann in den Netzanschlusspunkt einbauen.Viele Grüße Tim Gegenheimer
---
Hallo Tim, da man hier momentan recht wenig von den Herren von Viessmann hört versuche ich dir mal ein paar deiner Fragen zu beantworten 😉  @TimG  schrieb:Hallo Herr Schneider,ich hätte noch ein paar Fragen zu Ihrer Antwort. Gibt es zu der von Ihnen genannten "PV-Funktion" noch eine genauere Dokumentation, in die ich mich einlesen könnte?Bisher habe ich weder hier in der Community noch im Internet eine entsprechende Dokumentation gesehen. Eine genaue Beschreibung bzw. Dokumentation der PV-Funktion wurde hier aber bereits in diversen Beiträgen angefragt/gefordert. Haben sie eine Artikelnummer für das Smart Meter? Das Smart Meter wird unter dem Namen "Viessmann Energiezähler 3-phasig für 2-stufige Eigenstromnutzung" und Artikelnummer ZK06026 geführt. Wäre es nicht sinnvoller, dass ich den Smart Meter direkt am Netzanschlusspunkt einbaue anstatt in der PV-Zuleitung?Denn die Wärmepumpe soll ja nur den "überschüssigen" Strom verwenden.Bsp. Meine PV-Anlage produziert zum Zeitpunkt X 10kW Strom. Im Haus werden 5kW verbraucht. Bedeutet ich hätte 5kW übrig, die die Wärmepumpe nutzen kann.Hätte ich den SmartMeter im Netzanschlusspunkt montiert, würde dieser einen Überschuss von 5kW messen und diesen an die Wärmepumpe weitergeben. Sodass diese dann mit 5kW Leistung laufen kann.Hätte ich den SmartMeter direkt in die PV-Zuleitung montiert, detektiert dieser 10kW sodass die Wärmepumpe denkt, sie könnte 10kW nutzen, was jedoch nicht der Fall ist und ich müsste zusätzlich die 5kW, die mein Haus zu diesem Zeitpunkt benötigt, vom Netz beziehen. Die Aussage dass das Smart Meter in der PV-Zuleitung eingebaut werden muss ist unlogisch und zumindest laut Montage- und Serviceanleitung der Vitocal 250-A auch nicht (ganz) korrekt.Laut Schaltbild auf Seite 77 wird die WP direkt hinter dem Zweirichtungszähler des Hausanschluss angeschlossen. Der Viessmann Energiezähler sitzt dann wiederum zwischen Hausanschluss und den restlichen Haushalts-Verbrauchern sowie der PV-Anlage. Wird es mit dem Softwareupdate auch möglich sein, die/eine Schnittstelle selbst mit dem überschüssigen PV-Strom zu beschreiben? Aktuell wurde hier nur mehrfach berichtet das die bisher ausgelieferten 250-A noch keine Software für das Energiemanagement mit dem Energiezähler installiert hat und das es diesbezüglich diesen Winter ein Update geben soll. Mehr konnte man hier nach meinem Wissen über das Softwareupdate noch nicht erfahren. Das Ganze ist für Kunden wie mich, welche bereits eine PV-Anlage besitzen und auch schon die Vitocal 250-A bestellt bzw. installiert bekommen haben recht unbefriedigend. Haben wir doch die WP auch auf Grund der Werbeversprechen bezüglich Konnektivität und Intelligenz gekauft. Ich hoffe ich konnte dir etwas weiter helfen. Eventuell gibt es ja auch bald mal wieder News von offizieller Seite 😉
---
Hallo Sasha, vielen Dank für deine ausführliche Antwort!! 🙂Dann werde ich wohl erstmal abwarten, bis das Update erscheint. Hoffentlich setzt Viessmann damit dann eine entsprechende Funktionalität um. Viele GrüßeTim
---
Hallo, erst mal eine frohes neues zusammen!Das alte Jahr ist nun zuende, ohne dass ein Update zur Einbindung von PV-Anlagen in die 250-A veröffentlicht wurde.@Flo_Schneider, gibt es Neuigkeiten zu dem Thema? Viele Grüße!
---
Hallo, angeblich soll das Update bereits seit anfang Dezember 22 verfügbar sein, nur damit du das auch bekommst musst Du Dich selber “Aktiv” an Deinen HB wenden…..das hier der HB oder VM ”von selber” bei Dir wegen dem Update vorstelllig wird, das wird mit ziemlicher Sicherheit leider nicht passieren…..😉 lgGuennie
---
Hallo Guennie, vielen Dank für die Info, das sind doch schonmal prinzipiell gute News. Gibt es auch eine Art Funktionsbeschreibung zu dem Update. Denn ich würde gerne wissen was genau nun unterstützt wird bevor ich meinen Heizungsbauer kommen lasse.@Guennie  hast zu evtl. zufällig etwas entsprechendes und könntest es hier hochladen oder den Link mit uns teilen? 🙂 Viele GrüßeTim
---
leider hab ich diebezüglich auch nicht mehr, als die Info, das das Update verfügbar sein solll…. lgGuennie
---
Hallo TimG, ich bin auch einer der Gefrustenden wegen der  hochgepriesenen "Konnektivität" meiner neuen A-252. Falls Du VIEL Zeit und NOCH MEHR Leidenschaft mitbringst, kann ich Dir mit dem Homeautomation-System von FHEM einen Weg (ein neues Hobby) aufzeigen, der zumindest eine Ubergangslösung bieten kann.In FHEM gibt es mit vitoconnect bereits ein Modul, das über die Viessmann-API zyklisch z.B. alle 5 Minuten Werte abruft und das auch Werte setzen kann (z.B. HK1-Betriebsart, Steigung, Neigung, Warmwasser-Sollwert, WW-Einmalanforderung, Urlaub, ...).Die Verknüfung zur deinem Gebäudeleitsystem oder deiner PV-Anlage sollte in FHEM auch über Modbus funktionieren (bei mir ist es das Modul gen24 zur Anbindung eines Fronius-WR)  oder du zapfst die optische Schnittstelle des Einspeise- oder Zweirichtungszählers an.Was dann noch fehlt ist die entsprechende Regelung und eine geeignete Visualisierung. Beides baue und teste ich gerade für meine Anlage in einem eigenen Modul. Das Modul plane ich zumindest zu Testzwecken in FHEM freizugeben.Es soll folgende Funktionen bieten:* Regelung Heizbetrieb Ein/Aus je nach Heizbedarf von den Raumthermostaten (Homematic-IP)* Heizkurve Niveau erhöhen je nach Heizbedarf* Heizkurve Steigung erhöhen je nach Vortageswerten* Regelung der Zirkulationspumpe über Zeit, Bewegungsmelder, Anwesenheitserkennung, TasterDeine Anforderung könnte erfüllt werden über (wie Smart-Grid nur etwas feiner und einstellbar):* WW-Anforderung über Erhöhung der Solltemperatur um 5-10K* Erhöhung der Heizleistung über Anhebung des Niveaus um 1-5K* Berücksichtigung von Wetterprognosen zum zeitoptimalen EinsatzDas Modul ist so aufgebaut, dass ein späterer Umstieg von API auf eine lokale Anbindung mit überschaubarem Aufwand funktionieren sollte. GrußMoewe
---
Hallo Moewe,vielen Dank für deinen Vorschlag. Aber wie du richtig erwähnt hast, benötigt das extrem viel Zeit.Außerdem könnte ich bei einer Veränderung der Heizkurve nicht sicher vorhersehen, mit wie viel Leistung [kW elektrisch] die Wärmepumpe arbeiten wird. Folglich könnte ich es auch nicht optimal an die zur Verfügung stehende elektrische Leistung der PV-Anlage anpassen. Da ja scheinbar seit Anfang Dezember ein Update zur Verfügung steht, hoffe ich, dass entsprechende Funktionalitäten dort umgesetzt wurden und werde noch einmal auf die Nachricht von Herrn Schneider antworten und nachfragen.Grüße Tim
---
Hallo Herr Schneider, bzw. @Viessmann -Team, Ist es mit dem im Dezember 2022 erschienenen Software Update nun möglich, der Wärmepumpe vorzugeben, mit wie viel Leistung (elektrisch) diese arbeiten soll? Und falls ja, wo finde ich eine entsprechende Beschreibung der neuen Funktionen? Viele GrüßeTim
---
Hallo Tim,
 
mit dem Update vom November/Dezember kann dies aktuell nicht genutzt werden. Die PV-Funktion wird voraussichtlich mit einem der nächsten Updates eingeführt. Dann kann ich auch genaueres zur Funktion sagen. 
 
Viele GrüßeFlo
---
Hallo, dann habe ich ja hoffentlich echt gute Chancen dass es in meiner Vitocal 250 die erst im Spätsommer kommt schon eingebaut ist oder? Ich will nicht noch 2 Energiemeter kaufen müssen und in den Zählerschrank einbauen.
---
Die Energymeter sind nicht in der Wärmepumpe eingebaut. Um die PV-Funktion mit Visualisierung nutzen zu können, müssen diese bauseits gesetzt werden. 
 
Viele GrüßeFlo
---
@Flo_Schneider Hallo, das kann doch nicht euer Ernst sein. Ich habe doch schon 2 Energymeter im Zählerschrank eingebaut. Jetzt nochmals 2 von Viessmann gehen schon aus Platzgründen nicht mehr rein und 4 Energymeter die alle dasselbe messen ist doch ein klein wenig übertrieben.
---
Hallo,ich verstehe Deine absolut berechtigte Frage. Nur hier gibt es einen Punkt, warum VM eigentlich gar nichts anderes übrig bleibt, als das Ganze derzeit so zu lösen. Das Problem ist, das VM eine für Endkunden möglichst einfache Lösung benötigt, und es in diesem Bereich (Modbus-Parameter) keinerlei Standard gibt. Es kocht jeder Geräteanbieter sein eigenes "Süppchen". Jeder PV Wechselrichter spricht Modbus, jedoch in seiner eigenen Adresswelt, Jedes Smartmeter ebenfalls, und wenn Du einen Batteriewechselrichter hast sieht es wieder anders aus, und in der WP Welt sowieso noch einmal anders.......Ob wohl es den so genannten "SunSpec Standard" gäbe, aber selbst der ist nicht verpflichtend, und nicht jeder Gerätehersteller hält sich an diesen. Es gibt sogar Gerätehersteller, die deren Modbus-Protokoll nicht veröffentlichen, nur um zusätzlich eigene völlig überteuerte OEM-Smartmeter mit eigens für sie "verbogene Firmware" verkaufen. Es Lebe die Profitgier......  Genau deswegen bin ich bei mir gleich einen komplett anderen Weg gegangen, und habe einen Raspberry Pi sozusagen als Dolmetscher dazwischen geschalten. Ich setze dazu ausschließlich Geräte von Herstellern ein, die das Protokoll offenlegen, und jedes Gerät spricht nur mit dem Raspberry, und dieser Übersetzt das Ganze in die jeweilige "Sprache" für das andere Gerät. So etwas gibt es bisher nicht "von der Stange" sondern muss komplett individuell programmiert werden.....Deswegen gehen die Gerätehersteller den für die "Allgemeinheit" einfacheren Weg, jedes Gerät bekommt seinen eigenen Zähler - hast 5 Geräte hast 5 Zähler, die alle das komplett gleiche machen, nämlich Strom/Leistung messen. Das ist in der Tat ein absoluter Nonsens das Ganze, aber was willst machen, wenn es hier keine Norm gibt, sondern datentechnischer "wilder Westen" vorhanden ist. Dann muss man sich entweder selber helfen, oder man hat eben leider 5 Smartmeter im Zählerkasten...... lgGuennie
---
Hallo Guennie, das was du hier schreibst ist nach meiner Meinung nur teilweise richtig. Das "VM eigentlich gar nichts anderes übrig bleibt, als das Ganze derzeit so zu lösen" ist nach meiner Meinung als Aussage absoluter Quatsch. Es gibt sehr wohl Kommunikationsstandards wie z.B. SEMP und EEBus welche offen oder standardisiert sind und die Möglichkeit bieten das PV-Anlagen und  Wärmepumpen herstellerübergreifend kommunizieren. Gerade renommierten Hersteller von PV-Wechselrichtern und Energiemanagern wie z.B. SMA sind da offen und arbeiten auch schon seit Jahren mit Herstellern wie Stiebel Eltron, Vaillant und  Wolf zusammen so das deren WP von dem Sunny Home Manager 2.0 direkt angesteuert werden können. Warum sich gerade Viessmann hier so schwer tut ist mir persönlich ein Rätsel!Wir hatten es in diesem Forum bereits vor einem knappen Jahr über die neue WP Generation.Viessmann wirbt sowohl auf den hier im Forum geteilten Links/Websites, als auch in seiner Fach-Information zu der neuen Vitocal 250-A Serie, vollmundig damit das sich bei der neuen "Elektronik-Plattform" auch Gebäudeleittechnik anderer Anbieter mit KNX oder EEBUS problemlos in die Plattform integrieren lassen. Hierunter verstehe ich das Produkte wie die 250-A, welche über diese neue Plattform verfügen, auch mit Produkten anderer Hersteller, welche einen der oben genannten Kommunikationsstandards unterstützen, kommunizieren und sich gegenseitig ansteuern können. Wenn dies nicht der Fall ist dann sind die veröffentlichten Produktinformationen leider unpräzise und dadurch irreführend. Die aktuell angebotene Lösung mit den zwei VM Energiemeter passt für mich zu deinem vierten Absatz. Mir kommt es so vor als ob man momentan lieber die eigene Technik verkauft anstelle eine Kommunikation mit Technik von Drittanbietern zu ermöglichen. Ob diese Rechnung am Ende aufgeht wage ich zu bezweifeln. Neben den Anschaffungskosten von 700-800€ für die zwei Energiezähler muss im Sicherungskasten überhaupt erst einmal die Möglichkeit (Platz und Struktur) bestehen diese Zähler noch unter zu bringen. Bei einem Bestandsgebäude wird dies in den wenigsten Fällen noch möglich sein. Abschließend noch ein Wort zum Thema Updates. Ich hoffe inständig das sich die weiter oben getroffene Aussage das man sich für die Installation eines Updates aktiv an seinen HB wenden muss nicht stimmt!Wie soll denn das in der Praxis funktionieren? Ich schreibe meinen HB jedes Jahr ein bis zweimal an und frage auf Verdacht ob es für meine WP ein Update gibt. Sollte dies dann der Fall sein kommt der HB irgendwann einmal wenn er Lust und Zeit hat bei mir vorbei, installiert das Update und verlangt 120€ für Anfahrt und Arbeitszeit?!? Nichts für ungut aber hier besteht noch deutlich Luft nach oben. GrüßeSascha
---
Hallo, zum Thema Standard  - meine Anlagenkonfiguration sieht in Natur von der Hardware her so aus:elgris Smartmeter : Modbus TCP oder Modbus RTU (sunspec Standard)3kW SMA Wechselrichter : Modbus TCP (sunspec Standard) (komplett anderer Adressbereich)5kW SolarEdge Wechselrichter : Modbus TCP (komplett anderer Adressbereich)5kW Victron Batterie Wechselrichter : Modbus TCP (wieder anderer Adressbereich)VM Wärmepumpe 200-A : kann überhaupt kein Modbus sondern nur knx ( somit gleich ein komplett anderes Protokoll und auch die Anbindung an die restliche Umgebung komplett anders als beim ganzen Rest)....ich sehe hier in der Praxis nicht die geringste Möglichkeit das alle Geräte miteinander direkt kommunizieren (können)....eben....Wild-West...... Somit ein Raspberry pi dazwischen als Modbus / knx / Adressumsetzer, der ganz nebenbei noch alle Daten in eine DB aufzeichnet, das ganze grafisch auswertet, und das Energiemagement des kompletten Hauses regelt. und  - zum Glück habe ich keine neue 250-A:hier kannst Dir aktuell den VM Smartmeter zwar an die Anlage schnallen - jedoch du bekommst derzeit nicht mehr als "nette Bildchen" in der App dargestellt. PV/WP Kommunikation Regelung von der WP-Software her nicht fertig (Update mittlerweile angeblich schon bis ins Frühjahr/Sommer 2023 verschoben.Wenn die dann fertig ist bekommst keine Benachrichtigung, sondern du musst selber immer wieder nachfragen, ob diese bereits verfügbar ist.Die Parametrisierungsgeschichte , wie man sie noch von der alten Serie her kennt - hier nicht mehr möglich - für jede Änderung brauchst den HB. Mein Arbeitskollege kann bei seiner 250er nicht einmal die Hysterese des WW Speichers nach seinen pers. Bedürfnissen anpassen, sondern nur die Solltemperatur -----> für das andere kein Zugang.Datenanbindung nach außen hier ebenfalls nur über ein A......teures Wago VM/KNX oder VM/Modbus Schnittstellenmodul möglich........ also jetzt möchte ich echt wissen, was hier Quatsch sein soll.....das ist (leider) schlicht und einfach die aktuelle Realität. lgGuennie
---
Guten Morgen Guennie, ist jetzt nicht böse gemeint aber deine PV-Anlage ist halt auch alles andere als Standard und von den Komponenten wahrscheinlich über die Jahre gewachsen. Mir und wahrscheinlich den meisten anderen welche das Thema hier in diesem Forum angesprochen haben geht es aber um die Kommunikation der WP mit einer "standard" PV-Anlage. Bedeutet wir reden über einen, eventuell zwei (Hybrid-)Wechselrichter mit einem Energiemanager vom gleichen Hersteller (Fronius, Kostal, SMA, etc.) welcher bereits alle Energieflüsse misst und auch steuern kann. Ich behaupte jetzt mal das die meisten PV-Anlagen welche in den letzten Jahren aufgebaut/angeschafft wurden so aussehen. Mit solch einer PV Anlage bzw. dem dazugehörigen Energiemanager sollte eine moderne WP im Jahr 2023 auch kommunizieren können. Bei bei anderen Herstellern ist dies ja auch schon seit geraumer Zeit möglich obwohl deren WP inkl. Software nicht erst vor kurzem entwickelt und auf den Markt gebracht wurden. Man sieht also es gibt durchaus herstellerübergreifende Lösungen welche nicht zwei zusätzliche Energymeter benötigen. Vielleicht müssen wir Viessmann nur noch etwas Zeit lassen und die Anbindung an bestehende Energiemanager von renommierten PV-Herstellern ist bald möglich. Die Hoffnung stirbt bekanntlich zuletzt 😉 Mit einer "schlauen Teamplayerin" welche sich "bestens vernetzen" lässt, wie es aktuell beworben wird, hat die neue Vitocal für mich jedenfalls nichts zu tun. Aktuell sieht es für mich eher so aus als ob Viessmann sein eigenes Geschäft im Bereich von PV Anlagen und Batteriespeichern ausbauen will und sich daher auf die Kommunikation mit den eigenen Geräten beschränkt.  Was den Zugriff auf Updates und Einstellungen betrifft kann ich mich dir nur anschließen. Hier wird von Viessmann scheinbar völlig falsch eingeschätzt wie weit der Support des durchschnittlichen HB nach der Installation der Heizungsanlage noch geht. Ansonsten bin ich mit der neuen 250-A aber bisher sehr zufrieden. Man muss auch mal etwas Positives sagen 🙂 VGSascha
---
@Sascha_82: Es freut mich, dass du mit der neuen 250-A zufrieden bist. Was die Energymeter betrifft, so habe ich dir den Ist-Zustand mitgeteilt. Hierzu wird es in Zukunft noch weitere Updates geben. Was dabei wann genau eingeführt wird, kann ich aktuell aber noch nicht mitteilen. Dass der Weg aktuell noch über den Fachbetrieb gehen muss, um ein neues Update zu bekommen, ist nicht zufriedenstellend, das weiß ich. 
 
Viele GrüßeFlo
---
Hallo und guten Morgen,@Guennie Also, ich bin gerade dabei meinen uralt Zählerschrank gegen einen neuen auszutauschen da der alte einfach viel zu klein ist. Der ist von 1970 und hat nur 800X680mm. Zu meiner Überraschung wurde der vor 2 Jahren vom Netzbetreiber noch so anstandlos abgenommen als der Elektriker des Solateurs noch 2 SLS-Schalter in den verplompbaren Bereich für die Mietwohnung und unsere Wohnung und den Kostal KSEM im oberen Anschlussraum eingebaut hat. Ein Kombiableiter ist in dem Schrank nicht vorhanden. Aufgrund von eklatantem Platzmangel in dem alten Schrank gibts seitdem im Keller eine UV für die Kellerräume und die Solaranlage. Für die beiden Wallboxen sitzt ein kleiner UV in der Garage. Beide UV sind im alten Schrank über Neozedelemente vorgesichert. Dafür war in dem Schrank gerade noch Platz vorhanden.Für die kommende Wärmepumpe und die Erweiterung der PV Anlage werde ich jetzt den Zählerschrank versetzen und habe deshalb einen 5-feldrigen gekauft. Der hat 1400x1100mm. Feld 1 ist für den Zähler des Mieters, Feld 2 wird der Zähler für unsere Wohnung, Feld 3 und Feld 4 sind für den Kaskadenzähler und das TRE Gerät geplant. Feld 5 ist dann das Verteilerfeld mit APZ unten. Ich habe also 5 Hutschienen, das entspricht 60Platzeinheiten dort frei. Eine Hutschiene wird komplett für Wärmepumpe, FI,2x3poliger LS, und 2x1poliger LS-Schalter belegt, bleiben noch 4.Eine weitere Reihe ist komplett voll für die Absicherung der einzelnen Kellerräume. Also einmal 40A FI und 8LS-Schalter. Bleiben noch 3 Reihen.Den KSEM darf man nicht mehr in den AAR Raum über dem Zähler einbauen muss also auch rechts ins Verteilerfeld. Einen eigenen 3-Punkt Zweirichtungszähler für die Kaskade darf ich hier auch nicht in das 3.Zählerfeld einbauen. Gerade eben nochmals nachgefragt. Laut Netzbetreiber dürfen da nur offizielle Zähler rein. Da ich noch nicht weiss ob ich den Wärmepumpentarif beantragen werde benötige ich also einen Hutschienenzweirichtungszähler der auch rechts ins Verteilerfeld muss. Also wieder eine Reihe fast voll. Bleiben noch 2 Reihen übrig. Bei 3,8ct Unterschied zwischen Haushaltstarif und Wärmepumpentarif rentiert sich das wegen der Grundgebühr für den zweiten Zähle rund dem TRE Gerät erst ab ca. 4000kWh Wärmepumpenstrom. Wobei ich dann immer noch den Nachteil habe dass mir das EVU 3 mal am Tag die Wärmepumpe abschalten kann.   Geplant war eigentlich dass ich die beiden UV für die PV-Anlage und die Wallboxen wieder auflöse und alles in den neuen Schrank einbaue. Das kann ich aber vergessen. Das geht jetzt schon nicht mehr rein. Also müssen die 2 UV bleiben und im  Zählerschrank weiterhin mit Neozed vorgesichert werden. 2xNeozed sind 9 Platzeinheiten und dürfen natürlich auch nicht mehr in dem AAR über dem Zähler eingebaut werden. Also wieder fast ne Reihe voll im Verteilerfeld. Bleibt noch eine Reihe übrig. Von dieser letzten Reihe benötigt das Siedle Netzteil NG401 alleine auch schon 6 Platzeinheiten. Und jetzt kommt Viessmann und will nochmals 2 Energimeter für die Verbindung Wärmepumpe, PV-Anlage haben. Wo soll ich das einbauen? Mein Schrank hat schon 1400mm Breite. Einen 6-feldrigen Schrank gibts von Hager meines Wissens nicht. Könnte ja noch ein Zusatzschrank neben den neuen Schrank schrauben. Nein, das werde ich definitv nicht machen.
---
Hallo zusammen, ich würde gerne wissen, wie ich eine VITOCAL 250-A Wärmepumpe am besten mit einer PV Anlage kopple, um den Eigenverbrauch des PV Stroms möglichst zu maximieren. Die Wärmepumpe verfügt ja über einen Inverter/Frequenzumrichter, wodurch diese theoretisch stufenlos regelbar ist.Mein Smart-Home verfügt über einen Stromzähler direkt im Zählerschrank, sodass ich jederzeit weiß, wie viel Überschuss an PV Strom ins öffentliche Netz eingespeist wird. Ich möchte nicht die einfachen "Smart-Grid-Funktionen" nutzen, da mir dort lediglich Schaltkontakte zur Verfügung stehen, und ich die Wärmepumpe so nicht stufenlos regeln könnte. Am liebsten würde ich mithilfe einer Schnittstelle/ einem Protokoll wie Modbus, meinen Überschuss an PV Strom von meinem Gebäudeleitsystem an die Wärmepumpe melden, sodass diese dann entsprechend stufenlos mit dieser Leistung arbeitet. Ist dies möglich und wenn ja, wie?Gibt es eine Schnittstellenbeschreibung oder ähnliches? Vielen Dank im Voraus @Flo_Schneider Sie konnten teilweise bei ähnlichen Fragen weiterhelfen. Evtl. wissen Sie auch hier Bescheid.
---
Leute, nehmt das was ihr habt und gut ist ! Ihr programmiert z.B. 3 Heizzeiten (morgens, mittags, abends) mit Heizpausen, die gerade so lang sind, dass ihr keine unangenehmen Abfälle der Raumtemperatur wahrnehmen könnt.Dann überhöht ihr die Raumtemperatur Sollwerte in der Mittags- Heizphase, mittels Komfort-Stufe, z.B. auf 24°C. In diese Mittagsheizphase baut ihr auch die WW Phase mit ein, oder lässt diese daran anschließen.Statistisch habt ihr in der Zeit von 11:00 Uhr bis 14:00 Uhr bei einer Süd Dach PV das größte PV Angebot, welches dann bestmöglich ohne Mehrkosten verwertet wird. Bei einer West/Ost PV Anlage wäre dann eher die Überhöhung und WW in der Vormittags- bzw. Nachmittags Heizphase umzusetzen. GrußMichael
---
@Flo_Schneider Guten Morgen, ich hätte kurz ne Frage zu dem Viessmann Energiezähler ZK06026. Bei einer Kaskadenschaltung wird ja hinter dem ersten Zähler vom EVU ein 2. Zweirichtungszähler eingebaut. Zwischen den beiden Zählern hängt die Wärmepumpe. Da ich höchstwahrscheinlich keinen Wärmepumpentarif beantragen werde wird dieser 2. Zähler kein 3-Punktzähler werden sondern ein Hutschienenzähler. Sehe ich das jetzt richtig dass der Viessmann ZK06026 diese Aufgabe des zweiten Zählers übernehmen kann? Der hat ja ein Display und ist ein Zweirichtungszähler.  Die Energiewerte für Bezug und Einspeisung werden saldiert angezeigt, oder?Direkt vor dem Wechselrichter habe ich im Moment noch einen normalen Eltako DSZ15DE eingebaut um die Erzeugung zu messen. Du hast ja schon öfters geschrieben dass man 2 dieser Viessmann Energie Zähler benötigt um das ganze visualisieren zu können, d.h. also ich müsste diesen DSZ15DE auch gegen einen Viessamann ZK06026 austauschen. Habe ich das ganze so richtig verstanden?
---
Hat eigentlich schon irgendjemand so einen ZK06026 Energiezähler eingebaut? Lieferbar scheint der ja nirgends zu sein.
---
Hallo Kruemel64,
 
für die PV-Funktion und die Visualisierung benötigst du zwei dieser ZählerZK06026 , das ist korrekt. 
 
Viele GrüßeFlo
---
@Flo_Schneider kannst mir bitte auch was zu meinen anderen Frsgen oben sagen. Ersetzt so ein ZK 06026 einen Zweirichtungszähler? Gibts zu dem Zähler irgendwo eine Beschreibung? Ich finde bei Viessmann nichts zum Downloaden. Zeigt der mir die Energiewerte saldierend an? Ich sollte schon wissen wieviel PV Strom und wieviel Netzstrom die Wärmepumpe benötigt. Kann ja dem Mieter im EG nicht den Strom für Heizung und Warmwassr schenken.
---
Unter dem nachfolgenden Link findest du die Montageanleitung inklusive Informationen. 
 
https://static.viessmann.com/resources/technical_documents/DE/de/VMA/6152476VMA00001_1.pdf?#pagemode...
 
Viele GrüßeFlo
---
@Flo_Schneider Vielen Dank für den Link. Warum findet man denn diese Anleitung nicht auf der Viessmann Homepage zum downloaden oder bin ich blind?  Auf jeden Fall steht da dass der Zähler nur phasensaldierend ist. Leider steht da jetzt nicht wie er den kwH Verbrauch anzeigt.Kleines Beispiel. Auf L1 werden 2kw und auf L2 werden 1,5kw verbraucht. Das ergibt ja in Summer 3,5kw Verbrauch. Auf L3 werden gerade 4,25kw eingespeist.  Wie zählen jetzt die beiden In und Out-Zähler hoch. Wird jetzt der Import um 3,5kw erhöht und der Export gleichzeitig auch um 4,25kw oder zählt nur der Export richtigerweise um 2kw+1,5kw-4,25kw=0,75kw hoch und der Import ändert sich nicht?
---
In deinem Beispiel wäre es dann so, dass der Zähler 0,75kW Einspeisung zählt. 
 
Viele GrüßeFlo
---
@Flo_Schneider okay, wenn das so ist dann ist es ja gut. Dann kann ich mir ja wirklich den zweiten Zweirichtungszähler für die Kaskade sparen. Wenn du mir jetzt vielleicht noch sagen kannst was der zweite Viessmann Zähler visualisiert? Was sieht man dann und wo? Gibts da irgendwo ein paar Bilder davon.
---
Auf der Seit der 250-A auf unserer Homepage findest du beim Abschnitt "Mit der ViCare App alles im Blick" einen Screenshot zum Energiecockpit. 
 
https://www.viessmann.de/de/produkte/waermepumpe/vitocal-250-a.html
 
Viele GrüßeFlo
---
Hallo an Alle,bin neu hier (habe eine Vitocal 250 bestellt) und dachte ebenfalls dass diese irgendwie Smart ist .. die hier diskutierte Lösung mit drei/ vier Messgeräten ist mehr als lächerlich und alles andere als nachhaltig  - was eine Ressourcenverschwendung ... Was ich nicht verstehe: für fast jedes Unternehmen/ Produkt stehen heute Plugins für Systeme wie HomeAssist, OpenHab, ... zur Verfügung. Warum bietet Viessmann sowas nicht an (oder versteckt sich das hinter dem vitotronic binding  - kann es leider nicht testen da die WP noch nicht geliefert wurde)? Dann könnte ich meine SonnenBatterie, meinen SolarEdge Wechselrichter, ... mit der Wärmepumpe koppeln und brauche keine extra Meter für an die 800€ für die mir im Zählerschrank eh der Platz fehlt? Dann ist auch das Thema mit unterschiedlichen Protokollen usw durch ... Und es ist ja nicht so, als ginge es hier um eine billig WP aus Fernost - sondern eine Anlage die bei uns fast 40.000€ kosten wird (und dann keine Updates OTA *kopfschüttel* - wir sollten alle mehrmals pro Woche bei den Installateuren anrufen und nach Updates fragen  - die sind irgendwann so genervt, dass sie das bei Viessmann deutlich zum Ausdruck bringen werden) ... Hallo Viessmann  - wir haben 2023.  Wie schon mein Namensvetter geschrieben hat  - hier geht es darum eine Insellösung zu etablieren damit die Kunden gezwungen sind im Viessmann Kosmos möglichst viel Geld zu lassen. Geht aber nicht, wenn man bereits seit vielen Jahren ein heterogenes Smart Home aufgebaut hat (ich hatte auch für viele Jahre fhem  - bin dann aber auf eine CCU3 umgestiegen, weil es ein echter Zeitfresser war *lach*) Just my two cents  Sascha
---
@Sascha_82 Dem kann ich dir nur zustimmen. Mit unserem Heizungsaustausch im Sommer sind wir sogar über 40000 Euro. Letzte Woche wurde bei mir jetzt mal der uralt Zählerschrank gewechselt. Hab gedacht, machste gleich nen Nummer grösser rein. Wer weiß was noch kommt. 1400x1100mm, also 5-feldrig. Feld 1 für Wohnung EG, Feld 2 für uns, Feld 3 und Feld 4 sind für Kaskadenzähler und TRE Feld vorgesehen und Feld 5 Verteilerfeld mit APZ unten. Pustekuchen. Wenn ich da jetzt noch 2 dieser Viessmann Zähler benötige ist das 5-reihige Verteilerfeld jetzt schon zu klein. Ins obere Anschlussfeld dürfen die Zähler ja nicht rein. Also muss alles nach rechts. Völlig bescheuert, und absolut nicht nachvollziehbar.
---
@Sascha_69 Wenn Du die 250-A noch nicht geliefert und verbaut wurde, und Du die 70°C VL Temperatur nicht benötigst, würde ich mir an Deiner Stelle überlegen, anstelle der 250-A eine WP aus der 200-A Serie einbauen zu lassen……diese ist von der Software her komplett offen, Du kannst alles selber anpassen/optimieren, und lässt sich über eine KNX Schnittstelle Tadellos an die restliche Haustechnik anbinden……Mir käme eine 250-A genau wegen der neuen Softwarestrategie vom VM niemals ins Haus, solange VM hier nicht einlenkt…… lgGuennie
---
.......eigentlich ist das Ganze ja sehr einfach: In Zeiten des Internet, und der ganzen Sozialen Netzwerke, ist es für jeden interessierten, mündigen Anlagenbetreiber sehr einfach, wenn er vor hat sein Heizungssystem auf WP und entsprechende smarte Einbindung umzustellen, das man sich vorher erkundigt welche WP Hersteller welche Systeme haben, und was man damit wirklich machen kann, und was eben nicht....und man braucht sich somit auch nicht mehr von den Hochglanz-Prospektversprechen der Hersteller "blenden" lassen, bis es dann "zu spät" ist....... Jene zukünftigen Anlagenbetreiber, die Wert darauf legen, das sie selber einen ordentlichen Zugang zu den Parametern haben möchten, und das System auch ordentlich in die bestehende Haustechnik einbinden möchten, werden dann schlicht und einfach solche Systeme die das nicht entsprechend bieten, einfach nicht kaufen. Sind es sehr viele, die solche Systeme nicht kaufen, bekommen als erstes die HB das Problem, das sie bestimmte WP-Systeme nicht mehr an den Kunden bringt.....somit wird er genau diese Systeme nicht mehr in seinem Sortiment anbieten........im Anschluss bekommt zb. der VM Vertrieb das Problem, das ihm seine Kunden - die HBs die Anlagen nicht mehr abkaufen.....Da derzeit der WP-Markt auf Grund der ganzen Energiethematik in rasantem Tempo unterwegs ist, kann es sehr schnell gehen, das es viele HB-Kunden sind, die hier der VM-Vertrieb durch diese neue Strategie verliert, was glaubst wie lange es dann dauert, bis entweder VM seine Strategie ändert, oder eben auf seinen neuen WP-Systemen "sitzen bleibt".....das sind Entscheidungen für sehr lange, denn Kunden die jetzt dadurch VM verliert, hat VM für die nächsten 15-20 Jahre  - wenn nicht sogar für immer - verloren....und es gibt mittlerweile durchaus andere WP-Hersteller, die das ganze Thema erkannt haben, und im Grundpaket schon entsprechende Datenanbindungen, und Zugriffsmöglichkeiten (zb. über Modbus TCP) integriert haben.....und die Anlagenbetreiber werden immer mehr, denen entweder aus Überzeugung, oder aus Energiekostengründen wichtig ist, genau solche Möglichkeiten zu haben, wie zb. selber die Anlage an die individuelle Umgebung anpassen zu können. Somit:letztendlich hat es der mündige Kunde (zukünftige Anlagenbetreiber) in der Hand was die Systeme in Zukunft bieten, und was nicht.....Sind es überwiegend mehr Kunden, die eine entsprechende Integrationsmöglichkeit / Zugangsmöglichkeit wünschen und fordern, werden sich solche Systeme wie die 250-A sich nicht lange am Markt halten.....ist es jedoch der Mehrheit der Kunden egal, ob sie diese Möglichkeiten haben, oder ob sie irgendwann 5 Smartmeter im Verteilerschrank haben, die letztendlich alle das gleiche machen, dann wird die 250-A am Markt bestehen. lgGuennie
---
Ich habe vor meiner Krankheit mit der Industrie zusammen gearbeitet - das nannte sich Industrie 4.0, wo man sich auf gemeinsame Standards nicht nur auf der Physik sondern auch (fast) bei der Semantik geeinigt hat. Das auf Basis OPCUA - auch mit Pub/Sub und MQTT.Das läutet das Ende der kleinen Inseln der alleinigen Glückseligkeit (des Vertriebes) ein …
					
				
			
			
				
	LG JörgHaus Baujahr 1995, Heizkörper, VC 250-A AWO-E-AC 251.16Defekt seit Februar 2022 - Reparatur geplant Oktober 2023
---
.....leider ist das in der Haustechnik noch nicht "angekommen".....da ist noch immer komplett "Wilder Westen" was das betrifft......die einen setzen auf Modbus TCP....super Ansatz....funktioniert super.......andere wieder haben eeBus als Schnittstelle......diese "Normschnittstelle" als ordentlich Datenanbindung zu verwenden....naja....bis das sauber läuft.....ist eine eigene Geschichte........und dann noch KNX......funktioniert sehr gut.....aber auch sehr teuer.......und VM.......hat CAN-Bus "on Board", den man aber nicht "anzapfen" kann, sondern bei der neuen 250er Serie heißt es zb. für den TCP oder KNX Umsetzer von Wago, saftig Euros auf den Tisch des Hauses zu legen...... Das Ganze soll dann auch noch sauber mit unterschiedlichsten PV-Systemen kommunizieren.......auch weit gefehlt.......das bedeutet derzeit noch alles individuell Maßschneidern programmieren, u.s.w.Und um das Thema "Smart Grid" bewerben zu können bieten die Heizungshersteller gerade mal einen Ein/Aus Schaltkontakt an.......ein einziger Witz das Ganze in der Zeit der heutigen technischen Möglichkeiten..... Das schlimme daran, die Heizungs-Hersteller wollen alle von dem ganzen nicht wirklich etwas wissen. Jeder will am liebsten seine eigene "Insel", um ja nicht "austauschbar" zu sein....Nachhaltigkeit, u.s.w. alles sch....Egal......Hauptsache der Umsatz wird maximiert... hier ist eigentlich der Gesetzgeber gefordert, damit alleine schon aus Gründen der Nachhaltigkeit, diesem Wildwuchs ein Riegel vorgeschoben wird..... lgGuennie
---
Das würde ich so unterschreiben.
					
				
			
			
				
	LG JörgHaus Baujahr 1995, Heizkörper, VC 250-A AWO-E-AC 251.16Defekt seit Februar 2022 - Reparatur geplant Oktober 2023
---
@Guennie Da geb ich dir ja recht mit dem vorher informieren. Aber bin ich vielleicht Heizungsbauer? Ich hab von Heizungstechnik keine Ahnung und Millionen andere auch nicht. Dafür gibts ja Spezialisten die das gelernt haben. Und ich will auch nicht wochenlang die verschiedensten Foren durchsuchen müssen. Wenn mir der HB sagt das eine Kopplung der PV mit der WP möglich ist dann muss ich davon ausgehen dass das geht. Gut, es geht ja mit Smart Grid.
---
Ich habe auch den Fehler gemacht und mich vorher nicht mit SG Ready beschäftigt. So wäre mir dessen binäres Verhalten schon eher aufgefallen.Es scheint so, dass man einer VM Wärmepumpe nicht sagen kann: Hier hast du mal 3,2 kw - kümmere dich im Rahmen meiner Vorgaben. „… man braucht ein Energiemessgerät …“ - cool, habe ich. Aber von Viessmann - 😤
					
				
			
			
				
	LG JörgHaus Baujahr 1995, Heizkörper, VC 250-A AWO-E-AC 251.16Defekt seit Februar 2022 - Reparatur geplant Oktober 2023
---
Naja, anscheinend ja nicht nur eines sondern 2 davon
---
@Kruemel64 Du hast sicher vom "Idealzustand" her vollkommen recht, und es sollte auch so sein, nur die Realität sieht hier leider vollkommen anders aus: Die Spezialisten die das ganze "gelernt" haben, werden immer wenigerDie HB wollen am liebsten das verkaufen was sie kennen.......Weiterentwicklung, sich an die neue Zeit, bzw. Technik anzupassen (wollen)......weit gefehltWenn Du Dich somit darauf "blind" verlässt, bzw. daran glaubst, das der HB Dir genau das einbaut, was für Dich das beste ist......dann kannst genauso an den Osterhasen glauben......Der HB verkauft Dir letztendlich das was für ihn das beste ist, aber sicher nicht das was für Dich das beste ist....... Bei uns in Ö etabliert sich mittlerweile ein Business, das sich genau diesem Problem annimmt. Es gibt die ersten Firmen die genau das (Hersteller und HB Neutral) anbieten: Den normalen "Häuselbauer" genau davor zu "Schützen" (technische Beratung Vorort, Analyse der Bestandsanlage, Angebotsüberprüfung u.s.w.). So das er letztendlich genau das bekommt, was er auch wirklich benötigt, und nicht das was für den HB am bequemsten ist.......somit als neutraler "Dienstleister für den Häuselbauer" der sich selber nicht mit der ganzen Thematik auseinandersetzen kann, oder möchte. lgGuennie
---
Hallo Guennie,leider Bestandsimmobilie ohne Fußbodenheizung - wir brauchen daher wohl eine höhere Vorlauftemperatur. Ich muss allerdings sagen "hätte ich mich vorher mehr informiert" - ich hätte NIE gedacht, dass Viessmann im Hinblick auf Nachhaltigkeit (unnötige zusätzliche Meter, keine sinnvoll umsetzbare holistische PV - WP Lösung, ...) so rückständig ist. Und dieses Ankündigen von Features die irgendwann mal irgendwie unter Umständen kommen sollen - irgendwie erinnert mich das nach Politikersprech ... hab jetzt mal nachgesehen, was es sonst noch so gibt - die aroTherm von Vaillant sieht auf den ersten Blick gut aus - muss da aber nochmal genauer nachsehen ob diese WP gut in bestehende Hausautomatisationen eingebunden werden kann ...
---
Noch etwas zu deiner Vorstellung "HB-Fachfirmen": ein Arbeitskollege von mir hat mich mal vor längerem gefragt, auf was er bei den HB aufpassen muss, wenn diese bei ihm wegen dem Umbau von Gas auf WP Heizung zur Angebotslegung auftauchen...... Er hat sich dann zur Sicherheit - mit den Infos, die er von mir erhalten hatte, 5 HBs eingeladen, sich die Anlage anzusehen, und ein Angebot für den Umbau zu legen. Ergebnis:Bei 2 HBs hat er das Ganze nach einer halben Stunde abgebrochen, als er gemerkt hatte, die hatten nicht die geringste Ahnung von Wärmepumpen, und wie die vorgegangen währen.....dann hats ihm gereicht...... Bei weiteren 2 war das Ganze eher "Durchwachsen", aber hier hätte es  - mit entsprechendem persönlichen Nachdruck - etwas werden können..... Bei einem einzigen, hat man von Anfang an gemerkt - der versteht sein Handwerk wirklich, hat mehrere Möglichkeiten (inkl. der jeweiligen Vorteile und Nachteile) erklärt. Hat sich die Bestandsanlage Vorort genau angesehen, entsprechende vorhanden Unterlagen verlangt, Fragen bezüglich Zukunftsvorhanben (eventuell PV Montage, Dämmvorhaben, u.s.w.) gestellt, Vorort mit diesen Unterlagen schon mal drüber gerechnet, und erklärt, welche Anlage passen würde, und welche, warum nicht, u.s.w. Einfach so, wie man sich das eben, für einen Standard-Häuselbauer vorstellt.......leider wie gesagt, war es letztendlich - nur einer von fünf......... lgGuennie
---
@Kruemel64  schrieb:Gut, es geht ja mit Smart Grid. Smart-Grid ist doch eine völlig museumsreife Krücke, warum das heutzutage immer noch existiert ist schon ein armseliges Zeugnis einer völligen Fehlentwicklung am Markt. Traurig ist, wenn Schnittstellen existieren (wie z.B. die CAN Schnittstelle), aber nicht genutzt werden können, weil sich der Hersteller noch ein paar Euro davon verspricht, indem er versucht das "geheim" zu halten bzw. weitere Software/Hardware dafür obligatorisch macht.Es müsste ja nicht einmal ein branchenweiter Standard sein. Wenn jeder Hersteller seine Schnittstelle offenlegen würde, könnten auch Drittanbieter von Smart-Home-Lösungen die Anlagen vernünftig integrieren.Aber das ist wohl auch nicht gewünscht.
---
Selbst auf die Gefahr hin, das es eigentlich nicht sein sollte, hier bestimmte Hersteller nennen zu müssen, aber anscheinend geht es leider nicht anders.......... Bei Vaillant kann ich Dir auch gleich etwas mitgeben: die haben zur Datenanbindung eeBus.....das Ganze ordentlch darüber anzubinden, so wie man sich das auch vorstellt....echt fraglich.....bei Ochsner das gleiche Dilemma....eeBus......es gibt aber auch positiv-Beispiele: ein Arbeitskollege hat eine Solarfocus, die hat sich problemlos über Modbus TCP einbinden lassen........  lgGuennie
---
Hallo zusammen, ich würde gerne wissen, wie ich eine VITOCAL 250-A Wärmepumpe am besten mit einer PV Anlage kopple, um den Eigenverbrauch des PV Stroms möglichst zu maximieren. Die Wärmepumpe verfügt ja über einen Inverter/Frequenzumrichter, wodurch diese theoretisch stufenlos regelbar ist.Mein Smart-Home verfügt über einen Stromzähler direkt im Zählerschrank, sodass ich jederzeit weiß, wie viel Überschuss an PV Strom ins öffentliche Netz eingespeist wird. Ich möchte nicht die einfachen "Smart-Grid-Funktionen" nutzen, da mir dort lediglich Schaltkontakte zur Verfügung stehen, und ich die Wärmepumpe so nicht stufenlos regeln könnte. Am liebsten würde ich mithilfe einer Schnittstelle/ einem Protokoll wie Modbus, meinen Überschuss an PV Strom von meinem Gebäudeleitsystem an die Wärmepumpe melden, sodass diese dann entsprechend stufenlos mit dieser Leistung arbeitet. Ist dies möglich und wenn ja, wie?Gibt es eine Schnittstellenbeschreibung oder ähnliches? Vielen Dank im Voraus @Flo_Schneider Sie konnten teilweise bei ähnlichen Fragen weiterhelfen. Evtl. wissen Sie auch hier Bescheid.
---
@Guennie Ich habe auch 7 HB hier im Umkreis angefragt. 3 haben sich überhaupt nicht zurückgemeldet, weder auf Anruf, AB oder Mail. 4 waren hier. Der Buderus Mensch war zu zweit hier, der HB und einer von Buderus direkt. Die haben schon alles genau nachgefragt und alles auch aufgenommen. Auf ein Angebot warte ich aber seit August trotz Nachfrage bis heute noch. Beim nächsten genau dasselbe, der hätte auch ne Viessmann eingebaut. Der war auch über ne Stunde hier und hat alles genau aufgenommen und angeschaut. Angebpt bis heute keines erhalten. Von 2 habe ich ein Angebot erhalten, wobei mir der 2. Viessmann HB am kompetentesten und sympathischsten vorgekommen ist. Ich denke mal dass der auch nicht schlecht ist. Seine Mitarbeiter werden regelmässig auf Schulung geschickt und wenn WP mal defekt wäre  reparieren die das, und der Viessmann Kundendienst Monteur wäre auch direkt nebenan bei ihm.
---
@Guennie Bei uns war es ähnlich - wir haben einen HB genommen der bereits bei Bekannten eine WP installiert hat und die waren zufrieden - leider konnte ich mich nicht so tief in die Thematik einarbeiten da wir gleichzeitig eine PV Anlage mit 29,7kw peak, Insellösung und 22kwh Batteriespeicher bekommen haben - und da hatten die Anbieter die zu uns kamen leider auch nur wenig Ahnung sodass ich mich als Kaufmann ins Thema einarbeiten mussten... Ich muss gestehen: Zur Vitocal kam ich, weil der HB eine Stiebel Eltron angeboten hatte die aber als Kältemittel R410a hatte welches ab 2025 verboten ist. Er hat dann zwar mit "Bestandsschutz" argumentiert - ich habe ihn dann aber mal aufgefordert mit seinem alten Diesel nach Stuttgart reinzufahren - so viel zu Bestandsschutz .... Man hat halt leider nicht die Zeit sich da in jedes Thema in die Tiefe einzuarbeiten - deshalb kauft man ja einen namhaften Anbieter wie Viessmann - um das Risiko zu minimieren - und dann kommt so ein Mist... Ich frage mich da, wie der VM Vertrieb/ die GF tickt - denken die wirklich, dass ich meine HomeMatic Ventile usw gegen VM Ventile uä tausche, mir vier bis fünf Meter installiere, regelmäßig beim HB nachfrage ob es Updates für meine WP gibt - und falls ja Anfahrt + Stundensatz bezahle???? Leider morgen viel zu tun - aber dannach muss ich mich tiefer einarbeiten und uU bei Viessmann stornieren - muss ich dann nur meinen Bekannten sagen die mich gefragt haben, was ich bestellt habe - nicht dass ich mir da Feinde mache *lach* Sascha69
---
@Guennie Weishaupt kann ebenfalls Modbus TCP - aber leider auch mit R410a unterwegs weshalb das keine Alternative für mich ist. Und bei Solarfocus gibt es nur Luftwärmepumpe - soweit ich das verstanden habe sind die weniger effizient - oder? mir ist wichtig im Winter weder im kalten noch im dunkeln zu sitzen - daher die umfangreichen Investitionen ...
---
Mein Chef sagte mal: Wir brauchen dringend einen Salesmen to Code generator. Ich hätte nicht gedacht, dass es in solch konservativen Zweigen wie Heiztechnik ähnlich ist …
					
				
			
			
				
	LG JörgHaus Baujahr 1995, Heizkörper, VC 250-A AWO-E-AC 251.16Defekt seit Februar 2022 - Reparatur geplant Oktober 2023
---
Das mit dem R410A, und mit dem Bestandsschutz ist das so eine eigene "Sache"....aber dem Hausbesitzer plötzlich sagen er darf seine bestehende WP mit R410A plötzlich nicht mehr betreiben....doch etwas weit hergeholt, aber keiner kann wirklich heute sagen, was der Politik morgen noch so alles Sinnbefreites einfällt, da hast schon recht.... Egal was man macht....letztendlich hat alles sowieso seine eigenen vor und Nachteile - Beispiele:R410A....(Gemisch von R32 und R125 )......Umweltschutz....solange nichts davon in die Umwelt gelangt......kein Problem......R290 (Propan).....hier hast das Thema wegen Explosionsschutz......darf nicht überall aufgestellt werden....... was hier noch alles so auf den Markt kommt wird sich noch zeigen........also....egal auf was man aktuell setzt.....eine Garantie was die Zukunft bringt, hat man sowieso nie....... lgGuennie
---
@Guennie und @JörgWende Als Vertriebsprofi denke ich gerade darüber nach ob es sinnvoll sein könnte ein Start-Up hochzuziehen welches in SEA WP herstellen lässt welche unsere Anforderungen erfüllt, direkt mit APIs kommt die mit allen gängigen Systemen zusammenarbeiten und damit dann den Markt zu überrollen *lach* Kenne da eine VCs welche speziell in der Seed Phase Mittel zur Verfügung stellen ....
---
zum Thema Luftwärmepumpen, habe ist mittlerweile eine eigene "Einstellung" bekommen - diese sind von der Technik mittlerweile so gut, das man sich das schon überlegen sollte.....: Wenn eine LWP ordentlich geplant und eingerichtet ist, sind hier mit einer FBH durchaus JAZ zwischen 3,5 und 4 zu erreichen......hat man (zusätzlich) Radiatoren, schafft man irgendwo zwischen 3,2 und 3,5..... Stellt man jetzt eine Sole WP oder Tiefenbohrung dagegen, hat die logischerweise eine höhere JAZ....nur.....dann rechne mal nach, wann sich im privaten Hausbau die notwendigen Mehrkosten, der Tiefenbohrung, oder der Flächenkollektoren, durch die höhere JAZ refinanziert haben....irgendwo zwischen "nie" bis "überhaupt nie"... Wenn man die ganzen Euros anstelle in die Tiefenbohrung oder die Flächenkollektoren, in eine PV mit Speicher investiert, ist das meiner Meinung nach mit ziemlicher Sicherheit langfristig günstiger, und hat zusätzlich zur Hausbeheizung das ganze Jahr den Hausstrom gleich mit abgedeckt.....Erdwärme kannst im Sommer dagegen überhaupt nicht viel nutzen......außer zur Beheizung des Pools...... .....kommt aber letztendlich auf die individuelle Situation drauf an.......eine objektive RoI Rechnung über die komplette Laufzeit schadet hier jedenfalls nicht...... lgGuennie
---
Das wäre auch eine Option - LWP + Elektroheizung für das WarmwasserDann hätte man auch eine Klimaanlage für den Sommer
					
				
			
			
				
	LG JörgHaus Baujahr 1995, Heizkörper, VC 250-A AWO-E-AC 251.16Defekt seit Februar 2022 - Reparatur geplant Oktober 2023
---
@Guennie von ROI Berechnungen habe ich mich seit langem verabschiedet - zu viele Variablen mit zu viel Varianz *lach* - ich habe nur einen Return "im Winter warm und hell sitzen". und im Idealfall ein holistisches System haben welches ich so einrichten kann, dass es sich selbst optimal steuert ... Aber wer weiss  -vielleicht bekommt ja VM irgendwann mal mit gescheiter Smart Home Anbindung hin ... oder jemand macht sich die Arbeit zB ein Openhab Binding für die VitoCal zu erstellen .... Sascha69
---
....du wirst jetzt lachen.....vor nicht mal einem Monat war der GF eines Startups (Gruppe aus professionellen Programmieren und Elektrotechnikern) bei mir zu Hause, die sich genau mit dieser Thematik beschäftigen.....der wollte sich das mal ansehen, was ich hier bis jetzt wie gelöst habe......das interessante daran.......deren Ideen, wie sie diese Themen professionell lösen wollen decken sich von den Ansätzen her fast zur Gänze mit dem, was ich hier bei mir Hobbymäßig die letzten 3 Jahre aufgebaut / Entwickelt habe....... Die wollen das so angehen, das ein kleiner "Man in the Middle" erstmal in Form eines Raspberry Pi mit all diesen unterschiedlichen Geräte über deren Schnittstellen "sprechen" kann, und sozusagen als "Dolmetscher" allen vorhandenen Geräte (PV, Regler, WPs, Smartmeter, Batterie WR, Wallboxen etc....) dient, und bei Bedarf auch jedm jeweiligen Gerät die notwendigen Daten zur Verfügung stellen kann.... Beispiele daraus:ein einziger vorhandener Smartmeter, der mit dem "Man in de Middle" im Sunspec - Standard "spricht". Dieser stellt die Werte dann allen Geräten in deren jeweiligen individuellen Sprache und Schnittstelle zur Verfügung....... Der "Man in the Middle" kann auch so programmiert werden, damit dort bestimmte Aktionen bei anderen Geräten ausgelöst werden können....zb. soll ein bestimmter PV Überschuss eher in die Batterie ins WW in den Estrich, oder ins Netz gehen.... Bin echt schon gespannt, was die letztendlich hier auf die Beine stellen....ist noch sehr am Anfang das Ganze......bisher habe ich hier nur erfahren, das diesbezüglich viele Gerätehersteller die davon "wind" bekommen haben, das aktuell überhaupt nicht "witzig" finden...warum wohl.......😉 lgGuennie
---
Da hätte ich fast Lust mitzuarbeiten 😎🤷🏻‍♂️ du nicht?
					
				
			
			
				
	LG JörgHaus Baujahr 1995, Heizkörper, VC 250-A AWO-E-AC 251.16Defekt seit Februar 2022 - Reparatur geplant Oktober 2023
---
@JörgWende @Guennie  da wäre ich irgendwie auch dabei  - wobei das neue ja nur darin bestehen kann bestehende Systeme (HomeAssist, openhab, fhem, ...) benutzerfreundlicher zu machen - ist ja alles im Prinzip schon vorhanden (bis auf die Anbindung von Viessmann *lach*) ... Sascha69
---
....was glaubst was die Idee des GF gewesen währe, als er das bei mir gesehen hat: "da stecken ja locker 2-3 Jahre Vorsprung drinnen.....ob ich mir nicht - rein zufällig - deren Truppe mal ansehen möchte....."......😊 das Dumme daran....ich bin dafür einfach schon zu alt, um noch einmal hier was komplett anderes als bisher zu machen.....die Pension ist bei mir nicht mehr sehr weit entfernt...Erfahrungen zu teilen ist das eine, mach ich auch gerne.....aber ein kompletter Umstieg ist ab einem bestimmten Alter nicht mehr wirklich interessant.... lgGuennie
---
Wohin sich die bewegen wollen, da ist das was ich hier geschrieben habe nur ein kleiner Teil davon.....die haben noch Ideen in diesem Umfeld, da sind echt super Ideen dabei.....die werde ich aber aus Rücksichtnahme auf dieses Startup hier nicht Posten.... lgGuennie
---
@Guennie lach - bei mir das gleiche - auch wenn die Pension noch etwa 14 Jahre entfernt ist - was komplett neues anzufangen ist auch nicht meins - eher im Sinne von "Beta Tester"  Sascha69 - der sich gerade mit einem elenden HM-LC-S1PBU-FM rumschlägt der sich ums verrecken nicht anlernen lässt
---
gibt es eigentlich diesbezüglich Neuigkeiten? Auf der ish wurde ja großspurig die Interkonnektivität beworben?
---
Hallo, ich habe noch nicht verstanden, warum ich zwei VM Energymeter (E380CA) benötige, um den Überschuss der PV zu ermitteln und ein entsprechendes Signal an die WP (in meinem Fall eine 250) zu senden. Laut Anleitung schließe ich doch auch nur einen Energymeter an die 6-polige Anschlussbuchse links in der WP an. Dient der 2. Energymeter nur der Visualisierung in der App und wenn ich das nicht unbedingt haben will brauche ich auch nur 1 Energymeter?
---
Brauchst Du auch nicht……..es genügt ein Energymeter. Der muss jedoch an der richtigen (elektrischen) Stelle eingebaut sein, und auch der Einhang/Ausgang des Energymeter dürfen nicht vertauscht sein.Siehe die beigepackte Anleitung wo bzw. wie dieser eingebaut werden muss…… lgGuennie
---
Hi, danke für die schnelle Antwort. Die richtige Stelle ist nicht in der PV-Leitung, sondern zwischen Hausanschluss und Lasten, richtig? Dort, wo auch der Überschuss ermittelt werden kann?VG
---
Genau.Der VM Energymeter kommt gleich nach dem Hausanschlusszähler, somit vor den ganzen Lasten, (außer der WP) und auch vor der PV.Zwischen Hausanschlusszähler und VM Energymeter kommt nur die WP (damit der VM Energymeter den WP Strom nicht mit mißt. Auf diese Weise speist die PV als erstes alle Lasten im Haus (das bekommt der Energymeter nicht mit).Erst der PV Überschuss läuft durch den Energymeter zum Hausanschlusszähler, bzw. ist keine PV Energie da läuft der Netzstrom durch den Energymeter in Richtung Hauslasten. Die WP kommuniziert mit dem Energymeter über eine Datenleitung, und bekommt so die Info, ob noch PV Überschuss - nach Versorgung der Hauslasten vorhanden ist, und wie hoch dieser Überschuss ist. lgGuennie
---
Ok, jetzt muss ich auch mal eine konkretere Frage stellen *lach*. Mein Szenario sieht wie folgt aus. Ich habe: eine PV Anlage mit 29,7 kw/h Peak mit SolarEdge Wechselrichtereine Sonnenbatterie mit 22kw als Insellösungzwei Teslas an einer Go-e WallboxEinen smarten Meter vom Netzbetreiber (WestNetz) Bislang ist das bei mir so geregelt: geht der Dachstrom in den aktuellen VerbrauchÜberschuss geht in die Batterie bis diese eine SoC über 95% erreicht. Sobald dieser SoC erreicht ist, wird der angeschlossene Tesla geladenLaden Tesla Steuerung erfolgt über evcc -> es wird immer nur der Überschussstrom zum Laden genutzt (i.e. evcc schaltet eigenständig von 1 auf 3-phasig um und passt zusätzlich dann die Ladestärke an)Ebenso erfolgt das Tesla Laden sobald der Überschuss größer als 9,9 kw ist (mit mehr Ladestrom kann die Batterie nicht geladen werden) Meine Idee ist jetzt als 5ten Punkt die Wärmepumpe aufzunehmen  - i.e. falls nach Verbrauch fürs Haus, WP Standard Betrieb, Laden der Batterie sowie der Teslas IMMER NOCH Strom übrig ist (i.e. eingespeist wird) dass dann dieser Überschussstrom zB zum stärkeren Aufheizen des Wasserspeichers genutzt wird (i.e. höhere Wassertemperatur um das Wasser als Energiespeicher zu nutzen). So  - wie viele Meter brauche ich jetzt??? Aktuell kenne ich folgende Werte aus der SonnenApp Den erzeugten Strom vom Dach Wie viel Strom ich aktuell verbrauche (Inkl des Verbrauchs für das Laden der Teslas)Wie voll die Batterie ist Normalerweise sollte ich maximal einen weiteren brauchen falls ich einen gesonderten WP Tarif buchen will. Was ist eure Meinung dazu? Sascha
---
Hi, danke für die Erklärung. Ich habe aber jetzt noch ein Fragezeichen beim "Ort" der Einbindung. Ich habe schon einen Modbus-Zähler von Solaredge, der Im- und Export zählt und diese Werte an den WR für eine Visualisierung in der SE-App liefert. Ich habe bei mir einen zweiten Zähler für den Wärmepumpentarif, aufgebaut ist die Verteilung nach Messkonzept C3 (Seite 9: https://www.stadtwerke-lippe-weser-service.de/de/Stromnetz1/Eigenerzeugung-Einspeisung/Eigenerzeugun... weiß nicht, ob das bei allen Netzbetreibern gleich heißt). Wenn ich dich richtig verstehe, muss das VM Energymeter dann zwischen dem Anschlusspunkt der WP (steuerbarer Verbraucher) und Z2 eingeschliffen werden? Hoffe, das sprengt jetzt nicht den Rahmen hier 🙂
---
Hallo, der Link zum "Messkonzept C3" funktioniert nicht. Am besten Du skizzierst mal auf wie das Ganze bei Dir aktuell aufgebaut ist (Blockschaltbild von Hauslasten / PV / WP / Hausanschluss u.s.w.). Dann sollte man sehr rasch erkennen können, wo der VM Energymeter reingeschliffen werden sollte.  lgGuennie
---
Habe ein Schaubild angehängt, in das ich das VM Energymeter dort eingezeichnet habe, wie ich deine Beschreibung verstanden habe. Korrekt? Hier noch mal der Link, falls von Interesse:https://www.stadtwerke-lippe-weser-service.de/de/Stromnetz1/Eigenerzeugung-Einspeisung/Eigenerzeugun...

---

## Thread #20: Can Bus Verbindungsfehler

**URL**: https://community.viessmann.de/t5/Waermepumpe-Hybridsysteme/Can-Bus-Verbindungsfehler/td-p/310073
**Posts**: 2

Guten Morgen liebe Community,  ich habe meine Vitoair FS mit meiner Vitocal 200S mittels Can-Bus verbunden, um die Vitoair mit dem 7“ Display steuern zu können. Beide Geräte geben mir nun Fehler 910 „Mehrere Führungsgeräte erkannt“ aus. Weiß jemand was ich falsch gemacht habe? Vielen Dank!
---
Hallo Raphael1,
 
hierzu unterhalten wir uns unter deinem anderen Beitrag hier. 
 
Viele GrüßeFlo

---

## Thread #21: ioBroker Datenpunkte vitocharge vx3

**URL**: https://community.viessmann.de/t5/The-Viessmann-API/IBroker-Datenpunkte-vitocharge-vx3/td-p/352327
**Posts**: 3

Moin, ich habe den adapter viessmannapi 2.1.1 imstalliert. Verbindung steht. Die vitocaldens  222-f wird erkannt und liefert Datenpunkte zum Brenner und zum Kompressor.  Die Vitocharge wird auch erkannt, liefert aber keine Daten der PV-Anlage. Es gibt keinen Objektunterordner für die Datenpunkte. Hat jemand einen Tipp für mich?
---
…geht mir genauso. Die solardaten sind soweit ich sehe nur über ein bezahltes Paket zu sehen 8€/Monat. Find ich für einen privat Anwender zu viel. Ich verstehe auch nicht, warum Heizungsdaten kostenlos abgefragt werden können, Solardaten aber nicht.
---
Moin, danke für den Hinweis. Ich habe jetzt die Preisliste gefunden. 7,98 Euro pro Monat für meine eigenen Datenpunkte finde ich ... . Da installiere ich ja lieber einen Lesekopf (hichi mit tasmota) und habe die Werte fast umsonst. Der optische Lesekopf kostet zwischen 25 und 30 Euro.Eigentlich brauche ich auch nur den Einspeisedatenpunkt, damit ich den als Trigger im Winter für eine Infrarotheizung per Wlansteckdose steuern kann. Schade das dieses nicht im Standard vorhanden ist oder in der gridbox EMS.

---

## Thread #22: Local connection to VitoConnect

**URL**: https://community.viessmann.de/t5/The-Viessmann-API/Local-connection-to-VitoConnect/td-p/307457
**Posts**: 3

Hi, I hope that I am in the right section of the forum, since it does not seem to have an English language option. As Viessmann API has rate limitations, is there any plans to let us connect to the VitoConnect device on our homes directly with a simple http request to get the necessary data? This would let us get the data for our devices without limitations and also would simply reduce the load on Viessmann API.
---
Hi @keremerkan, you are correct here and thanks for your question!
There are no plans for the Vitoconnect to support local connections. The API that is provided is solely cloud-based.
However I understand the request of having a local connection as well. There is a gateway module "Vitogate" that provides local connection through different possible protocols. Have a look at http://www.vitogate.info/
I hope this helps.
Regards,
Michael
---
I understand that when Vitogate is in use, VitoConnect cannot be used. So this would not be a feasible solution and also having another device to connect while VitoConnect is readily available would complicate things. I am pretty sure most people using Viessmann API are home users that only want to expose their heating system to HomeKit or those that would like to gather historical data to optimize their system. Viessmann API is unfortunately cumbersome and prone to errors and rate limits while doing this. While I understand that it is completely cloud based at the moment, I am pretty sure the device would be able to handle a simple local http query without any authentication, that would just serve a json result like the API. Hope you will consider this in a future update. This will decrease the load substantially on the API and let us use our devices much more efficiently.

---

## Thread #23: Optolink Switch Splitter Vitoconnect MQTT

**URL**: https://community.viessmann.de/t5/Konnektivitaet/Optolink-Switch-Splitter-Vitoconnect-MQTT-amp-TCP-IP/td-p/439982
**Posts**: 51

Moin ihr! 🙂 Optolink ist 'alt', aber noch in Benutzung (bei mir auch). Öfter gab es Anfragen zum Betrieb zu lokalen Zwecken aber trotzdem weiter das Vitoconnect für Viessmann Cloud/Vicare/Viguide/Vi.API/Garantieverlängerung zu benutzen. Dazu jetzt hier die benutzerfreundliche Lösung, natürlich wieder open-source und kostenlos: der OptolinkVs2-Switch Er verbindet euer Optolink Gerät auf total einfache Weise mit allem was das Herz begehrt.Home Automation Anbindung per MQTTW/LAN Anbindung per TCP/IP und einfachen Ascii + $HexParallelbetrieb des Vitoconnect und damit Vicare, Viguide, Viessmann API weiter nutzbar und Erhaltung der erweiterten GarantieKein Gehassel mit komplizierter Einrichtung und irgendwelchen kryptischen xml's. Einfach nen Raspi, ein paar Python Module draufkopiert, Optolinkadapter und bei Bedarf das Vitoconnect angesteckt, ggf. noch ein paar Anpassungen in der Settings_ini (COM Ports, IP Adressen, MQTT Passwort, Poll-Liste, ...) und los.  viel Spass damit & Grüsse!Phil 🖖  ps. minimalistischer Optolink-Adapter: mit Diode und Transistor als SMD passt es auch unter die Schiebeklappe 😉
---
gut dass ich das Ding zumindest selber brauchen kann. ausser den Beiden, für die ich's gebaut hab, schein ja sonst niemand Interesse dran zu haben 😎 Wahrscheinlich ist die Optolink-(Betreiber-)Generation so alt, dass da niemand was mit Hausautomatisierung am Hut hat oder alles schon fertig...
---
Aber im HT Forum sind noch Fragen offen.
---
@qwert089  oh besten Dank Michael! immer dieser Benachrichtigungs-Issue im Haustechnikdialog.... 😴
---
ich hab ein kleines Video gemacht - kurze Einführung in die vielfältigen Möglichkeiten und die Einfachheit der Benutzung des Optolink-Switch https://youtu.be/95WIPFBxMsc
---
Hallo @HerrP ,sie sind keineswegs der einzige. Schon vor mehreren Wochen hat mich @qwert089 in meinen thread auf die neue möglichkeit aufmerksam gemacht. Nur leider hatte ich noch keine Zeit es umzusetzen. Das werde ich ändern demnächst tun. Da ich Loxonebenutzer bin, werde ich versuchen, wenn es für dich OK ist, dann ein Plugin für den loxberry zu erzeugen.Liebe Grüße und vielen Dank für deine Arbeit.
---
immer gerne! 🙂 es lebe open source! 🖖 Es gibt inzwischen auch eine Version, die auch mit dem älteren KW Protokoll funktioniert (Schater in der settings_ini). Da ist allerdings die Start-up Sequenz mit Vitoconnect noch nicht getestet, der Rest ist schon im Einsatz. Wenn man irgendwas neues bastelt, wäre es vlt gut, gleich da drauf aufzusetzen, irgendwann kommt doch wieder jemand mit KW Protokoll...
---
Guten Tag HerrP,Ich versuche, Optolink-Switch mit meiner Wärmepumpenanlage Vitocal 300-G zu verwenden. Der Anschluss klappt gut. Mit serLog.py wird der Informationsaustausch zwischen Vitoconnect und Vitocal korrekt ausgelesen und protokolliert. optolinkvs2_switch.py gibt jedoch einen Fehler aus: List index out of range. Wenn ich die Polling disable dan bekomme ich keine Fehler.Die console output geht hierbei, also auch ein pdf mit die output von serlog.py. Können sie mich berichten wie ich dass lösen soll.Hertzlichen Grüss,Fransawaiting VS2...Broker granted the following QoS: 0VS detectedrx 06rx 41 05 00 41 00 F8 01 3Frx 41 0D 01 01 08 8E 08 AE 0B 55 00 AE 0B AE 0B 2Dlist index out of rangeexit closeclosing serViConreset protocolclosing serViDevcancel poll timerexiting TCP/IP clientdisconnect MQTT clientclosing vitolog
---
Moin Frans! ich denke du hast die poll_items List in der settings_ini.py angepasst? ich vermute, da ist ein syntaktischer Fehler reingerutscht, ein Komma zu viel oder zu wenig oder ein Indent Problem oder sowas. Könntest du die settings_ini.py mal hier hochladen?! du musst die Dateiendung ändern in .txt oder so.Und wenn Passwords drin sind, diese vorher löschen/ersetzen! Grüsse!Phil
---
Hallo Phil,Weil ich noch nicht genau weiss welche Items für meine Anlage geeignet sind, habe ich nur die Anlagezeit und Aussentemperatur in meine Poll-liste.Files mit txt endung kan ich auch nicht hochladen, nur pdf, jpg, jpeg, png, gif, bmp, wbmp, mp4, mov. sind gültige Datatypen.Ist es vielleicht bequemer diese Discussion fort zu setzen in Github?
---
> Ist es vielleicht bequemer diese Discussion fort zu setzen in Github?ja, das sollten wir tun! machst du bitte eine Discussion oder ein Issue auf!? In der settings_ini kann ich so erstmal nix Fehlerhaftes erkennen, es kann aber sein, dass was mit Indent in der Leerzeile ist oder so. Lade bitte die settings_ini auf github noch mal als Text File hoch. und versuch mal    ("Anlagenzeit", 0x088E, 8, 'vdatetime'),zu ersetzen durch    ("Anlagenzeit", 0x088E, 8, 'raw'), damit wir den vdatetime 'Codec' schon mal ausschliessen können. Wir können auch auf Englisch weiter schreiben (auf github), wenn das bequemer für dich ist.
---
ich habe es schon gesehen... deine Anlage überträgt die Zeit anders als die Vitodens: rx 41 0D 01 01 08 8E 08 AE 0B 55 00 AE 0B AE 0B 2D 41 0D : STX, 13 Bytes Payload    01 01 : Antwort auf virtual read request        08 8E : DP Adresse           08 : 8 bytes dataAE 0B 55 00 AE 0B AE 0B : das ist ein anderes Format. Der 'Index out of Range' kommt bei      weekdays = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']    wkd = weekdays[int(data[4]) - 1]     data[4] ist AE, weekdays[0xAD] gibt es nicht...
---
Stimmt, ich habe die Analagezeit entfernt und jetzt lauft er mit nur die Aussentemperatur. Ich soll aber die ganze Datenpunktenliste neu machen. Der Aussentemperatu gibt immer 0, so ist auch nicht richtig codiert.Message 4 received on vitocal/AussenTemp at 1:56 PM:0QoS: 0 - Retain: false
---
Absolut geniale Lösung. Hab deinen Post gerade erst entdeckt, da ich nur noch wenig in der Community mache. Ich werde das nach dem Sommer ausprobieren und bei gegenseitiger Zuneigung (beider Konstrukte) mit meiner (noch) ViCare basierten Node-Red Anwendung verheiraten und darüber berichten.Danke nochmalChris
					
				
			
			
				
	https://www.rustimation.eu
---
Diese Software ist genau das, was ich brauchte. Ich hatte schon vor, es selbst zu machen, aber dies spart mir viele Stunden. Die Installation ist nicht schwierig, das einzige Problem ist, die Adressen der Parameter zu finden. Mit einer Abfrage in der Datenbank des Vitosoft-Programms konnte ich die meisten von ihnen finden. Im Home Assistant sieht es jetzt so aus. Es gibt noch ein kleines Problem mit dem Abgleich der HA Climate-Entität mit den Vitocal-Informationen.
---
Vielen lieben Dank für die postiven Rückmeldungen euch beiden! 'werden ja langsam doch ein paar mehr als die drei Nutzer (inkl. mir), für die ich das initial geschrieben hatte... 🙂 Über weitere Verbreitung freue ich mich natürlich. Schönen Blog hast du da @CaCicala , danke für die Erwähnung! Wenn du dein Projekt auf MQTT umstellst (sollte ja kein Problem sein), ist es nicht auf die alten Optolink Geräte beschränkt, sondern wir haben für die neuen ja open3e im Angebot. Das ist inzwischen einfach per pip install oder seit allerneuestem auch per Docker Container aufzusetzen, das sollten die Allermeisten hinbekommen. Grüsse! 🖖
---
Das Projekt sieht super aus👍 werde es die nächsten Tage mal Testen.Vorab schon mal eine Frage. Kann ich alle Parameter damit auslesen oder sind die Werte die über die Cloud z.B. nur über ein kostenpflichtiges Abo verfügbar verschlüsselt?
---
bezüglich der Viessmann Cloud verhält sich alles wie ohne den Splitter/Switch. Da reicht mein Projekt ja nur durch. Aber du kannst Daten, die in der V-Cloud oder API kostenpflichtig wären, lokal frei lesen und ggf. schreiben und dir damit auch deine eigene Cloud bauen (oder für MQTT Daten gibt es ja schon freie Cloud Lösungen). Es gibt gewisse Daten, wie bsw. der Energiekrempel bei den Wärmepumpen (vergl. hier), die nicht einfach per virtual_read/_write zugänglich sind, aber auch da lassen sich Wege finden, wie im wo1c_energy branch geschehen.
---
@HerrP >>Energiekrempel bei den Wärmepumpensicher? Vicare schafft das doch auch? Bei den Gas Geräten hat es zumindest jemand herausgefundenhttps://github.com/openv/openv/issues/171 hier auch was zu WPhttps://github.com/openv/openv/issues/480
---
hi @qwert089 ,ja, diese Datenpunkte kann man per virtual_read lesen. Dem timbrd ging es aber um die Energie-Historie, wie sie auch am Display angezeigt wird (die ist glaubich 'feingranularer' - per day...). Dazu mussten wir auf den Remote_Proc_Request Service zurückgreifen.Grüsse!
---
Bin auch interessiert. Liesse sich darüber ein Viessmann Vitovent (Lüftungsanlage) steuern?
---
moin @ceeage !gab es Vitovents mit Optolink? Falls du tatsächlich so eine hast, wäre es natürlich möglich - im Rahmen dessen, was man bei einer Vitovent überhaupt steuern kann. Ich meine gehört zu haben, dass die Möglichkeiten da ziemlich begrenzt sind.Also als erstes verifizieren, dass so eine Optolink Schnittstellevorhanden ist, und wenn es sie nicht gibt, dann open3e zum Steuern / Einbinden in eine HA benutzen 🙂Grüsse!Phil
---
Hi @Phil,nein ich möchte den Vitovent nicht direkt ansteuern. Das macht nämlich meine Vitocal. Mir ging es darum ob ich quasi über die Vitocal den Vitovent ansteuern kann?
---
Hallo @ceeage auf alles Fälle alles das was du über die App steuern kannst. zusätzlich kann man noch das alles abfragen. Die DP sollte man auch setzten können. Man muss nur die passenden Adressen herausfinden.
---
wo hast du die Liste her? die sieht ja interessant aus! die 7Dirgendwas scheinen ja schon die Adressen zu sein?!?
---
Moin ihr! 🙂 Optolink ist 'alt', aber noch in Benutzung (bei mir auch). Öfter gab es Anfragen zum Betrieb zu lokalen Zwecken aber trotzdem weiter das Vitoconnect für Viessmann Cloud/Vicare/Viguide/Vi.API/Garantieverlängerung zu benutzen. Dazu jetzt hier die benutzerfreundliche Lösung, natürlich wieder open-source und kostenlos: der OptolinkVs2-Switch Er verbindet euer Optolink Gerät auf total einfache Weise mit allem was das Herz begehrt.Home Automation Anbindung per MQTTW/LAN Anbindung per TCP/IP und einfachen Ascii + $HexParallelbetrieb des Vitoconnect und damit Vicare, Viguide, Viessmann API weiter nutzbar und Erhaltung der erweiterten GarantieKein Gehassel mit komplizierter Einrichtung und irgendwelchen kryptischen xml's. Einfach nen Raspi, ein paar Python Module draufkopiert, Optolinkadapter und bei Bedarf das Vitoconnect angesteckt, ggf. noch ein paar Anpassungen in der Settings_ini (COM Ports, IP Adressen, MQTT Passwort, Poll-Liste, ...) und los.  viel Spass damit & Grüsse!Phil 🖖  ps. minimalistischer Optolink-Adapter: mit Diode und Transistor als SMD passt es auch unter die Schiebeklappe 😉
---
@ceeage  wenn die Vitovent über die Vitocal gesteuert wird, sieht es mir aber ziemlich danach aus, als wäre das ein 'One Base' System? also was für open3e?! oder hat die Vitocal einen Optolink Anschluss?
---
@HerrP  creage  hat wohl eine alte 200-A da ist der Vitovent per Modbus an der WP angeschlossen und wird darüber bedient. Die DP sind aus dem Abnahme Protokoll einer 200-S VG
---
Mit die Vitosoft Software kann man ein Abnahme protocol darstellen dass alle relevante Datenpunkte für die Anlage enthält.
---
ja das scheinen gleich die Adressen zu sein.siehe auch https://github.com/openv/openv/wiki/Adressen-Ger%C3%A4te-VT-200-(WO1C)
---
na dann steht @ceeage 's Projekt ja nichts mehr im Weg 🙂 Bei weiteren Fragen ist hier offensichtlich bestens für Unterstüzung gesorgt 👍
---
Super interessantes Projekt. Das klingt genau nach dem was ich schon ewig suche.Die Einbindung der Anlage über die Viessmann Cloud API in Home Assistant ist so semigeil. Für den Schwiegervater bin ich aus "Komfortgründen" aber auf den Einsatz von Vitoconnect/App angewiesen.Sobald ich etwas Zeit finde, nehme ich mir das definitiv auch als neues Projekt vor 😉 Vielen Dank für die Arbeit!PS: Gibt es egtl irgendwo eine Datenbank mit den ganzen Adressen? Damit nicht jeder jedes Mal von vorne anfangen muss?PPS: Ließe sich so etwas egtl auf Basis von ESP Gräten umsetzen? Von denen habe ich noch ein paar hier herumliegen. Des Rasspi müsste ich mir erst zulegen.
---
Hallo, wegen der Adressen kannst du beim openv wiki nachschauen: hierhttps://github.com/openv/openv/wiki/Adressenoder in den issues suchen. VG
---
Mit die ESP Geräte geht das leider nicht da die keine USB Host unterstützten.
---
@CM000n  schön dass du das Projekt dann jetzt auch entdeckt hast! Wegen der Adressen ist hier https://github.com/philippoo66/ViessData21/blob/master/DP_Listen_2.zip noch eine sehr viel umfassendere 'Sammlung'. Das ist der 'Export' aus den Vitosoft xml's nach https://github.com/sarnau/InsideViessmannVitosoft . Um was für eine Anlage geht es denn? Es reicht locker ein Raspi 2, den bekommst du problemlos für 20eu auf Kleinanzeigen. Zugegeben immer noch etwas teurer als ein ESP, aber Frans sagte ja schon... Grüsse!Phil
---
>>keine USB Host unterstützten.  Wenn man sich einen   Optolink-Adapter selbst bastelt, dann ist der doch seriell. angeschlossen. Wäre das eine Option mit ESP  für CM000n?? VG
---
hm, stimmt. ich hatte das Vitoconnect im Kopf, aber das wird ja schon serial. wär auch ne gute Gelegenheit, mal die Volkszähleradapter mit angepasstem Diodenabstand auszuprobieren. Aber aktuell hab ich erstmal mit meiner PV zu tun... 😉 Ich kenn die CPU Last nicht wenn das Vitoconnect noch mitspielt, das sabbelt ja unaufhörlich vor sich hin. Wie leistungsfähig ist denn so ein ESP32? und man ist natürlich wieder auf WLAN....
---
Ich werd's mal mit nem Pi probieren. Wollte ich mir eh schon immer mal zulegen 😉
---
>> Um was für eine Anlage geht es denn? Es handelt sich dabei um eine Vitocrossal 300 in Verbindung mit einer Vitocell 300 und vier Vitosol 200 Modulen.
---
Es ist doch möglich USB Host mit ESP32. Die Unterstützung ist aber sehr basic. Die Optolink Switch auf ESP implementieren wäre eine ziemlich grosse Aufwand.  https://github.com/touchgadget/esp32-usb-host-demos.
---
wie gesagt - Volkszählerlesekopf wäre einen Versuch wert. Aber ich zitiere mal ChatGPT: Raspberry Pi 2CPU: Broadcom BCM2836Architektur: ARM Cortex-A7, 32-BitKerne: 4 (Quad-Core)Taktfrequenz: 900 MHzRAM: 1 GBESP32CPU: Tensilica Xtensa LX6Architektur: 32-BitKerne: 2 (Dual-Core)Taktfrequenz: bis zu 240 MHzRAM: 520 KB SRAM (integriert) + externe RAM-Optionen (bis zu 4 MB)Vergleich der CPU-LeistungRechenleistung:Der Raspberry Pi 2 hat eine höhere Rechenleistung aufgrund seiner Quad-Core-Architektur und der höheren Taktfrequenz (900 MHz vs. 240 MHz).Der ESP32 ist darauf ausgelegt, energieeffizient zu sein, daher ist die Leistung geringer, aber der Energieverbrauch ist deutlich niedriger.Multitasking:Der Raspberry Pi 2 kann aufgrund seiner vier Kerne und des größeren Speichers besseres Multitasking und komplexere Anwendungen bewältigen.Der ESP32 ist eher für Echtzeitanwendungen, IoT-Geräte und eingebettete Systeme geeignet, die keine umfangreichen Rechenressourcen benötigen.Einsatzbereich:Raspberry Pi 2: Geeignet für Anwendungen, die eine höhere Rechenleistung, eine vollständige Betriebssystemunterstützung (z.B. Linux) und mehr Speicher erfordern. Typische Anwendungen sind Home-Server, einfache Desktops oder Mediacenter.ESP32: Ideal für IoT-Anwendungen, Sensorik, Steuerungen und Anwendungen, bei denen geringer Stromverbrauch entscheidend ist.FazitDer Raspberry Pi 2 bietet deutlich mehr Rechenleistung und eignet sich für anspruchsvollere Aufgaben und Projekte, die mehr Speicher und Multitasking erfordern. So ein paar Threads laufen beim Splitter ja schon parallel. Wenn man einfach mal 240/900[MHz] * 2/4[Kerne] nimmt, sind das ~13,5% Rechenleistung. Wahrscheinlich wird auch das noch reichen, wahrscheinlich reicht auch der halbe Speicher, aber es bleibt erstmal die Einschränkung auf WLAN, und die Viessdata csv muss man woanders hin speichern (wenn man sie denn speichern will). Wenn ich irgendwann mal viel Langeweile haben sollte, werde ich das vielleicht mal angehen. So ein Ding läuft ja doch oft 24/365, da kann 1..2 Watt Unterschied Leistungsaufnahme schon was ausmachen, und so ein 5eu Ding wäre auch eleganter, statt einen 20eu Raspi sich langweilen zu lassen.... Bei mir läuft auf dem Raspi noch mehr, von daher keine Option, aber zumindest ein interessanter Gedanke...
---
>> eine Vitocrossal 300 in Verbindung mit einer Vitocell 300 und vier Vitosol 200 Modulen. die Vitocrossal bietet natürlich nur einen recht eingeschränkten 'Datenpunkteraum', aber das kennst du ja von Vicare...
---
Wegen der Adressen ist hier https://github.com/philippoo66/ViessData21/blob/master/DP_Listen_2.zip noch eine sehr viel umfassendere 'Sammlung'. Das ist der 'Export' aus den Vitosoft xml's nach https://github.com/sarnau/InsideViessmannVitosoft .Vielen Dank für die Links! Die .zip File mit den Adressen ist super! Wenn ich es richtig gesehen haben, wäre für meine Vitocrossal die DP_VScottHO1_72.txt file die richtige.Was ich jedoch noch nicht so ganz verstanden habe: In der settings_ini.py muss ich neben der eigentlichen Adresse auch angeben, auch die Länge, Typ/Skalierung und Signierung mit angeben.Wo bekomme ich diese Informationen her? Aus der .zip File mit den Adressen erschließt sich mir das erstmal nicht. Oder ist das ein wenig trial und error kombiniert mit Informationen von verschiedenen Stellen zusammenklauben? Beste grüße und nochmals vielen Dank!
---
um zu sagen welche DP_xxx.txt die passende ist, musst du Adresse F8 (am besten gleich 8 Bytes) auslesen. Da steht das sysDeviceIdent drin und damit kannst du mit der Devices.csv die passende Datei zuordnen. Wie das genau geht bzw was dabei zu beachten ist steht im ReadMe. zur ini - nehmen wir mal den Eintrag aus der Textdatei- Aussentemperatur (5373) [TiefpassTemperaturwert_ATS~0x5525 (SInt)]die 0x5525 ist die Datenpunktadresse.das "SInt" sagt dir zweierlei:"S" für signed, du solltest also signed auf True setzen, die obere Hälfte des 'Zahlenraumes' sind negative Werte."Int" heisst es sind 2 Bytes. Es gibt fast nur Int und Byte. Byte ist dann 1 Byte. Manchmal gibt es noch Int4, das sind dann 4 Bytes. Bei den Arrays (z.B. Schaltzeiten braucht man eh tieferes Wissen um die Interpretation. Mit etwas Glück steht die Länge des Arrays in der SQL Datenbank von Vitosoft.  Die Skalierung ist meist ziemich offensichtlich: Wenn du für die Aussentemperatur 234 Grad bekommst, ist die Skalierung 0.1. Es gibt kaum was anderes als 1 und 1/10. Bei der Brennerlaufzeit noch 1/3600 (Sekunden in Stunden). Aber meist ist es wenn dann nur ein Verschiebung des Kommas, bei Int4 auch schon mal 1/100. Tatsächlich ist es manchmal "ein wenig trial und error kombiniert mit Informationen von verschiedenen Stellen". Bsw. ist die Anlagenzeit meist 8 Bytes, die sind aber bei Gasgeräten anders kodiert als bei Wärmepumpen, aber die meisten Datenpunkte von Interesse sind ziemlich offensichtlich. Grüsse!
---
Super, vielen Dank für die ausführliche Antwort!Die VScottHO1_72 sollte die richtige sein. Wird zumindest schon so über die Viessmann Cloud API Home Assistant Integration angezeigt 😉Vor allem der Hinweis mit den Sint als Signed vs Int als Unsigned war seht hilfreich.
---
Hallo zusammen, ich schon wieder 😉Habe das ganze mittlerweile bei mir eingerichtet und es läuft bis jetzt tadellos.Es macht richtig Spaß, zu entdecken welche zusätzlichen Möglichkeiten und Werte gegenüber der App ausgelesen werden können. Und das wesentlich schneller und stabiler! Eine kleine Sache hat mich etwas verwirrt. Und zwar werden mit in der App bei den Brenner Betriebsstunden 41260h angezeigt. Lese ich die Daten jedoch mit dem Optolink Splitter aus, erhalte ich 32260h. Also exakt 9000h weniger. Hat zufällig noch jemand dieses Phänomen und kann mit erklären, wo sie fehlenden 9000h herkommen? Die Betriebsstunden im Optolink Switch lese ich über folgendes Poll Item aus:    ("brenner_betriebsstunden", 0x08A7, 2, 1, False), Ich habe bislang auch keine alternative Adresse für die Brenner Betriebsstunden gefunden. Es gibt lediglich noch eine Adresse für die Solar Betriebsstunden. Diese werden jedoch richtig und exakt gleich angezeigt, wie in der App.
---
Moin @CM000n ! Vielen Dank für das sehr positive Feedback! Mit den Brennerstunden ist ja erstmal die Frage, welcher Wert der richtige ist. Die werden doch auch irgendwo im Display angezeigt - hast du da schon mal nachgesehen? Mein Raspi ist wegen Umbauarbeiten grade offline, aber bei mir steht für die 300er    ("Betriebsstunden", 0x08A7, 4, 2.7777778e-4, False),  # 1/3600Hast du mal testweise probiert was dabei raukommt? Kannst du ja ganz einfach mit   read;0x08A7;4;2.7777778e-4als MPPT cmnd testen. Wenn nix hilft, müssen wir einen vitolog machen und schauen, was Viessmann da liest... 😉 Grüsse!
---
Mit 1/3600 als Skalierung erhalte ich dann einfach 8.9611 als Rückgabewert.Frage: Warum gibst du das relativ umständlich als eulersche Zahl und nicht einfach als Bruch an?("Betriebsstunden", 0x08A7, 4, 1/3600, False) funktioniert doch ebenfalls wunderbar 😉
---
oh, schau mal an! da ist Python mehr 'versatile' als ich dachte.und was sagt das Display von wegen Brennerlaufzeit?
---
Auf dem Display werden ebenfalls die 41260 Brenner Betriebsstunden angezeigt. FYI: Ich habe im Home Assistant Community Forum auch einmal einen Thread für mehr Home Assistant spezifische Fragen zum Optolink Splitter gestartet: Viessmann Optolink Splitter - Energy - Home Assistant Community (home-assistant.io)Ich konnte dort dazu bislang nichts finden und denke so ein tolles Projekt sollte man der Home Assistant Community nicht vorenthalten 😉
---
>> Auf dem Display werden ebenfalls...dann hilft nur der Vitolog und schauen, unter wasViessmann das ausliest >> Projekt sollte man der Home Assistant Community nicht vorenthalten supi, vielen Dank! ich guck mir das nachher mal an, grad weiss ich nicht 'wo mir der Kopf steht'...

---

## Thread #24: Direktzugriff VITOCONNECT 100 ohne Cloud

**URL**: https://community.viessmann.de/t5/Feedback-API/Direktzugriff-auf-Daten-per-VITOCONNECT-100-OPTO1-ohne-Cloud/td-p/247820
**Posts**: 13

Grüß Gott, ich habe eine LWP (Vitocal 222-A) welche per VITOCONNECT 100 OPTO1 die Daten in die Viessmann Cloud überträgt. Von dort hole ich mir die Daten über die API ab und verwende die Daten schlussendlich wieder lokal im Smart Home System.Jetzt wäre meine Idee, dass ich mein Smart Home System gerne direkt mit dem Vitoconnect 100 kommunizieren lassen möchte. Dies ergäbe für mich einige Vorteile:1) Unabhängig einer aktiven Internetverbindung2) Unabhängig von Viessmann Hardware/Services3) Unabhängig von API Änderungen (z.b. https://www.viessmann-community.com/t5/The-Viessmann-API/Datenpunkt-verschwunden/m-p/243822)4) Unabhängig von Verhaltensänderungen (https://www.viessmann-community.com/t5/The-Viessmann-API/Werte-der-API-ploetzlich-gerundet-geglaette...5) Höhere Datenqualität (siehe Changelog May 2022:  https://documentation.viessmann.com/static/changelog) Zudem würden damit auch die Viessmann Server entlastet werden, immerhin beruht der genannte Punkt 4 ja angeblich darauf, dass dadurch Datenmenge und Datenverkehr eingespart werden. Liebe Grüße,Bernhard Weingartner
					
				
			
			
				
			
			
				
	
			
				
					
						Gelöst!
					
					Gehe zu Lösung.
---
Nur um es festzuhalten: Es gibt eine Lösung, welche aber aus Kostengründen für dich nicht attraktiv ist. 
 
Der Direktzugriff auf die optische Schnittstelle oder der lokale Zugriff auf die Vitoconnect ist nicht vorgesehen.
---
Hallo Bernhard , direkt mit Vitoconnect 100 kannst du nicht kommunizieren ,oder zumindest ist das glaube ich noch niemandem gelungen. Du kannst nur das Optolink Kabel am Vitoconnect 100 abstecken und an deiner eigenen Hardware anstecken.Dann kannst du aber genau das machen was du möchtest. Leider hast du dann aber diese 5 Jahre Gewährleistung nicht mehr. VG Michael
---
Hallo,gibt es auch eine offizielle Sichtweise von Viessmann zu dem Thema?Immerhin wäre es ja auch im Interesse von Viessmann, da dadurch deren Infrastruktur entlastet wird.  Liebe Grüße,Bernhard Weingartner
---
Ein direkter Zugriff ist nicht vorgesehen, wie @quert089 bereits korrekt geschrieben hat. 
 
Wenn du lokal die Anlage steuern und Informationen auslesen möchtest kannst du entweder eine Fernbedienung anschließen oder ein Vitogate.
 
https://connectivity.viessmann.com/de-de/mp_rt/vitogate.html
---
Hallo, danke für die Antwort.Leider sind diese Gateways ja alle mit Mehrkosten von 800-1000€ verbunden. Ebenso ist danach noch eine Modbus bzw. KNX Anbindung seitens Smarthome notwendig. Dies würde die Kosten in meinem Fall (Loxone) nochmal steigern, von daher ist diese Lösung für mich nicht vernünftig. Ich dachte eher an eine einfache Software Lösung. Immerhin kann das Vitoconnect 100 ja mit Viessmann Servern kommunizieren, da wäre es doch ein leichtes, diese Schnittstelle offen zu legen, bzw. das Vitoconnect 100 auch mit anderen Servern/Anwendungen kommunizieren zu lassen, und zwar über LAN/WLAN. Lg,Bernhard
---
Okay, ich akzeptieren diese Lösung. Meine Begeisterung für die Firma Viessmann hält sich dadurch leider immer mehr in Grenzen. Ebenso wenn ich die Preise für die API Calls (Advanced Package) sehe, werde ich mir zukünftig gut überlegen, ob ich Viessmann als Partner für zukünftige Produkte (Batteriespeicher, PV Anlage etc) noch in Betracht ziehe. Immerhin bekommt man das Gefühl, dass Viessmann den Kunden melken will. Beispielsweise in dem man sich die Daten seiner EIGENEN Anlage wieder gegen einen monatlichen Betrag (oder über ein teures Gateway) selbst wieder zurückkaufen darf.Hoffentlich lernen andere Hersteller aus diesem Verhalten und bieten bessere/günstigere Alternativen für interessierte Kunden an.
---
Deine eigenen Daten kannst du an der Anlage selbst jeder Zeit kostenlos ablesen.
Wenn du aber Daten exportieren oder anderweitig verarbeiten willst, ist die Erwartungshaltung, dass der Hersteller dafür alles kostenlos bereitstellen muss auch nicht gerade fair.
---
Kann ich nur zustimmen,für mich ist es ein absolutes no go meine Heizung mit dem Viesmann Server zu verbinden.Damit ist für mich auch auch die zur Verfügung gestellte API sinnlos.
---
Es steht dir frei, ob du deine Anlage mit dem Viessmann-Server verbindest oder nicht. 
 
Es gibt auch entsprechende Alternativen, wie beispielsweise ein Vitogate oder schlichtweg eine Fernbedienung.
Für den Datenexport gibt es jedoch keine Alternative, denn das ist den Fachbetrieben vorbehalten.
---
Die Antwort dass ich meine Daten mit Fingern und Auge "manuell" ablesen kann, ist doch etwas aus dem letzten Jahrtausend! Und offiziell  diese Daten nur über Viessmann Server, zu verkaufen, ist in meinen Augen mehr als dreist, ganz davon abgesehen dass es Datenschutz Probleme gibt, weil dadurch das Verhalten einzelner Menschen beobachtet werden kann. (z.B. wann wird geduscht/gebadet....) Als Mieter kann ich mich da wegen Verstoß der DSVGO beschweren.Vor allem ist  technisch der direkte Zugriff auf die Vitoconnect Opto wesentlich einfacher , als der Umweg über WLAN und das Internet. (OpenV macht das vor....)Aber nur so kann Viessmann für meine eigenen Daten abkassieren! Und die Konnektivität mit anderen Smart Home Geräten wird erschwert. Ich bin bei der Planung einer Wärmepumpe. Das wird für Viessmann leider ein Ausschlußkriterium!
---
Sehe ich auch so,der einzige Grund warum Viessmann die Steuerung nur über den Viessman Server zulässt, istdie volle Kontrolle zu behalten.Ist leider ein Trent von vielen Firmen.,Dumm nur, das viele Kunden sich das einfach gefallen lassen.Und noch eine Bemerkung zu der Anwort am 19.09.202.Die Firma Viessman stellt nichts kostelos zur Vefügung.Wir haben alle für die Heizung bezahlt.
---
Die Antwort von CustomerCare zeigt doch eindeutig, dass von der Firma keine lokalen Lösungen gewünscht sind.Und mein Heizungsbauer ist ein hervorragend guter Heizungsbauer, aber von Netzwerk hat der keine Ahnung, und keine Lust sich in eine für ihn neue Materie einzuarbeiten. Warum auch? Wenn ich mir ansehe, wie gut die Home Automation Lösung von AVM und der Fritz!Box funktioniert. Mit WireGuard, also eine VPN Verbindung einfach von der Stange, und Datensicher herzustellen. Das sind halt Spezialisten für Netz Verbindung.Und Viessmann ist Spezialist für Heizungen. Leider bleiben die Schuster nicht bei Ihren Leisten.

---

## Thread #25: Open-Source Viessmann IoT API Datenlogger

**URL**: https://community.viessmann.de/t5/The-Viessmann-API/Open-Source-Viessmann-IoT-API-v2-Datenlogger-fuer-Vitocal/td-p/571453
**Posts**: 1

Hi zusammen,ich wollte meine Wärmepumpe (Vitocal 200-S) effizienter betreiben und brauchte dafür belastbare Daten – vor allem zum Taktverhalten des Kompressors. Daraus ist ein kleines, einsteigerfreundliches Open-Source-Projekt entstanden, das die Viessmann IoT API v2 nutzt, Messwerte ausliest und in MySQL speichert.Was das Projekt macht:🔐OAuth2/PKCE Login (neue Viessmann IoT API v2)🔄Automatischer Token-Refresh🧩 Flexible Feature-Erkennung (liest dynamisch alle Sensor-Features)💾Speicherung in MySQL (vitodata-Tabelle)📈Werte u. a.:AußentemperaturVorlauf/Rücklauf (HK 0 + 1)Warmwasser oben + SollSekundärkreis VorlaufKompressor: Startzähler, Laufzeit, Status (robust abgeleitet)🐳Docker-Compose Setup (mit/ohne mitgelieferte MySQL)Ziel: Die Taktung analysieren (Starts je Zeitraum, Laufzeiten pro Takt) und später mit Grafana visualisieren.Repo (MIT-Lizenz):👉https://github.com/rentasad/VissmannCollect Ich hoffe das Projekt kann auch Euch helfen. Feedback ist Willkommen! PS: Da ich noch neu auf der Materie bin, freue ich mich über wertvolle Hinweise, welche Werte ich ebenfalls sinnvollerweise loggen sollte, damit eine gute Auswertung funktioniert.

---

