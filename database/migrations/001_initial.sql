-- Executed transactionally as bag_end_owner by the migration runner.
CREATE TABLE bag_end.pools (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL UNIQUE CHECK (length(btrim(name)) BETWEEN 1 AND 100),
  active boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE bag_end.transactions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  type text NOT NULL CHECK (type IN ('PAYDAY', 'REGULAR')),
  pool_id uuid REFERENCES bag_end.pools(id) ON DELETE RESTRICT,
  date date NOT NULL,
  amount numeric(18, 2) NOT NULL CHECK (amount <> 'NaN'::numeric),
  merchant text NOT NULL CHECK (length(btrim(merchant)) BETWEEN 1 AND 300),
  note text,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX transactions_date_idx ON bag_end.transactions (date DESC, id);
CREATE INDEX transactions_pool_date_idx ON bag_end.transactions (pool_id, date DESC);
CREATE INDEX transactions_uncategorized_idx ON bag_end.transactions (date, id)
  WHERE pool_id IS NULL;

COMMENT ON COLUMN bag_end.transactions.type IS 'PAYDAY or REGULAR';
COMMENT ON COLUMN bag_end.transactions.pool_id IS 'NULL means uncategorized';
COMMENT ON COLUMN bag_end.transactions.amount IS
  'Signed decimal amount: income positive, spending negative. Currency semantics remain to be defined.';
COMMENT ON COLUMN bag_end.transactions.date IS 'Transaction calendar date, without a timezone';

GRANT SELECT ON bag_end.pools, bag_end.transactions
  TO bag_end_web, bag_end_tools, bag_end_importer, bag_end_backup;
GRANT INSERT (name, active), UPDATE (name, active)
  ON bag_end.pools TO bag_end_web;
GRANT INSERT (type, pool_id, date, amount, merchant, note),
  UPDATE (type, pool_id, date, amount, merchant, note)
  ON bag_end.transactions TO bag_end_web;
-- Imports preserve user-assigned pools and notes. Agent tools start read-only.
GRANT INSERT (type, date, amount, merchant), UPDATE (type, date, amount, merchant)
  ON bag_end.transactions TO bag_end_importer;
