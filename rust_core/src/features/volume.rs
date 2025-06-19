use rusqlite::Connection;

pub fn trade_value_between(
    conn: &Connection, table: &str, from: &str, to: &str
) -> Result<i64, rusqlite::Error> {
    let query = format!(
        "SELECT SUM(volume * (open + close) / 2) FROM {} WHERE date BETWEEN ?1 AND ?2", table
    );
    let mut stmt = conn.prepare(&query)?;
    let sum: i64 = stmt.query_row(&[&from, &to], |row| row.get(0))?;
    Ok(sum)
}
