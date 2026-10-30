# 認証・公開範囲・基盤の比較資料

**検討中・未採用｜確認日：2026-10-30（日本時間）｜対象：Issue #3・#4**

閲覧用の入口は[テーマ別HTML](index.html)です。このMarkdownは詳細な調査メモです。

この資料は採用案の決定ではなく、候補・制約・追加検証を同じ基準で相談するためのものです。「確認済み」は公式文書上の確認を指し、このアプリでの実装・実機検証済みを意味しません。料金はUSD、税・為替・ドメイン取得費を含みません。

## 1. 今回の前提と、先に決めること

| 項目 | 根拠・扱い |
| --- | --- |
| 目的 | 同期のトレーニング記録を共有し、筋トレの継続を後押しする。現在のREADMEとIssueを参照 |
| 規模 | 数十人。概算の基準は30人、増加例は50人。開発者はPR #1の案では3人 |
| アクセス | 同期だけが利用・閲覧できる仕組みを比較する。具体的な対象者の範囲は未決 |
| 会社アカウント | **利用しない。必須条件**。会社SSO、会社メールを前提とする案は対象外 |
| 個人情報 | 個人メール以外を優先して探索する。個人メールは代替案。ニックネームやIDでも記録と結び付けば個人に関する情報になる |
| 費用 | 原則無料。課金設定が必要な無料枠と、課金設定なしで使える無料プランを区別する |
| 要件 | トレーニング、応援、公開範囲、体重、PWA等はPR #1の要件案。MVPはIssue #2でも相談中 |
| 現在のGitHub | Organization所有のPrivateリポジトリ。取得時点でWiki無効、Pages無効。契約プランは今回のAPIでは未確認 |

