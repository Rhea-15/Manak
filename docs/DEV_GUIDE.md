# MANAK Development Guide

## Setup (All Devs)

**🚨 CRITICAL NOTE ON FOLDER STRUCTURE:** 
The repository currently contains only the CI/CD skeleton. **If your assigned folder (e.g., `src/backend`, `src/frontend`) or your specific test file does not exist yet, you must create it yourself following the exact naming conventions.**

### Backend/AI Devs (Dev 1, 2, 3, 4)
git clone https://github.com/Rhea-15/Manak.git
cd Manak
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
pytest tests/  # Verify setup (should run cleanly with 0 failures)

Frontend Dev (Dev 5)
# You will need to initialize the React/Next.js app here first
mkdir -p src/frontend
cd src/frontend
npm install
npm run dev  # Dev server at localhost:3000
npm test

Commit & Push
All commits trigger CI automatically:
git add .
git commit -m "Dev X: Feature description"
git push origin feature-branch

CodeRabbit will auto-review. GitHub Actions will:

✅ Lint your code
✅ Run tests
✅ Check security
