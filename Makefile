.PHONY: install build run-service run-cli clean help

# ── Python AI 服务 ─────────────────────────────────────

install-py:
	cd ai-service && pip install -r requirements.txt

run-service:
	cd ai-service && uvicorn main:app --host localhost --port 8000 --reload

# ── Go CLI ─────────────────────────────────────────────

install-go:
	cd cli && go mod tidy

build:
	cd cli && go build -o novel-skill .
	@echo "✅ 构建完成：cli/novel-skill"

run-cli: build
	./cli/novel-skill

# ── 一键安装全部依赖 ───────────────────────────────────

install: install-py install-go
	@echo "✅ 全部依赖安装完成"

# ── 初始化项目（首次使用）─────────────────────────────

init:
	@bash init_project.sh
	@cp -n config.yaml.example config.yaml || true
	@echo "⚠️  请编辑 config.yaml，填入你的 Gemini API Key"

# ── 清理构建产物 ───────────────────────────────────────

clean:
	rm -f cli/novel-skill cli/novel-skill.exe
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

# ── 帮助 ───────────────────────────────────────────────

help:
	@echo ""
	@echo "  make init          首次初始化项目目录"
	@echo "  make install       安装 Python + Go 全部依赖"
	@echo "  make run-service   启动 Python AI 服务（端口 8000）"
	@echo "  make build         编译 Go CLI"
	@echo "  make run-cli       编译并启动 CLI 交互式 shell"
	@echo "  make clean         清理构建产物"
	@echo ""
