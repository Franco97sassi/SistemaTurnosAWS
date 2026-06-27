import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";
 
const API_URL = "http://turnos-alb-172952982.us-east-1.elb.amazonaws.com";

function App() {
  const [turnos, setTurnos] = useState([]);
  const [cliente, setCliente] = useState("");
  const [servicio, setServicio] = useState("");
  const [fecha, setFecha] = useState("");

  const cargarTurnos = async () => {
    const response = await axios.get(`${API_URL}/turnos`);
    setTurnos(response.data);
  };

  const crearTurno = async (e) => {
    e.preventDefault();

    await axios.post(`${API_URL}/turnos`, {
      cliente,
      servicio,
      fecha,
    });

    setCliente("");
    setServicio("");
    setFecha("");
    cargarTurnos();
  };

  const cancelarTurno = async (id) => {
    await axios.delete(`${API_URL}/turnos/${id}`);
    cargarTurnos();
  };

  useEffect(() => {
    cargarTurnos();
  }, []);

  return (
    <div className="container">
      <h1>Sistema de Turnos AWS</h1>

      <form onSubmit={crearTurno} className="formulario">
        <input
          type="text"
          placeholder="Cliente"
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

      <h2>Turnos</h2>

      <div className="lista">
        {turnos.map((turno) => (
          <div key={turno.id} className="card">
            <p><strong>Cliente:</strong> {turno.cliente}</p>
            <p><strong>Servicio:</strong> {turno.servicio}</p>
            <p><strong>Fecha:</strong> {new Date(turno.fecha).toLocaleString()}</p>
            <p><strong>Estado:</strong> {turno.estado}</p>

            {turno.estado !== "cancelado" && (
              <button onClick={() => cancelarTurno(turno.id)}>
                Cancelar
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;