参照：[Issue #3](https://github.com/chuka57/doukin/issues/3)、[Issue #4](https://github.com/chuka57/doukin/issues/4)、[Issue #2](https://github.com/chuka57/doukin/issues/2)。背景の[要件案](https://github.com/chuka57/doukin/blob/d46cd222cff8051969818be0158e8cd126ce9b8d/docs/requirements.md)と[進め方案](https://github.com/chuka57/doukin/blob/d46cd222cff8051969818be0158e8cd126ce9b8d/docs/workflow.md)は、未マージのPR #1の特定コミットを参照しています。

**進め方の提案**：最初に「誰を招待するか」「何を誰に見せるか」「無料をどこまで厳密に守るか」を合わせ、その後に認証と基盤を並行比較する。最後は、認証・権限・DB・復旧までつながる構成を小さく試す。#3と#4の片方を丸ごと先に確定する必要はありません。

## 2. 現時点で優先して比べる構成

評価は今回の目的からの提案です。提供元の推奨や性能実測ではありません。

| 案 | 構成・役割 | メールを持たない運用 | 無料運用の条件 | 適合性と残る課題 |
| --- | --- | --- | --- | --- |
| N1 | React＋TypeScript＋Vite / Workers Static Assets＋Hono API / D1 / 招待＋WebAuthnパスキー | アプリでメール不要に設計できる。個人のパスワード管理サービス等によるパスキー同期は別の仕組み | Workers・D1のFree枠。画像・有料オプションは含めない | **メールなしの優先検証候補**。認証ライブラリのWorkers互換性、10ms CPU、セッション・復旧・招待を運営側で保守する負担が大きい |
| N2 | React＋TypeScript＋Vite / Workers Static Assets＋Hono API / D1 / Clerkのユーザー名＋パスワード | 公式のユーザーモデルはユーザー名を識別子にできる。メール・電話なしの登録、新端末ログイン、招待、復旧の通し検証は未実施 | Clerk Hobbyの機能範囲。**本番に所有ドメインとDNS設定権限が必要**。未所有なら取得費が発生 | **管理型認証の追加比較候補**。無料の本番パスキーは使えない。通常のパスワードリセットはメールか電話に依存するため、管理者復旧の設計が必要 |
| P1 | React＋TypeScript＋Vite / Workers Static Assets / Supabase Auth＋Postgres＋RLS | 個人Google・GitHub等のOAuthを使う代替案。メール入力がなくても認証基盤にメール等が保存され得る | Supabase Free。標準ドメイン利用ならドメイン購入を前提にしない | **個人アカウントを許容する場合の実装負担が比較的小さい案**。参加資格は別途確認。外部アカウントの所持を参加条件にしてよいか未決 |
| P2 | P1の認証を個人メールのOTP／Magic Link＋外部SMTPにする | メールを認証基盤で保有する | Supabase Freeに加え、SMTPの配信枠・送信ドメインの費用を確認 | 復旧経路が分かりやすい代替案。**Supabase標準SMTPを参加者向け本番配信には使えない** |
| F1 | React＋TypeScript＋Vite / Firebase Hosting / Firebase Auth / Firestore / Security Rules | 個人アカウント等を使う代替案。匿名認証だけで長期利用の復旧を完結させない | Sparkでテキスト中心。画像Storage、Cloud Functions、App Hostingを前提にしない | 一体型の別候補。ドキュメント単位の権限と読取回数を考慮したデータ設計が必要 |

N1のパスキー方式は標準に基づく設計候補で、既製ライブラリを使っても招待・復旧まで自動で完成するわけではありません。SimpleWebAuthnは候補ライブラリの一例で、公式のサーバー実行環境はNode／Denoを案内しており、Workersでそのまま利用できるとはこの調査では確認していません。[S01][s01] [S02][s02]

N2は、Clerkのユーザーモデル・管理APIと料金・本番要件から追加した候補です。開発モードで試せる機能と、無料の本番で使える機能を混同しないことが重要です。[S03][s03] [S04][s04] [S05][s05] [S06][s06]

今回の優先順位は、**N1・N2の成立条件を調べる → 個人メール／個人OAuthを許容した場合のP1・P2と比較 → チームで採用判断**です。「無料枠が大きい」だけで認証方式やDBを確定しません。

## 3. 認証方式を、招待・失効・復旧まで比較する

| 方式 | 招待・本人の確認 | 端末紛失・機種変更 | 失効 | 主な制約・判断 |
| --- | --- | --- | --- | --- |
| 招待＋パスキー（N1） | 個別の期限付き・1回限りの招待を、既知の同期との私的な連絡手段で渡す。登録時にパスキーを作る | 複数パスキー・個人のパスキー同期・1回限りの復旧コード・管理者による再確認を組み合わせる設計 | 会員状態を無効化し、セッション・復旧コード・必要な認証資格を失効 | メールなしが可能な設計。RP IDを固定し、対象端末、再登録、紛失を実機検証。生体情報そのものをアプリに送る方式ではない |
| 管理型ユーザー名＋パスワード（N2） | 参加資格を確認して個別に払い出す案。メールを使わない初回登録方法は要検証 | 別端末ではDevice Trust等の追加認証条件を確認。パスワードだけで利用できるとは断定しない。標準リセットはメール／電話が必要 | 認証側とアプリの会員状態を両方管理 | 送信メールを省けても管理者復旧の負担は残る。Clerkでは本番パスキーは有料。ユーザー名は公開表示用のニックネームと分ける |
| 個人OAuth（P1） | ログイン成功後、招待・会員承認を別に確認 | 個人の認証サービス側の復旧を利用 | 会員無効化＋アプリセッションの失効 | ログイン成功は「同期であること」の証明ではない。会社アカウントは使わず、認証基盤に保存される属性も確認 |
| 個人メールOTP／Magic Link（P2） | 個人メールの確認＋同期としての参加確認 | 個人メールにアクセスできれば再ログイン | 会員無効化＋セッションの失効 | 配信基盤、迷惑メール、送信上限、外部SMTPが必要。メール変更・紛失時の対応も決める |
| Supabase匿名ログイン | 匿名ユーザー作成後に会員承認する仕組みは作れる | **単独では不可**。サインアウト、ブラウザデータ削除、別端末で同じアカウントを利用できない | 会員状態とセッションを管理 | 長期のトレーニング履歴を持つ本番の唯一のログイン方式としては推奨しない。体験版・試作候補 |
| Cloudflare Access＋個人メールOTP | 個人メールの許可リストで入口を制限。同期かどうかは運営側が確認 | 個人メールで再ログイン | Accessのポリシー変更とアプリ側の会員状態を管理 | メール不要にはならない。無料枠は50人が目安。API側の個人別権限は別途必要 |
| 全員共通のパスワード・共通招待URL | 誰が使ったか識別できない | 個別復旧ができない | 一人だけの失効が難しい | **個人の記録・体重を扱う本用途には採用しない提案**。個別のIDと権限が必要 |

パスキーの設計根拠：[S01][s01]。Clerkの認証・リセット条件：[S06][s06] [S07][s07]。匿名ログインの制約：[S08][s08]。Accessの個人メールOTPと無料人数の根拠：[S09][s09] [S10][s10]。

### Supabaseのパスキーは「メールなし新規登録」の解決になるか

現行の公式文書にはパスキー機能がありますが、**実験的機能**で、登録には確認済みの非匿名ユーザーが必要です。匿名ユーザーは先にメールまたは電話を関連付ける必要があると明記されています。そのため「匿名登録してパスキーを追加すれば、メールも電話も不要」とは扱えません。ログイン画面でメールを入力しないことと、登録時にメールを持たないことは別です。[S11][s11]

Better AuthのUsernameプラグインも、標準の登録APIはメール必須です。「ユーザー名ログイン対応」という機能名だけで、メールなし登録可能と判断しません。[S12][s12]

### 招待と復旧の共通ルール案

1. 「同期」の対象を運営者が把握し、既知の連絡先・対面等で個別に確認する。会社のディレクトリや会社SSOを使わない。
2. 招待は十分に推測しにくいトークンとし、保存時はハッシュ化、期限・使用済み状態・発行者を記録する。並行した引換でも1回しか有効にならない仕組みを用意する。
3. 新規登録できても、会員承認がない間は他人のデータを読めない。会員状態は利用者自身が変更できないようにする。
4. 復旧コードは1回限り・ハッシュ保存とし、パスキー等と同じ端末だけに保存する運用を避ける。紛失時は既知の同期であることを改めて確認する。
5. 復旧・再招待時は古いセッション等を無効化し、元の会員IDへ履歴が戻るか確認する。ニックネームの一致だけで引き継がせない。

上記は設計提案であり、実装済みの機能ではありません。新端末や復旧時に個人メールが必要になる候補は、その時点で「メール不要の候補」から外して比較し直します。

## 4. 公開範囲は、認証サービスと別に設計する

以下は#2・#3で相談するための初期値案です。

| データ | 本人 | 承認済みの同期 | 未承認・失効済み・未ログイン | 初期値の提案 |
| --- | --- | --- | --- | --- |
| ニックネーム・公開プロフィール | 閲覧・編集 | 必要な項目のみ閲覧 | 閲覧不可 | メール・内部IDをプロフィールに出さない |
| トレーニング記録 | 自分の記録を閲覧・編集・削除 | 本人が同期共有を選んだ記録のみ閲覧 | 閲覧不可 | 保存時に本人が共有範囲を確認。既定を同期共有にするかは#2・#3で決める |
| 体重・身体情報 | 閲覧・編集・削除 | 本人が明示的に共有した範囲のみ | 閲覧不可 | **任意入力・初期非公開**を提案 |
| メール・認証資格・復旧情報 | 必要な管理操作のみ | 閲覧不可 | 閲覧不可 | タイムライン等のデータと分離 |
| 招待・会員状態 | 自分の状態確認に必要な範囲 | 他人の招待管理は不可 | データ読取は不可 | 権限のある運営者だけが変更 |

**実装で守る境界の提案**：

- UIで隠すだけでなく、API・DB側でも会員状態、所有者、共有範囲を確認する。自分の記録の更新・削除と、他人の閲覧を別条件にする。
- SupabaseではRLSを有効化し、対象テーブルへの権限・ポリシーを確認する。匿名ユーザーも`authenticated`になるため、そのロールだけで同期と見なさない。`service_role`など権限を迂回するキーをブラウザに配布しない。[S08][s08] [S13][s13]
- SupabaseのRLSは行に対する制御であり、共有可能なトレーニング行に体重を混ぜて、同じ読取許可で返さない。体重を別テーブルにする等、データの分け方を選ぶ。
- Firestore Rulesはドキュメントを部分的に隠して返せない。共有プロフィールと非公開の体重は別ドキュメント等に分ける。[S14][s14]
- D1案ではアプリのAPIが権限を検査する。Supabase RLSと同じ仕組みが自動で付く構成として扱わない。
- 会員失効は各アクセスで参照できる状態にする。JWTや画面の表示だけを信頼しない。Supabaseでもサインアウト後のJWTは期限まで利用可能なため、失効をどこまで即時反映するかを定義する。[S15][s15]
- Accessを入口に置いても、DB・画像ストレージへの別経路を保護する。APIがAccessのJWTを使う場合は署名・issuer・audience等を検証する。[S16][s16]
- PWAでは体重・トークン・他人の記録を安易に永続キャッシュしない。ログアウト、端末共有、オフライン時の残存を実機で確認する。

## 5. 技術スタックは役割をそろえて比較する

| 役割 | 候補 | 今回の評価・確認事項 |
| --- | --- | --- |
| 言語 | TypeScript | フロントと小さなAPIで共通化できる候補。採用は未決 |
| フロント | React＋Vite | ログイン後の画面中心なら静的配信とブラウザからのAPI利用で構成できる。SSRを必須としない案 |
| フロント・サーバー | Next.js | チームの経験を活かせる場合の候補。静的exportとSSR／Server Actionsを使う構成を区別する |
| Next.jsの実行先 | Cloudflare Workers＋OpenNext | Cloudflare公式の対応経路。Node環境との互換性や利用機能を確認する。通常のPages静的配信と同じ前提にはしない [S17][s17] |
| API | Hono＋Workers | D1、招待、会員権限、復旧用APIの候補。認証自体を代わりに実装してくれる機能ではない |
| DB・権限 | Supabase Postgres＋RLS | 記録・セット・リアクション・会員等の関係をSQLで扱える。RLSと移行・バックアップが必要 |
| DB | D1（SQLite系） | Workersから使うSQL DB。権限と認証はAPI側で実装し、インデックスと日次の読書き枠を確認 |
| DB・権限 | Firestore＋Security Rules | ドキュメントの形と検索、読取回数、権限に合わせて設計。SQLと同じJOIN前提にしない |
| 画像 | Supabase Storage／R2／Firebase Storage | テキストDBと別に見積もる。初期MVPは固定アイコン等で画像アップロードを省く案も#2で比較する |
| CI | GitHub連携／GitHub Actions | OrganizationのPrivateリポジトリとの連携、秘密情報、プレビュー環境と本番データの分離を確認 |

Cloudflare公式は現在、新規プロジェクトをWorkersから始めることを案内しています。Pagesも比較対象として残しますが、新規の第一候補はWorkers Static Assetsとしました。[S18][s18]

認証を自由に入れ替えられるとは限りません。例えば、Clerk＋D1はAPIでClerkのIDと会員を関連付ける必要があります。独自パスキー認証＋SupabaseでブラウザからDBへ直接アクセスするには、Supabaseが信頼するトークンとRLSの連携設計が必要です。別の認証でログインできたからといって、そのままSupabase Authの利用者にはなりません。

## 6. 無料枠・超過時の挙動・運用制約

**「月額0ドルのプラン」「有料契約に含まれる無料利用量」「運用全体の支出が0円」は別です。** ドメイン、SMTP、画像、バックアップ先、開発・本番の複数環境も含めて確認します。

| サービス・プラン | 主な無料枠／条件 | 上限到達・運用上の制約 | 出典 |
| --- | --- | --- | --- |
| Workers Static Assets | 静的ファイルへのリクエストは無料・回数制限なし。静的配信だけならWorkerスクリプトを実行しない | 認証ゲート、SSR等でWorkerを先に実行する経路はWorkerの枠を使う。静的フロントを配ること自体はアプリのデータ認可ではない | [S19][s19] |
| Workers Free | 動的リクエスト100,000/日、CPU 10ms/呼出、メモリ128MB | 日次枠・CPU制限超過で処理が失敗し得る。CPU時間は通信待ちを含む経過時間とは別。パスキーの検証・パスワードハッシュを未計測で収まると扱わない | [S20][s20] |
| Workers Builds Free | 3,000ビルド分/月、同時1ビルド、20分タイムアウト | 実行リクエストの枠とは別。3人のPRプレビュー・本番を合わせて見積もる | [S21][s21] |
| Pages Free（代替） | 500ビルド/月、同時1、20,000ファイル | Pages FunctionsはWorkersとして計上。Workers Buildsの3,000分と混同しない | [S22][s22] [S23][s23] |
| D1 Free | 読取500万行/日、書込10万行/日、全DB合計5GB。**1 DBは500MBまで**、10 DB | 読書き日次上限でクエリがエラー。容量上限で追加・変更に制限。返却行数ではなく走査行数が重要。インデックス更新も書込に加算 | [S24][s24] [S25][s25] |
| Supabase Free | DB 500MB、Auth 50,000 MAU、ファイル1GB、非キャッシュ転送5GB＋キャッシュ転送5GB | 低稼働時の停止。料金表は非活動1週間と記載。転送等の超過は通知・猶予後にサービス制限があり得る。2種類の転送枠は相互融通できる10GBと扱わない | [S26][s26] [S27][s27] |
| Supabaseの複数環境 | アクティブなFreeプロジェクトは2個の制限。Owner／Adminの他の利用状況も関係 | 「Organizationごとに自由に2個」ではない。本番・検証と既存プロジェクトを合わせて確認 | [S28][s28] |
| Supabase標準SMTP | プロジェクトのチームに属するメール宛てのみ。現在2通/時 | 参加者全員を開発チームへ追加して回避しない。P2では外部SMTPを準備し、その枠・費用を別見積り。一般にはSend Email Hookによる配信も選択肢 | [S29][s29] |
| Clerk Hobby | 50,000 MRU/アプリ、管理画面3席、セッション期間7日固定、ログ1日 | MRUはMAUと異なる指標。本番パスキー・Allowlist等に有料機能がある。所有ドメインが本番要件。4人目の管理者や高度な権限が必要になった時点で料金を再確認 | [S04][s04] [S05][s05] [S06][s06] [S30][s30] |
| Firebase Spark＋Firestore | 1GiB、読取50,000/日、書込20,000/日、削除20,000/日、転送10GiB/月 | 無料DBはプロジェクト内1つ。上限を超える利用には課金有効化が必要。PITR、バックアップ、復元は無料枠に含まれない | [S31][s31] |
| Firebase Hosting | 配信用ストレージ10GB、転送10GB/月 | Sparkでは保存枠上限で新規デプロイ不可。転送上限は短い猶予後にサイト停止、翌月等に復帰。ユーザー画像用Storageとは別 | [S32][s32] |
| Firebase Storage／App Hosting | 無料利用量が存在しても、**Blazeの課金設定が必要** | Storageは2026-02-03からの要件。App HostingもBlaze必須。Sparkだけで画像保存やNext.js動的ホスティングまで賄えると扱わない | [S33][s33] [S34][s34] |
| R2 Standard（画像の追加候補） | 10GB-month、Class A 100万回/月、Class B 1,000万回/月、インターネット転送無料 | R2サブスクリプションの有効化・checkoutが必要。無料枠超過は従量課金。アドオンの支払方法維持の公式規定から、支払情報が必要な前提で比較。個別checkoutは未確認。厳密に課金不可なら初期構成に入れない | [S35][s35] [S36][s36] |
| Vercel Hobby | 個人・非商用に限定 | **OrganizationのPrivateリポジトリをGit連携でデプロイできない**。共同開発者のコミットにも条件がある。現在のdoukinの無料Git連携先としては選ばない | [S37][s37] [S38][s38] |
| Cloudflare Access Free | 最初の50人まで無料という案内 | 数十人では将来の上限に近い。Zero Trust Freeでも初期設定に支払情報が必要。席を削除するだけではアクセス失効にならない。個人メールOTPはメールを必要とする。API・データの個人別認可は別実装 | [S09][s09] [S10][s10] [S39][s39] |

Supabaseの500MBは料金上のDB利用枠で、実際のディスク使用率によるread-only制御とは別です。現行のDBサイズ説明では組織単位・期間平均によるFair Use判定も案内されています。2プロジェクトで500MBずつ自由に使えると仮定せず、採用前にダッシュボードと当時の条件を確認します。[S40][s40]

**課金への移行を検討する目安**：Workers Paidは最低$5/月、Supabase Proは$25/月からという案内があります。いずれも上限のない定額契約ではありません。必要になったときに枠・追加利用料・複数環境を再見積りし、チーム合意を経て変更する提案です。[S41][s41] [S26][s26]

## 7. 利用量の概算

ここからは公式の料金ではなく、**仮定を置いた計算**です。MB／GBは十進表記、FirestoreのGiBは公式の単位を保持しています。利用者全員が毎日使う上限寄りの例で、実測や課金見積りを保証するものではありません。

| 仮定 | 基準値 |
| --- | --- |
| 毎日利用する人数 | 30人 |
| トレーニング記録 | 1人1件/日、1件あたり本文・セット等の合計2KB |
| DBの概算係数 | 生データの3倍。インデックス等の仮の余裕であり実測値ではない |
| データ取得 | 1人10回/日、1回20件、1件2KBを返す |
| 写真を追加する場合 | 1人1枚/日、1枚0.5MB、月30日、各写真を全体で10回配信 |

| 対象 | 計算 | 基準値での結果 |
| --- | --- | --- |
| 記録件数 | 30人×1件×30日 | 900件/月 |
| テキストの年間生データ | 30人×1件×365日×2KB | 約21.9MB/年 |
| DBの仮の年間増分 | 21.9MB×3 | 約65.7MB/年。既存の認証・標準スキーマ・ログ・別テーブル等は別 |
| データ取得API | 30人×10回 | 300回/日。書込・ログイン・管理操作は別 |
| 返す行／文書 | 30人×10回×20件 | 6,000件/日。D1の走査行数とは異なる |
| テキストのAPI転送 | 30人×10回×20件×2KB×30日 | 約0.36GB/月。アプリ本体・画像・ログイン等は別 |
| 写真の保存増分 | 30人×1枚×0.5MB×30日 | 0.45GB/月。保持を続けると3か月で1.35GB |
| 写真の配信 | 900枚×0.5MB×10回 | 4.5GB/月。全件非キャッシュならSupabaseの5GB枠に近い |
| 固定アバターの例 | 30人×0.1MB×1枚 | 合計約3MB。日々の写真と影響が異なる |

HTML版では人数・記録頻度・API回数・写真の頻度／サイズ／配信回数／保持期間を変更できます。計算機は主な枠の参考比率を出すだけで、認証の成立・CPU時間・全料金・実際の請求額を判定しません。DB係数3、1記録2KB、1取得20件、30日/月・365日/年は固定です。写真の転送は当月の投稿枚数から計算し、過去の写真が追加で配信される分は含みません。

### 人数だけで無料枠に収まると判断しない

- 50人なら、写真0.5MBを毎日1枚で保存0.75GB/月、10回配信で7.5GB/月。写真はテキストより先に無料枠へ影響する。
- D1でインデックスがなく、1年分のトレーニング行を毎回全走査すると、30人では10,950行×300回＝約328.5万行/日。50人では18,250行×500回＝約912.5万行/日となり、読取500万行/日を超える。これは全走査を仮定した例で、実際はインデックスとクエリで測定する。[S24][s24]
- セットを別行にするなら1件の記録が複数書込になる。30記録＋300セット＋90リアクション＋30体重で450行/日、さらにインデックス・認証等の書込が増えるという例になる。
- Firestoreのリアルタイム購読・再接続・Rulesの別ドキュメント参照も読取に影響する。6,000件/日だけで上限余裕を断定しない。[S42][s42]
- 写真なしなら、無料枠の容量より、認証・復旧・運用継続性が先に判断を左右する可能性が高い、というのがこの概算からの推測。

## 8. 少人数運用のための提案

### バックアップ・削除・復旧

| 構成 | 公式機能と不足分 | 今回の運用案 |
| --- | --- | --- |
| Supabase Free | 有料プランの日次バックアップと同じ復元機能を前提にしない。公式はFreeでCLI等による定期エクスポートを推奨。DBバックアップにStorageの画像本体は含まれない | 許容するデータ損失期間を決め、暗号化した別の場所への退避と、検証環境での復元を試す [S43][s43] |
| D1 Free | Time TravelはFreeで7日。Paidの30日と区別。別アカウント喪失等までカバーする外部バックアップではない | スキーマ変更前に復元点を確認。必要に応じエクスポートし、7日を超える保持が必要か決める [S25][s25] |
| Firestore Spark | PITR・バックアップ・復元操作に無料枠はない | 課金なしで実現するバックアップ・復元手順を別途検証。標準の自動バックアップが無料で使える前提では採用しない [S31][s31] |

退会・削除時は、本人の記録、体重、画像、認証アカウント、リアクション等の関連データと、バックアップ内の保持期間まで対象を決めます。復元により削除済みデータが戻った場合の再削除手順も残す案です。バックアップや実データをGitリポジトリ・Issue・HTML資料に含めません。

### 無料で続けるための実装・開発の範囲

- 初期はテキスト＋固定アイコンを優先する案とし、写真アップロードの採否は#2で合意する。通知・重い画像変換・常時リアルタイム配信を必要条件にしない。
- カーソルによるページ分割、必要な列だけの取得、利用者・日付等のインデックス、1人・1操作のサイズや頻度制限を設計する。
- プレビューは検証用DBとテストデータに接続し、本番会員や体重を読み込まない。OAuthのリダイレクト先やパスキーのRP IDも環境を分けて確認する。
- 認証・ホスティングの開発者アカウントも個人用とし、会社SSOや会社メールに依存しない。共有ログインを避け、保守できる運営者を複数人にする案。
- Freeのまま上限を迎えたときは、利用制限や一時停止を許容するか、誰が課金判断をするか決める。課金アカウントを追加したサービスでは、通知だけで支出を止められるとは扱わない。
- 小さな縦断試作で、招待 → ログイン → 自分の記録 → 同期への共有 → 体重非公開 → 失効 → 別端末復旧を確認してから採用する。

## 9. 資料をどこに置くか

閲覧用の正面は[テーマ別HTMLの入口](index.html)。HTMLはテーマ別ガイドと構成別詳細に分け、共通のCSS・SVG・JavaScriptを使います。料金や復旧の重要条件は本文に残し、細かな補足と出典は折りたたみで読める設計です。

資料と生成元はリポジトリの `docs/research/issue-3-4/` に置き、通常のPRでレビューします。比較資料をmainへ取り込むことと、サービスや仕様の採用は区別し、決定時には理由・不採用案・見直し条件を決定事項へ記録します。Organizationのprivate repoではGitHub FreeのDraft PRを前提にしません（[公式の対応プラン](https://docs.github.com/en/rest/pulls/pulls)）。現在の契約プランは未確認です。

共有方法は[HTMLの共有・更新ガイド](sharing.html)で比較しています。ZIPを展開してindex.htmlを開けば、新しいホスティング契約なしで読めます。URLで読む場合はWorkers Static Assets＋Cloudflare Accessを候補とし、閲覧対象を別途設定してから共有します。Zero Trust Freeでも支払情報が必要です。資料用の個人GitHub認証は、全参加者向けアプリ認証の採用を意味しません。

Wikiは任意のCSS/JavaScriptを含むHTMLのホストにはならず、private Wikiには対応プランが必要。Pagesもprivate repoの権限がそのままサイトの公開範囲になるとは限りません。[S44][s44] [S45][s45] [S46][s46]

Issueには質問・調査の補足・試作結果・判断の要点を残し、本文の最新版は該当HTMLへリンクします。分割案は[進め方のHTML](workflow.html)と[起票用の詳細メモ](issue-plan.md)を参照。Issue作成・投稿・設定変更・デプロイは未実施です。

## 10. 採用前に残る確認

| 確認事項 | 関係するIssue | 判断への影響 |
| --- | --- | --- |
| 同期の対象・承認者・離脱時の扱い | #3 | 招待・失効と会員データの持ち方 |
| 個人メールをアプリが保持しないだけか、認証事業者にも渡さないのか | #3 | 個人OAuthを代替案に残せるか |
| メールなしの端末紛失・パスワード忘れを、誰がどう復旧するか | #3 | N1・N2の採用可否 |
| N1のライブラリ互換性・実機動作・CPU時間 | #3・#4 | Workers Freeでの成立可否 |
| N2の登録・新端末・復旧の通し動作と本番の無料機能 | #3・#4 | 「ユーザー名が使える」から先の成立可否 |
| 画像・体重・PWAオフラインのMVP範囲 | #2 | 容量・転送・データ分離・キャッシュ方針 |
| 最大参加人数・写真の保持期間 | #4 | Accessの人数枠、DB・Storageの余裕 |
| GitHub／各サービスの契約と、既存の無料枠消費 | #4 | Wikiの利用可否、本番・検証環境、共同管理 |
| 独自ドメイン・SMTP・課金登録を許容するか | #4 | N2・P2・R2等の費用と運用 |
| バックアップ先・許容する損失期間・復元担当 | #4 | 無料プランを継続運用できるか |

## 11. 公式出典一覧

すべて2026-10-30（日本時間）に参照。料金・上限・機能は採用時にも再確認します。URLの先は更新されるため、この資料には確認した条件を併記しています。

| ID | 公式出典 | 確認した主な内容 |
| --- | --- | --- |
| S01 | [SimpleWebAuthn: Passkeys][s01] | パスキー、RP ID・ユーザー識別と認証 |
| S02 | [SimpleWebAuthn: Server][s02] | サーバー側の対応ランタイム、データ構造 |
| S03 | [Clerk: Users][s03] | メール・電話・ユーザー名の識別子 |
| S04 | [Clerk: Pricing][s04] | 50,000 MRU、管理画面3席、無料期間・ログ等 |
| S05 | [Clerk: Production][s05] | 所有ドメイン・DNS等の本番要件 |
| S06 | [Clerk: Sign-up and sign-in options][s06] | ユーザー名・パスワード、本番パスキーの有料条件 |
| S07 | [Clerk: Forgot password][s07] | メール／電話を使うパスワードリセット |
| S08 | [Supabase: Anonymous Sign-Ins][s08] | 端末変更・ブラウザ削除時の制約、authenticatedロール |
| S09 | [Cloudflare: One-time PIN][s09] | 許可したメールへのOTP |
| S10 | [Cloudflare公式サイト][s10] | Zero Trustの最初の50人が無料という案内 |
| S11 | [Supabase: Passkey authentication][s11] | 実験的、既存の確認済み非匿名ユーザーが必要 |
| S12 | [Better Auth: Username][s12] | 標準のユーザー名登録でもメール必須 |
| S13 | [Supabase: Row Level Security][s13] | DB内での行の認可、公開テーブルのRLS |
| S14 | [Firebase: Control access to specific fields][s14] | フィールドだけを隠す読取ルールは不可 |
| S15 | [Supabase: User sessions][s15] | JWT、サインアウトと失効、有料の一部セッション制御 |
| S16 | [Cloudflare: Validate JWTs][s16] | AccessのJWTの検証 |
| S17 | [Cloudflare: Next.js on Workers][s17] | OpenNextによる対応経路 |
| S18 | [Cloudflare Pages overview][s18] | 新規プロジェクトにはWorkersを案内 |
| S19 | [Workers Static Assets: Billing][s19] | 静的配信とWorker実行の区別 |
| S20 | [Workers: Limits][s20] | リクエスト数、CPU、メモリ等 |
| S21 | [Workers Builds: Limits & pricing][s21] | Free 3,000ビルド分、同時数 |
| S22 | [Pages: Limits][s22] | ビルド回数・ファイル数 |
| S23 | [Pages Functions: Pricing][s23] | Workerとしての課金 |
| S24 | [D1: Pricing][s24] | 日次読書き枠、走査行数、インデックス |
| S25 | [D1: Limits][s25] | 1DB 500MB、全体5GB、Time Travel 7日 |
| S26 | [Supabase: Pricing][s26] | 無料枠、低稼働時停止、Pro料金 |
| S27 | [Supabase: Egress usage][s27] | 非キャッシュとキャッシュの独立枠、超過時 |
| S28 | [Supabase: Billing FAQ][s28] | Freeプロジェクト数、Fair Useの制限 |
| S29 | [Supabase: Custom SMTP][s29] | 標準SMTPの送信先・回数制限 |
| S30 | [Clerk: Restricting access][s30] | Invite-only等の登録制御、有料Allowlist |
| S31 | [Firestore: Quotas][s31] | 日次枠・保存枠、有料の復元機能 |
| S32 | [Firebase Hosting: Quotas][s32] | 10GB/月転送、超過時の停止等 |
| S33 | [Firebase Storage: Billing changes][s33] | 2026年のBlaze要件 |
| S34 | [Firebase App Hosting: Costs][s34] | Blaze必須、関連サービスの利用料 |
| S35 | [R2: Pricing][s35] | Standardの無料枠と超過課金 |
| S36 | [R2: Get started][s36] | サブスクリプション有効化 |
| S37 | [Vercel: Git deployments][s37] | OrganizationのPrivateとHobbyの制限 |
| S38 | [Vercel: Hobby][s38] | 個人・非商用利用 |
| S39 | [Cloudflare: Seat management][s39] | 席の削除とアクセス失効の違い |
| S40 | [Supabase: Database and disk size][s40] | DB課金枠とディスク使用率の違い・Fair Use |
| S41 | [Workers: Pricing][s41] | Paidの最低月額と追加利用料 |
| S42 | [Firestore: Billing][s42] | 読取課金・Rules参照等 |
| S43 | [Supabase: Database Backups][s43] | Freeの退避、Storage本体は含まない |
| S44 | [GitHub: About wikis][s44] | 公開範囲と対応プラン |
| S45 | [GitHub: Markup][s45] | 表示時のHTMLサニタイズ・script等の除去 |
| S46 | [GitHub: Pages visibility][s46] | 非公開サイトのEnterprise Cloud条件 |

[s01]: https://simplewebauthn.dev/docs/advanced/passkeys
[s02]: https://simplewebauthn.dev/docs/packages/server
[s03]: https://clerk.com/docs/guides/users/managing
[s04]: https://clerk.com/pricing
[s05]: https://clerk.com/docs/guides/development/deployment/production
[s06]: https://clerk.com/docs/guides/configure/auth-strategies/sign-up-sign-in-options
[s07]: https://clerk.com/docs/guides/development/custom-flows/authentication/legacy/forgot-password
[s08]: https://supabase.com/docs/guides/auth/auth-anonymous
[s09]: https://developers.cloudflare.com/cloudflare-one/integrations/identity-providers/one-time-pin/
[s10]: https://www.cloudflare.com/
[s11]: https://supabase.com/docs/guides/auth/passkeys
[s12]: https://better-auth.com/docs/plugins/username
[s13]: https://supabase.com/docs/guides/database/postgres/row-level-security
[s14]: https://firebase.google.com/docs/firestore/security/rules-fields
[s15]: https://supabase.com/docs/guides/auth/sessions
[s16]: https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/authorization-cookie/validating-json/
[s17]: https://developers.cloudflare.com/workers/framework-guides/web-apps/nextjs/
[s18]: https://developers.cloudflare.com/pages/
[s19]: https://developers.cloudflare.com/workers/static-assets/billing-and-limitations/
[s20]: https://developers.cloudflare.com/workers/platform/limits/
[s21]: https://developers.cloudflare.com/workers/ci-cd/builds/limits-and-pricing/
[s22]: https://developers.cloudflare.com/pages/platform/limits/
[s23]: https://developers.cloudflare.com/pages/functions/pricing/
[s24]: https://developers.cloudflare.com/d1/platform/pricing/
[s25]: https://developers.cloudflare.com/d1/platform/limits/
[s26]: https://supabase.com/pricing
[s27]: https://supabase.com/docs/guides/platform/manage-your-usage/egress
[s28]: https://supabase.com/docs/guides/platform/billing-faq
[s29]: https://supabase.com/docs/guides/auth/auth-smtp
[s30]: https://clerk.com/docs/guides/secure/restricting-access
[s31]: https://firebase.google.com/docs/firestore/quotas
[s32]: https://firebase.google.com/docs/hosting/usage-quotas-pricing?hl=en
[s33]: https://firebase.google.com/docs/storage/faqs-storage-changes-announced-sept-2024
[s34]: https://firebase.google.com/docs/app-hosting/costs
[s35]: https://developers.cloudflare.com/r2/pricing/
[s36]: https://developers.cloudflare.com/r2/get-started/
[s37]: https://vercel.com/docs/git
[s38]: https://vercel.com/docs/plans/hobby
[s39]: https://developers.cloudflare.com/cloudflare-one/team-and-resources/users/seat-management/
[s40]: https://supabase.com/docs/guides/platform/database-size
[s41]: https://developers.cloudflare.com/workers/platform/pricing/
[s42]: https://firebase.google.com/docs/firestore/pricing
[s43]: https://supabase.com/docs/guides/platform/backups
[s44]: https://docs.github.com/en/communities/documenting-your-project-with-wikis/about-wikis
[s45]: https://github.com/github/markup
[s46]: https://docs.github.com/en/enterprise-cloud@latest/pages/getting-started-with-github-pages/changing-the-visibility-of-your-github-pages-site

## HTML再構成時のレビュー追記

2026-10-30 JSTに別モデルの独立レビューを行い、Clerkの新端末・統合登録フロー、Supabaseの容量制御、支払情報の条件を再確認しました。反映内容と追加の一次情報は[出典・レビュー](sources.html#review)に記載しています。

- ClerkのDevice Trust：[公式](https://clerk.com/docs/guides/secure/mfa-recovery)。メール・電話なしの新端末利用は要検証。
- Clerkの統合登録フロー：[公式](https://clerk.com/docs/guides/development/custom-flows/authentication/sign-in-or-up)。ユーザー名のみのsign-in-or-upには未対応。
- Cloudflare Zero Trustの初期設定：[公式](https://developers.cloudflare.com/cloudflare-one/setup/)。Freeでも支払情報が必要。
- R2とアドオンの支払方法：[公式](https://developers.cloudflare.com/billing/get-started/update-billing-info/)。実際のcheckoutは未操作。
- SupabaseのSend Email Hook：[公式](https://supabase.com/docs/guides/auth/auth-hooks/send-email-hook)。P2は外部SMTP案だが、一般に本番配信の唯一の方法ではない。
