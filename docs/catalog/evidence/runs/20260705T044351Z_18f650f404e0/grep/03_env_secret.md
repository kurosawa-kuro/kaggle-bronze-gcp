# grep: env_secret

evidence_id: ev.grep.env_secret
description: env / secret / credential

- doppler.yaml:L9: # 非機密の設定値は conf/config.yaml、ローカルだけの秘密情報は conf/secret.yaml に置く。
- doppler.yaml:L10: # conf/secret.yaml は .gitignore で除外し、コミットしない。
- doppler.yaml:L19: # ML_KAGGLE_TOKEN                 # Kaggle API トークン（make download / submit で使用）
- doppler.yaml:L20: #                                 # Makefile で KAGGLE_API_TOKEN にマッピングして kaggle CLI へ渡す
- doppler.yaml:L25: # AI_DEEPSEEK_API_KEY
- doppler.yaml:L26: # AI_OPENAI_API_KEY
- doppler.yaml:L27: # AI_PERPLEXITY_API_KEY
- doppler.yaml:L33: # AUTH_N8N_OWNER_PASSWORD       # 同上
- doppler.yaml:L36: # COOKIE（スクレイピング用 Cookie / 実行時に env/secret/ へ materialize）
- doppler.yaml:L46: # DB_NEON_API_KEY               # Neon API
- doppler.yaml:L49: # DB_TURSO_AUTH_TOKEN           # 同上
- doppler.yaml:L51: # DB_TURSO_HERMES_AUTH_TOKEN    # 同上
- doppler.yaml:L56: # INFRA_DOPPLER_AUTH_TOKEN
- doppler.yaml:L57: # INFRA_NGROK_AUTH_TOKEN        # 準備中(librechat skeleton)
- doppler.yaml:L59: # INFRA_PGADMIN_PASSWORD
- env/secret.example.yaml:L2: # env/secret.yaml のテンプレート（この example はコミットされる）
- env/secret.example.yaml:L3: # 実値は env/secret.yaml（gitignore 済み）に入れる。値はここに書かない。
- env/secret.example.yaml:L6: # Kaggle: <redacted>
- env/secret.yaml:L8: # ML_KAGGLE_TOKEN を Doppler kuro-dev-k/dev で管理する。
- env/secret.yaml:L9: # 取得: <redacted>
- env/secret.yaml:L10: # Makefile が doppler run -- 経由で取得し KAGGLE_API_TOKEN にマッピングして kaggle CLI へ渡す。
- src/config.py:L7: _cfg_path = Path(os.environ.get("KBC_CONFIG_PATH", _ROOT / "env" / "config.yaml"))
- src/runner/experiment/train.py:L167: os.environ["KBC_CONFIG_PATH"] = str(config_path)
- src/runner/experiment/tune.py:L53: os.environ["KBC_CONFIG_PATH"] = str(config_path)
- src/runner/model/register.py:L134: res = subprocess.run(["gsutil", "cat", gs], capture_output=True, text=True, env=clean_env())
- src/runner/ops/costs.py:L107: env = os.environ.get("DISCORD_WEBHOOK_URL")
- src/runner/ops/costs.py:L110: return _load_yaml(Path("env/secret.yaml")).get("discordWebhookUrl")
- src/runner/ops/costs.py:L116: print("[cost] Discord webhook 未設定（env/secret.yaml discordWebhookUrl / env DISCORD_WEBHOOK_URL）")
- src/runner/ops/submit.py:L44: env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
- src/runner/ops/submit.py:L45: return subprocess.run(cmd, check=False, env=env).returncode
- src/serving/predictor.py:L21: HEALTH_ROUTE = os.environ.get("AIP_HEALTH_ROUTE", "/health")
- src/serving/predictor.py:L22: PREDICT_ROUTE = os.environ.get("AIP_PREDICT_ROUTE", "/predict")
- src/serving/predictor.py:L23: PORT = int(os.environ.get("AIP_HTTP_PORT", "8080"))
- src/serving/predictor.py:L28: local = os.environ.get("MODEL_DIR")
- src/serving/predictor.py:L31: uri = os.environ.get("AIP_STORAGE_URI", "")
- src/utils/bq.py:L18: return {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
- src/utils/bq.py:L36: res = subprocess.run(cmd, capture_output=True, text=True, env=clean_env())
