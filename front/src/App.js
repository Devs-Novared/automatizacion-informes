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

  const [imageHoras, setImageHoras] = useState("");
  const [imageHorasVelocimetro, setImageHorasVelocimetro] = useState("");
  const [imageTickets, setImageTickets] = useState("");
  const [contratosSeleccionado, setContratosSeleccionado] = useState({});
  const [isReportReady, setIsReportReady] = useState(false);
  const [error, setError] = useState(""); 
  const [ticketsUltActSoporte, setTicketsUltActSoporte] = useState([]);
  const [ticketsUltActServicios, setTicketsUltActServicios] = useState([]);
  const [logoCliente, setLogoCliente] = useState("");
  const [logoTecnologia, setLogoTecnologia] = useState("");
  const [acumTicketsAbiertosSoporte, setacumTicketsAbiertosSoporte] = useState("");
  const [acumTicketsCerradosSoporte, setacumTicketsCerradosSoporte] = useState("");
  const [acumTicketsActivosSoporte, setacumTicketsActivosSoporte] = useState("");
  const [promHSConsultoria, setPromHSConsultoria] = useState("");
  const [horasRestantesConsultoria, setHorasRestantesConsultoria] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  

  useEffect(() => {
    const fetchContratos = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:5000/getContratos");

        if (response.status === 200) {
          const contratos = response.data.Result;
          setListaCliente([...new Set(contratos.map((item) => item.cliente.toLowerCase()))]);
          setListaTecnologia([...new Set(contratos.map((item) => item.tecnologia.toLowerCase()))]);
          setListaContrato([...new Set(contratos.map((item) => item.nroContrato.toLowerCase()))]);

          setListaContentIdContrato(contratos.map(data => ({
            cliente: data.cliente.toLowerCase(),
            tecnologia: data.tecnologia.toLowerCase(),
            nroContrato: data.nroContrato.toLowerCase(),
            contentId: data.contentId
          })));
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
    setError(""); 
  };

  const validarFormulario = () => {
    const { cliente, tecnologia, contrato, selectedMonth } = formData;
    if (!cliente || !tecnologia || !contrato || !selectedMonth) {
      setError("Todos los campos deben estar seleccionados antes de generar el informe.");
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validarFormulario()) return;

    setIsLoading(true); // Mostrar el popup de carga

    const { cliente, tecnologia, contrato, selectedMonth } = formData;
    let contentIdSeleccionado = listaContentIdContrato.find(
      (dupla) => dupla.nroContrato === contrato
    )?.contentId;

    const datosAEnviar = { selectedMonth, contentId: contentIdSeleccionado };

    try {
      const response = await axios.post("http://127.0.0.1:5000/informe", datosAEnviar);
      if (response.status === 200) {
        setImageHoras(response.data.image_horas);
        setImageHorasVelocimetro(response.data.image_horas_velocimetro);
        setImageTickets(response.data.image_tickets);
        setLogoCliente(response.data.logoCliente)
        setLogoTecnologia(response.data.logoTecnologia)
        setacumTicketsAbiertosSoporte(response.data.acumTicketsAbiertosSoporte)
        setacumTicketsCerradosSoporte(response.data.acumTicketsCerradosSoporte)
        setacumTicketsActivosSoporte(response.data.acumTicketsActivosSoporte)
        setContratosSeleccionado(response.data.contratosSeleccionado);
        setPromHSConsultoria(response.data.promHSConsultoria);
        setHorasRestantesConsultoria(response.data.horasRestantesConsultoria);
        setTicketsUltActSoporte(response.data.tickets_ult_act_soporte || []);
        setTicketsUltActServicios(response.data.tickets_ult_act_servicios || []);
        console.log(response.data)
        setIsReportReady(true);
        setError(""); 
      }
    } catch (error) {
      console.error("Error al generar el informe:", error);
      setError("Hubo un error al generar el informe. Intente nuevamente.");
    } finally {
      setIsLoading(false); // Ocultar el popup de carga cuando termine la solicitud
    }
  };

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
          listaContentIdContrato={listaContentIdContrato}
        />

        {error && <p style={{ color: "red" }}>{error}</p>}

        <button type="submit" onClick={handleSubmit} style={{ margin: "30px" }}>
          Generar Informe
        </button>
      </div>

      {isLoading && (
        <div className="popup-loading">
          <div className="popup-content">
            <p>Generando informe...</p>
          </div>
        </div>
      )}

      {isReportReady && contratosSeleccionado && (
        <Pdf
          contratosSeleccionado={contratosSeleccionado}
          formData={formData}
          imageHoras={imageHoras}
          imageHorasVelocimetro={imageHorasVelocimetro}
          imageTickets={imageTickets}
          ticketsUltActServicios={ticketsUltActServicios}
          ticketsUltActSoporte={ticketsUltActSoporte}
          logoCliente={logoCliente}
          logoTecnologia={logoTecnologia}
          acumTicketsAbiertosSoporte={acumTicketsAbiertosSoporte}
          acumTicketsCerradosSoporte={acumTicketsCerradosSoporte}
          acumTicketsActivosSoporte={acumTicketsActivosSoporte}
          promHSConsultoria={promHSConsultoria}
          horasRestantesConsultoria={horasRestantesConsultoria}
        />
      )}
    </>
  );
}

export default App;
