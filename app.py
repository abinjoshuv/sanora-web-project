import React, { useState, useEffect } from 'react';
import { initializeApp } from 'firebase/app';
import { 
  getAuth, 
  signInAnonymously, 
  signInWithCustomToken, 
  onAuthStateChanged 
} from 'firebase/auth';
import { 
  getFirestore, 
  collection, 
  doc, 
  addDoc, 
  onSnapshot, 
  deleteDoc 
} from 'firebase/firestore';
import { 
  Menu, 
  X, 
  ChevronRight, 
  Layout, 
  Home, 
  Users, 
  Settings, 
  Plus, 
  Trash2, 
  LogOut,
  Image as ImageIcon,
  CheckCircle,
  ArrowRight,
  Leaf,
  Compass,
  Sparkles,
  Wand2,
  Loader2
} from 'lucide-react';

// --- Firebase Configuration ---
const firebaseConfig = JSON.parse(__firebase_config);
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const appId = typeof __app_id !== 'undefined' ? __app_id : 'sanora-interior-organic';
const apiKey = ""; // Provided by environment

/**
 * SANORA LOGO: 
 */
const SanoraLogo = ({ className = "h-12", dark = false }) => (
  <div className={`flex items-center gap-4 ${className} group cursor-pointer`}>
    <div className="relative w-12 h-12 flex items-center justify-center">
      <div className="absolute inset-0 bg-[#C4A484] rounded-xl rotate-3 opacity-20 group-hover:rotate-6 transition-transform"></div>
      <svg viewBox="0 0 24 24" className="w-8 h-8 relative z-10 drop-shadow-sm" fill="none">
        <path d="M12 3L4 7V17L12 21L20 17V7L12 3Z" stroke="#84A98C" strokeWidth="2.5" strokeLinejoin="round"/>
        <path d="M12 3V21M4 7L12 11L20 7" stroke="#84A98C" strokeWidth="1.5" strokeLinejoin="round"/>
        <path d="M12 11L12 11.5" stroke="#C5A059" strokeWidth="4" strokeLinecap="round"/>
      </svg>
    </div>
    <div className="flex flex-col">
      <span className={`text-2xl font-light tracking-tight ${dark ? 'text-white' : 'text-slate-800'}`}>
        SANORA<span className="font-bold text-[#84A98C]">.</span>
      </span>
      <span className={`text-[10px] font-bold tracking-[0.4em] uppercase ${dark ? 'text-[#C5A059]' : 'text-[#8B7355]'}`}>
        Interior Atelier
      </span>
    </div>
  </div>
);

// --- Gemini API Helper ---
async function callGemini(prompt, systemPrompt) {
  let retries = 0;
  const maxRetries = 5;
  
  while (retries < maxRetries) {
    try {
      const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          systemInstruction: { parts: [{ text: systemPrompt }] }
        })
      });
      
      if (!response.ok) throw new Error('API failed');
      const data = await response.json();
      return data.candidates?.[0]?.content?.parts?.[0]?.text;
    } catch (err) {
      retries++;
      await new Promise(r => setTimeout(r, Math.pow(2, retries) * 1000));
    }
  }
  throw new Error('Failed to generate content after retries.');
}

