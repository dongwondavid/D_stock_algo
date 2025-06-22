use pyo3::prelude::*;
use crate::core::d_logic::evaluate_d_logic;

#[pyfunction]
pub fn evaluate_d_for_date_and_time(date: &str, to: &str) -> PyResult<Vec<(String, String, String)>> {
    evaluate_d_logic(date, to)
        .map(|d_stocks| {
            d_stocks.into_iter()
                .map(|stock| (stock.code, stock.name, stock.sector))
                .collect()
        })
        .map_err(|e: Box<dyn std::error::Error + 'static>| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))
} 