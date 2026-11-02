"""Conditional Access variants; not deployed settings."""
from guide_ui import section, note, table as guide_table, steps, diagram

def table(headers, rows, caption="Zero Trust追加案の比較"):
    return guide_table(headers, rows, caption)


def add_zero_trust_page(pages):
    body = note('推奨：まず運営画面・アプリの検証環境にCloudflare Accessを追加する案。', '一般会員にはN1の招待＋パスキーを維持し、運営者の入口を追加で保護します。全会員に個人IdP利用を求めてもよければ、アプリ全体をAccessで囲う案も比較できます。どちらも未実装の設計提案です。')
    body += section('compare', 'Zero Trustを、どこに入れる？', table(['構成案','一般会員の入口','運営・検証の入口','引き受ける条件'], [
        ('N1：現行の基準案','招待＋パスキー','アプリの認証・役割検査','独自認証と復旧を保守'),
        ('ZT-A：運営・検証だけ追加保護（推奨）','N1のまま','Cloudflare Access → パスキー → 運営役割','運営者の個人IdP・Zero Trust契約を許容'),
        ('ZT-B：全アプリを追加保護','Cloudflare Access → 招待＋パスキー','同じ入口＋運営者用の厳しいポリシー','全員にIdP等を要求。二つのログイン・復旧・失効を運用')], 'メールなしをアプリ内だけに求めるか、認証提供元にも求めるかで選択が変わります。'))
    body += section('architecture', 'ZT-B：アプリ全体をAccessで囲う構成', '<figure class="blueprint-diagram"><a href="zero-trust-stack.html"><img class="stack-image" src="assets/zero-trust-stack.png" width="1000" height="700" alt="ブラウザからCloudflare Accessへ進み、個人IdPで入口の資格を確認。許可後にStatic AssetsとWorkers Honoへ接続し、アプリの認証・認可後にD1へ保存する。"></a><figcaption><a href="zero-trust-stack.html">構成図を拡大</a> ／ <a href="assets/zero-trust-stack-dark.png">ダーク版</a>。Accessは入口の保護、Honoはアプリ会員とデータ権限、D1は保存を担当。応答経路・バックアップ経路は省略。</figcaption></figure>'
        + table(['具体的な製品・仕組み','この案での役割'],[
          ('Cloudflare Zero Trust / Access','許可したIdP・ユーザー等の条件で入口を制限。画面とAPIの両方を保護 [Z1]'),
          ('Cloudflare Workers Static Assets','React画面を配信。公開URLの保護はAccess側で行う'),
          ('Cloudflare Workers ＋ Hono','パスキー・セッション・会員状態・所有者・共有範囲を検査'),
          ('Cloudflare D1','会員・資格情報・セッション・記録を保存。Accessは行単位の認可を代行しない'),
          ('Cloudflare Tunnel / One Client（旧WARP）','今回のブラウザ→Workers案では必須にしない。私設サーバー接続や端末状態を要件にする場合に別途検討')]))
    body += section('recommended', 'ZT-A：一般会員の手間を増やさない追加案', diagram([
        ('person','一般会員','N1の入口を維持'),('key','運営者','Access＋パスキー'),('shield','管理API','Access証明＋運営役割'),('db','Cloudflare D1','同じ権限原則')], 'これは役割の比較です。一般会員が運営者の入口を経由する意味ではありません。')
        + table(['保護対象','設定の設計例','抜け道を作らない条件'],[
          ('運営画面 /admin/*','運営者のみAllow。IdP側でMFAを要求する運用を検討','画面だけでなく /api/admin/* を同じ条件で保護'),
          ('管理API /api/admin/*','WorkerでもAccess JWTを検証し、アプリの運営役割を検査','一般APIに招待発行・復旧承認・失効などの同等操作を残さない'),
          ('アプリの検証用Worker','Worker全体とそのプレビューをAccessで保護','ダミーデータ専用。D1・秘密・RP IDを本番と分離'),
          ('一般会員用アプリ','招待・パスキー・端末別セッション','管理URLのAccess除外条件が一般側から悪用できないか試験')])
        + '<p>ドメイン名・パス名は設計例です。ここでの「検証」はアプリの検証環境を指し、このGitHub Pages上の公開資料やPRプレビューを非公開にする変更ではありません。</p>')
    body += section('identity', '二つの本人確認を、混同しない', table(['確認','何が分かる？','何は分からない？'],[
        ('Accessの認証','入口のポリシーを満たす外部の利用者','doukinのどの会員か、どの記録を編集できるか'),
        ('doukinのパスキー認証','元の内部会員IDへ戻れること','その会員が今も有効か'),
        ('Honoの毎回の認可','有効会員・所有者・共有範囲・運営役割','基盤管理者からもデータを秘匿すること')])
        + '<p>ZT-Aの管理操作では、検証済みAccessの主体と内部運営会員IDを登録済みの対応に照合する案です。メール一致だけで自動連携しません。ZT-Bで対応表を全会員へ拡張すればIdP本人と記録の結び付きも増えます。対応を持たない場合、Accessは集団への入口確認にとどまり、二つのログインが同一人物だとは保証しません。</p>'
        + table(['個人IdPの例','情報最小化への影響'],[
          ('個人GitHub','公式設定でメールアドレスの読取権限等を要求。メール入力欄がなくても「誰もメールを持たない」構成ではない [Z3]'),
          ('メールのワンタイムPIN','承認したメールアドレスへ送る方式。メール不使用の条件とは両立しない [Z4]'),
          ('会社のSSO','元資料の会社アカウント不使用という比較条件では選ばない')]))
    body += section('workers', 'Workers固有の注意：ctx.accessだけに頼らない', note('Static Assets付きWorkerでは、ctx.accessが利用者のWorkerへ渡らない制約があります。', 'Accessはアプリと静的ファイルを保護しますが、内部ルーターを通るため、ctx.accessの有無だけでログイン判定を実装しないでください。Service Bindingでも自動伝搬しません。公式文書を2026-11-02に確認。[Z1]', 'orange')
        + steps([
          ('Accessの対象を決める','ZT-BはWorker全体保護を第一候補に。ホスト単位ならcustom domain・workers.dev・プレビュー・別ルートをすべて棚卸しし、不要な入口は閉じる。ZT-Aは管理画面と管理APIの両方を対象にする。'),
          ('Workerで証明を検査する','保護対象APIはCf-Access-Jwt-Assertionの署名、issuer、AUD、期限を既製JWT検証実装で確認。固定したチームの公開鍵を使い、不正・欠落・検証不能なら拒否。単なるメールヘッダーやJWTのdecodeだけを信用しない。[Z5]'),
          ('アプリの権限を重ねる','その後にdoukinのセッション・会員状態・所有者を確認。AccessのBypassやService Authを人間向けAPIの抜け道にしない。'),
          ('期限切れを画面で扱う','Access Cookieとdoukin Cookieは別々。APIでAccess期限切れ時の401応答を検討し、HTMLログイン画面をJSONとして処理しない。保存中の入力を失わず、再ログイン後の再送で重複を防ぐ。[Z6]')]))
    body += section('operation', '費用・退会・障害の扱い', table(['項目','提案と条件'],[
        ('無料枠','公式料金表はZero Trust Freeを50ユーザーとして案内。アプリ参加者だけでなく同じ契約の利用者も確認。Workers/D1の枠とは別で、50人想定は余裕がない。[Z2]'),
        ('契約','Zero Trust Freeでもセットアップ時の支払情報登録が必要と公式に案内。月額無料と支払登録不要は別条件。[Z7]'),
        ('会員失効','まずdoukin会員を無効化し全セッションを失効。Accessの許可条件からも除外してセッションを失効。Access側の反映をアプリの即時失効の代わりにしない。[Z6]'),
        ('復旧','doukinのパスキー復旧と個人IdPの復旧を別に用意。片方だけ回復しても通れないことを説明'),
        ('障害・締め出し','Access／IdP障害時に保護を外して公開しない。複数の管理者が安全な復旧経路を保持し、隔離環境で手順を試す'),
        ('ログ・個人情報','Access／IdPの本人属性・アクセスログにも情報が残り得る。アプリDBだけの最小化で全体の匿名性は保証しない'),
        ('性能','JWT検証を追加したWorkerのCPUと鍵更新時の挙動を実測。Freeで必ず収まるとは扱わない')]))
    body += section('acceptance','追加案の合格条件', table(['試験','期待する結果'],[
        ('Accessを通らず直アクセス','対象の全ホスト／プレビュー／管理APIで拒否。偽造ヘッダーも拒否'),
        ('Access通過・未招待／失効会員','doukin APIは拒否。他人の非公開記録も読めない'),
        ('一般会員の管理操作','ZT-Aで直接管理APIを呼んでも拒否。運営会員とAccess主体の取り違えも拒否'),
        ('Accessのみ／doukinのみ期限切れ','それぞれのログインへ案内し、入力消失・無限リダイレクト・重複保存なし'),
        ('Static Assets・実機','画面もAPIも保護され、iOS Safari／Android Chromeで再訪・ログアウト・復旧が成立'),
        ('設定・費用','利用者総数・支払登録・管理者復旧・本番と検証の分離を確認')])+'<p>現時点は公式文書の調査と構成提案のみ。Access設定変更・契約・実機検証は行っていません。</p>')
    sources=[('Z1','WorkersとAccess','https://developers.cloudflare.com/workers/configuration/cloudflare-access/'),('Z2','Cloudflare料金表','https://www.cloudflare.com/plans/'),('Z3','GitHub IdP','https://developers.cloudflare.com/cloudflare-one/integrations/identity-providers/github/'),('Z4','One-time PIN','https://developers.cloudflare.com/cloudflare-one/integrations/identity-providers/one-time-pin/'),('Z5','Access JWT検証','https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/authorization-cookie/validating-json/'),('Z6','Accessセッション管理','https://developers.cloudflare.com/cloudflare-one/access-controls/access-settings/session-management/'),('Z7','Zero Trust初期設定','https://developers.cloudflare.com/cloudflare-one/setup/')]
    body+=section('sources','公式出典と確認日', '<p>追加確認：2026-11-02（日本時間）。Z1〜Z7は公式情報、推奨する配置・運用・パス名は設計提案です。</p>'+table(['番号','出典'],[(f'<span id="source-{k}">{k}</span>',f'<a href="{url}">{label}</a>') for k,label,url in sources]))
    import re
    body=re.sub(r'\[(Z\d+)\]',r'<a href="#source-\1">[\1]</a>',body)
    pages['zero-trust']=dict(nav='Zero Trustを追加する案',title='入口にAccessを足すと、<br>何が変わる？',intro='運営・検証だけを保護する案と、全会員を保護する案を比較。Cloudflare Accessとアプリの認証・認可を分けて考えます。',body=body,icon='shield',group='追加調査',issue='追加構成案 / Zero Trust',kicker='DOUKIN / ZERO TRUST',related=('overall-spec','auth','platform','minimization'))
