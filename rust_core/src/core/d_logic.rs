use crate::features::{db, volume, price, stock_info::STOCK_INFO_MANAGER, stock_filter};
use crate::features::logging::init_logger;
use log::{info, debug};
use std::collections::HashSet;

#[derive(Debug, Clone)]
pub struct DStock {
    pub code: String,
    pub name: String,
    pub sector: String,
}

/// 여러 시간대의 D 조건 만족 종목들을 수집하여 중복을 제거한 리스트 반환
pub fn evaluate_d_logic_before(date: &str, to: &str) -> Result<Vec<DStock>, Box<dyn std::error::Error>> {
    init_logger();
    info!("🚀 D 종목 이전 데이터 수집 시작: {} (09:30 ~ {})", date, to);
    
    let conn = db::open("D:/db/stock_price(5min).db")?;
    let tables = db::get_all_tables(&conn)?;
    debug!("📊 전체 종목 수: {}개", tables.len());
    
    // 날짜 형식 변환
    let date_num = date.replace("-", "");
    
    // 시간대 리스트 생성 (to부터 30분씩 이전으로, 09:30까지)
    let time_intervals = generate_time_intervals(to);
    debug!("⏰ 분석할 시간대: {:?}", time_intervals);
    
    let mut all_d_stocks: HashSet<String> = HashSet::new();
    let mut total_processed = 0;
    
    for interval in &time_intervals {
        debug!("📅 {} 시간대 분석 중...", interval);
        
        let from = format!("{}0900", date_num);
        let to_time = format!("{}{}", date_num, interval);
        
        // 1단계: 거래대금 기준 상위 30개 종목 선정
        let top30 = select_top30_by_trade_value(&conn, &tables, &from, &to_time)?;
        
        // 2단계: D 조건 만족 종목 필터링
        let d_codes = filter_d_stocks(&conn, &top30, &from, &to_time)?;
        
        // 3단계: 종목 코드를 HashSet에 추가 (중복 자동 제거)
        let d_codes_count = d_codes.len();
        for code in d_codes {
            all_d_stocks.insert(code);
        }
        
        total_processed += 1;
        debug!("✅ {} 시간대 완료: D 조건 만족 종목 {}개 (누적 {}개)", 
               interval, d_codes_count, all_d_stocks.len());
    }
    
    // 4단계: 종목 정보 매핑 (중복 제거된 종목 코드들)
    let unique_codes: Vec<String> = all_d_stocks.into_iter().collect();
    let ds = map_stock_info(unique_codes)?;
    
    info!("✅ D 종목 이전 데이터 수집 완료: {}개 시간대 분석, {}개 고유 종목", 
          total_processed, ds.len());
    
    if !ds.is_empty() {
        let codes: Vec<String> = ds.iter().map(|s| s.code.clone()).collect();
        debug!("🎯 수집된 D 종목: {}", codes.join(", "));
    }
    
    Ok(ds)
}

/// 시간대 리스트 생성 (to부터 30분씩 이전으로, 09:30까지)
fn generate_time_intervals(to: &str) -> Vec<String> {
    let mut intervals = Vec::new();
    let mut current = to.to_string();
    
    // 09:30까지 반복
    while current >= "0930".to_string() {
        intervals.push(current.clone());
        
        // 30분 이전 시간 계산
        current = subtract_30_minutes(&current);
    }
    
    intervals.reverse(); // 시간순으로 정렬
    intervals
}

/// 시간에서 30분을 빼는 함수
fn subtract_30_minutes(time: &str) -> String {
    if time.len() != 4 {
        return time.to_string();
    }
    
    let hour: i32 = time[0..2].parse().unwrap_or(0);
    let minute: i32 = time[2..4].parse().unwrap_or(0);
    
    let total_minutes = hour * 60 + minute;
    let new_total_minutes = total_minutes - 30;
    
    if new_total_minutes < 0 {
        return "0900".to_string(); // 09:00 이하로는 내려가지 않음
    }
    
    let new_hour = new_total_minutes / 60;
    let new_minute = new_total_minutes % 60;
    
    format!("{:02}{:02}", new_hour, new_minute)
}

