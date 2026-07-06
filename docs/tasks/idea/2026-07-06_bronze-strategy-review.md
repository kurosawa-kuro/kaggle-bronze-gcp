# 銅メダル実戦基盤レビュー（2026-07-06）

> 依頼: `docs/tasks/idea/プロンプト` に基づく戦略レビュー。
> 前提: `full_gcp_lgbm_001` で GCP E2E（Custom Job → GCS → BQ 台帳 → Model Registry → Batch Prediction）完走済み。
> 実戦ターゲット: ROGII wellbore geology prediction（entry 締切 2026-07-29 / final 2026-08-05。**残り3週間**）。

---

## 1. 結論

**基盤フェーズは終わった。次の勝負は「基盤の拡張」ではなく「基盤に流す中身」である。**

現状の弱点は GCP 側にはほぼない。銅メダルへの最短経路を塞いでいるのは次の4点で、すべて ML 側・運用側にある。

1. **CV 戦略が shuffle KFold / StratifiedKFold 固定**（`src/models/lgbm.py:86-89`）。ROGII は well 単位の GroupKFold が必須で、現行 CV のままではリークした CV スコアを信じて private で崩れる。これが最大のリスク。
2. **config runner が LightGBM 単体**（`train.py:176-177` で `model.name != lgbm` は明示的に reject）。`src/models/catboost_.py` / `xgboost_.py` / `ensemble.py` は存在するのに正規経路に接続されておらず、oof.parquet を貯めているのに blend する ops がない。銅圏の常套手段（LGBM+CatBoost+XGB の OOF blend）が撃てない。
3. **提出が台帳に残らない**。`make submit` は Kaggle CLI を叩くだけで、どの run_id をいつ提出し public LB が何点だったかが BigQuery に残らない。CV↔LB の相関が測れず、public LB 過学習を防ぐ判断材料が構造的に欠けている。
4. **ROGII は code competition（notebook 提出）なのに、ファイル提出経路しかない**。ここを埋めないと「48時間以内に初回提出」が ROGII では成立しない。

GCP の非対称優位はすでに実装済みの「sweep fan-out + Vizier + Spot 大型マシン + BQ 台帳」にある。これを勝率に変換する式は単純で、**ローカル勢が1晩に3実験しか回せないところを、20実験×3seed×5fold 回して、翌朝 BQ で1クエリ比較して次の一手を決める**こと。ただし並列で流す「弾」（特徴量セット×モデル種×パラメータ）が config で表現できないと fan-out は空撃ちになる。だから上記 1〜3 が P0 になる。

## 2. 現状評価

### すでに強い点（ローカル勢に対して既に優位）

| 項目 | 評価 |
|---|---|
| 同一 runner の local/Vertex 二重実行契約 | ◎ smoke→full の昇格が config 1枚。再現性の核 |
| run_id 成果物の規律（config snapshot / fold_manifest / dataset_snapshot / schema hash / oof.parquet / leakage_audit） | ◎ ここまでやるローカル Kaggler はほぼいない。blend・振り返り・ポートフォリオの全部の土台 |
| BQ `experiments` × `cost_estimates` の run_id JOIN | ○ 実験とコストが1クエリ。あとは submissions と LB スコアが入れば完成 |
| sweep fan-out（非ブロッキング並列 Custom Job）+ Vizier | ◎ 壁時計時間の圧縮装置。これが本命の武器 |
| seed 平均が正規経路に組込み済み | ○ private 安定化の基本を既に装備 |
| `make init COMP=` の 48h ブートストラップ | ○ ファイル提出型コンペなら初日提出可能 |
| コスト規律（Spot 既定・¥1000/¥5000 しきい値・Discord 通知） | ◎ 「GCP は金がかかる」批判への実証的反論になっている |

### 足りない最重要ポイント

CV 戦略の可変化（＝ ROGII 対応）と、モデル多様性＋blend。この2つが埋まらない限り、Vertex の並列度は銅確率に変換されない。

### GCP 活用が自己満足になりかけている部分

- **Batch Prediction の常用**: test 予測は学習ジョブが `test_pred.parquet` として既に出力する。Kaggle 提出目的での Batch Prediction は経路として冗長（検証完了・ポートフォリオ素材としては価値があるので「維持するが使わない」が正解）。
- **Model Registry への全 run 登録**: 提出候補 run だけ登録すれば足りる。
- **KFP train→register DAG**: 既に「粗い DAG で止める」判断済みで正しい。これ以上細分化しない。

