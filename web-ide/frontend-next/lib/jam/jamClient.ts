/**
 * JAM RPC Client
 * 
 * WebSocket JSON-RPC client for interacting with JAM nodes.
 * Based on JIP-2 specification and Tessera implementation.
 * 
 * RPC Methods (from Tessera api_handlers.py):
 * - bestBlock: Get the best (head) block
 * - finalizedBlock: Get the finalized block
 * - parent: Get parent block
 * - stateRoot: Get state root for a block
 * - serviceValue: Get a value from service storage
 * - serviceRequest: Check if a preimage is requested
 * - servicePreimage: Get a preimage from service
 * - submitPreimage: Submit preimage data
 * - submitWorkPackage: Submit a work package
 */

import type { 
  HeaderHash, 
  StateRootHash, 
  ServiceId,
  Slot,
  CoreIndex,
  StateUpdate,
} from './types';
import { bytesToHex, hexToBytes } from './scaleCodec';

/**
 * RPC request ID counter
 */
let rpcIdCounter = 0;

/**
 * Pending RPC requests
 */
interface PendingRequest {
  resolve: (result: unknown) => void;
  reject: (error: Error) => void;
}

/**
 * Subscription callback
 */
type SubscriptionCallback = (update: StateUpdate<Uint8Array | null>) => void;

/**
 * Convert a Uint8Array to a number array (as returned by Tessera RPC)
 */
function bytesToNumberArray(bytes: Uint8Array): number[] {
  return Array.from(bytes);
}

/**
 * Convert a number array (from Tessera RPC) to Uint8Array
 */
function numberArrayToBytes(arr: number[]): Uint8Array {
  return new Uint8Array(arr);
}

/**
 * JAM RPC Client
 * 
 * Uses WebSocket JSON-RPC to communicate with JAM nodes.
 * All data is passed as arrays of numbers (bytes).
 */
export class JamClient {
  private ws: WebSocket | null = null;
  private pendingRequests: Map<number, PendingRequest> = new Map();
  private subscriptions: Map<string, SubscriptionCallback> = new Map();
  private url: string;
  private onLog: (msg: string) => void;

  constructor(url: string, onLog: (msg: string) => void = console.log) {
    this.url = url;
    this.onLog = onLog;
  }

