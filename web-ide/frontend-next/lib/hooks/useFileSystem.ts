'use client';

import { useState, useEffect } from 'react';
import type { File, FileSystem } from '../types';

const STORAGE_KEY = 'jamcode_ide_fs';
const ACTIVE_FILE_KEY = 'jamcode_ide_active_file';

const DEFAULT_TEMPLATE_PYTHON = `from aj_lang.decorators import service, refine, accumulate, on_transfer

@service
class MyService:
    @refine
    def refine(self, item_index: int, service_id: int, payload: bytes, payload_len: int, wp_hash: bytes) -> bytes:
        # Your refine logic here
        return b"Hello from JAM!"
    
    @accumulate
    def accumulate(self, timeslot: int, service_id: int, num_inputs: int):
        # Your accumulate logic here
        pass
    
    @on_transfer
    def on_transfer(self, sender: int, receiver: int, amount: int, memo: bytes, memo_len: int):
        # Your transfer logic here
        pass
`;

const DEFAULT_TEMPLATE_C = `#include "jam_sdk.c"
#include "jam_state_vars.h"

// Define your state
#define MY_STATE(X) \\
    X(U64, counter)

DEFINE_STATE(MY_STATE)

// Service implementation
jam_refine_result_t my_refine(
    uint32_t item_index,
    uint32_t service_id,
    const uint8_t* payload,
    uint64_t payload_len,
    const uint8_t* work_package_hash
) {
    counter++;
    LOG_UINT("counter", counter);
    return ok_void();
}

void my_accumulate(uint32_t timeslot, uint32_t service_id, uint64_t num_inputs) {
    // Accumulate logic
}

void my_on_transfer(uint32_t sender, uint32_t receiver, uint64_t amount, const uint8_t* memo, uint64_t memo_len) {
    // Transfer logic
}

// Export hooks
EXPORT_REFINE(my_refine)
EXPORT_ACCUMULATE(my_accumulate)
EXPORT_ON_TRANSFER(my_on_transfer)
`;

const DEFAULT_TEMPLATE_CPP = `#include "jam_sdk.c"
#include "jam_state_vars.h"

class ServiceHandler {
public:
    ServiceHandler() = default;
    
    jam_refine_result_t handle_refine(
        uint32_t item_index,
        uint32_t service_id,
        const uint8_t* payload,
        uint64_t payload_len,
        const uint8_t* work_package_hash
   ) {
        LOG_INFO("C++ Service called");
        return ok_void();
    }
};

// State definition
#define MY_STATE(X)
DEFINE_STATE(MY_STATE)

// Service implementation
jam_refine_result_t my_refine(
    uint32_t item_index,
    uint32_t service_id,
    const uint8_t* payload,
    uint64_t payload_len,
    const uint8_t* work_package_hash
) {
    ServiceHandler handler;
    return handler.handle_refine(item_index, service_id, payload, payload_len, work_package_hash);
}

void my_accumulate(uint32_t timeslot, uint32_t service_id, uint64_t num_inputs) {}
void my_on_transfer(uint32_t sender, uint32_t receiver, uint64_t amount, const uint8_t* memo, uint64_t memo_len) {}

EXPORT_REFINE(my_refine)
EXPORT_ACCUMULATE(my_accumulate)
EXPORT_ON_TRANSFER(my_on_transfer)
`;

const DEFAULT_FILES: FileSystem = {};

function getTemplate(language: 'python' | 'c' | 'cpp'): string {
  switch (language) {
    case 'python': return DEFAULT_TEMPLATE_PYTHON;
    case 'c': return DEFAULT_TEMPLATE_C;
    case 'cpp': return DEFAULT_TEMPLATE_CPP;
  }
}

export function useFileSystem() {
  const [files, setFiles] = useState<FileSystem>(() => {
    if (typeof window === 'undefined') return DEFAULT_FILES;
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) : DEFAULT_FILES;
  });

  const [activeFileName, setActiveFileName] = useState<string | null>(null);
  const [openTabs, setOpenTabs] = useState<string[]>([]);
  const [initialized, setInitialized] = useState(false);

  // Initialize active file and tabs after files are loaded
  useEffect(() => {
    if (initialized || typeof window === 'undefined') return;
    
    const savedActive = localStorage.getItem(ACTIVE_FILE_KEY);
    
    // Only restore active file if it exists in saved files
    if (savedActive && files[savedActive]) {
      setActiveFileName(savedActive);
      setOpenTabs([savedActive]);
    }
    // Otherwise start with empty state (welcome screen)
    
    setInitialized(true);
  }, [files, initialized]);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(files));
    }
  }, [files]);

  useEffect(() => {
    if (typeof window !== 'undefined' && activeFileName) {
      localStorage.setItem(ACTIVE_FILE_KEY, activeFileName);
    }
  }, [activeFileName]);

  const saveFile = (name: string, content: string) => {
    setFiles(prev => ({
      ...prev,
      [name]: { ...prev[name], content, lastModified: Date.now() }
    }));
  };

  const createFile = (name: string, language: 'python' | 'c' | 'cpp', content?: string) => {
    if (files[name]) return false;
    
    const newFile: File = { 
      name, 
      language, 
      content: content || getTemplate(language), 
      lastModified: Date.now() 
    };
    
    setFiles(prev => ({ ...prev, [name]: newFile }));
    setActiveFileName(name);
    
    // Add to open tabs if not already there
    if (!openTabs.includes(name)) {
      setOpenTabs(prev => [...prev, name]);
    }
    
    return true;
  };

  const deleteFile = (name: string) => {
    const newFiles = { ...files };
    delete newFiles[name];
    setFiles(newFiles);
    
    // Remove from open tabs
    const newTabs = openTabs.filter(t => t !== name);
    setOpenTabs(newTabs);
    
    // If deleting active file, switch to another
    if (activeFileName === name) {
      const fileNames = Object.keys(newFiles);
      setActiveFileName(newTabs[0] || fileNames[0] || null);
    }
  };

  const openTab = (name: string) => {
    if (!openTabs.includes(name)) {
      setOpenTabs(prev => [...prev, name]);
    }
    setActiveFileName(name);
  };

  const closeTab = (name: string) => {
    const newTabs = openTabs.filter(t => t !== name);
    setOpenTabs(newTabs);
    
    if (activeFileName === name) {
      // Switch to the tab to the left, or the first tab
      const currentIndex = openTabs.indexOf(name);
      const nextTab = newTabs[Math.max(0, currentIndex - 1)];
      setActiveFileName(nextTab || null);
    }
  };

  return {
    files,
    activeFileName,
    setActiveFileName,
    saveFile,
    createFile,
    deleteFile,
    openTab,
    closeTab,
    openTabs,
    activeFile: activeFileName ? files[activeFileName] : null
  };
}