## 3. ブロンズ取得に効く改善点ランキング

1. **P0-1: CV 戦略の config 駆動化**（group / stratified / kfold / time を `cv.strategy` + `cv.group_col` で切替）
2. **P0-2: code competition 提出経路**（run_id 成果物 → Kaggle Dataset 化 → 推論 notebook テンプレ）
3. **P0-3: マルチモデル runner + OOF blend ops**（catboost/xgboost を train.py に通し、`make blend RUN_IDS=` を新設。重み平均に加え rank averaging も実装）
4. **P0-4: 提出台帳 + CV↔LB 相関**（BQ `kaggle_ops.submissions`、public LB 自動取得）
5. **P1-1: adversarial validation の標準成果物化**
6. **P1-2: metric のプラガブル化**（rmse/auc/logloss 以外への対応。ROGII の指標対応の前提）
7. **P1-3: 特徴量セットの config 駆動化**（`features:` リストで FE を宣言 → sweep の弾にする）
8. **P1-4: 失敗 run の台帳記録**（status 列。失敗実験も資産化）
9. **P1-5: Day-0 チェックリストの実体化**（セクション9の運用フローを `.claude/skills/` の実行可能手順に落とす）
10. **P2**: BQ external table での SQL EDA、Cloud Build、英語 README・アーキ図

## 4. 改善案の整理表

