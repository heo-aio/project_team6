# scheduler.py
import os
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

LOG_FILE = "./store/last_update.txt"

# ① 실제 작업 함수
async def task1(msg: str):
    print(f"[{datetime.now()}] 작업 실행 중: {msg}")
    
    # TODO: 팀원이 만든 파이프라인 함수 연결
    # raw_data = fetch_api_data()
    # cleaned_data = clean_data(raw_data)
    # insert_to_db(cleaned_data)

    # call_policies_api
    # call_region_api
    # build_region_codes
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(today_str)
    print(f"[{datetime.now()}] 데이터 업데이트 및 기록 완료 ({today_str})")

# ② 부팅 시 누락분 체크 함수
async def check_and_run_on_startup():
    today_str = datetime.now().strftime("%Y-%m-%d")
    last_updated = ""
    
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            last_updated = f.read().strip()
            
    if last_updated != today_str:
        print("[부팅 체크] 오늘 자정 업데이트를 놓쳤거나 서버가 새로 켜졌습니다. 누락된 데이터를 갱신합니다.")
        await task1("서버 부팅 시 누락분 즉시 업데이트")
    else:
        print("[부팅 체크] 데이터가 이미 최신 상태입니다.")


# ③ 스케줄러 구동 함수
def sch_start():
    sch = AsyncIOScheduler()
    sch.add_job(
        task1, 
        'cron',
        hour=0, minute=0,
        id='midnight_update',
        args=['자정 정기 업데이트']
    )
    sch.start()
    print("일일 자정 데이터 수집 스케줄러가 등록되었습니다.")
    return sch