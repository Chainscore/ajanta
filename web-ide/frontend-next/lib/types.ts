export interface File {
  name: string;
  content: string;
  language: 'python' | 'c' | 'cpp';
  lastModified: number;
}

export interface FileSystem {
  [name: string]: File;
}

export interface Template {
  name: string;
  language: string;
  path: string;
}

export interface CompileResponse {
  success: boolean;
  logs: string;
  pvm?: string;
}

export interface RunResponse {
  success: boolean;
  result: string;
  logs: string;
}

export type Status = 'idle' | 'compiling' | 'running' | 'success' | 'error';
