const Container = ({ children }) => {
    return (
      <div 
        style={{
          width: "500px", 
          height: "300px",
          display: "flex",
          flexWrap: "wrap",
          alignContent: "flex-start",
          gap: "10px", 
          backgroundColor: "rgba(200, 200, 200, 0.5)",
          padding: "10px",
          borderRadius: "10px"
        }}
      >
        {children}
      </div>
    );
  };
  