| 優先度 | 改善案 | Kaggle ブロンズへの寄与 | GCP/Vertex/BQ/GCS を使う意味 | 実装コスト | 金銭コスト | 破綻条件 | 最初の具体アクション |
|---|---|---|---|---|---|---|---|
| P0-1 | CV 戦略 config 駆動化（`cv.strategy: group\|stratified\|kfold\|time`、`cv.group_col`）。fold_manifest に fold 間 group overlap 検査を追加 | **最大**。ROGII で well リークした CV は private で確実に崩れる。正しい CV は銅の前提条件 | fold_manifest.json + GCS 保存で「どの分割で出した CV か」が全 run で監査可能になり、Vertex 並列実験の比較が信用できるようになる | 小（`lgbm.py:_splits` と `train.py:_write_fold_manifest` の分岐追加、config スキーマ拡張） | ¥0 | group_col の指定ミス（well ID が train/test で非重複なのに group を切らない等）。leakage_audit で train/test の group 重複率を出して防ぐ | `configs/` に `cv.strategy` を追加し、`_splits()` に GroupKFold 分岐を実装。smoke で fold_manifest の overlap=0 を確認 |
| P0-2 | code competition 提出経路: `make package-kernel RUN_ID=` で model/ ディレクトリを Kaggle Dataset として version up し、boosters をロードして推論する notebook テンプレを生成 | **必須**。ROGII は notebook 提出型。これが無いと 48h 初回提出が成立しない | **ここが最大の非対称武器**: 重い学習（seed×fold×モデル種）は Vertex Spot で済ませ、Kaggle kernel 9h 制限内では推論だけ行う。kernel 内で学習するローカル勢に対し、持ち込める計算量が桁で違う | 中（kaggle datasets CLI ラッパ + notebook テンプレ + manifest.json 読込の推論コード。serving/predictor.py のロジックを流用可能） | ¥0 | コンペルールが外部データ/事前学習成果物の持込を禁止している場合（ROGII ルールを最初に確認）。internet-off kernel での dataset attach 手順ミス | ROGII のルール（external data / models 可否）を確認 → `src/runner/ops/package_kernel.py` を新設 |
| P0-3 | train.py のマルチモデル化（model.name: catboost/xgboost）+ `make blend RUN_IDS="a b c"`: 各 run の oof.parquet を読み、OOF 上で重み最適化（scipy or 単純グリッド）→ blended submission + BQ 記録。blend 方式は weighted mean に加え **rank averaging** を実装（AUC 系指標の定番。数行で足せてスケール差に頑健） | **大**。単発 LGBM とマルチモデル blend の差は playground 系で銅圏内外を分ける定番。既に oof.parquet を貯めているので原価回収でもある | blend の材料（oof/test_pred）が run_id レイアウトで GCS に揃っている前提が活きる。モデル種×seed の学習は sweep で Vertex に並列投入 | 中（catboost_/xgboost_ の train_cv は既存。train.py のモデル分岐と、blend ops 新設） | 実験1回あたり数十円〜（Spot n2-standard-16） | oof の fold 分割が run 間で不一致だと blend の CV が壊れる → fold_manifest の `valid_index_sha256` 一致を blend 前にアサート（既に実装済みのハッシュがそのまま使える） | `train.py:176` の lgbm 固定チェックを外し、model.name ディスパッチを実装 → `configs/catboost_baseline.yaml` を作って smoke |
| P0-4 | BQ `kaggle_ops.submissions` テーブル（run_id, submitted_at, message, cv_score, public_lb, selected_final）。`make submit` が自動 INSERT、`kaggle competitions submissions` で LB スコアを回収する `make lb-sync` | **大**（守りの要）。CV↔LB 相関が数字で見えると「public に釣られた提出」を構造的に防げる。final 2 提出の選定を CV ベースで行える | experiments × cost_estimates × submissions が run_id で 3-way JOIN でき、「この1点の改善に何円・何実験かかったか」まで1クエリ。ローカル勢のスプレッドシート管理と決定速度が違う | 小（logger.py と同型のテーブル + submit.py への追記 + lb-sync ops） | ¥0（BQ 無料枠内） | 手動提出（Web UI）が混ざると台帳が欠ける → lb-sync が CLI 経由で全提出を吸えば穴は埋まる | submissions テーブルの DDL を `utils/bq.py` 系に追加し、submit.py の成功時に INSERT |
| P1-1 | adversarial validation を標準成果物に: train/test 識別の AUC + 上位 drift 特徴を `adversarial_audit.json` として毎 full run に出力 | **中〜大**。train/test 分布ずれの早期検知は private 安定化に直結。ROGII のような well/空間データではほぼ必須の診断 | 全 run に自動付与され GCS に残るので、「どの特徴を足したら drift が悪化したか」を後から BQ/成果物で追える | 小（LGBM で binary 1本。既存 train_cv 流用で 30 行程度） | 微小（full run に数分追加） | AUC が高い＝即悪ではない（時系列コンペ等）。機械的に特徴を落とす自動化はしない。診断のみ | train.py の成果物書き出し群に `_write_adversarial_audit()` を追加 |
| P1-2 | metric プラガブル化: `evaluate.py` の 3 分岐（rmse/auc/logloss）を registry 化し、MAE/RMSLE/custom を追加可能に | **中**。ROGII の評価指標が現行 3 種に無い場合、これが無いと CV と LB の最適化対象がずれる | Vizier の目的値・BQ の cv_score の意味が正しくなる（基盤全体の前提） | 小 | ¥0 | custom metric の実装ミス → コンペ公式実装 or sklearn と突合するユニットテストを1本置く | ROGII の指標を確認し、`evaluate.py` を dict ディスパッチに書換え |
| P1-3 | 特徴量セットの config 駆動化: `features: [base, stellar_colors]` のように宣言し、featurize.py が features/ 配下の関数を順適用。FE バージョンが config snapshot に自動記録される | **大**（実験回数の質を決める）。銅圏の差は HPO ではなく FE で付く。FE セット×パラメータを sweep の弾にできて初めて Vertex 並列が FE 探索に使える | **fan-out の弾倉**。`make sweep CONFIGS="fe_a.yaml fe_b.yaml fe_c.yaml"` で FE の A/B/C を一晩で並列検証。どの FE がどのスコアかは config snapshot + BQ で完全追跡 | 中（featurize.py に registry パターン。features/stellar.py の手動 wiring を置換） | sweep 1回数十円〜数百円 | FE 関数が encode() 前提/後提かの規約が曖昧だと事故る → 「features/ の関数は encode 前の raw df を受ける」を規約として docstring とテストで固定 | featurize.py に `FEATURE_REGISTRY` を実装し、stellar.py を最初の登録例として移植 |
| P1-4 | 失敗 run も BQ に記録（experiments に status/error 列 or 別テーブル）。sweep の失敗を `make compare` で可視化 | **小〜中**。「何が失敗したか」が消えると同じ失敗を繰り返す。夜間 fan-out の翌朝 triage が速くなる | Vertex ジョブの失敗は GCP コンソールに散らばる。BQ に寄せて初めて実験台帳が「全実験」台帳になる | 小 | ¥0 | — | train.py の except 経路と vertex_run の失敗検知から log_run(status="failed") を呼ぶ |
| P1-5 | Day-0 チェックリストの実体化: セクション9の Day 0 フロー（init → ルール確認 → CV 設計 → adversarial validation → smoke → 初回提出）を `.claude/skills/comp-day0/SKILL.md` の実行可能手順に落とし、`docs/competitions/_template.md` に CV 設計・提出形式・external models 可否の必須記入欄を追加 | **中**。48h 初回提出の実戦力は「手順が頭にある」ではなく「手順が実行可能な形で存在する」で決まる。判断漏れ（code comp 見落とし・group 構造見落とし）を構造的に防ぐ | GCP 固有ではないが、既存スキル運用（create-task / execute-task）と同じ流儀に乗るので導入コストが低い | 小（既存フローの文書化。新規コードなし） | ¥0 | チェックリストが長すぎると形骸化する → Day 0 の判断項目（提出形式 / CV 戦略 / 指標 / 締切）だけに絞る | セクション9の Day 0 部分を SKILL.md として切り出し、ROGII 参戦時に初回実戦テストする |
| P2-1 | raw data の BQ external table 化（GCS 上の CSV/parquet を SQL で EDA） | 小〜中（数百万行級コンペでのみ効く） | pandas に載らないデータの GROUP BY / window 集計を BQ に投げられる。ROGII の well ログが大きい場合に効く | 小（Terraform に external table 追加） | 無料枠内 | 小データコンペでは工数の無駄。データを見てから判断 | ROGII データサイズを見てから着手判断 |
| P2-2 | Cloud Build で push→build-push 自動化 | ほぼ 0（快適性のみ） | ポートフォリオ価値はある | 小 | 微小 | コンペ期間中にやる価値はない | コンペ後 |
| P2-3 | 英語 README + アーキ図 + full_gcp_lgbm_001 のケーススタディ記事化 | 0（ポートフォリオ専用） | PM/コンサル路線の証拠資産（実務語彙: lineage, cost governance, reproducibility） | 小〜中 | ¥0 | — | コンペ後、ROGII の実戦記録を含めて書く方が強い |

