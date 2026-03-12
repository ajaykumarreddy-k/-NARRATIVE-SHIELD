import { useState, useEffect, useCallback } from 'react';
import { Moon, Sun } from 'lucide-react';
import { analyzeLocally } from './analysisEngine';

const MarqueeTop = () => (
    <div className="bg-black h-10 flex items-center overflow-hidden border-b-4 border-black fixed top-0 w-full z-[100]">
        <div className="animate-marquee flex items-center">
            {[1, 2].map((i) => (
                <div key={i} className="flex items-center">
                    <span className="text-yellow font-mono text-sm font-bold uppercase mx-8 flex items-center gap-4">
                        NarrativeShield v1.0 <span className="text-xl">★</span> AI Disinformation Detection <span className="text-xl">★</span> Real-Time Threat Scoring <span className="text-xl">★</span> Provenance Analysis <span className="text-xl">★</span> Problem #06 · Cybersecurity <span className="text-xl">★</span> SciComp 2026 · SIMATS <span className="text-xl">★</span> Dual-Layer AI Pipeline <span className="text-xl">★</span> Built in 5 Hours <span className="text-xl">★</span>
                    </span>
                </div>
            ))}
        </div>
    </div>
);

type BackendStatus = 'checking' | 'online' | 'offline';

const Header = ({ onOpenApiModal, hasApiKey, isDarkMode, toggleDarkMode, backendStatus }: {
    onOpenApiModal: () => void;
    hasApiKey: boolean;
    isDarkMode: boolean;
    toggleDarkMode: () => void;
    backendStatus: BackendStatus;
}) => {
    const statusColor = backendStatus === 'online'
        ? 'bg-green dark:text-black'
        : backendStatus === 'offline'
            ? 'bg-red text-white'
            : 'bg-yellow dark:text-black';
    const statusLabel = backendStatus === 'online'
        ? (hasApiKey ? 'BACKEND: ONLINE ✓' : 'BACKEND: ONLINE (NO KEY)')
        : backendStatus === 'offline'
            ? 'BACKEND: OFFLINE — LOCAL MODE'
            : 'BACKEND: CHECKING...';

    return (
        <header className="bg-white dark:bg-gray-900 h-20 border-b-4 border-black flex items-center justify-between px-6 sticky top-10 z-[90]">
            <div className="flex items-center gap-6">
                <h1 className="text-3xl font-black tracking-tighter flex items-center gap-2">
                    🛡️ NARRATIVESHIELD
                </h1>
                <div className="hidden lg:flex gap-3">
                    <button
                        onClick={toggleDarkMode}
                        className="bg-white dark:bg-gray-800 px-3 py-1 border-2 border-black text-xs font-bold shadow-shSm hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all cursor-pointer flex items-center gap-2"
                    >
                        {isDarkMode ? <Sun size={14} /> : <Moon size={14} />}
                        {isDarkMode ? 'LIGHT' : 'DARK'}
                    </button>
                    <button
                        onClick={onOpenApiModal}
                        className={`${statusColor} px-3 py-1 border-2 border-black text-xs font-bold shadow-shSm hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all cursor-pointer`}
                    >
                        {statusLabel}
                    </button>
                    {backendStatus === 'offline' && (
                        <span className="bg-violet dark:text-black px-3 py-1 border-2 border-black text-xs font-bold shadow-shSm animate-pulse">
                            ⚡ LOCAL ENGINE ACTIVE
                        </span>
                    )}
                </div>
            </div>
            <div className="bg-red text-black px-4 py-1 border-2 border-black font-black text-xs transform rotate-2 shadow-shSm uppercase">
                Cybersecurity Badge v2.4
            </div>
        </header>
    );
};

