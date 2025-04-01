# 404gram
Не найден, как и его безопасность

## Как запускать

```bash
cd eng_words_bot
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Открывать: <http://localhost:8000/>