use crate::features::{db, volume, price, stock_info::STOCK_INFO_MANAGER};
use crate::features::logging::init_logger;
use log::{info};

#[derive(Debug, Clone)]
pub struct D0Stock {
    pub code: String,
    pub name: String,
    pub sector: String,
}

pub fn evaluate_d0_logic(date: &str) -> Result<Vec<D0Stock>, Box<dyn std::error::Error>> {
    init_logger();
    info!("🚀 D0 종목 분석 시작: {}", date);
    let conn = db::open("D:/db/stock_price(5min).db")?;
    let tables = db::get_all_tables(&conn)?;
    info!("📊 전체 종목 수: {}개", tables.len());
    // 5분봉 DB는 date가 INT(예: 202003300905)임에 유의
    // 입력 date(YYYY-MM-DD) → 20240101 등으로 변환 필요
    let date_num = date.replace("-", "");
    let from = format!("{}0900", date_num); // 09:00
    let to = format!("{}0930", date_num);   // 09:30
    
    info!("⏰ 분석 시간 범위: {} ~ {} (INT 형식)", from, to);
    
    let mut scored = vec![];
    let mut success_count = 0;
    let mut zero_count = 0;
    let mut error_count = 0;
    
    for t in &tables {
        // 5분봉 DB는 date가 INT이므로 쿼리도 INT로
        match volume::trade_value_between(&conn, t, &from, &to) {
            Ok(sum) => {
                if sum > 0 {
                    scored.push((t.clone(), sum));
                    success_count += 1;
                } else {
                    zero_count += 1;
                }
            },
            Err(e) => {
                error_count += 1;
                if error_count <= 3 { // 처음 3개 에러만 로그
                    info!("❌ {} 거래대금 계산 에러: {}", t, e);
                }
            }
        }
    }
    
    info!("💰 거래대금 계산 완료: {}개 종목", scored.len());
    info!("📊 계산 상세: 성공={}, 거래대금0={}, 에러={}", success_count, zero_count, error_count);
    scored.sort_by(|a, b| b.1.cmp(&a.1));
    let top30 = scored.into_iter().take(30).map(|x| x.0).collect::<Vec<_>>();
    info!("🏆 상위 30개 종목 선정 완료");
    let d0_codes: Vec<String> = top30
        .into_iter()
        .filter(|code| price::is_d0(&conn, code, &from, &to).unwrap_or(false))
        .collect();
    info!("✅ D0 조건 만족 종목: {}개", d0_codes.len());
    
    // 종목 정보 매니저에서 종목명과 업종 정보 가져오기
    let stock_manager = STOCK_INFO_MANAGER.lock().unwrap();
    let d0s: Vec<D0Stock> = d0_codes
        .into_iter()
        .map(|code| {
            let stock_info = stock_manager.get_stock_info(&code);
            D0Stock {
                code: stock_info.code,
                name: stock_info.name,
                sector: stock_info.sector,
            }
        })
        .collect();
    
    if !d0s.is_empty() {
        let codes: Vec<String> = d0s.iter().map(|s| s.code.clone()).collect();
        info!("🎯 D0 종목: {}", codes.join(", "));
    }
    Ok(d0s)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::env;

    #[test]
    fn test_evaluate_d0_logic_real_db() {
        // 테스트에서만 로그 초기화
        env::set_var("RUST_LOG", "info");
        init_logger();
        
        println!("🧪 D0 로직 테스트 시작");
        
        // 실제 DB가 없으면 테스트를 실패로 처리
        let conn = db::open("D:/db/stock_price(5min).db");
        if conn.is_err() {
            assert!(false, "실제 5분봉 DB가 존재하지 않습니다: D:/db/stock_price(5min).db");
        }
        
        println!("✅ DB 연결 성공, evaluate_d0_logic 실행");
        let result = evaluate_d0_logic("2025-04-30");
        assert!(result.is_ok(), "evaluate_d0_logic 실행 실패: {:?}", result.err());
        
        let d0s = result.unwrap();
        println!("📊 테스트 결과: D0 종목 {}개", d0s.len());
        if !d0s.is_empty() {
            println!("🎯 D0 종목: {:?}", d0s);
        }
        
        println!("🧪 D0 로직 테스트 완료");
    }
} 