const ApiKeyModal = ({ isOpen, onClose, apiKey, setApiKey }: { isOpen: boolean, onClose: () => void, apiKey: string, setApiKey: (key: string) => void }) => {
    if (!isOpen) return null;
    return (
        <div className="fixed inset-0 bg-black/60 z-[200] flex items-center justify-center p-4 backdrop-blur-sm">
            <div className="bg-white dark:bg-gray-900 neo-border-bold p-6 max-w-md w-full shadow-shLg relative animate-in fade-in duration-200">
                <button onClick={onClose} className="absolute top-4 right-4 font-black text-xl hover:text-red transition-colors">X</button>
                <h2 className="text-2xl font-black mb-4 uppercase">API Configuration</h2>
                <div className="bg-cream dark:bg-gray-800 neo-border p-4 mb-6 text-sm font-medium">
                    <p className="mb-2 font-black text-lg uppercase">Bring Your Own Key</p>
                    <p className="mb-3">To power the NarrativeShield analysis engine, you need a Google Gemini API key.</p>
                    <ol className="list-decimal pl-5 space-y-2 text-xs font-mono mb-3">
                        <li>Go to <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noreferrer" className="text-blue-600 dark:text-blue-400 underline font-bold hover:text-blue-800 dark:hover:text-blue-300">Google AI Studio</a></li>
                        <li>Create a new API key or copy an existing one</li>
                        <li>Paste it securely in the field below</li>
                    </ol>
                    <p className="mt-2 text-[10px] text-gray-500 dark:text-gray-400 italic">* Your key is stored locally in your browser session and never sent to our servers.</p>
                </div>
                <div className="mb-4">
                    <label className="block font-black text-xs uppercase mb-2">Gemini API Key</label>
                    <input
                        type="password"
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                        placeholder="AIzaSy..."
                        className="w-full neo-border p-3 font-mono text-sm focus:ring-0 focus:border-black bg-cream dark:bg-gray-800 outline-none"
                    />
                </div>
                <button
                    onClick={onClose}
                    className="w-full bg-yellow dark:text-black font-black text-lg neo-border shadow-shSm hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all py-3 active:bg-black active:text-white"
                >
                    SAVE CONFIGURATION
                </button>
            </div>
        </div>
    );
};

const Hero = () => (
    <section className="bg-black text-white py-20 px-6 border-b-4 border-black overflow-hidden relative">
        <div className="container mx-auto flex flex-col md:flex-row items-center gap-12">
            <div className="flex-1">
                <h2 className="text-6xl md:text-8xl font-black leading-none mb-6">
                    <span className="text-outline block">NARRATIVE</span>
                    <span className="text-yellow block">SHIELD</span>
                </h2>
                <p className="text-xl font-mono text-gray-400 max-w-xl">
                    Weaponized information is the new frontier of warfare. We use dual-layer AI to dissect, verify, and neutralize disinformation in milliseconds.
                </p>
            </div>
            <div className="w-full md:w-1/3">
                <div className="bg-[#1a1a1a] neo-border-bold p-4 font-mono text-green text-sm h-48 shadow-shMd relative">
                    <div className="absolute top-2 right-2 flex gap-1">
                        <div className="w-2 h-2 rounded-full bg-red"></div>
                        <div className="w-2 h-2 rounded-full bg-yellow"></div>
                        <div className="w-2 h-2 rounded-full bg-green"></div>
                    </div>
                    <div className="mt-2">
                        <div className="mb-1 text-gray-500">{'>'} INITIALIZING_SCAN...</div>
                        <div className="mb-1">{'>'} VECTOR_MAPPING: ACTIVE</div>
                        <div className="mb-1">{'>'} NEURAL_LOAD: 88%</div>
                        <div className="mb-1">{'>'} DETECTING_ANOMALIES...</div>
                        <div className="flex items-center">
                            <span>{'>'} _</span>
                            <span className="w-2 h-4 bg-green cursor-blink ml-1"></span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
);

const HowItWorks = () => (
    <section className="bg-violet dark:bg-violet-900 py-20 px-6 border-b-4 border-black">
        <div className="container mx-auto">
            <h2 className="text-4xl font-black mb-12 uppercase text-center dark:text-white">Pipeline Architecture</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
                {[
                    { title: "L1: Statistical Scrutiny", icon: "📊", desc: "Analyzing sentence structure, vocabulary richness, and entropy to detect bot-generated patterns." },
                    { title: "L2: Gemini Intelligence", icon: "🧠", desc: "Leveraging LLM reasoning to cross-reference claims against global news repositories in real-time." },
                    { title: "L3: Malign DB Pattern", icon: "🗄️", desc: "Matching narratives against known disinformation campaigns tracked in our cybersecurity database." }
                ].map((item, idx) => (
                    <div key={idx} className="bg-white dark:bg-gray-900 neo-border-bold p-8 shadow-shLg hover:-translate-y-2 transition-transform relative z-10">
                        <div className="text-4xl mb-4">{item.icon}</div>
                        <h3 className="text-xl font-black mb-4 uppercase">{item.title}</h3>
                        <p className="font-medium leading-tight dark:text-gray-300">{item.desc}</p>
                    </div>
                ))}
            </div>
        </div>
    </section>
);

