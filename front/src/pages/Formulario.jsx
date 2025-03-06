import React, { useState, useEffect } from "react";

const Formulario = ({ 
  formData = { cliente: "", tecnologia: "", contrato: "", selectedMonth: "" }, 
  handleFilterChange, 
  listaContentIdContrato = []
}) => {
  const [searchTerm, setSearchTerm] = useState({ cliente: "", tecnologia: "", contrato: "" });
  const [nombreArchivo, setNombreArchivo] = useState("reporte.pdf");

  useEffect(() => {
    const { cliente, tecnologia, contrato, selectedMonth } = formData;
    let nuevoNombre = `${cliente || "Cliente"}_${tecnologia || "Tecnologia"}_${contrato || "Contrato"}_${selectedMonth || "Mes"}.pdf`;
    nuevoNombre = nuevoNombre.replace(/\s+/g, "_").toLowerCase();
    setNombreArchivo(nuevoNombre);
  }, [formData]);

  const handleSearchChange = (e) => {
    setSearchTerm({ ...searchTerm, [e.target.name]: e.target.value.toLowerCase() });
  };

  const clientesFiltrados = listaContentIdContrato
    .filter(item => !formData.tecnologia || item.tecnologia === formData.tecnologia)
    .map(item => item.cliente)
    .filter((v, i, a) => a.indexOf(v) === i)
    .filter(cliente => cliente.toLowerCase().includes(searchTerm.cliente));

  const tecnologiasFiltradas = listaContentIdContrato
    .filter(item => !formData.cliente || item.cliente === formData.cliente)
    .map(item => item.tecnologia)
    .filter((v, i, a) => a.indexOf(v) === i)
    .filter(tecnologia => tecnologia.toLowerCase().includes(searchTerm.tecnologia));

  const contratosFiltrados = listaContentIdContrato
    .filter(item => 
      (!formData.cliente || item.cliente === formData.cliente) &&
      (!formData.tecnologia || item.tecnologia === formData.tecnologia)
    )
    .map(item => item.nroContrato)
    .filter(contrato => contrato.toLowerCase().includes(searchTerm.contrato));

  // Selección automática cuando queda una sola opción en las listas filtradas
  useEffect(() => {
    if (clientesFiltrados.length === 1 && formData.cliente === "") {
      handleFilterChange({ target: { name: "cliente", value: clientesFiltrados[0] } });
    }
    if (tecnologiasFiltradas.length === 1 && formData.tecnologia === "") {
      handleFilterChange({ target: { name: "tecnologia", value: tecnologiasFiltradas[0] } });
    }
    if (contratosFiltrados.length === 1 && formData.contrato === "") {
      handleFilterChange({ target: { name: "contrato", value: contratosFiltrados[0] } });
    }
  }, [clientesFiltrados, tecnologiasFiltradas, contratosFiltrados]);

  return (
    <form>
      {/* Cliente */}
      <div>
        <label>Cliente:</label>
        <input
          type="text"
          placeholder="Buscar cliente..."
          name="cliente"
          value={searchTerm.cliente}
          onChange={handleSearchChange}
        />
        <select name="cliente" value={formData.cliente} onChange={handleFilterChange}>
          <option value="">Selecciona el Cliente</option>
          {clientesFiltrados.map((cliente, index) => (
            <option key={index} value={cliente}>{cliente}</option>
          ))}
        </select>
      </div>

      {/* Tecnología */}
      <div>
        <label>Tecnología:</label>
        <input
          type="text"
          placeholder="Buscar tecnología..."
          name="tecnologia"
          value={searchTerm.tecnologia}
          onChange={handleSearchChange}
        />
        <select name="tecnologia" value={formData.tecnologia} onChange={handleFilterChange}>
          <option value="">Selecciona una Tecnología</option>
          {tecnologiasFiltradas.map((tecnologia, index) => (
            <option key={index} value={tecnologia}>{tecnologia}</option>
          ))}
        </select>
      </div>

      {/* Contrato */}
      <div>
        <label>Contrato:</label>
        <input
          type="text"
          placeholder="Buscar contrato..."
          name="contrato"
          value={searchTerm.contrato}
          onChange={handleSearchChange}
        />
        <select name="contrato" value={formData.contrato} onChange={handleFilterChange}>
          <option value="">Selecciona el Contrato</option>
          {contratosFiltrados.map((contrato, index) => (
            <option key={index} value={contrato}>{contrato}</option>
          ))}
        </select>
      </div>

      {/* Mes */}
      <div>
        <label>Mes:</label>
        <select name="selectedMonth" value={formData.selectedMonth} onChange={handleFilterChange}>
          <option value="">Selecciona el Mes</option>
          {["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"].map((mes, index) => (
            <option key={index} value={mes}>{mes}</option>
          ))}
        </select>
      </div>

      {/* Nombre del archivo */}
      <div>
        <label>Nombre del archivo:</label>
        <input type="text" value={nombreArchivo} readOnly />
      </div>
    </form>
  );
};

export default Formulario;
