/**
 * JAM Deploy Module
 * 
 * High-level functions for deploying and invoking services on JAM.
 * Based on jamt create-service and item commands.
 * 
 * Updated to work with Tessera RPC implementation using proper Blake2b-256 hashing.
 */

import { createJamClient } from './jamClient';
import { encodeWorkPackage, encodeInstructions } from './jamEncoder';
import { getNullAuthorizerHash, blake2b256 } from './nullAuthorizer';
import { hexToBytes, bytesToHex } from './scaleCodec';
import { InstructionType } from './types';
import type {
  WorkPackage,
  WorkItem,
  RefineContext,
  CreateServiceInstruction,
  CoreIndex,
} from './types';

/**
 * Default gas limits (hardcoded since Tessera doesn't have parameters RPC)
 * These match the values from jam-std-common
 */
const MAX_REFINE_GAS = BigInt('20000000');   // 20 million
const MAX_ACCUMULATE_GAS = BigInt('1000000'); // 1 million

/**
 * Bootstrap service ID (typically 0)
 */
const BOOTSTRAP_SERVICE_ID = 0;

/**
 * Result of a service deployment
 */
export interface DeployResult {
  success: boolean;
  serviceId?: string;
  slot?: number;
  error?: string;
}

/**
 * Result of a service invocation
 */
export interface InvokeResult {
  success: boolean;
  packageHash?: string;
  slot?: number;
  error?: string;
}

/**
 * Parse service account data from the raw bytes returned by serviceData RPC
 * Based on AccountMetadata structure from jam-types (Service struct)
 * 
 * From jam-std-common/src/simple.rs Service struct:
 * - code_hash: CodeHash (32 bytes)
 * - balance: Balance (8 bytes)
 * - min_item_gas: UnsignedGas (8 bytes)  
 * - min_memo_gas: UnsignedGas (8 bytes)
 * ...etc
 */
function parseServiceData(data: Uint8Array): { codeHash: Uint8Array } | null {
  if (data.length < 32) {
    return null;
  }
  // First 32 bytes are the code hash
  const codeHash = data.slice(0, 32);
  return { codeHash };
}

/**
 * Deploy a service to JAM
 * 
 * This replicates the jamt create-service command:
 * 1. Connect to the RPC
 * 2. Get chain state (best block, state root, finalized block)
 * 3. Query bootstrap service code hash
 * 4. Create a WorkPackage with CreateService instruction
 * 5. Submit the work package
 * 
 * Work package: {
 * 'auth_code_host': 0,
 * 'authorization': '',
 * 'authorizer': {'code_hash': 'aa7eaf029f48cbd4c551d1f8e5e2e4287b7bb557ce86775971707565d4629216', 'params': ''},
 * 'context': {'anchor': '38ba1537012db48345cc3d4e13b5b7e74afe852c5441fe1578207fb474678f01', 'state_root': '80d118284fc3e8891dd252dc7f9415c3ddac8269a3371860e70cb0d4451d25cd', 'beefy_root': '675f9e53123c83ddcdb2c1f5231f13646378aefc83837a4571d052ac80014837', 'lookup_anchor': '38ba1537012db48345cc3d4e13b5b7e74afe852c5441fe1578207fb474678f01', 'lookup_anchor_slot': 4970180, 'prerequisites': []},
 * 'items': [{'service': 0, 'code_hash': 'ddabff6937d84d5a8e659722e66cf60bbfcd47a61b82e021355568cc531a1192', 'refine_gas_limit': 1000000000, 'accumulate_gas_limit': 10000000, 'export_count': 0, 'payload': '0675af2040786d850abd54c7ac2e500bb35bb0ee59d5ac58312276f66e9a960e2c3f14000000000000', 
 * 'import_segments': [], 'extrinsic': []}]}
 * 
 * 
 * Work package: {
 * 'auth_code_host': 0, 'authorization': '', 
 * 'authorizer': {'code_hash': 'aa7eaf029f48cbd4c551d1f8e5e2e4287b7bb557ce86775971707565d4629216', 'params': ''}, 
 * 'context': {'anchor': '972ed28b50cc4f232f00546bef300d63accf93ae02aa5f853773961d05182024', 'state_root': 'c31b1830928482bce88e0258b920b72755403cc1bd013e8469fa149712e24317', 'beefy_root': '0000000000000000000000000000000000000000000000000000000000000000', 'lookup_anchor': '972ed28b50cc4f232f00546bef300d63accf93ae02aa5f853773961d05182024', 'lookup_anchor_slot': 4970218, 'prerequisites': []}, 
 * 'items': [{'service': 0, 'code_hash': 'ddabff6937d84d5a8e659722e66cf60bbfcd47a61b82e021355568cc531a1192', 'refine_gas_limit': 20000000, 'accumulate_gas_limit': 1000000, 'export_count': 0, 'payload': '00ddabff6937d84d5a8e659722e66cf60bbfcd47a61b82e021355568cc531a11924b1c00000000000040420f000000000040420f0000000000102700000000000000', 
 * 'import_segments': [], 'extrinsic': []}]}
 */
