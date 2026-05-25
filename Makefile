.PHONY: install download-models build-index serve-llm run-app lint test

install:
	pip install -e ".[dev]"

download-models:
	python scripts/download_models.py

build-index:
	docker compose up -d qdrant
	python scripts/build_index.py

serve-llm:
	@echo "Start vLLM server manually, e.g.:"
	@echo "  vllm serve Qwen/Qwen3-8B-Instruct-AWQ --port 8000 --quantization awq"

run-app:
	streamlit run src/app/streamlit_app.py

lint:
	ruff check src tests scripts

test:
	pytest -v
