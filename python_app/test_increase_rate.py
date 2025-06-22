import rust_core
import os
from datetime import datetime, timedelta
import statistics

# Rust 로그 레벨 설정
os.environ["RUST_LOG"] = "info"

def test_single_stock_increase_rate():
    """단일 종목 상승률 계산 테스트"""
    print("=" * 60)
    print("📈 단일 종목 상승률 계산 테스트")
    print("=" * 60)
    
    # 테스트용 종목코드들 (실제 DB에 있는 종목들)
    test_stocks = [
        ("005930", "삼성전자"),
        ("000660", "SK하이닉스"),
        ("035420", "NAVER"),
        ("051910", "LG화학"),
        ("006400", "삼성SDI")
    ]
    
    # 테스트 날짜 (실제 DB에 있는 날짜로 변경)
    test_date = "2025-03-05"
    test_time = "0930"
    
    print(f"📅 테스트 날짜: {test_date}")
    print(f"⏰ 테스트 시간: 09:00 ~ {test_time}")
    print()
    
    for code, name in test_stocks:
        try:
            rate = rust_core.calculate_increase_rate(code, test_date, test_time)
            print(f"✅ {name} ({code}): {rate:.2f}%")
        except Exception as e:
            print(f"❌ {name} ({code}): {e}")

def test_multiple_time_intervals():
    """여러 시간대별 상승률 테스트"""
    print("\n" + "=" * 60)
    print("⏰ 여러 시간대별 상승률 테스트")
    print("=" * 60)
    
    test_stock = "005930"  # 삼성전자
    test_date = "2025-03-05"
    time_intervals = ["0930", "1000", "1030", "1100", "1130", "1200", "1230", "1300", "1330", "1400", "1430", "1500", "1530"]
    
    print(f"📊 종목: 삼성전자 ({test_stock})")
    print(f"📅 날짜: {test_date}")
    print()
    
    rates = []
    for time in time_intervals:
        try:
            rate = rust_core.calculate_increase_rate(test_stock, test_date, time)
            rates.append(rate)
            print(f"  {time}: {rate:.2f}%")
        except Exception as e:
            print(f"  {time}: ❌ {e}")
            rates.append(0.0)
    
    if rates:
        print(f"\n📈 통계:")
        print(f"  - 평균: {statistics.mean(rates):.2f}%")
        print(f"  - 최고: {max(rates):.2f}%")
        print(f"  - 최저: {min(rates):.2f}%")
        print(f"  - 중간값: {statistics.median(rates):.2f}%")

def test_batch_calculation():
    """일괄 상승률 계산 테스트"""
    print("\n" + "=" * 60)
    print("🔄 일괄 상승률 계산 테스트")
    print("=" * 60)
    
    test_stocks = ["005930", "000660", "035420", "051910", "006400"]
    test_date = "2025-03-05"
    test_time = "0930"
    
    print(f"📅 날짜: {test_date}")
    print(f"⏰ 시간: 09:00 ~ {test_time}")
    print(f"📊 종목 수: {len(test_stocks)}개")
    print()
    
    try:
        results = rust_core.calculate_increase_rates_batch(test_stocks, test_date, test_time)
        
        print("📈 일괄 계산 결과:")
        total_rate = 0
        valid_count = 0
        
        for code, rate in results:
            print(f"  - {code}: {rate:.2f}%")
            if rate != 0.0:  # 0%는 계산 실패로 간주
                total_rate += rate
                valid_count += 1
        
        if valid_count > 0:
            avg_rate = total_rate / valid_count
            print(f"\n📊 평균 상승률: {avg_rate:.2f}% (유효 종목 {valid_count}개)")
        
    except Exception as e:
        print(f"❌ 일괄 계산 실패: {e}")

def test_custom_period():
    """커스텀 기간 상승률 계산 테스트"""
    print("\n" + "=" * 60)
    print("🎯 커스텀 기간 상승률 계산 테스트")
    print("=" * 60)
    
    test_stock = "005930"  # 삼성전자
    test_date = "2025-03-05"
    
    # 다양한 시간대 조합 테스트
    test_periods = [
        ("1000", "1100", "10:00~11:00"),
        ("1100", "1200", "11:00~12:00"),
        ("1200", "1300", "12:00~13:00"),
        ("1300", "1400", "13:00~14:00"),
        ("1400", "1500", "14:00~15:00"),
    ]
    
    print(f"📊 종목: 삼성전자 ({test_stock})")
    print(f"📅 날짜: {test_date}")
    print()
    
    for from_time, to_time, period_name in test_periods:
        try:
            rate = rust_core.calculate_increase_rate_custom_period(test_stock, test_date, from_time, to_time)
            print(f"  {period_name}: {rate:.2f}%")
        except Exception as e:
            print(f"  {period_name}: ❌ {e}")

def test_different_dates():
    """다른 날짜들의 상승률 비교 테스트"""
    print("\n" + "=" * 60)
    print("📅 다른 날짜들의 상승률 비교 테스트")
    print("=" * 60)
    
    test_stock = "005930"  # 삼성전자
    test_time = "0930"
    
    # 최근 5일간 테스트
    dates = []
    for i in range(5):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        dates.append(date)
    
    print(f"📊 종목: 삼성전자 ({test_stock})")
    print(f"⏰ 시간: 09:00 ~ {test_time}")
    print()
    
    rates = []
    for date in dates:
        try:
            rate = rust_core.calculate_increase_rate(test_stock, date, test_time)
            rates.append(rate)
            print(f"  {date}: {rate:.2f}%")
        except Exception as e:
            print(f"  {date}: ❌ {e}")
            rates.append(0.0)
    
    if rates:
        print(f"\n📈 기간별 통계:")
        print(f"  - 평균: {statistics.mean(rates):.2f}%")
        print(f"  - 최고: {max(rates):.2f}%")
        print(f"  - 최저: {min(rates):.2f}%")

def test_error_handling():
    """에러 처리 테스트"""
    print("\n" + "=" * 60)
    print("⚠️ 에러 처리 테스트")
    print("=" * 60)
    
    # 잘못된 입력들로 테스트
    test_cases = [
        ("INVALID", "2025-03-05", "0930", "잘못된 종목코드"),
        ("005930", "2025-13-45", "0930", "잘못된 날짜"),
        ("005930", "2025-03-05", "2500", "잘못된 시간"),
        ("", "2025-03-05", "0930", "빈 종목코드"),
        ("005930", "", "0930", "빈 날짜"),
    ]
    
    for code, date, time, description in test_cases:
        try:
            rate = rust_core.calculate_increase_rate(code, date, time)
            print(f"  {description}: {rate:.2f}% (예상과 다름)")
        except Exception as e:
            print(f"  {description}: ✅ {e}")

def main():
    """메인 실행 함수"""
    print("🚀 상승률 측정 테스트 시작")
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 각종 테스트 실행
        test_single_stock_increase_rate()
        test_multiple_time_intervals()
        test_batch_calculation()
        test_custom_period()
        test_different_dates()
        test_error_handling()
        
        print("\n" + "=" * 60)
        print("✅ 모든 테스트 완료")
        print(f"⏰ 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        raise

if __name__ == "__main__":
    main() 