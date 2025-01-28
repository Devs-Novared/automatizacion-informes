// InformeForm.js
import React from "react";

const Formulario = ({ formData, handleFilterChange, listaCliente, listaTecnologia, listaContrato, months, handleFileNameChange, nombre_archivo }) => {
  return (
    <form>
      <div>
        <label>
          Cliente:
          <select
            name="cliente"
            value={formData.cliente}
            onChange={handleFilterChange}
          >
            <option value="" disabled>
              Selecciona el Cliente
            </option>
            {listaCliente.map((cliente, index) => (
              <option key={index} value={cliente}>
                {cliente}
              </option>
            ))}
          </select>
        </label>
      </div>
      <div>
        <label>
          Tecnología:
          <select
            name="tecnologia"
            value={formData.tecnologia}
            onChange={handleFilterChange}
          >
            <option value="" disabled>
              Selecciona una Tecnología
            </option>
            {listaTecnologia.map((tecnologia, index) => (
              <option key={index} value={tecnologia}>
                {tecnologia}
              </option>
            ))}
          </select>
        </label>
      </div>
      <div>
        <label>
          Contrato:
          <select
            name="contrato"
            value={formData.contrato}
            onChange={handleFilterChange}
          >
            <option value="" disabled>
              Selecciona el Contrato
            </option>
            {listaContrato.map((contrato, index) => (
              <option key={index} value={contrato}>
                {contrato}
              </option>
            ))}
          </select>
        </label>
      </div>
      <div>
        <label>
          Mes:
          <select
            name="selectedMonth"
            value={formData.selectedMonth}
            onChange={handleFilterChange}
          >
            <option value="" disabled>
              Selecciona un mes
            </option>
            {months.map((month, index) => (
              <option key={index} value={month}>
                {month}
              </option>
            ))}
          </select>
        </label>
      </div>

      {/* Nombre del archivo */}
      <div>
        <label>
          Nombre del archivo:
          <input
            type="text"
            value={nombre_archivo}
            onChange={handleFileNameChange}
            required
          />
        </label>
      </div>
    </form>
  );
};

export default Formulario;
