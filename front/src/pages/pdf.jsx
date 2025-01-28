import React, { useEffect, useState } from "react";
import "./styles/pdf.css";

const Pdf = ({contratosInfo, formData, imageHoras, imageTickets,}) => {
  const [fechaTexto, setFechaTexto] = useState("");
  const [year, setYear] = useState("");

  useEffect(() => {
    const fecha = new Date();
    setFechaTexto(
      `Fecha: ${fecha.toLocaleString("es-ES", { month: "long" })} - ${fecha.getFullYear()}`
    );
    setYear(fecha.getFullYear());
  }, []);

  const { cliente, tecnologia, contrato, selectedMonth } = formData;
  const { fechaFin, soporteCorrectivo } = contratosInfo;

  return (
    <div className="container">
      <header>
        <h1>Informe Estado del Servicio</h1>
        <h2 id="mes" data-year={year}>
          {selectedMonth ? `Mes: ${selectedMonth} - ${year}` : fechaTexto}
        </h2>
      </header>

      {/* Sección de logos agregada antes del primer section */}
      <section className="logos">
        <img src="logo1.png" alt="tecnologia-logo" />
        <img src="logo2.png" alt="cliente-logo" />
        <img src="../pages/images/novaredLogo.png" alt="novared-logo" />
      </section>

      <section>
        <h2 className="titulo-central">Nuestro Objetivo</h2>
        <p className="texto-central">
          Ofrecer a <strong>{cliente || "Cliente no seleccionado"}</strong> un servicio de soporte
          correctivo y evolutivo sobre la plataforma{" "}
          <strong>{tecnologia || "Tecnología no seleccionada"}</strong>.
        </p>
        <div className="parrafos">
          <h3>Soporte Correctivo</h3>
          <hr style={{ color: "#004987" }} />
          <p>
            El servicio contempla la atención, seguimiento y resolución de incidentes o problemas
            generados ante fallas en el funcionamiento de la plataforma, cuando la misma no opere
            conforme a las especificaciones del fabricante.
          </p>
          <h3>Soporte Evolutivo</h3>
          <hr style={{ color: "#004987" }} />
          <p>
            El alcance del servicio de consultoría consiste en brindar asesoramiento o implementar
            funcionalidades o configuraciones que mejoren el uso de los productos incluidos en el
            soporte brindado por Novared.
          </p>
        </div>
      </section>

      <section className="informacion-adicional">
        <div>
          <h3>Soporte Correctivo</h3>
          <hr style={{ color: "#004987" }} />
          <p>{contrato || "Contrato no seleccionado"}</p>
        </div>
        <div>
          <h3>Soporte Evolutivo</h3>
          <hr style={{ color: "#004987" }} />
          <strong>{soporteCorrectivo}</strong>
        </div>
        <div>
          <h3>Vigencia</h3>
          <hr style={{ color: "#004987" }} />
          <strong>{fechaFin}</strong>
        </div>
      </section>

      {/* Agregar los gráficos */}
      <section>
        {imageHoras && (
          <div>
            <img src={`data:image/png;base64,${imageHoras}`} alt="Horas Consumidas" />
          </div>
        )}
        {imageTickets && (
          <div>
            <img src={`data:image/png;base64,${imageTickets}`} alt="Tickets Consumidos" />
          </div>
        )}
      </section>

      <div className="footer-logo">
        <img src="" alt="logo-novared-pie" />
      </div>

      <footer></footer>
    </div>
  );
};

export default Pdf;