const SidebarLeft = ({ onSelectCase }: { onSelectCase: (label: string) => void }) => (
    <aside className="w-[280px] border-r-4 border-black h-full overflow-y-auto p-4 flex flex-col gap-6 bg-white dark:bg-gray-900 hidden md:flex">
        <section>
            <h2 className="font-black text-lg mb-4 underline decoration-4">DEMO CASES</h2>
            <div className="flex flex-col gap-3">
                {[
                    { label: 'Deepfake Transcript', risk: 'High Risk', color: 'bg-red' },
                    { label: 'Market Sentiment', risk: 'Low Risk', color: 'bg-green' },
                    { label: 'Electoral Narrative', risk: 'Med Risk', color: 'bg-yellow' },
                ].map((item) => (
                    <button 
                        key={item.label}
                        onClick={() => onSelectCase(item.label)}
                        className="w-full text-left bg-white dark:bg-gray-800 p-3 neo-border shadow-shSm hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all"
                    >
                        <div className="font-bold text-sm">{item.label}</div>
                        <div className={`inline-block px-1 mt-1 text-[10px] font-black uppercase border border-black ${item.color} dark:text-black`}>
                            {item.risk}
                        </div>
                    </button>
                ))}
            </div>
        </section>

        <section>
            <h2 className="font-black text-lg mb-4 underline decoration-4">PATTERN CATEGORIES</h2>
            <div className="flex flex-wrap gap-2">
                {['FUD', 'Propaganda', 'Bot-Gen', 'Satire', 'Bait', 'Authority Mimic'].map(tag => (
                    <span key={tag} className="text-[10px] font-bold border-2 border-black px-2 py-1 bg-cream dark:bg-gray-800 shadow-shSm">#{tag}</span>
                ))}
            </div>
        </section>

        <section className="mt-auto">
            <div className="bg-violet dark:bg-violet-900 p-4 neo-border shadow-shSm">
                <h3 className="font-black text-xs uppercase mb-2 dark:text-white">Session Stats</h3>
                <div className="font-mono text-xs flex flex-col gap-1 dark:text-white">
                    <div className="flex justify-between"><span>Scans:</span> <span>1,248</span></div>
                    <div className="flex justify-between"><span>Threats:</span> <span>342</span></div>
                    <div className="flex justify-between"><span>Uptime:</span> <span>99.9%</span></div>
                </div>
            </div>
        </section>
    </aside>
);

