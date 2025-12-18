use pyo3::pyclass;

#[pyclass]
#[derive(Copy, Clone, PartialEq, Eq, Debug)]
pub enum Reg {
    rax = 0,
    rcx = 1,
    rdx = 2,
    rbx = 3,
    rsp = 4,
    rbp = 5,
    rsi = 6,
    rdi = 7,
    r8 = 8,
    r9 = 9,
    r10 = 10,
    r11 = 11,
    r12 = 12,
    r13 = 13,
    r14 = 14,
    r15 = 15,
}

#[pyclass]
#[derive(Copy, Clone, PartialEq, Eq, Debug)]
pub enum ImmKind {
    I8 { value: u8 },
    I16 { value: u16 },
    I32 { value: u32 },
    I64 { value: i32 },
}

#[pyclass]
#[derive(Copy, Clone, PartialEq, Eq, Debug, Default)]
pub enum LoadKind {
    U8,
    U16,
    U32,
    #[default]
    U64,
    I8,
    I16,
    I32,
}

#[pyclass]
#[derive(Copy, Clone, PartialEq, Eq, Debug)]
pub enum RegSize {
    R32,
    R64,
}

#[pyclass]
#[derive(Copy, Clone, PartialEq, Eq, Debug, Default)]
pub enum Size {
    U8,
    U16,
    U32,
    #[default]
    U64,
}

#[pyclass]
#[derive(Copy, Clone, PartialEq, Eq, Debug)]
pub enum Condition {
    Overflow = 0,
    NotOverflow = 1,
    Below = 2,        // For unsigned values.
    AboveOrEqual = 3, // For unsigned values.
    Equal = 4,
    NotEqual = 5,
    BelowOrEqual = 6, // For unsigned values.
    Above = 7,        // For unsigned values.
    Sign = 8,
    NotSign = 9,
    Parity = 10,
    NotParity = 11,
    Less = 12,           // For signed values.
    GreaterOrEqual = 13, // For signed values.
    LessOrEqual = 14,    // For signed values.
    Greater = 15,        // For signed values.
}

#[pyclass]
#[derive(Copy, Clone, PartialEq, Eq, Debug)]
pub enum RegIndex {
    rax = 0,
    rcx = 1,
    rdx = 2,
    rbx = 3,
    // No `rsp`.
    rbp = 5,
    rsi = 6,
    rdi = 7,
    r8 = 8,
    r9 = 9,
    r10 = 10,
    r11 = 11,
    r12 = 12,
    r13 = 13,
    r14 = 14,
    r15 = 15,
}

#[pyclass]
#[derive(Copy, Clone, PartialEq, Eq, Debug)]
pub enum SegReg {
    fs,
    gs,
}

#[pyclass]
#[derive(Copy, Clone, PartialEq, Eq, Debug)]
pub enum Scale {
    x1 = 0,
    x2 = 1,
    x4 = 2,
    x8 = 3,
}

#[pyclass]
#[derive(Copy, Clone, PartialEq, Eq, Debug)]
pub enum MemOp {
    /// segment:base + offset
    BaseOffset {
        seg: Option<SegReg>,
        size: RegSize,
        base: Reg,
        offset: i32,
    },
    /// segment:base + index * scale + offset
    BaseIndexScaleOffset {
        seg: Option<SegReg>,
        size: RegSize,
        base: Reg,
        index: RegIndex,
        scale: Scale,
        offset: i32,
    },
    /// segment:base * scale + offset
    IndexScaleOffset {
        seg: Option<SegReg>,
        size: RegSize,
        index: RegIndex,
        scale: Scale,
        offset: i32,
    },
    /// segment:offset
    Offset {
        seg: Option<SegReg>,
        size: RegSize,
        offset: i32,
    },
    /// segment:rip + offset
    RipRelative { seg: Option<SegReg>, offset: i32 },
}

#[pyclass]
#[derive(Copy, Clone, PartialEq, Eq, Debug)]
pub enum RegMem {
    Reg { reg: Reg },
    Mem { mem: MemOp },
}

#[pyclass]
#[derive(Copy, Clone, PartialEq, Eq, Debug)]
pub enum Operands {
    RegMem_Reg {
        size: Size,
        reg_mem: RegMem,
        reg: Reg,
    },
    Reg_RegMem {
        size: Size,
        reg: Reg,
        reg_mem: RegMem,
    },
    RegMem_Imm {
        reg_mem: RegMem,
        imm: ImmKind,
    },
}
