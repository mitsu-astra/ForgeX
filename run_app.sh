#!/usr/bin/env bash
# ==============================================================================
# Industrial AI Decision Intelligence Platform - Unified Startup Script
# NEURAX Hackathon 3.0: Domain 2 - Visual Inspection & Root-Cause Assistant
# ==============================================================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -d "$PROJECT_DIR/.venv" ]; then
    VENV_PATH="$PROJECT_DIR/.venv"
else
    VENV_PATH="$PROJECT_DIR/venv"
fi
BACKEND_PORT=8000
FRONTEND_PORT=3000

export KMP_DUPLICATE_LIB_OK=TRUE
export OMP_NUM_THREADS=4

echo "=============================================================================="
echo "  🚀 Starting Industrial AI Decision Intelligence Platform"
echo "=============================================================================="

# 1. Clean up existing stale listeners on ports if any
if command -v lsof &> /dev/null; then
    echo "✓ Checking ports $BACKEND_PORT and $FRONTEND_PORT..."
    lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
    lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
    sleep 1
elif command -v fuser &> /dev/null; then
    echo "✓ Checking ports $BACKEND_PORT and $FRONTEND_PORT..."
    fuser -k $BACKEND_PORT/tcp 2>/dev/null || true
    fuser -k $FRONTEND_PORT/tcp 2>/dev/null || true
    sleep 1
fi

# 2. Activate Python Virtual Environment
if [ -d "$VENV_PATH" ]; then
    echo "✓ Activating virtual environment: $VENV_PATH"
    source "$VENV_PATH/bin/activate"
else
    echo "❌ Error: Virtual environment not found at $VENV_PATH"
    echo "Please create it using: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# 3. Check Acceleration
python3 -c "import torch; print(f'✓ PyTorch {torch.__version__} | Device: {\"CUDA (GPU)\" if torch.cuda.is_available() else \"CPU Optimized\"}')"

# 4. Start Backend FastAPI Server in background
echo "✓ Launching FastAPI backend server on port $BACKEND_PORT..."
export PYTHONPATH="$PROJECT_DIR"
python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload --reload-dir backend/app &

BACKEND_PID=$!

# 5. Handle clean termination on Ctrl+C
cleanup() {
    echo ""
    echo "🛑 Shutting down backend and frontend services..."
    kill $BACKEND_PID 2>/dev/null || true
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# 6. Wait for backend to become ready
echo "Waiting for FastAPI backend to initialize preloaded AI models..."
for i in {1..30}; do
    if curl -s "http://localhost:$BACKEND_PORT/health" | grep -q "healthy"; then
        echo "✓ FastAPI backend is ready and healthy! (http://localhost:$BACKEND_PORT)"
        break
    fi
    sleep 1
done

# 7. Start Frontend Next.js Server
echo "✓ Launching Next.js frontend on port $FRONTEND_PORT (http://localhost:$FRONTEND_PORT)..."
cd "$PROJECT_DIR/frontend"
npm run dev -- -p $FRONTEND_PORT &
FRONTEND_PID=$!

wait $FRONTEND_PID
