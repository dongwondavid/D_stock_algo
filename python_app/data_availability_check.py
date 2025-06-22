import os
import rust_core
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Set
from collections import defaultdict

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
os.environ["RUST_LOG"] = "info"

def generate_date_list(days: int = 90) -> List[str]:
    """최근 N일간의 날짜 리스트를 생성합니다."""
    today = datetime.today()
    return [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]

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

def check_data_availability() -> Dict:
    """데이터 가용성을 체계적으로 분석합니다."""
    
    date_list = generate_date_list(90)
    time_intervals = generate_time_intervals()
    
    print(f"🔍 데이터 가용성 분석 시작")
    print(f"📅 분석 기간: {len(date_list)}일 ({date_list[-1]} ~ {date_list[0]})")
    print(f"⏰ 분석 시간대: {len(time_intervals)}개 ({time_intervals})")
    print(f"📊 총 시도 횟수: {len(date_list) * len(time_intervals):,}회")
    
    # 결과 저장용 딕셔너리
    results = {
        'total_attempts': 0,
        'successful_selections': 0,
        'data_unavailable_dates': set(),
        'data_unavailable_intervals': defaultdict(list),
        'error_details': [],
        'daily_summary': {},
        'interval_summary': defaultdict(lambda: {'success': 0, 'no_data': 0, 'error': 0}),
        'consecutive_no_data_days': [],
        'weekday_analysis': defaultdict(lambda: {'total': 0, 'success': 0, 'no_data': 0, 'error': 0})
    }
    
    current_no_data_streak = 0
    max_no_data_streak = 0
    streak_start_date = None
    
    for date in date_list:
        print(f"\n📅 {date} 분석 중...")
        
        # 요일 분석
        weekday = datetime.strptime(date, "%Y-%m-%d").strftime("%A")
        results['weekday_analysis'][weekday]['total'] += len(time_intervals)
        
        daily_success = 0
        daily_no_data = 0
        daily_errors = 0
        
        for interval in time_intervals:
            results['total_attempts'] += 1
            
            try:
                selected_stocks = rust_core.evaluate_d_for_date_and_time(date, interval)
                
                if selected_stocks:
                    results['successful_selections'] += 1
                    results['interval_summary'][interval]['success'] += 1
                    daily_success += 1
                    results['weekday_analysis'][weekday]['success'] += 1
                    
                    # 연속 데이터 없음 스트릭 리셋 (업종별 최고 종목 선별 성공)
                    if current_no_data_streak > 0:
                        if current_no_data_streak > max_no_data_streak:
                            max_no_data_streak = current_no_data_streak
                        results['consecutive_no_data_days'].append({
                            'start': streak_start_date,
                            'end': date,
                            'days': current_no_data_streak
                        })
                        current_no_data_streak = 0
                        streak_start_date = None
                    
                else:
                    results['interval_summary'][interval]['no_data'] += 1
                    daily_no_data += 1
                    results['weekday_analysis'][weekday]['no_data'] += 1
                    results['data_unavailable_intervals'][interval].append(date)
                    
            except Exception as e:
                error_msg = f"{date} {interval} 처리 실패: {e}"
                print(f"  ⚠️ {error_msg}")
                
                results['interval_summary'][interval]['error'] += 1
                daily_errors += 1
                results['weekday_analysis'][weekday]['error'] += 1
                results['error_details'].append({
                    'date': date,
                    'interval': interval,
                    'error': str(e)
                })
        
        # 일별 요약 저장
        results['daily_summary'][date] = {
            'success': daily_success,
            'no_data': daily_no_data,
            'error': daily_errors,
            'total': len(time_intervals),
            'success_rate': daily_success / len(time_intervals) * 100 if daily_success > 0 else 0
        }
        
        # 연속 데이터 없음 스트릭 계산
        if daily_success == 0:
            if current_no_data_streak == 0:
                streak_start_date = date
            current_no_data_streak += 1
            results['data_unavailable_dates'].add(date)
        else:
            # 연속 데이터 없음 스트릭 종료
            if current_no_data_streak > 0:
                if current_no_data_streak > max_no_data_streak:
                    max_no_data_streak = current_no_data_streak
                results['consecutive_no_data_days'].append({
                    'start': streak_start_date,
                    'end': date,
                    'days': current_no_data_streak
                })
                current_no_data_streak = 0
                streak_start_date = None
    
    # 마지막 스트릭 처리
    if current_no_data_streak > 0:
        if current_no_data_streak > max_no_data_streak:
            max_no_data_streak = current_no_data_streak
        results['consecutive_no_data_days'].append({
            'start': streak_start_date,
            'end': date_list[0],
            'days': current_no_data_streak
        })
    
    return results

