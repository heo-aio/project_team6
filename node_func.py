#from prompts import GraphState, PromptManager, UserProfileState
#from llama_index.core import VectorStoreIndex
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
import chromadb

from prompts2 import State, PromptManager
from llm_config import init_llm_settings
from db_history import get_recent_history
from data.region import get_region_code
from data.search import search_policies

# 1. LLM 및 임베딩 전역 초기화
llm, embed_model = init_llm_settings()

def format_doc(doc) -> str:
    """검색된 정책 문서를 LLM에 넘길 텍스트로 만든다 (본문 + 연령/기간/링크)"""
    m = doc.metadata
    if m.get("min_age", 0) == 0 and m.get("max_age", 999) == 999:
        age_text = "제한 없음"
    else:
        age_text = f"{m.get('min_age', 0)}~{m.get('max_age', 999)}세"

    return (
        f"{doc.page_content}\n"
        f"지원 연령: {age_text}\n"
        f"신청 기간: {m.get('apply_period') or '정보 없음'}\n"
        f"신청 링크: {m.get('apply_url') or '정보 없음'}\n"
        f"참고 링크: {m.get('ref_url') or '정보 없음'}"
    )

def retrieve_node(state: State) -> dict:
    """
    [노드 1] RAG 문서 검색 노드
    - GraphState의 question, location을 활용해 정책 문서를 검색합니다.
    """
    print("--- [Node] 정책 문서 검색 시작 ---")
    question = state.get("question", "")
    location = state.get("location", "")
    age = state.get("age", None)
    
    # 1. 지역 이름(시도, 시군구)을 search.py가 이해하는 행정구역 코드로 변환
    region_code = None
    if location and isinstance(location, str):
        parts = location.strip().split()
        if len(parts) >= 2:
            region_code = get_region_code(parts[0], parts[1])
        elif len(parts) == 1:
            # 시도만 들어온 경우 등 필요에 따라 처리 가능
            pass

    # 2. search.py에 정의된 정식 검색 함수 호출 (메타데이터 필터 + 시맨틱 검색)
    docs = search_policies(
        query=question,
        age=age,
        user_region_code=region_code,
        top_k=2  # 필요한 문서 개수
    )
    
    retrieved_context = [format_doc(doc) for doc in docs]
    
    # GraphState의 context 필드 갱신
    return {"context": retrieved_context}


def generate_node(state: State) -> dict:
    """
    [노드 2] LLM 답변 생성 노드
    - GraphState의 모든 필드를 PromptManager에 연동하여 최종 답변을 생성합니다.
    """
    print("--- [Node] LLM 답변 생성 시작 ---")
    user_id = state.get("user_id", "user_01")
    question = state.get("question", "")
    context = state.get("context", [])
    age = state.get("age", None)
    location = state.get("location", None)

    user_extra_info = state.get("data", "없음")

    chat_history = get_recent_history(user_id=user_id, limit=6)
    
    # 1. UserProfileState 및 PromptManager 연동
    pm = PromptManager(state=state)
    pm.update_profile(extra_info=user_extra_info)
    
    # 2. 프롬프트 템플릿 및 RAG Context 조립
    system_prompt_template = pm.build_system_prompt_str()
    context_str = "\n".join([str(ctx) for ctx in context]) if context else "검색된 관련 문서 없음"
    
    final_prompt = system_prompt_template.format(
        context_str=context_str,
        query_str=question
    )

    final_prompt += f"""
        [이전 대화 기록]
        {chat_history}

        [출력 규칙]
        - 답변은 반드시 자연스러운 한국어로만 작성하세요.
        - 중국어, 영어 등 다른 언어를 절대 출력하지 마세요.
        - 역슬래시 n(\\n) 문자를 텍스트에 직접 쓰지 말고 실제 엔터(줄바꿈)를 치세요.
        - 똑같은 인사말이나 문장을 여러 번 반복하지 마세요.
        - 이전 대화기록이 필요한 경우 적극적으로 활용하세요.
        - 이전 대화기록을 묻거나 정책 정보가 없이도 대답할수있는 간단한 답변의 경우 정책정보를 활용하지 마세요
        
        \n\n[AI 답변]: 
    """

    #print("=== [DEBUG] Final Prompt ===")
    print(final_prompt)
    #print("============================")

    """
    #42~57 대체
    # 프롬프트 템플릿에 state 값을 바로 때려박기
    from prompts import BASE_SYSTEM_PROMPT
    
    context_str = "\n".join([str(ctx) for ctx in context]) if context else "검색된 관련 문서 없음"
    age_str = f"만 {age}세" if isinstance(age, int) else str(age)
    
    final_prompt = BASE_SYSTEM_PROMPT.format(
        age=age_str,
        location=location,
        extra_info=question,
        context_str=context_str,
        query_str=question
    )
    """
    
    # 2. LLM 호출
    response = llm.complete(final_prompt)
    
    return {"generation": response.text}

def evaluate_node(state: State) -> dict:
    """
    [노드] 정보 충족 여부 평가 노드
    - 필수 정보(예: location 등)가 누락되었는지 확인하여 need_more_info 플래그를 결정합니다.
    """
    print("--- [Node] 정보 충족 여부 평가 시작 ---")
    print(f"DEBUG STATE -> question: {state.get('question')}, location: {state.get('location')}, age: {state.get('age')}")
    question = state.get("question", "")
    location = state.get("location", "")

    # 예시 로직: 거주지(location)나 질문이 비어있으면 정보 부족으로 판단
    need_more = False

    if not str(location).strip() or not str(question).strip():
        need_more = True
        
    print(need_more)
    
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
    
    if not location.strip():
        msg = "원활한 정책 검색을 위해 거주하시는 지역(예: 서울특별시, 경기도 등)을 입력해 주세요!"
    elif not question.strip():
        msg = "어떤 청년 정책이나 지원금을 찾고 계신지 구체적인 질문을 입력해 주세요!"
    else:
        msg = "필요한 정보가 부족합니다. 상세 내용을 입력해 주세요."
        
    return {"generation": msg}