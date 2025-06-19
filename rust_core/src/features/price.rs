use rusqlite::Connection;

pub fn is_d0(
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
        Ok(rate >= 5.0 && long_bull)
    } else {
        Ok(false)
    }
}
