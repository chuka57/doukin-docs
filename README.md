# doukin-docs

同期向け筋トレアプリ doukin の技術検討資料です。掲載内容は検討中・未採用の案を含みます。

## 閲覧

公開用HTMLは `docs/index.html` に配置します。GitHub Pages設定後のURLは https://chuka57.github.io/doukin-docs/ です。

## Pagesの設定

資料のPRをmainにマージした後、Settings → Pagesで Source を Deploy from a branch、Branch を main、Folder を /docs にして保存します。

以後、mainのdocs配下を更新するとサイトへ反映されます。HTML・assetsは一緒に更新してください。

## 更新

生成元もdocs配下に置き、次のコマンドでHTMLを更新します。

```sh
python docs/build_html.py
```

資料の掲載と技術採用は別の判断です。公開リポジトリなので、本文・生成元・履歴は誰でも閲覧できます。
