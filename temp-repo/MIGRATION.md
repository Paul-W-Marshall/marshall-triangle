# Migration Notes

## Database Migration

The application now uses a new database schema with the following tables:

- **marshall_states**: Stores user-saved states (formerly harmony_states)
- **rendering_presets**: Stores user-saved rendering parameters

The migration script (migrate_db.py) will automatically:

1. Create the new tables if they don't exist
2. Transfer data from old tables to new tables
3. Preserve existing data during upgrades

## Legacy Data

If you're upgrading from an older version, your saved states will be automatically migrated to the new format.

## Reset Database

If you need to reset the database completely, you can delete the harmony_presets.db file and restart the application.
