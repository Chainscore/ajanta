#![cfg(feature = "python")]

use pyo3::prelude::*;
use pyo3::types::PyBytes;

use crate::{amd64, Assembler, Label};

use crate::types::{ImmKind, Size, Reg, RegMem, Operands, MemOp, RegSize, Condition, LoadKind};

#[pyclass]
pub struct PyAssembler {
    inner: Assembler,
}

#[pymethods]
impl PyAssembler {
    #[new]
    fn new() -> Self {
        Self {
            inner: Assembler::new(),
        }
    }

    // labels --------------------------------------------------------------
    fn forward_declare_label(&mut self) -> u32 {
        self.inner.forward_declare_label().raw()
    }

    fn create_label(&mut self) -> u32 {
        self.inner.create_label().raw()
    }

    fn define_label(&mut self, raw: u32) {
        self.inner.define_label(Label::from_raw(raw));
    }

    // origin, length, etc. -----------------------------------------------
    fn origin(&self) -> u64 {
        self.inner.origin()
    }

    fn set_origin(&mut self, o: u64) {
        self.inner.set_origin(o);
    }

    fn len(&self) -> usize {
        self.inner.len()
    }

    fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }

    fn current_address(&self) -> u64 {
        self.inner.current_address()
    }

    // raw bytes -----------------------------------------------------------
    fn push_raw(&mut self, b: &[u8]) {
        self.inner.push_raw(b);
    }

    // final machine code --------------------------------------------------
    fn finalize<'py>(&'py mut self, py: Python<'py>) -> PyResult<&'py PyBytes> {
        let code = self.inner.finalize();
        Ok(PyBytes::new(py, &code))
    }

    fn clear(&mut self) {
        self.inner.clear();
    }

    // Individual instruction methods --------------------------------------

    fn ud2(&mut self) {
        self.inner.push(amd64::inst::ud2());
    }

    fn endbr64(&mut self) {
        self.inner.push(amd64::inst::endbr64());
    }

    fn syscall(&mut self) {
        self.inner.push(amd64::inst::syscall());
    }

    fn push(&mut self, reg: Reg) {
        self.inner.push(amd64::inst::push(reg));
    }

    fn push_imm(&mut self, val: i32) {
        self.inner.push(amd64::inst::push_imm(val));
    }

    fn pop(&mut self, reg: Reg) {
        self.inner.push(amd64::inst::pop(reg));
    }

    fn nop(&mut self) {
        self.inner.push(amd64::inst::nop());
    }

    fn nop2(&mut self) {
        self.inner.push(amd64::inst::nop2());
    }

    fn nop3(&mut self) {
        self.inner.push(amd64::inst::nop3());
    }

    fn nop4(&mut self) {
        self.inner.push(amd64::inst::nop4());
    }

    fn nop5(&mut self) {
        self.inner.push(amd64::inst::nop5());
    }

    fn nop6(&mut self) {
        self.inner.push(amd64::inst::nop6());
    }

    fn nop7(&mut self) {
        self.inner.push(amd64::inst::nop7());
    }

    fn nop8(&mut self) {
        self.inner.push(amd64::inst::nop8());
    }

    fn nop9(&mut self) {
        self.inner.push(amd64::inst::nop9());
    }

    fn nop10(&mut self) {
        self.inner.push(amd64::inst::nop10());
    }

    fn nop11(&mut self) {
        self.inner.push(amd64::inst::nop11());
    }

    // To keep things going - update its positioning later
    fn mov_imm64(&mut self, reg: Reg, val: u64) {
        self.inner.push(amd64::inst::mov_imm64(reg, val));
    }

    fn mov_imm(&mut self, mem: RegMem, imm: ImmKind) {
        self.inner.push(amd64::inst::mov_imm(mem, imm));
    }

    fn mov(&mut self, size: RegSize, a: Reg, b: Reg) {
        self.inner.push(amd64::inst::mov(size, a, b));
    }

    fn ret(&mut self) {
        self.inner.push(amd64::inst::ret());
    }

    fn cmp(&mut self, val: Operands) {
        self.inner.push(amd64::inst::cmp(val));
    }

    fn jcc_label32(&mut self, cond: Condition, label: u32) {
        self.inner.push(amd64::inst::jcc_label32(cond, Label::from_raw(label)));
    }
    
    fn jmp_label32(&mut self, label: u32) {
        self.inner.push(amd64::inst::jmp_label32(Label::from_raw(label)));
    }

    fn add(&mut self, value: Operands) {
        self.inner.push(amd64::inst::add(value));
    }

    fn load(&mut self, kind: LoadKind, reg: Reg, mem: MemOp) {
        self.inner.push(amd64::inst::load(kind, reg, mem));
    }
    
    fn store(&mut self, size: Size, mem: MemOp, reg: Reg) {
        self.inner.push(amd64::inst::store(size, mem, reg));
    }

    fn call(&mut self, regmem: RegMem) {
        self.inner.push(amd64::inst::call(regmem));
    }

    fn movsx_8_to_64(&mut self, reg_size: RegSize, dst: Reg, src: Reg) {
        self.inner.push(amd64::inst::movsx_8_to_64(reg_size, dst, src));
    }

    fn movsx_16_to_64(&mut self, reg_size: RegSize, dst: Reg, src: Reg) {
        self.inner.push(amd64::inst::movsx_16_to_64(reg_size, dst, src));
    }

    fn movzx_16_to_64(&mut self, reg_size: RegSize, dst: Reg, src: Reg) {
        self.inner.push(amd64::inst::movzx_16_to_64(reg_size, dst, src));
    }

    fn movsxd_32_to_64(&mut self, dst: Reg, src: Reg) {
        self.inner.push(amd64::inst::movsxd_32_to_64(dst, src));
    }

    fn cmov(&mut self, cond: Condition, reg_size: RegSize, dst: Reg, src: RegMem) {
        self.inner.push(amd64::inst::cmov(cond, reg_size, dst, src));
    }

    fn xchg_mem(&mut self, reg_size: RegSize, reg: Reg, mem: MemOp) {
        self.inner.push(amd64::inst::xchg_mem(reg_size, reg, mem));
    }

    fn inc(&mut self, size: Size, regmem: RegMem) {
        self.inner.push(amd64::inst::inc(size, regmem));
    }

    fn dec(&mut self, size: Size, regmem: RegMem) {
        self.inner.push(amd64::inst::dec(size, regmem));
    }

    fn sub(&mut self, operands: Operands) {
        self.inner.push(amd64::inst::sub(operands));
    }

    fn or_(&mut self, operands: Operands) {
        self.inner.push(amd64::inst::or(operands));
    }

    fn and_(&mut self, operands: Operands) {
        self.inner.push(amd64::inst::and(operands));
    }

    fn xor_(&mut self, operands: Operands) {
        self.inner.push(amd64::inst::xor(operands));
    }
    
    fn bts(&mut self, reg_size: RegSize, regmem: RegMem, bit: u8) {
        self.inner.push(amd64::inst::bts(reg_size, regmem, bit));
    }

    fn neg(&mut self, size: Size, regmem: RegMem) {
        self.inner.push(amd64::inst::neg(size, regmem));
    }

    fn not_(&mut self, size: Size, regmem: RegMem) {
        self.inner.push(amd64::inst::not(size, regmem));
    }

    fn sar_cl(&mut self, reg_size: RegSize, regmem: RegMem) {
        self.inner.push(amd64::inst::sar_cl(reg_size, regmem));
    }

    fn sar_imm(&mut self, reg_size: RegSize, regmem: RegMem, imm: u8) {
        self.inner.push(amd64::inst::sar_imm(reg_size, regmem, imm));
    }

    fn shl_cl(&mut self, reg_size: RegSize, regmem: RegMem) {
        self.inner.push(amd64::inst::shl_cl(reg_size, regmem));
    }

    fn shl_imm(&mut self, reg_size: RegSize, regmem: RegMem, imm: u8) {
        self.inner.push(amd64::inst::shl_imm(reg_size, regmem, imm));
    }

    fn shr_cl(&mut self, reg_size: RegSize, regmem: RegMem) {
        self.inner.push(amd64::inst::shr_cl(reg_size, regmem));
    }

    fn shr_imm(&mut self, reg_size: RegSize, regmem: RegMem, imm: u8) {
        self.inner.push(amd64::inst::shr_imm(reg_size, regmem, imm));
    }

    fn ror_imm(&mut self, reg_size: RegSize, regmem: RegMem, imm: u8) {
        self.inner.push(amd64::inst::ror_imm(reg_size, regmem, imm));
    }

    fn rol_cl(&mut self, reg_size: RegSize, regmem: RegMem) {
        self.inner.push(amd64::inst::rol_cl(reg_size, regmem));
    }

    fn ror_cl(&mut self, reg_size: RegSize, regmem: RegMem) {
        self.inner.push(amd64::inst::ror_cl(reg_size, regmem));
    }

    fn rcr_imm(&mut self, reg_size: RegSize, regmem: RegMem, imm: u8) {
        self.inner.push(amd64::inst::rcr_imm(reg_size, regmem, imm));
    }

    fn popcnt(&mut self, reg_size: RegSize, dst: Reg, src: RegMem) {
        self.inner.push(amd64::inst::popcnt(reg_size, dst, src));
    }

    fn lzcnt(&mut self, reg_size: RegSize, dst: Reg, src: RegMem) {
        self.inner.push(amd64::inst::lzcnt(reg_size, dst, src));
    }

    fn tzcnt(&mut self, reg_size: RegSize, dst: Reg, src: RegMem) {
        self.inner.push(amd64::inst::tzcnt(reg_size, dst, src));
    }

    fn bswap(&mut self, reg_size: RegSize, reg: Reg) {
        self.inner.push(amd64::inst::bswap(reg_size, reg));
    }

    fn test(&mut self, operands: Operands) {
        self.inner.push(amd64::inst::test(operands));
    }

    fn imul(&mut self, reg_size: RegSize, dst: Reg, src: RegMem) {
        self.inner.push(amd64::inst::imul(reg_size, dst, src));
    }

    fn imul_imm(&mut self, reg_size: RegSize, dst: Reg, src: RegMem, imm: i32) {
        self.inner.push(amd64::inst::imul_imm(reg_size, dst, src, imm));
    }

    fn imul_dx_ax(&mut self, reg_size: RegSize, regmem: RegMem) {
        self.inner.push(amd64::inst::imul_dx_ax(reg_size, regmem));
    }

    fn mul(&mut self, reg_size: RegSize, regmem: RegMem) {
        self.inner.push(amd64::inst::mul(reg_size, regmem));
    }

    fn mul_dx_ax(&mut self, reg_size: RegSize, regmem: RegMem) {
        self.inner.push(amd64::inst::mul_dx_ax(reg_size, regmem));
    }

    fn div(&mut self, reg_size: RegSize, regmem: RegMem) {
        self.inner.push(amd64::inst::div(reg_size, regmem));
    }

    fn idiv(&mut self, reg_size: RegSize, regmem: RegMem) {
        self.inner.push(amd64::inst::idiv(reg_size, regmem));
    }

    fn cdq(&mut self) {
        self.inner.push(amd64::inst::cdq());
    }

    fn cqo(&mut self) {
        self.inner.push(amd64::inst::cqo());
    }

    fn setcc(&mut self, cond: Condition, regmem: RegMem) {
        self.inner.push(amd64::inst::setcc(cond, regmem));
    }

    fn lea(&mut self, reg_size: RegSize, dst: Reg, mem: MemOp) {
        self.inner.push(amd64::inst::lea(reg_size, dst, mem));
    }

    fn mfence(&mut self) {
        self.inner.push(amd64::inst::mfence());
    }

    fn lfence(&mut self) {
        self.inner.push(amd64::inst::lfence());
    }

    fn rdtscp(&mut self) {
        self.inner.push(amd64::inst::rdtscp());
    }

    fn rdpmc(&mut self) {
        self.inner.push(amd64::inst::rdpmc());
    }

    fn cpuid(&mut self) {
        self.inner.push(amd64::inst::cpuid());
    }

    fn call_rel32(&mut self, offset: i32) {
        self.inner.push(amd64::inst::call_rel32(offset));
    }

    fn jmp(&mut self, regmem: RegMem) {
        self.inner.push(amd64::inst::jmp(regmem));
    }

    fn jmp_rel8(&mut self, offset: i8) {
        self.inner.push(amd64::inst::jmp_rel8(offset));
    }

    fn jmp_rel32(&mut self, offset: i32) {
        self.inner.push(amd64::inst::jmp_rel32(offset));
    }

    fn jcc_rel8(&mut self, cond: Condition, offset: i8) {
        self.inner.push(amd64::inst::jcc_rel8(cond, offset));
    }

    fn jcc_rel32(&mut self, cond: Condition, offset: i32) {
        self.inner.push(amd64::inst::jcc_rel32(cond, offset));
    }

    fn jmp_label8(&mut self, label: u32) {
        self.inner.push(amd64::inst::jmp_label8(Label::from_raw(label)));
    }

    fn call_label32(&mut self, label: u32) {
        self.inner.push(amd64::inst::call_label32(Label::from_raw(label)));
    }

    fn jcc_label8(&mut self, cond: Condition, label: u32) {
        self.inner.push(amd64::inst::jcc_label8(cond, Label::from_raw(label)));
    }

    fn jcc_label32_default(&mut self, cond: Condition, label: u32, default_offset: i32) {
        self.inner.push(amd64::inst::jcc_label32_default(cond, Label::from_raw(label), default_offset));
    }

    fn lea_rip_label(&mut self, reg: Reg, label: u32) {
        self.inner.push(amd64::inst::lea_rip_label(reg, Label::from_raw(label)));
    }

    // Cache flush
    #[pyo3(signature = (seg, reg_size, base, offset))]
    fn clflushopt(&mut self, seg: Option<u8>, reg_size: u8, base: Reg, offset: i32) {
        let mem = crate::types::MemOp::BaseOffset {
            seg: seg.map(|s| match s {
                1 => crate::types::SegReg::fs,
                2 => crate::types::SegReg::gs,
                _ => panic!("Invalid segment register"),
            }),
            size: match reg_size {
                32 => crate::types::RegSize::R32,
                64 => crate::types::RegSize::R64,
                _ => panic!("Invalid reg size"),
            },
            base: base,
            offset,
        };
        self.inner.push(amd64::inst::clflushopt(mem));
    }

    // Additional assembler methods
    fn get_label_origin_offset(&self, label: u32) -> Option<isize> {
        self.inner.get_label_origin_offset(Label::from_raw(label))
    }

    fn push_with_label(&mut self, label: u32, _opcode: &str) {
        // This is a placeholder - in practice you'd need to parse the opcode string
        // For now, just define the label
        self.inner.define_label(Label::from_raw(label));
    }

    fn reserve_code(&mut self, length: usize) {
        self.inner.reserve_code(length);
    }

    fn reserve_labels(&mut self, length: usize) {
        self.inner.reserve_labels(length);
    }

    fn spare_capacity(&self) -> usize {
        self.inner.spare_capacity()
    }

    fn resize(&mut self, size: usize, fill_with: u8) {
        self.inner.resize(size, fill_with);
    }

    fn code_mut<'py>(&'py mut self, py: Python<'py>) -> PyResult<&'py PyBytes> {
        let code = self.inner.code_mut();
        Ok(PyBytes::new(py, code))
    }

    
}
