mod rules;
mod features;
mod core;
mod utility;

use pyo3::prelude::*;
use crate::rules::d::evaluate_d_for_date_and_time;
use crate::utility::price_calculator::{calculate_increase_rate, calculate_30min_increase_rate, calculate_increase_rates_batch, calculate_increase_rate_custom_period};

#[pymodule]
fn rust_core(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(evaluate_d_for_date_and_time, m)?)?;
    m.add_function(wrap_pyfunction!(calculate_increase_rate, m)?)?;
    m.add_function(wrap_pyfunction!(calculate_30min_increase_rate, m)?)?;
    m.add_function(wrap_pyfunction!(calculate_increase_rates_batch, m)?)?;
    m.add_function(wrap_pyfunction!(calculate_increase_rate_custom_period, m)?)?;
    Ok(())
}
