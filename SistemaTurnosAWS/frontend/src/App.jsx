import { useCallback, useEffect, useMemo, useState } from "react";
import axios from "axios";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const api = axios.create({ baseURL: API_URL, timeout: 8000 });
const initialForm = { cliente: "", servicio: "", fecha: "" };

const errorMessage = (error, fallback) =>
  error.response?.data?.detail || (error.code === "ECONNABORTED" ? "La API tardó demasiado en responder" : fallback);

function App() {
  const [data, setData] = useState({ items: [], total: 0 });
  const [form, setForm] = useState(initialForm);
  const [filter, setFilter] = useState("todos");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [notice, setNotice] = useState(null);

  const cargarTurnos = useCallback(async () => {
    setLoading(true);
    try {
      const params = { page_size: 100 };
      if (filter !== "todos") params.estado = filter;
      if (search.trim()) params.search = search.trim();
      const response = await api.get("/turnos", { params });
      setData(response.data);
    } catch (error) {
      setNotice({ type: "error", text: errorMessage(error, "No pudimos cargar la agenda") });
    } finally {
      setLoading(false);
    }
  }, [filter, search]);

  useEffect(() => {
    const timer = setTimeout(cargarTurnos, 250);
    return () => clearTimeout(timer);
  }, [cargarTurnos]);

  const crearTurno = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    try {
      await api.post("/turnos", form);
      setForm(initialForm);
      setNotice({ type: "success", text: "Turno reservado correctamente" });
      await cargarTurnos();
    } catch (error) {
      setNotice({ type: "error", text: errorMessage(error, "No pudimos crear el turno") });
    } finally {
      setSubmitting(false);
    }
  };

  const cancelarTurno = async (turno) => {
    if (!window.confirm(`¿Cancelar el turno de ${turno.cliente}?`)) return;
    try {
      await api.delete(`/turnos/${turno.id}`);
      setNotice({ type: "success", text: "Turno cancelado; conservamos su historial" });
      await cargarTurnos();
    } catch (error) {
      setNotice({ type: "error", text: errorMessage(error, "No pudimos cancelar el turno") });
    }
  };

  const stats = useMemo(() => ({
    pendientes: data.items.filter((item) => item.estado === "pendiente").length,
    cancelados: data.items.filter((item) => item.estado === "cancelado").length,
  }), [data.items]);

  return (
    <main className="shell">
      <header className="hero">
        <nav><span className="brand"><i>ST</i> Turnos Cloud</span><span className="live"><b /> AWS operativo</span></nav>
        <div className="hero-copy">
          <div><p className="eyebrow">GESTIÓN INTELIGENTE DE AGENDA</p><h1>Tu tiempo, <em>bien organizado.</em></h1><p className="subtitle">Reserva y administra turnos desde una experiencia rápida, segura y disponible en la nube.</p></div>
          <div className="architecture"><span>React</span><b>→</b><span>FastAPI</span><b>→</b><span>AWS</span></div>
        </div>
      </header>

      <section className="stats" aria-label="Resumen de agenda">
        <article><span>Total visible</span><strong>{data.total}</strong></article>
        <article><span>Pendientes</span><strong>{stats.pendientes}</strong></article>
        <article><span>Cancelados</span><strong>{stats.cancelados}</strong></article>
        <article><span>Disponibilidad</span><strong className="online">En línea</strong></article>
      </section>

      {notice && <div role="status" className={`notice ${notice.type}`}>{notice.text}<button aria-label="Cerrar mensaje" onClick={() => setNotice(null)}>×</button></div>}

      <div className="workspace">
        <section className="booking panel">
          <div className="section-heading"><div><span>01</span><h2>Nuevo turno</h2></div><p>Completa los datos para reservar</p></div>
          <form onSubmit={crearTurno}>
            <label>Nombre del cliente<input value={form.cliente} onChange={(e) => setForm({ ...form, cliente: e.target.value })} placeholder="Ej. Ada Lovelace" minLength="2" maxLength="100" required /></label>
            <label>Servicio<input value={form.servicio} onChange={(e) => setForm({ ...form, servicio: e.target.value })} placeholder="Ej. Consultoría" minLength="2" maxLength="100" required /></label>
            <label>Fecha y hora<input type="datetime-local" value={form.fecha} min={new Date().toISOString().slice(0, 16)} onChange={(e) => setForm({ ...form, fecha: e.target.value })} required /></label>
            <button className="primary" disabled={submitting}>{submitting ? "Reservando…" : "Reservar turno"}<span>→</span></button>
          </form>
        </section>

        <section className="agenda panel">
          <div className="section-heading"><div><span>02</span><h2>Agenda</h2></div><button className="icon-button" onClick={cargarTurnos} aria-label="Actualizar agenda">↻</button></div>
          <div className="toolbar">
            <label className="search"><span>⌕</span><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Buscar cliente o servicio" aria-label="Buscar turnos" /></label>
            <div className="filters">{["todos", "pendiente", "cancelado"].map((value) => <button key={value} className={filter === value ? "active" : ""} onClick={() => setFilter(value)}>{value}</button>)}</div>
          </div>
          {loading ? <div className="empty">Actualizando agenda…</div> : data.items.length === 0 ? <div className="empty"><b>Agenda despejada</b><span>No encontramos turnos con esos filtros.</span></div> : <div className="cards">{data.items.map((turno) => <article className="appointment" key={turno.id}>
            <div className="date"><strong>{new Date(turno.fecha).toLocaleDateString("es-AR", { day: "2-digit" })}</strong><span>{new Date(turno.fecha).toLocaleDateString("es-AR", { month: "short" }).replace(".", "")}</span></div>
            <div className="details"><div><h3>{turno.cliente}</h3><span className={`status ${turno.estado}`}>{turno.estado}</span></div><p>{turno.servicio} · {new Date(turno.fecha).toLocaleTimeString("es-AR", { hour: "2-digit", minute: "2-digit" })} hs</p></div>
            {turno.estado === "pendiente" && <button className="cancel" onClick={() => cancelarTurno(turno)}>Cancelar</button>}
          </article>)}</div>}
        </section>
      </div>
      <footer><span>Diseñado para escalar en AWS</span><span>FastAPI · PostgreSQL · ECS Fargate · Terraform</span></footer>
    </main>
  );
}

export default App;
