import React, { useState, useEffect, useRef } from 'react';
import Navbar from './components/Navbar';
import SmartSearch from './components/SmartSearch';
import StatsOverview from './components/StatsOverview';
import ResultsStream from './components/ResultsStream';
import GraphView from './components/GraphView';
import CasesModal from './components/CasesModal';
import SettingsModal from './components/SettingsModal';
import ExportModal from './components/ExportModal';
import { 
  getCases, 
  createCase, 
  deleteCase, 
  getModules, 
  startScan, 
  stopScan,
  getRecentScans
} from './services/api';
import { Shield, Sparkles, Terminal, Cpu, ArrowUpRight } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('feed'); // 'feed' | 'graph'
  const [currentTarget, setCurrentTarget] = useState('');
  const [currentTargetType, setCurrentTargetType] = useState('unknown');
  const [activeScanId, setActiveScanId] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [findings, setFindings] = useState([]);
  const [scanSummary, setScanSummary] = useState(null);
  
  // Available modules
  const [availableModules, setAvailableModules] = useState([]);

  // Cases management
  const [cases, setCases] = useState([]);
  const [activeCase, setActiveCase] = useState(null);

  // Modals
  const [isCasesOpen, setIsCasesOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isExportOpen, setIsExportOpen] = useState(false);

  const eventSourceRef = useRef(null);

  // Initial load
  useEffect(() => {
    getModules().then(setAvailableModules);
    getCases().then((list) => {
      setCases(list);
      if (list.length > 0) setActiveCase(list[0]);
    });
  }, []);

  // Handle SSE streaming
  const handleStartScan = async (scanPayload) => {
    try {
      // Abort any existing stream
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      setFindings([]);
      setScanSummary(null);
      setIsScanning(true);
      setCurrentTarget(scanPayload.target);
      setCurrentTargetType(scanPayload.target_type || 'unknown');

      const res = await startScan({
        ...scanPayload,
        case_id: activeCase?.id || null,
      });

      const scanId = res.scan_id;
      setActiveScanId(scanId);

      // Open EventSource SSE connection
      const es = new EventSource(`/api/scan/${scanId}/stream`);
      eventSourceRef.current = es;

      es.addEventListener('scan_start', (e) => {
        const data = JSON.parse(e.data);
        setCurrentTarget(data.target);
        setCurrentTargetType(data.target_type);
      });

      es.addEventListener('finding', (e) => {
        const finding = JSON.parse(e.data);
        setFindings((prev) => [finding, ...prev]);

        // Dynamically increment counters
        setScanSummary((prev) => {
          const current = prev || {
            total_checks: 0,
            found_count: 0,
            not_found_count: 0,
            error_count: 0,
          };
          return {
            ...current,
            total_checks: current.total_checks + 1,
            found_count:
              finding.status === 'found' ? current.found_count + 1 : current.found_count,
            not_found_count:
              finding.status === 'not_found'
                ? current.not_found_count + 1
                : current.not_found_count,
            error_count: ['error', 'rate_limited'].includes(finding.status)
              ? current.error_count + 1
              : current.error_count,
          };
        });
      });

      es.addEventListener('scan_complete', (e) => {
        const summary = JSON.parse(e.data);
        setScanSummary(summary);
        setIsScanning(false);
        es.close();
      });

      es.addEventListener('scan_stopped', () => {
        setIsScanning(false);
        es.close();
      });

      es.addEventListener('scan_failed', (e) => {
        console.error('Scan failed:', e.data);
        setIsScanning(false);
        es.close();
      });

      es.onerror = (err) => {
        console.warn('SSE stream closed or completed:', err);
        setIsScanning(false);
        es.close();
      };
    } catch (err) {
      console.error('Failed to initiate scan:', err);
      setIsScanning(false);
    }
  };

  const handleStopScan = async () => {
    if (activeScanId) {
      await stopScan(activeScanId);
    }
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    setIsScanning(false);
  };

  // Case actions
  const handleCreateCase = async (caseData) => {
    const created = await createCase(caseData);
    setCases((prev) => [created, ...prev]);
    setActiveCase(created);
  };

  const handleDeleteCase = async (caseId) => {
    await deleteCase(caseId);
    setCases((prev) => prev.filter((c) => c.id !== caseId));
    if (activeCase?.id === caseId) {
      setActiveCase(null);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#080c14] text-slate-100 radar-grid selection:bg-cyan-500/30">
      {/* Top Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        activeCase={activeCase}
        onOpenCases={() => setIsCasesOpen(true)}
        onOpenSettings={() => setIsSettingsOpen(true)}
        onOpenExport={() => setIsExportOpen(true)}
        isScanning={isScanning}
        hasResults={findings.length > 0}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        
        {/* Hero Section if no scan has been run yet */}
        {findings.length === 0 && !isScanning && (
          <div className="text-center max-w-2xl mx-auto my-6 sm:my-10 animate-fadeIn">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-cyan-950/70 border border-cyan-800/60 text-cyan-400 text-xs font-mono mb-4">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Next-Gen OSINT Intelligence Platform</span>
            </div>
            <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-slate-100 leading-tight">
              Investigate Any Entity <br />
              <span className="bg-gradient-to-r from-cyan-400 via-sky-300 to-blue-500 bg-clip-text text-transparent">
                Directly In Your Browser
              </span>
            </h1>
            <p className="mt-3 text-sm sm:text-base text-slate-400 max-w-xl mx-auto">
              OmniTrace aggregates world-class open-source intelligence tools into a unified, self-hosted, OPSEC-safe dashboard.
            </p>
          </div>
        )}

        {/* Universal Smart Search Box */}
        <SmartSearch
          onStartScan={handleStartScan}
          onStopScan={handleStopScan}
          isScanning={isScanning}
          availableModules={availableModules}
        />

        {/* Real-time Statistics Cards */}
        <StatsOverview summary={scanSummary} isScanning={isScanning} />

        {/* Primary View Area (Feed vs Relationship Graph) */}
        {activeTab === 'feed' ? (
          <ResultsStream findings={findings} isScanning={isScanning} />
        ) : (
          <GraphView
            target={currentTarget}
            targetType={currentTargetType}
            findings={findings}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/40 py-6 mt-12 text-center text-xs text-slate-500 font-mono">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            <span>OmniTrace Core Active • 100% Client/Self-Hosted Reconnaissance</span>
          </div>
          <div>
            Built with Privacy & OPSEC Integrity • Free & Open Source under MIT License
          </div>
        </div>
      </footer>

      {/* Modals */}
      <CasesModal
        isOpen={isCasesOpen}
        onClose={() => setIsCasesOpen(false)}
        cases={cases}
        activeCase={activeCase}
        onSelectCase={setActiveCase}
        onCreateCase={handleCreateCase}
        onDeleteCase={handleDeleteCase}
      />

      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
      />

      <ExportModal
        isOpen={isExportOpen}
        onClose={() => setIsExportOpen(false)}
        scanId={activeScanId}
        target={currentTarget}
      />
    </div>
  );
}