/**
 * Wait for service creation by monitoring bootstrap service storage
 */
async function waitForServiceCreation(
  client: ReturnType<typeof createJamClient>,
  bootstrapId: number,
  submissionSlot: number,
  onLog: (msg: string) => void
): Promise<{ serviceId: number; headerHash: Uint8Array; slot: number }> {
  onLog('⏳ Waiting for service creation...\n');
  
  return new Promise((resolve, reject) => {
    let subId: string | null = null;
    let timeoutId: NodeJS.Timeout;

    // Timeout after 60 seconds (10 blocks)
    timeoutId = setTimeout(() => {
      if (subId) client.unsubscribe(subId);
      reject(new Error('Timed out waiting for service creation'));
    }, 60000);

    const cleanup = () => {
      clearTimeout(timeoutId);
      if (subId) client.unsubscribe(subId).catch(console.error);
    };

    client.subscribeServiceValue(
      bootstrapId,
      hexToBytes('63726561746564'), // "created" in hex
      true, // Get current value immediately
      (update) => {
        if (update.value && update.value.length === 4) {
          // Decode ServiceId (u32 little endian)
          const view = new DataView(update.value.buffer);
          const serviceId = view.getUint32(0, true);
          
          if (update.slot >= submissionSlot) {
            onLog(`✨ Service ${serviceId} (0x${serviceId.toString(16)}) created at slot ${update.slot}!\n`);
            cleanup();
            resolve({
              serviceId,
              headerHash: update.headerHash,
              slot: update.slot
            });
          }
        }
      }
    ).then(id => {
      subId = id;
    }).catch(err => {
      cleanup();
      reject(err);
    });
  });
}

/**
 * Provision service code by waiting for request and submitting preimage
 */
async function provisionPreimage(
  client: ReturnType<typeof createJamClient>,
  serviceId: number,
  pvmCode: Uint8Array,
  creationHeaderHash: Uint8Array,
  creationSlot: number,
  onLog: (msg: string) => void
): Promise<void> {
  onLog('🔍 Monitoring for code preimage request...\n');

  // Compute code hash for subscription
  const codeHash = blake2b256(pvmCode);
  const codeLen = pvmCode.length;

  return new Promise((resolve, reject) => {
    let subId: string | null = null;
    let provided = false;
    let timeoutId: NodeJS.Timeout;

    // Timeout after 60 seconds
    timeoutId = setTimeout(() => {
      if (subId) client.unsubscribe(subId);
      reject(new Error('Timed out waiting for service code request'));
    }, 60000);

    const cleanup = () => {
      clearTimeout(timeoutId);
      if (subId) client.unsubscribe(subId).catch(console.error);
    };

    client.subscribeServiceRequest(
      serviceId,
      codeHash,
      codeLen,
      true, // Get current status immediately
      async (update) => {
        // value is null if waiting, empty array if requested?
        // jamt checks: Some((0, _)) -> Request active.
        // Tessera returns value as bytes.
        // If value is present (not null), it means request exists?
        
        // Wait, jamt logic: "None => Still waiting", "Some((0, _)) => Submitted".
        // Tessera subscription sends updates.
        // If we get an update, check if it matches request.
        
        if (!provided && update.value !== null) {
          // Request exists!
          provided = true;
          onLog('📥 Code request received. Providing preimage...\n');
          
          try {
            await client.submitPreimage(serviceId, pvmCode, creationHeaderHash);
            onLog('✅ Service code provided successfully!\n');
            cleanup();
            resolve();
          } catch (err) {
            cleanup();
            reject(err);
          }
        }
      }
    ).then(id => {
      subId = id;
    }).catch(err => {
      cleanup();
      reject(err);
    });
  });
}

