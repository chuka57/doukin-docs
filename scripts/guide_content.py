"""Curated reading pages. Facts, proposals and unresolved work are labeled separately."""
from html import escape
from guide_ui import section, note, card, grid, bullets, steps, details, table, diagram, definition, ref
from guide_decisions import recommendation_overview, theme_guide

EXTRA_SOURCES = {
 'S47': ('Clerk: MFA and recovery / Device Trust', 'https://clerk.com/docs/guides/secure/mfa-recovery', '新端末での追加認証と識別子・MFAの条件'),
 'S48': ('Clerk: Sign-in-or-up', 'https://clerk.com/docs/guides/development/custom-flows/authentication/sign-in-or-up', 'ユーザー名のみの統合フローの制約'),
 'S49': ('Clerk: updateUser', 'https://clerk.com/docs/reference/backend/user/update-user', '管理APIのパスワード更新と他セッション失効'),
 'S50': ('Cloudflare One: Get started', 'https://developers.cloudflare.com/cloudflare-one/setup/', 'Zero Trust Freeでも初期設定に支払情報が必要'),
 'S51': ('Cloudflare Access: GitHub IdP', 'https://developers.cloudflare.com/cloudflare-one/integrations/identity-providers/github/', '個人GitHubログイン、組織・チーム・メールの読取権限'),
 'S52': ('Workers: Cloudflare Access', 'https://developers.cloudflare.com/workers/configuration/cloudflare-access/', 'WorkersとStatic Assetsの保護、ctx.accessの制約'),
 'S53': ('Workers: workers.dev', 'https://developers.cloudflare.com/workers/configuration/routing/workers-dev/', '標準URLとAccess、プレビューURLの保護'),
 'S54': ('GitHub: Pull requests API', 'https://docs.github.com/en/rest/pulls/pulls', 'Organizationのprivate repoでのDraft PRの対応プラン'),
 'S55': ('GitHub: Adding sub-issues', 'https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues', 'Issueの親子関係と作業分割'),
 'S56': ('GitHub: Issue dependencies', 'https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-issue-dependencies', '親子関係と依存関係の違い'),
 'S57': ('Cloudflare: Update billing information', 'https://developers.cloudflare.com/billing/get-started/update-billing-info/', 'アドオン購読と支払方法の維持'),
 'S58': ('Supabase Auth: Rate limits', 'https://supabase.com/docs/guides/auth/rate-limits', '外部SMTP設定後にもあるAuth側の送信制限'),
 'S59': ('Supabase: Billing', 'https://supabase.com/docs/guides/platform/billing-on-supabase', 'Fair Useと無料利用枠の扱い'),
 'S60': ('OWASP: Authorization Cheat Sheet', 'https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html', '既定拒否、各リクエストでの権限検査、最小権限'),
 'S61': ('OWASP: Forgot Password Cheat Sheet', 'https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html', '復旧トークンの期限・単回利用、安全な復旧設計'),
 'S62': ('Supabase: Send Email Hook', 'https://supabase.com/docs/guides/auth/auth-hooks/send-email-hook', 'SMTPに代わり独自の配信経路を使うAuth Hook'),
 'S63': ('D1: Import and export data', 'https://developers.cloudflare.com/d1/best-practices/import-export-data/', 'SQLのエクスポート・インポートと復元時の制約'),
}


