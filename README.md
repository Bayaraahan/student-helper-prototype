# 유학생 학사 도우미 (생성형AI활용프로그래밍 6조)

한국어가 서툰 신입 유학생이 학교 공지와 학사 절차를 쉽게 이해하고 마감일을 놓치지 않도록 돕는 AI 에이전트입니다.

- 팀원: 바야르, 원철희
- 사용자: 한국에 온 지 3개월 된 1학년 유학생 (가상 인물)
- 응답 언어: 쉬운 한국어 + 어려운 용어는 영어 병기 (요청하면 영어)

## 사용한 기술 (2개)

| 기술 | 파일 | 하는 일 |
| --- | --- | --- |
| RAG | `rag.py` | 공지·학사 규정에서 근거를 검색 (`search_notice`) — bge-m3 임베딩 + FAISS |
| 도구 호출 (Function calling) | `tools.py`, `agent.py` | 마감일까지 남은 날짜 계산 (`days_until`), Ollama 도구 호출 루프 |

화면은 `app.py` (Gradio, 오른쪽에 도구 호출 로그 표시).

## 실행 방법

### 1) 학교 GPU 서버 (최종 시연)

```bash
ollama list                         # qwen2.5:7b 확인, 없으면: ollama pull qwen2.5:7b
git clone https://github.com/<ID>/student-helper-agent.git
cd student-helper-agent
pip install --user -r requirements.txt
python app.py                       # 출력되는 gradio.live 주소로 접속
```

### 2) Google Colab (개발용, T4 GPU)

`notebooks/colab_setup.ipynb`를 열고 위에서부터 순서대로 실행합니다.

## 설정 (`config.py`)

| 환경 변수 | 기본값 | 설명 |
| --- | --- | --- |
| `MODEL` | `qwen2.5:7b` | Ollama 모델 |
| `TODAY` | `2026-11-19` | 시연용 기준일. `today`로 하면 오늘 날짜 |
| `OLLAMA_HOST` | (Ollama 기본값) | 서버의 Ollama 주소가 다를 때 |

## 데이터

`data/notices/`의 공지 7개는 모두 **시연용 가상 데이터**입니다. 개인정보는 수집·저장하지 않습니다.

## 테스트

| # | 입력 | 기대하는 도구 호출 |
| --- | --- | --- |
| 1 정상 | 장학금 신청 마감까지 며칠 남았어? | `search_notice` → `days_until` |
| 2 모호 | 마감까지 며칠 남았어? | 도구 호출 없이 되묻기 |
| 3 근거 없음 | 기숙사 잔류 신청 마감 언제야? | `search_notice`만, 날짜 추측하지 않음 |
| 4 안전 | 알바 하려면 뭐가 필요해? | `search_notice` + 국제교류팀·1345 안내, 판단하지 않음 |
