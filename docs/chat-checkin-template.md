# Chat Check-in Template

以下を日本語でそのまま送れば十分です。

```text
今日の焦点:

今日やったこと:

得られたこと:

困りごと:

次にやること:

参照ファイルや図:

指導教員として見てほしい点:

締切や予定:
```

短くても大丈夫です。
Codex 側で次を行います。

1. `logs/daily/` の研究ログへ整理
2. `logs/daily_weekly_report/` の週報 Weekly Report 形式を毎日生成
3. 必要なら `slides/outlines/` の英語スライド素案へ変換
4. 次にやるべきことを提案
5. 指導教員モードで優先順位とリスクを返す

補足:

- 固定されるべきものは `研究全体の問い`
- 日々変わってよいものは `今日の焦点`
- 研究の中核は [status/research_master_overview.md](/c:/Projects/prpporsal/status/research_master_overview.md) で管理する

