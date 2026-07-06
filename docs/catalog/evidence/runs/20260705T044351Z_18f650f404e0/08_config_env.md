# Config / Env Inventory

- AIP_HEALTH_ROUTE
  found_in:
    - src/serving/predictor.py:L21
  value: redacted (name/参照のみ)
  requiredness: unknown
- AIP_HTTP_PORT
  found_in:
    - src/serving/predictor.py:L23
  value: redacted (name/参照のみ)
  requiredness: unknown
- AIP_PREDICT_ROUTE
  found_in:
    - src/serving/predictor.py:L22
  value: redacted (name/参照のみ)
  requiredness: unknown
- AIP_STORAGE_URI
  found_in:
    - src/serving/predictor.py:L31
  value: redacted (name/参照のみ)
  requiredness: unknown
- DISCORD_WEBHOOK_URL
  found_in:
    - src/runner/ops/costs.py:L107
  value: redacted (name/参照のみ)
  requiredness: unknown
- KBC_CONFIG_PATH
  found_in:
    - src/config.py:L7
    - src/runner/experiment/train.py:L167
    - src/runner/experiment/tune.py:L53
  value: redacted (name/参照のみ)
  requiredness: unknown
- MODEL_DIR
  found_in:
    - src/serving/predictor.py:L28
  value: redacted (name/参照のみ)
  requiredness: unknown
- PYTHONPATH
  found_in:
    - infra/Dockerfile:L19
  value: redacted (name/参照のみ)
  requiredness: unknown

## Scan Limitations

- required/optional は未確認。
- default 値は解析していない。
- secret 値は含めない。