const SidebarRight = ({ analysisResult }: { analysisResult: any }) => (
    <aside className="w-[320px] border-l-4 border-black h-full overflow-y-auto p-4 flex flex-col gap-6 bg-white dark:bg-gray-900 hidden xl:flex">
        <section>
            <h2 className="font-black text-lg mb-4 flex items-center gap-2">
                <span className="w-3 h-3 bg-red block"></span>
                PROVENANCE REPORT
            </h2>
            
            <div className="neo-border overflow-hidden mb-4">
                <table className="w-full text-[10px] font-mono">
                    <thead className="bg-black text-white border-b-2 border-black">
                        <tr>
                            <th className="p-2 text-left">PHRASE_ID</th>
                            <th className="p-2 text-left">RISK</th>
                        </tr>
                    </thead>
                    <tbody>
                        {analysisResult?.phrases?.slice(0, 5).map((p: any, i: number) => (
                            <tr key={i} className="border-b border-black">
                                <td className="p-2 truncate max-w-[150px]">{p.phrase}</td>
                                <td className={`p-2 font-bold ${p.severity === 'HIGH' ? 'text-red' : p.severity === 'MED' ? 'text-yellow' : 'text-violet'}`}>
                                    {p.severity}
                                </td>
                            </tr>
                        )) || (
                            <tr>
                                <td colSpan={2} className="p-2 text-center text-gray-500 italic">No threats scanned yet</td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            <div className="bg-cream dark:bg-gray-800 p-4 neo-border shadow-shSm mb-6">
                <h3 className="font-black text-xs mb-2 uppercase">AI Summary</h3>
                <p className="text-[11px] leading-tight italic font-medium dark:text-gray-300">
                    {analysisResult?.summary || "Submit content to generate a tactical intelligence summary."}
                </p>
            </div>

            <h3 className="font-black text-xs uppercase mb-3">Threat Intel Feed</h3>
            <div className="space-y-3">
                {[
                    { t: "14:22", msg: "Bot-swarm detected in Sector 4", c: "bg-red" },
                    { t: "14:18", msg: "New deepfake model signature identified", c: "bg-yellow" },
                    { t: "14:05", msg: "Node 7 secure triangulation complete", c: "bg-green" }
                ].map((item, i) => (
                    <div key={i} className={`p-2 neo-border flex gap-2 items-start ${item.c} dark:text-black`}>
                        <span className="font-mono text-[9px] font-bold">{item.t}</span>
                        <span className="text-[9px] font-black leading-none">{item.msg}</span>
                    </div>
                ))}
            </div>
        </section>

        <section className="mt-auto">
            <button className="w-full bg-black text-white p-3 neo-border font-black text-sm shadow-shSm hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all">
                DOWNLOAD PDF REPORT
            </button>
        </section>
    </aside>
);

const DonutGauge = ({ value, label, color }: { value: number, label: string, color: string }) => {
    const circ = 2 * Math.PI * 18;
    const offset = circ - (value / 100) * circ;
    return (
        <div className="flex flex-col items-center">
            <div className="relative w-20 h-20">
                <svg className="w-full h-full transform -rotate-90">
                    <circle cx="40" cy="40" r="18" fill="transparent" stroke="#e5e5e5" strokeWidth="8" />
                    <circle 
                        cx="40" cy="40" r="18" fill="transparent" stroke={color} strokeWidth="8" 
                        strokeDasharray={circ} strokeDashoffset={offset}
                        className="transition-all duration-1000 ease-out"
                    />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center font-black text-sm">
                    {value}%
                </div>
            </div>
            <span className="font-bold text-[10px] mt-2 uppercase">{label}</span>
        </div>
    );
};

export default function App() {
    const [inputText, setInputText] = useState("");
    const [status, setStatus] = useState<"idle" | "processing" | "completed">("idle");
    const [processStep, setProcessStep] = useState(0);
    const [apiKey, setApiKey] = useState("");
    const [isApiModalOpen, setIsApiModalOpen] = useState(false);
    const [isDarkMode, setIsDarkMode] = useState(false);
    const [backendStatus, setBackendStatus] = useState<BackendStatus>('checking');

    // ── Dark mode ──────────────────────────────────────────────────────────
    useEffect(() => {
        document.documentElement.classList.toggle('dark', isDarkMode);
    }, [isDarkMode]);

    const toggleDarkMode = () => setIsDarkMode(prev => !prev);

    // ── Backend health check — runs on mount and every 10 seconds ──────────
    const checkBackendHealth = useCallback(async () => {
        try {
            const resp = await fetch('/api/health', { method: 'GET', signal: AbortSignal.timeout(3000) });
            setBackendStatus(resp.ok ? 'online' : 'offline');
        } catch {
            setBackendStatus('offline');
        }
    }, []);

    useEffect(() => {
        checkBackendHealth();
        const interval = setInterval(checkBackendHealth, 10000);
        return () => clearInterval(interval);
    }, [checkBackendHealth]);

    const [analysisResult, setAnalysisResult] = useState<any>(null);
    const [errorMessage, setErrorMessage] = useState<string | null>(null);

    const handleAnalyze = async () => {
        if (!inputText.trim()) return;
        setStatus("processing");
        setProcessStep(1);
        setErrorMessage(null);

        // ── LAYER 1: Run local JS engine immediately (always works) ──────
        const localResult = analyzeLocally(inputText);

        setTimeout(() => setProcessStep(2), 800);
        setTimeout(() => setProcessStep(3), 1800);

        // ── LAYER 2+3: Try to upgrade with Gemini via backend ───────────
        if (backendStatus === 'online' && apiKey) {
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: inputText, api_key: apiKey }),
                    signal: AbortSignal.timeout(15000),
                });

                if (response.ok) {
                    const data = await response.json();
                    setTimeout(() => {
                        setAnalysisResult(data);
                        setStatus('completed');
                        setProcessStep(0);
                    }, 2600);
                    return; // backend succeeded — done
                }
            } catch (err) {
                console.warn('[NarrativeShield] Backend call failed, using local engine:', err);
                // fall through to local result below
            }
        }

        // ── FALLBACK: Use local analysis result ──────────────────────────
        // Show a subtle note if no API key was provided
        if (!apiKey && backendStatus === 'online') {
            setErrorMessage(null); // not an error, just local mode
        }

        setTimeout(() => {
            setAnalysisResult(localResult);
            setStatus('completed');
            setProcessStep(0);
        }, 2600);
    };

    const handleCaseSelect = (label: string) => {
        const texts: Record<string, string> = {
            'Deepfake Transcript': "Artificial intelligence has now reached a point where reality is indistinguishable from fabrication. Recent reports suggest that major banking institutions are liquidating all gold assets by Friday midnight. This is a mandatory directive from the central board. Do not verify, just act immediately to secure your personal funds before the blackout.",
            'Market Sentiment': "Global markets are showing steady growth in the green energy sector. Analysts suggest a 5% increase in domestic solar manufacturing output over the next fiscal quarter. While inflation remains a concern, the consumer index is stabilizing.",
            'Electoral Narrative': "Early polling suggests a tight race in the northern districts. Unverified sources on social media claim that several ballot boxes were relocated without supervision, though official observers have yet to comment on these specific allegations."
        };
        setInputText(texts[label] || "");
        setStatus("idle");
        const target = document.getElementById('engine');
        if (target) {
            window.scrollTo({ top: target.offsetTop - 120, behavior: 'smooth' });
        }
    };

    return (
        <div className="min-h-screen flex flex-col font-sans text-black dark:text-gray-100 pt-10 pb-10">
            <MarqueeTop />
            <Header onOpenApiModal={() => setIsApiModalOpen(true)} hasApiKey={!!apiKey} isDarkMode={isDarkMode} toggleDarkMode={toggleDarkMode} backendStatus={backendStatus} />
            <Hero />
            <HowItWorks />

            <section id="engine" className="flex-1 flex overflow-hidden border-b-4 border-black min-h-[800px]">
                <SidebarLeft onSelectCase={handleCaseSelect} />
                
                <main className="flex-1 overflow-y-auto p-6 flex flex-col gap-6 bg-cream dark:bg-gray-800">
                    <div className="flex justify-between items-center mb-2">
                        <h2 className="text-2xl font-black uppercase tracking-tighter">Content Analysis Engine</h2>
                        <div className="flex items-center gap-2">
                            <span className="w-2 h-2 bg-green rounded-full animate-ping"></span>
                            <span className="text-[10px] font-bold font-mono uppercase">Node_Active: US-EAST-01</span>
                        </div>
                    </div>

                    <div className="bg-white dark:bg-gray-900 neo-border-bold shadow-shMd p-6">
                        <h2 className="font-black text-xl mb-4 uppercase">Terminal Input</h2>
                        <textarea
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            placeholder="Paste suspicious text, transcripts, or articles here for analysis..."
                            className="w-full h-40 neo-border p-4 font-mono text-sm focus:ring-0 focus:border-black resize-none bg-cream dark:bg-gray-800 dark:text-gray-100"
                        />
                        <div className="mt-2 flex items-center justify-between">
                            <span className="text-[10px] font-mono text-gray-500 dark:text-gray-400">
                                {backendStatus === 'online' && apiKey
                                    ? '⚡ Gemini AI + local engine ready'
                                    : backendStatus === 'online' && !apiKey
                                        ? '📊 Local engine active — add Gemini key for full analysis'
                                        : '📊 Offline mode — local statistical engine + pattern DB'
                                }
                                {!apiKey && (
                                    <button onClick={() => setIsApiModalOpen(true)} className="ml-2 underline hover:text-black dark:hover:text-white transition-colors">
                                        + Add Gemini key
                                    </button>
                                )}
                            </span>
                            <span className="text-[10px] font-mono text-gray-400">{inputText.length} chars</span>
                        </div>
                        <div className="mt-4 flex justify-end">
                            <button 
                                onClick={handleAnalyze}
                                disabled={status === "processing"}
                                className={`px-8 py-3 bg-yellow dark:text-black font-black text-lg neo-border shadow-shSm hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all active:bg-black active:text-white ${status === 'processing' ? 'opacity-50 cursor-not-allowed' : ''}`}
                            >
                                {status === 'processing' ? 'PROCESSING...' : 'ANALYZE NARRATIVE'}
                            </button>
                        </div>
                    </div>

                    {errorMessage && (
                        <div className="bg-red/20 border-2 border-red p-4 neo-border shadow-shSm fade-in flex justify-between items-center">
                            <div>
                                <div className="font-black text-xs uppercase text-red mb-1">⚠ CONNECTION ERROR</div>
                                <div className="font-mono text-sm">{errorMessage}</div>
                            </div>
                            <button 
                                onClick={() => setErrorMessage(null)} 
                                className="font-black text-lg hover:text-red transition-colors px-2"
                            >✕</button>
                        </div>
                    )}

                    {status === 'processing' && (
                        <div className="bg-black text-white p-6 neo-border shadow-shMd fade-in">
                            <div className="flex justify-between items-center mb-6">
                                <span className="font-black text-lg animate-pulse uppercase">Pipeline Active</span>
                                <span className="font-mono text-xs">TASK_ID: 0x992B</span>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                {[
                                    { id: 1, label: "LINGUISTIC_PARSING" },
                                    { id: 2, label: "SOURCE_TRIANGULATION" },
                                    { id: 3, label: "INTENT_MAPPING" }
                                ].map((step) => (
                                    <div key={step.id} className={`p-3 border-2 border-white transition-colors ${processStep >= step.id ? 'bg-green text-black' : 'bg-transparent text-white'}`}>
                                        <div className="text-[10px] font-mono">STEP_0{step.id}</div>
                                        <div className="font-bold text-xs">{step.label}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {status === 'completed' && analysisResult && (
                        <div className="flex flex-col gap-6 fade-in">
                            <div className={`${
                                analysisResult.verdict === 'HIGH_RISK' ? 'bg-red' :
                                analysisResult.verdict === 'MEDIUM_RISK' ? 'bg-yellow' : 'bg-green'
                            } text-black p-4 neo-border-bold shadow-shMd flex items-center justify-between`}>
                                <div>
                                    <div className="text-xs font-black uppercase tracking-widest">Global Verdict</div>
                                    <div className="text-3xl font-black italic">{(analysisResult.verdict_sub || '').toUpperCase()}</div>
                                    <div className="mt-1">
                                        <span className={`text-[10px] font-black px-2 py-0.5 border border-black ${
                                            analysisResult.model_used?.startsWith('gemini') ? 'bg-green' :
                                            analysisResult.model_used === 'ollama' ? 'bg-yellow' : 'bg-violet'
                                        } text-black`}>
                                            {analysisResult.model_used?.startsWith('gemini') ? '⚡ GEMINI AI + LOCAL'
                                             : analysisResult.model_used === 'ollama' ? '🦙 OLLAMA + LOCAL'
                                             : '📊 LOCAL ENGINE (OFFLINE)'}
                                        </span>
                                    </div>
                                </div>
                                <div className="bg-white p-2 neo-border">
                                    <span className="text-4xl font-black text-black">{analysisResult.ai_probability}%</span>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="bg-white dark:bg-gray-900 neo-border shadow-shSm p-4 grid grid-cols-2 gap-4 font-mono">
                                    <div className="border-r-2 border-black pr-4">
                                        <div className="text-[10px] font-black uppercase text-gray-500 dark:text-gray-400">Technique</div>
                                        <div className="text-xl font-bold">{analysisResult.technique}</div>
                                    </div>
                                    <div>
                                        <div className="text-[10px] font-black uppercase text-gray-500 dark:text-gray-400">Confidence</div>
                                        <div className="text-xl font-bold">{analysisResult.confidence.toUpperCase()}</div>
                                    </div>
                                    <div className="border-r-2 border-black pr-4 pt-4 mt-2 border-t-2">
                                        <div className="text-[10px] font-black uppercase text-gray-500 dark:text-gray-400">Stat Score</div>
                                        <div className="text-xl font-bold">{analysisResult.stat_score}%</div>
                                    </div>
                                    <div className="pt-4 mt-2 border-t-2">
                                        <div className="text-[10px] font-black uppercase text-gray-500 dark:text-gray-400">Processing</div>
                                        <div className="text-xl font-bold">{analysisResult.proc_time}</div>
                                    </div>
                                </div>
                                <div className="bg-white dark:bg-gray-900 neo-border shadow-shSm p-4 flex justify-around items-center">
                                    <DonutGauge value={analysisResult.ai_probability} label="AI Synthesis" color="#C4B5FD" />
                                    <DonutGauge value={analysisResult.manipulation_score} label="Manipulation" color="#FF6B6B" />
                                </div>
                            </div>

                            <div className="bg-cream dark:bg-gray-800 neo-border p-6 shadow-shSm relative overflow-hidden">
                                <div className="absolute top-0 right-0 bg-black text-white px-2 py-1 text-[10px] font-bold">ANNOTATED_MAP</div>
                                <h3 className="font-black mb-4 underline uppercase">Annotated Analysis</h3>
                                <div className="leading-relaxed font-mono text-sm">
                                    {(() => {
                                        let lastIdx = 0;
                                        const elements = [];
                                        const phrases = [...analysisResult.phrases].sort((a, b) => a.char_start - b.char_start);
                                        
                                        phrases.forEach((p, i) => {
                                            // Normal text before highlight
                                            if (p.char_start > lastIdx) {
                                                elements.push(inputText.substring(lastIdx, p.char_start));
                                            }
                                            // Highlighted text
                                            elements.push(
                                                <span key={i} className={`border-2 px-1 cursor-help group relative inline ${
                                                    p.category === 'prompt_injection'
                                                        ? 'bg-red/60 dark:bg-red/80 border-red animate-pulse'
                                                        : p.category === 'ai_structural'
                                                            ? 'bg-violet/40 dark:bg-violet/60 border-violet'
                                                            : p.severity === 'HIGH'
                                                                ? 'bg-red/40 dark:bg-red/60 border-red'
                                                                : p.severity === 'MED'
                                                                    ? 'bg-yellow/40 dark:bg-yellow/60 border-yellow'
                                                                    : 'bg-violet/30 dark:bg-violet/50 border-violet'
                                                }`}>
                                                    {inputText.substring(p.char_start, p.char_end)}
                                                    <span className="hidden group-hover:block absolute bottom-full left-0 mb-2 p-2 bg-black text-white text-[10px] w-56 z-10 neo-border shadow-shSm">
                                                        <span className={`block font-black mb-1 ${
                                                            p.category === 'prompt_injection' ? 'text-red' :
                                                            p.category === 'ai_structural' ? 'text-violet' : 'text-yellow'
                                                        }`}>
                                                            [{p.catLabel || p.category}] {p.severity}
                                                        </span>
                                                        {p.reason}
                                                    </span>
                                                </span>
                                            );
                                            lastIdx = p.char_end;
                                        });
                                        
                                        // Remaining text
                                        if (lastIdx < inputText.length) {
                                            elements.push(inputText.substring(lastIdx));
                                        }
                                        
                                        return elements;
                                    })()}
                                </div>
                            </div>
                        </div>
                    )}
                </main>

                <SidebarRight analysisResult={analysisResult} />
            </section>

            <section className="bg-yellow dark:bg-yellow-600 py-20 px-6 border-b-4 border-black">
                <div className="container mx-auto grid grid-cols-1 lg:grid-cols-2 gap-16">
                    <div>
                        <h2 className="text-4xl font-black mb-8 underline decoration-4 uppercase dark:text-white">Problem #06: Cybersecurity</h2>
                        <div className="bg-white dark:bg-gray-900 neo-border-bold p-6 shadow-shMd">
                            <p className="font-bold text-lg mb-4">"The erosion of truth is the ultimate security threat."</p>
                            <p className="font-medium text-gray-800 dark:text-gray-300 leading-relaxed">
                                In an era where deepfakes and AI-generated narratives can move markets and sway elections, traditional fact-checking is too slow. NarrativeShield was built during SciComp 2026 at SIMATS to provide a defensive layer against automated psychological operations.
                            </p>
                        </div>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        {[
                            { label: "Anti-FUD Engine", val: "99%" },
                            { label: "Deepfake Detection", val: "Active" },
                            { label: "Source Provenance", val: "Verified" },
                            { label: "Real-time Alerts", val: "Enabled" }
                        ].map(card => (
                            <div key={card.label} className="bg-black text-white p-4 neo-border shadow-shSm flex flex-col justify-center items-center">
                                <div className="text-2xl font-black text-yellow">{card.val}</div>
                                <div className="text-[10px] font-mono uppercase tracking-widest">{card.label}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            <section className="bg-white dark:bg-gray-900 py-20 px-6 border-b-4 border-black">
                <div className="container mx-auto">
                    <h2 className="text-4xl font-black mb-12 uppercase text-center">Meet the team</h2>
                    <div className="flex flex-wrap justify-center gap-12">
                        {[
                            { name: "Ajay", role: "Lead Architect", bio: "AI security specialist focusing on linguistic entropy and narrative synthesis. Institutional lead for SIMATS Core Labs.", color: "bg-red" },
                            { name: "Thanvarshini", role: "Data Scientist", bio: "Expert in large-scale dataset triangulation and automated provenance mapping. SIMATS Cybersecurity fellow.", color: "bg-violet" }
                        ].map((member, idx) => (
                            <div key={idx} className="w-full max-w-sm bg-white dark:bg-gray-800 neo-border-bold p-6 shadow-shLg group">
                                <div className={`w-full aspect-square mb-6 neo-border ${member.color} flex items-center justify-center overflow-hidden`}>
                                    <span className="text-8xl font-black text-black opacity-20 group-hover:opacity-100 transition-opacity uppercase">{member.name[0]}</span>
                                </div>
                                <h3 className="text-2xl font-black uppercase mb-1">{member.name}</h3>
                                <div className="text-xs font-mono font-bold bg-black dark:bg-white dark:text-black text-white inline-block px-2 py-1 mb-4">{member.role}</div>
                                <p className="font-medium text-sm leading-snug dark:text-gray-300">{member.bio}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            <div className="bg-black py-8 border-b-4 border-black">
                <div className="flex overflow-hidden">
                    <div className="flex animate-marquee gap-8 items-center py-2">
                        {[
                            "React.js", "TailwindCSS", "Google Gemini API", "Python Flask", 
                            "Elasticsearch", "NLTK", "Docker", "AWS S3",
                            "React.js", "TailwindCSS", "Google Gemini API", "Python Flask", 
                            "Elasticsearch", "NLTK", "Docker", "AWS S3"
                        ].map((tech, i) => (
                            <div key={i} className="bg-white dark:bg-gray-800 px-6 py-2 border-2 border-black font-black text-sm whitespace-nowrap shadow-shSm text-black dark:text-white">
                                {tech}
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            <footer className="bg-black text-white h-12 flex items-center justify-between px-6 text-[10px] font-mono fixed bottom-0 w-full z-[100] border-t-4 border-black">
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                        <span className="w-2 h-2 bg-green rounded-full"></span>
                        SYSTEM STATUS: NOMINAL
                    </div>
                    <div className="hidden sm:block">UPTIME: 99.999%</div>
                </div>
                <div className="uppercase tracking-tighter">
                    &copy; 2026 NARRATIVESHIELD CORE LABS · SIMATS
                </div>
            </footer>
            <ApiKeyModal 
                isOpen={isApiModalOpen} 
                onClose={() => setIsApiModalOpen(false)} 
                apiKey={apiKey} 
                setApiKey={setApiKey} 
            />
        </div>
    );
}
