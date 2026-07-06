# Redaction Report

status: passed
redacted_count: 3

checked_keywords:
  - secret
  - token
  - password
  - api_key
  - apikey
  - key

scope:
  - env_secret grep の代入形 (`KEY = ...` / `KEY: ...`) の value を伏せた。

notes:
  - name / 参照箇所は残し、value のみ `<redacted>` に置換している。
  - これは網羅的な secret スキャンではない（高エントロピー文字列検出は対象外）。
  - env 参照の呼び出し（env::var / os.environ）は value を持たないため redaction 対象外。
