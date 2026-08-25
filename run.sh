#!/usr/bin/env bash

set -euo pipefail

MODE=""
TASK="app"

usage() {
  echo "Usage: ./run.sh --local|--docker [--eval|--performance-test]"
  exit 1
}

if [[ $# -lt 1 || $# -gt 2 ]]; then
  usage
fi

case "$1" in
  --local)
    MODE="local"
    ;;
  --docker)
    MODE="docker"
    ;;
  *)
    usage
    ;;
esac

if [[ $# -eq 2 ]]; then
  case "$2" in
    --eval)
      TASK="eval"
      ;;
    --performance-test)
      TASK="performance"
      ;;
    *)
      usage
      ;;
  esac
fi

echo "[1/8] Preparing .env from .env.example..."
cp .env.example .env

echo "[2/8] Configuring OLLAMA_BASE_URL for mode: ${MODE}..."
if [[ "$MODE" == "local" ]]; then
    awk '
        /^OLLAMA_BASE_URL=/ { print "OLLAMA_BASE_URL=\"http://localhost:11434\""; next }
        /^#OLLAMA_BASE_URL=http:\/\/host\.docker\.internal:11434/ { print "#OLLAMA_BASE_URL=http://host.docker.internal:11434"; next }
        { print }
    ' .env > .env.tmp && mv .env.tmp .env
else
    awk '
        /^OLLAMA_BASE_URL=/ { print "#OLLAMA_BASE_URL=\"http://localhost:11434\""; next }
        /^#?OLLAMA_BASE_URL=http:\/\/host\.docker\.internal:11434/ { print "OLLAMA_BASE_URL=http://host.docker.internal:11434"; next }
        { print }
    ' .env > .env.tmp && mv .env.tmp .env
fi

echo "[3/8] Ensuring local .venv exists..."
if [[ ! -d ".venv" ]]; then
    uv venv .venv
    echo "Created .venv"
else
    echo ".venv already exists"
fi

echo "[4/8] Activating local .venv..."
source .venv/bin/activate

DATABASE_PATH="$(awk -F= '/^DATABASE_PATH=/{print $2; exit}' .env | tr -d '"')"
DATABASE_PATH="${DATABASE_PATH:-database}"

echo "[5/8] Downloading database release into ${DATABASE_PATH}..."
curl -L \
  "https://github.com/skillsharer/rag-chatbot-practice/releases/download/database-v1/database.zip" \
  -o database.zip

tmp_extract_dir="$(mktemp -d)"
unzip -o database.zip -d "$tmp_extract_dir"
rm -f database.zip

mkdir -p "$(dirname "$DATABASE_PATH")"
rm -rf "$DATABASE_PATH"
if [[ -d "$tmp_extract_dir/database" ]]; then
  mv "$tmp_extract_dir/database" "$DATABASE_PATH"
else
  extracted_root="$(find "$tmp_extract_dir" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
  if [[ -n "${extracted_root}" ]]; then
    mv "$extracted_root" "$DATABASE_PATH"
  else
    mkdir -p "$DATABASE_PATH"
    cp -R "$tmp_extract_dir"/. "$DATABASE_PATH"/
  fi
fi
rm -rf "$tmp_extract_dir"

if [[ "$MODE" == "local" ]]; then
  echo "[6/8] Syncing dependencies with uv..."
    uv sync

  echo "[7/8] Running data upload..."
    uv run python -m src.upload

  if [[ "$TASK" == "eval" ]]; then
    echo "[8/8] Running local evaluation (src/eval/eval.py)..."
    uv run python -m src.eval.eval
  elif [[ "$TASK" == "performance" ]]; then
    echo "[8/8] Running local performance test (src/eval/performance_test.py)..."
    uv run python -m src.eval.performance_test
  else
    echo "[8/8] Starting Streamlit agent..."
    uv run python -m streamlit run src/main.py
  fi
else
  echo "[6/8] Building Docker image rag-chatbot..."
  docker build --no-cache -t rag-chatbot .

  mkdir -p tmp

  echo "[7/8] Running data upload inside Docker..."
  docker run --rm \
      --env-file .env \
      -v "$(pwd)/${DATABASE_PATH}:/app/${DATABASE_PATH}:ro" \
      -v "$(pwd)/tmp:/app/tmp" \
      -v "$HOME/.cache/huggingface:/root/.cache/huggingface" \
      rag-chatbot \
      uv run python -m src.upload

  if [[ "$TASK" == "eval" ]]; then
    echo "[8/8] Running Docker evaluation (src/eval/eval.py)..."
    docker run --rm \
        --env-file .env \
        -v "$(pwd)/${DATABASE_PATH}:/app/${DATABASE_PATH}:ro" \
        -v "$(pwd)/tmp:/app/tmp" \
        -v "$HOME/.cache/huggingface:/root/.cache/huggingface" \
        rag-chatbot \
        uv run python -m src.eval.eval

  elif [[ "$TASK" == "performance" ]]; then
    echo "[8/8] Running Docker performance test (src/eval/performance_test.py)..."
    docker run --rm \
        --env-file .env \
        -v "$(pwd)/${DATABASE_PATH}:/app/${DATABASE_PATH}:ro" \
        -v "$(pwd)/tmp:/app/tmp" \
        -v "$HOME/.cache/huggingface:/root/.cache/huggingface" \
        rag-chatbot \
        uv run python -m src.eval.performance_test

  else
    echo "[8/8] Starting Docker container (Streamlit)..."
    docker run --rm -ti \
        --env-file .env \
        -v "$(pwd)/${DATABASE_PATH}:/app/${DATABASE_PATH}:ro" \
        -v "$(pwd)/tmp:/app/tmp" \
        -v "$HOME/.cache/huggingface:/root/.cache/huggingface" \
        -p 8501:8501 \
        rag-chatbot \
        uv run python -m streamlit run src/main.py
  fi
fi