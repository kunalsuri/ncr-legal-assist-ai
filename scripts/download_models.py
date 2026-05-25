"""Download the open-weights models used by the system into the local HF cache."""
from __future__ import annotations

from huggingface_hub import snapshot_download

MODELS = [
    "law-ai/InLegalBERT",
    "BAAI/bge-reranker-v2-m3",
]

# The generation model is large; pull it separately via vLLM at serve time
# or uncomment one of these to pre-fetch:
# "Qwen/Qwen3-8B-Instruct-AWQ",
# "meta-llama/Llama-3.3-8B-Instruct",


def main() -> None:
    for m in MODELS:
        print(f"Downloading {m}...")
        snapshot_download(repo_id=m)
    print("Done.")


if __name__ == "__main__":
    main()
