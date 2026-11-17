from pathlib import Path
from langchain_core.documents import Document
from config import DATA_DIR, EMBED_MODEL


def load_notices(folder=DATA_DIR):
    """공지 파일 하나 = Document 하나. 맨 위 '키: 값' 줄들은 metadata가 된다."""
    docs = []
    for path in sorted(Path(folder).glob('*.md')):
        head, body = path.read_text(encoding='utf-8').split('\n\n', 1)
        meta = dict(line.split(': ', 1) for line in head.splitlines() if ': ' in line)
        meta['source'] = path.name
        docs.append(Document(page_content=body.strip(), metadata=meta))
    return docs


def build_retriever(k=3):
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(load_notices())   # 조각마다 제목·마감일 metadata 유지
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL,
                                       encode_kwargs={'normalize_embeddings': True})
    db = FAISS.from_documents(chunks, embeddings)
    return db.as_retriever(search_kwargs={'k': k})


_retriever = None


def format_hit(d):
    deadline = d.metadata.get('마감일')
    hint = (f"→ 남은 날짜가 필요하면 days_until('{deadline}')을 호출할 것" if deadline
            else '→ 이 공지에는 마감일이 없음. 날짜를 추측하지 말 것')
    return (f"[{d.metadata.get('제목', d.metadata['source'])}] "
            f"마감일: {deadline or '공지에 없음'} / 담당: {d.metadata.get('담당', '공지에 없음')}\n"
            f"{hint}\n{d.page_content}")


def format_hits(hits):
    if not hits:
        return '검색 결과 없음'
    return '\n\n'.join(format_hit(d) for d in hits)


def search_notice(query: str) -> str:
    """학교 공지와 학사 규정에서 질문과 관련된 내용을 검색한다.
    장학금, 수강신청, 계절학기, 졸업요건, 증명서 발급, 기숙사, 아르바이트(시간제취업), 마감일 질문에 사용한다.
    날짜 계산에는 사용하지 않는다.

    Args:
        query: 검색할 질문 (예: '외국인 유학생 장학금 마감일')
    """
    global _retriever
    if _retriever is None:
        _retriever = build_retriever()
    return format_hits(_retriever.invoke(query))
