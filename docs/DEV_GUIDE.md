# MANAK Development Guide

## Setup (All Devs)

### Backend/AI Devs (Dev 1,2,3,4)
```bash
git clone https://github.com/binary-minds/manak.git
cd manak
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
pytest tests/  # Verify setup
```

### Frontend Dev (Dev 5)
```bash
cd frontend
npm install
npm start  # Dev server at localhost:3000
npm test
```

## Commit & Push

All commits trigger CI automatically:
```bash
git add .
git commit -m "Dev X: Feature description"
git push origin feature-branch
```

CodeRabbit will auto-review. GitHub Actions will:
- ✅ Lint your code
- ✅ Run tests
- ✅ Check security
- ✅ Report coverage

## Dev Responsibilities

| Dev | Tests to Pass | Key Components |
|-----|---------------|-----------------|
| Dev 1 | `tests/backend/test_api.py` | FastAPI, PostgreSQL, Rules Engine |
| Dev 2 | `tests/backend/test_database.py` | PostgreSQL, Neo4j, Migrations |
| Dev 3 | `tests/ai_search/test_parsers.py` | PDF parsing, Qdrant, spaCy |
| Dev 4 | `tests/backend/test_search.py` | FastAPI routes, integration |
| Dev 5 | `frontend/npm test` | React components, TypeScript |

## CI/CD Flow

1. Open PR → CodeRabbit auto-reviews
2. Push commits → GitHub Actions runs all tests
3. All tests pass → Ready to merge
4. Merge to main → Auto-deploy (optional)

## Troubleshooting

**Tests failing locally?**
```bash
pytest -v tests/  # See detailed errors
```

**Want to skip slow tests?**
```bash
pytest -m "not slow" tests/
```

**Clear cache:**
```bash
rm -rf .pytest_cache/ __pycache__/
```