export default function App() {
  const [user, setUser] = useState(null);
  const [view, setView] = useState('home'); 
  const [projects, setProjects] = useState([]);
  const [services, setServices] = useState([]);
  const [leads, setLeads] = useState([]);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  useEffect(() => {
    const initAuth = async () => {
      try {
        if (typeof __initial_auth_token !== 'undefined' && __initial_auth_token) {
          await signInWithCustomToken(auth, __initial_auth_token);
        } else {
          await signInAnonymously(auth);
        }
      } catch (err) { console.error(err); }
    };
    initAuth();
    const unsubscribe = onAuthStateChanged(auth, setUser);
    return () => unsubscribe();
  }, []);

  useEffect(() => {
    if (!user) return;
    const qProjects = collection(db, 'artifacts', appId, 'public', 'data', 'projects');
    const unsubP = onSnapshot(qProjects, (s) => setProjects(s.docs.map(d => ({id: d.id, ...d.data()})).length ? s.docs.map(d => ({id: d.id, ...d.data()})) : defaultProjects), err => console.error(err));
    
    const qServices = collection(db, 'artifacts', appId, 'public', 'data', 'services');
    const unsubS = onSnapshot(qServices, (s) => setServices(s.docs.map(d => ({id: d.id, ...d.data()})).length ? s.docs.map(d => ({id: d.id, ...d.data()})) : defaultServices), err => console.error(err));

    const qLeads = collection(db, 'artifacts', appId, 'public', 'data', 'leads');
    const unsubL = onSnapshot(qLeads, (s) => setLeads(s.docs.map(d => ({id: d.id, ...d.data()}))), err => console.error(err));

    return () => { unsubP(); unsubS(); unsubL(); };
  }, [user]);

  if (view === 'admin') return <AdminDashboard user={user} projects={projects} services={services} leads={leads} onExit={() => setView('home')} />;

  return (
    <div className="min-h-screen bg-white text-slate-800 font-sans">
      {/* Navigation */}
      <nav className="fixed w-full bg-white/90 backdrop-blur-md z-50 border-b border-slate-100 h-24">
        <div className="max-w-7xl mx-auto px-6 h-full flex justify-between items-center">
          <SanoraLogo />
          
          <div className="hidden md:flex items-center gap-12">
            {['Projects', 'Services', 'Contact'].map((item) => (
              <a key={item} href={`#${item.toLowerCase()}`} className="text-xs font-bold uppercase tracking-widest text-slate-500 hover:text-[#84A98C] transition-colors">{item}</a>
            ))}
            <button onClick={() => setView('admin')} className="bg-[#C5A059] text-white px-8 py-3 rounded-full text-xs font-bold uppercase tracking-widest hover:bg-[#84A98C] transition-all">
              Studio Portal
            </button>
          </div>

          <button className="md:hidden" onClick={() => setIsMenuOpen(!isMenuOpen)}>
            {isMenuOpen ? <X size={28} /> : <Menu size={28} />}
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative h-screen flex items-center pt-24">
        <div className="absolute inset-0 z-0 overflow-hidden">
          <img 
            src="https://images.unsplash.com/photo-1615874959474-d609969a20ed?auto=format&fit=crop&q=80&w=2000" 
            className="w-full h-full object-cover" 
            alt="Organic Interior"
          />
          <div className="absolute inset-0 bg-white/40"></div>
          <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-[#84A98C]/10 rounded-full blur-[100px]"></div>
        </div>
        
        <div className="relative z-10 max-w-7xl mx-auto px-6 w-full">
          <div className="max-w-3xl">
            <span className="inline-block text-[#C5A059] font-bold text-xs uppercase tracking-[0.5em] mb-6">SANORA DESIGN STUDIO</span>
            <h1 className="text-6xl md:text-8xl font-light text-slate-900 leading-[1.1] mb-8">
              Bespoke <br /> 
              <span className="font-serif italic text-[#84A98C]">Organic Luxury.</span>
            </h1>
            <p className="text-lg text-slate-600 mb-10 max-w-lg leading-relaxed border-l-2 border-[#C5A059] pl-6">
              Interweaving natural oak finishes with antique brass and fresh yellow-green hues to create SANORA living sanctuaries.
            </p>
            <div className="flex gap-4">
              <a href="#contact" className="bg-[#84A98C] text-white px-10 py-5 rounded-full font-bold uppercase tracking-widest text-xs flex items-center gap-3 hover:bg-[#C5A059] transition-all">
                Book Consultation <ArrowRight size={16} />
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Services Grid */}
      <section id="services" className="py-32 bg-[#F9F7F2]">
        <div className="max-w-7xl mx-auto px-6 grid md:grid-cols-3 gap-16">
          <div className="md:col-span-1">
            <h2 className="text-4xl font-light text-slate-900 mb-6 tracking-tight leading-tight">SANORA Crafts the <span className="font-serif italic text-[#C5A059]">Soul</span> of Home.</h2>
            <div className="w-16 h-1 bg-[#84A98C] mb-8"></div>
            <p className="text-slate-500 text-sm leading-relaxed mb-8">Our signature methodology focuses on the tactile experience of wood, the warmth of antique finishes, and the energy of biophilic color palettes.</p>
            <div className="p-8 bg-white rounded-3xl border border-slate-100 shadow-sm">
              <Leaf className="text-[#84A98C] mb-4" />
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">Biophilic Standard</p>
              <p className="text-slate-700 font-medium mt-1">Sustainability integrated into every grain of wood.</p>
            </div>
          </div>
          
          <div className="md:col-span-2 grid sm:grid-cols-2 gap-8">
            {services.map((s) => (
              <div key={s.id} className="bg-white p-10 rounded-[2.5rem] shadow-sm hover:shadow-xl transition-all group border border-slate-100">
                <div className="w-12 h-12 rounded-2xl bg-[#84A98C]/10 flex items-center justify-center text-[#84A98C] mb-8 group-hover:bg-[#84A98C] group-hover:text-white transition-all">
                  <Compass size={24} />
                </div>
                <h3 className="text-2xl font-bold mb-4 text-slate-900 tracking-tight">{s.title}</h3>
                <p className="text-slate-500 text-sm leading-relaxed">{s.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* AI Concept Section (New Integration) */}
      <section className="py-32 bg-white">
        <div className="max-w-4xl mx-auto px-6 text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#84A98C]/10 text-[#84A98C] text-[10px] font-bold uppercase tracking-widest mb-6">
                <Sparkles size={14} /> New AI Concept Engine
            </div>
            <h2 className="text-5xl font-light text-slate-900 mb-8 leading-tight">Can't describe your vision? <br/><span className="italic font-serif">Let us architect it.</span></h2>
            <p className="text-slate-500 mb-12 leading-relaxed">Type a few words about your dream room—mood, materials, or even a feeling—and SANORA's Vision Architect will draft a professional interior concept for you.</p>
            <AIConceptGenerator />
        </div>
      </section>

      {/* Portfolio Gallery */}
      <section id="projects" className="py-32 bg-[#F9F7F2]">
        <div className="max-w-7xl mx-auto px-6 mb-20 text-center">
          <h2 className="text-5xl font-light text-slate-900 tracking-tight">Curation of <span className="font-serif italic">Natural Spaces</span></h2>
        </div>
        
        <div className="max-w-[1600px] mx-auto px-6 grid grid-cols-1 md:grid-cols-12 gap-6">
          {projects.map((p, i) => (
            <div key={p.id} className={`relative group overflow-hidden rounded-[2rem] bg-slate-100 ${i === 0 ? 'md:col-span-7 aspect-video' : i === 1 ? 'md:col-span-5 aspect-[4/5]' : 'md:col-span-4 aspect-square'}`}>
              <img src={p.image} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-1000" alt={p.name} />
              <div className="absolute inset-0 bg-gradient-to-t from-slate-900/60 to-transparent flex flex-col justify-end p-10 opacity-0 group-hover:opacity-100 transition-opacity">
                <span className="text-[#84A98C] font-bold text-xs uppercase tracking-widest mb-2">{p.location}</span>
                <h4 className="text-white text-3xl font-bold tracking-tight">{p.name}</h4>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="py-32 bg-slate-900 relative overflow-hidden">
        <div className="absolute inset-0 opacity-10 bg-[url('https://www.transparenttextures.com/patterns/wood-pattern.png')]"></div>
        <div className="max-w-7xl mx-auto px-6 grid lg:grid-cols-2 gap-24 relative z-10">
          <div className="text-white">
            <h2 className="text-6xl font-light leading-tight mb-12 tracking-tight">Your <span className="text-[#C5A059]">SANORA</span> legacy begins here.</h2>
            <div className="space-y-12">
              <div className="flex gap-8 items-start">
                <div className="w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-[#84A98C]"><Users size={24} /></div>
                <div><h4 className="font-bold text-[#C5A059] uppercase tracking-widest text-xs mb-2">Visit Atelier</h4><p className="text-xl text-slate-300">Design District, Level 4, Studio 12</p></div>
              </div>
              <div className="flex gap-8 items-start">
                <div className="w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-[#84A98C]"><Leaf size={24} /></div>
                <div><h4 className="font-bold text-[#C5A059] uppercase tracking-widest text-xs mb-2">Organic Consulting</h4><p className="text-xl text-slate-300">+91 98765 43210</p></div>
              </div>
            </div>
          </div>
          <div className="bg-white p-12 rounded-[3rem] shadow-2xl">
            <LeadForm user={user} />
          </div>
        </div>
      </section>

      <footer className="py-20 bg-white text-center">
        <SanoraLogo className="mx-auto mb-12" />
        <div className="flex justify-center gap-12 text-[10px] font-bold uppercase tracking-[0.3em] text-slate-400">
          <a href="#" className="hover:text-[#84A98C]">Instagram</a>
          <a href="#" className="hover:text-[#84A98C]">LinkedIn</a>
          <a href="#" className="hover:text-[#84A98C]">Privacy</a>
          <button onClick={() => setView('admin')} className="hover:text-[#C5A059]">Admin</button>
        </div>
        <p className="mt-12 text-[10px] text-slate-300 font-bold uppercase tracking-widest">© 2024 SANORA Interior Atelier.</p>
      </footer>
    </div>
  );
}

function AIConceptGenerator() {
    const [prompt, setPrompt] = useState("");
    const [result, setResult] = useState("");
    const [loading, setLoading] = useState(false);

    const generate = async () => {
        if (!prompt) return;
        setLoading(true);
        try {
            const systemPrompt = "You are SANORA's lead interior architect. Based on the user's brief, provide a sophisticated design concept including: 1. A poetic name for the space. 2. A 3-sentence description of the atmosphere. 3. Suggested materials (mention wood types, antique finishes). 4. A specific biophilic color accent (like wasabi, olive, or sage). Keep it professional and architectural.";
            const res = await callGemini(prompt, systemPrompt);
            setResult(res);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="bg-[#F9F7F2] p-8 rounded-[3rem] text-left border border-slate-100 shadow-inner">
            <div className="flex flex-col md:flex-row gap-4 mb-6">
                <input 
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="e.g. A sun-drenched library with a view of the forest..."
                    className="flex-1 bg-white p-5 rounded-2xl outline-none border border-slate-100 text-slate-600 italic"
                />
                <button 
                    onClick={generate}
                    disabled={loading}
                    className="bg-[#84A98C] text-white px-8 py-5 rounded-2xl font-bold uppercase tracking-widest text-[10px] flex items-center justify-center gap-2 hover:bg-[#C5A059] transition-all disabled:opacity-50"
                >
                    {loading ? <Loader2 className="animate-spin" size={16} /> : <Wand2 size={16} />}
                    ✨ Generate Vision
                </button>
            </div>
            {result && (
                <div className="bg-white p-8 rounded-2xl border border-slate-100 animate-in fade-in slide-in-from-bottom-4">
                    <div className="prose prose-slate prose-sm max-w-none whitespace-pre-wrap text-slate-600 leading-relaxed font-serif">
                        {result}
                    </div>
                </div>
            )}
        </div>
    )
}

function AdminDashboard({ user, projects, services, leads, onExit }) {
  const [activeTab, setActiveTab] = useState('projects');
  const [isAdding, setIsAdding] = useState(false);
  const [formData, setFormData] = useState({});

  const handleAddProject = async (e) => {
    e.preventDefault();
    if (!user) return;
    try {
      await addDoc(collection(db, 'artifacts', appId, 'public', 'data', 'projects'), { ...formData, createdAt: Date.now() });
      setIsAdding(false);
      setFormData({});
    } catch (err) { console.error(err); }
  };

  const deleteItem = async (col, id) => {
    if (!user) return;
    try {
      await deleteDoc(doc(db, 'artifacts', appId, 'public', 'data', col, id));
    } catch (err) { console.error(err); }
  };

  return (
    <div className="min-h-screen bg-[#F9F7F2] flex">
      <aside className="w-72 bg-white p-10 border-r border-slate-100 hidden lg:flex flex-col">
        <SanoraLogo className="mb-20" />
        <nav className="space-y-4 flex-1">
          {['projects', 'services', 'leads'].map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`w-full text-left p-4 rounded-2xl text-xs font-bold uppercase tracking-widest transition-all ${activeTab === t ? 'bg-[#84A98C] text-white shadow-lg shadow-[#84A98C]/20' : 'text-slate-400 hover:bg-slate-50'}`}>
              {t}
            </button>
          ))}
        </nav>
        <button onClick={onExit} className="flex items-center gap-3 text-slate-400 hover:text-red-500 font-bold uppercase text-[10px] tracking-widest">
          <LogOut size={14} /> Close Portal
        </button>
      </aside>

      <main className="flex-1 p-12 overflow-y-auto h-screen">
        <div className="flex justify-between items-center mb-12">
          <h1 className="text-3xl font-light text-slate-900 tracking-tight uppercase tracking-[0.2em]">{activeTab}</h1>
          {activeTab === 'projects' && (
            <button onClick={() => setIsAdding(true)} className="bg-[#C5A059] text-white px-8 py-3 rounded-full text-[10px] font-bold uppercase tracking-widest">
              Add Record
            </button>
          )}
        </div>

        {activeTab === 'projects' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {projects.map(p => (
              <div key={p.id} className="bg-white rounded-[2rem] overflow-hidden border border-slate-100 shadow-sm group">
                <div className="h-56 overflow-hidden"><img src={p.image} className="w-full h-full object-cover" /></div>
                <div className="p-8">
                  <div className="flex justify-between items-center mb-4">
                    <div>
                        <h4 className="font-bold text-slate-900">{p.name}</h4>
                        <p className="text-[10px] font-bold text-[#84A98C] tracking-widest uppercase">{p.location}</p>
                    </div>
                    <button onClick={() => deleteItem('projects', p.id)} className="text-slate-200 hover:text-red-500"><Trash2 size={18} /></button>
                  </div>
                  <AIAssistant project={p} />
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'leads' && (
          <div className="bg-white rounded-[2rem] shadow-sm border border-slate-100 overflow-hidden">
            <table className="w-full text-left">
              <thead className="bg-[#F9F7F2]">
                <tr>
                  <th className="p-6 text-[10px] font-bold uppercase tracking-widest text-slate-400">Client</th>
                  <th className="p-6 text-[10px] font-bold uppercase tracking-widest text-slate-400">Contact</th>
                  <th className="p-6 text-[10px] font-bold uppercase tracking-widest text-slate-400 text-right">Action</th>
                </tr>
              </thead>
              <tbody>
                {leads.map(l => (
                  <tr key={l.id} className="border-t border-slate-50">
                    <td className="p-6 font-bold text-slate-900">{l.name}</td>
                    <td className="p-6 text-sm text-slate-500">{l.email} / {l.phone}</td>
                    <td className="p-6 text-right"><button onClick={() => deleteItem('leads', l.id)} className="text-red-500"><Trash2 size={16} /></button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {isAdding && (
          <div className="fixed inset-0 bg-slate-950/60 backdrop-blur-sm z-[100] flex items-center justify-center p-6">
            <div className="bg-white w-full max-w-md rounded-[3rem] p-12">
              <h2 className="text-2xl font-light mb-8 text-slate-900 tracking-tight uppercase tracking-widest">New Entry</h2>
              <form onSubmit={handleAddProject} className="space-y-6">
                <input required type="text" placeholder="Project Title" onChange={e => setFormData({...formData, name: e.target.value})} className="w-full bg-[#F9F7F2] p-4 rounded-2xl outline-none" />
                <input required type="text" placeholder="Region/City" onChange={e => setFormData({...formData, location: e.target.value})} className="w-full bg-[#F9F7F2] p-4 rounded-2xl outline-none" />
                <input required type="url" placeholder="Visual URL" onChange={e => setFormData({...formData, image: e.target.value})} className="w-full bg-[#F9F7F2] p-4 rounded-2xl outline-none" />
                <div className="flex gap-4 pt-4">
                  <button type="button" onClick={() => setIsAdding(false)} className="flex-1 p-4 bg-slate-100 rounded-2xl font-bold text-[10px] uppercase">Cancel</button>
                  <button type="submit" className="flex-1 p-4 bg-[#84A98C] text-white rounded-2xl font-bold text-[10px] uppercase">Publish</button>
                </div>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

// AI Assistant for Admin to generate descriptions
function AIAssistant({ project }) {
    const [loading, setLoading] = useState(false);
    const [suggestion, setSuggestion] = useState("");

    const generateBlurb = async () => {
        setLoading(true);
        try {
            const prompt = `Write a short, luxury-focused marketing blurb for a project named "${project.name}" located in "${project.location}". Focus on organic materials and high-end design.`;
            const system = "You are a professional architectural copywriter. Write exactly two sentences. Be elegant and sophisticated.";
            const res = await callGemini(prompt, system);
            setSuggestion(res);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="mt-4 pt-4 border-t border-slate-50">
            <button 
                onClick={generateBlurb}
                disabled={loading}
                className="text-[9px] font-bold uppercase tracking-[0.2em] text-[#C5A059] flex items-center gap-2 hover:text-[#84A98C] transition-colors"
            >
                {loading ? <Loader2 className="animate-spin" size={10} /> : <Sparkles size={10} />}
                ✨ Suggest Marketing Copy
            </button>
            {suggestion && (
                <p className="mt-3 text-[11px] text-slate-400 italic leading-relaxed animate-in fade-in duration-500">
                    "{suggestion}"
                </p>
            )}
        </div>
    )
}

function LeadForm({ user }) {
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!user) return;
    setLoading(true);
    const fd = new FormData(e.target);
    const data = Object.fromEntries(fd);
    try {
      await addDoc(collection(db, 'artifacts', appId, 'public', 'data', 'leads'), { ...data, timestamp: Date.now() });
      setSent(true);
    } catch (err) { console.error(err); } finally { setLoading(false); }
  };

  if (sent) return (
    <div className="text-center py-16">
      <CheckCircle size={64} className="text-[#84A98C] mx-auto mb-6" />
      <h3 className="text-3xl font-light tracking-tight mb-2">Request Received.</h3>
      <p className="text-slate-500 italic font-serif">SANORA will connect with you shortly.</p>
    </div>
  );

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      <h3 className="text-3xl font-light tracking-tight text-slate-900 mb-8">SANORA <span className="text-[#84A98C]">Atelier</span></h3>
      <div className="grid md:grid-cols-2 gap-6">
        <input required name="name" className="w-full bg-[#F9F7F2] p-5 rounded-2xl border-none outline-none focus:ring-2 ring-[#84A98C]/20 transition-all" placeholder="Client Name" />
        <input required name="phone" className="w-full bg-[#F9F7F2] p-5 rounded-2xl border-none outline-none focus:ring-2 ring-[#84A98C]/20 transition-all" placeholder="Contact No" />
      </div>
      <input required name="email" type="email" className="w-full bg-[#F9F7F2] p-5 rounded-2xl border-none outline-none focus:ring-2 ring-[#84A98C]/20 transition-all" placeholder="Email Address" />
      <textarea name="message" rows="3" className="w-full bg-[#F9F7F2] p-5 rounded-2xl border-none outline-none focus:ring-2 ring-[#84A98C]/20 transition-all" placeholder="Project Vision..."></textarea>
      <button disabled={loading} className="w-full bg-[#C5A059] text-white font-bold py-6 rounded-[2rem] text-[10px] uppercase tracking-[0.4em] shadow-lg shadow-[#C5A059]/30 hover:bg-[#84A98C] transition-all">
        {loading ? 'Processing...' : 'Secure Consultation'}
      </button>
    </form>
  );
}

const defaultProjects = [
  { id: 'dp1', name: 'The Oak Pavilion', location: 'Vancouver, BC', image: 'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&q=80&w=1200' },
  { id: 'dp2', name: 'Wasabi Minimalist', location: 'Kyoto, JP', image: 'https://images.unsplash.com/photo-1588854337221-4cf9fa96059c?auto=format&fit=crop&q=80&w=800' },
  { id: 'dp3', name: 'Antique Brass Loft', location: 'London, UK', image: 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&q=80&w=800' },
  { id: 'dp4', name: 'Terrace Sanctuary', location: 'Mumbai, IN', image: 'https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&q=80&w=800' }
];

const defaultServices = [
  { id: 'ds1', title: 'Timber Architecture', description: 'Specializing in sustainable wood-based interior structural design and custom cabinetry.' },
  { id: 'ds2', title: 'Antique Metal Craft', description: 'Curated brass, bronze, and copper finishes to add timeless character to modern spaces.' },
  { id: 'ds3', title: 'Biophilic Palettes', description: 'Nature-inspired color consulting focused on yellow-green hues and earth tones.' }
];