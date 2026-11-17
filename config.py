"""Colab과 학교 GPU 서버에서 다른 값은 여기서만 바꾼다."""
import os
from datetime import date

MODEL = os.getenv('MODEL', 'qwen2.5:7b')            # 두 곳에서 같은 모델
EMBED_MODEL = os.getenv('EMBED_MODEL', 'BAAI/bge-m3')
DATA_DIR = os.getenv('DATA_DIR', 'data/notices')

# 시연용 기준일. 실제로 쓸 때는 TODAY=today 로 실행하면 오늘 날짜를 쓴다.
_today = os.getenv('TODAY', '2026-11-19')
TODAY = date.today() if _today == 'today' else date.fromisoformat(_today)
