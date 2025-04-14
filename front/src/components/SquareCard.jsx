const SquareCard = ({ title, number }) => {
    return (
      <div style={{ backgroundColor: "rgba(200, 200, 200, 0.5)", marginRight: "10px", borderRadius: "20px", width:"300px", height:"150px", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "space-between" }} >
        <p style={{ textAlign: "center", margin: "5px" }}>
            {title}
        </p>
        <h1 style={{ flexGrow: 1, display: "flex", alignItems: "center", justifyContent: "center", margin: "0px", fontSize: "73px",  lineHeight: "1", fontWeight: 300 }}>
            {number}
        </h1>
      </div>
    );
  };
  
  export default SquareCard;
  