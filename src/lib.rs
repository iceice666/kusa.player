pub mod player;
mod test;
pub mod track;
mod util;

////////////////////////////////////////////////
// This part is used for porting python script
use pyo3::prelude::*;

#[pymodule]
fn pylib(_py: Python<'_>, _pm: &PyModule) -> PyResult<()> {
    Ok(())
}

////////////////////////////////////////////////
