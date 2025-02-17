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
  const [contratosSeleccionado, setContratosSeleccionado] = useState({}); 

  const [isReportReady, setIsReportReady] = useState(false); 

  useEffect(() => {
    const fetchContratos = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:5000/getContratos");
  
        if (response.status === 200) {
          const contratos = response.data.Result;
  
          const contratosUnicos = [...new Set(contratos.map((item) => item.nroContrato.toLowerCase()))];
          const clientesUnicos = [...new Set(contratos.map((item) => item.cliente.toLowerCase()))];
          const tecnologiasUnicas = [...new Set(contratos.map((item) => item.tecnologia.toLowerCase()))];
  
          setListaContrato(contratosUnicos);
          setListaCliente(clientesUnicos);
          setListaTecnologia(tecnologiasUnicas);
  
          const listaAuxiliar = contratos.map(data => ({
            contrato: data.nroContrato.toLowerCase(),
            contentId: data.contentId
          }));
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

    const { cliente, tecnologia, contrato, selectedMonth } = formData;

    let contentIdSeleccionado = listaContentIdContrato.find(
      (dupla) => dupla.contrato === contrato
    )?.contentId;

    const datosAEnviar = {
      cliente,
      tecnologia,
      contrato,
      selectedMonth,
      contentId: contentIdSeleccionado,
    };

    try {
      await axios.post("http://127.0.0.1:5000/selected-data", datosAEnviar);

      const response = await axios.post("http://127.0.0.1:5000/informe", datosAEnviar);
      
      if (response.status === 200) {
        //console.log(response.data, "data")
        //console.log(contratosSeleccionado, "hola")
        setImageHoras(response.data.image_horas);
        setImageTickets(response.data.image_tickets);
        const datosContratos = {...response.data.contratosSeleccionado};
        setContratosSeleccionado(datosContratos);
        setIsReportReady(true);
      }
    } catch (error) {
      console.error("Error al generar el informe:", error);
    }
  };

  const months = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
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

          <button type="submit" onClick={handleSubmit} style={{ margin: '30px' }}>
          Generar Informe
          </button>
      </div>

      {isReportReady && contratosSeleccionado && (
        <Pdf
          contratosSeleccionado={contratosSeleccionado}
          formData={formData}
          imageHoras={imageHoras}
          imageTickets={imageTickets}
        />
      )}
    </>
  );
}

export default App;
