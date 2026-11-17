# 코랩이랑 학교 서버에서 다른 값은 여기서만 바꾸기
import os
from datetime import date

MODEL = os.getenv('MODEL', 'qwen2.5:14b')   # 7b, qwen3:8b 보다 도구 호출이 정확했음
EMBED_MODEL = os.getenv('EMBED_MODEL', 'BAAI/bge-m3')
DATA_DIR = os.getenv('DATA_DIR', 'data/notices')

# 시연할 때 날짜 고정 (TODAY=today 로 하면 진짜 오늘)
_today = os.getenv('TODAY', '2026-11-19')
TODAY = date.today() if _today == 'today' else date.fromisoformat(_today)
