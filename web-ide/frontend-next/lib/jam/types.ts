/**
 * JAM Protocol Types
 * 
 * TypeScript definitions for JAM blockchain types based on jam-types crate.
 */

// Basic types
export type Hash = Uint8Array;       // 32 bytes
export type ServiceId = number;      // u32
export type Slot = number;           // u32  
export type Balance = bigint;        // u64
export type UnsignedGas = bigint;    // u64
export type CoreIndex = number;      // u16

// Opaque hash types (all 32 bytes)
export type HeaderHash = Uint8Array;
export type StateRootHash = Uint8Array;
export type MmrPeakHash = Uint8Array;
export type CodeHash = Uint8Array;
export type WorkPackageHash = Uint8Array;
export type AuthorizerHash = Uint8Array;
export type PayloadHash = Uint8Array;
export type ExtrinsicHash = Uint8Array;

// Bounded types
export type Authorization = Uint8Array;  // BoundedVec<u8, 128>
export type AuthParam = Uint8Array;      // BoundedVec<u8, 128>
export type WorkPayload = Uint8Array;    // BoundedVec<u8, 5MB>
export type Memo = Uint8Array;           // BoundedVec<u8, 128>

/**
 * Refine context - contextual information for refinement
 */
export interface RefineContext {
  anchor: HeaderHash;
  stateRoot: StateRootHash;
  beefyRoot: MmrPeakHash;
  lookupAnchor: HeaderHash;
  lookupAnchorSlot: Slot;
  prerequisites: WorkPackageHash[];
}

/**
 * Import specification for a segment
 */
export interface ImportSpec {
  root: Hash;
  index: number;
  isDirect: boolean;
}

/**
 * Extrinsic specification
 */
export interface ExtrinsicSpec {
  hash: ExtrinsicHash;
  len: number;
}

/**
 * Work item definition
 */
export interface WorkItem {
  service: ServiceId;
  codeHash: CodeHash;
  payload: WorkPayload;
  refineGasLimit: UnsignedGas;
  accumulateGasLimit: UnsignedGas;
  importSegments: ImportSpec[];
  extrinsics: ExtrinsicSpec[];
  exportCount: number;
}

/**
 * Authorizer tuple
 */
export interface Authorizer {
  codeHash: CodeHash;
  param: AuthParam;
}

/**
 * Work package structure
 */
export interface WorkPackage {
  authorization: Authorization;
  authCodeHost: ServiceId;
  authorizer: Authorizer;
  context: RefineContext;
  items: WorkItem[];
}

/**
 * Bootstrap service instruction enum
 * Based on jam-bootstrap-service-common
 */
export enum InstructionType {
  CreateService = 0,
  Upgrade = 1,
  Transfer = 2,
  Zombify = 3,
  Eject = 4,
  DeleteItems = 5,
  Solicit = 6,
  Forget = 7,
  Lookup = 8,
  Import = 9,
  Export = 10,
  Bless = 11,
  Assign = 12,
  Designate = 13,
  Yield = 14,
  Checkpoint = 15,
  Panic = 16,
}

/**
 * CreateService instruction parameters
 */
export interface CreateServiceInstruction {
  type: InstructionType.CreateService;
  codeHash: CodeHash;
  codeLen: bigint;
  minItemGas: UnsignedGas;
  minMemoGas: UnsignedGas;
  endowment: Balance;
  memo: Memo;
}

/**
 * Transfer instruction parameters
 */
export interface TransferInstruction {
  type: InstructionType.Transfer;
  destination: ServiceId;
  amount: Balance;
  gasLimit: UnsignedGas;
  memo: Memo;
}

export type Instruction = CreateServiceInstruction | TransferInstruction;

/**
 * Service info returned from queries
 */
export interface ServiceInfo {
  codeHash: CodeHash;
  balance: Balance;
  threshold: Balance;
  minItemGas: UnsignedGas;
  minMemoGas: UnsignedGas;
  bytes: bigint;
  items: number;
}

/**
 * RPC subscription update
 */
export interface StateUpdate<T> {
  headerHash: HeaderHash;
  slot: Slot;
  value: T | null;
}
