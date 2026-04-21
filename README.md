# Research Workspace

このリポジトリは、研究テーマ
`生理反応と主観的意味づけの可変性`
を進めるための実務用ワークスペースです。

目的は 3 つです。

1. 毎日の研究を `logs/daily/` に残す
2. H1 / H2 / H3 ごとの検討を `research/` に蓄積する
3. 日々のログから `slides/outlines/` にスライド素案を起こせるようにする

## 研究の核

- `H1` 既存研究のメタレビューによる条件整理
- `H2` WESAD を軸にした公開データ解析による生理 - 主観ラベルのズレ検証
- `H3` 外在化インターフェースによる意味づけ差異の観察

補足:

- 研究計画の主軸は WESAD
- repo の構造は CASE などの追加比較にも対応できるようにしてある

詳細は [docs/research-plan.md](/c:/Projects/prpporsal/docs/research-plan.md) に整理しています。

## 2026 年の中心課題

1. H1 のメタレビュー
2. H2 の WESAD 論文
3. `n=20〜30` の追試設計
4. Lazarus 理論との接続とモデル化

この 4 本が毎週少しずつ前に進むように repo を使います。

## Language Convention

- 研究ログ: 日本語
- 日々の相談や進捗共有: 日本語でよい
- スライド素案と発表用の文面: 英語

毎回チャットで言い直さなくて大丈夫です。
この repo では、
`記録は日本語、対外発表のスライドは英語`
を既定ルールとして扱います。

進捗共有の型は [docs/chat-checkin-template.md](/c:/Projects/prpporsal/docs/chat-checkin-template.md) を使えます。

## ディレクトリ

```text
docs/                研究計画と運用ガイド
logs/daily/          日次研究ログ
logs/weekly/         週次レビュー
references/          論文メモや文献整理
research/            H1/H2/H3 ごとの作業場
slides/outlines/     発表用スライド素案
status/              現在地と次アクション
templates/           ログ・レビュー・実験メモの型
scripts/             ログ作成とスライド素案生成
```

## 基本運用

### 1. その日のログを作る

```powershell
python scripts/new_daily_log.py --date 2026-04-21 --theme H1 H2 --focus "WESADのズレ定義とレビュー軸を詰める"
```

### 2. 研究した内容を埋める

最低限、以下だけ埋めれば後で再利用しやすくなります。

- `今日の問い`
- `今日やったこと`
- `得られたこと`
- `スライド化メモ`
- `次にやること`

### 3. スライド素案を作る

```powershell
python scripts/build_slide_outline.py --from 2026-04-21 --to 2026-04-27 --title "研究立ち上げ週の進捗"
```

### 4. 次にやることを確認する

- 現在地: [status/current_focus.md](/c:/Projects/prpporsal/status/current_focus.md)
- 直近の行動: [status/next_actions.md](/c:/Projects/prpporsal/status/next_actions.md)

## 運用のコツ

- 1 日の終わりに `スライド化メモ` を 3 行だけでも残す
- 図にしたいものは `参照・成果物` にファイル名を書く
- H1 / H2 / H3 のどれに効く作業かを front matter で必ず残す
- H2 を触る日は、WESAD を基準にして、必要なら CASE などの比較対象も本文に残す
- 週末に `slides/outlines/` を 1 本作る
- 進捗をチャットで日本語で送ってくれれば、その内容をログと英語スライド素案に落とし込む

## 今のおすすめ

最初の 1 週間は、広げるよりも以下を固めるのが良いです。

1. H1 のレビュー観点を 1 枚に固定する
2. H2 の WESAD 解析手順と `ズレ` の定義を書く
3. Lazarus 理論との接続を 1 ページで整理する
4. H3 の最小プロトタイプを 1 つに絞る

更新の起点は [status/next_actions.md](/c:/Projects/prpporsal/status/next_actions.md) を見れば追える状態にしています。
