import os
import rust_core
from datetime import datetime, timedelta
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
os.environ["RUST_LOG"] = "info"

def test_db_connection():
    """데이터베이스 연결과 기본 데이터 존재 여부를 테스트합니다."""
    
    print("🔍 데이터베이스 연결 테스트 시작")
    print("="*50)
    
    # 최근 날짜들로 테스트
    test_dates = []
    today = datetime.today()
    for i in range(10):
        test_date = today - timedelta(days=i)
        test_dates.append(test_date.strftime("%Y-%m-%d"))
    
    print(f"📅 테스트 날짜: {test_dates}")
    print()
    
    success_count = 0
    error_count = 0
    no_data_count = 0
    
    for date in test_dates:
        print(f"📅 {date} 테스트 중...")
        
        try:
            # 간단한 시간대로 테스트 (09:30)
            result = rust_core.evaluate_d_for_date_and_time(date, "0930")
            
            if result:
                print(f"  ✅ 성공: {len(result)}개 종목 선별 (업종별 최고 종목)")
                for code, name, sector in result:
                    print(f"    - {name} ({code}) - {sector}")
                success_count += 1
            else:
                print(f"  ❌ 데이터 없음 또는 조건 불만족")
                no_data_count += 1
                
        except Exception as e:
            print(f"  ⚠️ 오류 발생: {e}")
            error_count += 1
        
        print()
    
    # 결과 요약
    print("="*50)
    print("📊 테스트 결과 요약:")
    print(f"  - 총 테스트: {len(test_dates)}일")
    print(f"  - 성공: {success_count}일")
    print(f"  - 데이터 없음: {no_data_count}일")
    print(f"  - 오류: {error_count}일")
    print(f"  - 성공률: {success_count/len(test_dates)*100:.1f}%")
    
    if success_count > 0:
        print("\n✅ 데이터베이스 연결 및 데이터 접근 정상")
    elif no_data_count > 0:
        print("\n⚠️ 데이터베이스는 연결되지만 해당 날짜의 데이터가 없음")
    else:
        print("\n❌ 데이터베이스 연결 또는 데이터 접근에 문제가 있음")

def test_specific_date():
    """특정 날짜에 대해 더 상세한 테스트를 수행합니다."""
    
    print("\n🔍 특정 날짜 상세 테스트")
    print("="*50)
    
    # 오늘 날짜로 테스트
    today = datetime.today().strftime("%Y-%m-%d")
    print(f"📅 테스트 날짜: {today}")
    
    # 여러 시간대로 테스트
    time_intervals = ["0930", "1000", "1030", "1100", "1130", "1200"]
    
    for interval in time_intervals:
        print(f"\n⏰ {interval} 시간대 테스트:")
        try:
            result = rust_core.evaluate_d_for_date_and_time(today, interval)
            
            if result:
                print(f"  ✅ 성공: {len(result)}개 종목 (업종별 최고 종목)")
                for code, name, sector in result:
                    print(f"    - {name} ({code}) - {sector}")
            else:
                print(f"  ❌ 선별된 종목 없음")
                
        except Exception as e:
            print(f"  ⚠️ 오류: {e}")

def main():
    """메인 실행 함수"""
    try:
        # 기본 연결 테스트
        test_db_connection()
        
        # 특정 날짜 상세 테스트
        test_specific_date()
        
        print("\n✅ 모든 테스트 완료")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        raise

if __name__ == "__main__":
    main() 