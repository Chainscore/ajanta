/**
 * @file jam_sdk.c
 * @brief Combined JAM SDK implementation
 * 
 * This file includes all SDK modules for single-file compilation.
 * Include this file in your build to get the full SDK functionality.
 */

// Include the combined header first
#include "jam_sdk.h"

// Include string utilities (no dependencies)
#include "jam_str.c"

// Include the logger implementation (depends on jam_str)
#include "jam_log.c"

// Include the codec implementation
#include "jam_codec.c"

// Include the storage module
#include "jam_storage.c"

// Include the service types implementation
#include "jam_service.c"

// Include the runtime preprocessor
#include "jam_runtime.c"
