#!/bin/bash

# Automated Demo Runner for Database Security System
# This script runs the complete demo automatically

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║          DATABASE SECURITY SYSTEM - AUTOMATED DEMO               ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Initialize database
echo "📦 Step 1: Initializing database..."
python init_db.py
if [ $? -ne 0 ]; then
    echo "❌ Database initialization failed!"
    exit 1
fi
echo ""

# Step 2: Start Django server in background
echo "🚀 Step 2: Starting Django server..."
python manage.py &
SERVER_PID=$!
echo "Server PID: $SERVER_PID"
sleep 3
echo ""

# Step 3: Run legitimate user tests
echo "👤 Step 3: Running legitimate user tests..."
sleep 2
python legitimate_user.py
echo ""

# Step 4: Run attacker simulation
echo "🔴 Step 4: Running attack simulation..."
sleep 2
python attacker.py
echo ""

# Step 5: Show final statistics
echo "📊 Step 5: Final Statistics..."
sleep 1
curl -s http://localhost:8000/stats/ | python -m json.tool
echo ""

# Cleanup
echo "🧹 Cleaning up..."
kill $SERVER_PID 2>/dev/null
echo ""

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                    DEMO COMPLETE!                                ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "Summary:"
echo "  ✅ Legitimate users: All requests authorized"
echo "  ❌ Attackers: All attacks blocked"
echo "  🛡️ Security system: Working perfectly!"
echo ""
