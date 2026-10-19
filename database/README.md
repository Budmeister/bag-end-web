# Initial Bag End schema

The application schema is `bag_end`. Its master transaction table is
`bag_end.transactions`:

| Column | Type | Meaning |
| --- | --- | --- |
| `id` | UUID | Generated primary key |
| `type` | text, required | Exactly `PAYDAY` or `REGULAR` |
| `pool_id` | UUID, optional | Foreign key to `bag_end.pools.id`; NULL means uncategorized |
| `date` | date, required | Transaction date, without a time/timezone |
| `amount` | numeric(18,2), required | Positive income, negative spending; no floating-point storage |
| `merchant` | text, required | Merchant or employer; nonblank, at most 300 characters |
| `note` | text, optional | User note; NULL is allowed |
| `created_at` | timestamptz | Database insertion time |

Amounts use two decimal places. PostgreSQL rounds extra fractional digits to that
scale and rejects out-of-range values and NaN. The schema does not force a sign
based on type, allowing regular credits/refunds. Currency handling, bank account
identity, import deduplication, manual overrides, and audit history will be added
when those features are designed.

`bag_end.pools` has a generated UUID, unique nonblank name, an `active` flag, and
creation time. Pools referenced by transactions cannot be deleted; they can be
marked inactive without losing transaction history. Pool assignments are optional
for both PAYDAY and REGULAR records.

The runtime infrastructure script applies migrations with the dedicated migration
role and tracks checksums. Add new migration files for changes; do not edit a
migration after it has been applied. The fixture file contains synthetic data
only. In cloud development, `scripts/test.py` creates its own isolated PostgreSQL
cluster and the test suite applies these migrations/fixtures without requiring
the parent infrastructure repository or the persistent runtime database.

No database connection is added to the hello-world HTTP app in this step.
