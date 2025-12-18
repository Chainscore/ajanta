#![doc = include_str!("../README.md")]
#![cfg_attr(not(feature = "python"), no_std)]

// NOTE: The `#[inline(always)]` in this crate were put strategically and actually make a difference; do not remove them!

use pyo3::prelude::*;
use pyo3::types::PyModule;
use pyo3::{PyResult, Python};

pub mod amd64;
pub mod types;

#[cfg(feature = "alloc")]
mod assembler;
mod misc;

#[cfg(feature = "alloc")]
extern crate alloc;

#[cfg(feature = "python")]
extern crate std;

#[cfg(feature = "alloc")]
pub use crate::assembler::{Assembler, NonZero, ReservedAssembler, U0, U1, U2, U3, U4, U5, U6};
pub use crate::misc::{Instruction, Label};

#[cfg(feature = "python")]
mod py_asm;
pub use py_asm::PyAssembler;

pub use types::{
    Condition, ImmKind, LoadKind, MemOp, Operands, Reg, RegIndex, RegMem, RegSize, Scale, SegReg,
    Size,
};

#[pymodule]
fn tsrkit_asm(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyAssembler>()?;
    m.add_class::<Reg>();
    m.add_class::<ImmKind>();
    m.add_class::<LoadKind>();
    m.add_class::<RegMem>();
    m.add_class::<RegSize>();
    m.add_class::<Size>();
    m.add_class::<Condition>();
    m.add_class::<RegIndex>();
    m.add_class::<SegReg>();
    m.add_class::<Scale>();
    m.add_class::<MemOp>();
    m.add_class::<Operands>()?;

    Ok(())
}
