db_path = "D:/db/stock_price(5min).db"

import sqlite3
import polars as pl
from datetime import datetime, timedelta

def get_top_30_trading_volume_by_date(start_date=None, end_date=None):
    """
    9시~9시반까지의 각 날짜별 거래대금 상위 30종을 가져오는 함수
    
    Args:
        start_date (str): 시작 날짜 (YYYY-MM-DD 형식, None이면 최근 30일)
        end_date (str): 종료 날짜 (YYYY-MM-DD 형식, None이면 오늘)
    
    Returns:
        dict: 날짜별 상위 30종 거래대금 데이터
    """
    
    # 날짜 설정
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    conn = sqlite3.connect(db_path)
    
    try:
        # 9시~9시반 거래대금 상위 30종 쿼리
        query = """
        WITH trading_volume AS (
            SELECT 
                date,
                code,
                name,
                SUM(volume * price) as total_trading_value,
                SUM(volume) as total_volume,
                AVG(price) as avg_price
            FROM stock_price 
            WHERE time BETWEEN '09:00' AND '09:30'
                AND date BETWEEN ? AND ?
            GROUP BY date, code, name
        ),
        ranked_stocks AS (
            SELECT 
                *,
                ROW_NUMBER() OVER (PARTITION BY date ORDER BY total_trading_value DESC) as rank
            FROM trading_volume
        )
        SELECT 
            date,
            code,
            name,
            total_trading_value,
            total_volume,
            avg_price,
            rank
        FROM ranked_stocks
        WHERE rank <= 30
        ORDER BY date DESC, rank ASC
        """
        
        # 데이터 가져오기 (polars 사용)
        df = pl.read_database(query, conn, args=[start_date, end_date])
        
        # 날짜별로 그룹화
        result = {}
        for date in df['date'].unique():
            daily_data = df.filter(pl.col('date') == date).sort('rank')
            result[date] = daily_data
        
        return result
        
    except Exception as e:
        print(f"데이터베이스 조회 중 오류 발생: {e}")
        return {}
    
    finally:
        conn.close()

def print_top_30_summary(result):
    """
    상위 30종 결과를 출력하는 함수
    """
    for date, data in result.items():
        print(f"\n=== {date} 거래대금 상위 30종 ===")
        print(f"{'순위':<4} {'종목코드':<8} {'종목명':<15} {'거래대금(억원)':<12} {'거래량':<10}")
        print("-" * 60)
        
        for row in data.iter_rows(named=True):
            trading_value_billion = row['total_trading_value'] / 100000000  # 억원 단위
            print(f"{row['rank']:<4} {row['code']:<8} {row['name']:<15} {trading_value_billion:>10.2f} {row['total_volume']:>10,}")

def get_specific_date_top_30(target_date):
    """
    특정 날짜의 상위 30종만 가져오는 함수
    
    Args:
        target_date (str): 조회할 날짜 (YYYY-MM-DD 형식)
    
    Returns:
        polars.DataFrame: 해당 날짜의 상위 30종 데이터
    """
    result = get_top_30_trading_volume_by_date(target_date, target_date)
    return result.get(target_date, pl.DataFrame())

# 사용 예시
if __name__ == "__main__":
    # 최근 7일간의 상위 30종 조회
    print("최근 7일간 9시~9시반 거래대금 상위 30종 조회 중...")
    recent_data = get_top_30_trading_volume_by_date(
        start_date=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
        end_date=datetime.now().strftime('%Y-%m-%d')
    )
    
    if recent_data:
        print_top_30_summary(recent_data)
    else:
        print("데이터를 찾을 수 없습니다.")
    
    # 특정 날짜 조회 예시
    # specific_date = "2024-01-15"
    # daily_data = get_specific_date_top_30(specific_date)
    # if not daily_data.is_empty():
    #     print(f"\n=== {specific_date} 상위 30종 ===")
    #     print(daily_data.select(['rank', 'code', 'name', 'total_trading_value']).head(10))