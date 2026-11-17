from datetime import date
from config import TODAY


def days_until(deadline: str) -> str:
    """마감일까지 남은 날짜를 계산한다. 마감일은 반드시 search_notice로 공지에서 찾은 날짜를 넣는다.
    공지에 마감일이 없으면 이 도구를 쓰지 않는다.

    Args:
        deadline: 마감일, YYYY-MM-DD 형식 (예: '2026-11-27')
    """
    try:
        d = date.fromisoformat(str(deadline).strip())
    except ValueError:
        return f'날짜 형식 오류: {deadline} (YYYY-MM-DD 형식이 필요합니다)'
    n = (d - TODAY).days
    if n > 0:
        return f'마감까지 {n}일 남았습니다 (D-{n}).'
    if n == 0:
        return '오늘이 마감일입니다 (D-day).'
    return f'마감일이 {-n}일 지났습니다.'
