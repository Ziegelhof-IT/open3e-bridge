# Known Bugs & Migration Issues

## BUG-01: Stale statistics_meta blocks HA long-term statistics

**Status:** Fixed (manual DB cleanup) | **Severity:** High | **Date:** 2026-02-27

### Problem

Home Assistant `statistics_meta` entries created by the old open3e setup (July 2025,
before the bridge existed) had `unit_of_measurement = NULL`. When the bridge later
created entities with correct `unit_of_measurement` via MQTT Discovery, HA did NOT
update the existing `statistics_meta` rows. Result: no long-term or short-term
statistics were recorded for affected entities, even though state changes were
tracked correctly.

### Affected Entities (before fix)

All `_actual` temperature sensors (269, 271, 274, 286, 1770, 2333, 2334, 354),
pressure sensors (318), pump sensors (381, 1043), and counter sensors (2369, 2370).
Only `268_actual` and `3016_actual` were unaffected (created fresh with correct units).

147 stale `statistics_meta` rows, 5078 orphaned `statistics` rows, 105 orphaned
`statistics_short_term` rows were cleaned up.

### Root Cause

HA creates `statistics_meta` on first state recording. Once created, `unit_of_measurement`
is never updated from Discovery payloads. The old open3e client (pre-bridge) published
raw MQTT sensors without units, creating the initial `statistics_meta` with NULL.

### Fix Applied

1. `ha core stop`
2. SQL: Delete from `statistics_short_term`, `statistics`, `statistics_meta` where
   `statistic_id LIKE 'sensor.open3e%' AND unit_of_measurement IS NULL`
3. `ha core start` -- HA recreates `statistics_meta` with correct units from entity registry

### Prevention

When migrating from old open3e setups or changing `unit_of_measurement` on existing
entities, the `statistics_meta` table must be manually cleaned. HA does not auto-fix this.
Consider adding a migration script to the bridge deployment process.

---

## BUG-02: Zombie entities from "Unknown" sub-items

**Status:** Open | **Severity:** Low | **Date:** 2026-02-27

### Problem

The open3e client publishes sub-items named "Unknown" for some DIDs (e.g., DID 271).
The bridge generates discovery entities for these, creating unwanted "Unknown" entities
in HA.

### Current Mitigation

`generate_entity_id()` in `base.py` skips "unknown" sub-items in entity ID generation,
but discovery messages may still be generated.

### TODO

- Filter out "Unknown" sub-items entirely in `_generate_typed_discovery()`
- Only generate entities for sub-items explicitly listed in `subs:` config

---

## BUG-03: `object_id` deprecated in HA 2026.4

**Status:** Open | **Severity:** Medium | **Date:** 2026-02-27

### Problem

HA 2026.4 deprecates `object_id` in MQTT Discovery. Must migrate to
`default_entity_id` with domain prefix (e.g., `sensor.open3e_680_268_actual`).

### TODO

- Update `_build_entity_config()` in `homeassistant.py`
- Replace `object_id` with `default_entity_id` (format: `{entity_type}.{entity_id}`)
- Test with HA 2026.4 beta before release
- Timeline: Must be done before HA 2026.4 release

---

## BUG-04: Min/Max/Average sub-items create unwanted entities

**Status:** Open | **Severity:** Low | **Date:** 2026-02-27

### Problem

Some DIDs publish Min/Max/Average sub-items alongside Actual. If these sub-items
are not filtered, the bridge creates unnecessary entities.

### Current Mitigation

`datapoints.yaml` only lists `Actual` in `subs:` config. Unlisted sub-items are
skipped in `_generate_typed_discovery()`. This works correctly.

### Note

This is effectively resolved by the current whitelist approach. Keeping as documentation.
