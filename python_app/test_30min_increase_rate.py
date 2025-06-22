import os
import rust_core
from datetime import datetime, timedelta
import statistics

# Rust 로그 레벨 설정
os.environ["RUST_LOG"] = "info"

def test_30min_vs_cumulative():
    """30분 간격 상승률 vs 누적 상승률 비교 테스트"""
    print("=" * 80)
    print("📊 30분 간격 상승률 vs 누적 상승률 비교 테스트")
    print("=" * 80)
    
    test_stock = "005930"  # 삼성전자
    test_date = "2025-03-05"
    time_intervals = ["0930", "1000", "1030", "1100", "1130", "1200", "1230", "1300", "1330", "1400", "1430", "1500", "1530"]
    
    print(f"📊 종목: 삼성전자 ({test_stock})")
    print(f"📅 날짜: {test_date}")
    print()
    print(f"{'시간대':<8} {'30분간격':<12} {'누적(09:00~)':<15} {'차이':<10}")
    print("-" * 50)
    
    cumulative_rates = []
    interval_rates = []
    
    for time in time_intervals:
        try:
            # 30분 간격 상승률
            interval_rate = rust_core.calculate_30min_increase_rate(test_stock, test_date, time)
            interval_rates.append(interval_rate)
            
            # 누적 상승률 (09:00부터)
            cumulative_rate = rust_core.calculate_increase_rate(test_stock, test_date, time)
            cumulative_rates.append(cumulative_rate)
            
            # 차이 계산
            difference = cumulative_rate - interval_rate
            
            print(f"{time:<8} {interval_rate:<12.2f}% {cumulative_rate:<15.2f}% {difference:<10.2f}%")
            
        except Exception as e:
            print(f"{time:<8} ❌ 오류: {e}")
            interval_rates.append(0.0)
            cumulative_rates.append(0.0)
    
    print("-" * 50)
    if interval_rates and cumulative_rates:
        print(f"📈 30분 간격 통계:")
        print(f"  - 평균: {statistics.mean(interval_rates):.2f}%")
        print(f"  - 최고: {max(interval_rates):.2f}%")
        print(f"  - 최저: {min(interval_rates):.2f}%")
        print(f"  - 표준편차: {statistics.stdev(interval_rates):.2f}%")
        
        print(f"\n📈 누적 상승률 통계:")
        print(f"  - 평균: {statistics.mean(cumulative_rates):.2f}%")
        print(f"  - 최고: {max(cumulative_rates):.2f}%")
        print(f"  - 최저: {min(cumulative_rates):.2f}%")
        print(f"  - 표준편차: {statistics.stdev(cumulative_rates):.2f}%")

def test_multiple_stocks_30min():
    """여러 종목의 30분 간격 상승률 테스트"""
    print("\n" + "=" * 80)
    print("📊 여러 종목 30분 간격 상승률 테스트")
    print("=" * 80)
    
    test_stocks = [
        ("005930", "삼성전자"),
        ("000660", "SK하이닉스"),
        ("035420", "NAVER"),
        ("051910", "LG화학"),
        ("006400", "삼성SDI")
    ]
    
    test_date = "2025-03-05"
    test_time = "1030"  # 10:00~10:30 구간
    
    print(f"📅 날짜: {test_date}")
    print(f"⏰ 시간: 10:00~10:30 (30분 간격)")
    print()
    
    rates = []
    for code, name in test_stocks:
        try:
            # 30분 간격 상승률
            interval_rate = rust_core.calculate_30min_increase_rate(code, test_date, test_time)
            rates.append(interval_rate)
            print(f"✅ {name} ({code}): {interval_rate:.2f}%")
        except Exception as e:
            print(f"❌ {name} ({code}): {e}")
            rates.append(0.0)
    
    if rates:
        print(f"\n📈 30분 간격 통계:")
        print(f"  - 평균: {statistics.mean(rates):.2f}%")
        print(f"  - 최고: {max(rates):.2f}%")
        print(f"  - 최저: {min(rates):.2f}%")
        print(f"  - 중간값: {statistics.median(rates):.2f}%")

