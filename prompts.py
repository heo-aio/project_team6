# prompts.py
from dataclasses import dataclass
from typing import TypedDict, List, Any, Optional, Dict
from langgraph.graph import StateGraph
from llama_index.core.prompts import PromptTemplate


# ==========================================
# 1. LangGraph 전용 GraphState 정의
# ==========================================
class GraphState(TypedDict):
    """LangGraph 전체 워크플로우 대화 상태 데이터 구조"""
    age: Optional[int]          # 만 나이
    location: Optional[str]     # 거주 지역
    question: str               # 사용자 입력 질문
    generation: str             # LLM 최종 생성 답변
    context: List[Any]          # RAG 검색 결과 문서 데이터
    need_more_info: bool        # 정보 부족 시 역질문 필요 여부 (True/False)


def get_graph():
    """LangGraph StateGraph 생성자"""
    return StateGraph(GraphState)


# ==========================================
# 2. 사용자 프로필 State 관리 클래스
# ==========================================
@dataclass
class UserProfileState:
    """Streamlit UI 및 프롬프트 동적 갱신용 프로필 클래스"""
    age: Optional[int] = None
    location: Optional[str] = None
    extra_info: Optional[str] = None

    def is_profile_complete(self) -> bool:
        """필수 조건(나이, 지역) 입력 완료 여부 확인"""
        return self.age is not None and bool(self.location)

    def to_dict(self) -> Dict[str, Any]:
        """dict 변환 메서드"""
        return {
            "age": self.age if self.age is not None else "미지정",
            "location": self.location if self.location else "미지정",
            "extra_info": self.extra_info if self.extra_info else "없음"
        }


# ==========================================
# 3. 동적 시스템 프롬프트 템플릿 & 매니저
# ==========================================
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
    """UserProfileState 기반 동적 프롬프트 생성 클래스"""

    def __init__(self, state: Optional[UserProfileState] = None):
        self.state = state or UserProfileState()

    def update_state(self, age: Optional[int] = None, location: Optional[str] = None, extra_info: Optional[str] = None):
        """State 상태값 갱신"""
        if age is not None:
            self.state.age = age
        if location is not None:
            self.state.location = location
        if extra_info is not None:
            self.state.extra_info = extra_info

    def build_system_prompt_str(self) -> str:
        """현재 State가 반영된 최종 System Prompt 문자열 반환"""
        state_dict = self.state.to_dict()
        age_val = state_dict["age"]
        age_str = f"만 {age_val}세" if isinstance(age_val, int) else str(age_val)

        return BASE_SYSTEM_PROMPT.format(
            age=age_str,
            location=state_dict["location"],
            extra_info=state_dict["extra_info"],
            context_str="{context_str}",
            query_str="{query_str}"
        )

    def get_rag_prompt_template(self) -> PromptTemplate:
        """LlamaIndex QueryEngine 적용을 위한 PromptTemplate 객체 반환"""
        return PromptTemplate(self.build_system_prompt_str())


if __name__ == "__main__":
    user_state = UserProfileState(age=25, location="서울특별시", extra_info="구직 중")
    pm = PromptManager(state=user_state)
    print("=== 프롬프트 생성 테스트 ===")
    print(pm.build_system_prompt_str()[:350] + "\n...(이하 생략)")