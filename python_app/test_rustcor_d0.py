import os
import rust_core

# Rust 로그 레벨 설정 (debug로 변경하여 상세 정보 확인)
os.environ["RUST_LOG"] = "debug"

def test_evaluate_d0_for_date():
    # 테스트할 날짜 (실제 DB가 있다면 해당 날짜로)
    date = "2025-04-29"
    try:
        result = rust_core.evaluate_d0_for_date(date)
        print(f"D0 종목 리스트 ({date}):", result)
    except Exception as e:
        print("에러 발생:", e)

if __name__ == "__main__":
    test_evaluate_d0_for_date()