## 5. 今すぐやるべき P0（今週 = 7/6〜7/13）

順番に意味がある。

1. **P0-1 CV 戦略 config 駆動化**（1日）— ROGII 参戦の前提。GroupKFold + fold_manifest の group overlap 検査まで。
2. **P0-3 マルチモデル + blend**（1〜2日）— catboost を train.py に通し、`make blend` を新設。playground-series-s6e6 で LGBM+CatBoost blend を実際に1回提出して経路を検証。
3. **P0-4 提出台帳**（半日）— submissions テーブル + lb-sync。上の blend 提出を最初のレコードにする。
4. **P0-2 kernel パッケージング**（1〜2日）— ROGII ルール確認 → package-kernel ops。**7/13 までに ROGII entry + 初回 notebook 提出**まで行けるのが理想（entry 締切 7/29 に対し 2 週間のバッファ）。

## 6. 次にやるべき P1（ROGII 参戦後、7/13〜）

- **P1-2 metric 対応**は ROGII の指標次第で P0 に繰上げ（初回提出前に必要なら即実装）。
- **P1-1 adversarial validation** — ROGII の train/test 分布ずれ診断として初週に1回走らせる。
- **P1-3 FE registry** — ROGII の well 系 FE（深度方向 rolling、typewell 対応付け等）を弾として量産し、sweep で夜間並列検証するために必要。実質 ROGII 2 週目の主戦場。
- **P1-4 失敗 run 記録** — 夜間 sweep 運用が始まったタイミングで。
- **P1-5 Day-0 チェックリストのスキル化** — ROGII の Day 0 を実際にやりながら SKILL.md に固めるのが最も安い（机上で書かない）。

## 7. 後回しでよい P2

BQ external table（データを見てから）、Cloud Build、英語ポートフォリオ整備。いずれも ROGII final（8/5）以降。

## 8. やらない方がよいこと

| 項目 | 理由 |
|---|---|
| Endpoint 常駐・Model Monitoring | Kaggle に推論 API は不要。常駐コストだけ発生。現方針（コードのみ・実デプロイしない）を維持 |
| Feature Store | 単一コンペ・単一人・batch 特徴量に store は過剰。config 駆動 FE registry（P1-3）で足りる |
| KFP DAG の細分化（ingest/featurize/train/score 分割） | GCS 往復が増えて反復速度が落ちる。ADR 0002 の「粗い DAG で止める」判断が正しい |
| Batch Prediction を Kaggle 提出の正規経路にする | test_pred.parquet が学習ジョブから既に出る。二重経路は運用コスト。検証済みの現状で凍結 |
| 全 run の Model Registry 登録 | 提出候補のみ登録。版の洪水は判断を遅くする |
| 分散 Optuna / Ray / Spark | 単機 + Vizier で足りる規模。ADR 0002 どおりスコープ外を維持 |
| HPO のさらなる深掘り（trial 数増） | 既に Optuna best が入っている。ここから先の限界効用は FE・blend より一桁小さい。**HPO はコンペ終盤の最後の絞り込みに1回**でよい |
| Vertex Experiments / ML Metadata への移行 | BQ 統一（ADR 0002）が JOIN 可能性で勝る。再検討不要 |

