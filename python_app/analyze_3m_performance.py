import os
import rust_core
from datetime import datetime, timedelta
import logging
import statistics
import time
from typing import List, Tuple, Dict

# 로깅 설정 - 더 상세한 정보를 위해 INFO 레벨로 변경
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

os.environ["RUST_LOG"] = "warn"

# 수수료 기준 (승률 계산용)
COMMISSION_RATE = 0.249

def calculate_win_rate(rates: List[float]) -> float:
    """수수료 0.249% 이상의 수익률을 보여준 비율을 계산합니다."""
    if not rates:
        return 0.0
    winning_trades = sum(1 for rate in rates if rate > COMMISSION_RATE)
    return (winning_trades / len(rates)) * 100

def plus_30_minutes(time: str) -> str:
    """30분을 더한 시간을 반환합니다."""
    hour = int(time[:2])
    minute = int(time[2:])

    if minute ==30:
        return f"{hour+1:02d}00"
    else:
        return f"{hour:02d}30"

def generate_time_intervals() -> List[str]:
    """하루 중 30분 간격의 시간대를 생성합니다."""
    intervals = []
    for hour in range(9, 16):  # 9시부터 15시까지
        for minute in [0, 30]:
            if hour == 9 and minute == 0:  # 09:00은 시작점이므로 제외
                continue
            if hour == 15 and minute == 30:  # 15:30은 장 마감 후이므로 제외
                continue
            intervals.append(f"{hour:02d}{minute:02d}")
    return intervals

def generate_date_list(days: int = 90) -> List[str]:
    """최근 N일간의 날짜 리스트를 생성합니다."""
    today = datetime.strptime("2025-01-30", "%Y-%m-%d")
    return [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]

def format_time(seconds: float) -> str:
    """초를 읽기 쉬운 시간 형식으로 변환합니다."""
    if seconds < 60:
        return f"{seconds:.1f}초"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}분 {remaining_seconds:.1f}초"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        remaining_seconds = seconds % 60
        return f"{hours}시간 {minutes}분 {remaining_seconds:.1f}초"

