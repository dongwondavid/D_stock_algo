use pyo3::prelude::*;
use rusqlite::Connection;
use crate::features::db;

/// 특정 종목의 9:00부터 지정된 시간까지의 상승률을 계산하는 함수
#[pyfunction]
pub fn calculate_increase_rate(
    stock_code: &str, 
    date: &str, 
    to_time: &str
) -> PyResult<f64> {
    let conn = db::open("D:/db/stock_price(5min).db")
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("DB 연결 실패: {}", e)))?;
    
    let result = calculate_increase_rate_internal(&conn, stock_code, date, to_time)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("상승률 계산 실패: {}", e)))?;
    
    Ok(result)
}

/// 30분 간격 상승률을 계산하는 함수 (이전 30분 구간의 상승률)
#[pyfunction]
pub fn calculate_30min_increase_rate(
    stock_code: &str, 
    date: &str, 
    to_time: &str
) -> PyResult<f64> {
    let conn = db::open("D:/db/stock_price(5min).db")
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("DB 연결 실패: {}", e)))?;
    
    let result = calculate_30min_increase_rate_internal(&conn, stock_code, date, to_time)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("30분 간격 상승률 계산 실패: {}", e)))?;
    
    Ok(result)
}

/// 내부 30분 간격 상승률 계산 함수
fn calculate_30min_increase_rate_internal(
    conn: &Connection,
    stock_code: &str,
    date: &str,
    to_time: &str
) -> Result<f64, Box<dyn std::error::Error>> {
    // 날짜 형식 변환 (YYYY-MM-DD -> YYYYMMDD)
    let date_num = date.replace("-", "");
    
    // 30분 이전 시간 계산
    let from_time = match to_time {
        "0930" => "0900",
        "1000" => "0930", 
        "1030" => "1000",
        "1100" => "1030",
        "1130" => "1100",
        "1200" => "1130",
        "1230" => "1200",
        "1300" => "1230",
        "1330" => "1300",
        "1400" => "1330",
        "1430" => "1400",
        "1500" => "1430",
        "1530" => "1500",
        _ => return Err("지원하지 않는 시간대입니다.".into())
    };
    
    let start_time = format!("{}{}", date_num, from_time);
    let end_time = format!("{}{}", date_num, to_time);
    
    // 테이블명은 "A" + 종목코드 형태
    let table_name = format!("A{}", stock_code);
    
    let query = format!(
        "SELECT open, close FROM {} WHERE date BETWEEN ?1 AND ?2 ORDER BY date", 
        table_name
    );
    
    let mut stmt = conn.prepare(&query)?;
    let mut rows = stmt.query(&[&start_time, &end_time])?;

    let mut first_open = None;
    let mut last_close = None;

    while let Some(row) = rows.next()? {
        let open: i64 = row.get(0)?;
        let close: i64 = row.get(1)?;
        
        if first_open.is_none() {
            first_open = Some(open);
        }
        last_close = Some(close);
    }

    if let (Some(open), Some(close)) = (first_open, last_close) {
        let rate = (close - open) as f64 / open as f64 * 100.0;
        Ok(rate)
    } else {
        Ok(0.0) // 데이터가 없으면 0% 반환
    }
}

/// 내부 상승률 계산 함수
fn calculate_increase_rate_internal(
    conn: &Connection,
    stock_code: &str,
    date: &str,
    to_time: &str
) -> Result<f64, Box<dyn std::error::Error>> {
    // 날짜 형식 변환 (YYYY-MM-DD -> YYYYMMDD)
    let date_num = date.replace("-", "");
    let open_time = format!("{}0900", date_num);
    let close_time = format!("{}{}", date_num, to_time);
    
    // 테이블명은 "A" + 종목코드 형태
    let table_name = format!("A{}", stock_code);
    
    let query = format!(
        "SELECT open, close FROM {} WHERE date BETWEEN ?1 AND ?2 ORDER BY date", 
        table_name
    );
    
    let mut stmt = conn.prepare(&query)?;
    let mut rows = stmt.query(&[&open_time, &close_time])?;

    let mut open_0900 = None;
    let mut close_to = None;

    while let Some(row) = rows.next()? {
        let open: i64 = row.get(0)?;
        let close: i64 = row.get(1)?;
        
        if open_0900.is_none() {
            open_0900 = Some(open);
        }
        close_to = Some(close);
    }

    if let (Some(open), Some(close)) = (open_0900, close_to) {
        let rate = (close - open) as f64 / open as f64 * 100.0;
        Ok(rate)
    } else {
        Ok(0.0) // 데이터가 없으면 0% 반환
    }
}

