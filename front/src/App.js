import React, { useState } from "react";
import "./App.css";

function App() {
  // State for basic form data
  const [formData, setFormData] = useState({
    empresa: "",
    mes: new Date().toLocaleString("default", { month: "long" }),
    tecnologia: "",
    contrato: "",
  });

  // State for additional filters
  const [filters, setFilters] = useState({
    selectedMonth: "",
    status: "",
    category: "",
  });

  // State for the file name
  const [nombre_archivo, setNombre_archivo] = useState("reporte.pdf");

  // Handle changes in the main form data
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  // Handle changes in the additional filters
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters({ ...filters, [name]: value });
  };

  // Handle changes in the file name
  const handleFileNameChange = (e) => {
    let fileName = e.target.value;
    if (!fileName.endsWith(".pdf")) {
      fileName += ".pdf";
    }
    setNombre_archivo(fileName);
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    const combinedFilters = {
      ...formData,
      ...filters,
      nombre_archivo,
    };
    console.log("Datos y Filtros combinados:", combinedFilters);

    // Call backend to generate and download the PDF
    fetch("http://127.0.0.1:5000/download-pdf", {  // Asegúrate de que la URL esté correcta
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(combinedFilters),
    })
      .then((response) => response.blob())
      .then((blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = nombre_archivo;
        document.body.appendChild(a);
        a.click();
        a.remove();
      })
      .catch((error) => console.error("Error al descargar el PDF:", error));
  };

  // List of months
  const months = [
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
  ];

  return (
    <div style={{ padding: "20px" }}>
      <h1>Datos para Informe</h1>

      <form onSubmit={handleSubmit}>
        {/* Main form fields */}
        <div>
          <label>
            Cliente:
            <input
              type="text"
              name="cliente"
              value={formData.cliente}
              onChange={handleChange}
            />
          </label>
        </div>
        <div>
          <label>
            Tecnología:
            <input
              type="text"
              name="tecnologia"
              value={formData.tecnologia}
              onChange={handleChange}
            />
          </label>
        </div>
        <div>
          <label>
            Contrato:
            <input
              type="text"
              name="contrato"
              value={formData.contrato}
              onChange={handleChange}
            />
          </label>
        </div>

        <div>
          <label>
            Mes:
            <select
              name="selectedMonth"
              value={filters.selectedMonth}
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

        {/* File name */}
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

        <button type="submit">Generar Informe</button>
      </form>
    </div>
  );
}

export default App;
