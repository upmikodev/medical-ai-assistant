import { createContext, useState } from "react";
import runChat from "../config/gemini";

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

        const response = await runChat(currentPrompt);

        // Aplicar formato (negritas y saltos de línea)
        let responseArray = response.split('**');
        let formatted = "";
        for (let i = 0; i < responseArray.length; i++) {
            if (i === 0 || i % 2 !== 1) {
                formatted += responseArray[i];
            } else {
                formatted += "<b>" + responseArray[i] + "</b>";
            }
        }
        const finalResponse = formatted.split('*').join("</br>");

        // Añadir a historial
        setChatHistory(prev => [
            ...prev,
            { role: "user", content: currentPrompt },
            { role: "bot", content: finalResponse }
        ]);

        // Para render animado actual (opcional)
        const animatedArray = finalResponse.split(" ");
        for (let i = 0; i < animatedArray.length; i++) {
            const nextWord = animatedArray[i];
            delayPara(i, nextWord + " ");
        }

        setLoading(false);
        setInput("");
    }

    const newChat = () => {
        setLoading(false);
        setShowResult(false);
        setChatHistory([]); // Limpiar historial si empiezas una conversación nueva
        setResultData("");
    }

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
    }

    return (
        <Context.Provider value={contextValue}>
            {props.children}
        </Context.Provider>
    );
}

export default ContextProvider;
