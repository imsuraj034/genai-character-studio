@echo off
cd /d "%~dp0"
echo Starting GenAI Character Design Studio...
python -m pip install -q -r requirements.txt
python -m streamlit run app.py --browser.gatherUsageStats false
pause
