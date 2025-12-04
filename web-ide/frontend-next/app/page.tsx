'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Header } from '@/components/ide/Header';
import { Sidebar } from '@/components/ide/Sidebar';
import { EditorArea } from '@/components/ide/EditorArea';
import { ControlPanel } from '@/components/ide/ControlPanel';
import { Console } from '@/components/ide/Console';
import { useFileSystem } from '@/lib/hooks/useFileSystem';
import { useKeyboardShortcuts } from '@/lib/hooks/useKeyboardShortcuts';
import type { Template, CompileResponse, RunResponse, Status } from '@/lib/types';

const API_URL = 'http://localhost:8000';

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

  // IDE State
  const [templates, setTemplates] = useState<Template[]>([]);
  const [logs, setLogs] = useState<string>('');
  const [status, setStatus] = useState<Status>('idle');
  const [pvmHex, setPvmHex] = useState<string | null>(null);
  const [payload, setPayload] = useState<string>('');

  // Fetch templates on mount
  useEffect(() => {
    axios
      .get(`${API_URL}/templates`)
      .then((res) => setTemplates(res.data))
      .catch((err) => console.error('Failed to fetch templates', err));
  }, []);

  // Handlers
  const handleImportTemplate = async (template: Template) => {
    try {
      const res = await axios.get(`${API_URL}/templates/${template.path}`);
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
    const filename = prompt('Enter filename (e.g., service.py, main.c, app.cpp):');
    if (!filename) return;

    createFile(filename, coerceLanguage(filename));
  };

  const handleCompile = async () => {
    if (!activeFile) return;

    setStatus('compiling');
    setLogs('🔨 Compiling...\n');
    setPvmHex(null);

    try {
      const res = await axios.post<CompileResponse>(`${API_URL}/compile`, {
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
    setLogs((prev) => prev + '\n\n▶️ Running service...\n');

    try {
      const res = await axios.post<RunResponse>(`${API_URL}/run`, {
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

  // Keyboard shortcuts
  useKeyboardShortcuts({
    onCompile: handleCompile,
    onRun: handleRun,
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
          status={status}
          pvmHex={pvmHex}
          payload={payload}
          onPayloadChange={setPayload}
        />
      </div>

      <Console logs={logs} status={status} />
    </div>
  );
}
