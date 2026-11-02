"""One concise review page with optional source details."""
from pathlib import Path
import re
from guide_ui import section, note, table, diagram, details
from guide_zero_trust import add_zero_trust_page


def add_blueprint_page(pages):
    original = (Path(__file__).resolve().parent.parent / 'content' / 'overall-spec.html').read_text(encoding='utf-8')
    original = re.sub(r'<aside class="note">.*?</aside>', '', original, count=1, flags=re.S)
    extra = {}
    add_zero_trust_page(extra)
    zero = extra['zero-trust']['body']
    body = note('推奨案：N1 ＋ 運営・検証だけCloudflare Accessで保護。', '一般会員は招待＋パスキーで参加。記録は本人のみ、選んだ記録だけ同期に共有します。運営者にはAccessの確認も追加します。以下は採用前の設計案です。')
    body += section('summary-stack', '1. 構成はこれだけ',
        '<p><strong>一般会員の経路</strong>：メール入力をアプリで求めず、パスキーと保持セッションで利用。</p>'
        + diagram([('person','React画面','TypeScript＋Vite'),('key','招待＋パスキー','端末別Cookieで保持'),('cloud','Workers＋Hono','会員・所有者を毎回確認'),('db','Cloudflare D1','会員・記録・体重を保存')], '画面ファイルの配信元はCloudflare Workers Static Assets。D1へはAPI経由で接続します。')
        + '<p><strong>運営者の経路</strong>：個人IdP → <strong>Cloudflare Access</strong> → アプリ認証・運営役割 → 管理API。アプリの検証環境もAccessで保護し、本番とDBを分けます。</p>'
        + '<p>Accessは入口の確認、Honoは記録ごとの権限確認、D1は保存担当です。</p>')
    body += section('summary-behavior', '2. 使う人から見た仕様', table(['項目','推奨する動き'],[
        ('参加・日々の利用','個別招待＋パスキー。通常の再訪はログイン保持で入力を省く。'),
        ('筋トレ記録','種目・重量・回数・セットを保存。初期は本人のみ、共有は明示操作。'),
        ('体重・写真','体重を実装する場合は本人専用の別データ。写真アップロードは後回し。'),
        ('紛失・退会','予備パスキー／復旧コードで復旧。退会・失効時は会員とセッションを無効化。'),
        ('情報・復元','氏名・メールの対応表をアプリに持たない。日次の暗号化退避と復元試験を用意。')], '数十人規模を想定した案。体重のMVP採否と退避先は未決定です。'))
    body += section('summary-access', '3. Zero Trustは、どこまで使う？', table(['案','保護する範囲','向いている条件'],[
        ('<strong>推奨：運営・検証だけ</strong>','管理画面・管理API・アプリ検証環境をAccessで保護','一般会員の手間と本人情報の追加を抑えたい。'),
        ('代替：全アプリ','全会員がAccess → アプリ認証の順に通過','全員の個人IdP利用と二つのログイン・復旧を許容できる。')], 'Accessを追加しても、アプリの招待・会員状態・データ権限の確認は必要です。')
        + '<p>個人GitHub等のIdPはメール等を扱い得ます。<strong>「アプリでメールを持たない」と「認証基盤にも持たない」は別</strong>です。元のN1構成はAccessなしでも比較基準として残します。</p>')
    body += section('summary-gates', '4. 実装前に確認する4点', table(['確認点','判断材料'],[
        ('Workers互換性','Hono・パスキー・JWT検証を実ランタイムで試す。FreeのCPU 10 ms内に収まるか実測。'),
        ('Accessの入口','管理API・別URL・プレビューにも抜け道を作らない。Static Assetsではctx.accessに頼らずJWT検証を設計。'),
        ('契約・人数','Zero Trust Freeは50ユーザー枠、支払情報登録が必要。Workers/D1・ドメイン・退避費は別に確認。'),
        ('復旧・期限切れ','スマホ2種で紛失・失効・再ログインを試す。日次退避から削除済み情報を復活させず復元できること。')], '公式確認：Workers関連2026-11-01、Access関連2026-11-02。実機・性能・本番設定は未検証。'))
    # Keep old anchors available inside optional detail; exclude them from the main TOC.
    original = original.replace('<h2 ', '<h3 ').replace('<h2>', '<h3>').replace('</h2>', '</h3>')
    zero = zero.replace('<h2 ', '<h3 ').replace('<h2>', '<h3>').replace('</h2>', '</h3>')
    body += details('必要なときだけ：構成図・技術仕様・公式出典', original + zero)
    pages['overall-spec'] = dict(nav='全体設計案（要約）',title='全体設計案を、<br>1ページで確認。',intro='基本構成とZero Trustをまとめて確認。通常は4項目だけ、細かな仕様と出典は下の補足から読めます。',body=body,icon='map',group='はじめに',issue='統合設計案 / 要約',kicker='DOUKIN / BLUEPRINT',related=('index',))
    anchors = re.findall(r'id="([^"]+)"', extra['zero-trust']['body'])
    pages['zero-trust'] = dict(extra['zero-trust'])
    pages['zero-trust'].update(group='互換URL',title='Zero Trust案は、全体設計案へ統合しました。',intro='基本構成とZero Trustの比較を、ひとつの資料で確認できます。',body='<p><a class="button primary" href="overall-spec.html#summary-access">統合した全体設計案を見る →</a></p>'+''.join(f'<p id="{a}"><a href="overall-spec.html#{a}">旧資料の該当箇所を見る →</a></p>' for a in anchors),related=('overall-spec',))