def make_pages(bibliography):
    pages = {}
    def add(slug, nav, title, intro, body, icon='book', group='テーマから調べる', issue='Issue #3・#4', kicker='DOUKIN / GUIDE', related=()):
        pages[slug] = dict(nav=nav, title=title, intro=intro, body=body, icon=icon, group=group, issue=issue, kicker=kicker, related=related)

    index = note('この資料で調べること', 'doukinの構成候補を比較するために、<strong>推奨の理由、データ保護の方法、復旧や費用管理を想定した運用例</strong>を調査・整理します。数十人の利用・３人での保守を比較条件として仮定し、５つのテーマで追加検証の観点を説明します。確定要件や採用結果を記録する資料ではありません。')
    index += recommendation_overview()
    index += section('start', 'どこから読もう？', grid(
        card('構成案を見くらべる', '５つの組み合わせを、メール・費用・つくる負担で比較。各案の詳しい取扱説明書へ進めます。', 'map', 'compare.html', '全体を知りたい'),
        card('決める順序をつかむ', 'Issue #3と#4をつなぐ進め方。先に合わせる前提と、小さく試すことを整理しています。', 'steps', 'workflow.html', '相談を進めたい')))
    index += section('themes', 'テーマから調べよう', grid(
        card('認証・招待・復旧', '推奨は個別招待＋パスキーの試作。復旧を保守できない場合の代替と、担当者の手順を説明します。', 'key', 'auth.html', '#3'),
        card('公開範囲・権限', '初期非公開・本人の明示共有を推奨。権限の実装場所と退会時の失効を決めます。', 'shield', 'privacy.html', '#3'),
        card('技術スタック・配信', '静的なReact画面＋必要なAPIを推奨。本番・検証環境とリリースの方法を決めます。', 'cloud', 'platform.html', '#4'),
        card('データ・画像・復元', 'SQL・テキスト中心・毎日の退避を推奨。DBの選び分けと復元の手順を説明します。', 'db', 'data.html', '#4'),
        card('無料枠・費用', '無料を続ける制限と監視を推奨。上限前に対処し、有料化を相談する条件を決めます。', 'cost', 'cost.html', '#4')))
    index += section('rules', '今回、忘れないこと', definition([
        ('比較に置く条件', '<strong>会社アカウントを使わない場合</strong>を仮定して比較します。登録・ログイン・復旧・開発運用も対象にします。確定要件の記載ではありません。'),
        ('優先して探す方法', '個人メール以外の方法を優先。個人メールや個人OAuthは、許容できる場合の代替案として比較します。'),
        ('費用の考え方', '原則無料。月額0円と、支払情報の登録・超過課金のある無料枠を区別します。'),
        ('まだ仮定の部分', '数十人の利用・開発者約3人を想定。写真・体重・PWAなどのMVP範囲はIssue #2と相談中です。')]) + '<div class="legend"><span>公式確認：提供元の文書で確認</span><span>設計提案：今回に合わせた案</span><span>要検証：実機・本番設定で未確認</span></div>')
    index += '<div class="buttons"><a class="button primary" href="workflow.html#actions">追加調査・試作の例を見る →</a><a class="button" href="history.html">改訂履歴を見る</a></div>'
    add('index','はじめに','doukinの技術と運用を、<br>検討するための調査ノート。','認証・権限・基盤・データ・費用を比較し、条件付きの推奨、その理由、運用例と追加検証の観点をまとめます。',index,'book','はじめに',kicker='DOUKIN / FIELD GUIDE 01',related=('compare','workflow','sources'))

    auth = theme_guide('auth')
    auth += section('journey','参加から復旧までの流れ',diagram([
        ('person','参加を確認','運営者が既知の同期か確認'),('key','個別に招待','期限付き・１回限り'),('shield','会員として利用','ログイン＋会員状態を確認'),('steps','復旧・失効','元の履歴に戻す／利用を止める')], '設計提案：会社の名簿・会社SSOに頼らず、既知の私的な連絡手段や対面で確認します。') + note('ログインと参加資格は、別々に確認しよう','GoogleやGitHubでログインできても、「この集まりの同期」とは限りません。認証後にも招待・承認を確認し、未承認なら共有データを返さない設計です。','orange'))
    auth += section('methods','４つの入口を見くらべよう', table(['方法','よいところ','採用前に確かめること'],[
        ('<a href="plan-n1.html">N1 パスキー</a>','アプリでメールもパスワードも持たない設計が可能。','端末対応・復旧・ライブラリのWorkers互換性。'+ref('S01','S02')),
        ('<a href="plan-n2.html">N2 ユーザー名＋パスワード</a>','Clerkに認証を任せる候補。','メール・電話なしの登録、新端末、管理者復旧。本番ドメインと有料機能。'+ref('S03','S05','S47')),
        ('<a href="plan-p1.html">P1 個人OAuth</a>','個人の認証サービスを使い、パスワード管理を委ねられる。','個人アカウントの利用を許容するか。認証基盤にメール等が渡る可能性。'),
        ('<a href="plan-p2.html">P2 個人メール</a>','OTPやリンクでログインし、メールを復旧の入口にできる。','外部SMTP、送信ドメイン、配信上限、メール自体を失った場合。'+ref('S29','S58'))], '同じ軸で比べる、ログインの入口'))
    auth += section('recovery','メールなしなら、復旧を先に決めよう',steps([
        ('別の認証手段を準備する','パスキーを複数登録する、１回限りの復旧コードを用意するなどの案。すべてを同じ端末だけに置かないようにします。'),
        ('本人を確かめて、元の会員へ戻す','表示名の一致だけで引き継がせません。既知の本人への再確認と、権限のある運営者の操作を組み合わせる案です。'),
        ('古い入口を閉じる','古いセッション・招待・復旧コード等を失効し、必要ならパスキーも登録し直します。復旧に使った認証情報をログへ残さないようにします。')]) + '<p>期限付き・単回利用・推測困難な復旧トークン等はOWASPのガイドにも沿う方針。復旧窓口の担当と対応待ち時間は、チームで決める提案です。'+ref('S61')+'</p>')
    auth += section('traps','ここは、名前だけで判断しないでね',
        details('「匿名ログイン＋パスキー」で完全にメール不要になる？','<p>Supabaseの匿名ログインだけでは、サインアウト・ブラウザデータ削除・別端末から同じ履歴へ戻れません。パスキーは実験的機能で、登録には確認済みの非匿名ユーザーが必要。匿名ユーザーには先にメールか電話の関連付けが求められます。</p>'+ref('S08','S11')) +
        details('ユーザー名が使えれば、メールなしで全部できる？','<p>Clerkの統合されたsign-in-or-upフローは、ユーザー名のみの登録に対応していません。別の登録フローを検討し、新端末ではDevice Trustがメール等を要求しないかも確認します。Better AuthのUsernameプラグインも、標準登録APIにはメールが必要です。</p>'+ref('S48','S47','S12')) +
        details('共通パスワードや、全員共通の招待URLは？','<p>個人の記録を持つ今回の用途では、個別の本人識別・復旧・失効が難しくなります。個別IDと個別招待を採用する提案です。URLを知っていることだけを、長期の参加資格にしません。</p>'))
    auth += note('要検証：実機で通す６つの場面','登録／別端末／認証手段の紛失／元の履歴への復旧／退会後のアクセス／期限切れ招待。iOS SafariとAndroid Chromeの両方で確認します。','orange')
    add('auth','認証・招待・復旧','どの認証を選び、<br>どう招待・復旧する？','まず個別招待＋パスキーを試す理由、個人OAuth等へ切り替える条件、参加から紛失・退会までの運用案です。',auth,'key',issue='Issue #3',kicker='01 / IDENTITY',related=('privacy','plan-n1','plan-p1'))

    privacy = theme_guide('privacy')
    privacy += section('scope','見られる範囲の初期案',table(['データ','本人','承認済みの同期'],[
        ('トレーニング記録','初期非公開。閲覧・編集・削除','本人が同期共有を選んだ記録だけ閲覧'),
        ('体重・身体情報','任意入力。初期は非公開を提案','本人が明示的に共有した範囲のみ'),
        ('プロフィール','自分の必要項目を管理','共有用ニックネーム等、必要な項目のみ'),
        ('認証・復旧情報','必要な管理操作のみ','閲覧不可'),
        ('招待・会員状態','運営権限を持つ人が変更','他人の参加資格を変更不可')], '設計提案：未ログイン・未承認・失効済みの人には、これらのデータを公開しません') + '<p class="subtle">体重の初期非公開や、記録の共有初期値はまだ提案。MVPの範囲と合わせてIssue #2・#3で決めます。運営者が管理上アクセスできる範囲も、利用者への説明とセットで決めよう。</p>')
    privacy += section('boundary','守る場所は、構成で変わります',grid(
        card('Workers＋D1','APIで会員状態・所有者・公開範囲を毎回確認。ブラウザから渡された会員IDをそのまま信用せず、検証済みのセッションから本人を特定します。','shield'),
        card('Supabase＋RLS','DBの行ごとのポリシーで閲覧と変更を制御。公開対象テーブルのRLSを確認し、ブラウザへ管理用キーを配らない設計です。'+ref('S13'),'db'),
        card('Firestore＋Rules','ドキュメントごとに許可を判定。Rulesで体重のフィールドだけを隠して返すことはできないので、共有データと分けます。'+ref('S14'),'db'),
        card('Accessの入口制限','サイトに入る人を限定できます。各人の記録の所有権や、別URLで到達するDB・画像の保護も必要です。'+ref('S16'),'key')))
    privacy += section('data-split','共有する箱と、自分だけの箱',diagram([
        ('person','会員','状態・役割を運営側で管理'),('book','トレーニング','所有者＋共有範囲を保存'),('shield','体重','別テーブル／別文書で管理')], 'データの分け方の提案。体重が共有記録のレスポンスに混ざらないようにします。') + note('失効は、いま持っているログインにも効かせよう','Supabaseではサインアウト後もJWTが期限まで有効です。会員状態をDBやAPIで確認し、失効から何分以内に読めなくするかを定義します。匿名ユーザーもauthenticatedロールになるため、ログイン済みだけで承認済みとは見なしません。'+ref('S15','S08'),'orange'))
    privacy += section('verify','確かめるときの、４人のテスト',bullets(
        '会員A：自分の記録は変更できる。他人の記録は変更できない。',
        '会員B：Aが共有した記録だけ見える。非公開の体重は直接APIを呼んでも読めない。',
        '未承認の人：ログインできても、共有データは読めない。',
        '失効済みの人：手元に古いCookieやJWTがあっても、決めた時間内に読めなくなる。') + details('PWAと画像も忘れずに','<p>端末に体重・認証情報・他人の記録を安易に永続キャッシュしない方針です。ログアウト後の表示、共有端末、オフラインの残存を確認。非公開の画像には認可付き配信や短い期限のURLを使い、公開バケットへ置かない設計を検討します。</p>'))
    add('privacy','公開範囲・権限','何を共有し、<br>どこで権限を守る？','初期非公開と明示共有を推奨する理由、API・DBの設計案、退会時の失効を検証する観点です。',privacy,'shield',issue='Issue #3',kicker='02 / PRIVACY',related=('auth','data','workflow'))

    platform = theme_guide('platform')
    platform += section('roles','アプリをつくる４つの部品',diagram([
        ('book','画面','React・TypeScript・Vite'),('key','認証','パスキー／Clerk／Auth'),('cloud','API・権限','Workers／DBの認可'),('db','保存','D1／Postgres／Firestore')], '役割の地図。すべての構成に独立したAPIサーバーが必要なわけではありません。') + definition([
        ('React＋Vite案','画面をビルドして静的に配信。記録の取得はAPIや管理型DBを利用。公開検索やSSRが必須でない今回の候補です。'),
        ('Next.js案','チームの経験があるなら比較対象。静的exportと、SSR／Server Actions等を動かす構成を分けて検討します。'),
        ('Hono案','Workers上のAPIを整理する候補。招待・復旧・権限が自動で完成するわけではありません。')]))
    platform += section('hosts','配信先を見くらべよう',table(['配信先','今回の使い方','気をつける条件'],[
        ('Workers Static Assets','静的な画面を配信。必要なときだけWorkers API。','静的配信と動的処理の枠を区別。Cloudflareは新規案件にWorkersを案内。'+ref('S18','S19')),
        ('Cloudflare Pages','既存経験がある場合の代替。','Pages FunctionsはWorkers枠。500ビルド/月とWorkers Builds 3,000分/月は別。'+ref('S21','S22','S23')),
        ('Firebase Hosting','F1の静的画面を配信。','App Hostingとは別。Sparkの転送枠と上限到達時の停止を確認。'+ref('S32','S34')),
        ('Vercel Hobby','現在の無料Git連携先には選ばない提案。','Organizationのprivate repoをGit連携でデプロイ不可。個人・非商用、コミット作成者にも条件。'+ref('S37','S38'))], 'GitHub Organizationのprivateリポジトリを維持する前提で比較'))
    platform += section('runtime','組み合わせの境目を確認しよう',grid(
        card('Next.jsをWorkersへ','Cloudflareの公式経路はOpenNext。Nodeと同じ実行環境だとは見なさず、使う機能と互換性をプレビューで確認します。'+ref('S17'),'cloud'),
        card('認証を入れ替えるとき','ClerkのIDはアプリの会員と関連付けが必要。独自認証を入れただけでは、SupabaseのRLSが自動でその本人を認識しません。信頼するトークンの設計が要ります。','key')))
    platform += section('team','３人で保守するための、小さな約束',steps([
        ('個人アカウントで、必要な権限だけ','開発・運営にも会社SSOや会社メールを使いません。共通ログインを避け、保守担当を複数人にする案です。管理席数や既存の無料枠消費を確認します。'),
        ('プレビューは、検証データへ','本番の会員・体重を開発プレビューへつなぎません。OAuthの戻り先やパスキーのRP IDも環境ごとに確認します。'),
        ('サービスを選ぶ前に、小さく動かす','ビルドが通るだけでなく、招待・権限・失効・復旧・DB復元まで通して比較。WorkersのCPUやDB読取回数は実測します。')]))
    add('platform','技術スタック・配信','何で作り、<br>どうリリースする？','React＋Viteと静的配信を推奨する理由、Next.js等を選ぶ条件、３人で安全に変更を届ける手順です。',platform,'cloud',issue='Issue #4',kicker='03 / PLATFORM',related=('compare','cost','data'))

    data = theme_guide('data')
    data += section('database','３つの保存先を見くらべよう',table(['DB','得意な整理','今回、必要な設計'],[
        ('D1 / SQLite系','会員・記録・セットをSQLで扱う。','Workers APIで権限を確認。1 DB 500MB、走査行数、インデックスを意識。'+ref('S24','S25')),
        ('Supabase / Postgres','関係のあるデータをSQLとRLSで扱う。','RLS、スキーマ移行、会員状態、体重の分離。DB枠とディスクを区別。'+ref('S13','S40')),
        ('Firestore','文書単位で画面に必要な情報を扱う。','Rulesとクエリを一緒に設計。JOIN前提にせず、重複データの更新・読取数を見積もる。'+ref('S14','S42'))], '保存容量だけでは決まらない、DBの選び方'))
    data += section('pictures','写真を入れると、ここが増えるよ',grid(
        card('保存する量','30人が毎日0.5MBの写真を１枚で、月0.45GB増加。３か月保持すると1.35GB。圧縮後のサイズと保持期間を決めよう。','db'),
        card('見てもらう量','当月の写真を１枚あたり全体で10回配信すると4.5GB/月。過去の写真の再閲覧はさらに別です。','share')) + note('画像サービスの「無料」にも条件があります','R2は無料利用量付きの従量課金サブスクリプション。Firebase StorageはBlazeの課金設定が必要。Supabase Storageの1GB枠も、転送やバックアップ先とは別に考えよう。'+ref('S35','S36','S33','S26'),'orange') + '<p>画像追加時は、最大サイズ・許可する形式・アップロード回数・非公開の配信経路を決める提案です。位置情報など不要な付加情報も残さない方針を検討します。</p>')
    data += section('backup','戻せるところまでが、バックアップ',table(['候補','公式の機能・制約','運用の提案'],[
        ('D1 Free','Time Travelは７日。外部退避とは別。'+ref('S25'),'変更前に復元点を確認。アカウント喪失にも備えるなら別の保管先を検討。'),
        ('Supabase Free','CLI等の定期エクスポートを推奨。DBバックアップに画像本体は含まれない。'+ref('S43'),'DBと画像を別々に退避。検証環境で両方の復元を試す。'),
        ('Firestore Spark','PITR・標準バックアップ・復元に無料枠なし。'+ref('S31'),'課金なしで使うなら、代替の退避・復元方法と読取費用の影響を検証。')], '無料プランでも「何を、どこまで戻せるか」を確認') + '<p>D1は実行中のエクスポートが他のDB要求を止めます。利用の少ない時間帯に実施し、所要時間を試作で測る運用案です。FTS等の仮想テーブルを含むDBはエクスポート非対応なので、追加時は退避方法も見直します。'+ref('S63')+'</p>')
    data += section('operation','小さく運用するための約束',steps([
        ('なくしてよい時間を決める','最後の保存から何時間分の記録を失っても許容するか、何時間で戻すか。必要な頻度・保持日数・復元担当を決めます。'),
        ('削除したデータを、戻しっぱなしにしない','退会時の記録・画像・認証情報・関連リアクションを整理。バックアップの保持期限と、復元後に再削除する手順も残します。'),
        ('取得は少しずつ、測って調整する','カーソルでページ分割し、必要な項目だけを取得。所有者・日付などのインデックスを用意し、全件取得や不要な常時購読を避ける案です。')]) + details('D1とFirestoreで、数え方が違うところ','<p>D1は返した行数ではなく、クエリが走査した行数が大切。インデックス更新も書込に加わります。Firestoreは文書読取に加え、Rulesの参照・リアルタイム購読・再接続や一部クエリのインデックス読取も確認します。</p>'+ref('S24','S42')) + '<p class="subtle">実際の会員データやバックアップは、Gitリポジトリ・Issue・このHTML資料へ入れません。</p>')
    add('data','データ・画像・復元','どこへ保存し、<br>どう復元する？','SQLとテキスト中心を推奨する理由、写真を追加する条件、毎日の退避と復元・削除の運用案です。',data,'db',issue='Issue #4・関連 #2 / #3',kicker='04 / DATA',related=('cost','privacy','workflow'))

    from guide_costs import cost_body, calculator_body
    add('cost','無料枠・費用','無料をどう維持し、<br>いつ見直す？','写真なしで始める理由、利用率70%・85%での対処案、有料化や構成変更を相談する条件です。',cost_body(),'cost',issue='Issue #4',kicker='05 / COST',related=('compare','data','sharing'))
    add('calculator','利用量の計算機','何人で、どのくらい？<br>使い方を試算しよう。','人数・記録・写真量を変えると、保存量と転送量はどう変わるかな。',calculator_body(),'cost',issue='Issue #4',kicker='06 / CALCULATOR',related=('cost','data','compare'))

    from guide_plans import add_plan_pages
    add_plan_pages(add)

    add_workflow_and_sharing(add)
    add_sources(add, bibliography)
    return pages


