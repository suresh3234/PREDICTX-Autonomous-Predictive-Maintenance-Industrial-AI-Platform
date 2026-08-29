import React, { useState, useEffect } from 'react';
import {
  BookOpen,
  Search,
  FileText,
  ShieldAlert,
  Sparkles,
  ExternalLink,
  ChevronRight,
  Layers,
  Wrench,
  CheckCircle2,
} from 'lucide-react';
import { fetchKnowledgeDocuments, searchRAG } from '../api/client';

export const KnowledgeBase: React.FC = () => {
  const [documents, setDocuments] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState<any | null>(null);

  useEffect(() => {
    async function loadDocs() {
      try {
        const res = await fetchKnowledgeDocuments();
        setDocuments(res.documents || []);
        if (res.documents && res.documents.length > 0) {
          setSelectedDoc(res.documents[0]);
        }
      } catch (err) {
        console.error('Failed loading documents:', err);
      }
    }
    loadDocs();
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setSearching(true);
    try {
      const res = await searchRAG(searchQuery, 5);
      setSearchResults(res.results || []);
    } catch (err) {
      console.error('RAG Search failed:', err);
    } finally {
      setSearching(false);
    }
  };

  const sampleManuals = [
    {
      title: 'Centrifugal Slurry Pump Maintenance & Bearing Overhaul SOP',
      machine_type: 'Centrifugal Pump (M1000, M1004)',
      sop_id: 'SOP-PUMP-04',
      summary: 'Diagnostic procedures for cavitation, impeller wear, mechanical seal leaks, and ISO 10816 vibration thresholds.',
      content: `1. LOCKOUT/TAGOUT (LOTO): De-energize 400V motor circuit at breaker MCC-04 and tag with yellow padlock.
2. VIBRATION DIAGNOSIS: If RMS vibration exceeds 3.5 mm/s at 1X rotational frequency (1500 RPM), inspect drive coupling alignment.
3. BEARING REPLACEMENT: Drain ISO VG 68 oil reservoir. Extract front/rear roller bearings. Press fit new SKF 6309 bearings heated to 110°C.
4. SEAL FLUSH: Ensure mechanical seal barrier fluid pressure is maintained at 15 PSI above pump discharge pressure.`
    },
    {
      title: 'Rotary Screw Compressor Cooling Radiator & Air-End SOP',
      machine_type: 'Rotary Compressor (M1001)',
      sop_id: 'SOP-COMP-02',
      summary: 'Thermal runaway prevention, oil-separator differential pressure checks, and radiator fin hydro-cleaning.',
      content: `1. THERMAL SAFETY: When discharge temperature exceeds 85°C, automatic thermal protection trips. Clean external radiator fins with 3-bar degreasing wash.
2. OIL SEPARATOR: Replace oil separator cartridge if differential pressure gauge exceeds 0.8 bar.
3. INTAKE VALVE: Inspect modulating intake valve actuator pneumatic diaphragm for tears if unloaded pressure exceeds 7.5 bar.`
    },
    {
      title: '3-Phase Induction Motor Stator & Rotor Integrity Manual',
      machine_type: 'Induction Motor (M1002)',
      sop_id: 'SOP-MTR-01',
      summary: 'Insulation resistance (Megger) testing, stator winding temperature limits, and shaft current grounding.',
      content: `1. MEGGER TEST: Perform 1000V DC insulation test. Minimum acceptable phase-to-ground resistance is 100 Megaohms at 25°C.
2. CURRENT IMBALANCE: If phase current imbalance exceeds 5%, inspect supply contactor points and incoming line voltage harmonics.
3. GREASE REGIME: Lubricate drive-end bearing with 15g Mobil Polyrex EM grease every 2000 operating hours.`
    },
    {
      title: 'High-Pressure Hydraulic Press Cylinder & Valve Block Overhaul',
      machine_type: 'Hydraulic Press (M1003)',
      sop_id: 'SOP-HYD-08',
      summary: 'Proportional valve calibration, high-pressure polyurethane seal replacement, and oil contamination particle analysis.',
      content: `1. PRESSURE RELIEF: De-pressurize main cylinder accumulator circuit before loosening any hydraulic flange.
2. SEAL INTEGRITY: If cylinder leakage exceeds 5 drops/min under 160 bar holding pressure, replace dual wiper and Chevron packings.
3. FLUID SPECIFICATION: Use ISO VG 46 anti-wear hydraulic oil. Particle cleanliness must meet ISO 4406 16/14/11 standard.`
    }
  ];

  const docsToDisplay = documents.length > 0 ? documents : sampleManuals;

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400">
            <BookOpen className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-100">Engineering Knowledge Base & RAG Search</h1>
            <p className="text-sm text-slate-400">
              Hybrid dense/sparse indexed standard operating procedures (SOPs) and equipment reliability manuals
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3 py-1.5 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5" /> Dense + BM25 Hybrid Store Active
          </span>
        </div>
      </div>

      {/* Semantic Search Bar */}
      <form onSubmit={handleSearch} className="relative">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search maintenance procedures (e.g. 'bearing replacement SOP', 'high temperature compressor radiator clean', 'hydraulic seal leak')..."
          className="w-full bg-slate-900 border border-slate-800 rounded-2xl pl-12 pr-28 py-3.5 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 shadow-xl"
        />
        <Search className="w-5 h-5 text-slate-500 absolute left-4 top-4" />
        <button
          type="submit"
          disabled={searching}
          className="absolute right-2.5 top-2 px-4 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md transition-all flex items-center gap-1.5"
        >
          {searching ? 'Retrieving...' : 'Hybrid Search'}
        </button>
      </form>

      {/* Search Results if any */}
      {searchResults.length > 0 && (
        <div className="p-5 rounded-2xl bg-slate-900/90 border border-blue-500/30 shadow-2xl space-y-3">
          <h3 className="text-xs font-bold text-blue-400 uppercase tracking-wider flex items-center gap-2">
            <Sparkles className="w-3.5 h-3.5" />
            Hybrid RAG Retrieval Ranked Matches for: "{searchQuery}"
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {searchResults.map((r, i) => (
              <div key={i} className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 hover:border-blue-500/40 transition-all">
                <div className="flex justify-between items-start mb-1.5">
                  <span className="text-xs font-bold text-white">{r.title}</span>
                  <span className="text-[10px] font-mono text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded">
                    Score: {(r.hybrid_score * 100).toFixed(1)}%
                  </span>
                </div>
                <p className="text-xs text-slate-400 line-clamp-2">{r.text || r.summary}</p>
                <div className="mt-2 flex items-center gap-2 text-[10px] text-slate-500 font-mono">
                  <span>Ref: {r.sop_reference}</span>
                  <span>•</span>
                  <span>{r.machine_type}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Manuals Viewer Split */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Document List */}
        <div className="lg:col-span-4 space-y-3">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider px-1">Indexed Manuals ({docsToDisplay.length})</h3>
          <div className="space-y-2">
            {docsToDisplay.map((doc, idx) => (
              <button
                key={idx}
                onClick={() => setSelectedDoc(doc)}
                className={`w-full text-left p-4 rounded-xl border transition-all ${
                  selectedDoc?.sop_id === doc.sop_id || selectedDoc?.title === doc.title
                    ? 'bg-blue-600/10 border-blue-500/50 text-white shadow-lg'
                    : 'bg-slate-900/80 border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-mono font-semibold text-blue-400">{doc.sop_id || `DOC-0${idx + 1}`}</span>
                  <span className="text-[10px] text-slate-500 font-mono">PDF/JSON</span>
                </div>
                <h4 className="text-sm font-semibold text-slate-200 mb-1">{doc.title}</h4>
                <p className="text-xs text-slate-400 line-clamp-1">{doc.machine_type}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Right: Selected Document Content Viewer */}
        <div className="lg:col-span-8">
          {selectedDoc ? (
            <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
              <div className="border-b border-slate-800 pb-4">
                <div className="flex items-center gap-2 text-xs font-mono text-blue-400 mb-1">
                  <span>{selectedDoc.sop_id || 'SOP-GEN-01'}</span>
                  <span>•</span>
                  <span>{selectedDoc.machine_type}</span>
                </div>
                <h2 className="text-lg font-bold text-white">{selectedDoc.title}</h2>
                <p className="text-xs text-slate-400 mt-1">{selectedDoc.summary}</p>
              </div>

              {/* Document Text */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 text-xs text-slate-300 font-mono leading-relaxed whitespace-pre-wrap">
                {selectedDoc.content || selectedDoc.text || 'Standard operating procedure detailed maintenance checklist...'}
              </div>

              {/* Safety Requirements Footer */}
              <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-300 flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 shrink-0" />
                <span>Mandatory PPE: Safety Glasses, Heat-Resistant Gloves, Lockout-Tagout (LOTO) Padlock.</span>
              </div>
            </div>
          ) : (
            <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-12 text-center text-slate-500">
              Select a manual from the library to view full technical text
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
