import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";
import Pdf from "./pages/Pdf";
import Formulario from "./pages/Formulario";

function App() {
  const [listaContrato, setListaContrato] = useState([]);
  const [listaCliente, setListaCliente] = useState([]);
  const [listaTecnologia, setListaTecnologia] = useState([]);
  const [listaContentIdContrato, setListaContentIdContrato] = useState([]);

  const [formData, setFormData] = useState({
    cliente: "",
    tecnologia: "",
    contrato: "",
    selectedMonth: "",
  });

  const [nombre_archivo, setNombre_archivo] = useState("reporte.pdf");

  const [imageHoras, setImageHoras] = useState(""); // Estado para la imagen de horas
  const [imageTickets, setImageTickets] = useState(""); // Estado para la imagen de tickets
  const [contratosInfo, setContratosInfo] = useState(""); 

  useEffect(() => {
    const fetchContratos = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:5000/getContratos");

        if (response.status === 200) {
          const contratos = response["data"]["Result"];

          const contratosUnicos = [...new Set(contratos.map((item) => item.nroContrato))];
          const clientesUnicos = [...new Set(contratos.map((item) => item.cliente))];
          const tecnologiasUnicas = [...new Set(contratos.map((item) => item.tecnologia))];

          setListaContrato(contratosUnicos);
          setListaCliente(clientesUnicos);
          setListaTecnologia(tecnologiasUnicas);

          const listaAuxiliar = [];

          for (let data of contratos) {
            const dupla = {
              contrato: data.nroContrato,
              contentId: data.contentId,
            };

            listaAuxiliar.push(dupla);
          }
          setListaContentIdContrato(listaAuxiliar);
        } else {
          console.error("Error al obtener datos:", response.statusText);
        }
      } catch (error) {
        console.error("Error en la solicitud:", error);
      }
    };

    fetchContratos();
  }, []);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevState) => ({
      ...prevState,
      [name]: value,
    }));
  };

  const handleFileNameChange = (e) => {
    let fileName = e.target.value;
    if (!fileName.endsWith(".pdf")) {
      fileName += ".pdf";
    }
    setNombre_archivo(fileName);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const clienteSeleccionado = formData.cliente;
    const tecnologiaSeleccionada = formData.tecnologia;
    const contratoSeleccionado = formData.contrato;
    const mesSeleccionado = formData.selectedMonth;
    let contentIdSeleccionado;

    for (let dupla of listaContentIdContrato) {
      if (dupla.contrato === contratoSeleccionado) {
        contentIdSeleccionado = dupla.contentId;
      }
    }

    const datosAEnviar = {
      cliente: clienteSeleccionado,
      tecnologia: tecnologiaSeleccionada,
      contrato: contratoSeleccionado,
      selectedMonth: mesSeleccionado,
      contentId: contentIdSeleccionado,
    };

    try {
      // Enviar datos al endpoint /selected-data
      await axios.post("http://127.0.0.1:5000/selected-data", datosAEnviar);

      // Solicitar las imágenes al endpoint /informe
      const response = await axios.post("http://127.0.0.1:5000/informe", datosAEnviar);

      if (response.status === 200) {
        setContratosInfo(response.data.contratosInfo);
        console.log(contratosInfo)
        setImageHoras(response.data.image_horas); // Guardar imagen de horas en base64
        setImageTickets(response.data.image_tickets); // Guardar imagen de tickets en base64
      }
    } catch (error) {
      console.error("Error al generar el informe:", error);
    }
  };

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
    <>
      <div style={{ padding: "20px" }}>
        <h1>Datos para Informe</h1>

        <Formulario
          formData={formData}
          handleFilterChange={handleFilterChange}
          listaCliente={listaCliente}
          listaTecnologia={listaTecnologia}
          listaContrato={listaContrato}
          months={months}
          nombre_archivo={nombre_archivo}
          handleFileNameChange={handleFileNameChange}
        />

        <button type="submit" onClick={handleSubmit}>
          Generar Informe
        </button>
      </div>

      {/* Renderizar el componente Pdf con los datos del formulario y las imágenes */}
      {formData.cliente &&
        formData.tecnologia &&
        formData.contrato &&
        formData.selectedMonth && (
          <Pdf
            contratosInfo={contratosInfo}
            formData={formData}
            imageHoras={imageHoras}
            imageTickets={imageTickets}
          />
        )}
    </>
  );
}

export default App;
