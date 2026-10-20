# llm_config.py
import requests
from typing import Tuple
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core import Settings


def check_ollama_status(base_url: str = "http://localhost:11434") -> bool:
    """Ollama 데몬 서버 동작 상태 확인"""
    try:
        response = requests.get(base_url, timeout=3)
        return response.status_code == 200
    except Exception:
        return False


def get_optimized_ollama_llm(
    model_name: str = "qwen2.5",
    base_url: str = "http://localhost:11434",
    num_ctx: int = 4096,
    temperature: float = 0.1,
) -> Ollama:
    """
    VRAM/RAM 최적화 옵션이 적용된 Ollama LLM 인스턴스를 반환합니다.
    """
    return Ollama(
        model=model_name,
        base_url=base_url,
        request_timeout=120.0,
        temperature=temperature,
        additional_kwargs={
            "num_ctx": num_ctx,      # 맥락 길이 제한 -> VRAM 대폭 절감
            "low_vram": False,       # GPU VRAM 4GB 이하일 경우 True로 변경 가능
            "f16_kv": True,          # Key-Value 캐시 FP16 압축
        }
    )


def init_llm_settings(
    primary_model: str = "qwen2.5",
    fallback_model: str = "llama3.1",
    embed_model_name: str = "nomic-embed-text",
    base_url: str = "http://localhost:11434",
    num_ctx: int = 4096
) -> Tuple[Ollama, OllamaEmbedding]:
    """
    메모리 최적화 및 Fallback 처리 구조가 적용된 LlamaIndex 전역 세팅 초기화 함수
    """
    if not check_ollama_status(base_url):
        raise ConnectionError(
            f"[Error] Ollama 서버({base_url})가 실행되어 있지 않습니다. 터미널에서 'ollama serve'를 확인하세요."
        )

    # 1. Primary LLM 로드 시도
    try:
        llm = get_optimized_ollama_llm(model_name=primary_model, base_url=base_url, num_ctx=num_ctx)
        llm.complete("ping", formatted=False)
        print(f"[OK] 주 모델 ({primary_model}) 로드 완료 (Context Window: {num_ctx})")
    except Exception as e:
        print(f"[경고] {primary_model} 로드 실패: {e}. 대체 모델({fallback_model})로 전환합니다.")
        try:
            llm = get_optimized_ollama_llm(model_name=fallback_model, base_url=base_url, num_ctx=num_ctx)
            print(f"[OK] 대체 모델 ({fallback_model}) 로드 완료")
        except Exception as fallback_err:
            raise RuntimeError(f"[Fatal] 모든 LLM 모델 로드 실패: {fallback_err}")

    # 2. 임베딩 모델 메모리 제어
    embed_model = OllamaEmbedding(
        model_name=embed_model_name,
        base_url=base_url,
        embed_batch_size=10,  # 배치 크기를 축소해 순간 메모리 폭증 방지
    )

    # 3. LlamaIndex 전역 Settings 적용
    Settings.llm = llm
    Settings.embed_model = embed_model
    Settings.context_window = num_ctx

    return llm, embed_model


if __name__ == "__main__":
    llm, embed = init_llm_settings()
    res = llm.complete("안녕하세요!")
    print("\n[응답 테스트]:", res.text)