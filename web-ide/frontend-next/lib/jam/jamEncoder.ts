/**
 * JAM Type Encoders
 * 
 * SCALE encoding functions for JAM protocol structures.
 */

import { InstructionType } from './types';
import type {
  WorkPackage,
  WorkItem,
  RefineContext,
  Authorizer,
  ImportSpec,
  ExtrinsicSpec,
  CreateServiceInstruction,
  TransferInstruction,
  Instruction,
} from './types';

import {
  encodeCompact,
  encodeU8,
  encodeU16,
  encodeU32,
  encodeU64,
  encodeVecU8,
  encodeBoundedVec,
  encodeFixedBytes,
  concat,
} from './scaleCodec';

/**
 * Encode RefineContext
 */
export function encodeRefineContext(ctx: RefineContext): Uint8Array {
  return concat(
    encodeFixedBytes(ctx.anchor),         // 32 bytes
    encodeFixedBytes(ctx.stateRoot),      // 32 bytes
    encodeFixedBytes(ctx.beefyRoot),      // 32 bytes
    encodeFixedBytes(ctx.lookupAnchor),   // 32 bytes
    encodeU32(ctx.lookupAnchorSlot),      // 4 bytes
    encodeBoundedVec(ctx.prerequisites, encodeFixedBytes), // VecSet<Hash>
  );
}

/**
 * Encode ImportSpec
 */
export function encodeImportSpec(spec: ImportSpec): Uint8Array {
  // Root is 32 bytes, index encodes whether it's direct or indirect (high bit)
  const indexWithFlag = spec.isDirect ? spec.index : spec.index | (1 << 15);
  return concat(
    encodeFixedBytes(spec.root),
    encodeU16(indexWithFlag),
  );
}

/**
 * Encode ExtrinsicSpec
 */
export function encodeExtrinsicSpec(spec: ExtrinsicSpec): Uint8Array {
  return concat(
    encodeFixedBytes(spec.hash),
    encodeU32(spec.len),
  );
}

/**
 * Encode WorkItem
 * 
 * Order based on Tessera WorkItem (jam/types/work/item.py):
 * 1. service (ServiceId - u32)
 * 2. code_hash (OpaqueHash - 32 bytes)
 * 3. refine_gas_limit (Gas - u64)
 * 4. accumulate_gas_limit (Gas - u64)
 * 5. export_count (Uint[16] - u16)
 * 6. payload (Bytes)
 * 7. import_segments (ImportSpecs)
 * 8. extrinsic (ExtrinsicSpecs)
 */
export function encodeWorkItem(item: WorkItem): Uint8Array {
  console.log(encodeU16(item.exportCount), encodeVecU8(item.payload))
  return concat(
    encodeU32(item.service),
    encodeFixedBytes(item.codeHash),
    encodeU64(item.refineGasLimit),
    encodeU64(item.accumulateGasLimit),
    encodeU16(item.exportCount),
    encodeVecU8(item.payload),
    encodeBoundedVec(item.importSegments, encodeImportSpec),
    encodeBoundedVec(item.extrinsics, encodeExtrinsicSpec),
  );
} 

/**
 * Encode Authorizer
 */
export function encodeAuthorizer(auth: Authorizer): Uint8Array {
  return concat(
    encodeFixedBytes(auth.codeHash),
    encodeVecU8(auth.param),
  );
}

/**
 * Encode WorkPackage
 */
/**
 * Encode WorkPackage
 * 
 * Order based on Tessera implementation (jam/types/work/package.py):
 * 1. auth_code_host (ServiceId)
 * 2. authorizer.code_hash (Hash)
 * 3. context (RefineContext)
 * 4. authorization (Bytes)
 * 5. authorizer.params (Bytes)
 * 6. items (WorkItems)
 */
export function encodeWorkPackage(pkg: WorkPackage): Uint8Array {
  return concat(
    encodeU32(pkg.authCodeHost),
    encodeFixedBytes(pkg.authorizer.codeHash), // 32 bytes
    encodeRefineContext(pkg.context),
    encodeVecU8(pkg.authorization),
    encodeVecU8(pkg.authorizer.param),
    encodeBoundedVec(pkg.items, encodeWorkItem),
  );
}

/**
 * Encode CreateService instruction
 */
export function encodeCreateServiceInstruction(inst: CreateServiceInstruction): Uint8Array {
  return concat(
    encodeU8(InstructionType.CreateService),  // Enum variant index
    encodeFixedBytes(inst.codeHash),          // 32 bytes
    encodeU64(inst.codeLen),                  // u64
    encodeU64(inst.minItemGas),               // u64
    encodeU64(inst.minMemoGas),               // u64
    encodeU64(inst.endowment),                // u64 (Balance)
    encodeVecU8(inst.memo),                   // BoundedVec<u8, 128>
  );
}

/**
 * Encode Transfer instruction
 */
export function encodeTransferInstruction(inst: TransferInstruction): Uint8Array {
  return concat(
    encodeU8(InstructionType.Transfer),      // Enum variant index
    encodeU32(inst.destination),             // ServiceId (u32)
    encodeU64(inst.amount),                  // Balance (u64)
    encodeU64(inst.gasLimit),                // UnsignedGas (u64)
    encodeVecU8(inst.memo),                  // BoundedVec<u8, 128>
  );
}

/**
 * Encode any Instruction
 */
export function encodeInstruction(inst: Instruction): Uint8Array {
  switch (inst.type) {
    case InstructionType.CreateService:
      return encodeCreateServiceInstruction(inst);
    case InstructionType.Transfer:
      return encodeTransferInstruction(inst);
    default:
      throw new Error(`Unknown instruction type: ${(inst as Instruction).type}`);
  }
}

/**
 * Encode multiple instructions (payload for bootstrap service)
 * Instructions are concatenated without a length prefix
 */
export function encodeInstructions(instructions: Instruction[]): Uint8Array {
  const encoded = instructions.map(encodeInstruction);
  return concat(...encoded);
}