def print_progress(current: int, total: int, start_time: float, current_time: float, 
                  success_count: int, error_count: int, no_data_count: int):
    """진행률과 예상 완료 시간을 출력합니다."""
    progress = current / total * 100
    elapsed_time = current_time - start_time
    
    if current > 0:
        avg_time_per_item = elapsed_time / current
        remaining_items = total - current
        estimated_remaining_time = avg_time_per_item * remaining_items
        estimated_completion_time = current_time + estimated_remaining_time
        
        # 진행률 바 생성 (50자 길이)
        bar_length = 50
        filled_length = int(bar_length * current // total)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # 성공률 계산
        total_processed = success_count + error_count + no_data_count
        success_rate = (success_count / total_processed * 100) if total_processed > 0 else 0
        
        print(f"\r[{bar}] {current}/{total} ({progress:.1f}%) | "
              f"성공: {success_count} | 에러: {error_count} | 데이터없음: {no_data_count} | "
              f"성공률: {success_rate:.1f}% | "
              f"경과: {format_time(elapsed_time)} | "
              f"예상완료: {format_time(estimated_remaining_time)} | "
              f"완료시각: {datetime.fromtimestamp(estimated_completion_time).strftime('%H:%M:%S')}", 
              end='', flush=True)

def analyze_3m_performance() -> Dict:
    """3달 동안 30분 간격으로 업종별 최고 종목 선별 및 상승률 분석"""
    
    # 날짜와 시간대 설정
    date_list = generate_date_list(90)
    time_intervals = generate_time_intervals()
    
    total_attempts = len(date_list) * len(time_intervals)
    
    print(f"🚀 3개월 대장주 성과 분석 시작")
    print(f"📅 분석 기간: {len(date_list)}일 ({date_list[-1]} ~ {date_list[0]})")
    print(f"⏰ 분석 시간대: {len(time_intervals)}개 ({time_intervals})")
    print(f"📊 총 시도 횟수: {total_attempts:,}회")
    print(f"⏱️ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 80)
    
    # 결과 저장용 딕셔너리 - 데이터 가용성 분석 추가
    results = {
        'total_attempts': 0,
        'successful_selections': 0,
        'data_unavailable_dates': [],
        'data_unavailable_intervals': {},
        'increase_rates': [],
        'daily_stats': {},
        'interval_stats': {},
        'selected_stocks': [],
        'error_details': []
    }
    
    # 각 시간대별 통계 초기화
    for interval in time_intervals:
        results['interval_stats'][interval] = {
            'count': 0,
            'rates': [],
            'stocks': [],
            'errors': 0,
            'no_data': 0,
            'win_rate': 0.0
        }
        results['data_unavailable_intervals'][interval] = []
    
    # 진행률 추적 변수
    start_time = time.time()
    current_attempt = 0
    success_count = 0
    error_count = 0
    no_data_count = 0
    
    # 각 날짜별로 분석
    for date in date_list:
        daily_rates = []
        daily_stocks = []
        daily_errors = 0
        daily_no_data = 0
        
        for interval in time_intervals:
            current_attempt += 1
            results['total_attempts'] += 1
            
            try:
                # 해당 시간대까지의 업종별 최고 종목 선별
                selected_stocks = rust_core.evaluate_d_for_date_and_time(date, interval)
                
                if selected_stocks:

                    best_stock = selected_stocks[0]

                    results['successful_selections'] += 1
                    results['interval_stats'][interval]['count'] += 1
                    success_count += 1
                    
                    # 선별된 종목 정보 저장
                    for code, name, sector in [best_stock]:
                        stock_info = {
                            'date': date,
                            'time': interval,
                            'code': code,
                            'name': name,
                            'sector': sector
                        }
                        results['selected_stocks'].append(stock_info)
                        results['interval_stats'][interval]['stocks'].append(stock_info)
                        daily_stocks.append(stock_info)
                    
                    # 실제 상승률 계산 (30분 간격)
                    for code, name, sector in [best_stock]:
                        try:
                            interval_30 = plus_30_minutes(interval)
                            increase_rate = rust_core.calculate_30min_increase_rate(code, date, interval_30)
                            
                            results['increase_rates'].append(increase_rate)
                            results['interval_stats'][interval]['rates'].append(increase_rate)
                            daily_rates.append(increase_rate)
                            
                        except Exception as e:
                            logging.warning(f"  ⚠️ {code} 상승률 계산 실패: {e}")
                            # 상승률 계산 실패시 0%로 처리
                            results['increase_rates'].append(0.0)
                            results['interval_stats'][interval]['rates'].append(0.0)
                            daily_rates.append(0.0)
                else:
                    results['interval_stats'][interval]['no_data'] += 1
                    daily_no_data += 1
                    no_data_count += 1
                    results['data_unavailable_intervals'][interval].append(date)
                    
            except Exception as e:
                error_msg = f"{date} {interval} 처리 실패: {e}"
                logging.warning(f"  ⚠️ {error_msg}")
                results['interval_stats'][interval]['errors'] += 1
                daily_errors += 1
                error_count += 1
                results['error_details'].append({
                    'date': date,
                    'interval': interval,
                    'error': str(e)
                })
            
            # 진행률 출력 (매 10번째 시도마다 또는 마지막 시도)
            if current_attempt % 10 == 0 or current_attempt == total_attempts:
                print_progress(current_attempt, total_attempts, start_time, time.time(),
                             success_count, error_count, no_data_count)
        
        # 일별 통계 저장
        if daily_rates:
            results['daily_stats'][date] = {
                'count': len(daily_rates),
                'avg_rate': statistics.mean(daily_rates),
                'max_rate': max(daily_rates),
                'min_rate': min(daily_rates),
                'win_rate': calculate_win_rate(daily_rates),
                'stocks': daily_stocks,
                'errors': daily_errors,
                'no_data': daily_no_data
            }
        else:
            # 데이터가 전혀 없는 날짜 기록
            results['data_unavailable_dates'].append(date)
            results['daily_stats'][date] = {
                'count': 0,
                'avg_rate': 0.0,
                'max_rate': 0.0,
                'min_rate': 0.0,
                'win_rate': 0.0,
                'stocks': [],
                'errors': daily_errors,
                'no_data': daily_no_data
            }
    
    # 최종 진행률 출력
    print_progress(total_attempts, total_attempts, start_time, time.time(),
                  success_count, error_count, no_data_count)
    print()  # 줄바꿈
    
    # 각 시간대별 승률 계산
    for interval in time_intervals:
        if results['interval_stats'][interval]['rates']:
            results['interval_stats'][interval]['win_rate'] = calculate_win_rate(results['interval_stats'][interval]['rates'])
    
    # 전체 통계 계산
    if results['increase_rates']:
        results['overall_stats'] = {
            'avg_rate': statistics.mean(results['increase_rates']),
            'median_rate': statistics.median(results['increase_rates']),
            'max_rate': max(results['increase_rates']),
            'min_rate': min(results['increase_rates']),
            'std_dev': statistics.stdev(results['increase_rates']) if len(results['increase_rates']) > 1 else 0,
            'win_rate': calculate_win_rate(results['increase_rates'])
        }
    
    # 실행 시간 정보 추가
    total_time = time.time() - start_time
    results['execution_info'] = {
        'start_time': datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S'),
        'end_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_time': total_time,
        'avg_time_per_attempt': total_time / total_attempts if total_attempts > 0 else 0
    }
    
    return results

def print_analysis_results(results: Dict):
    """분석 결과를 출력합니다."""
    
    print("\n" + "="*60)
    print("📊 3개월 업종별 최고 종목 선별 및 상승률 분석 결과")
    print("="*60)
    
    # 실행 정보
    if 'execution_info' in results:
        exec_info = results['execution_info']
        print(f"\n⏱️ 실행 정보:")
        print(f"  - 시작 시간: {exec_info['start_time']}")
        print(f"  - 종료 시간: {exec_info['end_time']}")
        print(f"  - 총 실행 시간: {format_time(exec_info['total_time'])}")
        print(f"  - 평균 처리 시간: {exec_info['avg_time_per_attempt']:.3f}초/시도")
    
    # 데이터 가용성 분석
    print(f"\n📋 데이터 가용성 분석:")
    print(f"  - 총 시도 횟수: {results['total_attempts']:,}회")
    print(f"  - 성공 선별 횟수: {results['successful_selections']:,}회")
    print(f"  - 선별 성공률: {results['successful_selections']/results['total_attempts']*100:.1f}%")
    print(f"  - 데이터 없는 날짜: {len(results['data_unavailable_dates'])}일")
    print(f"  - 데이터 없는 날짜 비율: {len(results['data_unavailable_dates'])/len(results['daily_stats'])*100:.1f}%")
    
    if results['data_unavailable_dates']:
        print(f"  - 데이터 없는 날짜 샘플: {results['data_unavailable_dates'][:10]}")
    
    # 전체 통계
    if 'overall_stats' in results:
        stats = results['overall_stats']
        print(f"\n📈 전체 통계:")
        print(f"  - 평균 상승률: {stats['avg_rate']:.2f}%")
        print(f"  - 중간값 상승률: {stats['median_rate']:.2f}%")
        print(f"  - 최고 상승률: {stats['max_rate']:.2f}%")
        print(f"  - 최저 상승률: {stats['min_rate']:.2f}%")
        print(f"  - 표준편차: {stats['std_dev']:.2f}%")
        print(f"  - 승률 (수수료 {COMMISSION_RATE}% 이상): {stats['win_rate']:.1f}%")
    
    # 시간대별 통계
    print(f"\n⏰ 시간대별 통계:")
    for interval, stats in results['interval_stats'].items():
        total_attempts = stats['count'] + stats['errors'] + stats['no_data']
        if total_attempts > 0:
            success_rate = stats['count'] / total_attempts * 100
            error_rate = stats['errors'] / total_attempts * 100
            no_data_rate = stats['no_data'] / total_attempts * 100
            
            print(f"  - {interval}: 성공 {stats['count']}회 ({success_rate:.1f}%), "
                  f"에러 {stats['errors']}회 ({error_rate:.1f}%), "
                  f"데이터없음 {stats['no_data']}회 ({no_data_rate:.1f}%)")
            
            if stats['rates']:
                avg_rate = statistics.mean(stats['rates'])
                print(f"    평균 상승률: {avg_rate:.2f}%, 승률: {stats['win_rate']:.1f}%")
    
    # 상위 성과 시간대
    print(f"\n🏆 상위 성과 시간대 (선별 횟수 기준):")
    sorted_intervals = sorted(
        results['interval_stats'].items(), 
        key=lambda x: x[1]['count'], 
        reverse=True
    )
    for i, (interval, stats) in enumerate(sorted_intervals[:5], 1):
        if stats['count'] > 0:
            avg_rate = statistics.mean(stats['rates'])
            print(f"  {i}. {interval}: {stats['count']}회, 평균 {avg_rate:.2f}%, 승률 {stats['win_rate']:.1f}%")
    
    # 에러 분석
    if results['error_details']:
        print(f"\n⚠️ 에러 분석:")
        error_types = {}
        for error in results['error_details']:
            error_msg = error['error']
            if 'database' in error_msg.lower() or 'connection' in error_msg.lower():
                error_types['DB 연결'] = error_types.get('DB 연결', 0) + 1
            elif 'table' in error_msg.lower():
                error_types['테이블 없음'] = error_types.get('테이블 없음', 0) + 1
            elif 'data' in error_msg.lower():
                error_types['데이터 없음'] = error_types.get('데이터 없음', 0) + 1
            else:
                error_types['기타'] = error_types.get('기타', 0) + 1
        
        for error_type, count in error_types.items():
            print(f"  - {error_type}: {count}회")
    
    # 상위 성과 종목
    print(f"\n🎯 상위 선별 종목:")
    stock_counts = {}
    for stock in results['selected_stocks']:
        key = f"{stock['name']} ({stock['code']})"
        stock_counts[key] = stock_counts.get(key, 0) + 1
    
    sorted_stocks = sorted(stock_counts.items(), key=lambda x: x[1], reverse=True)
    for i, (stock_name, count) in enumerate(sorted_stocks[:10], 1):
        print(f"  {i}. {stock_name}: {count}회 선별")

def main():
    """메인 실행 함수"""
    try:
        # 분석 실행
        results = analyze_3m_performance()
        
        # 결과 출력
        print_analysis_results(results)
        
        print("\n✅ 분석 완료")
        
    except Exception as e:
        logging.error(f"❌ 분석 중 오류 발생: {e}")
        raise

if __name__ == "__main__":
    main() 