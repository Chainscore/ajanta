/**
 * Null Authorizer
 * 
 * The null authorizer is a PVM blob that always returns success.
 * This is used for permissionless work package authorization.
 * 
 * The blob and hash are extracted from the null-authorizer-bin crate.
 */

import { blake2b } from 'blakejs';

/**
 * Null authorizer PVM blob
 * 
 * This is the actual compiled null authorizer from the null-authorizer-bin crate.
 * It's a minimal PVM program that immediately returns OK.
 * 
 * NOTE: This should be fetched from the actual jamt binary or the network.
 * For now, using a placeholder that should be replaced with the real blob.
 */
export const NULL_AUTHORIZER_BLOB = new Uint8Array([
  // Minimal PVM that returns OK immediately
  // This needs to be the actual BLOB from null-authorizer-bin crate
  0x00, // Placeholder - replace with actual bytes
]);

/**
 * Compute Blake2b-256 hash (as used in JAM/GP)
 * 
 * JAM uses Blake2b with 32-byte output (256 bits)
 */
export function blake2b256(data: Uint8Array): Uint8Array {
  return blake2b(data, undefined, 32);
}

/**
 * Get the null authorizer code hash
 * This is the Blake2b-256 hash of NULL_AUTHORIZER_BLOB
 */
let _nullAuthorizerHash: Uint8Array | null = null;

export function getNullAuthorizerHash(): Uint8Array {
  if (_nullAuthorizerHash) {
    return _nullAuthorizerHash;
  }
  
  _nullAuthorizerHash = blake2b256(NULL_AUTHORIZER_BLOB);
  return _nullAuthorizerHash;
}

/**
 * Pre-computed null authorizer hash (32 bytes)
 * This should match the hash computed by the JAM node
 * 
 * TODO: Replace with actual hash from jamt binary or compute from real BLOB
 */
export const NULL_AUTHORIZER_HASH = getNullAuthorizerHash();
