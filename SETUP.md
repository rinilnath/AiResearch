# 🔧 Setup Guide - Manufacturing Defect AI Agent

Complete setup instructions for fresh installation.

## System Requirements

- **OS**: Windows 10/11, macOS 10.15+, or Linux
- **Python**: 3.12 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 500MB free space
- **Internet**: Required for AI API calls

## Step-by-Step Installation

### Step 1: Install Python

**Windows:**
1. Download from [python.org](https://www.python.org/downloads/)
2. Run installer
3. ✅ Check "Add Python to PATH"
4. Click "Install Now"

**Mac:**
```bash
brew install python@3.12
```

**Linux (Ubuntu):**
```bash
sudo apt update
sudo apt install python3.12 python3.12-venv
```

Verify installation:
```bash
python --version  # Should show 3.12+
```

### Step 2: Get Anthropic API Key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up / Log in
3. Navigate to "API Keys"
4. Click "Create Key"
5. Copy the key (starts with `sk-ant-`)
6. **Keep it secret!**

### Step 3: Clone or Download Project

**Option A: Git Clone**
```bash
git clone https://github.com/yourusername/manufacturing-ai-agent.git
cd manufacturing-ai-agent
```

**Option B: Download ZIP**
1. Download ZIP from GitHub
2. Extract to folder
3. Open terminal in that folder

### Step 4: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- streamlit 1.50.0
- anthropic 0.71.0
- pandas 2.3.3
- plotly 5.18.0
- fastapi 0.115.0
- uvicorn 0.32.0
- pydantic 2.10.0

Wait 2-3 minutes for installation.

### Step 6: Configure API Key

Create `.env` file:

**Windows:**
```bash
copy .env.example .env
notepad .env
```

**Mac/Linux:**
```bash
cp .env.example .env
nano .env
```

Edit file:
```
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

Save and close.

### Step 7: Initialize Database

```bash
python database.py
```

Expected output:
```
Created defect: MECH-20241024-001
Summary Stats:
Total Defects: 1
By Priority: {'HIGH': 1}
```

This creates:
- `data/defects.db` - SQLite database
- 4 tables: defects, teams, defect_history, notifications
- 5 default teams

### Step 8: Verify Installation

Test AI agent:
```bash
python ai_agent.py
```

Should process test defect and show JSON output.

### Step 9: Run Application

**Terminal 1 - Streamlit UI:**
```bash
streamlit run app.py
```

Opens browser at `http://localhost:8501`

**Terminal 2 - REST API (Optional):**
```bash
uvicorn api:app --reload --port 8000
```

Swagger docs at `http://localhost:8000/docs`

## Verification Checklist

- [ ] Python 3.12+ installed
- [ ] Virtual environment activated
- [ ] All dependencies installed (no errors)
- [ ] `.env` file created with API key
- [ ] Database initialized (defects.db exists)
- [ ] `python ai_agent.py` works
- [ ] Streamlit app opens in browser
- [ ] Can submit test defect
- [ ] AI returns categorization

## Common Issues & Solutions

### Issue: "command not found: python"

**Solution:**
```bash
# Try python3 instead
python3 --version
python3 -m venv venv
```

### Issue: "No module named 'streamlit'"

**Solution:**
```bash
# Make sure venv is activated
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Reinstall
pip install -r requirements.txt
```

### Issue: "ANTHROPIC_API_KEY not found"

**Solution:**
1. Check `.env` file exists in project root
2. Verify key format: `ANTHROPIC_API_KEY=sk-ant-...`
3. No quotes around key
4. Restart application after editing

### Issue: "database is locked"

**Solution:**
```bash
# Close all Python processes
# Delete database
rm data/defects.db  # Mac/Linux
del data\defects.db  # Windows

# Recreate
python database.py
```

### Issue: "Address already in use"

**Solution:**
```bash
# Kill process on port 8501
# Windows:
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:8501 | xargs kill -9
```

### Issue: SSL Certificate Error

**Solution:**
Add to `ai_agent.py` after imports:
```python
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
```

## First-Time Usage

1. Open `http://localhost:8501`
2. Click "📝 Report Defect"
3. Try test input:
   ```
   Emergency stop button on Station 7 not responding. 
   Worker tested multiple times. Immediate safety hazard.
   ```
4. Click "🚀 Submit Defect Report"
5. Wait 5-10 seconds for AI processing
6. View result:
   - Category: Safety
   - Priority: CRITICAL
   - Team: Safety
   - Recommended actions

## Next Steps

- Add your own historical defects to `data/historical_defects.csv`
- Customize team info in `data/teams.csv`
- Try the REST API: `http://localhost:8000/docs`
- Read API documentation
- Explore dashboard and reports

## Production Deployment

For production use, see `DEPLOYMENT.md` (coming soon).

Key upgrades needed:
- PostgreSQL instead of SQLite
- HTTPS/SSL
- Authentication
- Rate limiting
- Monitoring
- Backups

## Getting Help

- Check README.md
- Review troubleshooting section above
- Create GitHub issue
- Email: support@manufacturing-ai.com

## Useful Commands

```bash
# Activate venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Run Streamlit
streamlit run app.py

# Run API
uvicorn api:app --reload --port 8000

# Test components
python ai_agent.py
python database.py

# Deactivate venv
deactivate
```

---

**🎉 Setup complete! You're ready to use the Manufacturing Defect AI Agent.**
