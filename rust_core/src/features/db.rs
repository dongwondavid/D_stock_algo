use rusqlite::{Connection, Result};

pub fn open(path: &str) -> Result<Connection> {
    Connection::open(path)
}

pub fn get_all_tables(conn: &Connection) -> Result<Vec<String>> {
    let mut stmt = conn.prepare("SELECT name FROM sqlite_master WHERE type='table'")?;
    let tables: Vec<String> = stmt.query_map((), |row| row.get(0))?
        .filter_map(Result::ok)
        .collect();
    Ok(tables)
}
