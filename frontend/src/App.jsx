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
  stopScan
} from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('feed');
  const [currentTarget, setCurrentTarget] = useState('');
  const [currentTargetType, setCurrentTargetType] = useState('unknown');
  const [activeScanId, setActiveScanId] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [findings, setFindings] = useState([]);
  const [scanSummary, setScanSummary] = useState(null);
  
  const [availableModules, setAvailableModules] = useState([]);
  const [cases, setCases] = useState([]);
  const [activeCase, setActiveCase] = useState(null);

  const [isCasesOpen, setIsCasesOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isExportOpen, setIsExportOpen] = useState(false);

  const eventSourceRef = useRef(null);

  useEffect(() => {
    getModules().then(setAvailableModules);
    getCases().then((list) => {
      setCases(list);
      if (list.length > 0) setActiveCase(list[0]);
    });
  }, []);

  const handleStartScan = async (scanPayload) => {
    try {
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

      es.addEventListener('scan_failed', () => {
        setIsScanning(false);
        es.close();
      });

      es.onerror = () => {
        setIsScanning(false);
        es.close();
      };
    } catch (err) {
      console.error('Scan launch failed:', err);
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
    <div className="min-h-screen flex flex-col bg-[#09090b] text-zinc-100 subtle-grid">
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

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {findings.length === 0 && !isScanning && (
          <div className="text-center max-w-2xl mx-auto my-8 sm:my-14 animate-fadeIn">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-900 border border-white/10 text-zinc-300 text-xs font-mono mb-4">
              <span className="w-1.5 h-1.5 rounded-full bg-white"></span>
              <span>Minimalist OSINT Reconnaissance Framework</span>
            </div>
            <h1 className="text-3xl sm:text-5xl font-bold tracking-tight text-white leading-tight">
              Universal Entity <br />
              <span className="text-zinc-400">Intelligence Dashboard</span>
            </h1>
            <p className="mt-3 text-xs sm:text-sm text-zinc-400 max-w-lg mx-auto font-mono">
              Fast, privacy-first reconnaissance across 130+ sources. Zero external logs, instant link analysis, and full OPSEC control.
            </p>
          </div>
        )}

        <SmartSearch
          onStartScan={handleStartScan}
          onStopScan={handleStopScan}
          isScanning={isScanning}
          availableModules={availableModules}
        />

        <StatsOverview summary={scanSummary} isScanning={isScanning} />

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

      <footer className="border-t border-white/5 bg-zinc-950/60 py-6 mt-16 text-xs text-zinc-500 font-mono">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-white"></span>
            <span>OmniTrace Core • 100% Client/Self-Hosted Architecture</span>
          </div>
          <div>
            Zero Telemetry • Free & Open Source under MIT License
          </div>
        </div>
      </footer>

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
