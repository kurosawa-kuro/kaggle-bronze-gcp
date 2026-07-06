# grep: auth_permission

evidence_id: ev.grep.auth_permission
description: auth / permission / role

- doppler.yaml:L30: # AUTH（認証・ログイン）
- doppler.yaml:L32: # AUTH_N8N_OWNER_EMAIL          # n8n オーナーアカウント(保管用・env消費なし)
- doppler.yaml:L33: # AUTH_N8N_OWNER_PASSWORD       # 同上
- doppler.yaml:L49: # DB_TURSO_AUTH_TOKEN           # 同上
- doppler.yaml:L51: # DB_TURSO_HERMES_AUTH_TOKEN    # 同上
- doppler.yaml:L56: # INFRA_DOPPLER_AUTH_TOKEN
- doppler.yaml:L57: # INFRA_NGROK_AUTH_TOKEN        # 準備中(librechat skeleton)
- src/runner/experiment/hp_tune.py:L44: service_account = pcfg.get("vertexServiceAccount")
- src/runner/experiment/hp_tune.py:L113: run_kwargs = {"service_account": service_account} if service_account else {}
- src/runner/experiment/vertex_run.py:L42: service_account: str | None = None,
- src/runner/experiment/vertex_run.py:L61: service_account = service_account or project_cfg.get("vertexServiceAccount")
- src/runner/experiment/vertex_run.py:L107: "service_account": service_account,
- src/runner/experiment/vertex_run.py:L124: kwargs = {"service_account": service_account, "timeout": int(timeout_hours * 3600)}
- src/runner/experiment/vertex_run.py:L148: service_account=args.service_account,
