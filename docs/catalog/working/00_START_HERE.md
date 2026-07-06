# START HERE — この Evidence Pack の使い方

> これは `dcm` が自動生成した**作業誘導**。この Pack は観測事実にすぎない。
> **成果を出すには下の手順を上から実行する**。放置すると機能しない。

- profile: `infra+node+python` / files: 105 / symbols: 139（test 0） / env参照: 8 / static signal hits: 217
- 鮮度: ✅ **fresh** — 対象の git commit に固定されている。通常どおり利用してよい。

## 次にやること（順に）

- [ ] 1. **鮮度を確認**: [evidence/00_evidence_freshness.md](./evidence/00_evidence_freshness.md)。fresh でなければ以降は仮説扱い。
- [ ] 2. **調査候補を掴む**: [evidence/30_static_signal_hits.md](./evidence/30_static_signal_hits.md)（観測シグナル。決定ではない）。
- [ ] 3. **差分だけ見る**（2回目以降）: [evidence/09_diff_evidence.md](./evidence/09_diff_evidence.md)。全体でなく差分審査に使う。
- [ ] 4. **調査結果を作る**: `cargo run -- investigate --api <対象パス>` で LLM enrichment 済み findings を作る。
- [ ] 5. **LLM prompt を作る**: `cargo run -- pack <対象パス>` で investigated findings 入り prompt pack を作る。
- [ ] 6. **draft を作る**: `cargo run -- draft --api <対象パス>` で Decision Catalog draft を作る。
- [ ] 7. **機械検査**: `cargo run -- check <対象パス>` で evidence_ref・secret 混入・鮮度を検証。
- [ ] 8. **advice 混入を確認**: 判断カタログに `next_action` 等の前向き処方が混ざっていないか確認する。task / チェックリスト生成は別プロジェクトで扱う。

## 守るルール

- grep no-hit を「存在しない」と読まない（[evidence/grep/99_no_hits.md](./evidence/grep/99_no_hits.md)）。
- evidence_ref のない断定をしない。
- `99_scan_limitations.md` の限界を無視して断定しない。
- secret 値を復元・出力しない（[evidence/98_redaction_report.md](./evidence/98_redaction_report.md)）。

---
再生成: 親 repo で `cargo run -- scan infra+node+python <対象パス>`（この Pack は再生成可能・stale 化する）。
