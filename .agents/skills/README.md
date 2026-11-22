# 資料作成スキル

このリポジトリで使う3つのスキルを、参照資料・スクリプト・テンプレート・ライセンスと一緒に管理します。ユーザーフォルダへの個別インストールは不要です。

| スキル | 用途 | 配布元 |
| --- | --- | --- |
| [yomiyasu](yomiyasu/SKILL.md) | 意味・条件・確度を保って日本語を推敲する | [nanaism/yomiyasu](https://github.com/nanaism/yomiyasu) |
| [visual-explainer](visual-explainer/SKILL.md) | 構成・比較・手順を図解中心のHTMLにする | [nicobailon/visual-explainer](https://github.com/nicobailon/visual-explainer) |
| [stack-diagram](stack-diagram/SKILL.md) | 公式ロゴ・グループ・矢印でアーキテクチャ図を作る | [caru-ini/stack-diagram](https://github.com/caru-ini/stack-diagram) |

`stack-diagrams` と呼んでいたスキルの正式名は `stack-diagram` です。既存の `content/stack-diagram.html` も、この配布元のテンプレートを使っています。

## エージェントから使う

Codexでは、このリポジトリを作業フォルダとして開くと `.agents/skills/` がスキルの探索対象になります。追加前から開いていたセッションでは、新しいセッションを開始して読み込んでください。名前を指定する例は次のとおりです。

```text
$yomiyasu で、content/overall-spec.html の本文を意味を変えずに推敲して。
$visual-explainer を使って、構成案の違いを図解するHTML資料を作って。
$stack-diagram を使って、WorkersとD1の構成図を作って。
```

Claude Code向けには `.claude/skills/<名前>` から同じディレクトリへの相対シンボリックリンクを配置しています。`/yomiyasu`、`/visual-explainer`、`/stack-diagram` で指定します。Windows等でリンクが通常のテキストファイルとしてチェックアウトされた場合は、Gitのシンボリックリンク対応を有効にしてチェックアウトし直すか、各スキルの `SKILL.md` をパスで指定して読ませてください。

その他のエージェントでも、必要な `.agents/skills/<名前>/SKILL.md` を明示して読ませられます。利用可能なツールは各エージェントの実行環境に従います。スキルの同梱だけでMCPサーバーや外部サービスが有効になることはありません。

## このリポジトリでの作成手順

見た目は [AGENTS.md](../../AGENTS.md) の「HTML資料の作り方」を目安にします。既存の目次・案内キャラクター・雰囲気を引き継ぎ、図解や余白は内容に合わせて整えてください。

1. [AGENTS.md](../../AGENTS.md) と、使うスキルの `SKILL.md` を読む。必要なスキルだけを選ぶ。
2. 本文・図の原稿を `content/`、共通部品を `scripts/`、公開画像を `docs/assets/` に置き、既存の生成処理へ組み込む。
3. 共通CSS・日本語の表記・出典に合わせる。推奨・比較用の仮定・未検証事項の区別を保つ。
4. 閲覧時に外部リソースを取得しない形へ整える。`visual-explainer` の生成HTMLに入るGoogle Fontsや、追加したCDN参照をローカルのフォント・共通CSS・同梱アセットへ置き換える。`stack-diagram` のロゴとフォントは作成時に埋め込む。
5. `python scripts/build_html.py` と `python scripts/check_html.py docs` を実行し、ブラウザで表示を確認する。原稿と生成物を同じPRに含める。

既存ページのURL・見出しID・共通目次・版表示は維持します。外部ギャラリーへの投稿は資料作成に含めません。

## 必要な実行環境

既存資料の生成・検査は、引き続きPython標準ライブラリだけで実行できます。以下はスキルの補助ツールを使うときに必要です。

- **yomiyasu**：Python 3.9以降、標準ライブラリだけで動作します。検査の引数は同梱スクリプトのヘルプを確認してください。HTML全体を文章として一括変換せず、本文を対象にし、タグ・URL・識別子を保ちます。
- **visual-explainer**：通常のHTMLレンダリングにはNode.js 20以降を使用します。表示確認には `playwright-core` とChromiumまたはGoogle Chromeが必要です。MCP・PPTX・動画用の追加依存は、それぞれの同梱ガイドと配布元の案内を参照してください。
- **stack-diagram**：Python 3.9以降。HTMLへの埋め込み処理は標準ライブラリだけで動作します。新しいロゴの取得にはネットワーク、PNG出力にはPython版PlaywrightとChromium、日本語の描画には日本語フォントが必要です。

リポジトリ直下から、補助ツールを確認できます。

```sh
python .agents/skills/yomiyasu/scripts/yomiyasu_lint.py --help
python .agents/skills/yomiyasu/scripts/yomiyasu_check.py --help
```

`visual-explainer` の表示確認用依存は、必要な環境で次のように導入できます。

```sh
npm install --no-save --package-lock=false --prefix .agents/skills/visual-explainer playwright-core
npm exec --prefix .agents/skills/visual-explainer -- playwright-core install chromium-headless-shell
```

`stack-diagram` のPNG出力用には、Pythonの仮想環境に導入します。

```sh
python -m venv .venv
.venv/bin/python -m pip install playwright
.venv/bin/python -m playwright install chromium
```

Windowsでは `.venv/bin/python` を `.venv/Scripts/python.exe` に読み替えます。Linuxでブラウザの共有ライブラリが不足する場合は、環境の管理方法に従って追加してください。依存のインストールを通常のHTMLビルドやCIへ追加する必要はありません。

## 配布元・ライセンス・更新

[sources.json](sources.json) に、取り込んだ配布元・コミットSHA・元のディレクトリを記録しています。Git submoduleやユーザーフォルダへのリンクを使わず、固定した内容を同梱しています。

- 各スキルの `LICENSE` を保持しています。`visual-explainer/LICENSE` は配布元ルートから追加しています。
- yomiyasuの `UNICODE-LICENSE.txt`、visual-explainerの `kit/vendor/PELE-LICENSE`、stack-diagramのフォント用 `assets/fonts/OFL-*.txt` も保持しています。
- 新しく取得するロゴの利用条件とクレジットは、それぞれの提供元に従います。

更新時は配布元の変更を確認し、採用するコミットを固定して、`sources.json` の `path` にあるディレクトリを一式置き換えます。`additional_files` がある場合は、そのファイルも配布元からコピーします。`sources.json` のコミットSHAを更新し、相対リンク・テンプレート・スクリプトが揃っていることと、既存のHTML生成・検査が通ることを確認してPRにします。

配布元のファイルは原則そのまま保持し、このリポジトリ向けの使い方はこの案内とルートの `AGENTS.md` に記載します。