export async function deployService(
  rpcUrl: string,
  pvmHex: string,
  initialAmount: number = 10000,
  onLog: (msg: string) => void = console.log,
): Promise<DeployResult> {
  const client = createJamClient(rpcUrl, onLog);
  
  try {
    // Connect to the JAM node
    onLog('🔗 Connecting to JAM node...\n');
    await client.connect();
    
    // Get best block info
    const { hash: anchor, slot: anchorSlot } = await client.bestBlock();
    onLog(`📦 Anchor block slot: ${anchorSlot}\n`);

    // Get state root
    const stateRoot = await client.stateRoot(anchor);
    onLog(`📊 State root: ${bytesToHex(stateRoot).substring(0, 16)}...\n`);

    // Get finalized block
    const { hash: finHash, slot: finSlot } = await client.finalizedBlock();
    onLog(`✅ Finalized block slot: ${finSlot}\n`);

    // Decode PVM code
    const pvmCode = hexToBytes(pvmHex);

    // Get bootstrap service data to get its code hash
    const bootData = await client.serviceData(anchor, BOOTSTRAP_SERVICE_ID);
    if (!bootData) {
      throw new Error('Bootstrap service not found (serviceData returned null)');
    }
    
    const bootInfo = parseServiceData(bootData);
    if (!bootInfo) {
      throw new Error('Failed to parse bootstrap service data');
    }
    onLog(`🔧 Bootstrap service code: ${bytesToHex(bootInfo.codeHash).substring(0, 16)}...\n`);

    // Create the CreateService instruction
    const createInst: CreateServiceInstruction = {
      type: InstructionType.CreateService,
      codeHash: bootInfo.codeHash,
      codeLen: BigInt(pvmCode.length),
      minItemGas: BigInt(1_000_000),
      minMemoGas: BigInt(1_000_000),
      endowment: BigInt(initialAmount),
      memo: new Uint8Array(0),
    };

    // Encode the instruction as payload
    const payload = encodeInstructions([createInst]);
    onLog(`📦 Encoded instruction payload: ${payload.length} bytes\n`);

    // Get null authorizer hash
    const nullAuthHash = getNullAuthorizerHash();

    // Create the work item
    const workItem: WorkItem = {
      service: BOOTSTRAP_SERVICE_ID,
      codeHash: bootInfo.codeHash,
      payload: payload,
      // Use user-provided gas limits if they are known to work better
      refineGasLimit: MAX_REFINE_GAS,
      accumulateGasLimit: MAX_ACCUMULATE_GAS,
      importSegments: [],
      extrinsics: [],
      exportCount: 0,
    };

    // Create the refine context
    const context: RefineContext = {
      anchor: anchor,
      stateRoot: stateRoot,
      beefyRoot: new Uint8Array(32), // Placeholder
      lookupAnchor: finHash,
      lookupAnchorSlot: finSlot,
      prerequisites: [],
    };

    // Create the work package
    const workPackage: WorkPackage = {
      authorization: new Uint8Array(0),
      authCodeHost: BOOTSTRAP_SERVICE_ID,
      authorizer: {
        codeHash: nullAuthHash,
        param: new Uint8Array(0),
      },
      context: context,
      items: [workItem],
    };

    // Encode the work package
    const encodedPackage = encodeWorkPackage(workPackage);
    onLog(`📤 Submitting work package (${encodedPackage.length} bytes)...\n`);

    const coreIndex: CoreIndex = 0;
    await client.submitWorkPackage(coreIndex, encodedPackage);
    onLog(`✅ Work package submitted to core ${coreIndex}\n`);

    // Monitor for service creation
    const { serviceId, headerHash: creationHeaderHash, slot: creationSlot } = await waitForServiceCreation(
      client, 
      BOOTSTRAP_SERVICE_ID, 
      anchorSlot, 
      onLog
    );

    // Provide code preimage
    await provisionPreimage(
      client, 
      serviceId, 
      pvmCode, 
      creationHeaderHash, 
      creationSlot, 
      onLog
    );

    client.disconnect();

    return {
      success: true,
      serviceId: serviceId.toString(),
      slot: creationSlot,
    };
  } catch (err) {
    client.disconnect();
    const message = err instanceof Error ? err.message : 'Unknown error';
    onLog(`❌ DEPLOYMENT FAILED: ${message}\n`);
    return {
      success: false,
      error: message,
    };
  }
}

