import React from "react";

const Tablas = ({ data, title }) => {

  const columnas = Object.keys(data[0]);

  return (
    <div className="tabla-container">
      <h2>{title}</h2>
      <table className="tabla-tickets">
        <thead>
          <tr>
            {columnas.map((columna, index) => (
              <th key={index}>{columna}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((item, index) => (
            <tr key={index}>
              {columnas.map((columna, i) => (
                <td key={i}>{item[columna]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Tablas;
