"""Free-tier facts and a separate, explicitly hypothetical usage calculator."""
from guide_ui import section, note, card, grid, bullets, details, table, definition, ref


def cost_body():
    body = note('０円にも、いくつか種類があります。','月額０円のプラン、課金契約に含まれる無料利用量、運用全体の支出０円。<strong>この３つを分ける</strong>と、あとで困りにくくなるよ。料金はUSD。税・為替・ドメイン費は別です。')
    body += section('types','無料の条件を３つに分けよう',grid(
        card('無料プランの範囲で使う','Workers Free・D1 Free、Supabase Free、Firebase Sparkなど。容量のほかに、機能制限・停止・復元の条件があります。','leaf'),
        card('無料利用量のある課金契約','R2、FirebaseのBlazeが必要な機能など。無料枠を超えると支出につながるため、支払登録なしの案とは分けて比較します。','cost')) + note('本体が無料でも、ここを足してね','Clerk本番の所有ドメイン、メール認証のSMTP・送信ドメイン、画像、バックアップ先、開発と本番の複数環境。運営アカウントは会社のものを使わない前提です。','orange'))
    body += section('limits','サービスごとの枠と、超えたとき',
        '<p>必要なサービスをひらいて確認しよう。<strong>小さな人数でも、CPU・機能・契約条件が先に制約になることがあります。</strong></p>' +
        details('Cloudflare：静的配信・Workers・D1',table(['対象','Freeの主な条件','上限・補足'],[
            ('Static Assets','静的リクエストは無料・回数制限なし。保存追加料なし。','Workerを先に実行する経路は動的処理の枠を利用。'+ref('S19')),
            ('Workers','100,000リクエスト/日、CPU 10ms/呼出、メモリ128MB。','超過で処理が失敗し得る。CPU時間は通信待ちを含む経過時間とは別。'+ref('S20')),
            ('D1','500万行読取/日、10万行書込/日。1 DB 500MB、全体5GB、10 DB。','日次読書き上限でクエリエラー。返却件数ではなく走査数。インデックス更新も書込。'+ref('S24','S25')),
            ('D1復元','Time Travel ７日。','外部バックアップとは別。Paidの30日と混同しない。'+ref('S25')),
            ('Workers Builds','3,000ビルド分/月、同時１、20分タイムアウト。','Pagesの500ビルド/月とは別。PR検証分も含める。'+ref('S21','S22'))], 'Cloudflare：公式文書で確認') + '<p>run_worker_firstを使うFree経路は上限を超えると429となり、静的配信に戻って助けてくれるわけではありません。パスキー検証などのCPU負荷は実測が必要です。</p>'+ref('S19')) +
        details('Supabase：DB・認証・画像・転送',table(['対象','Freeの主な条件','上限・補足'],[
            ('DB / Auth','DB 500MB、50,000 MAU。','非活動１週間で停止の案内。MAUは月間利用者の指標。'+ref('S26')),
            ('Storage / 転送','ファイル1GB、非キャッシュ5GB＋キャッシュ5GB/月。','別々の転送枠。自由に融通できる合計10GBとして扱わない。'+ref('S26','S27')),
            ('プロジェクト','アクティブなFreeは２個。','Owner/Adminの他の利用も関係。組織ごとに２個ずつとは仮定しない。'+ref('S28')),
            ('標準SMTP','チームに属するメール宛てのみ。２通/時。','P2は外部SMTPで本番配信する案。代替にSend Email Hookもある。Auth側にも制限あり。'+ref('S29','S58','S62'))], 'Supabase：公式文書で確認') + note('500MBと2GBは、別の数字だよ','500MBはDBの無料利用枠。2GBはWAL等も含む各プロジェクトの固定ディスク容量で、95%使用時にread-onlyの制御があります。500MBを超えた瞬間に同じ制御になるとは書けません。'+ref('S40'),'orange') + '<p>料金表は500MB/projectと案内する一方、現行のDB使用量説明には組織合計・期間平均によるFair Use判定もあります。ダッシュボードと当時の条件を確認してください。転送等の超過は通知・猶予後に制限され得ます。Freeが自動で従量課金に変わる、とも即時停止する、とも断定しません。</p>'+ref('S26','S27','S40','S59')) +
        details('Clerk：無料の認証と、本番の条件',definition([
            ('Hobbyの枠','50,000 MRU/アプリ、管理画面３席、セッション期間７日固定、ログ１日。カード不要の案内。'+ref('S04')),
            ('MRUとは','登録後、少なくとも24時間後に戻って当月に利用するユーザーの指標。MAUとは数え方が違います。超過は１か月の猶予後、Proが必要という案内。'+ref('S04')),
            ('本番の条件','所有ドメインとDNSを設定する権限が必要。未所有ならドメインの取得費を含めて比較。'+ref('S05')),
            ('有料機能','本番パスキー・MFA・Allowlist等はHobbyの機能と分けて確認。開発環境で試せることだけでは無料の本番採用を判断しません。'+ref('S04','S06','S30'))])) +
        details('Firebase：SparkとBlazeの境目',table(['対象','主な無料枠・条件','上限・補足'],[
            ('Firestore','1 GiB保存、50,000読取/日、20,000書込/日、20,000削除/日、10 GiB転送/月。','無料対象DBは１つ。PITR・バックアップ・復元・TTL削除は課金有効化が必要。'+ref('S31')),
            ('Hosting','配信用ストレージ10GB、転送10GB/月。','Sparkで保存上限は新規デプロイ不可、転送超過は短い猶予後にサイト停止。'+ref('S32')),
            ('Cloud Storage','2026-02-03以降、Blaze＋Cloud Billingが必要。','新規バケットの無料利用量にはリージョン条件等もある。全地域一律に無料とは扱わない。'+ref('S33')),
            ('App Hosting','Blazeが必要。','通常のFirebase Hostingと別。Cloud FunctionsもF1のSpark案に含めない。'+ref('S34'))], 'Firebase：公式文書で確認。GBとGiBは公式の単位を保持')) +
        details('追加候補：R2・Access・Vercel',definition([
            ('R2 Standard','10GB-month、Class A 100万回/月、Class B 1,000万回/月、インターネット転送無料。サブスクリプションが必要で、超過は従量課金。支払方法が必要な前提で比較し、実際のcheckoutは未確認です。'+ref('S35','S36','S57')),
            ('Access Free','最初の50人まで無料の案内。Zero Trustの初期設定はFreeでも支払情報が必要。席の削除だけではアクセス失効になりません。'+ref('S10','S50','S39')),
            ('Vercel Hobby','個人・非商用。Organization所有のprivate repoはGit連携でデプロイ不可。コミット作成者にも条件があるので、今回の無料Git連携候補から外す提案です。'+ref('S37','S38'))])))
    body += section('budget','枠の大きさより、続けられるか',steps_for_budget() + '<div class="buttons"><a class="button primary" href="calculator.html">人数と写真量を変えてみる →</a><a class="button" href="compare.html">構成ごとの条件を比べる</a></div>')
    return body


