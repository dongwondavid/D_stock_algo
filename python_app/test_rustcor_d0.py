import os
import rust_core

# Rust 로그 레벨 설정 (debug로 변경하여 상세 정보 확인)
os.environ["RUST_LOG"] = "info"

def test_evaluate_d0_for_date_and_time():
    # 테스트할 날짜 (실제 DB가 있다면 해당 날짜로)
    date = "2023-08-31"
    
    # 여러 시간대 테스트
    time_ranges = ["0930", "1000", "1030", "1100"]
    
    for to_time in time_ranges:
        print(f"\n=== 테스트: {date}, 09:00~{to_time} ===")
        try:
            result = rust_core.evaluate_d0_for_date_and_time(date, to_time)
            print(f"D0 종목 수: {len(result)}개")
            if result:
                print("D0 종목들:")
                for code, name, sector in result:
                    print(f"  - {code}: {name} ({sector})")
        except Exception as e:
            print(f"에러 발생: {e}")

if __name__ == "__main__":
    test_evaluate_d0_for_date_and_time()