import gradio as gr
from agent import run_agent


def to_text(content):
    """Gradio 버전에 따라 메시지 내용이 문자열 또는 리스트로 온다 → 글자만 꺼낸다."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return ' '.join(c.get('text', '') for c in content if isinstance(c, dict))
    return ''


def respond(message, chat_history):
    history = [{'role': m['role'], 'content': to_text(m['content'])}
               for m in chat_history][-6:]                # 최근 3번 대화만 기억
    answer, log = run_agent(message, history)
    chat_history = chat_history + [{'role': 'user', 'content': message},
                                   {'role': 'assistant', 'content': answer}]
    return '', chat_history, '\n'.join(log) or '(도구 호출 없음)'


def make_chatbot():
    try:
        return gr.Chatbot(type='messages', height=480)   # Gradio 4~5
    except TypeError:
        return gr.Chatbot(height=480)                    # Gradio 6 (messages 형식이 기본)


with gr.Blocks(title='유학생 학사 도우미') as demo:
    gr.Markdown('## 유학생 학사 도우미 — 학교 공지와 마감일을 쉽게')
    with gr.Row():
        with gr.Column(scale=2):
            chatbot = make_chatbot()
            msg = gr.Textbox(placeholder='예: 장학금 신청 마감까지 며칠 남았어?')
            clear = gr.Button('새 대화')
        with gr.Column(scale=1):
            log_box = gr.Textbox(label='도구 호출 로그', lines=20)
    msg.submit(respond, [msg, chatbot], [msg, chatbot, log_box])
    clear.click(lambda: ([], ''), None, [chatbot, log_box])

if __name__ == '__main__':
    demo.launch(share=True)
