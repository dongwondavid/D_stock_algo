import os
import rust_core

# Rust 로그 레벨 설정 (info로 변경하여 중요한 정보만 출력)
os.environ["RUST_LOG"] = "warn"

def test_evaluate_d_for_date_and_time():
    # 테스트할 날짜 (실제 DB가 있다면 해당 날짜로)
    date = "2025-04-29"
    
    # 여러 시간대 테스트
    time_ranges = ["0930", "1000", "1030", "1100", "1130", "1200", "1230", "1300", "1330", "1400", "1430", "1500", "1530"]
    
    for to_time in time_ranges:
        print(f"\n=== 테스트: {date}, 09:00~{to_time} ===")
        try:
            result = rust_core.evaluate_d_for_date_and_time(date, to_time)
            print(f"선정된 종목 수: {len(result)}개")
            if result:
                print("선정된 종목들 (업종별 최고 종목):")
                for code, name, sector in result:
                    print(f"  - {code}: {name} ({sector})")
                    
                    # 상승률 계산 테스트
                    try:
                        increase_rate = rust_core.calculate_increase_rate(code, date, to_time)
                        print(f"    상승률: {increase_rate:.2f}%")
                    except Exception as e:
                        print(f"    상승률 계산 실패: {e}")
            else:
                print("  선정된 종목이 없습니다.")
        except Exception as e:
            print(f"에러 발생: {e}")

def test_increase_rate_calculation():
    """상승률 계산 함수 테스트"""
    print("\n=== 상승률 계산 함수 테스트 ===")
    
    # 테스트용 종목코드들 (실제 DB에 있는 종목으로 변경 필요)
    test_stocks = ["005930", "000660", "035420"]  # 삼성전자, SK하이닉스, NAVER
    date = "2025-03-05"
    time = "0930"
    
    for stock_code in test_stocks:
        try:
            rate = rust_core.calculate_increase_rate(stock_code, date, time)
            print(f"✅ {stock_code}: {rate:.2f}%")
        except Exception as e:
            print(f"❌ {stock_code}: {e}")

def test_batch_increase_rate_calculation():
    """일괄 상승률 계산 함수 테스트"""
    print("\n=== 일괄 상승률 계산 함수 테스트 ===")
    
    test_stocks = ["005930", "000660", "035420"]
    date = "2025-03-05"
    time = "0930"
    
    try:
        results = rust_core.calculate_increase_rates_batch(test_stocks, date, time)
        print("일괄 계산 결과:")
        for code, rate in results:
            print(f"  - {code}: {rate:.2f}%")
    except Exception as e:
        print(f"일괄 계산 실패: {e}")

if __name__ == "__main__":
    test_evaluate_d_for_date_and_time()
    test_increase_rate_calculation()
    test_batch_increase_rate_calculation()