def add_workflow_and_sharing(add):
    workflow = note('N1を優先して検証する場合の調査案。','５テーマの推奨を比較できる形にするため、招待・記録・失効・復旧・DB復元をつなぐ試作を例にします。下の役割や成果物は分担を考える材料です。<strong>実施予定、実際の担当者、採用結果は記載しません。</strong>')
    workflow += section('actions', '追加調査・試作で整理したいもの', table(['役割の例', '検証用に作るものの例', '比較の観点'], [
        ('認証・権限担当／代行１人', '<a href="auth.html#next">N1の通し試作</a>と<a href="privacy.html#next">４者の権限テスト</a>。#3へ結果を記録。', 'スマホ２種で復旧、旧セッションの失効、非公開データの拒否。'),
        ('基盤・データ担当／代行１人', '<a href="platform.html#next">本番・検証の分離</a>と<a href="data.html#next">毎日の退避・復元手順</a>。#4へ結果を記録。', '再現可能なビルド、代行者による復元、削除・失効の再適用。'),
        ('運用担当／代行１人', '<a href="cost.html#next">費用項目・監視と制限の対応例</a>。認証の本人確認と復旧を交代で試す。', '確認する指標、70%／85%時の対応例、有料化を比較する条件。')], '３人で分担する場合を仮定した役割例です。実際の担当者名・期限・予算は記載しません')
        + '<p>試作を始める前に相談するのは、記録の初期非公開、写真を後にする案、管理者復旧を２人で担えるか、バックアップ先と許容損失24時間／復旧１日の目標です。個人OAuthを代替として許容するかも確認します。未合意の項目はダミーデータで検証し、実会員の運用へ持ち込みません。</p>')
    workflow += section('order','進める順序は、この４歩',steps([
        ('比較条件を置く','参加者の範囲、体重と記録の公開範囲、メール不要の意味、無料の定義を仮定します。会社アカウント不使用も比較の条件として扱い、確定要件とは表現しません。'),
        ('N1を試作の例にする','招待・記録・権限・失効・復旧・バックアップ復元をつなぐ検証例を整理します。各テーマの確認観点から、測定項目を揃える案です。'),
        ('不合格の条件で代替を選ぶ','認証保守が難しく個人OAuthを許容できればP1、メールなしを維持するならN2の成立条件を確認。無料枠に収まらなければ機能範囲か予算を相談します。'),
        ('調査の要点を残す','推奨の理由、候補ごとの制約、代替案、追加検証の観点をまとめます。採用の判断や確定した要件は、この公開資料へ転記しません。')]))
    workflow += section('issues','Sub-issueは、必要な単位で分けよう',table(['親Issue','子の作業案','分ける目的'],[
        ('<a href="https://github.com/chuka57/doukin/issues/3">#3 認証・公開範囲</a>','A：前提・権限<br>B：メールなし認証・復旧','誰を参加させ、どう本人とデータを守るか。'),
        ('<a href="https://github.com/chuka57/doukin/issues/4">#4 基盤・費用</a>','C：配信・開発環境<br>D：DB・画像・復元<br>E：全体の小さな試作','無料条件を満たし、運用まで続けられるか。'),
        ('<a href="https://github.com/chuka57/doukin/issues/2">#2 MVP</a>','写真・体重・PWA等の範囲を相談','A/Dへ前提を共有。#3/#4でMVPを決め直さない。')], 'A〜Eは相談用のラベル。まだ実際のIssue番号ではありません') + '<p>#3と#4は同じ階層に残します。横断するEは親を#4、関連先を#3にする案。親子関係と、「どの結果を待つか」の依存関係は分けて表そう。</p>'+ref('S55','S56') +
        details('A：参加資格・公開範囲を整理する',definition([('親 / 関連','#3 / #2、B、D、E'),('調べること','同期の範囲、承認者、私的な招待経路、離脱、復旧の本人確認、権限表。メール不要がアプリ入力だけか、認証基盤の保有までかも確認。'),('完了の目安','比較の仮定・提案・追加検証の点を区別した権限表ができ、BとDが同じ前提で比較できる。')])) +
        details('B：メールなし認証・復旧を検証する',definition([('親 / 関連','#3 / A、C、E'),('調べること','最初にN1のWorkers互換性・紛失復旧を試す。失敗時は条件に応じてN2の登録・Device Trust・管理者復旧、またはP1の個人OAuthを確認。'),('完了の目安','招待・登録・新端末・失効・復旧・保存属性・費用を説明できる。実測結果と不合格の理由から、試作を継続する案か代替案を決められる。')])) +
        details('C：ホスティング・共同開発の条件を確認する',definition([('親 / 関連','#4 / B、D、E'),('調べること','Workers/Pages/Firebase/Vercel、React/ViteとNext.jsの違い、org private Git連携、３人の管理権限、CPUとビルド枠。'),('完了の目安','現在のGitHub構成を維持できる候補と、費用や運用が変わる候補が分かる。プレビューと本番データを分離できる。')])) +
        details('D：DB・画像・バックアップを比較する',definition([('親 / 関連','#4 / #2、A、C、E'),('調べること','30/50人のテキストと写真、走査/文書読取、認可、復元、退会と再削除、保管先、無料プランと従量課金の違い。'),('完了の目安','仮定と式、上限、運用で補うことが整理され、画像とバックアップを含めた継続条件を説明できる。')])) +
        details('E：認証から記録まで、小さく通す',definition([('親 / 関連','#4 / #3、A〜D'),('着手条件','優先はN1。小さな認証検証が通ったら接続し、代替案に切り替えた場合はその認証を先に検証。ダミーの会員・記録を使い、実際の体重などを持ち込まない。'),('完了の目安','構成、バージョン、端末、通過/失敗/未確認、CPU・利用量、復元結果、費用条件を記録し、採用を相談できる。')])) )
    workflow += section('prototype','小さな試作で確認すること',bullets(
        '未招待・期限切れ・使用済み・同時引換の招待から、データ閲覧に進めない。',
        '会社アカウントを使わず登録・新端末ログイン・紛失復旧を完了できる。',
        '会員A/B、未承認、失効済みで、APIを直接呼んでも権限が守られる。',
        '旧JWT/Cookieがある場合の失効と、ブラウザデータ削除後の履歴復旧ができる。',
        'iOS SafariとAndroid Chrome、必要ならPWAで、登録・認証・復旧を確認。',
        'CPU・DB読書き・転送を測り、バックアップから復元し、削除済みデータの扱いも確認。'))
    workflow += section('record','議論を、あとからたどれるように',definition([
        ('Issueのコメント','質問、追加調査、試作結果、判断の要点。該当ページや変更PRへリンク。'),
        ('HTML資料','最新版の比較、前提、出典、未解決事項。リポジトリ内で更新し、PRでレビュー。'),
        ('改訂履歴','この資料で何を調べ直し、何を追記したかの短い要約。詳しい差分・レビューは関連PRから辿ります。確定事項や採用の議事録は載せません。')]) + '<p>ここでは比較結果と追加検証の観点を共有します。実際の採用結果・確定要件・運用体制の記録は、このリポジトリの対象外です。</p>')
    add('workflow','検討の進め方','調査と試作を、<br>どう整理する？','Issue #3・#4を背景にした調査項目・役割例・検証の進め方を整理します。実施予定や採用結果の記録ではありません。',workflow,'steps','相談と資料のこと',kicker='WORKFLOW / DISCUSS',related=('compare','privacy','history'))

    sharing = note('公開するのは、調査と検討の材料。','原稿と変更履歴はこのリポジトリで管理します。<strong>アプリの確定事項や採用結果は掲載しません。</strong>資料の版と変更要約は<a href="history.html">改訂履歴</a>から、詳細な差分・レビューは関連PRから確認できます。')
    sharing += section('choices','２つの共有方法から選べるよ',grid(
        card('GitHub Pagesで読む','PublicリポジトリからHTMLを配信する方法。GitHub内で資料を更新し、同じURLから最新版を読めます。資料とソースは一般公開になります。','book','https://chuka57.github.io/doukin-docs/','今回の配信方法'),
        card('URLで読む：認証付き配信','Workers Static Assets＋Cloudflare Accessを候補に。スマホから読みやすく、更新先を１つにできます。設定・支払情報・ログイン連携が必要です。','cloud','sharing.html#web','未設定の候補')) + '<p>GitHubの通常ファイル画面ではHTMLはソース表示になります。Wikiも任意のCSS/JavaScriptを使うサイトの配信先にはなりません。HTML本体と共通assetsをセットで扱おう。</p>'+ref('S45','S44'))
    sharing += section('web','URLで共有する場合の構成案',diagram([
        ('book','GitHub','HTML・履歴・PRを管理'),('cloud','Static Assets','標準workers.devで配信'),('shield','Access','許可した人だけ閲覧')], '配信の考え方。現時点では設定・デプロイしていません。') + definition([
        ('無料の条件','静的配信は無料・リクエスト無制限。Accessは最初の50人まで無料という案内です。標準workers.devを保護できるので、資料用の独自ドメイン購入は必須にしない案。'+ref('S19','S10','S52','S53')),
        ('支払情報','Zero Trust Freeでも初期設定の支払情報入力が必要と公式に明記。無料プランでは課金されない案内と、支払情報不要は別です。'+ref('S50')),
        ('閲覧者の認証','開発メンバー個人のGitHubログインを候補に。組織・チームやメールの読取権限を求めるため、メール情報を一切渡さない方式ではありません。会社アカウントは使いません。'+ref('S51')),
        ('公開範囲','GitHubのリポジトリ権限は自動でサイトに引き継がれません。Accessの許可対象を別に設定し、実際に閲覧してよいメンバーと対応させます。'),
        ('保護の確認','本番URLだけでなく、Version/Preview/Deployment URL等も対象。内容を置く前に保護し、未ログイン・非メンバー・失効済みで拒否されるか確認。'+ref('S52','S53'))]) + note('資料とアプリのログインは、別々に検討します','開発者の資料閲覧に個人GitHubを使う案でも、アプリの参加者全員にGitHubを要求する意味ではありません。アプリの「個人メール以外を優先する」条件はそのままです。','orange'))
    sharing += section('github','GitHubの機能と、今回の使い分け',table(['機能','できること','今回の注意点'],[
        ('通常PR','比較資料をレビューし、履歴を残す。','資料のマージと、技術採用の合意を区別。'),
        ('Draft PR','作業中として共有する。','org privateのGitHub Freeでは使えない。Team/Enterprise Cloud等の条件を確認。現在の契約は未確認。'+ref('S54')),
        ('Wiki','Markdown等の文書を整理する。','private Wikiには対応プランが必要。公開範囲はrepoに従い、リンク限定やページ別ACLはない。'+ref('S44')),
        ('GitHub Pages','HTMLサイトを配信する。','private repoだからサイトもprivateとは限らない。組織サイトの非公開配信にはEnterprise Cloudの条件。'+ref('S46'))], 'GitHub上での管理と、HTMLの配信を分けて考える'))
    sharing += section('updates','更新するときの、お約束',steps([
        ('調査資料を更新する','テーマ別原稿と、content/revisions.jsonの版・改訂日・短い変更要約・PR番号を更新し、HTMLを生成します。出典確認日は実際に再確認した場合だけ更新。採用結果・確定要件は転記しません。'),
        ('PRでレビューする','料金・上限は公式情報を再確認。別モデルのレビューも補助にし、最後は根拠と実機検証で判断します。'),
        ('入口を一定に保つ','index.htmlとテーマのURLを維持し、Issueから該当ページへリンク。複数の場所に本文をコピーして手動更新しない方針です。')]))
    add('sharing','資料の共有・更新','読みやすいまま、<br>みんなに届けよう。','GitHubで管理しながら、HTMLをブラウザで読めるようにする方法と、更新のルール案です。',sharing,'share','相談と資料のこと',issue='資料の共有方法',kicker='SHARING / HANDBOOK',related=('index','workflow','sources'))


