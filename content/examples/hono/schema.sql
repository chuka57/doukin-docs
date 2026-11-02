-- ローカルのダミーデータ専用。本番用マイグレーションではありません。
CREATE TABLE IF NOT EXISTS workouts (
  id TEXT PRIMARY KEY,
  member_id TEXT NOT NULL,
  exercise TEXT NOT NULL,
  visibility TEXT NOT NULL DEFAULT 'private' CHECK (visibility = 'private')
);
