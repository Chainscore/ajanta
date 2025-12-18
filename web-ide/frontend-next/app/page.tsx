'use client';

import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Header } from '@/components/ide/Header';
import { Sidebar } from '@/components/ide/Sidebar';
import { EditorArea } from '@/components/ide/EditorArea';
import { ControlPanel } from '@/components/ide/ControlPanel';
import { Console } from '@/components/ide/Console';
import { NewFileModal } from '@/components/ui/NewFileModal';
import { useFileSystem } from '@/lib/hooks/useFileSystem';
import { useKeyboardShortcuts } from '@/lib/hooks/useKeyboardShortcuts';
import type { Template, CompileResponse, RunResponse, AccumulateResponse, Status, Environment } from '@/lib/types';
import { deployService, invokeService } from '@/lib/jam';

const DEFAULT_API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const DEFAULT_RPC_URL = process.env.NEXT_PUBLIC_RPC_URL || 'ws://localhost:19800';

// Local storage keys
const BACKEND_URL_KEY = 'jamcode_ide_backend_url';
const RPC_URL_KEY = 'jamcode_ide_rpc_url';
const ENVIRONMENT_KEY = 'jamcode_ide_environment';

export default function IDEPage() {
  const coerceLanguage = (value: string): 'python' | 'c' | 'cpp' => {
    if (value.endsWith('.c') || value === 'c') return 'c';
    if (value.endsWith('.cpp') || value.endsWith('.cc') || value.endsWith('.cxx') || value === 'cpp') return 'cpp';
    return 'python';
  };

  // File System
  const {
    files,
    activeFileName,
    setActiveFileName,
    saveFile,
    createFile,
    deleteFile,
    openTab,
    closeTab,
    openTabs,
    activeFile,
  } = useFileSystem();

  // API URL with localStorage persistence
  const [apiUrl, setApiUrl] = useState<string>(() => {
    if (typeof window === 'undefined') return DEFAULT_API_URL;
    return localStorage.getItem(BACKEND_URL_KEY) || DEFAULT_API_URL;
  });

  // Environment state with localStorage persistence
  const [environment, setEnvironment] = useState<Environment>(() => {
    if (typeof window === 'undefined') return 'simulation';
    const saved = localStorage.getItem(ENVIRONMENT_KEY);
    return saved === 'live' ? 'live' : 'simulation';
  });

  // RPC URL with localStorage persistence
  const [rpcUrl, setRpcUrl] = useState<string>(() => {
    if (typeof window === 'undefined') return DEFAULT_RPC_URL;
    return localStorage.getItem(RPC_URL_KEY) || DEFAULT_RPC_URL;
  });

  // IDE State
  const [templates, setTemplates] = useState<Template[]>([]);
  const [logs, setLogs] = useState<string>('');
  const [status, setStatus] = useState<Status>('idle');
  const [pvmHex, setPvmHex] = useState<string | null>(null);
  const [payload, setPayload] = useState<string>('');
  const [deployedServiceId, setDeployedServiceId] = useState<string | null>(null);
  const [showNewFileModal, setShowNewFileModal] = useState(false);

  // Persist settings to localStorage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(BACKEND_URL_KEY, apiUrl);
    }
  }, [apiUrl]);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(ENVIRONMENT_KEY, environment);
    }
  }, [environment]);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(RPC_URL_KEY, rpcUrl);
    }
  }, [rpcUrl]);

  // Reset deployed service when switching environments
  useEffect(() => {
    setDeployedServiceId(null);
  }, [environment]);

  // Fetch templates on mount
  useEffect(() => {
    axios
      .get(`${apiUrl}/templates`)
      .then((res) => setTemplates(res.data))
      .catch((err) => console.error('Failed to fetch templates', err));
  }, [apiUrl]);

  // Handlers
  const handleImportTemplate = async (template: Template) => {
    try {
      const res = await axios.get(`${apiUrl}/templates/${template.path}`);
      const content = res.data.content;

      let name = template.name;
      let counter = 1;
      while (files[name]) {
        const parts = template.name.split('.');
        const ext = parts.pop();
        const base = parts.join('.');
        name = `${base}_${counter}.${ext}`;
        counter++;
      }

      createFile(name, coerceLanguage(template.language), content);
    } catch (err) {
      console.error('Failed to import template', err);
    }
  };

  const handleCreateFile = () => {
    setShowNewFileModal(true);
  };

  const handleNewFileSubmit = (filename: string) => {
    createFile(filename, coerceLanguage(filename));
  };

  const handleCompile = async () => {
    if (!activeFile) return;

    setStatus('compiling');
    setLogs('🔨 Compiling...\n');
    setPvmHex(null);
    setDeployedServiceId(null);

    try {
      const res = await axios.post<CompileResponse>(`${apiUrl}/compile`, {
        source: activeFile.content,
        language: activeFile.language,
      });

      if (res.data.success && res.data.pvm) {
        setStatus('success');
        setPvmHex(res.data.pvm);
        const size = res.data.pvm.length / 2;
        setLogs(
          res.data.logs +
            `\n\n✅ SUCCESS: PVM generated (${size.toLocaleString()} bytes)`
        );
      } else {
        setStatus('error');
        setLogs(res.data.logs || '❌ Unknown compilation error');
      }
    } catch (err) {
      setStatus('error');
      const message = err instanceof Error ? err.message : 'Unknown error';
      setLogs(`❌ Compilation failed: ${message}`);
    }
  };

  const handleRun = async () => {
    if (!pvmHex) {
      setLogs((prev) => prev + '\n\n❌ No PVM to run. Compile first.');
      return;
    }

    setStatus('running');
    setLogs((prev) => prev + '\n\n▶️ Running service (simulation)...\n');

    try {
      const res = await axios.post<RunResponse>(`${apiUrl}/run`, {
        pvm_hex: pvmHex,
        payload: payload,
      });

      if (res.data.success) {
        setStatus('success');
        setLogs(
          (prev) =>
            prev +
            `\n📤 OUTPUT:\n${res.data.logs}\n\n📊 Result: ${res.data.result}`
        );
      } else {
        setStatus('error');
        setLogs((prev) => prev + `\n\n❌ ERROR:\n${res.data.logs}`);
      }
    } catch (err) {
      setStatus('error');
      const message = err instanceof Error ? err.message : 'Unknown error';
      setLogs((prev) => prev + `\n\n❌ Execution failed: ${message}`);
    }
  };

  const handleAccumulate = async () => {
    if (!pvmHex) {
      setLogs((prev) => prev + '\n\n❌ No PVM to accumulate. Compile first.');
      return;
    }

    setStatus('accumulating');
    setLogs((prev) => prev + '\n\n🚀 Simulating Accumulate...\n');

    try {
      const res = await axios.post<AccumulateResponse>(`${apiUrl}/accumulate`, {
        pvm_hex: pvmHex,
      });

      if (res.data.success) {
        setStatus('success');
        setLogs(
          (prev) =>
            prev +
            `\n📤 ACCUMULATE OUTPUT:\n${res.data.logs}\n\n📊 Result:\n${res.data.result}`
        );
      } else {
        setStatus('error');
        setLogs((prev) => prev + `\n\n❌ ERROR:\n${res.data.logs}`);
      }
    } catch (err) {
      setStatus('error');
      const message = err instanceof Error ? err.message : 'Unknown error';
      setLogs((prev) => prev + `\n\n❌ Accumulation failed: ${message}`);
    }
  };

  const handleDeploy = useCallback(async () => {
    if (!pvmHex) {
      setLogs((prev) => prev + '\n\n❌ No PVM to deploy. Compile first.');
      return;
    }

    setStatus('deploying');
    setLogs((prev) => prev + '\n\n🚀 Deploying to live network (direct RPC)...\n');
    setLogs((prev) => prev + `📡 RPC: ${rpcUrl}\n`);

    try {
      // Use direct JAM RPC instead of backend
      const result = await deployService(
        rpcUrl,
        pvmHex,
        10000,
        (msg) => setLogs((prev) => prev + msg)
      );

      if (result.success && result.serviceId) {
        setStatus('success');
        setDeployedServiceId(result.serviceId);
        setLogs(
          (prev) =>
            prev + `\n🆔 Service ID: ${result.serviceId}`
        );
      } else {
        setStatus('error');
        setLogs((prev) => prev + `\n\n❌ DEPLOYMENT FAILED: ${result.error || 'Unknown error'}`);
      }
    } catch (err) {
      setStatus('error');
      const message = err instanceof Error ? err.message : 'Unknown error';
      setLogs((prev) => prev + `\n\n❌ Deployment failed: ${message}`);
    }
  }, [pvmHex, rpcUrl]);

  const handleInvoke = useCallback(async () => {
    if (!deployedServiceId) {
      setLogs((prev) => prev + '\n\n❌ No deployed service. Deploy first.');
      return;
    }

    setStatus('invoking');
    setLogs((prev) => prev + '\n\n⚡ Invoking service on live network (direct RPC)...\n');
    setLogs((prev) => prev + `📡 RPC: ${rpcUrl}\n`);
    setLogs((prev) => prev + `🆔 Service: ${deployedServiceId}\n`);

    try {
      // Use direct JAM RPC instead of backend
      const result = await invokeService(
        rpcUrl,
        deployedServiceId,
        payload,
        (msg) => setLogs((prev) => prev + msg)
      );

      if (result.success) {
        setStatus('success');
        setLogs(
          (prev) =>
            prev + `\n✅ Invocation complete! Package: ${result.packageHash?.substring(0, 16)}...`
        );
      } else {
        setStatus('error');
        setLogs((prev) => prev + `\n\n❌ INVOCATION FAILED: ${result.error || 'Unknown error'}`);
      }
    } catch (err) {
      setStatus('error');
      const message = err instanceof Error ? err.message : 'Unknown error';
      setLogs((prev) => prev + `\n\n❌ Invocation failed: ${message}`);
    }
  }, [deployedServiceId, payload, rpcUrl]);

  // Keyboard shortcuts
  useKeyboardShortcuts({
    onCompile: handleCompile,
    onRun: environment === 'live' && deployedServiceId ? handleInvoke : (environment === 'live' ? handleDeploy : handleRun),
    onNewFile: handleCreateFile,
    onSave: () => {
      // Auto-save is already handled
      setLogs((prev) => prev + '\n💾 Auto-saved');
      setTimeout(() => setLogs((prev) => prev.replace('\n💾 Auto-saved', '')), 1000);
    },
  });

  return (
    <div className="h-screen w-screen flex flex-col overflow-auto" style={{ backgroundColor: '#1e1e1e' }}>
      <Header />

      <div className="flex-1 flex min-h-0 overflow-auto">
        <Sidebar
          files={files}
          activeFileName={activeFileName}
          onSelectFile={(name) => {
            openTab(name);
            setActiveFileName(name);
          }}
          onCreateFile={handleCreateFile}
          onDeleteFile={deleteFile}
          templates={templates}
          onImportTemplate={handleImportTemplate}
        />

        <main className="flex-1 flex flex-col min-w-0 overflow-auto">
          <EditorArea
            activeFile={activeFile}
            openTabs={openTabs}
            onEditorChange={(value) => activeFile && saveFile(activeFile.name, value)}
            onTabChange={setActiveFileName}
            onTabClose={closeTab}
            onCreateFile={handleCreateFile}
            templates={templates}
            onImportTemplate={handleImportTemplate}
          />
        </main>

        <ControlPanel
          onCompile={handleCompile}
          onRun={handleRun}
          onAccumulate={handleAccumulate}
          onDeploy={handleDeploy}
          onInvoke={handleInvoke}
          status={status}
          pvmHex={pvmHex}
          payload={payload}
          onPayloadChange={setPayload}
          environment={environment}
          onEnvironmentChange={setEnvironment}
          rpcUrl={rpcUrl}
          onRpcUrlChange={setRpcUrl}
          deployedServiceId={deployedServiceId}
        />
      </div>

      <Console logs={logs} status={status} />

      {/* New File Modal */}
      <NewFileModal
        isOpen={showNewFileModal}
        onClose={() => setShowNewFileModal(false)}
        onSubmit={handleNewFileSubmit}
      />
    </div>
  );
}
