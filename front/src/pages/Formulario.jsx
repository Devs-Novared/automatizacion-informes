import React, { useState, useEffect } from "react";

const Formulario = ({ formData, handleFilterChange, listaCliente = [], listaTecnologia = [], listaContrato = [], listaContentIdContrato = [], months = [] }) => {
  const [searchTerm, setSearchTerm] = useState({ cliente: "", tecnologia: "", contrato: "" });
  const [nombreArchivo, setNombreArchivo] = useState("reporte.pdf");

  // **Actualizar nombre del archivo basado en selecciones**
  useEffect(() => {
    const { cliente, tecnologia, contrato, selectedMonth } = formData;
    let nuevoNombre = `${cliente || "Cliente"}_${tecnologia || "Tecnologia"}_${contrato || "Contrato"}_${selectedMonth || "Mes"}.pdf`;
    nuevoNombre = nuevoNombre.replace(/\s+/g, "_").toLowerCase();
    setNombreArchivo(nuevoNombre);
  }, [formData]);

  const handleSearchChange = (e) => {
    const { name, value } = e.target;
    setSearchTerm((prev) => ({
      ...prev,
      [name]: value.toLowerCase(),
    }));
  };

  // **Filtrar tecnologías según el cliente seleccionado**
  const tecnologiasFiltradas = listaTecnologia.filter(tecnologia =>
    !formData.cliente || listaContentIdContrato.some(item => item.cliente === formData.cliente && item.tecnologia === tecnologia)
  );

  // **Filtrar contratos según cliente y tecnología seleccionados**
  const contratosFiltrados = listaContrato.filter(contrato =>
    listaContentIdContrato.some(item =>
      (!formData.cliente || item.cliente === formData.cliente) &&
      (!formData.tecnologia || item.tecnologia === formData.tecnologia) &&
      item.nroContrato === contrato
    )
  );

  // **Actualizar cliente y tecnología automáticamente cuando se selecciona un contrato**
  const handleContratoChange = (e) => {
    const contratoSeleccionado = e.target.value;
    const datosContrato = listaContentIdContrato.find(item => item.nroContrato === contratoSeleccionado);

    if (datosContrato) {
      handleFilterChange({ target: { name: "cliente", value: datosContrato.cliente } });
      handleFilterChange({ target: { name: "tecnologia", value: datosContrato.tecnologia } });
    }

    handleFilterChange(e);
  };

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
          {listaCliente
            .filter(cliente => cliente.toLowerCase().includes(searchTerm.cliente))
            .map((cliente, index) => (
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
          {tecnologiasFiltradas.length > 0
            ? tecnologiasFiltradas
                .filter(tecnologia => tecnologia.toLowerCase().includes(searchTerm.tecnologia))
                .map((tecnologia, index) => (
                  <option key={index} value={tecnologia}>{tecnologia}</option>
                ))
            : <option disabled>No hay tecnologías disponibles</option>
          }
        </select>
      </div>

      {/* Contrato */}
      <div>
        <label>Contrato <span style={{ color: "red" }}>*</span>:</label>
        <input
          type="text"
          placeholder="Buscar contrato..."
          name="contrato"
          value={searchTerm.contrato}
          onChange={handleSearchChange}
        />
        <select name="contrato" value={formData.contrato} onChange={handleContratoChange} required>
          <option value="">Selecciona el Contrato</option>
          {contratosFiltrados.length > 0
            ? contratosFiltrados
                .filter(contrato => contrato.toLowerCase().includes(searchTerm.contrato))
                .map((contrato, index) => (
                  <option key={index} value={contrato}>{contrato}</option>
                ))
            : <option disabled>No hay contratos disponibles</option>
          }
        </select>
      </div>

      {/* Mes */}
      <div>
        <label>Mes <span style={{ color: "red" }}>*</span>:</label>
        <select name="selectedMonth" value={formData.selectedMonth} onChange={handleFilterChange} required>
          <option value="">Selecciona un mes</option>
          {months.map((month, index) => (
            <option key={index} value={month}>{month}</option>
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