def add_sources(add, bibliography):
    body = note('根拠と、まだ確かめていないことを残そう。','料金・機能は提供元の公式文書を優先。設計の考え方はOWASP等の専門ガイドも参照しています。<strong>公式確認は、今回のアプリで動作確認済みという意味ではありません。</strong>')
    body += section('reading','この資料の読み方',definition([
        ('確認日','2026-10-30（日本時間）。料金はUSD、税・為替・ドメイン費は別。サービスの情報は比較に使う時点でも再確認します。'),
        ('公式確認','公式の料金・制限・機能説明に記載がある事項。提供元の記述が分かれる場合は、そのまま条件と不確実さを記載します。'),
        ('設計提案','今回の用途と条件に合わせた判断。N1を先に試す順序、初期非公開、招待24時間、日次７世代の退避、許容損失24時間／復旧１日、70%／85%の対応目安も提案です。サービスの仕様・保証値やチームの合意事項ではありません。'),
        ('要検証','組み合わせの実動作、本番契約の画面、端末や負荷など。ベンダーの説明やモデルのレビューだけでは確認済みにしません。')]))
    body += section('review','別モデルのレビューで見直したところ', '<p><strong>GPT-6.1 Terraを指定した別エージェント</strong>へ独立レビューを依頼し、公式情報と照合。主に無料条件と認証の成立条件を確認し、次の修正を反映しました。モデルの判断自体を一次情報としては扱いません。</p>' + table(['対象','反映したこと'],[
        ('Clerkの新端末','パスワードだけで必ず使える、という断定を修正。Device Trustとメール・電話なしの挙動を試作の合格条件に。'+ref('S47')),
        ('Clerkの登録・復旧','ユーザー名のみの統合フロー制約、管理APIの復旧と安全な本人確認、本番DNS・有料機能を明記。'+ref('S48','S49','S05')),
        ('Supabaseの容量','500MBのDB無料枠と2GBのディスクを区別。組織単位のFair Useと、転送超過後の猶予を補足。'+ref('S40','S59','S27')),
        ('Supabaseのメール配信','外部SMTPだけが配信方法であるような一般論を修正。Send Email Hookもあると補足し、P2は外部SMTPを選ぶ案として記述。'+ref('S62')),
        ('無料でも必要な登録','Access Freeの支払情報、R2のサブスク、Firebase Storage/App HostingのBlaze条件を目立つ位置へ。'+ref('S50','S36','S33','S34'))], '調査レビュー：2026-10-30 JST') + '<p class="subtle">再確認した主な対象：Workers/D1、Clerk、Supabase Auth・DB・転送、Firestore、Firebase Hosting/Storage、Vercel Git連携、R2、Access。実アプリの認証・課金画面・復元操作の試作は未実施です。</p>')
    body += section('glossary','よく出てくる言葉',definition([
        ('認証 / 認可','認証は誰かを確かめること。認可は、その人が何をしてよいかを判断すること。'),
        ('パスキー / RP ID','端末側の認証操作と公開鍵を使うログイン手段。RP IDはどのサービス向けの資格情報かを区別するドメイン識別子。'),
        ('OAuth','外部サービスの認証連携で使われる仕組み。今回は個人の認証サービスを利用するログイン案として扱います。'),
        ('RLS / Security Rules','DBやサービス側でデータの読書きを制御する機能。UIで表示を隠すだけの処理とは別です。'),
        ('JWT / セッション','ログイン状態を示す情報や仕組み。署名の確認、期限、失効の反映、会員状態の確認が必要です。'),
        ('MAU / MRU','MAUは月間アクティブユーザー。ClerkのMRUは登録後に戻ってくるユーザーの独自指標。料金比較で同じ数え方と見なさないでね。'),
        ('CPU / 経過時間','CPUは処理に使う時間。通信を待つ時間を含む、操作全体の経過時間とは異なります。'),
        ('走査行 / 返却行','DBが探すために読んだ行と、利用者へ返した行。20件返すだけでも、全件を走査している場合があります。'),
        ('GB / GiB','十進と二進の容量単位。概算はMB/GB、Firestoreの公式枠はGiB表記を維持しています。'),
        ('SMTP / DNS','SMTPはメールを送る仕組み。DNSはドメインの接続先などを管理する設定。送信ドメインの確認にも使います。'),
        ('PITR / Time Travel','ある時点へデータを戻す仕組み。対象期間・プラン・戻せるデータはサービスごとに異なります。'),
        ('PWA / SSR','PWAはWebアプリをインストール等に対応させる仕組み。SSRはサーバーで画面のHTMLを生成する方式。本資料では利用する場合・省く場合を比較し、要件の確定状況は記載しません。')]))
    groups = {'認証と権限':[], 'Cloudflare':[], 'Supabase':[], 'Firebase':[], 'GitHub・Vercel':[]}
    for key, (title, url, claim) in sorted(bibliography.items()):
        if any(s in url for s in ['clerk.com','simplewebauthn','better-auth','owasp']): group = '認証と権限'
        elif 'cloudflare.com' in url: group = 'Cloudflare'
        elif 'supabase.com' in url: group = 'Supabase'
        elif 'firebase.google.com' in url: group = 'Firebase'
        else: group = 'GitHub・Vercel'
        groups[group].append(f'<li id="source-{key}"><a href="{escape(url, quote=True)}">{key} · {escape(title)} ↗</a><small>{escape(claim)}</small></li>')
    body += section('bibliography','一次情報の一覧', '<p>各ページのS番号から、そのページで使った出典を直接ひらけます。こちらは一覧です。</p>' + ''.join(details(f'{group}（{len(items)}件）','<ul class="source-index">'+''.join(items)+'</ul>') for group, items in groups.items()))
    body += section('context','今回の背景と、確認の範囲', '<p>目的と調査範囲は<a href="https://github.com/chuka57/doukin/issues/3">Issue #3</a>・<a href="https://github.com/chuka57/doukin/issues/4">#4</a>、MVPは<a href="https://github.com/chuka57/doukin/issues/2">#2</a>を参照しています。開発者３人・要件・運用の背景は、背景資料の<a href="https://github.com/chuka57/doukin/blob/d46cd222cff8051969818be0158e8cd126ce9b8d/docs/requirements.md">PR #1の要件案（特定コミット）</a>も参照。本資料には確定仕様として転記しません。</p><p>ここにまとめるのは文書調査と検証の観点です。アプリの採用・契約・本番設定や実施状況は、本資料には記載しません。</p>')
    add('sources','出典・用語・レビュー','確かめたことを、<br>たどれる形に。','出典、言葉の意味、レビューで見直した点を、ひとつの場所にまとめています。',body,'book','相談と資料のこと',issue='調査の根拠',kicker='REFERENCE / SOURCES',related=('compare','workflow','index'))
