from fastapi import FastAPI
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from langgraph.constants import END
from pydantic import BaseModel
from scheduler import check_and_run_on_startup, sch_start
from contextlib import asynccontextmanager

#from common import get_state
#from prompts import get_graph
from prompts2 import get_state
#from 'prompts(수정본)' import get_state
from db_history import init_db, save_message
from node_func import *

class ChatRequest(BaseModel):
    user_id: str = "user_01"
    query: str    # 사용자 질문
    age: int      # 사용자 나이
    area:str      # 사용자 지역
    data:str      # 사용자 개인정보
  
@asynccontextmanager
async def lifespan(app: FastAPI):
    global scheduler
    
    # 서버 켜질 때 부팅 체크 실행
    await check_and_run_on_startup()
    
    # 스케줄러 구동
    scheduler = sch_start()
    print("스케줄러가 시작되었습니다.")
    
    yield  # 서버 실행 중...
    
    # 서버 꺼질 때 종료
    if scheduler:
        scheduler.shutdown()
        print("스케줄러가 안전하게 종료되었습니다.")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처에서의 요청을 허용 (테스트용)
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST 등 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

app.mount("/view", StaticFiles(directory="view"))

# LangGraph State
wf = get_state()

# node 등록
wf.add_node('evaluate', evaluate_node)
wf.add_node('retrieve', retrieve_node)
wf.add_node('generate', generate_node)
wf.add_node('ask_more', ask_more_node)

#시작점 등록
wf.set_entry_point('evaluate')

# 조건부(라우터) edge 등록
wf.add_conditional_edges(
    'evaluate',
    router,
    {
        'retrieve':'retrieve',
        'ask_more':'ask_more',
    }
)

# edge(경로)등록
wf.add_edge("retrieve","generate")
wf.add_edge("generate", END)
wf.add_edge("ask_more", END)

i = wf.compile()



@app.get("/")
def root():
    return RedirectResponse("/view/index.html")
    #return RedirectResponse(url="/docs")

@app.post("/chat")
async def chat(query: ChatRequest):

    save_message(user_id=query.user_id, role="user", message=query.query)

    # LangGraph 실행 후 결과 반환
    #query = input('월세지원을 받고있다는 등의 개인사정을 상세하게 입력해주세요')
    result = i.invoke({
        "user_id": query.user_id,
        "question": query.query,  # 사용자 질문
        "age": query.age,  # 사용자 나이
        "location": query.area, # 사용자 지역
        "data": query.data  # 개인정보
    })

    answer = result.get("generation", "")

    # 3. AI 답변을 DB에 저장
    save_message(user_id=query.user_id, role="assistant", message=answer)
  
    # 챗봇 모드에서 추가 정보가 필요하다고 판단된 경우
    if result.get("need_more_info", False):
        return {
            "type": "ask_more",          
            "answer": result["generation"] 
        }
    
    # 일반적인 RAG 답변 생성 완료 경우
    return {
        "type": "chat_answer",
        "answer": result["generation"]
    }