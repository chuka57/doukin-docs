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

Settings → PagesでDeploy from a branch、main、/docsを選択します。生成後のHTMLも同じPRに含めます。
