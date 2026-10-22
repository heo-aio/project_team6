from fastapi import FastAPI
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from langgraph.constants import END
from pydantic import BaseModel

# from common import get_state
# from prompts import get_graph
from prompts2 import get_state
# from 'prompts(수정본)' import get_state
from node_func import *
from db_history import init_db, save_message  # DB 연동 함수 임포트


class ChatRequest(BaseModel):
    user_id: str = "user_01"  # 대화 맥락 유지를 위한 사용자 ID (기본값 설정)
    query: str  # 사용자 질문
    age: int  # 사용자 나이
    area: str  # 사용자 지역
    data: str  # 사용자 개인정보


app = FastAPI()

# 서버가 켜질 때 DB 및 테이블 자동 생성/확인
@app.on_event("startup")
def startup_event():
    init_db()


app.mount("/view", StaticFiles(directory="view"))

# LangGraph State
wf = get_state()

# node 등록
wf.add_node('evaluate', evaluate_node)
wf.add_node('retrieve', retrieve_node)
wf.add_node('generate', generate_node)
wf.add_node('ask_more', ask_more_node)

# 시작점 등록
wf.set_entry_point('evaluate')

# 조건부(라우터) edge 등록
wf.add_conditional_edges(
    'evaluate',
    router,
    {
        'retrieve': 'retrieve',
        'ask_more': 'ask_more',
    }
)

# edge(경로)등록
wf.add_edge("retrieve", "generate")
wf.add_edge("generate", END)
wf.add_edge("ask_more", END)

i = wf.compile()


@app.get("/")
def root():
    # return RedirectResponse("/view/index.html")
    return RedirectResponse(url="/docs")


@app.post("/chat")
async def chat(query: ChatRequest):
    # 1. 사용자 질문을 DB에 저장
    save_message(user_id=query.user_id, role="user", message=query.query)

    # 2. LangGraph 실행 (user_id 추가 전달)
    result = i.invoke({
        "user_id": query.user_id,
        "question": query.query,  # 사용자 질문
        "age": query.age,  # 사용자 나이
        "location": query.area,  # 사용자 지역
        "data": query.data  # 개인정보
    })

    answer = result.get("generation", "")

    # 3. AI 답변을 DB에 저장
    save_message(user_id=query.user_id, role="assistant", message=answer)

    # 챗봇 모드에서 추가 정보가 필요하다고 판단된 경우
    if result.get("need_more_info", False):
        return {
            "type": "ask_more",
            "answer": answer
        }

    # 일반적인 RAG 답변 생성 완료 경우
    return {
        "type": "chat_answer",
        "answer": answer
    }