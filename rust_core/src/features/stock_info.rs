use std::collections::HashMap;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::Path;
use once_cell::sync::Lazy;
use std::sync::Mutex;

#[derive(Debug, Clone)]
pub struct StockInfo {
    pub code: String,
    pub name: String,
    pub sector: String,
}

pub struct StockInfoManager {
    stock_map: HashMap<String, StockInfo>,
}

impl StockInfoManager {
    pub fn new() -> Self {
        Self {
            stock_map: HashMap::new(),
        }
    }

    pub fn load_from_csv(&mut self, csv_path: &str) -> Result<(), Box<dyn std::error::Error>> {
        let path = Path::new(csv_path);
        if !path.exists() {
            return Err(format!("CSV 파일이 존재하지 않습니다: {}", csv_path).into());
        }

        let file = File::open(path)?;
        let reader = BufReader::new(file);
        let mut line_count = 0;

        for line in reader.lines() {
            let line = line?;
            line_count += 1;

            // 첫 번째 줄은 헤더로 건너뛰기
            if line_count == 1 {
                continue;
            }

            let parts: Vec<&str> = line.split(',').collect();
            if parts.len() >= 3 {
                let code = parts[0].trim().to_string();
                let name = parts[1].trim().to_string();
                let sector = parts[2].trim().to_string();

                let stock_info = StockInfo {
                    code: code.clone(),
                    name,
                    sector,
                };

                self.stock_map.insert(code, stock_info);
            }
        }

        Ok(())
    }

    pub fn get_stock_info(&self, code: &str) -> StockInfo {
        // 종목코드에서 'A' 접두사 제거 (DB 테이블명에서 종목코드 추출)
        let clean_code = code.trim_start_matches('A');
        
        self.stock_map.get(clean_code).cloned().unwrap_or_else(|| {
            StockInfo {
                code: clean_code.to_string(),
                name: "종목명 모름".to_string(),
                sector: "기타".to_string(),
            }
        })
    }
}

impl Default for StockInfoManager {
    fn default() -> Self {
        Self::new()
    }
}

pub static STOCK_INFO_MANAGER: Lazy<Mutex<StockInfoManager>> = Lazy::new(|| {
    let mut manager = StockInfoManager::new();
    
    // 여러 가능한 경로를 순차적으로 시도
    let possible_paths = [
        "rust_core/data/sector_utf8.csv",
        "data/sector_utf8.csv", 
        "../rust_core/data/sector_utf8.csv",
        "../../rust_core/data/sector_utf8.csv",
    ];
    
    let mut csv_path = None;
    for path_str in &possible_paths {
        if std::path::Path::new(path_str).exists() {
            csv_path = Some(path_str.to_string());
            break;
        }
    }
    
    let csv_path = csv_path.unwrap_or_else(|| {
        panic!("sector_utf8.csv 파일을 찾을 수 없습니다. 다음 경로들을 확인해주세요: {:?}", possible_paths);
    });
    
    manager.load_from_csv(&csv_path).expect("업종 CSV 로드 실패");
    Mutex::new(manager)
}); 