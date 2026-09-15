import { useCallback, useEffect, useMemo, useState } from "react";
import axios from "axios";
import "./App.css";
import { appointmentStats, initials } from "./lib/agenda.js";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const api = axios.create({ baseURL: API_URL, timeout: 8000 });
const initialForm = { cliente: "", servicio: "Consulta general", fecha: "" };
const services = ["Consulta general", "Odontología", "Nutrición", "Psicología", "Kinesiología"];

const Icon = ({ name, size = 20 }) => {
  const paths = {
    calendar: <><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18"/></>,
    grid: <><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></>,
    users: <><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></>,
    clock: <><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
    search: <><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></>,
    plus: <path d="M12 5v14M5 12h14"/>,
    logout: <><path d="M10 17l5-5-5-5M15 12H3M21 19V5a2 2 0 0 0-2-2h-6"/></>,
    edit: <><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L8 18l-4 1 1-4Z"/></>,
    trash: <><path d="M3 6h18M8 6V4h8v2M19 6l-1 15H6L5 6M10 11v6M14 11v6"/></>,
    close: <path d="m6 6 12 12M18 6 6 18"/>,
    chevron: <path d="m9 18 6-6-6-6"/>,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>;
};

const errorMessage = (error, fallback) => {
  const detail = error.response?.data?.detail;
  if (Array.isArray(detail)) return detail[0]?.msg?.replace("Value error, ", "") || fallback;
  return detail || (error.code === "ECONNABORTED" ? "La API tardó demasiado en responder" : fallback);
};

function Login({ onLogin }) {
  const [credentials, setCredentials] = useState({ email: "admin@turnos.local", password: "TurnosDemo2026!" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const submit = async (event) => {
    event.preventDefault(); setLoading(true); setError("");
    try { const { data } = await api.post("/auth/login", credentials); onLogin(data); }
    catch (err) { setError(errorMessage(err, "No pudimos iniciar sesión")); }
    finally { setLoading(false); }
  };
  return <main className="login-page">
    <section className="login-showcase"><div className="logo light"><span><Icon name="calendar" /></span> Turnia</div><div className="showcase-copy"><span className="pill">GESTIÓN SIMPLE Y PROFESIONAL</span><h1>Tu agenda,<br/><em>siempre al día.</em></h1><p>Organiza turnos, reduce ausencias y brinda una mejor atención desde un solo lugar.</p><div className="trust"><div className="avatars"><i>AM</i><i>JR</i><i>LC</i></div><span><b>+2.500 profesionales</b> organizan su día con Turnia</span></div></div><div className="showcase-orb" /></section>
    <section className="login-panel"><form className="login-card" onSubmit={submit}><div className="mobile-logo logo"><span><Icon name="calendar" /></span> Turnia</div><p className="overline">BIENVENIDO DE NUEVO</p><h2>Inicia sesión</h2><p className="muted">Accede a tu panel para gestionar la agenda.</p>{error && <div className="form-error" role="alert">{error}</div>}<label>Correo electrónico<input type="email" value={credentials.email} onChange={e => setCredentials({...credentials,email:e.target.value})} required /></label><label>Contraseña<input type="password" value={credentials.password} onChange={e => setCredentials({...credentials,password:e.target.value})} required /></label><button className="primary wide" disabled={loading}>{loading ? "Ingresando…" : "Ingresar al panel"}<Icon name="chevron" size={18}/></button><p className="demo-hint">Demo: las credenciales ya están completadas</p></form></section>
  </main>;
}

function AppointmentModal({ turno, onClose, onSave }) {
  const editing = Boolean(turno);
  const [form, setForm] = useState(editing ? { cliente: turno.cliente, servicio: turno.servicio, fecha: turno.fecha.slice(0,16) } : initialForm);
  const [saving, setSaving] = useState(false);
  const submit = async e => { e.preventDefault(); setSaving(true); await onSave(form, turno); setSaving(false); };
  return <div className="modal-backdrop" onMouseDown={e => e.target === e.currentTarget && onClose()}><section className="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title"><button className="close" onClick={onClose} aria-label="Cerrar"><Icon name="close"/></button><span className="modal-icon"><Icon name={editing ? "edit" : "calendar"}/></span><h2 id="modal-title">{editing ? "Reprogramar turno" : "Agendar nuevo turno"}</h2><p>{editing ? "Selecciona una nueva fecha y hora para la cita." : "Completa los datos del paciente y confirma la cita."}</p><form onSubmit={submit}><label>Paciente<input value={form.cliente} onChange={e=>setForm({...form,cliente:e.target.value})} minLength="2" maxLength="100" disabled={editing} required/></label><label>Servicio<select value={form.servicio} onChange={e=>setForm({...form,servicio:e.target.value})} disabled={editing}>{services.map(service=><option key={service}>{service}</option>)}</select></label><label>Fecha y hora<input type="datetime-local" value={form.fecha} min={new Date().toISOString().slice(0,16)} onChange={e=>setForm({...form,fecha:e.target.value})} required/></label><div className="modal-actions"><button type="button" className="secondary" onClick={onClose}>Cancelar</button><button className="primary" disabled={saving}>{saving ? "Guardando…" : editing ? "Confirmar cambio" : "Agendar turno"}</button></div></form></section></div>;
}

function App() {
  const [session, setSession] = useState(() => JSON.parse(localStorage.getItem("turnia_session") || "null"));
  const [data, setData] = useState({ items: [], total: 0 });
  const [filter, setFilter] = useState("todos"); const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true); const [notice, setNotice] = useState(null); const [modal, setModal] = useState(undefined);
  useEffect(() => { if (session?.access_token) { api.defaults.headers.common.Authorization = `Bearer ${session.access_token}`; localStorage.setItem("turnia_session", JSON.stringify(session)); } else { delete api.defaults.headers.common.Authorization; localStorage.removeItem("turnia_session"); } }, [session]);
  const logout = useCallback(() => setSession(null), []);
  const cargarTurnos = useCallback(async () => {
    if (!session) return; setLoading(true);
    try { const params={page_size:100}; if(filter!=="todos")params.estado=filter;if(search.trim())params.search=search.trim(); const response=await api.get("/turnos",{params});setData(response.data); }
    catch(error){ if(error.response?.status===401) logout(); else setNotice({type:"error",text:errorMessage(error,"No pudimos cargar la agenda")}); }
    finally{setLoading(false);}
  },[filter,search,session,logout]);
  useEffect(()=>{const timer=setTimeout(cargarTurnos,250);return()=>clearTimeout(timer)},[cargarTurnos]);
  const saveTurno=async(form,turno)=>{try{if(turno)await api.patch(`/turnos/${turno.id}`,{fecha:form.fecha});else await api.post("/turnos",form);setModal(undefined);setNotice({type:"success",text:turno?"Turno reprogramado correctamente":"Turno agendado correctamente"});await cargarTurnos();}catch(error){setNotice({type:"error",text:errorMessage(error,"No pudimos guardar el turno")});}};
  const cancelar=async turno=>{if(!window.confirm(`¿Cancelar el turno de ${turno.cliente}?`))return;try{await api.delete(`/turnos/${turno.id}`);setNotice({type:"success",text:"Turno cancelado; su historial se conserva"});await cargarTurnos();}catch(error){setNotice({type:"error",text:errorMessage(error,"No pudimos cancelar el turno")});}};
  const stats=useMemo(()=>appointmentStats(data.items),[data.items]);
  if(!session)return <Login onLogin={setSession}/>;
  return <div className="app-shell">
    <aside className="sidebar"><div className="logo"><span><Icon name="calendar"/></span> Turnia</div><nav className="side-nav"><p>MENÚ</p><button className="active"><Icon name="grid"/> Resumen</button><button><Icon name="calendar"/> Agenda <small>{stats.pendientes}</small></button><button><Icon name="users"/> Pacientes</button><button><Icon name="clock"/> Historial</button></nav><div className="sidebar-help"><span>?</span><b>¿Necesitas ayuda?</b><p>Consulta nuestra guía rápida.</p></div><button className="logout" onClick={logout}><Icon name="logout"/> Cerrar sesión</button></aside>
    <main className="dashboard"><header className="topbar"><div><p>{new Intl.DateTimeFormat("es-AR",{weekday:"long",day:"numeric",month:"long"}).format(new Date())}</p><h1>Buenos días, {session.user.name.split(" ")[0]} 👋</h1></div><div className="user"><span>ER</span><div><b>{session.user.name}</b><small>Administrador</small></div></div></header>
      <section className="dashboard-content"><div className="page-heading"><div><h2>Resumen de agenda</h2><p>Consulta y administra los turnos de tu equipo.</p></div><button className="primary add" onClick={()=>setModal(null)}><Icon name="plus"/> Nuevo turno</button></div>
      <section className="metric-grid"><article><span className="metric-icon blue"><Icon name="calendar"/></span><div><p>Turnos totales</p><strong>{data.total}</strong><small>en la agenda actual</small></div></article><article><span className="metric-icon green"><Icon name="clock"/></span><div><p>Para hoy</p><strong>{stats.hoy}</strong><small>citas programadas</small></div></article><article><span className="metric-icon amber"><Icon name="users"/></span><div><p>Pendientes</p><strong>{stats.pendientes}</strong><small>requieren atención</small></div></article><article><span className="metric-icon violet"><Icon name="grid"/></span><div><p>Cancelados</p><strong>{stats.cancelados}</strong><small>historial conservado</small></div></article></section>
      {notice&&<div className={`notice ${notice.type}`} role="status"><span>{notice.text}</span><button onClick={()=>setNotice(null)}><Icon name="close" size={17}/></button></div>}
      <section className="agenda-panel"><div className="agenda-header"><div><h3>Próximos turnos</h3><p>{data.total} resultados en total</p></div><div className="agenda-tools"><label className="search"><Icon name="search" size={18}/><input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Buscar paciente o servicio…"/></label><div className="filters">{["todos","pendiente","cancelado"].map(value=><button key={value} className={filter===value?"active":""} onClick={()=>setFilter(value)}>{value}</button>)}</div></div></div>
      <div className="table-head"><span>FECHA Y HORA</span><span>PACIENTE</span><span>SERVICIO</span><span>ESTADO</span><span>ACCIONES</span></div>
      <div className="appointment-list">{loading?<div className="empty"><span className="spinner"/>Actualizando agenda…</div>:data.items.length===0?<div className="empty"><span className="empty-calendar"><Icon name="calendar" size={28}/></span><b>No hay turnos para mostrar</b><p>Prueba con otro filtro o agenda una nueva cita.</p></div>:data.items.map(turno=><article className="appointment" key={turno.id}><div className="when"><span>{new Date(turno.fecha).toLocaleDateString("es-AR",{day:"2-digit",month:"short"})}</span><div><b>{new Date(turno.fecha).toLocaleDateString("es-AR",{weekday:"long"})}</b><small>{new Date(turno.fecha).toLocaleTimeString("es-AR",{hour:"2-digit",minute:"2-digit"})} hs</small></div></div><div className="patient"><i>{initials(turno.cliente)}</i><b>{turno.cliente}</b></div><span className="service">{turno.servicio}</span><span className={`status ${turno.estado}`}><i/>{turno.estado}</span><div className="actions">{turno.estado==="pendiente"&&<><button onClick={()=>setModal(turno)} aria-label={`Reprogramar turno de ${turno.cliente}`}><Icon name="edit" size={17}/></button><button className="danger" onClick={()=>cancelar(turno)} aria-label={`Cancelar turno de ${turno.cliente}`}><Icon name="trash" size={17}/></button></>}</div></article>)}</div></section>
      <footer>Turnia · Gestión de turnos segura en AWS <span>API v1.0 · Sistema operativo</span></footer></section>
    </main>{modal!==undefined&&<AppointmentModal turno={modal} onClose={()=>setModal(undefined)} onSave={saveTurno}/>}</div>;
}

export default App;
