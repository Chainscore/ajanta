"use client";

import Image from "next/image";
import type { Status, Environment } from "@/lib/types";
import Link from "next/link";

interface ControlPanelProps {
  onCompile: () => void;
  onRun: () => void;
  onAccumulate: () => void;
  onDeploy: () => void;
  onInvoke: () => void;
  status: Status;
  pvmHex: string | null;
  payload: string;
  onPayloadChange: (value: string) => void;
  environment: Environment;
  onEnvironmentChange: (env: Environment) => void;
  rpcUrl: string;
  onRpcUrlChange: (url: string) => void;
  deployedServiceId: string | null;
}

const Icons = {
  build: () => (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
      <path d="M9.972 2.508a.5.5 0 0 0-.16-.556l-.178-.129a5.009 5.009 0 0 0-2.076-.783C6.215.862 4.504 1.229 2.84 3.133H1.786a.5.5 0 0 0-.354.147L.146 4.567a.5.5 0 0 0 0 .706l2.571 2.579a.5.5 0 0 0 .708 0l1.286-1.29a.5.5 0 0 0 .146-.353V5.57l8.387 8.873A.5.5 0 0 0 14 14.5l1.5-1.5a.5.5 0 0 0 .017-.689l-9.129-8.63c.747-.456 1.772-.839 3.112-.839a.5.5 0 0 0 .472-.334z" />
    </svg>
  ),
  play: () => (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
      <path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z" />
    </svg>
  ),
  download: () => (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
      <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z" />
      <path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z" />
    </svg>
  ),
  deploy: () => (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
      <path d="M8.186 1.113a.5.5 0 0 0-.372 0L1.846 3.5l2.404.961L10.404 2l-2.218-.887zm3.564 1.426L5.596 5 8 5.961 14.154 3.5l-2.404-.961zm3.25 1.7-6.5 2.6v7.922l6.5-2.6V4.24zM7.5 14.762V6.838L1 4.239v7.923l6.5 2.6zM7.443.184a1.5 1.5 0 0 1 1.114 0l7.129 2.852A.5.5 0 0 1 16 3.5v8.662a1 1 0 0 1-.629.928l-7.185 2.874a.5.5 0 0 1-.372 0L.63 13.09a1 1 0 0 1-.63-.928V3.5a.5.5 0 0 1 .314-.464L7.443.184z" />
    </svg>
  ),
  rocket: () => (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
      <path d="M10.175.656a.5.5 0 0 1 .168.057l.03.01c1.098.38 2.254 1.04 3.238 1.996.998.97 1.68 2.132 2.082 3.232l.03.05a.501.501 0 0 1-.046.555l-.032.03-.01.01-.34.415c-.547.66-1.1 1.167-1.676 1.566-.44.307-.898.544-1.37.732l.07.08c.158.188.376.458.596.764.24.335.5.728.705 1.134.205.407.43.945.387 1.507-.036.47-.204.924-.46 1.347l-.01.01-.01.018-.22.35c-.24.385-.515.64-.826.832a2.11 2.11 0 0 1-.997.305c-.494.023-1.005-.102-1.513-.3-.508-.197-1.04-.47-1.577-.77l-.04-.02a9.59 9.59 0 0 1-.55.09 9.81 9.81 0 0 1-2.54 0 9.648 9.648 0 0 1-.55-.09l-.04.02c-.537.3-1.07.573-1.577.77-.508.198-1.019.323-1.513.3a2.11 2.11 0 0 1-.997-.305c-.311-.192-.586-.447-.826-.832l-.22-.35-.01-.018-.01-.01c-.256-.423-.424-.877-.46-1.347-.043-.562.182-1.1.387-1.507.205-.406.464-.8.705-1.134.22-.306.438-.576.596-.764l.07-.08c-.472-.188-.93-.425-1.37-.732-.576-.4-1.129-.906-1.676-1.567l-.34-.415-.01-.01-.032-.03a.501.501 0 0 1-.046-.555l.03-.05c.402-1.1 1.084-2.262 2.082-3.232.984-.956 2.14-1.617 3.238-1.996l.03-.01a.5.5 0 0 1 .168-.057l.014-.008.017-.006a.5.5 0 0 1 .172-.025.5.5 0 0 1 .175.03l.015.007.015.007a5.8 5.8 0 0 0 2.063 0l.015-.007.015-.007a.5.5 0 0 1 .175-.03.5.5 0 0 1 .172.025l.017.006.014.008zM8 3a1.498 1.498 0 0 0-1.5 1.5c0 .404.262.89.654 1.244.392.352.902.632 1.512.644h.004c.004 0 .013 0 .03-.002l.01-.001h.068l.01.001c.017.002.026.002.03.002h.004c.61-.012 1.12-.292 1.512-.644.392-.354.654-.84.654-1.244A1.498 1.498 0 0 0 8 3zm0 5.5c-.852 0-1.604.268-2.207.686-.603.42-1.044.987-1.293 1.572a.5.5 0 1 0 .92.392c.183-.43.508-.865.958-1.18C6.828 9.654 7.38 9.5 8 9.5s1.172.155 1.622.47c.45.315.775.75.958 1.18a.5.5 0 1 0 .92-.392c-.249-.585-.69-1.153-1.293-1.572C9.604 8.768 8.852 8.5 8 8.5z" />
    </svg>
  ),
  network: () => (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
      <path d="M6.5 1A1.5 1.5 0 0 0 5 2.5V3H1.5A1.5 1.5 0 0 0 0 4.5v8A1.5 1.5 0 0 0 1.5 14h13a1.5 1.5 0 0 0 1.5-1.5v-8A1.5 1.5 0 0 0 14.5 3H11v-.5A1.5 1.5 0 0 0 9.5 1h-3zm0 1h3a.5.5 0 0 1 .5.5V3H6v-.5a.5.5 0 0 1 .5-.5zm1.886 6.914L15 7.151V12.5a.5.5 0 0 1-.5.5h-13a.5.5 0 0 1-.5-.5V7.15l6.614 1.764a1.5 1.5 0 0 0 .772 0zM1.5 4h13a.5.5 0 0 1 .5.5v1.616l-6.614 1.764a.5.5 0 0 1-.258 0L1 6.116V4.5a.5.5 0 0 1 .5-.5z" />
    </svg>
  ),
};

