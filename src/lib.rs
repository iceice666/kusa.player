// This file will put some method from python package.
////////////////////////////////////////////////
use pyo3::prelude::*;

#[pymodule]
fn pylib(_py: Python<'_>, _pm: &PyModule) -> PyResult<()> {
    Ok(())
}