/**
 * Invoke a deployed service
 * 
 * This replicates the jamt item command:
 * 1. Connect to the RPC
 * 2. Get the service's code hash
 * 3. Create a WorkPackage with the payload
 * 4. Submit the work package
 */
export async function invokeService(
  rpcUrl: string,
  serviceId: string,
  payloadHex: string = '',
  onLog: (msg: string) => void = console.log
): Promise<InvokeResult> {
  const client = createJamClient(rpcUrl, onLog);
  
  try {
    // Connect to the JAM node
    onLog('🔗 Connecting to JAM node...\n');
    await client.connect();

    // Get best block info
    const { hash: anchor, slot: anchorSlot } = await client.bestBlock();
    onLog(`📦 Anchor block slot: ${anchorSlot}\n`);

    // Get state root
    const stateRoot = await client.stateRoot(anchor);

    // Get finalized block
    const { hash: finHash, slot: finSlot } = await client.finalizedBlock();

    // Parse service ID
    const serviceIdNum = parseInt(serviceId, 16);
    onLog(`🔍 Looking up service ${serviceId} (${serviceIdNum})...\n`);

    // Get service data
    const serviceData = await client.serviceData(anchor, serviceIdNum);
    if (!serviceData) {
      return {
        success: false,
        error: `Service ${serviceId} not found`,
      };
    }
    
    const serviceInfo = parseServiceData(serviceData);
    if (!serviceInfo) {
      return {
        success: false,
        error: `Failed to parse service ${serviceId} data`,
      };
    }
    onLog(`🔧 Service code: ${bytesToHex(serviceInfo.codeHash).substring(0, 16)}...\n`);

    // Get null authorizer hash
    const nullAuthHash = getNullAuthorizerHash();

    // Decode payload
    const payload = payloadHex ? hexToBytes(payloadHex) : new Uint8Array(0);
    onLog(`📦 Payload: ${payload.length} bytes\n`);

    // Create work item
    const workItem: WorkItem = {
      service: serviceIdNum,
      codeHash: serviceInfo.codeHash,
      payload: payload,
      refineGasLimit: MAX_REFINE_GAS,
      accumulateGasLimit: MAX_ACCUMULATE_GAS,
      importSegments: [],
      extrinsics: [],
      exportCount: 0,
    };

    // Note: beefyRoot is not yet implemented in Tessera, use zeros for now
    const beefyRoot = new Uint8Array(32);

    // Create refine context
    const context: RefineContext = {
      anchor: anchor,
      stateRoot: stateRoot,
      beefyRoot: beefyRoot,
      lookupAnchor: finHash,
      lookupAnchorSlot: finSlot,
      prerequisites: [],
    };

    // Create work package
    const workPackage: WorkPackage = {
      authorization: new Uint8Array(0),
      authCodeHost: BOOTSTRAP_SERVICE_ID,
      authorizer: {
        codeHash: nullAuthHash,
        param: new Uint8Array(0),
      },
      context: context,
      items: [workItem],
    };

    // Encode and submit
    const encodedPackage = encodeWorkPackage(workPackage);
    onLog(`📤 Submitting work package (${encodedPackage.length} bytes)...\n`);

    await client.submitWorkPackage(0, encodedPackage);

    // Compute package hash using Blake2b-256
    const packageHash = blake2b256(encodedPackage);
    const packageHashHex = bytesToHex(packageHash);
    
    onLog(`✅ Work package submitted: ${packageHashHex.substring(0, 16)}...\n`);
    onLog(`📊 Anchor slot: ${anchorSlot}\n`);

    client.disconnect();

    return {
      success: true,
      packageHash: packageHashHex,
      slot: anchorSlot,
    };
  } catch (err) {
    client.disconnect();
    const message = err instanceof Error ? err.message : 'Unknown error';
    onLog(`❌ Error: ${message}\n`);
    return {
      success: false,
      error: message,
    };
  }
}
