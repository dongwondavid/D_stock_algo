use rusqlite::Connection;
use log::{info, debug};
use std::collections::HashMap;
use crate::core::d_logic::{DStock, evaluate_d_logic_before};

/// 업종별로 그룹화하여 3개 이상인 업종명을 찾는 함수
pub fn find_sectors_with_3_or_more(ds: &[DStock]) -> Vec<String> {
    let mut sector_count: HashMap<String, usize> = HashMap::new();
    
    for stock in ds {
        *sector_count.entry(stock.sector.clone()).or_insert(0) += 1;
    }
    
    sector_count
        .into_iter()
        .filter(|(_, count)| *count >= 3)
        .map(|(sector, _)| sector)
        .collect()
}

/// 9:00~to 구간의 상승률을 계산하는 함수 (D 조건과 일관성 유지)
pub fn calculate_d_period_increase_rate(
    conn: &Connection, 
    code: &str, 
    date_num: &str,
    to: &str
) -> Result<f64, rusqlite::Error> {
    let open_time = format!("{}0900", date_num);
    let close_time = format!("{}{}", date_num, to);
    
    // 테이블명은 "A" + 종목코드 형태
    let table_name = format!("A{}", code);
    
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

/// 업종명 필터링과 상승률 기반 최종 선정을 수행하는 함수
pub fn select_best_stock_by_increase_rate(
    conn: &Connection,
    ds: Vec<DStock>,
    date_num: &str,
    to: &str
) -> Result<Vec<DStock>, Box<dyn std::error::Error>> {

    // 0단계: 이전 시간대의 D알고리즘으로 선별된 업종명 모으기
    let ds_before = evaluate_d_logic_before(&format!("{}-{}-{}", 
        &date_num[0..4], &date_num[4..6], &date_num[6..8]), to)?;
    
    debug!("📊 이전 시간대 수집된 종목: {}개", ds_before.len());

    // 1단계: 업종명이 3개 이상인 업종명을 찾기 (이전 데이터 포함)
    let sectors_with_3_or_more = find_sectors_with_3_or_more(&ds_before);
    debug!("📋 3개 이상 업종명: {:?}", sectors_with_3_or_more);
    
    if sectors_with_3_or_more.is_empty() {
        info!("⚠️ 3개 이상인 업종명이 없습니다.");
        return Ok(vec![]);
    }
    
    // 2단계: 해당 업종명을 가진 종목들만 추려내기
    let ds_selected: Vec<DStock> = ds
        .into_iter()
        .filter(|stock| sectors_with_3_or_more.contains(&stock.sector))
        .collect();
    
    debug!("🎯 3개 이상 업종명 필터링 결과: {}개 종목", ds_selected.len());
    
    if ds_selected.is_empty() {
        info!("⚠️ 필터링 후 종목이 없습니다.");
        return Ok(vec![]);
    }
    
    // 3단계: 각 업종별로 상승률이 가장 높은 종목 찾기
    let mut sector_best_stocks: HashMap<String, (DStock, f64)> = HashMap::new();
    
    for stock in &ds_selected {
        match calculate_d_period_increase_rate(conn, &stock.code, date_num, to) {
            Ok(rate) => {
                debug!("📈 {} ({}): 9:00~{} 상승률 {:.2}%", stock.name, stock.code, to, rate);
                
                let entry = sector_best_stocks.entry(stock.sector.clone()).or_insert_with(|| {
                    (stock.clone(), f64::NEG_INFINITY)
                });
                
                if rate > entry.1 {
                    *entry = (stock.clone(), rate);
                }
            },
            Err(e) => {
                info!("⚠️ {} 상승률 계산 오류: {}", stock.code, e);
            }
        }
    }
    
    // 4단계: 각 업종의 최고 종목들을 상승률이 높은 순서대로 정렬된 결과 벡터로 변환
    let mut result: Vec<DStock> = Vec::new();
    
    // HashMap을 벡터로 변환하고 상승률 기준으로 정렬
    let mut sorted_stocks: Vec<(String, DStock, f64)> = sector_best_stocks
        .into_iter()
        .map(|(sector, (stock, rate))| (sector, stock, rate))
        .collect();
    
    // 상승률 기준으로 내림차순 정렬
    sorted_stocks.sort_by(|a, b| b.2.partial_cmp(&a.2).unwrap_or(std::cmp::Ordering::Equal));
    
    for (sector, stock, rate) in sorted_stocks {
        info!("🏆 {} 업종 최고 종목: {} ({}), 상승률: {:.2}%", 
              sector, stock.name, stock.code, rate);
        result.push(stock);
    }
    
    info!("✅ 최종 선정 종목: {}개 업종에서 {}개 종목 선정 (상승률 순)", 
          sectors_with_3_or_more.len(), result.len());
    
    
    Ok(result)
}