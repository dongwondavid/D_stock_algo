import rust_core
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import logging

# 날짜 리스트 생성 (최근 3개월, 실제 DB에 있는 날짜만 사용해야 함)
def generate_date_list(days=90):
    today = datetime.today()
    return [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]

# D 종목 수집 및 업종 분석
def analyze_industry_overlaps(date_list):
    industry_counter = Counter()
    industry_date_map = defaultdict(set)

    for date in date_list:
        try:
            results = rust_core.evaluate_d_for_date_and_time(date, "0930")
            if not results:
                continue  # D 종목이 없는 날짜는 제외

            # 업종별 최고 종목들이 반환되므로 각 업종별로 카운트
            for _, _, industry in results:
                industry_counter[industry] += 1
                industry_date_map[industry].add(date)

        except Exception as e:
            print(f"⚠️ {date} 처리 실패: {e}")

    return industry_counter, industry_date_map

# 실행 예시
if __name__ == "__main__":
    date_list = generate_date_list(90)

    logging.info(f"date_list 완성")
    industry_counts, industry_dates = analyze_industry_overlaps(date_list)

    logging.info(f"industry_counts 완성")

    print("\n📌 업종별 선정 빈도 (최근 3개월 기준):")
    for industry, count in industry_counts.most_common():
        print(f"- {industry}: {count}일")

    print("\n🗓️ 업종별 선정된 날짜 샘플:")
    for industry, dates in industry_dates.items():
        print(f"- {industry} ({len(dates)}일): {sorted(dates)[:5]} ...")