def test_time_series_30min():
    """시간대별 30분 간격 상승률 시계열 테스트"""
    print("\n" + "=" * 80)
    print("📊 시간대별 30분 간격 상승률 시계열 테스트")
    print("=" * 80)
    
    test_stock = "005930"  # 삼성전자
    test_date = "2025-03-05"
    time_intervals = ["0930", "1000", "1030", "1100", "1130", "1200", "1230", "1300", "1330", "1400", "1430", "1500", "1530"]
    
    print(f"📊 종목: 삼성전자 ({test_stock})")
    print(f"📅 날짜: {test_date}")
    print()
    print(f"{'시간대':<8} {'구간':<15} {'상승률':<10}")
    print("-" * 35)
    
    rates = []
    for time in time_intervals:
        try:
            # 30분 간격 상승률
            rate = rust_core.calculate_30min_increase_rate(test_stock, test_date, time)
            rates.append(rate)
            
            # 구간 표시
            if time == "0930":
                period = "09:00~09:30"
            else:
                # 이전 시간 계산
                hour = int(time[:2])
                minute = int(time[2:])
                if minute == 0:
                    prev_hour = hour - 1
                    prev_minute = 30
                else:
                    prev_hour = hour
                    prev_minute = 0
                period = f"{prev_hour:02d}:{prev_minute:02d}~{hour:02d}:{minute:02d}"
            
            print(f"{time:<8} {period:<15} {rate:<10.2f}%")
            
        except Exception as e:
            print(f"{time:<8} ❌ 오류: {e}")
            rates.append(0.0)
    
    print("-" * 35)
    if rates:
        print(f"📈 시계열 통계:")
        print(f"  - 평균: {statistics.mean(rates):.2f}%")
        print(f"  - 최고: {max(rates):.2f}%")
        print(f"  - 최저: {min(rates):.2f}%")
        print(f"  - 변동성: {statistics.stdev(rates):.2f}%")
        
        # 상승/하락 구간 분석
        positive_count = sum(1 for r in rates if r > 0)
        negative_count = sum(1 for r in rates if r < 0)
        zero_count = sum(1 for r in rates if r == 0)
        
        print(f"  - 상승 구간: {positive_count}개")
        print(f"  - 하락 구간: {negative_count}개")
        print(f"  - 보합 구간: {zero_count}개")

def test_different_dates_30min():
    """다른 날짜들의 30분 간격 상승률 비교"""
    print("\n" + "=" * 80)
    print("📊 다른 날짜들의 30분 간격 상승률 비교")
    print("=" * 80)
    
    test_stock = "005930"  # 삼성전자
    test_time = "1030"  # 10:00~10:30 구간
    
    # 최근 5일간 테스트
    dates = []
    for i in range(5):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        dates.append(date)
    
    print(f"📊 종목: 삼성전자 ({test_stock})")
    print(f"⏰ 시간: 10:00~10:30 (30분 간격)")
    print()
    
    rates = []
    for date in dates:
        try:
            rate = rust_core.calculate_30min_increase_rate(test_stock, date, test_time)
            rates.append(rate)
            print(f"  {date}: {rate:.2f}%")
        except Exception as e:
            print(f"  {date}: ❌ {e}")
            rates.append(0.0)
    
    if rates:
        print(f"\n📈 날짜별 통계:")
        print(f"  - 평균: {statistics.mean(rates):.2f}%")
        print(f"  - 최고: {max(rates):.2f}%")
        print(f"  - 최저: {min(rates):.2f}%")
        print(f"  - 변동성: {statistics.stdev(rates):.2f}%")

def main():
    """메인 실행 함수"""
    print("🚀 30분 간격 상승률 계산 테스트 시작")
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 각종 테스트 실행
        test_30min_vs_cumulative()
        test_multiple_stocks_30min()
        test_time_series_30min()
        test_different_dates_30min()
        
        print("\n" + "=" * 80)
        print("✅ 모든 테스트 완료")
        print(f"⏰ 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        raise

if __name__ == "__main__":
    main() 