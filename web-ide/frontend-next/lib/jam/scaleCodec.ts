/**
 * SCALE Codec Utilities
 * 
 * Minimal SCALE encoding for JAM protocol types.
 * Based on: https://docs.substrate.io/reference/scale-codec/
 */

/**
 * Encode a compact integer (SCALE Compact<u*>)
 */
export function encodeCompact(value: number | bigint): Uint8Array {
  const n = BigInt(value);
  
  const THRESHOLD_64 = BigInt(128);
  const THRESHOLD_16384 = BigInt(16384);
  const THRESHOLD_1073741824 = BigInt(1073741824);
  const ZERO = BigInt(0);
  const MASK_FF = BigInt(0xff);
  const EIGHT = BigInt(8);
  
  if (n < THRESHOLD_64) {
    // Single byte mode
    return new Uint8Array([Number(n)]);
  } else if (n < THRESHOLD_16384) {
    // Two byte mode
    const v = (Number(n) << 2) | 0b01;
    return new Uint8Array([v & 0xff, v >> 8]);
  } else if (n < THRESHOLD_1073741824) {
    // Four byte mode
    const v = (Number(n) << 2) | 0b10;
    return new Uint8Array([v & 0xff, (v >> 8) & 0xff, (v >> 16) & 0xff, v >> 24]);
  } else {
    // Big integer mode
    const bytes: number[] = [];
    let remaining = n;
    while (remaining > ZERO) {
      bytes.push(Number(remaining & MASK_FF));
      remaining >>= EIGHT;
    }
    // Prepend length header
    const header = ((bytes.length - 4) << 2) | 0b11;
    return new Uint8Array([header, ...bytes]);
  }
}

/**
 * Encode a u8
 */
export function encodeU8(value: number): Uint8Array {
  return new Uint8Array([value & 0xff]);
}

/**
 * Encode a u16 (little endian)
 */
export function encodeU16(value: number): Uint8Array {
  return new Uint8Array([value & 0xff, (value >> 8) & 0xff]);
}

/**
 * Encode a u32 (little endian)
 */
export function encodeU32(value: number): Uint8Array {
  const arr = new Uint8Array(4);
  const view = new DataView(arr.buffer);
  view.setUint32(0, value, true);
  return arr;
}

/**
 * Encode a u64 (little endian)
 */
export function encodeU64(value: bigint): Uint8Array {
  const arr = new Uint8Array(8);
  const view = new DataView(arr.buffer);
  view.setBigUint64(0, value, true);
  return arr;
}

/**
 * Encode a Vec<u8> (length-prefixed bytes)
 */
export function encodeVecU8(data: Uint8Array): Uint8Array {
  const lenBytes = encodeCompact(data.length);
  const result = new Uint8Array(lenBytes.length + data.length);
  result.set(lenBytes, 0);
  result.set(data, lenBytes.length);
  return result;
}

/**
 * Encode a BoundedVec<T, N> - same as Vec for encoding purposes
 */
export function encodeBoundedVec<T>(
  items: T[],
  encodeItem: (item: T) => Uint8Array
): Uint8Array {
  const lenBytes = encodeCompact(items.length);
  const encodedItems = items.map(encodeItem);
  const totalLen = lenBytes.length + encodedItems.reduce((acc, arr) => acc + arr.length, 0);
  
  const result = new Uint8Array(totalLen);
  let offset = 0;
  result.set(lenBytes, offset);
  offset += lenBytes.length;
  
  for (const item of encodedItems) {
    result.set(item, offset);
    offset += item.length;
  }
  
  return result;
}

/**
 * Encode a fixed-size byte array (no length prefix)
 */
export function encodeFixedBytes(data: Uint8Array): Uint8Array {
  return data;
}

/**
 * Concatenate multiple Uint8Arrays
 */
export function concat(...arrays: Uint8Array[]): Uint8Array {
  const totalLen = arrays.reduce((acc, arr) => acc + arr.length, 0);
  const result = new Uint8Array(totalLen);
  let offset = 0;
  for (const arr of arrays) {
    result.set(arr, offset);
    offset += arr.length;
  }
  return result;
}

/**
 * Convert hex string to Uint8Array
 */
export function hexToBytes(hex: string): Uint8Array {
  const cleanHex = hex.startsWith('0x') ? hex.slice(2) : hex;
  const bytes = new Uint8Array(cleanHex.length / 2);
  for (let i = 0; i < bytes.length; i++) {
    bytes[i] = parseInt(cleanHex.substr(i * 2, 2), 16);
  }
  return bytes;
}

/**
 * Convert Uint8Array to hex string
 */
export function bytesToHex(bytes: Uint8Array): string {
  return Array.from(bytes)
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
}
