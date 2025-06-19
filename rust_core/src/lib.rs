mod rules;
mod features;
mod core;

use pyo3::prelude::*;
use crate::rules::d0::evaluate_d0_for_date;

#[pymodule]
fn rust_core(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(evaluate_d0_for_date, m)?)?;
    Ok(())
}
