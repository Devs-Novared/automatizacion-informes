import React, { useEffect, useState } from "react";
import "./App.css";

function App() {

  //useEffect(async () => { 
    //const respuesta = await fetch("http://127.0.0.1:5000/getContratos", {  // Asegúrate de que la URL esté correcta
      //method: "GET",
      //headers: {
        //"Content-Type": "application/json",
      //}})

      //lista sin repetir
    //setListaContrato (respuesta.contrato)
    //})

  

  const [listaContrato, setListaContrato] = useState([])
  
  const [listaCliente, setListaCliente] = useState([])

  const [listaTecnologia, setListaTecnologia] = useState([])

  // State for basic form data
  const [formData, setFormData] = useState({
    cliente: "",
    tecnologia: "",
    contrato: "",
    selectedMonth: "",
  });

  useEffect(() => {
    const respuesta = async () => {
      try {
        const respuesta = await fetch("http://127.0.0.1:5000/getContratos", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (respuesta.ok) {
          const datos = await respuesta.json();

          // Suponiendo que los datos tienen esta estructura:
          // [{ contrato: 'A', cliente: 'Cliente1', tecnologia: 'Tecnologia1' }, ...]

          // Procesar listas sin duplicados
          const contratosUnicos = [...new Set(datos.map((item) => item.contrato))];
          const clientesUnicos = [...new Set(datos.map((item) => item.cliente))];
          const tecnologiasUnicas = [...new Set(datos.map((item) => item.tecnologia))];

          // Actualizar estados
          setListaContrato(contratosUnicos);
          setListaCliente(clientesUnicos);
          setListaTecnologia(tecnologiasUnicas);
        } else {
          console.error("Error al obtener datos:", respuesta.statusText);
        }
      } catch (error) {
        console.error("Error en la solicitud:", error);
      }
    };

    respuesta();
  }, []);

  


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
            <select
              name="cliente"
              value={formData.cliente}
              onChange={handleFilterChange}
            >
              <option value="" disabled>
                Selecciona el Cliente
              </option>
              {listaCliente.map((listaCliente, index) => (
                <option key={index} value={listaCliente}>
                  {listaCliente}
                </option>
              ))}
            </select>
          </label>
        </div>
        <div>
          <label>
            Tecnologia:
            <select
              name="tecnologia"
              value={formData.tecnologia}
              onChange={handleFilterChange}
            >
              <option value="" disabled>
                Selecciona una Tecnologia
              </option>
              {listaTecnologia.map((listaTecnologia, index) => (
                <option key={index} value={listaTecnologia}>
                  {listaTecnologia}
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
              {listaContrato.map((listaContrato, index) => (
                <option key={index} value={listaContrato}>
                  {listaContrato}
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
