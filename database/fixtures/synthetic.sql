-- Explicit opt-in only. No real bank, person, or transaction data.
BEGIN;
SET LOCAL ROLE bag_end_owner;
INSERT INTO bag_end.pools (id, name) VALUES
  ('10000000-0000-4000-8000-000000000001', 'Synthetic Income'),
  ('10000000-0000-4000-8000-000000000002', 'Synthetic Groceries'),
  ('10000000-0000-4000-8000-000000000003', 'Synthetic Household')
ON CONFLICT (id) DO NOTHING;
INSERT INTO bag_end.transactions (id, type, pool_id, date, amount, merchant, note) VALUES
  ('20000000-0000-4000-8000-000000000001', 'PAYDAY',
   '10000000-0000-4000-8000-000000000001', '2026-10-01', 2500.00,
   'Synthetic Employer', 'Synthetic fixture; no real financial data.'),
  ('20000000-0000-4000-8000-000000000002', 'REGULAR',
   '10000000-0000-4000-8000-000000000002', '2026-10-02', -42.35,
   'Synthetic Grocery Store', NULL),
  ('20000000-0000-4000-8000-000000000003', 'REGULAR',
   '10000000-0000-4000-8000-000000000003', '2026-10-03', -18.90,
   'Synthetic Household Store', 'Synthetic fixture; no real financial data.'),
  ('20000000-0000-4000-8000-000000000004', 'REGULAR',
   NULL, '2026-10-04', -7.25, 'Synthetic Uncategorized Merchant', NULL)
ON CONFLICT (id) DO NOTHING;
COMMIT;