const LoadingSpinner = ({ color = "#00c8ff" }) => (
  <svg
    width="14"
    height="14"
    viewBox="0 0 16 16"
    fill="none"
    className="animate-spin"
    style={{ color }}
  >
    <circle
      cx="8"
      cy="8"
      r="6"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeDasharray="28.27"
      strokeDashoffset="28.27"
      className="opacity-25"
    />
    <circle
      cx="8"
      cy="8"
      r="6"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeDasharray="28.27"
      strokeDashoffset="14.13"
      className="opacity-75"
    />
  </svg>
);

export function ControlPanel({
  onCompile,
  onRun,
  onDeploy,
  onInvoke,
  onAccumulate,
  status,
  pvmHex,
  payload,
  onPayloadChange,
  environment,
  onEnvironmentChange,
  rpcUrl,
  onRpcUrlChange,
  deployedServiceId,
}: ControlPanelProps) {
  const isLive = environment === "live";
  const isWorking =
    status === "compiling" ||
    status === "running" ||
    status === "deploying" ||
    status === "invoking" ||
    status === "accumulating";

  return (
    <aside
      className="w-56 flex flex-col shrink-0"
      style={{
        backgroundColor: "#252526",
        borderLeft: "1px solid #333",
      }}
    >
      {/* Actions Header */}
      <div className="h-10 px-4 flex items-center">
        <span
          style={{
            fontFamily: "JetBrains Mono, monospace",
            fontSize: "11px",
            color: "#858585",
            textTransform: "uppercase",
            letterSpacing: "0.5px",
          }}
        >
          {"// actions"}
        </span>
      </div>

      {/* 1. BUILD PHASE */}
      <div className="px-3 pb-3">
        <button
          onClick={onCompile}
          disabled={isWorking}
          className="w-[86%] px-3 flex items-center gap-3 rounded-lg transition-all disabled:opacity-40 disabled:cursor-not-allowed"
          style={{
            height: "40px",
            backgroundColor: "rgba(0, 200, 255, 0.1)",
            border: "1px solid rgba(0, 200, 255, 0.2)",
            fontFamily: "JetBrains Mono, monospace",
            fontSize: "13px",
            color: "#00c8ff",
          }}
          onMouseEnter={(e) => {
            if (!e.currentTarget.disabled) {
              e.currentTarget.style.backgroundColor = "rgba(0, 200, 255, 0.15)";
              e.currentTarget.style.borderColor = "rgba(0, 200, 255, 0.4)";
            }
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = "rgba(0, 200, 255, 0.1)";
            e.currentTarget.style.borderColor = "rgba(0, 200, 255, 0.2)";
          }}
        >
          {status === "compiling" ? (
            <LoadingSpinner color="#00c8ff" />
          ) : (
            <Icons.build />
          )}
          <span>build()</span>
          <span
            className="ml-auto px-1.5 py-0.5 rounded"
            style={{
              fontSize: "10px",
              backgroundColor: "#333",
              color: "#888",
            }}
          >
            ⌘B
          </span>
        </button>
      </div>

      {/* Bytecode Status */}
      {pvmHex && (
        <div
          className="mx-3 mb-3 p-3 rounded-lg flex items-center justify-between"
          style={{
            backgroundColor: "#1e1e1e",
            border: "1px solid #3c3c3c",
          }}
        >
          <div>
            <div
              style={{
                fontFamily: "JetBrains Mono, monospace",
                fontSize: "11px",
                color: "#858585",
              }}
            >
              bytecode
            </div>
            <div
              style={{
                fontFamily: "JetBrains Mono, monospace",
                fontSize: "12px",
                color: "#00ff88",
              }}
            >
              {(pvmHex.length / 2).toLocaleString()} bytes
            </div>
          </div>
          <button
            onClick={() => {
              const bytes = new Uint8Array(pvmHex.length / 2);
              for (let i = 0; i < pvmHex.length; i += 2) {
                bytes[i / 2] = parseInt(pvmHex.substr(i, 2), 16);
              }
              const blob = new Blob([bytes], {
                type: "application/octet-stream",
              });
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = "service.jam";
              document.body.appendChild(a);
              a.click();
              document.body.removeChild(a);
              URL.revokeObjectURL(url);
            }}
            className="flex items-center justify-center w-8 h-8 rounded-lg transition-colors"
            style={{ backgroundColor: "#333" }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = "#444";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = "#333";
            }}
          >
            <Icons.download />
          </button>
        </div>
      )}

      {/* 2. ENVIRONMENT CONFIG */}
      <div className="px-3 pb-3">
        <div
          className="mb-2"
          style={{
            fontFamily: "JetBrains Mono, monospace",
            fontSize: "11px",
            color: "#858585",
          }}
        >
          {"// environment"}
        </div>
        <div
          className="flex gap-1 p-1 rounded-lg"
          style={{ backgroundColor: "#1e1e1e" }}
        >
          <button
            onClick={() => onEnvironmentChange("simulation")}
            className="flex-1 py-1.5 rounded-md text-center transition-all"
            style={{
              fontFamily: "JetBrains Mono, monospace",
              fontSize: "10px",
              backgroundColor: !isLive
                ? "rgba(0, 200, 255, 0.15)"
                : "transparent",
              color: !isLive ? "#00c8ff" : "#666",
              border: !isLive
                ? "1px solid rgba(0, 200, 255, 0.3)"
                : "1px solid transparent",
            }}
          >
            simulate
          </button>
          <button
            onClick={() => onEnvironmentChange("live")}
            className="flex-1 py-1.5 rounded-md text-center transition-all"
            style={{
              fontFamily: "JetBrains Mono, monospace",
              fontSize: "10px",
              backgroundColor: isLive
                ? "rgba(255, 136, 0, 0.15)"
                : "transparent",
              color: isLive ? "#ff8800" : "#666",
              border: isLive
                ? "1px solid rgba(255, 136, 0, 0.3)"
                : "1px solid transparent",
            }}
          >
            live
          </button>
        </div>
      </div>

      {isLive && (
        <div className="px-3 pb-3">
          <div
            className="mb-2"
            style={{
              fontFamily: "JetBrains Mono, monospace",
              fontSize: "11px",
              color: "#858585",
            }}
          >
            {"// rpc url"}
          </div>
          <select
            value={rpcUrl}
            onChange={(e) => onRpcUrlChange(e.target.value)}
            className="w-full px-2 py-1.5 rounded-lg focus:outline-none appearance-none"
            style={{
              backgroundColor: "#1e1e1e",
              border: "1px solid #3c3c3c",
              fontFamily: "JetBrains Mono, monospace",
              fontSize: "10px",
              color: "#ccc",
              backgroundImage: `url("data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3E%3Cpath stroke='%23858585' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3E%3C/svg%3E")`,
              backgroundPosition: "right 0.2rem center",
              backgroundRepeat: "no-repeat",
              backgroundSize: "1.2em 1.2em",
              paddingRight: "1.5rem",
            }}
          >
            <option value="ws://localhost:19800">Localnet - localhost</option>
            <option value="ws://tessera-nodes-4166.eastus.azurecontainer.io:19800">
              JAM-Mumbai-0.7.0
            </option>
          </select>
        </div>
      )}

      {/* 3. SIMULATION FLOW */}
      {!isLive && (
        <>
          <div className="px-3 pt-4">
            <div
              className="mb-2"
              style={{
                fontFamily: "JetBrains Mono, monospace",
                fontSize: "11px",
                color: "#858585",
              }}
            >
              {"// payload"}
            </div>
            <textarea
              value={payload}
              onChange={(e) => onPayloadChange(e.target.value)}
              className="w-full h-20 px-3 py-2 rounded-lg resize-none focus:outline-none"
              style={{
                backgroundColor: "#1e1e1e",
                border: "1px solid #3c3c3c",
                fontFamily: "JetBrains Mono, monospace",
                fontSize: "12px",
                color: "#ccc",
              }}
              placeholder="input data..."
              onFocus={(e) => {
                e.currentTarget.style.borderColor = "#00ff88";
                e.currentTarget.style.boxShadow =
                  "0 0 0 1px rgba(0, 255, 136, 0.1)";
              }}
              onBlur={(e) => {
                e.currentTarget.style.borderColor = "#1a1a1a";
                e.currentTarget.style.boxShadow = "none";
              }}
            />
          </div>

          <div className="px-3 pt-3">
            <button
              onClick={onRun}
              disabled={!pvmHex || isWorking}
              className="w-[86%] px-3 flex items-center gap-3 rounded-lg transition-all disabled:opacity-40 disabled:cursor-not-allowed"
              style={{
                height: "40px",
                backgroundColor: pvmHex
                  ? "rgba(0, 255, 136, 0.1)"
                  : "rgba(255, 255, 255, 0.02)",
                border: `1px solid ${
                  pvmHex ? "rgba(0, 255, 136, 0.2)" : "rgba(255, 255, 255, 0.05)"
                }`,
                fontFamily: "JetBrains Mono, monospace",
                fontSize: "13px",
                color: pvmHex ? "#00ff88" : "#404040",
              }}
              onMouseEnter={(e) => {
                if (!e.currentTarget.disabled && pvmHex) {
                  e.currentTarget.style.backgroundColor =
                    "rgba(0, 255, 136, 0.15)";
                  e.currentTarget.style.borderColor = "rgba(0, 255, 136, 0.4)";
                }
              }}
              onMouseLeave={(e) => {
                if (pvmHex) {
                  e.currentTarget.style.backgroundColor =
                    "rgba(0, 255, 136, 0.1)";
                  e.currentTarget.style.borderColor = "rgba(0, 255, 136, 0.2)";
                }
              }}
            >
              {status === "running" ? (
                <LoadingSpinner color="#00ff88" />
              ) : (
                <Icons.play />
              )}
              <span>refine()</span>
              <span
                className="ml-auto px-1.5 py-0.5 rounded"
                style={{
                  fontSize: "10px",
                  backgroundColor: "#333",
                  color: "#888",
                }}
              >
                ⌘R
              </span>
            </button>
          </div>

          <div className="px-3 pt-2">
            <button
              onClick={onAccumulate}
              disabled={!pvmHex || isWorking}
              className="w-[86%] px-3 flex items-center gap-3 rounded-lg transition-all disabled:opacity-40 disabled:cursor-not-allowed"
              style={{
                height: "40px",
                backgroundColor: pvmHex
                  ? "rgba(168, 85, 247, 0.1)"
                  : "rgba(255, 255, 255, 0.02)",
                border: `1px solid ${
                  pvmHex ? "rgba(168, 85, 247, 0.2)" : "rgba(255, 255, 255, 0.05)"
                }`,
                fontFamily: "JetBrains Mono, monospace",
                fontSize: "13px",
                color: pvmHex ? "#a855f7" : "#404040",
              }}
              onMouseEnter={(e) => {
                if (!e.currentTarget.disabled && pvmHex) {
                  e.currentTarget.style.backgroundColor =
                    "rgba(168, 85, 247, 0.15)";
                  e.currentTarget.style.borderColor = "rgba(168, 85, 247, 0.4)";
                }
              }}
              onMouseLeave={(e) => {
                if (pvmHex) {
                  e.currentTarget.style.backgroundColor =
                    "rgba(168, 85, 247, 0.1)";
                  e.currentTarget.style.borderColor = "rgba(168, 85, 247, 0.2)";
                }
              }}
            >
              {status === "accumulating" ? (
                <LoadingSpinner color="#a855f7" />
              ) : (
                <Icons.play />
              )}
              <span>accumulate()</span>
              <span
                className="ml-auto px-1.5 py-0.5 rounded"
                style={{
                  fontSize: "10px",
                  backgroundColor: "#333",
                  color: "#888",
                }}
              >
                ⌘A
              </span>
            </button>
          </div>
        </>
      )}

      {/* 4. LIVE FLOW */}
      {isLive && (
        <>
          {/* DEPLOY PHASE */}
          {pvmHex && (
            <div className="px-3 pb-3 pt-3">
              <div
                className="mb-2"
                style={{
                  fontFamily: "JetBrains Mono, monospace",
                  fontSize: "11px",
                  color: "#858585",
                }}
              >
                {"// deploy"}
              </div>
              {deployedServiceId ? (
                <div
                  className="p-3 rounded-lg"
                  style={{
                    backgroundColor: "#1e1e1e",
                    border: "1px solid rgba(255, 136, 0, 0.3)",
                  }}
                >
                  <div
                    style={{
                      fontFamily: "JetBrains Mono, monospace",
                      fontSize: "11px",
                      color: "#858585",
                    }}
                  >
                    service id
                  </div>
                  <div
                    style={{
                      fontFamily: "JetBrains Mono, monospace",
                      fontSize: "12px",
                      color: "#ff8800",
                      wordBreak: "break-all",
                    }}
                  >
                    {deployedServiceId}
                  </div>
                </div>
              ) : (
                <div className="relative">
                  <button
                    disabled={true}
                    className="w-[86%] px-3 flex items-center gap-3 rounded-lg transition-all opacity-50 cursor-not-allowed"
                    style={{
                      height: "40px",
                      backgroundColor: "rgba(255, 136, 0, 0.05)",
                      border: "1px solid rgba(255, 136, 0, 0.1)",
                      fontFamily: "JetBrains Mono, monospace",
                      fontSize: "13px",
                      color: "#666",
                    }}
                  >
                    <Icons.deploy />
                    <span>deploy()</span>
                    <span
                      className="ml-auto px-1.5 py-0.5 rounded"
                      style={{
                        fontSize: "10px",
                        backgroundColor: "#333",
                        color: "#888",
                      }}
                    >
                      ⌘D
                    </span>
                  </button>
                  {/* Coming Soon Badge */}
                  <div
                    className="absolute -top-2 -right-2 px-2 py-0.5 rounded-full"
                    style={{
                      backgroundColor: "rgba(255, 136, 0, 0.15)",
                      border: "1px solid rgba(255, 136, 0, 0.3)",
                      fontFamily: "JetBrains Mono, monospace",
                      fontSize: "9px",
                      color: "#ff8800",
                      whiteSpace: "nowrap",
                    }}
                  >
                    coming soon
                  </div>
                </div>
              )}
            </div>
          )}

          {/* INVOKE PHASE */}
          {deployedServiceId && (
            <div className="px-3 pt-2">
              <div
                className="mb-2"
                style={{
                  fontFamily: "JetBrains Mono, monospace",
                  fontSize: "11px",
                  color: "#858585",
                }}
              >
                {"// invoke"}
              </div>
              <textarea
                value={payload}
                onChange={(e) => onPayloadChange(e.target.value)}
                className="w-full h-20 px-3 py-2 rounded-lg resize-none focus:outline-none"
                style={{
                  backgroundColor: "#1e1e1e",
                  border: "1px solid #3c3c3c",
                  fontFamily: "JetBrains Mono, monospace",
                  fontSize: "12px",
                  color: "#ccc",
                }}
                placeholder="input data..."
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = "#00ff88";
                  e.currentTarget.style.boxShadow =
                    "0 0 0 1px rgba(0, 255, 136, 0.1)";
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = "#1a1a1a";
                  e.currentTarget.style.boxShadow = "none";
                }}
              />

              <button
                onClick={onInvoke}
                disabled={isWorking}
                className="w-[86%] px-3 mt-3 flex items-center gap-3 rounded-lg transition-all disabled:opacity-40 disabled:cursor-not-allowed"
                style={{
                  height: "40px",
                  backgroundColor: "rgba(0, 255, 136, 0.1)",
                  border: "1px solid rgba(0, 255, 136, 0.2)",
                  fontFamily: "JetBrains Mono, monospace",
                  fontSize: "13px",
                  color: "#00ff88",
                }}
                onMouseEnter={(e) => {
                  if (!e.currentTarget.disabled) {
                    e.currentTarget.style.backgroundColor =
                      "rgba(0, 255, 136, 0.15)";
                    e.currentTarget.style.borderColor =
                      "rgba(0, 255, 136, 0.4)";
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor =
                    "rgba(0, 255, 136, 0.1)";
                  e.currentTarget.style.borderColor =
                    "rgba(0, 255, 136, 0.2)";
                }}
              >
                {status === "invoking" ? (
                  <LoadingSpinner color="#00ff88" />
                ) : (
                  <Icons.play />
                )}
                <span>invoke()</span>
                <span
                  className="ml-auto px-1.5 py-0.5 rounded"
                  style={{
                    fontSize: "10px",
                    backgroundColor: "#333",
                    color: "#888",
                  }}
                >
                  ⌘R
                </span>
              </button>
            </div>
          )}
        </>
      )}

      {/* Shortcuts Footer */}
      <div className="mt-auto" style={{ borderTop: "1px solid #333" }}>
        <Link
          href={"https://chainscore.finance"}
          target="_blank"
          className="mx-3 mt-auto mb-1 p-2 rounded-lg flex flex-col items-center gap-3"
        >
          <div
            style={{
              fontFamily: "JetBrains Mono, monospace",
              fontSize: "12px",
              color: "#bdbdbd",
            }}
          >
            Developed by
          </div>
          <Image
            src="/assets/chainscore.svg"
            alt="Chainscore Labs"
            width={140}
            height={20}
          />
        </Link>

        <div className="px-3 py-3" style={{ borderTop: "1px solid #333" }}>
          <div
            className="space-y-1"
            style={{
              fontFamily: "JetBrains Mono, monospace",
              fontSize: "10px",
              color: "#666",
            }}
          >
            <div className="flex items-center justify-between">
              <span>⌘B</span>
              <span>build</span>
            </div>
            <div className="flex items-center justify-between">
              <span>⌘R</span>
              <span>{isLive && deployedServiceId ? "invoke" : "run"}</span>
            </div>
            {isLive && !deployedServiceId && (
              <div className="flex items-center justify-between">
                <span>⌘D</span>
                <span>deploy</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </aside>
  );
}
