use pyo3::prelude::*;
use crate::core::d0_logic::evaluate_d0_logic;

#[pyfunction]
pub fn evaluate_d0_for_date_and_time(date: &str, to: &str) -> PyResult<Vec<(String, String, String)>> {
    evaluate_d0_logic(date, to)
        .map(|d0_stocks| {
            d0_stocks.into_iter()
                .map(|stock| (stock.code, stock.name, stock.sector))
                .collect()
        })
        .map_err(|e: Box<dyn std::error::Error + 'static>| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))
}
