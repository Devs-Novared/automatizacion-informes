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
  const [imageTickets, setImageTickets] = useState("");
  const [contratosSeleccionado, setContratosSeleccionado] = useState({});
  const [isReportReady, setIsReportReady] = useState(false);
  const [error, setError] = useState(""); 
  const [ticketsMensual, setTicketsMensual] = useState([]); // Estado para los tickets
  const [ticketsUltAct, setTicketsUltAct] = useState([]);
  const [logoCliente, setLogoCliente] = useState("");
  const [logoTecnologia, setLogoTecnologia] = useState("");

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

    const { cliente, tecnologia, contrato, selectedMonth } = formData;

    let contentIdSeleccionado = listaContentIdContrato.find(
      (dupla) => dupla.nroContrato === contrato
    )?.contentId;

    const datosAEnviar = {
      cliente,
      tecnologia,
      contrato,
      selectedMonth,
      contentId: contentIdSeleccionado,
    };

    try {
      const response = await axios.post("http://127.0.0.1:5000/informe", datosAEnviar);
      console.log(response.data)
      
      if (response.status === 200) {
        setImageHoras(response.data.image_horas);
        setImageTickets(response.data.image_tickets);
        setLogoCliente(response.data.logoCliente)
        setLogoTecnologia(response.data.logoTecnologia)
        setContratosSeleccionado(response.data.contratosSeleccionado);
        setTicketsMensual(response.data.tickets_mensual_Cerrados || []); // Agregar tickets
        setTicketsUltAct(response.data.tickets_ult_act || []);
        
        setIsReportReady(true);
        setError(""); 
      }
    } catch (error) {
      console.error("Error al generar el informe:", error);
      setError("Hubo un error al generar el informe. Intente nuevamente.");
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

      {isReportReady && contratosSeleccionado && (
        <Pdf
          contratosSeleccionado={contratosSeleccionado}
          formData={formData}
          imageHoras={imageHoras}
          imageTickets={imageTickets}
          ticketsMensual={ticketsMensual} // Pasamos los tickets al PDF
          ticketsUltAct={ticketsUltAct}
          logoCliente={logoCliente}
          logoTecnologia={logoTecnologia}
        />
      )}
    </>
  );
}

export default App;
