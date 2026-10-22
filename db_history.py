import sqlite3

DB_PATH = "chat_history.db"


def init_db():
    """대화 히스토리 테이블 생성"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL,       -- 'user' 또는 'assistant'
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_message(user_id: str, role: str, message: str):
    """메시지 DB 저장"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_history (user_id, role, message) VALUES (?, ?, ?)",
        (user_id, role, message)
    )
    conn.commit()
    conn.close()


def get_recent_history(user_id: str, limit: int = 6) -> str:
    """최근 대화 내역 조회 후 프롬프트용 텍스트 변환"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, message FROM chat_history 
        WHERE user_id = ? 
        ORDER BY id DESC LIMIT ?
    """, (user_id, limit))
    rows = cursor.fetchall()
    conn.close()

    rows.reverse()

    history_str = ""
    for role, msg in rows:
        prefix = "사용자" if role == "user" else "AI"
        history_str += f"{prefix}: {msg}\n"
    return history_str