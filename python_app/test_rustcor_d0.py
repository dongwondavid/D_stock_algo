import os
import rust_core

# Rust 로그 레벨 설정 (warn으로 변경하여 중요한 정보만 출력)
os.environ["RUST_LOG"] = "warn"

def test_evaluate_d0_for_date_and_time():
    # 테스트할 날짜 (실제 DB가 있다면 해당 날짜로)
    date = "2023-08-31"
    
    # 여러 시간대 테스트
    time_ranges = ["0930", "1000", "1030", "1100", "1130", "1200", "1230", "1300", "1330", "1400", "1430", "1500", "1530"]
    
    for to_time in time_ranges:
        print(f"\n=== 테스트: {date}, 09:00~{to_time} ===")
        try:
            result = rust_core.evaluate_d0_for_date_and_time(date, to_time)
            print(f"선정된 종목 수: {len(result)}개")
            if result:
                print("선정된 종목:")
                for code, name, sector in result:
                    print(f"  - {code}: {name} ({sector})")
            else:
                print("  선정된 종목이 없습니다.")
        except Exception as e:
            print(f"에러 발생: {e}")

if __name__ == "__main__":
    test_evaluate_d0_for_date_and_time()