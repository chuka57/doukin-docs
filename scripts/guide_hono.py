"""Beginner guide; example files are the source of displayed code."""
from pathlib import Path
from html import escape
from guide_ui import section, note, table, diagram, details
ROOT = Path(__file__).resolve().parent.parent

def code(text, language='typescript'):
    return '<pre class="example-code"><code class="language-'+language+'">'+escape(text.strip())+'</code></pre>'

def add_hono_page(pages):
    body = note('Hono（炎）は、APIを組み立てる軽量なWebフレームワーク。', '「このURLにはこの処理」「先にログインを確認」「結果をJSONで返す」を整理する道具です。Cloudflareのサービスではなく、Workers以外でも動くライブラリです。')
    body += section('workers-vs-ec2', 'Workersは、EC2よりLambdaに近い', '<p><strong>EC2は仮想サーバーを借りるサービス。Workersは、リクエストなどのイベントに応じてコードを実行するサービスです。</strong>サーバー自体は存在しますが、OSや起動台数の管理をCloudflareへ任せます。AWSでの考え方はLambdaに近く、機能が一対一で同じという意味ではありません。</p>'+table(['観点','Amazon EC2','Cloudflare Workers'],[('用意するもの','仮想マシン、OS、アプリ実行環境','Workerのコードと設定'),('HTTP処理','自分でWebサーバーやプロセスを起動・運用','HTTP要求が来るとfetchハンドラーが呼ばれる'),('実行環境','OS上でNode.jsなどを動かせる','V8ベースのWorkersランタイム。Node.js互換は部分対応'),('データの保存','EBSなどのディスクや外部DBを設計','今回の永続データはD1へ。グローバル変数をDB代わりにしない'),('自由度と負担','自由度が高い一方、OS・更新・運用も管理','基盤管理を減らせる一方、CPU・メモリ・利用APIに制約')], '一般的なEC2とWorkersの比較。構成や利用プランによって運用方法は変わります。')+'<p>doukinでは「保存ボタン → Workerのfetch → HonoがURLを振り分け → D1へ保存 → 応答」という流れです。SSHでWorkerへ入り、npm startを常駐させる運用はしません。サーバーを管理する手間を減らせるため候補にしています。</p><p>確認：2026-11-03。<a href="https://developers.cloudflare.com/workers/reference/how-workers-works/">Cloudflare：Workersの仕組み</a> ／ <a href="https://docs.aws.amazon.com/lambda/latest/dg/welcome.html">AWS：Lambdaの概要</a> ／ <a href="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html">AWS：EC2の概要</a></p>')
    body += section('language', '使う言語はTypeScript。実行されるのはJavaScript。', '<p>今回の案は<strong>TypeScript（JavaScriptに型を付けた言語）</strong>で書き、ビルド後のJavaScriptをWorkersで実行します。HonoはJavaScriptでも使えます。</p>'+table(['場所','書くもの','実行する場所'],[('Reactの画面','.tsx：TypeScript＋JSX','ビルド後のJavaScriptをブラウザで実行'),('HonoのAPI','.ts：TypeScript','ビルド後のJavaScriptをCloudflare Workersで実行'),('D1のデータ操作','SQL（文字列または.sql）','Cloudflare D1が実行')], '型は開発中の間違いを見つける助けです。外部から届くJSONの検査は、型を書くだけでは済まないため実行時にも行います。'))
    body += section('roles','まず、3つの役割を分ける', table(['名前','担当','doukinなら'],[
        ('Cloudflare Workers','コードを動かす実行基盤','HTTP要求が来たときにAPI処理を実行'),
        ('Hono','処理の振り分け・共通処理・応答作成','POST /api/workouts を記録作成へ振り分け'),
        ('Cloudflare D1','SQLデータベース','会員・筋トレ記録などを永続保存')], 'Reactはブラウザで画面を作ります。Honoは今回、サーバー側のAPIを担当します。')
        + diagram([('person','React画面','保存ボタンを押す'),('cloud','Workers','Honoのコードを実行'),('key','Hono','認証→入力検査→保存'),('db','Cloudflare D1','SQLを実行')], '応答はD1 → Hono → ブラウザへ戻ります。Honoだけではデータベースやログイン機能は完成しません。'))
    plain = '''export default {
  async fetch(request: Request) {
    const url = new URL(request.url)
    if (request.method === 'GET' && url.pathname === '/api/health') {
      return Response.json({ ok: true })
    }
    return new Response('Not Found', { status: 404 })
  },
}'''
    hono = '''import { Hono } from 'hono'
const app = new Hono()
app.get('/api/health', (c) => c.json({ ok: true }))
export default app'''
    body += section('minimal','1. まずは「動いている？」と返すAPI', '<p>ブラウザから <code>GET /api/health</code> を呼ぶと <code>{"ok":true}</code> が返ります。Honoを使うと、URLの判定とJSON応答を短く書けます。</p>'+code(hono)+details('比較：Honoを使わず、素のWorkersで書くと',code(plain))
        + table(['記述','意味'],[('app.get(パス, 処理)','GET要求の担当処理を登録する。postなら作成などに使うPOST。'),('c（Context）','その1回の要求・応答・環境設定をまとめた窓口。'),('c.json(値, ステータス)','JSON応答を作る。200は成功、201は作成成功。'),('export default app','Workersが呼べるfetchハンドラーを持つアプリを渡す。')], '別サーバーを起動してHonoへ転送する構成ではなく、Workerの中でHonoが動きます。'))
    worker=(ROOT/'content/examples/hono/worker.ts').read_text()
    schema=(ROOT/'content/examples/hono/schema.sql').read_text()
    body += section('record','2. doukinの「保存→取得」を小さく書く', '<p>実装例は「種目名を1件保存し、自分の記録だけ取得する」ところまで。重量・セット・共有・本番認証を省いた、ローカル学習用です。</p>'
        + table(['要求','送るもの','返るもの'],[('POST /api/workouts','{"exercise":"スクワット"}','201：作成したidとprivate'),('GET /api/workouts/:id','保存時に返ったid','200：自分の記録／404：なし・他人'),('認証なし／不正な入力','トークンなし／空の種目名','401／400')], '成功応答はD1の保存が終わってから返します。')
        + details('実装例を開く：src/index.ts（Hono＋D1）',code(worker))
        + table(['注目するところ','何のため？'],[('app.use(..., next)','ミドルウェア。記録処理の前に共通チェックし、通ったらnextで先へ進む。'),('c.env.DB','WranglerでDBという名前を付けて接続したCloudflare D1。'),('prepare(...).bind(...)','SQLの?へ値を渡す。入力をSQL文字列へ直接連結しない。'),('run() / first()','SQL実行／最初の1行を取得。結果を待つのでawaitを使う。'),('c.set / c.get','この要求の中だけで、確認した会員IDを次の処理へ渡す。'),('WHERE id = ? AND member_id = ?','IDが分かっても他人の記録を取得できないよう、SQLにも所有者条件を入れる。')], 'Honoが所有権や入力の妥当性を自動判定するわけではありません。実装者が条件を書きます。'))
    commands='''npm create hono@latest doukin-hono-demo
# テンプレートは cloudflare-workers、パッケージ管理は npm を選択
cd doukin-hono-demo
npm install
# 下の設定を反映し、表示したコードを src/index.ts に保存
npx wrangler d1 execute doukin-demo --local --file=./schema.sql
npx wrangler types
npm run dev'''
    config='''// wrangler.jsonc（生成済み設定へこの項目を追加・調整）
{
  "name": "doukin-hono-demo",
  "main": "src/index.ts",
  "compatibility_date": "2026-11-03",
  "d1_databases": [{
    "binding": "DB",
    "database_name": "doukin-demo",
    "database_id": "00000000-0000-0000-0000-000000000000"
  }]
}'''
    curl='''# .dev.vars（gitへ登録しない。値は学習用）
DEMO_TOKEN="local-learning-only"

# 別のターミナルから。既定ポート8787の例
curl http://localhost:8787/api/health
curl -i -X POST http://localhost:8787/api/workouts \\
  -H 'Authorization: Bearer local-learning-only' \\
  -H 'Content-Type: application/json' \\
  --data '{"exercise":"スクワット"}'
# 応答のidを下へ入れる
curl http://localhost:8787/api/workouts/返されたID \\
  -H 'Authorization: Bearer local-learning-only' '''
    body += section('try','3. 自分のPCで試す手順', '<p>Node.jsとnpmが必要です。生成されたプロジェクトで、下の設定とコードを使います。<strong>--localのみで試し、deployはしません。</strong>DBのゼロUUIDはローカル学習用で、本番DBのIDではありません。</p>'
        +details('手順・Wrangler設定・SQL・リクエスト例を開く',code(commands,'bash')+code(config,'json')+'<p><code>schema.sql</code>として保存：</p>'+code(schema,'sql')+'<p><code>.dev.vars</code>にトークンを置き、再起動後にcurlで呼びます。Windows PowerShellではcurl.exeを使うか、同等のHTTPクライアントで送信してください。</p>'+code(curl,'bash'))
        +'<p>この環境ではnpm依存を入れた実行・デプロイは未検証です。テンプレートの版により設定形式や起動コマンドが変わる場合は、生成READMEと公式手順を確認してください。</p>')
    body += section('production','4. この例と、本番の設計案の違い', table(['学習用の例','本番へ進むときに追加すること'],[
        ('固定トークン＋固定会員','招待・パスキー・端末別セッションを検証し、有効な内部会員IDを設定。利用者が送るmemberIdを信用しない。'),
        ('種目名だけ・本人のみ','記録とセットの整合、明示共有、体重の分離、再送時の重複防止。'),
        ('最低限の入力検査','リクエストサイズ、試行制限、Cookie認証時のCSRF対策、ログに秘密を出さない監視。'),
        ('ローカルのD1','本番・検証の分離、マイグレーション、バックアップ・復元、CPUと走査行数の実測。'),
        ('Access未使用','運営用APIはAccess JWTとアプリの運営役割を両方検査。Hono自体はAccessの代わりにならない。')], 'DEMO_TOKENは学習専用です。例をそのまま本番へ公開する設計ではありません。')+'<p>まずhealth APIでHonoの役割を理解し、次にD1保存を試すと、画面・API・DBの境界を確認できます。</p>')
    body += section('sources','公式資料', '<p>確認日：2026-11-03（日本時間）。実装例はdoukin向けに作った説明用コードで、公式サンプルの転載ではありません。</p>'+table(['読みたい内容','公式リンク'],[
        ('WorkersでHonoを始める','<a href="https://hono.dev/docs/getting-started/cloudflare-workers">Hono / Cloudflare Workers</a>'),
        ('c.req・c.env・c.jsonを調べる','<a href="https://hono.dev/docs/api/context">Hono / Context</a>'),
        ('D1のSQL実行・bind・first','<a href="https://developers.cloudflare.com/d1/worker-api/prepared-statements/">Cloudflare D1 / Prepared statements</a>')], '既存の全体設計案の出典確認日は変更していません。'))
    pages['workers-hono']=dict(nav='Workers＋Hono入門',title='Honoって何？<br>小さなAPIで理解する。',intro='Workers・Hono・D1の役割から、筋トレ記録を保存するコードまで。コードは必要なところだけ開いて読めます。',body=body,icon='cloud',group='追加調査',issue='技術解説 / 実装例',kicker='DOUKIN / WORKERS + HONO',related=('overall-spec','platform'))
