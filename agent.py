import ollama
from config import MODEL
from rag import search_notice
from tools import days_until

TOOLS = {'search_notice': search_notice, 'days_until': days_until}

SYSTEM = """너는 한국어가 서툰 신입 유학생을 돕는 학사 도우미다.
규칙:
1. 학교 공지·학사 질문은 반드시 search_notice로 검색하고, 검색 결과에 있는 내용만 답한다.
2. 마감일까지 남은 날짜는 반드시 days_until로 계산한다. 직접 계산하지 않는다.
3. 공지에 날짜가 없으면 추측하지 말고 '공지에서 확인할 수 없습니다. 담당 부서에 문의하세요.'라고 답한다.
4. 어떤 공지인지 분명하지 않으면 검색하기 전에 먼저 되묻는다.
5. 비자·체류·아르바이트 허가는 공지 내용만 알려 주고, 가능하다/불가능하다 판단하지 말고 국제교류팀이나 1345를 안내한다.
6. 쉬운 한국어로 짧게 답하고, 어려운 용어는 괄호 안에 영어로 설명한다. 사용자가 영어를 원하면 영어로 답한다.
7. 답 끝에 근거 공지 제목과 담당 부서를 적는다.
8. 개인정보(외국인등록번호, 여권번호 등)는 묻지도 저장하지도 않는다."""


def run_agent(question, history=None, max_rounds=5):
    """질문 하나를 처리하고 (최종 답변, 도구 호출 로그)를 돌려준다."""
    messages = [{'role': 'system', 'content': SYSTEM}] + (history or []) + \
               [{'role': 'user', 'content': question}]
    log = []
    for _ in range(max_rounds):                      # 무한 반복 방지
        resp = ollama.chat(model=MODEL, messages=messages, tools=list(TOOLS.values()))
        msg = resp.message
        messages.append(msg)
        if not msg.tool_calls:                         # 도구가 필요 없으면 최종 답변
            return msg.content, log
        for call in msg.tool_calls:
            name, args = call.function.name, dict(call.function.arguments or {})
            fn = TOOLS.get(name)
            try:
                result = fn(**args) if fn else f'알 수 없는 도구: {name}'
            except Exception as e:                     # 도구 오류로 프로그램이 멈추지 않게
                result = f'도구 오류: {e}'
            log.append(f'🔧 {name}({args}) → {str(result)[:200]}')
            messages.append({'role': 'tool', 'content': str(result), 'tool_name': name})
    return '죄송합니다. 답을 끝내지 못했습니다. 국제교류팀에 문의하세요.', log


if __name__ == '__main__':
    answer, log = run_agent('장학금 신청 마감까지 며칠 남았어?')
    print('\n'.join(log) or '(도구 호출 없음)')
    print('\n답변:', answer)
