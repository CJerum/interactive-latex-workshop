#!/bin/bash

# Run both backend and frontend servers concurrently

echo "🚀 Starting Interactive LaTeX Workshop..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run ./setup.sh first."
    exit 1
fi

# Function to kill background processes on exit
cleanup() {
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped."
    exit 0
}

trap cleanup SIGINT SIGTERM

# Activate virtual environment
source venv/bin/activate

echo "📡 Starting backend server on port 5000..."
cd backend
python app.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

echo "🎨 Starting frontend server on port 3000..."
python server.py &
FRONTEND_PID=$!

echo ""
echo "🎉 Workshop is running!"
echo "📱 Frontend: http://127.0.0.1:3000"
echo "🔧 Backend:  http://127.0.0.1:5000"
echo ""
echo "Press Ctrl+C to stop both servers."

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