  /**
   * Connect to the JAM node
   */
  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
          this.onLog(`📡 Connected to ${this.url}\n`);
          resolve();
        };

        this.ws.onerror = () => {
          this.onLog(`❌ WebSocket error\n`);
          reject(new Error('WebSocket connection failed'));
        };

        this.ws.onclose = () => {
          this.onLog(`🔌 Disconnected from ${this.url}\n`);
        };

        this.ws.onmessage = (event) => {
          this.handleMessage(event.data);
        };
      } catch (err) {
        reject(err);
      }
    });
  }

  /**
   * Disconnect from the JAM node
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    // Reject all pending requests
    for (const request of this.pendingRequests.values()) {
      request.reject(new Error('Client disconnected'));
    }
    this.pendingRequests.clear();
    this.subscriptions.clear();
  }

  // ... existing methods ...

  /**
   * Subscribe to service preimage requests
   */
  async subscribeServiceRequest(
    serviceId: ServiceId,
    hash: Uint8Array,
    len: number,
    immediate: boolean,
    callback: SubscriptionCallback
  ): Promise<string> {
    const subId = await this.rpc<string>('subscribeServiceRequest', [
      serviceId,
      bytesToNumberArray(hash),
      len,
      immediate,
    ]);
    
    this.subscriptions.set(subId, callback);
    return subId;
  }



  /**
   * Handle incoming WebSocket message
   */
  private handleMessage(data: string): void {
    try {
      const msg = JSON.parse(data);
      
      // Check if it's a subscription notification
      if (msg.method && msg.params) {
        const subId = msg.params.subscription;
        const callback = this.subscriptions.get(subId);
        if (callback) {
          const result = msg.params.result;
          callback({
            headerHash: result.header_hash ? numberArrayToBytes(result.header_hash) : new Uint8Array(32),
            slot: result.slot || 0,
            value: result.value ? numberArrayToBytes(result.value) : null,
          });
        }
        return;
      }

      // Regular RPC response
      if (msg.id !== undefined) {
        const pending = this.pendingRequests.get(msg.id);
        if (pending) {
          this.pendingRequests.delete(msg.id);
          if (msg.error) {
            pending.reject(new Error(msg.error.message || JSON.stringify(msg.error)));
          } else {
            pending.resolve(msg.result);
          }
        }
      }
    } catch (err) {
      console.error('Failed to parse RPC message:', err);
    }
  }

  /**
   * Send RPC request
   * 
   * Based on JIP-2: Arguments are passed as arrays
   */
  private async rpc<T>(method: string, params: unknown[] = []): Promise<T> {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket not connected');
    }

    const id = ++rpcIdCounter;
    
    return new Promise((resolve, reject) => {
      this.pendingRequests.set(id, {
        resolve: (result) => {
          resolve(result as unknown as T);
        },
        reject,
      });

      console.log('Sending RPC request:', {
        jsonrpc: '2.0',
        id,
        method,
        params,
      });

      const request = {
        jsonrpc: '2.0',
        id,
        method,
        params,
      };

      this.ws!.send(JSON.stringify(request));
    });
  }

  /**
   * Helper to parse hex result which might be string, string[] (digits), or number[]
   */
  private parseHexResult(data: string | string[] | number[] | null | undefined): Uint8Array {
    if (!data) return new Uint8Array(0);
    
    if (Array.isArray(data)) {
      if (data.length === 0) return new Uint8Array(0);
      
      // Check if it's number array (raw bytes)
      if (typeof data[0] === 'number') {
        return numberArrayToBytes(data as number[]);
      }
      
      // Check if it's string array (hex digits ["a", "b", ...])
      if (typeof data[0] === 'string') {
        return hexToBytes((data as string[]).join(''));
      }
    }
    
    if (typeof data === 'string') {
      return hexToBytes(data);
    }
    
    throw new Error(`Unknown data format: ${typeof data}`);
  }

  /**
   * Get the best (head) block
   * 
   * Method: bestBlock
   * Returns: { header_hash: number[], slot: number }
   */
  async bestBlock(): Promise<{ hash: HeaderHash; slot: Slot }> {
    const result = await this.rpc<{ header_hash: number[]; slot: number }>('bestBlock', []);
    return {
      hash: numberArrayToBytes(result.header_hash),
      slot: result.slot,
    };
  }

  /**
   * Get the finalized block
   * 
   * Method: finalizedBlock
   * Returns: { header_hash: number[], slot: number }
   */
  async finalizedBlock(): Promise<{ hash: HeaderHash; slot: Slot }> {
    const result = await this.rpc<{ header_hash: number[]; slot: number }>('finalizedBlock', []);
    return {
      hash: numberArrayToBytes(result.header_hash),
      slot: result.slot,
    };
  }

  /**
   * Get state root for a block
   * 
   * Method: stateRoot
   * Args: [header_hash: number[]]
   * Returns: { header_hash: string[] } - array of hex digit characters!
   */
  async stateRoot(blockHash: HeaderHash): Promise<StateRootHash> {
    // Note: Tessera returns { header_hash: ["a", "b", ...] }
    const result = await this.rpc<string[]>('stateRoot', [
      bytesToNumberArray(blockHash)
    ]);
    
    if (!result) {
      throw new Error(`stateRoot returned invalid result: ${JSON.stringify(result)}`);
    }

    return this.parseHexResult(result);
  }

  /**
   * Get service storage value
   * 
   * Method: serviceValue
   * Args: [header_hash: number[], service_id: number, key: number[]]
   * Returns: { result: string[] } (hex encoded digits)
   */
  async serviceValue(
    blockHash: HeaderHash, 
    serviceId: ServiceId, 
    key: Uint8Array
  ): Promise<Uint8Array | null> {
    try {
      const result = await this.rpc<{ result: string[] | string } | null>('serviceValue', [
        bytesToNumberArray(blockHash),
        serviceId,
        bytesToNumberArray(key),
      ]);
      if (!result || !result.result) return null;
      return this.parseHexResult(result.result);
    } catch {
      return null;
    }
  }

  /**
   * Check if a preimage is requested
   * 
   * Method: serviceRequest
   * Args: [header_hash: number[], service_id: number, hash: number[], len: number]
   * Returns: { result: ... }
   */
  async serviceRequest(
    blockHash: HeaderHash,
    serviceId: ServiceId,
    hash: Uint8Array,
    len: number
  ): Promise<unknown> {
    const result = await this.rpc<{ result: unknown }>('serviceRequest', [
      bytesToNumberArray(blockHash),
      serviceId,
      bytesToNumberArray(hash),
      len,
    ]);
    return result.result;
  }

  /**
   * Get a preimage from service
   * 
   * Method: servicePreimage
   * Args: [header_hash: number[], service_id: number, preimage_hash: number[]]
   * Returns: { result: string[] } (hex encoded digits)
   */
  async servicePreimage(
    blockHash: HeaderHash,
    serviceId: ServiceId,
    preimageHash: Uint8Array
  ): Promise<Uint8Array | null> {
    try {
      const result = await this.rpc<{ result: string[] | string } | null>('servicePreimage', [
        bytesToNumberArray(blockHash),
        serviceId,
        bytesToNumberArray(preimageHash),
      ]);
      if (!result || !result.result) return null;
      return this.parseHexResult(result.result);
    } catch {
      return null;
    }
  }

  /**
   * Submit a work package
   * 
   * Method: submitWorkPackage
   * Args: [core_index: number, encoded_package: number[], extrinsics: number[][]]
   */
  async submitWorkPackage(
    coreIndex: CoreIndex,
    encodedPackage: Uint8Array,
    extrinsics: Uint8Array[] = []
  ): Promise<void> {
    await this.rpc('submitWorkPackage', [
      coreIndex,
      bytesToNumberArray(encodedPackage),
      extrinsics.map(bytesToNumberArray),
    ]);
    this.onLog(`📦 Work package submitted to core ${coreIndex}\n`);
  }

  /**
   * Submit preimage data
   * 
   * Method: submitPreimage
   * Args: [service_id: number, data: number[], header_hash: number[]]
   */
  async submitPreimage(
    serviceId: ServiceId,
    data: Uint8Array,
    headerHash: HeaderHash
  ): Promise<void> {
    await this.rpc('submitPreimage', [
      serviceId,
      bytesToNumberArray(data),
      bytesToNumberArray(headerHash),
    ]);
    this.onLog(`📤 Preimage submitted for service ${serviceId}\n`);
  }

  /**
   * Get service data (account metadata)
   * 
   * Method: serviceData
   * Args: [header_hash: number[], service_id: number]
   */
  async serviceData(
    blockHash: HeaderHash,
    serviceId: ServiceId
  ): Promise<Uint8Array | null> {
    try {
      const result = await this.rpc<number[] | null>('serviceData', [
        bytesToNumberArray(blockHash),
        serviceId
      ]);
      if (!result) return null;
      return numberArrayToBytes(result);
    } catch {
      return null;
    }
  }

  /**
   * Get statistics (pi state)
   * 
   * Method: statistics
   * Args: [header_hash: number[]]
   * Returns: { result: string[] } (hex chars)
   */
  async statistics(blockHash: HeaderHash): Promise<Uint8Array | null> {
    try {
      const result = await this.rpc<{ result: string[] | string } | null>('statistics', [
        bytesToNumberArray(blockHash),
      ]);
      if (!result || !result.result) return null;
      return this.parseHexResult(result.result);
    } catch {
      return null;
    }
  }

  /**
   * Subscribe to service storage value changes
   * Note: This may not be implemented in Tessera yet
   */
  async subscribeServiceValue(
    serviceId: ServiceId,
    key: Uint8Array,
    immediate: boolean,
    callback: SubscriptionCallback
  ): Promise<string> {
    const subId = await this.rpc<string>('subscribeServiceValue', [
      serviceId,
      bytesToNumberArray(key),
      immediate,
    ]);
    
    this.subscriptions.set(subId, callback);
    return subId;
  }

  /**
   * Unsubscribe from a subscription
   */
  async unsubscribe(subId: string): Promise<void> {
    await this.rpc('unsubscribe', [subId]);
    this.subscriptions.delete(subId);
  }
}

/**
 * Create a new JAM client
 */
export function createJamClient(
  rpcUrl: string, 
  onLog: (msg: string) => void = console.log
): JamClient {
  return new JamClient(rpcUrl, onLog);
}
