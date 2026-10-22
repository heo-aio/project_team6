# from prompts import GraphState, PromptManager, UserProfileState
from prompts2 import State, PromptManager
# from llama_index.core import VectorStoreIndex
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from llm_config import init_llm_settings
import chromadb
from db_history import get_recent_history  # DB 히스토리 모듈 추가

# 1. LLM 및 임베딩 전역 초기화
llm, embed_model = init_llm_settings()


def retrieve_node(state: State) -> dict:
    """
    [노드 1] RAG 문서 검색 노드
    - GraphState의 question, location을 활용해 정책 문서를 검색합니다.
    """
    print("--- [Node] 정책 문서 검색 시작 ---")
    question = state.get("question", "")
    location = state.get("location", "")
    age = state.get("age", None)

    embed_fn = OllamaEmbeddings(base_url="http://localhost:11434", model="bge-m3:latest")
    client = chromadb.PersistentClient(path="./store")
    vectorstore = Chroma(client=client, collection_name="policies_data", embedding_function=embed_fn)

    # RAG 검색 시 문서 수(k)를 2~3개로 유지하여 LLM 부하 및 타임아웃 방지
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    docs = retriever.invoke(f"{location} 청년 정책 {question}".strip())

    retrieved_context = [doc.page_content for doc in docs]

    # GraphState의 context 필드 갱신
    return {"context": retrieved_context}


def generate_node(state: State) -> dict:
    """
    [노드 2] LLM 답변 생성 노드
    - GraphState의 모든 필드 및 DB 대화 기록을 연동하여 최종 답변을 생성합니다.
    """
    print("--- [Node] LLM 답변 생성 시작 ---")
    user_id = state.get("user_id", "user_01")  # user_id 가져오기 (기본값 user_01)
    question = state.get("question", "")
    context = state.get("context", [])
    age = state.get("age", None)
    location = state.get("location", None)

    user_extra_info = state.get("data", "없음")

    # 1. DB에서 해당 사용자의 최근 대화 기록 조회
    chat_history = get_recent_history(user_id=user_id, limit=6)

    # 2. UserProfileState 및 PromptManager 연동
    pm = PromptManager(state=state)
    pm.update_profile(extra_info=user_extra_info)

    # 3. 프롬프트 템플릿 및 RAG Context 조립
    system_prompt_template = pm.build_system_prompt_str()
    context_str = "\n".join([str(ctx) for ctx in context]) if context else "검색된 관련 문서 없음"

    final_prompt = system_prompt_template.format(
        context_str=context_str,
        query_str=question
    )

    # 4. 이전 대화 기록 및 출력을 위한 세부 지침 병합
    final_prompt += f"""

[이전 대화 기록]
{chat_history}

[현재 질문]
{question}

[출력 규칙]
- 답변은 반드시 자연스러운 한국어로만 작성하세요.
- 중국어, 영어 등 다른 언어를 절대 섞어서 출력하지 마세요.
- 이전 대화 내용이 있다면 그 맥락을 이어서 답변하세요.
- 역슬래시 n(\\n) 문자를 텍스트에 직접 쓰지 말고 실제 엔터(줄바꿈)를 치세요.
- 똑같은 인사말이나 문장을 여러 번 반복하지 마세요.

\n\n[AI 답변]: 
"""

    # 5. LLM 호출 및 줄바꿈 문자 정제
    response = llm.complete(final_prompt)
    clean_text = response.text.replace("\\n", "\n")

    return {"generation": clean_text}


def evaluate_node(state: State) -> dict:
    """
    [노드] 정보 충족 여부 평가 노드
    - 필수 정보(예: location 등)가 누락되었는지 확인하여 need_more_info 플래그를 결정합니다.
    """
    print("--- [Node] 정보 충족 여부 평가 시작 ---")
    print(f"DEBUG STATE -> question: {state.get('question')}, location: {state.get('location')}, age: {state.get('age')}")
    question = state.get("question", "")
    location = state.get("location", "")

    need_more = False

    if not str(location).strip() or not str(question).strip():
        need_more = True

    print(f"Need More Info: {need_more}")

    return {"need_more_info": need_more}


def router(state: State):
    """평가 결과에 따라 다음 노드를 결정하는 라우팅 함수"""
    if state.get("need_more_info", False):
        return "ask_more"  # 정보가 부족하면 추가 정보 요구 노드로
    else:
        return "retrieve"


def ask_more_node(state: State) -> dict:
    """[노드] 사용자에게 추가 정보(지역 또는 질문)를 요구하는 메시지 생성"""
    print("--- [Node] 추가 정보 요구 메시지 생성 ---")
    location = state.get("location", "")
    question = state.get("question", "")

    if not str(location).strip():
        msg = "원활한 정책 검색을 위해 거주하시는 지역(예: 전라북도 전주시, 서울특별시 등)을 입력해 주세요!"
    elif not str(question).strip():
        msg = "어떤 청년 정책이나 지원금을 찾고 계신지 구체적인 질문을 입력해 주세요!"
    else:
        msg = "필요한 정보가 부족합니다. 상세 내용을 입력해 주세요."

    return {"generation": msg}