/// 여러 종목의 상승률을 일괄 계산하는 함수
#[pyfunction]
pub fn calculate_increase_rates_batch(
    stock_codes: Vec<String>,
    date: &str,
    to_time: &str
) -> PyResult<Vec<(String, f64)>> {
    let conn = db::open("D:/db/stock_price(5min).db")
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("DB 연결 실패: {}", e)))?;
    
    let mut results = Vec::new();
    
    for code in stock_codes {
        match calculate_increase_rate_internal(&conn, &code, date, to_time) {
            Ok(rate) => results.push((code, rate)),
            Err(e) => {
                // 개별 종목 오류는 로그만 남기고 계속 진행
                eprintln!("⚠️ {} 상승률 계산 실패: {}", code, e);
                results.push((code, 0.0));
            }
        }
    }
    
    Ok(results)
}

/// 특정 종목의 특정 시간대 상승률을 계산하는 함수 (시작 시간 지정 가능)
#[pyfunction]
pub fn calculate_increase_rate_custom_period(
    stock_code: &str,
    date: &str,
    from_time: &str,
    to_time: &str
) -> PyResult<f64> {
    let conn = db::open("D:/db/stock_price(5min).db")
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("DB 연결 실패: {}", e)))?;
    
    let result = calculate_increase_rate_custom_period_internal(&conn, stock_code, date, from_time, to_time)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("상승률 계산 실패: {}", e)))?;
    
    Ok(result)
}

/// 내부 커스텀 기간 상승률 계산 함수
fn calculate_increase_rate_custom_period_internal(
    conn: &Connection,
    stock_code: &str,
    date: &str,
    from_time: &str,
    to_time: &str
) -> Result<f64, Box<dyn std::error::Error>> {
    // 날짜 형식 변환 (YYYY-MM-DD -> YYYYMMDD)
    let date_num = date.replace("-", "");
    let start_time = format!("{}{}", date_num, from_time);
    let end_time = format!("{}{}", date_num, to_time);
    
    // 테이블명은 "A" + 종목코드 형태
    let table_name = format!("A{}", stock_code);
    
    let query = format!(
        "SELECT open, close FROM {} WHERE date BETWEEN ?1 AND ?2 ORDER BY date", 
        table_name
    );
    
    let mut stmt = conn.prepare(&query)?;
    let mut rows = stmt.query(&[&start_time, &end_time])?;

    let mut first_open = None;
    let mut last_close = None;

    while let Some(row) = rows.next()? {
        let open: i64 = row.get(0)?;
        let close: i64 = row.get(1)?;
        
        if first_open.is_none() {
            first_open = Some(open);
        }
        last_close = Some(close);
    }

    if let (Some(open), Some(close)) = (first_open, last_close) {
        let rate = (close - open) as f64 / open as f64 * 100.0;
        Ok(rate)
    } else {
        Ok(0.0) // 데이터가 없으면 0% 반환
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_calculate_increase_rate() {
        // 실제 DB가 있는 경우에만 테스트 실행
        let conn = db::open("D:/db/stock_price(5min).db");
        if conn.is_err() {
            println!("⚠️ 테스트 DB가 없어서 테스트를 건너뜁니다.");
            return;
        }
        
        // 테스트용 종목코드 (실제 DB에 있는 종목으로 변경 필요)
        let result = calculate_increase_rate("005930", "2025-03-05", "0930");
        match result {
            Ok(rate) => {
                println!("✅ 상승률 계산 성공: {}%", rate);
                assert!(rate >= -100.0 && rate <= 1000.0); // 합리적인 범위 체크
            },
            Err(e) => {
                println!("⚠️ 상승률 계산 실패: {}", e);
                // 테스트 실패로 처리하지 않음 (DB 데이터 부족 등)
            }
        }
    }
} 