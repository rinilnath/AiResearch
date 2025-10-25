# 🏭 EvoFix

AI-powered defect management system using Natural Language Processing for manufacturing plants. Workers report defects in plain English, and AI automatically categorizes, prioritizes, routes to teams, and suggests solutions.

## 🎯 Features

- **Natural Language Input**: Workers describe defects naturally - no forms, no training required
- **AI Categorization**: Auto-classifies into 5 categories (Mechanical, Electrical, Quality Control, Safety, Process)
- **Smart Prioritization**: Assigns CRITICAL/HIGH/MEDIUM/LOW based on semantic understanding
- **Intelligent Routing**: Auto-assigns to appropriate teams
- **Solution Recommendations**: RAG-based suggestions from historical data
- **Real-time Dashboard**: Analytics and visualizations
- **REST API**: Swagger-documented endpoints for integration
- **99% Time Savings**: 30 minutes → 30 seconds per report

## 🛠️ Tech Stack

- **AI**: Claude Sonnet 4.5 (Anthropic)
- **Backend**: Python 3.12, FastAPI
- **Frontend**: Streamlit
- **Database**: SQLite
- **Visualization**: Plotly
- **API Docs**: Swagger/OpenAPI

## 📋 Prerequisites

- Python 3.12 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com))

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/manufacturing-ai-agent.git
cd manufacturing-ai-agent
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up API Key

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```
ANTHROPIC_API_KEY=your APIKEY```

### 5. Initialize Database

```bash
python database.py
```

### 6. Run the Application

**Streamlit UI:**
```bash
streamlit run app.py
```
Open browser to `http://localhost:8501`

**REST API (Optional):**
```bash
uvicorn api:app --reload --port 8000
```
Swagger docs at `http://localhost:8000/docs`

## 📖 Usage

### Reporting a Defect

1. Open the app in browser
2. Navigate to "📝 Report Defect"
3. Type defect description in plain English:
   ```
   Emergency stop button on Station 7 not responding. 
   Safety hazard - machine cannot be stopped manually.
   ```
4. Click "Submit"
5. AI analyzes and creates ticket instantly

### Dashboard & Analytics

- View real-time defect statistics
- Analyze trends by priority, category, team
- Track resolution rates
- Export reports to CSV

### API Integration

**Report Defect:**
```bash
curl -X POST "http://localhost:8000/api/v1/defects/report" \
  -H "Content-Type: application/json" \
  -d '{"description": "Hydraulic leak on Line 3"}'
```

**Get All Defects:**
```bash
curl "http://localhost:8000/api/v1/defects"
```

Full API docs: `http://localhost:8000/docs`

## 🎓 AI/ML Techniques Used

1. **Natural Language Processing (NLP)** - Text understanding with LLM
2. **Few-Shot Learning** - Historical examples in context window
3. **RAG (Retrieval-Augmented Generation)** - Past solutions for recommendations
4. **Multi-Label Classification** - Category + Priority + Team simultaneously
5. **Named Entity Recognition** - Extract equipment, location, severity
6. **Zero-Shot Learning** - Works immediately without training
7. **Semantic Analysis** - Context-aware priority scoring

## 📁 Project Structure

```
manufacturing-ai-agent/
├── app.py                    # Streamlit UI (main application)
├── ai_agent.py              # AI processing engine
├── database.py              # Database operations
├── api.py                   # REST API with Swagger
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── README.md               # This file
└── data/
    ├── historical_defects.csv  # Training data for RAG
    ├── teams.csv              # Team contact information
    └── defects.db            # SQLite database (auto-created)
```

## 🔧 Configuration

### Environment Variables

```bash
ANTHROPIC_API_KEY=your-key-here  # Required
```

### Database

Default: SQLite at `data/defects.db`

For production, migrate to PostgreSQL (see deployment guide).

## 📊 Sample Data

Historical defects included for demo:
- 15 past defects with resolutions
- 5 teams with contact info

Add your own data to `data/historical_defects.csv` for better AI recommendations.

## 🧪 Testing

Test AI agent:
```bash
python ai_agent.py
```

Test database:
```bash
python database.py
```

## 🐛 Troubleshooting

### API Key Error
```
Error: No API key found
```
**Solution:** Create `.env` file with valid `ANTHROPIC_API_KEY`

### Database Lock Error
```
database is locked
```
**Solution:** Close Streamlit, delete `data/defects.db`, run `python database.py`

### Import Errors
```
ModuleNotFoundError: No module named 'xyz'
```
**Solution:** `pip install -r requirements.txt`

## 🚀 Deployment

### Production Checklist

- [ ] Migrate to PostgreSQL
- [ ] Add authentication (JWT)
- [ ] Set up HTTPS
- [ ] Configure CORS
- [ ] Add rate limiting
- [ ] Set up monitoring (Sentry)
- [ ] Enable database backups
- [ ] Add vector database for semantic search

### Docker Deployment (Coming Soon)

```bash
docker-compose up
```

## 📈 Roadmap

### Phase 1 (Current)
- ✅ Natural language defect reporting
- ✅ AI categorization and routing
- ✅ Dashboard and analytics
- ✅ REST API with Swagger

### Phase 2 (Next)
- [ ] Voice input integration
- [ ] Image OCR for defect photos
- [ ] Multi-language support
- [ ] Mobile app

### Phase 3 (Future)
- [ ] Vector database for semantic search
- [ ] Predictive maintenance models
- [ ] IoT sensor integration
- [ ] Multi-plant deployment

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👥 Team

Built with ❤️ for manufacturing excellence.

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Email: support@manufacturing-ai.com

## 🙏 Acknowledgments

- Anthropic for Claude API
- Streamlit for amazing Python web framework
- Manufacturing professionals who provided domain insights

---

**⭐ Star this repo if you find it useful!**