pub fn evaluate_d_logic(date: &str, to: &str) -> Result<Vec<DStock>, Box<dyn std::error::Error>> {
    init_logger();
    info!("🚀 D 종목 분석 시작: {} (09:00 ~ {})", date, to);
    
    let conn = db::open("D:/db/stock_price(5min).db")?;
    let tables = db::get_all_tables(&conn)?;
    debug!("📊 전체 종목 수: {}개", tables.len());
    
    // 날짜 형식 변환
    let date_num = date.replace("-", "");
    let from = format!("{}0900", date_num);
    let to_time = format!("{}{}", date_num, to);
    
    debug!("⏰ 분석 시간 범위: {} ~ {} (INT 형식)", from, to_time);
    
    // 1단계: 거래대금 기준 상위 30개 종목 선정
    let top30 = select_top30_by_trade_value(&conn, &tables, &from, &to_time)?;
    debug!("🏆 상위 30개 종목 선정 완료");
    
    // 2단계: D 조건 만족 종목 필터링
    let d_codes = filter_d_stocks(&conn, &top30, &from, &to_time)?;
    info!("✅ D 조건 만족 종목: {}개", d_codes.len());
    
    // 3단계: 종목 정보 매핑
    let ds = map_stock_info(d_codes)?;
    
    if !ds.is_empty() {
        let codes: Vec<String> = ds.iter().map(|s| s.code.clone()).collect();
        debug!("🎯 D 종목: {}", codes.join(", "));
    }
    
    // 4단계: 업종명 필터링 및 상승률 기반 최종 선정
    stock_filter::select_best_stock_by_increase_rate(&conn, ds, &date_num, to)
}

/// 거래대금 기준 상위 30개 종목 선정
fn select_top30_by_trade_value(
    conn: &rusqlite::Connection,
    tables: &[String],
    from: &str,
    to: &str
) -> Result<Vec<String>, Box<dyn std::error::Error>> {
    let mut scored = vec![];
    let mut success_count = 0;
    let mut zero_count = 0;
    let mut error_count = 0;
    
    for table in tables {
        match volume::trade_value_between(conn, table, from, to) {
            Ok(sum) => {
                if sum > 0 {
                    scored.push((table.clone(), sum));
                    success_count += 1;
                } else {
                    zero_count += 1;
                }
            },
            Err(e) => {
                error_count += 1;
                if error_count <= 3 {
                    debug!("❌ {} 거래대금 계산 에러: {}", table, e);
                }
            }
        }
    }
    
    debug!("💰 거래대금 계산 완료: {}개 종목", scored.len());
    debug!("📊 계산 상세: 성공={}, 거래대금0={}, 에러={}", success_count, zero_count, error_count);
    
    scored.sort_by(|a, b| b.1.cmp(&a.1));
    Ok(scored.into_iter().take(30).map(|x| x.0).collect())
}

/// D 조건 만족 종목 필터링
fn filter_d_stocks(
    conn: &rusqlite::Connection,
    codes: &[String],
    from: &str,
    to: &str
) -> Result<Vec<String>, Box<dyn std::error::Error>> {
    let d_codes: Vec<String> = codes
        .iter()
        .filter(|code| {
            let is_d_result = price::is_d(conn, code, from, to);
            match is_d_result {
                Ok(is_d) => is_d,
                Err(e) => {
                    debug!("⚠️ {} D 조건 확인 중 오류: {}", code, e);
                    false
                }
            }
        })
        .cloned()
        .collect();
    
    Ok(d_codes)
}

/// 종목 코드를 종목 정보로 매핑
fn map_stock_info(codes: Vec<String>) -> Result<Vec<DStock>, Box<dyn std::error::Error>> {
    let stock_manager = STOCK_INFO_MANAGER.lock().unwrap();
    let ds: Vec<DStock> = codes
        .into_iter()
        .map(|code| {
            let stock_info = stock_manager.get_stock_info(&code);
            DStock {
                code: stock_info.code,
                name: stock_info.name,
                sector: stock_info.sector,
            }
        })
        .collect();
    
    Ok(ds)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::env;

    #[test]
    fn test_evaluate_d_logic_real_db() {
        env::set_var("RUST_LOG", "info");
        init_logger();
        
        println!("🧪 D 로직 테스트 시작");
        
        let conn = db::open("D:/db/stock_price(5min).db");
        if conn.is_err() {
            assert!(false, "실제 5분봉 DB가 존재하지 않습니다: D:/db/stock_price(5min).db");
        }
        
        println!("✅ DB 연결 성공, evaluate_d_logic 실행");
        let result = evaluate_d_logic("2025-04-30", "0930");
        assert!(result.is_ok(), "evaluate_d_logic 실행 실패: {:?}", result.err());
        
        let ds = result.unwrap();
        println!("📊 테스트 결과: 선정된 종목 {}개", ds.len());
        if !ds.is_empty() {
            println!("🎯 선정된 종목: {:?}", ds);
        }
        
        println!("🧪 D 로직 테스트 완료");
    }
} 