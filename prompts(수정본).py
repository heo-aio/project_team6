from typing import Any, List, Optional, TypedDict, Dict
from langgraph.graph import StateGraph
from llama_index.core.prompts import PromptTemplate


# ==========================================
# 1. 통합 State 정의
# ==========================================
class State(TypedDict):
    """LangGraph 및 Streamlit UI 통합 대화 상태 데이터 구조"""
    # 기존 팀원 필수 필드
    question: str
    generation: str
    data: str
    context: List[Any]

    # 프로필 및 흐름 제어 필드
    age: Optional[int]
    location: Optional[str]
    extra_info: Optional[str]
    need_more_info: bool


def get_state() -> StateGraph:
    """LangGraph StateGraph 생성자"""
    return StateGraph(State)


# ==========================================
# 2. State 헬퍼 함수
# ==========================================
def get_formatted_profile_dict(state: State) -> Dict[str, str]:
    """State에서 프로필 정보를 포맷팅된 텍스트 딕셔너리로 변환"""
    age_val = state.get("age")
    age_str = f"만 {age_val}세" if isinstance(age_val, int) else "미지정"

    return {
        "age": age_str,
        "location": state.get("location") or "미지정",
        "extra_info": state.get("extra_info") or "없음"
    }


# ==========================================
# 3. 동적 시스템 프롬프트 템플릿 & 매니저
# ==========================================
# [최적화 1] 줄바꿈 간격 정돈 및 템플릿 인자 포맷 깔끔하게 정제
BASE_SYSTEM_PROMPT = """\
당신은 대한민국 청년들을 위한 '맞춤형 청년 정책 안내 AI 챗봇'입니다.
제공된 정책 정보(RAG Context)를 바탕으로 사용자의 조건에 알맞은 정부 및 지자체 청년 정책을 정확히 안내하세요.

[현재 사용자 프로필 상태]
- 연령/나이: {age}
- 거주 지역: {location}
- 기타 특이사항: {extra_info}

[지침 (Guidelines)]
1. **프로필 기반 답변**: 사용자의 나이({age})와 거주지({location}) 지원 자격 조건을 최우선으로 검토하고 안내하세요.
2. **선제적 역질문 (정보 미비 시)**:
   - 프로필 정보가 '미지정' 상태이거나, 특정 정책 지원 자격 확인(취업 상태, 소득 기준 등)을 위해 추가 정보가 필요하다면 **선제적으로 친절하게 역질문**을 던지세요.
   - 예시: "현재 거주하시는 지역이나 연령대를 말씀해 주시면 더 정확한 청년 지원 정책을 찾아드릴 수 있습니다."
3. **공식 신청 링크 및 접수처 제공**:
   - 정책을 추천할 때는 해당 정책의 **공식 신청 페이지 URL/링크**나 신청 접수처, 주관 기관을 반드시 포함하세요.
4. **출처 기반 답변 (할루시네이션 방지)**:
   - RAG Context에 명시되지 않은 정책 내용을 임의로 지어내지 마세요.
5. **어조**: 친절하고 정중하며 명확한 어조를 유지하세요.

[검색된 정책 정보 (RAG Context)]
{context_str}

[사용자 질문]
{query_str}
"""


class PromptManager:
    """State 기반 동적 프롬프트 관리 클래스"""

    def __init__(self, state: Optional[State] = None):
        # [최적화 2] 얕은 복사 방지 및 기본 상태 값 보장
        default_state: State = {
            "question": "",
            "generation": "",
            "data": "",
            "context": [],
            "age": None,
            "location": None,
            "extra_info": None,
            "need_more_info": False
        }
        if state is not None:
            default_state.update(state)
        self.state: State = default_state

    def update_profile(
        self,
        age: Optional[int] = None,
        location: Optional[str] = None,
        extra_info: Optional[str] = None
    ) -> None:
        """프로필 상태 업데이트 (빈 문자열 처리 포함)"""
        if age is not None:
            self.state["age"] = age
        if location is not None:
            self.state["location"] = location
        if extra_info is not None:
            self.state["extra_info"] = extra_info

    def build_system_prompt_str(self) -> str:
        """State 값으로 시스템 프롬프트 생성 (LlamaIndex 매개변수 유지)"""
        profile = get_formatted_profile_dict(self.state)

        return BASE_SYSTEM_PROMPT.format(
            age=profile["age"],
            location=profile["location"],
            extra_info=profile["extra_info"],
            context_str="{context_str}",
            query_str="{query_str}"
        )

    def get_rag_prompt_template(self) -> PromptTemplate:
        """LlamaIndex QueryEngine 적용을 위한 PromptTemplate 객체 반환"""
        return PromptTemplate(template=self.build_system_prompt_str())


if __name__ == "__main__":
    # 간단한 실행 테스트
    pm = PromptManager({"age": 26, "location": "서울특별시", "extra_info": "취업준비생"})
    print("=== 최적화된 프롬프트 출력 테스트 ===")
    print(pm.build_system_prompt_str()[:320] + "\n...(이하 생략)")