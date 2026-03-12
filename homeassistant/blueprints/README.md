# Open3E Home Assistant Blueprints

## Urlaubsmodus (`holiday_mode.yaml`)

Simuliert den Urlaubsmodus fuer Open3E Heizungsanlagen.

### Was macht das Blueprint?

- **Urlaubsbeginn**: Setzt Heizkreis auf "heat" (Reduziert-Modus), senkt Warmwasser-Temperatur
- **Urlaubsende**: Stellt automatisch den normalen Betriebsmodus wieder her

### Installation

1. Blueprint-Datei nach Home Assistant kopieren:
   ```
   config/blueprints/automation/open3e/holiday_mode.yaml
   ```

2. Oder direkt importieren ueber HA UI:
   - Einstellungen > Automatisierungen & Szenen > Blueprints
   - "Blueprint importieren" > URL eingeben

3. Neue Automatisierung aus Blueprint erstellen:
   - Einstellungen > Automatisierungen > "+ Automatisierung erstellen"
   - "Blueprint verwenden" > "Open3E Urlaubsmodus"

### Parameter

| Parameter | Beschreibung | Standard |
|-----------|-------------|----------|
| Urlaubsbeginn | Erster Urlaubstag | - |
| Urlaubsende | Letzter Urlaubstag | - |
| Reduzierte Raumtemperatur | Solltemperatur waehrend Urlaub | 16°C |
| Reduzierte WW-Temperatur | Warmwasser-Solltemperatur | 40°C |
| Normaler Betriebsmodus | Modus nach Urlaubsende | auto |

### Voraussetzungen

- Open3E Bridge laeuft mit MQTT
- MQTT-Integration in Home Assistant aktiv
- Heizkreis-Entities verfuegbar (DID 1415, 424, 396)

### Hinweis

Dieses Blueprint ersetzt NICHT den geraeteseitigen Urlaubsmodus (DID 511/512),
sondern steuert die Heizung ueber vorhandene schreibbare Entities.
Der Vorteil: Keine Abhaengigkeit von undokumentierten DID-Formaten.
