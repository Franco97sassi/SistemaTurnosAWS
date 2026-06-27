import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://turnos-alb-172952982.us-east-1.elb.amazonaws.com";

function App() {
  const [turnos, setTurnos] = useState([]);
  const [cliente, setCliente] = useState("");
  const [servicio, setServicio] = useState("");
  const [fecha, setFecha] = useState("");
  const [loading, setLoading] = useState(false);
  const [mensaje, setMensaje] = useState("");

  const cargarTurnos = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/turnos`);
      setTurnos(response.data);
    } catch (error) {
      setMensaje("Error al cargar turnos");
    } finally {
      setLoading(false);
    }
  };

  const crearTurno = async (e) => {
    e.preventDefault();

    try {
      await axios.post(`${API_URL}/turnos`, {
        cliente,
        servicio,
        fecha,
      });

      setCliente("");
      setServicio("");
      setFecha("");
      setMensaje("Turno creado correctamente");
      cargarTurnos();
    } catch (error) {
      setMensaje("Error al crear el turno");
    }
  };

  const cancelarTurno = async (id) => {
    try {
      await axios.delete(`${API_URL}/turnos/${id}`);
      setMensaje("Turno cancelado correctamente");
      cargarTurnos();
    } catch (error) {
      setMensaje("Error al cancelar el turno");
    }
  };

  useEffect(() => {
    cargarTurnos();
  }, []);

  return (
    <div className="page">
      <div className="container">
        <header className="header">
          <div>
            <h1>Sistema de Turnos AWS</h1>
            <p>Frontend React conectado a FastAPI en ECS Fargate + RDS PostgreSQL</p>
          </div>

          <button className="refresh" onClick={cargarTurnos}>
            Actualizar
          </button>
        </header>

        {mensaje && <div className="mensaje">{mensaje}</div>}

        <section className="panel">
          <h2>Crear nuevo turno</h2>

          <form onSubmit={crearTurno} className="formulario">
            <input
              type="text"
              placeholder="Nombre del cliente"
              value={cliente}
              onChange={(e) => setCliente(e.target.value)}
              required
            />

            <input
              type="text"
              placeholder="Servicio"
              value={servicio}
              onChange={(e) => setServicio(e.target.value)}
              required
            />

            <input
              type="datetime-local"
              value={fecha}
              onChange={(e) => setFecha(e.target.value)}
              required
            />

            <button type="submit">Crear turno</button>
          </form>
        </section>

        <section className="panel">
          <div className="section-title">
            <h2>Turnos registrados</h2>
            <span>{turnos.length} turnos</span>
          </div>

          {loading ? (
            <p className="empty">Cargando turnos...</p>
          ) : turnos.length === 0 ? (
            <p className="empty">Todavía no hay turnos cargados.</p>
          ) : (
            <div className="grid">
              {turnos.map((turno) => (
                <div key={turno.id} className="card">
                  <div className="card-top">
                    <h3>{turno.cliente}</h3>
                    <span className={turno.estado === "cancelado" ? "cancelado" : "pendiente"}>
                      {turno.estado}
                    </span>
                  </div>

                  <p>
                    <strong>Servicio:</strong> {turno.servicio}
                  </p>

                  <p>
                    <strong>Fecha:</strong>{" "}
                    {new Date(turno.fecha).toLocaleString("es-AR")}
                  </p>

                  <p>
                    <strong>ID:</strong> #{turno.id}
                  </p>

                  {turno.estado !== "cancelado" && (
                    <button
                      className="cancelar"
                      onClick={() => cancelarTurno(turno.id)}
                    >
                      Cancelar turno
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

export default App;