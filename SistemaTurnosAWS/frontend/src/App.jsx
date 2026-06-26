import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL;

function App() {
  const [clientes, setClientes] = useState([]);
  const [nombre, setNombre] = useState("");
  const [email, setEmail] = useState("");
  const [telefono, setTelefono] = useState("");

  const cargarClientes = async () => {
    const res = await axios.get(`${API_URL}/clientes/`);
    setClientes(res.data);
  };

  const crearCliente = async (e) => {
    e.preventDefault();

    await axios.post(`${API_URL}/clientes/`, {
      nombre,
      email,
      telefono,
    });

    setNombre("");
    setEmail("");
    setTelefono("");
    cargarClientes();
  };

  useEffect(() => {
    cargarClientes();
  }, []);

  return (
    <div className="container">
      <h1>Sistema de Turnos AWS</h1>

      <form onSubmit={crearCliente} className="card">
        <h2>Crear Cliente</h2>

        <input
          placeholder="Nombre"
          value={nombre}
          onChange={(e) => setNombre(e.target.value)}
        />

        <input
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          placeholder="Teléfono"
          value={telefono}
          onChange={(e) => setTelefono(e.target.value)}
        />

        <button type="submit">Guardar Cliente</button>
      </form>

      <div className="card">
        <h2>Clientes</h2>

        {clientes.length === 0 ? (
          <p>No hay clientes cargados.</p>
        ) : (
          clientes.map((cliente) => (
            <div key={cliente.id} className="item">
              <strong>{cliente.nombre}</strong>
              <p>{cliente.email}</p>
              <p>{cliente.telefono}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default App;