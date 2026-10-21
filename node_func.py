from prompts import GraphState, PromptManager, UserProfileState
from llama_index.core import VectorStoreIndex
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from llm_config import init_llm_settings
import chromadb

# 1. LLM 및 임베딩 전역 초기화
llm, embed_model = init_llm_settings()

def retrieve_node(state: GraphState) -> dict:
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
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(f"{state.get('location')} 청년 정책 {state.get('question')}")
    
    retrieved_context = [doc.page_content for doc in docs]
    
    # GraphState의 context 필드 갱신
    return {"context": retrieved_context}


def generate_node(state: GraphState) -> dict:
    """
    [노드 2] LLM 답변 생성 노드
    - GraphState의 모든 필드를 PromptManager에 연동하여 최종 답변을 생성합니다.
    """
    print("--- [Node] LLM 답변 생성 시작 ---")
    question = state.get("question", "")
    context = state.get("context", [])
    age = state.get("age", None)
    location = state.get("location", None)
    
    # 1. UserProfileState 및 PromptManager 연동
    user_profile = UserProfileState(
        age=age,
        location=location,
        extra_info=question
    )
    pm = PromptManager(state=user_profile)
    
    # 2. 프롬프트 템플릿 및 RAG Context 조립
    system_prompt_template = pm.build_system_prompt_str()
    context_str = "\n".join([str(ctx) for ctx in context]) if context else "검색된 관련 문서 없음"
    
    final_prompt = system_prompt_template.format(
        context_str=context_str,
        query_str=question
    )

    final_prompt += """
        - 답변은 반드시 자연스러운 한국어로만 작성하세요. 
        - 중국어, 영어 등 다른 언어를 절대 섞어서 출력하지 마세요.
        - 코드 형태의 특수문자(\n 등)를 노출하지 말고 실제 줄바꿈을 사용하세요.
        
        \n\n[AI 답변]: 
    """

    #print("=== [DEBUG] Final Prompt ===")
    #print(final_prompt)
    #print("============================")

    """
    42~57 대체
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

def evaluate_node(state: GraphState) -> dict:
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

def router(state: GraphState):
    """평가 결과에 따라 다음 노드를 결정하는 라우팅 함수"""
    if state.get("need_more_info", False):
        return "ask_more"  # 정보가 부족하면 추가 정보 요구 노드로
    else:
        return "retrieve"

def ask_more_node(state: GraphState) -> dict:
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