# doukin の技術検討ノート

**検討中・未採用｜確認日：2026-10-30（日本時間）**

閲覧の入口は **[index.html](docs/index.html)**。認証・基盤・費用と５つの構成案を、16ページのHTMLに分けています。共通の色・SVG・図解、テーマ間のリンク、折りたたみの補足、利用量の計算機を備えます。

## 読む・共有する

[GitHub Pages](https://chuka57.github.io/doukin-docs/)で閲覧します。公開設定とデプロイの完了後に利用できます。

- HTMLと `docs/assets/` は同じ階層関係で保存します。HTMLだけを１枚取り出すと共通のスタイルや図を読めません。
- 読むための外部ライブラリ、フォント、アクセス解析、通信APIは使いません。外部の公式出典やGitHubへのリンクは、クリックしたときに移動します。
- GitHubのファイル画面はHTMLをWebサイトとして配信しません。URLで共有する候補と公開範囲は [sharing.html](docs/sharing.html) を参照してください。ホスティングやAccessは未設定です。

## ページの構成

| 種類 | ページ |
| --- | --- |
| 入口と比較 | `index.html`、`compare.html` |
| テーマ | `auth.html`、`privacy.html`、`platform.html`、`data.html`、`cost.html` |
| 概算計算機 | `calculator.html` |
| 構成別の詳細 | `plan-n1.html`、`plan-n2.html`、`plan-p1.html`、`plan-p2.html`、`plan-f1.html` |
| 検討・運用 | `workflow.html`、`sharing.html` |
| 根拠 | `sources.html`（出典・用語・独立レビューの反映事項） |

## 変更・生成する

Python 3の標準ライブラリだけで生成できます。Pandocやアプリ本体の依存追加は不要です。

```sh
python scripts/build_html.py
```

- `scripts/guide_content.py`：テーマ別本文、進め方、共有、出典とレビュー。
- `scripts/guide_plans.py`：５つの構成案と共通の比較項目。
- `scripts/guide_costs.py`：無料枠、概算の前提と入力画面。
- `scripts/guide_ui.py`：カード・手順・SVGアイコン・図解等の共通部品。
- `docs/assets/guide.css`：全ページ共通の色・文字・レイアウト。
- `docs/assets/guide.svg`：案内役のイラスト。
- `docs/assets/guide.js`：目次・出典の開閉、計算機、印刷時の補足展開。
- `content/comparison.md`：詳細な調査メモと初回出典の一覧。生成時に出典を参照。
- `content/issue-plan.md`：相談用のSub-issue本文案。実際の起票はしていません。

生成したHTMLと原稿を同じPRで更新します。閲覧する人にMarkdownの読解を要求しません。調査事実を更新する場合は、原稿と詳細メモの整合も確認します。既存のテーマURLを維持し、Issueからページや見出しへリンクする運用案です。

## 引き継いでいる条件

会社アカウントは登録・復旧・開発運用にも使わず、個人メール以外の方法を優先します。個人メール／個人OAuthは許容する場合の代替案です。無料プランと課金契約の無料利用量を区別し、公式確認・設計提案・実機未検証を分けています。

要件の背景には未マージのPR #1の特定コミットも参照しており、確定仕様とは扱っていません。比較資料のマージと技術採用は別の判断です。Issueへの投稿・設定変更・契約・デプロイは実施していません。

## 調査レビュー

別エージェントへGPT-6.1 Terraを指定して独立レビューを依頼し、公式情報の確認と完成原稿の再レビューを行いました。ClerkのDevice Trust／登録フロー、SupabaseのDB容量・配信経路、課金登録の条件等を修正しています。結果の要点と出典は [sources.html#review](docs/sources.html#review) に掲載。モデルの判断そのものは一次情報や実機検証の代替にしていません。

## HTMLの確認結果

2026-10-30 JSTに、ローカルHTTP配信とChromiumで確認しました。

- 全16ページを幅1440px・390px・320pxで表示し、ページ全体の横はみ出しがないことを確認。
- モバイル目次、構成案への移動、出典リンクによる補足の展開を確認。
- 計算機の30人・50人・写真なし・不正入力・初期値への復帰を確認。30人のDB年間増分は65.7MB、写真とテキストの月転送は4.86GBという計算例と一致。
- ページ内・ページ間のリンク、共通アセット、重複ID、JavaScriptエラーを確認。閲覧時の外部リソース読込・データ送信はなし。
- HTMLの再生成が同じ内容になることを確認。

これは資料の表示と計算機の確認です。各候補サービスの本番認証・課金・権限・バックアップ復元の試作は未実施です。iOS Safari等の実機とfile://配信はこの環境では確認していません。

## 公開用と編集用の配置

- `docs/`：Pages配信用のHTML・CSS・JavaScript・SVGと`.nojekyll`。
- `scripts/`：HTMLを生成するPython。Pagesでは実行しません。
- `content/`：調査メモと出典。

生成後のHTMLも同じPRに含めます。公開は以下のActionsフローで行います。

## PRプレビューと正式版の自動公開

AIには、同じリポジトリ内のブランチで修正し、原稿と生成HTMLをまとめてPRにするよう依頼します。PRのチェックが成功すると、公開後に自動コメントへプレビューURLが表示されます。修正をpushすると同じURLが更新され、マージまたはクローズするとプレビューを削除します。

| 処理 | 担当するファイル |
| --- | --- |
| PR・mainの生成、リンクとID、生成漏れ、公開処理のテスト | `.github/workflows/docs-build.yml` |
| 成功したPRビルドの公開、mainの正式版更新、終了したPRの削除 | `.github/workflows/docs-publish.yml` |
| 静的ファイルの検査 | `scripts/check_html.py` |
| プレビューの保存・組立、公開後のコメント更新 | `scripts/publish_pages.py` |
| 古いビルド・複数PR・削除・アーカイブ境界等のテスト | `tests/test_pages.py` |

正式版のURLは [https://chuka57.github.io/doukin-docs/](https://chuka57.github.io/doukin-docs/) のままです。PR #2ならプレビューは `https://chuka57.github.io/doukin-docs/pr-preview/pr-2/` になります。プレビューも一般公開です。フォークからのPRはチェックのみ行い、プレビューは公開しません。

### 初回だけ必要な設定

このフローをmainへマージしてから、管理権限のある人が次を行います。

1. **Settings → Pages → Build and deployment → Source** を **GitHub Actions** に変更します。`gh-pages` を公開元として指定する方式ではありません。
2. **Settings → Environments → github-pages** で、デプロイを許可するブランチを **main** にします。毎回の手動承認を不要にする場合はRequired reviewersを設定しません。
3. **Actions → Publish docs and PR previews → Run workflow → main** で初回公開します。設定変更前に公開ジョブが失敗していた場合も、この操作で再実行できます。
4. 既存のPRは、そのブランチに変更をpushするか **Docs build** の実行を再実行して、ビルド完了後のプレビューコメントを確認します。導入前に作成されたPRでビルド実行自体がなければ、空コミットでも起動できます。

組織でActionsを制限している場合は、使用している公式 `actions/*` を許可し、ワークフローで宣言した権限を使えることを確認します。権限はジョブごとに指定し、個人アクセストークンや追加シークレットは不要です。設定はこのPRの作成だけでは切り替わりません。

### 普段の操作と、失敗したとき

- 原稿を変更したら `python scripts/build_html.py` を実行し、生成HTMLもコミットします。CIでは生成し直した結果との差分をチェックするので、原稿だけの更新は失敗します。
- PRコメントのURLは同じままで、対象PRコミットをコメントに記載します。プレビューはチェック時のmainとのマージ結果です。ビルドに失敗した場合は最後に公開できた版が残るため、対象コミットと最新チェックの結果を確認します。
- ビルド失敗は **Docs build**、公開・コメント失敗は **Publish docs and PR previews** のログを確認し、修正後にpushするか失敗した実行を再実行します。コメントはPagesの公開成功後に更新します。
- 一時障害後の全体再公開・クローズ済みプレビューの再整理は **Publish docs and PR previews → Run workflow → main** で行えます。コメント更新だけが失敗した場合は、該当実行の失敗ジョブを再実行します。
- `gh-pages` は生成済みサイトとプレビューの保存専用ブランチで、自動作成します。直接編集・削除しません。正式版は毎回mainから生成し、開いている他のPRのプレビューを保存したまま一括配信します。公開処理は同時実行を直列化します。
- PRのビルド成果物は７日で期限切れになりますが、公開済みプレビューは `gh-pages` に残るため期限では消えません。未公開のまま７日経過した場合はDocs buildを再実行します。PRを閉じると保存済みプレビューも削除します。
- 公開側はmainのコードだけを実行します。PRのPythonは読取専用のビルドで実行し、公開側は成果物を静的ファイルとして検査・配置します。PR側へ書込トークンや本番のシークレットは渡しません。

ローカル確認はPython 3の標準ライブラリだけで実行できます。

```sh
python -m unittest discover -s tests -v
python scripts/build_html.py
python scripts/check_html.py docs
git diff --exit-code -- docs
```

公式ActionはコミットSHAで固定しています。更新はSHAとバージョンコメントを同じPRで変更し、チェック・公開・クローズ削除を確認します。[Pagesの公開設定](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)と[公式deploy-pages](https://github.com/actions/deploy-pages)も参照してください。