def steps_for_budget():
    return bullets('初期はテキスト中心の案から比較。写真・通知・常時リアルタイム配信はMVPで本当に必要か確認します。','日次・月次・保存容量を分けて監視。予算アラートだけで支出が必ず止まるとは扱いません。','上限時に何を制限・停止するか、誰が課金を判断するかを決めておきます。','有料移行の目安はWorkers Paid最低$5/月、Supabase Pro $25/月から。追加利用・複数環境等を含む上限なしの定額料金ではありません。'+ref('S41','S26'))


def calculator_body():
    body = note('これは、仮定を変えるための計算機です。','実際の請求額や「必ず無料」を判定するものではありません。写真が増えると何が大きくなるか、みんなで同じ前提を見ながら相談しよう。')
    fields = [
        ('people','毎日使う人数（人）',30,1,1000,1),('records','１人の記録（件/日）',1,0,100,.1),('api','１人の取得（回/日）',10,0,10000,1),
        ('photos','１人の写真（枚/日）',1,0,100,.1),('size','写真１枚（MB）',.5,.01,100,.01),('views','１枚の総配信（回）',10,0,100000,1),('months','写真の保持（月）',3,1,120,1)]
    inputs = ''.join(f'<label for="{key}">{label}<input id="{key}" name="{key}" type="number" value="{value}" min="{low}" max="{high}" step="{step}" required></label>' for key,label,value,low,high,step in fields)
    body += section('try','人数と、使い方を入れてみよう',f'<div class="calculator"><div class="calc-presets"><button type="button" data-preset="30">30人・写真あり</button><button type="button" data-preset="50">50人・写真あり</button><button type="button" data-preset="text">30人・写真なし</button></div><form id="calc-form" aria-label="利用量の概算"><div class="calc-fields">{inputs}</div></form><p id="calc-error" class="calc-error" role="alert"></p><div id="calc-results" class="calc-results" aria-live="polite" aria-atomic="true"></div><noscript><p class="no-script">計算機にはJavaScriptを使います。下の「30人の例」はそのまま読めるよ。</p></noscript></div>')
    body += section('baseline','30人の例を、先に見てみる',table(['対象','計算結果','読み方'],[
        ('DB年間増分','65.7MB/年','30人×１記録×365日×2KB×仮の３倍。既存DBは別。'),
        ('取得する文書','6,000件/日','30人×10回×20件。D1の走査行数ではありません。'),
        ('テキスト転送','0.36GB/月','6,000件×2KB×30日。画面本体・ログインは別。'),
        ('写真保存','0.45GB/月増加','３か月保持すると1.35GB。'),
        ('写真の転送','4.5GB/月','１枚0.5MBを毎日投稿し、各写真を全体で10回配信。')], '仮定：30人が毎日利用。１人１記録・１枚/日、取得10回/日') + '<p>写真とテキストの転送を合わせると4.86GB/月。50人では8.1GB/月です。これは全件非キャッシュで、過去の写真の追加配信を含まない例だよ。</p>')
    body += section('formula','この計算で、含めたもの・残るもの',definition([
        ('固定した値','１記録2KB、DB係数３倍、１取得20件、30日/月・365日/年。MB・GBは十進表記。係数は仮の余裕で、実測ではありません。'),
        ('写真の扱い','月の投稿量×保持月数が保存量。転送は当月の写真×総配信回数。昔の写真の再閲覧、サムネイル、変換結果は別です。'),
        ('含めない処理','認証・管理・書込API、DB既存使用量、Rules参照、画面配信、ログ、CPU、バックアップ、税・ドメイン・SMTP費用。'),
        ('参考枠','DB500MB、Workers10万回/日、Firestore５万読取/日、Supabase非キャッシュ５GB/月、画像１GBを個別に参照。全指標が１つのサービスの請求に対応するわけではありません。'+ref('S20','S25','S26','S31'))]) + details('D1で全件走査してしまうと？','<p>30人の１年分10,950行を１日300回走査すると約328.5万行/日。50人なら18,250行×500回で約912.5万行/日となり、Freeの500万行/日を超える例です。返す行が20件でも、読み方次第で負荷が違います。</p><p>これは全走査の仮定。実際はインデックス・クエリプランと、D1が報告する走査数を確認します。FirestoreのRules参照・再接続等の追加読取も別に測ろう。</p>'+ref('S24','S42')))
    return body