def print_data_availability_results(results: Dict):
    """데이터 가용성 분석 결과를 출력합니다."""
    
    print("\n" + "="*80)
    print("📊 데이터 가용성 분석 결과")
    print("="*80)
    
    # 전체 통계
    print(f"\n📋 전체 통계:")
    print(f"  - 총 시도 횟수: {results['total_attempts']:,}회")
    print(f"  - 성공 선별 횟수: {results['successful_selections']:,}회")
    print(f"  - 선별 성공률: {results['successful_selections']/results['total_attempts']*100:.1f}%")
    print(f"  - 데이터 없는 날짜: {len(results['data_unavailable_dates'])}일")
    print(f"  - 데이터 없는 날짜 비율: {len(results['data_unavailable_dates'])/len(results['daily_summary'])*100:.1f}%")
    
    # 연속 데이터 없음 분석
    if results['consecutive_no_data_days']:
        print(f"\n📅 연속 데이터 없음 기간:")
        sorted_streaks = sorted(results['consecutive_no_data_days'], key=lambda x: x['days'], reverse=True)
        for i, streak in enumerate(sorted_streaks[:5], 1):
            print(f"  {i}. {streak['start']} ~ {streak['end']}: {streak['days']}일 연속")
    
    # 요일별 분석
    print(f"\n📅 요일별 분석:")
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for weekday in weekday_order:
        if weekday in results['weekday_analysis']:
            stats = results['weekday_analysis'][weekday]
            if stats['total'] > 0:
                success_rate = stats['success'] / stats['total'] * 100
                no_data_rate = stats['no_data'] / stats['total'] * 100
                error_rate = stats['error'] / stats['total'] * 100
                print(f"  - {weekday}: 성공 {stats['success']}회 ({success_rate:.1f}%), "
                      f"데이터없음 {stats['no_data']}회 ({no_data_rate:.1f}%), "
                      f"에러 {stats['error']}회 ({error_rate:.1f}%)")
    
    # 시간대별 분석
    print(f"\n⏰ 시간대별 분석:")
    for interval in sorted(results['interval_summary'].keys()):
        stats = results['interval_summary'][interval]
        total = stats['success'] + stats['no_data'] + stats['error']
        if total > 0:
            success_rate = stats['success'] / total * 100
            no_data_rate = stats['no_data'] / total * 100
            error_rate = stats['error'] / total * 100
            print(f"  - {interval}: 성공 {stats['success']}회 ({success_rate:.1f}%), "
                  f"데이터없음 {stats['no_data']}회 ({no_data_rate:.1f}%), "
                  f"에러 {stats['error']}회 ({error_rate:.1f}%)")
    
    # 에러 분석
    if results['error_details']:
        print(f"\n⚠️ 에러 분석:")
        error_types = defaultdict(int)
        for error in results['error_details']:
            error_msg = error['error'].lower()
            if 'database' in error_msg or 'connection' in error_msg:
                error_types['DB 연결 오류'] += 1
            elif 'table' in error_msg:
                error_types['테이블 없음'] += 1
            elif 'data' in error_msg:
                error_types['데이터 없음'] += 1
            elif 'file' in error_msg:
                error_types['파일 오류'] += 1
            else:
                error_types['기타 오류'] += 1
        
        for error_type, count in error_types.items():
            print(f"  - {error_type}: {count}회")
    
    # 데이터 없는 날짜 샘플
    if results['data_unavailable_dates']:
        print(f"\n📅 데이터 없는 날짜 샘플 (최근 10일):")
        sorted_dates = sorted(list(results['data_unavailable_dates']), reverse=True)
        for date in sorted_dates[:10]:
            print(f"  - {date}")

def main():
    """메인 실행 함수"""
    try:
        print("🚀 데이터 가용성 분석 시작")
        
        # 분석 실행
        results = check_data_availability()
        
        # 결과 출력
        print_data_availability_results(results)
        
        print("\n✅ 데이터 가용성 분석 완료")
        
    except Exception as e:
        print(f"❌ 분석 중 오류 발생: {e}")
        raise

if __name__ == "__main__":
    main() 