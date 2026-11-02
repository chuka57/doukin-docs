// ローカル学習専用。招待・パスキー認証の実装ではありません。
import { Hono } from 'hono'

type Env = {
  Bindings: { DB: D1Database; DEMO_TOKEN?: string }
  Variables: { memberId: string }
}
const app = new Hono<Env>()

app.get('/api/health', (c) => c.json({ ok: true }))

// middleware：記録APIより先に共通のチェックを通す。
// DEMO_TOKENは.dev.varsだけに置く。本番には設定・公開しない。
app.use('/api/workouts/*', async (c, next) => {
  c.header('Cache-Control', 'no-store')
  if (!c.env.DEMO_TOKEN ||
      c.req.header('Authorization') !== `Bearer ${c.env.DEMO_TOKEN}`) {
    return c.json({ error: 'unauthorized' }, 401)
  }
  c.set('memberId', 'demo-member') // 学習用の固定会員
  await next()
})

app.post('/api/workouts', async (c) => {
  let input: unknown
  try { input = await c.req.json() }
  catch { return c.json({ error: 'invalid_json' }, 400) }
  if (typeof input !== 'object' || input === null ||
      !('exercise' in input) || typeof input.exercise !== 'string' ||
      input.exercise.trim().length < 1 || input.exercise.length > 80) {
    return c.json({ error: 'exercise_required_max_80' }, 400)
  }
  const id = crypto.randomUUID()
  // 所有者は送信されたmemberIdではなく、検証した文脈から取得する。
  await c.env.DB.prepare(
    'INSERT INTO workouts (id, member_id, exercise) VALUES (?, ?, ?)'
  ).bind(id, c.get('memberId'), input.exercise.trim()).run()
  return c.json({ id, visibility: 'private' }, 201)
})

app.get('/api/workouts/:id', async (c) => {
  const row = await c.env.DB.prepare(
    'SELECT id, exercise, visibility FROM workouts WHERE id = ? AND member_id = ?'
  ).bind(c.req.param('id'), c.get('memberId')).first()
  // 他人の記録の存在も応答から区別させない。
  if (!row) return c.json({ error: 'not_found' }, 404)
  return c.json(row)
})

app.onError((_error, c) => c.json({ error: 'internal_error' }, 500))
export default app
