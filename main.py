import client
import db
import model
import signgen
import train
import time

def main():
    print("=== Binance Futures Data Manager ===")
    
    # 예상 시간 계산 (DB 업데이트 시간)
    from config import DATA_START_TIMESTAMP
    current_time = int(time.time() * 1000)  # ms 단위
    start_time = DATA_START_TIMESTAMP
    total_minutes = (current_time - start_time) // (60 * 1000)  # 총 분 수
    api_calls = total_minutes // 1000  # 1000개씩 가져오므로 API 호출 횟수
    estimated_seconds = api_calls * 1  # 1초 간격으로 API 호출
    
    print(f"초기 데이터 수집 시 예상 소요 시간: 약 {estimated_seconds//60}분 {estimated_seconds%60}초")
    print("(1분 간격 데이터, 1000개씩 가져오며 1초 간격으로 API 호출)")
    
    # DB 초기화
    database = db.EquityData()
    
    while True:
        print("\n=== 메뉴 ===")
        print("1. 종목 추가")
        print("2. 모든 종목 데이터 갱신")
        print("3. 종목 목록 보기")
        print("4. 종료")
        
        choice = input("\n선택하세요 (1-4): ").strip()
        
        if choice == '1':
            add_symbol_menu(database)
        elif choice == '2':
            update_all_symbols(database)
        elif choice == '3':
            show_symbols(database)
        elif choice == '4':
            print("프로그램을 종료합니다.")
            database.close()
            break
        else:
            print("잘못된 선택입니다. 다시 선택해주세요.")

def add_symbol_menu(db):
    print("\n=== 종목 추가 ===")
    symbol = input("종목 심볼을 입력하세요 (예: BTC/USDT): ").strip().upper()
    
    if not symbol:
        print("심볼을 입력해주세요.")
        return
    
    # config에서 기본 interval 가져오기
    from config import DEFAULT_INTERVAL, DATA_START_TIMESTAMP
    interval = DEFAULT_INTERVAL
    
    print(f"\n{symbol} 종목을 추가하고 초기 데이터를 수집합니다...")
    print("(2020년 1월 1일부터 현재까지의 데이터를 수집합니다)")
    
    # 예상 시간 계산 (DB 업데이트 시간)
    current_time = int(time.time() * 1000)  # ms 단위
    start_time = DATA_START_TIMESTAMP
    total_minutes = (current_time - start_time) // (60 * 1000)  # 총 분 수
    api_calls = total_minutes // 1000  # 1000개씩 가져오므로 API 호출 횟수
    estimated_seconds = api_calls * 1  # 1초 간격으로 API 호출
    
    print(f"예상 소요 시간: 약 {estimated_seconds//60}분 {estimated_seconds%60}초")
    print("진행하시겠습니까? (y/n): ", end="")
    
    confirm = input().strip().lower()
    if confirm != 'y':
        print("취소되었습니다.")
        return
    
    if db.add_symbol(symbol, interval):
        print(f"{symbol} 종목 추가 완료!")
        print("초기 데이터 수집을 시작합니다...")
        db.update_symbol_data(symbol)
    else:
        print(f"{symbol} 종목이 이미 존재합니다.")

def update_all_symbols(db):
    print("\n=== 모든 종목 데이터 갱신 ===")
    symbols = db.get_symbols()
    
    if not symbols:
        print("등록된 종목이 없습니다.")
        return
    
    print(f"총 {len(symbols)}개 종목의 데이터를 갱신합니다...")
    
    for symbol, interval, last_ts in symbols:
        print(f"\n{symbol} 갱신 중...")
        db.update_symbol_data(symbol)
        time.sleep(1)  # API 호출 간격 조절
    
    print("\n모든 종목 갱신 완료!")

def show_symbols(db):
    print("\n=== 등록된 종목 목록 ===")
    symbols = db.get_symbols()
    
    if not symbols:
        print("등록된 종목이 없습니다.")
        return
    
    for symbol, interval, last_ts in symbols:
        last_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_ts/1000)) if last_ts > 0 else "데이터 없음"
        print(f"종목: {symbol}, 간격: {interval}, 최신 데이터: {last_time}")

if __name__ == "__main__":
    main()