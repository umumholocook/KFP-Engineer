# common/customField/

## Purpose
Custom Peewee field types for serializing complex Python objects into SQLite columns.

## Files
- `BuffField.py` — stores `RPGUtil.Buff` objects (buff type + expiry)
- `ItemTypeField.py` — stores `RPGUtil.ItemType` enum values

## Usage
Referenced by Peewee models in `common/models/` (e.g. `InventoryRecord`, `Item`) for non-primitive column types.

## When Adding
Follow existing pattern: implement `db_value()` and `python_value()` for round-trip serialization.