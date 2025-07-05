import React, { useContext } from 'react';
import './Main.css';
import { assets } from '../../assets/assets';
import { Context } from '../../context/Context';
import ProgresoDiagnostico from '../ProgresoDiagnostico';

const Main = () => {
  const {
    onSent,
    recentPrompt,
    showResult,
    loading,
    resultData,
    setInput,
    input,
    chatHistory
  } = useContext(Context);

  return (
    <div className='main'>
      <div className="nav">
        <p>Juanan</p>
        <img src={assets.user_icon} alt="" />
      </div>

      <div className="main-container">
        {chatHistory.length > 0 ? (
          <div className="result-history">
            {chatHistory.map((msg, i) => (
              <div key={i} className="result">
                <div className="result-title">
                  <img src={msg.role === 'user' ? assets.user_icon : assets.gemini_icon} alt="" />
                  <p dangerouslySetInnerHTML={{ __html: msg.content }} />
                </div>
              </div>
            ))}
            {loading && (
              <div className="result">
                <div className="result-title">
                  <img src={assets.gemini_icon} alt="" />
                  <div className="loader">
                    <hr className="animated-bg" />
                    <hr className="animated-bg" />
                    <hr className="animated-bg" />
                  </div>
                </div>
              </div>
            )}
            {/* progreso en vivo */}
            {showResult && <ProgresoDiagnostico />}
          </div>
        ) : (
          <>
            <div className="greet">
              <p><span>Hola Doctor,</span></p>
              <p>¿Cómo puedo ayudarte?</p>
            </div>
            <div className="cards">
              <div className="card">
                <p>Analiza una imagen de resonancia magnética y detecta zonas tumorales</p>
                <img src={assets.compass_icon} alt="" />
              </div>
              <div className="card">
                <p>Explica cómo funciona el modelo DenseNet121 en este contexto clínico</p>
                <img src={assets.bulb_icon} alt="" />
              </div>
              <div className="card">
                <p>Realiza la segmentación del tumor utilizando UNet</p>
                <img src={assets.message_icon} alt="" />
              </div>
              <div className="card">
                <p>Resume el caso clínico a partir del análisis de la imagen</p>
                <img src={assets.code_icon} alt="" />
              </div>
            </div>
          </>
        )}

        <div className="main-bottom">
          <div className="search-box">
            <input
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && input.trim() !== "") {
                  onSent();
                }
              }}
              value={input}
              type="text"
              placeholder="Escribe tu consulta aquí..."
            />
            <div>
              <img src={assets.gallery_icon} width={30} alt="" />
              <img src={assets.mic_icon} width={30} alt="" />
              {input && (
                <img onClick={() => onSent()} src={assets.send_icon} width={30} alt="Enviar" />
              )}
            </div>
          </div>
          <p className="bottom-info">
            Este asistente está en fase experimental. Consulta siempre con especialistas médicos.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Main;
