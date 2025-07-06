import { createContext, useState } from "react";
import { runChatLocal } from "../config/backend";

export const Context = createContext();

const ContextProvider = (props) => {
    const [prevPrompts, setPrevPrompts] = useState([]);
    const [input, setInput] = useState("");
    const [recentPrompt, setRecentPrompt] = useState("");
    const [showResult, setShowResult] = useState(false);
    const [loading, setLoading] = useState(false);
    const [resultData, setResultData] = useState("");
    const [chatHistory, setChatHistory] = useState([]);

    function delayPara(index, nextWord) {
        setTimeout(() => {
            setResultData(prev => prev + nextWord);
        }, 75 * index);
    }

    const onSent = async (prompt) => {
        setLoading(true);
        setShowResult(true);
        setResultData("");

        let currentPrompt = prompt || input;
        setRecentPrompt(currentPrompt);
        setPrevPrompts(prev => [...prev, currentPrompt]);

        const responseRaw = await runChatLocal(currentPrompt);

        let response = responseRaw;
        let pdfLink = "";

        // intentar parsear JSON si lo devuelve
        try {
            const parsed = JSON.parse(responseRaw);
            if (parsed.summary) {
                response = parsed.summary;
            }
            if (parsed.pdf_path) {
                pdfLink = `<br/><a href="http://localhost:8000${parsed.pdf_path}" target="_blank">📄 Descargar informe PDF</a>`;
            }
        } catch {
            // no es JSON, asumimos texto plano
        }

        // aplicar formato básico (negritas)
        let responseArray = response.split('**');
        let formatted = "";
        for (let i = 0; i < responseArray.length; i++) {
            if (i === 0 || i % 2 !== 1) {
                formatted += responseArray[i];
            } else {
                formatted += "<b>" + responseArray[i] + "</b>";
            }
        }
        let finalResponse = formatted.split('*').join("</br>") + pdfLink;

        // añadir a historial
        setChatHistory(prev => [
            ...prev,
            { role: "user", content: currentPrompt },
            { role: "bot", content: finalResponse }
        ]);

        // para render animado actual
        const animatedArray = finalResponse.split(" ");
        for (let i = 0; i < animatedArray.length; i++) {
            const nextWord = animatedArray[i];
            delayPara(i, nextWord + " ");
        }

        setLoading(false);
        setInput("");
    };

    const newChat = () => {
        setLoading(false);
        setShowResult(false);
        setChatHistory([]);
        setResultData("");
    };

    const contextValue = {
        prevPrompts,
        setPrevPrompts,
        onSent,
        setRecentPrompt,
        recentPrompt,
        showResult,
        loading,
        resultData,
        input,
        setInput,
        newChat,
        chatHistory,
        setChatHistory
    };

    return (
        <Context.Provider value={contextValue}>
            {props.children}
        </Context.Provider>
    );
};

export default ContextProvider;
