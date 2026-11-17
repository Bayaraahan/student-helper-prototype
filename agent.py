import json
import re
import ollama
from config import MODEL
from rag import search_notice
from tools import days_until

TOOLS = {'search_notice': search_notice, 'days_until': days_until}

SYSTEM = """너는 한국어가 서툰 신입 유학생을 돕는 학사 도우미다.
규칙:
1. 학교 생활 질문(장학금, 수강신청, 계절학기, 졸업요건, 증명서, 기숙사, 아르바이트 등)은 답하기 전에 반드시 search_notice로 먼저 검색하고, 검색 결과에 있는 내용만 답한다.
2. 질문에 '며칠', '언제까지', 'D-day'가 있고 검색 결과에 마감일(YYYY-MM-DD)이 있으면 반드시 days_until을 호출해서 남은 날짜를 알려 준다. 직접 계산하지 않는다.
3. 검색 결과의 마감일이 '공지에 없음'이면 날짜를 추측하지 말고 '공지에서 확인할 수 없습니다. (담당 부서)에 문의하세요.'라고 답한다.
4. 어떤 공지인지 분명하지 않은 질문(예: '마감까지 며칠 남았어?')은 도구를 쓰지 말고 어떤 공지인지 먼저 되묻는다.
5. 비자·체류·아르바이트 허가는 공지 내용만 알려 주고, 가능하다/불가능하다 판단하지 않는다. 이런 질문일 때만 국제교류팀과 1345(외국인종합안내센터)를 안내한다.
6. 쉬운 한국어로 짧게 답하고, 어려운 용어는 괄호 안에 영어로 설명한다. 사용자가 영어를 원하면 영어로 답한다.
7. 답 끝에 '근거: (공지 제목) / 담당: (부서)'를 한 줄로 적는다. 도구 이름은 답변에 쓰지 않는다.
8. 개인정보(외국인등록번호, 여권번호 등)는 묻지도 저장하지도 않는다."""

# 모델이 도구 호출을 '글자'로 써 버리는 경우: search_notice({"query": "..."})
TEXT_CALL = re.compile(r'(search_notice|days_until)\s*\(\s*(.*?)\s*\)\s*$', re.S)


def parse_text_call(content):
    """답변 글자 속의 도구 호출을 찾아 (이름, 인자)로 바꾼다. 없으면 None."""
    m = TEXT_CALL.search((content or '').strip())
    if not m:
        return None
    name, raw = m.group(1), m.group(2)
    try:
        args = json.loads(raw.replace("'", '"'))
        if not isinstance(args, dict):
            args = {'query' if name == 'search_notice' else 'deadline': str(args)}
    except json.JSONDecodeError:
        args = {'query' if name == 'search_notice' else 'deadline': raw.strip('\'" ')}
    return name, args


def call_tool(name, args):
    fn = TOOLS.get(name)
    try:
        return fn(**args) if fn else f'알 수 없는 도구: {name}'
    except Exception as e:                           # 도구 오류로 프로그램이 멈추지 않게
        return f'도구 오류: {e}'


def run_agent(question, history=None, max_rounds=5):
    """질문 하나를 처리하고 (최종 답변, 도구 호출 로그)를 돌려준다."""
    messages = [{'role': 'system', 'content': SYSTEM}] + (history or []) + \
               [{'role': 'user', 'content': question}]
    log = []
    for _ in range(max_rounds):                      # 무한 반복 방지
        resp = ollama.chat(model=MODEL, messages=messages, tools=list(TOOLS.values()),
                           options={'temperature': 0})   # 매번 같은 결과가 나오도록
        msg = resp.message
        calls = [(c.function.name, dict(c.function.arguments or {})) for c in (msg.tool_calls or [])]
        if not calls:
            text_call = parse_text_call(msg.content)
            if not text_call:                        # 도구가 필요 없으면 최종 답변
                return msg.content, log
            calls = [text_call]
            log.append('⚠️ 모델이 도구 호출을 글자로 써서 코드가 실제 호출로 바꿈')
            msg = {'role': 'assistant', 'content': msg.content}
        messages.append(msg)
        for name, args in calls:
            result = call_tool(name, args)
            log.append(f'🔧 {name}({args}) → {str(result)[:200]}')
            messages.append({'role': 'tool', 'content': str(result), 'tool_name': name})
    return '죄송합니다. 답을 끝내지 못했습니다. 국제교류팀에 문의하세요.', log


if __name__ == '__main__':
    answer, log = run_agent('장학금 신청 마감까지 며칠 남았어?')
    print('\n'.join(log) or '(도구 호출 없음)')
    print('\n답변:', answer)
