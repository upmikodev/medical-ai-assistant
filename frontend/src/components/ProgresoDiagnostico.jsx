import { useEffect, useState } from "react";

function ProgresoDiagnostico() {
  const [logs, setLogs] = useState("");
  const [pdfName, setPdfName] = useState("");

  useEffect(() => {
    const interval = setInterval(() => {
      fetch("http://localhost:8000/progress")
        .then((res) => res.text())
        .then((data) => {
          setLogs(data);

          const match = data.match(/reporte_\w+\.pdf/i);
          if (match) {
            setPdfName(match[0]);
          }
        })
        .catch((err) => console.error("Error obteniendo progreso:", err));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ background: "#f9f9f9", marginTop: "1rem", padding: "1rem", borderRadius: "8px", border: "1px solid #ddd" }}>
      <h3>Progreso del diagnóstico</h3>
      <pre style={{ whiteSpace: "pre-wrap", fontSize: "0.9rem" }}>{logs}</pre>
      {pdfName && (
        <a
          href={`http://localhost:8000/download/${pdfName}`}
          download
          style={{ display: "inline-block", marginTop: "1rem", padding: "0.5rem 1rem", backgroundColor: "#007bff", color: "#fff", borderRadius: "4px", textDecoration: "none" }}
        >
          Descargar informe PDF
        </a>
      )}
    </div>
  );
}

export default ProgresoDiagnostico;
