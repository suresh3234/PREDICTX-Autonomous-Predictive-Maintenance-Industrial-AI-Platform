import React, { useState, useEffect } from 'react';
import {
  Boxes,
  Play,
  Terminal,
  RefreshCw,
  CheckCircle2,
  Server,
  Layers,
  Code2,
  Cpu,
} from 'lucide-react';
import { fetchMCPServers, executeMCPTool } from '../api/client';

export const MCPTools: React.FC = () => {
  const [mcpData, setMcpData] = useState<any>(null);
  const [selectedTool, setSelectedTool] = useState<string>('get_latest_telemetry');
  const [toolArgs, setToolArgs] = useState<string>('{\n  "machine_id": "M1000"\n}');
  const [executing, setExecuting] = useState(false);
  const [execResult, setExecResult] = useState<any | null>(null);

  useEffect(() => {
    async function loadMcp() {
      try {
        const res = await fetchMCPServers();
        setMcpData(res);
      } catch (err) {
        console.error('Failed loading MCP servers:', err);
      }
    }
    loadMcp();
  }, []);

  const handleExecute = async () => {
    setExecuting(true);
    try {
      let parsedArgs = {};
      try {
        parsedArgs = JSON.parse(toolArgs);
      } catch {
        parsedArgs = {};
      }
      const res = await executeMCPTool(selectedTool, parsedArgs);
      setExecResult(res);
    } catch (err: any) {
      setExecResult({ error: err.message });
    } finally {
      setExecuting(false);
    }
  };

  const sampleServers = [
    { server_id: 'sensor', name: 'predictx-sensor-server', description: 'IoT Sensor Telemetry Streams & Thresholds', tools_count: 3 },
    { server_id: 'database', name: 'predictx-database-server', description: 'Asset Metadata & Maintenance Records', tools_count: 3 },
    { server_id: 'knowledge', name: 'predictx-knowledge-server', description: 'Equipment SOPs & Fault Manuals', tools_count: 3 },
    { server_id: 'maintenance', name: 'predictx-maintenance-server', description: 'Work Order Management & Inventory', tools_count: 3 },
    { server_id: 'alert', name: 'predictx-alert-server', description: 'SCADA Alarms & Notifications', tools_count: 3 },
  ];

  const sampleTools = [
    { name: 'get_latest_telemetry', server_id: 'sensor', description: 'Fetches latest live sensor readings for a machine.' },
    { name: 'get_breached_sensors', server_id: 'sensor', description: 'Checks if sensor channels breach operating thresholds.' },
    { name: 'query_machine_metadata', server_id: 'database', description: 'Retrieves machine specs, model number, and installation date.' },
    { name: 'search_manuals', server_id: 'knowledge', description: 'Searches equipment manuals for troubleshooting procedures.' },
    { name: 'create_work_order', server_id: 'maintenance', description: 'Creates a preventive or corrective maintenance work order.' },
    { name: 'trigger_emergency_alert', server_id: 'alert', description: 'Triggers a plant-wide emergency alert for critical assets.' },
  ];

  const servers = mcpData?.servers || sampleServers;
  const tools = mcpData?.tools || sampleTools;

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
            <Boxes className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-100">Model Context Protocol (MCP) Tools</h1>
            <p className="text-sm text-slate-400">
              Standardized JSON-RPC 2.0 tool servers connecting AI agents to industrial sensors, databases, and alerting
            </p>
          </div>
        </div>

        <span className="px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-xs font-mono font-bold">
          MCP Spec v2024-11-05
        </span>
      </div>

      {/* Mounted Servers Grid */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {servers.map((srv: any, idx: number) => (
          <div key={idx} className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl">
            <div className="flex items-center justify-between mb-2">
              <Server className="w-4 h-4 text-cyan-400" />
              <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">MOUNTED</span>
            </div>
            <h4 className="text-xs font-bold text-white mb-1 font-mono truncate">{srv.name}</h4>
            <p className="text-[11px] text-slate-400 mb-2 line-clamp-2">{srv.description}</p>
            <span className="text-[10px] text-slate-500 font-mono">{srv.tools_count} Registered Tools</span>
          </div>
        ))}
      </div>

      {/* Interactive Tool Execution Playground */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Tool Selector & Arguments Input */}
        <div className="lg:col-span-5 bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Terminal className="w-4 h-4 text-cyan-400" />
            MCP Tool Invocation Playground
          </h3>

          <div>
            <label className="text-xs text-slate-400 block mb-1 font-medium">Select Tool</label>
            <select
              value={selectedTool}
              onChange={(e) => {
                setSelectedTool(e.target.value);
                if (e.target.value === 'get_latest_telemetry') setToolArgs('{\n  "machine_id": "M1000"\n}');
                else if (e.target.value === 'get_breached_sensors') setToolArgs('{\n  "machine_id": "M1003"\n}');
                else if (e.target.value === 'search_manuals') setToolArgs('{\n  "query": "bearing wear"\n}');
                else setToolArgs('{\n  "machine_id": "M1000"\n}');
              }}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs font-mono text-cyan-300 focus:outline-none focus:border-cyan-500"
            >
              {tools.map((t: any, i: number) => (
                <option key={i} value={t.name}>
                  {t.name} ({t.server_id || 'mcp'})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs text-slate-400 block mb-1 font-medium">JSON-RPC Arguments</label>
            <textarea
              rows={6}
              value={toolArgs}
              onChange={(e) => setToolArgs(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs font-mono text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <button
            onClick={handleExecute}
            disabled={executing}
            className="w-full py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs shadow-lg shadow-cyan-600/30 flex items-center justify-center gap-2 transition-all"
          >
            {executing ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
            Execute MCP Tool Call
          </button>
        </div>

        {/* Execution Output Console */}
        <div className="lg:col-span-7 bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Code2 className="w-4 h-4 text-emerald-400" />
              JSON-RPC 2.0 Response Payload
            </h3>
            <span className="text-[11px] font-mono text-slate-500">HTTP 200 OK</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs text-emerald-400 overflow-x-auto max-h-80">
            <pre>
              {execResult
                ? JSON.stringify(execResult, null, 2)
                : JSON.stringify(
                    {
                      jsonrpc: '2.0',
                      id: 1,
                      result: {
                        tool: selectedTool,
                        status: 'READY_FOR_EXECUTION',
                        message: 'Click "Execute MCP Tool Call" to route call to the mounted tool server.',
                      },
                    },
                    null,
                    2
                  )}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
};
