#!/bin/bash
# NEXUS AI Agent - Quick Start Guide
# Copy-paste these commands to get started immediately

# ============================================================================
# STEP 1: ENVIRONMENT SETUP
# ============================================================================

echo "Step 1: Setting up environment..."

# Create project directory
mkdir -p ~/nexus-ai-agent
cd ~/nexus-ai-agent

# Create virtual environment
python -m venv venv

# Activate virtual environment (choose based on OS)
# For macOS/Linux:
source venv/bin/activate
# For Windows:
# venv\Scripts\activate

# Copy files from Claude's work directory
cp /home/claude/*.py .
cp /home/claude/requirements.txt .
cp /home/claude/Dockerfile .
cp /home/claude/docker-compose.yml .
cp /home/claude/README.md .
cp /home/claude/GITHUB_SETUP.md .

echo "✅ Environment setup complete!"

# ============================================================================
# STEP 2: INSTALL DEPENDENCIES
# ============================================================================

echo ""
echo "Step 2: Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed!"

# ============================================================================
# STEP 3: SET ANTHROPIC API KEY
# ============================================================================

echo ""
echo "Step 3: Setting up API key..."
read -p "Enter your ANTHROPIC_API_KEY: " api_key
export ANTHROPIC_API_KEY="$api_key"
echo "✅ API key configured!"

# ============================================================================
# STEP 4: RUN BACKEND
# ============================================================================

echo ""
echo "Step 4: Starting backend server..."
echo "Run in Terminal 1:"
echo "python -m uvicorn nexus-backend-main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Backend will be available at: http://localhost:8000"
echo "API Docs at: http://localhost:8000/docs"

# ============================================================================
# STEP 5: RUN FRONTEND
# ============================================================================

echo ""
echo "Step 5: Starting frontend dashboard..."
echo "Run in Terminal 2:"
echo "streamlit run nexus-frontend-streamlit.py"
echo ""
echo "Dashboard will be available at: http://localhost:8501"

# ============================================================================
# STEP 6: RUN DEMO
# ============================================================================

echo ""
echo "Step 6: Running demo script..."
echo "Run in Terminal 3 (after backend is ready):"
echo "python demo_script.py"

# ============================================================================
# STEP 7: DOCKER SETUP (OPTIONAL)
# ============================================================================

echo ""
echo "Step 7 (Optional): Docker deployment..."
echo "Run:"
echo "docker-compose up -d"
echo ""
echo "This starts both backend and frontend in containers"

# ============================================================================
# STEP 8: GITHUB SETUP
# ============================================================================

echo ""
echo "Step 8: Prepare for GitHub upload..."
echo ""
echo "Initialize git:"
git init
git config user.name "Your Name"
git config user.email "your.email@gmail.com"

echo ""
echo "Create .gitignore:"
cat > .gitignore << 'EOF'
__pycache__/
*.py[cod]
*.so
.Python
env/
venv/
.env
.DS_Store
nexus_agent.db
*.log
.pytest_cache/
EOF

echo ""
echo "Create .env.example:"
cat > .env.example << 'EOF'
ANTHROPIC_API_KEY=sk-ant-your-key-here
LOG_LEVEL=INFO
EOF

echo ""
echo "✅ Git setup complete!"

# ============================================================================
# QUICK COMMANDS REFERENCE
# ============================================================================

echo ""
echo "=========================================="
echo "🚀 NEXUS AI Agent - Quick Reference"
echo "=========================================="
echo ""
echo "📦 Installation:"
echo "  pip install -r requirements.txt"
echo ""
echo "🔐 API Key:"
echo "  export ANTHROPIC_API_KEY='your-key'"
echo ""
echo "🎯 Backend (Terminal 1):"
echo "  python -m uvicorn nexus-backend-main:app --reload"
echo ""
echo "🎨 Frontend (Terminal 2):"
echo "  streamlit run nexus-frontend-streamlit.py"
echo ""
echo "🎬 Demo (Terminal 3):"
echo "  python demo_script.py"
echo ""
echo "🐳 Docker (Single command):"
echo "  docker-compose up -d"
echo ""
echo "📊 Access Points:"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "  Frontend: http://localhost:8501"
echo ""
echo "📤 GitHub Upload:"
echo "  1. Create repo on github.com"
echo "  2. git add ."
echo "  3. git commit -m 'Initial commit: NEXUS AI Agent'"
echo "  4. git remote add origin <your-repo-url>"
echo "  5. git push -u origin main"
echo ""
echo "=========================================="
echo "✅ All set! Follow the commands above"
echo "=========================================="
