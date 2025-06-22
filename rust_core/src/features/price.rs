use rusqlite::Connection;
use log::{debug, info};

pub fn is_d(
    conn: &Connection, table: &str, from: &str, to: &str
) -> Result<bool, rusqlite::Error> {
    let query = format!(
        "SELECT open, close, volume FROM {} WHERE date BETWEEN ?1 AND ?2", table
    );
    let mut stmt = conn.prepare(&query)?;
    let mut rows = stmt.query(&[from, to])?;

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
        let long_bull = close > open && (close - open) > (open / 30); // 단순 장대양봉
        
        let result = rate >= 5.0 && long_bull;
        
        // D 조건을 만족하는 경우에만 상세 로그 출력
        if result {
            info!("✅ {} D 조건 만족: 시가={}, 종가={}, 상승률={:.2}%, 장대양봉={}", 
                  table, open, close, rate, long_bull);
        }
        
        Ok(result)
    } else {
        debug!("⚠️ {} 데이터 없음", table);
        Ok(false)
    }
}
