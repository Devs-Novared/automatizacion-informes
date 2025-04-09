import React, { useEffect, useState } from "react";
import html2pdf from "html2pdf.js";
import "./styles/pdf.css";
import SquareCard from "../components/SquareCard"

const Pdf = ({ contratosSeleccionado, formData, imageHoras, imageHorasVelocimetro, imageTickets, ticketsUltActServicios, ticketsUltActSoporte, logoCliente, logoTecnologia, acumTicketsActivosSoporte, promHSConsultoria }) => {
  const [fechaTexto, setFechaTexto] = useState("");
  const [year, setYear] = useState("");

  useEffect(() => {
    const fecha = new Date();
    setFechaTexto(
      `Fecha: ${fecha.toLocaleString("es-ES", { month: "long" })} - ${fecha.getFullYear()}`
    );
    setYear(fecha.getFullYear());
  }, []);

  const { cliente, tecnologia, selectedMonth } = formData;
  const { fechaFin, soporteCorrectivo, horasSoporte } = contratosSeleccionado;

  const handleDownloadPDF = () => {
    const downloadButton = document.querySelector(".download-pdf-btn");
    if (!downloadButton) return; 

    downloadButton.style.display = "none"; 

    const element = document.getElementById("pdf-content");
    if (!element) return; 

    const filename = `informe_estado_servicio_${selectedMonth || "mes-no-especificado"}_${year}.pdf`;

    const options = {
      margin: 0,
      filename,
      image: { type: "jpeg", quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true, scrollY: 0 },
      jsPDF: { unit: "mm", format: "a4", orientation: "landscape" }, // Ajuste exacto del tamaño del PDF
      pagebreak: { mode: ["css"] },
    };
    

    html2pdf().from(element).set(options).save().then(() => {
      setTimeout(() => {
        downloadButton.style.display = "block"; // Show the button again after PDF download
      }, 100); // Small delay to ensure it's restored after rendering
    });
  };

  return (
    <div className="container" id="pdf-content">
      {/* Página 1 - Encabezado */}
      <section className="page">
        <h1 style={{ textAlign: "center", marginTop: "215px" }}>Informe Estado del Servicio</h1>
        <h2 id="mes" data-year={year} style={{ textAlign: "center", marginBottom: "100px", marginTop: "80px" }}>
          {selectedMonth ? `Fecha: ${selectedMonth} - ${year}` : fechaTexto}
        </h2>
        <section className="logos">
          {logoTecnologia && (
            <img
              src={`data:image/png;base64,${logoTecnologia}`}
              alt="tecnologia-logo"
              style={{ height: "100px", margin: "10px" }}
            />
          )}
          {logoCliente && (
            <img
              src={`data:image/png;base64,${logoCliente}`}
              alt="cliente-logo"
              style={{ height: "50px", margin: "35px" }}
            />
          )}
          <img 
            src="novaredLogo.png"
            alt="novared-logo"
            style={{ height: "50px", margin: "35px" }} />
        </section>
      </section>

      {/* Página 2 - Objetivos y Soporte */}
      <section className="page">
        <h2 className="titulo-central">Nuestro Objetivo</h2>
        <p className="texto-central" style={{ color: "white" }}>
          Ofrecer a <strong>{cliente || "Cliente no seleccionado"}</strong> un servicio de soporte
          correctivo y evolutivo con la tecnología{" "}
          <strong>{tecnologia || "Tecnología no seleccionada"}</strong>.
        </p>
        <div className="parrafos">
          <div>
            <h3>Soporte Correctivo</h3>
            <hr style={{ color: "#004987" }} />
            <p>
              El servicio contempla la atención, seguimiento y resolución de incidentes o problemas
              generados ante fallas en el funcionamiento de la plataforma.
            </p>
          </div>
          <div>
            <h3>Soporte Evolutivo</h3>
            <hr style={{ color: "#004987" }} />
            <p>
              El servicio de consultoría consiste en brindar asesoramiento o implementar
              funcionalidades o configuraciones que mejoren el uso de la plataforma.
            </p>
          </div>
        </div>
        <div className="informacion-adicional">
          <div>
            <h3>Soporte Correctivo</h3>
            <hr style={{ color: "#00599d" }} />
            <strong style={{ color: "#004987" }}>{soporteCorrectivo || "0"}</strong>
          </div>
          <div>
            <h3>Soporte Evolutivo</h3>
            <hr style={{ color: "#00599d" }} />
            <strong style={{ color: "#004987" }}>
              {horasSoporte ? `${horasSoporte} hrs mensuales No Acumulables` : "0 hrs mensuales No Acumulables"}
            </strong>
          </div>
          <div>
            <h3>Vigencia</h3>
            <hr style={{ color: "#00599d" }} />
            <strong style={{ color: "#004987" }}>{fechaFin || "Sin Dato"}</strong>
          </div>
        </div>
      </section>

      {/* Página 3 - Soporte evolutivo */}
      <section className="page">
        <h1>Soporte Evolutivo</h1>
        <div style={{ display: "flex", marginTop: "20px" }}>
          <div style={{ textAlign: "center" }}>
            {imageHoras && (
              <img
                src={`data:image/png;base64,${imageHoras}`}
                alt="Horas Consumidas"
                style={{ width: "30vw", height: "auto", margin: "10px", borderRadius: "20px", marginBottom: "0px" }}
              />
            )}
          </div>
          <div style={{ textAlign: "center" }}>
            {imageTickets && (
              <img
                src={`data:image/png;base64,${imageTickets}`}
                alt="Tickets Consumidos"
                style={{ width: "30vw", height: "auto", margin: "10px", borderRadius: "20px", marginBottom: "0px" }}
              />
            )}
          </div>
        </div>
        <div style={{ display: "flex"}}>
          <div style={{ textAlign: "center" }}>
            {imageHorasVelocimetro && (
              <img
                src={`data:image/png;base64,${imageHorasVelocimetro}`}
                alt="Horas Consumidas Velocimetro"
                style={{ width: "30vw", height: "auto", margin: "10px", borderRadius: "20px", marginBottom: "0px" }}
              />
            )}
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", width: "30vw", margin: "10px"}}>
            {promHSConsultoria && (
              <SquareCard title={`Promedio horas consumidas - ${selectedMonth}`} number={promHSConsultoria} />
            )}
            {promHSConsultoria && (
              <SquareCard title={`Promedio horas consumidas - ${selectedMonth}`} number={promHSConsultoria} />
            )}
          </div>
        </div>
        
        <h2>Última Actualización de Tickets</h2>
        {ticketsUltActServicios && ticketsUltActServicios.length > 0 ? (
          <table className="tabla-tickets">
            <thead>
              <tr>
                {Object.keys(ticketsUltActServicios[0]).map((key) => (
                  <th key={key}>{key}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {ticketsUltActServicios.map((ticket, index) => (
                <tr key={index}>
                  {Object.values(ticket).map((value, i) => (
                    <td key={i} style={{ backgroundColor: 'rgba(212, 229, 252, 0.74)' }}>{value}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No hay tickets evolutivos con actualización reciente.</p>
        )}
      </section>
      
      {/* Página 4 - Soporte Correctivo */}
      <section className="page">
        <h1 style={{ display: "flex", justifyContent: "center", gap: "1rem", flexWrap: "wrap", marginTop: "2rem" }}>Soporte Correctivo</h1>
        <div style={{ display: "flex", justifyContent: "center", gap: "1rem", flexWrap: "wrap", marginTop: "3rem" }}>
          {ticketsUltActSoporte && (
            <SquareCard title={`Tickets Abiertos - ${selectedMonth}`} number={ticketsUltActSoporte.length} />
          )}
          {acumTicketsActivosSoporte && (
            <SquareCard title={`Tickets cerrados - ${selectedMonth}`} number={acumTicketsActivosSoporte} />
          )}
          {acumTicketsActivosSoporte && (
            <SquareCard title={`Tickets en curso - ${selectedMonth}`} number={acumTicketsActivosSoporte} />
          )}
        </div>
        <div>
          <h2 style={{ display: "flex", justifyContent: "center", gap: "1rem", flexWrap: "wrap", marginTop: "2rem" }}>Última Actualización de Tickets</h2>
          {ticketsUltActSoporte && ticketsUltActSoporte.length > 0 ? (
            <table className="tabla-tickets">
              <thead>
                <tr>
                  {Object.keys(ticketsUltActSoporte[0]).map((key) => (
                    <th key={key}>{key}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {ticketsUltActSoporte.map((ticket, index) => (
                  <tr key={index}>
                    {Object.values(ticket).map((value, i) => (
                      <td key={i} style={{ backgroundColor: 'rgba(212, 229, 252, 0.74)' }}>{value}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div style={{display: "flex"}}>
              <p style={{margin: "auto"}}>No hay tickets correctivos con una actualización reciente.</p>
            </div>
          )}
        </div>
      </section>
      <button onClick={handleDownloadPDF} className="download-pdf-btn no-print">
        Descargar PDF
      </button>
    </div>
  );
};

export default Pdf;
