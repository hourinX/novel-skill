.PHONY: install install-py install-go build run-service run-cli init-data clean help

# ── 初始化（首次使用，必须先跑这一步）─────────────────
init-data:
	@if [ ! -f data/preferences.json ]; then \
	  cp data/preferences.example.jsonc data/preferences.json; \
	  echo "✅ 已创建 data/preferences.json"; \
	  echo "⚠️  请打开 data/preferences.json，删除所有 // 开头的注释行，使其成为合法 JSON"; \
	else \
	  echo "⏭  data/preferences.json 已存在，跳过"; \
	fi
	@mkdir -p data/chapters
	@echo "✅ data/chapters/ 目录就绪"

# ── Python AI 服务 ─────────────────────────────────────

install-py:
	@echo "⚠️  安装前请确保已关闭 VPN / 系统代理，否则 SSL 握手可能失败"
	pip install -r ai_service/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

run-service:
	python -m uvicorn ai_service.main:app --host localhost --port 8000 --reload

# ── Go CLI ─────────────────────────────────────────────

install-go:
	cd cli && go mod tidy

build:
	cd cli && go build -o novel-skill.exe .
	@echo "✅ 构建完成：cli/novel-skill.exe"

run-cli: build
	./cli/novel-skill.exe

# ── 一键安装全部依赖 ───────────────────────────────────

install: install-py install-go
	@echo "✅ 全部依赖安装完成"

# ── 清理构建产物 ───────────────────────────────────────

clean:
	rm -f cli/novel-skill cli/novel-skill.exe
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

# ── 帮助 ───────────────────────────────────────────────

help:
	@echo ""
	@echo "首次使用："
	@echo "  make init-data     创建 preferences.json 并确保 data/chapters/ 目录存在（必须先跑）"
	@echo "  make install       安装 Python + Go 全部依赖"
	@echo ""
	@echo "日常使用："
	@echo "  make run-service   启动 Python AI 服务（端口 8000）"
	@echo "  make build         编译 Go CLI（生成 cli/novel-skill.exe）"
	@echo "  make run-cli       编译并启动 CLI 交互式 shell"
	@echo "  make clean         清理构建产物"
	@echo ""