## 9. 48時間ブロンズチャレンジ運用フロー案

> このフローは文書のままにせず、Day 0 部分を `.claude/skills/comp-day0/` の実行可能手順に落とす（P1-5）。

**Day 0（0〜4h）: 偵察と CV 設計 — ここだけは人間の仕事**
1. `make init COMP=<slug>`（download→正規化→config 下書き→doc 生成）
2. ルール確認: code comp か / external models 可否 / 指標 / final 2 提出
3. **CV 設計の決定**（最重要判断）: group 構造・時系列性の有無 → `cv.strategy` を config に固定。adversarial validation を1本流して train/test ずれを見る
4. metric が未対応なら evaluate.py に追加

**Day 0（4〜12h）: ローカルで最小ループ**
5. `make smoke` → `make train-local` で LGBM ベースライン
6. leakage_audit / fold_manifest / feature_importance を確認
7. **初回提出**（ファイル型: `make submit` / code 型: `make package-kernel` → notebook 提出）。CV と public LB の差を submissions 台帳に記録 — この差が以後の羅針盤

**Day 1: Vertex に離陸**
8. `make stage-data` + `make build-push`
9. FE 案 3〜5 個を config 化 → `make sweep CONFIGS="..."` で夜間 fan-out（Spot）
10. 並行で catboost/xgboost の config も同じ sweep に混ぜる

**Day 2: 収穫と blend**
11. 朝 `make compare` で1クエリ triage → 勝ち FE を採用
12. 上位 run を `make blend` → 2 回目提出
13. 以後のループ: 昼 = FE 仮説出し（ローカル EDA）、夜 = Vertex fan-out、朝 = BQ triage → 提出は CV 改善時のみ。**public LB は1日1回しか見ない**と決める

**最終週**: Vizier で最終 HPO 1回 → seed 増し（5 seed）で最終学習 → final 2 提出は「CV ベスト」と「CV/LB バランス」の2枚（submissions 台帳の selected_final に記録）

## 10. ポートフォリオとしての訴求点

PM/コンサル路線（キャリア戦略）に合わせるなら、「Vertex を使えます」ではなく**意思決定と統制の物語**として見せる。

1. **コストガバナンス**: 予算しきい値（¥1000/¥5000）を BQ + Discord 通知で機械化し、Spot 既定で実験単価を数十円に抑えた — 「クラウド ML は高い」への定量的反論
2. **再現性の監査証跡**: config snapshot / fold manifest hash / schema hash / leakage audit が全 run に自動付与 — 規制産業の ML 監査要件と同じ語彙で語れる
3. **意思決定の高速化**: 実験×コスト×提出が BigQuery で 3-way JOIN、翌朝1クエリで次の一手 — 「実験管理をスプレッドシートから台帳に上げた」話は実務にそのまま転用可能
4. **アーキテクチャ判断の記録**: ADR で「採用してから削る」方針と、実際に削ったもの（Endpoint 常駐、KFP 細分化）を残している — 技術選定の説明能力の証拠
5. **非対称戦略そのもの**: 「過剰と言われる基盤を、kernel 9h 制限下で事前計算済みモデルを持ち込む武器に変換した」— ROGII の実戦記録が付くと一気に説得力が出る

---

## 付記: 小さいが直しておきたい点

- `train.py:_trained_mask` が `oof != 0` で学習済み判定をしており、真の予測値 0 と未学習を区別できない。max_folds 使用時（smoke）限定の仕組みなので実害は小さいが、mask を fold index から直接構築する方が安全。
- `metrics.json` に fold 別スコアと std が残らない（stdout には出る）。CV std は「LB との乖離をどこまで許容するか」の判断材料なので、seed_scores と同様に fold_scores も永続化したい（P0-4 とセットで）。
- `run.py` の BEST_PARAMS ハードコードは config runner と二重管理。旧経路として凍結を明示するか、`make run` を train-local の alias にして退役させる。
