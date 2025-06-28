import React, { useState, useContext } from 'react';
import './Voice.css';
import { Context } from '../../context/Context';
import mic_icon from '../../assets/mic_icon.png';

const Voice = () => {
    const { setInput } = useContext(Context);
    const [isListening, setIsListening] = useState(false);

    const handleVoiceInput = () => {
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.onstart = () => {
            setIsListening(true);
        };

        recognition.onend = () => {
            setIsListening(false);
        };

        recognition.onresult = (event) => {
            const speechResult = event.results[0][0].transcript;
            setInput(speechResult);
        };

        recognition.start();
    };

    return (
        <div className="voice-container">
            <button className="voice-btn" onClick={handleVoiceInput} disabled={isListening}>                
                <img src={mic_icon} alt="" />
            </button>
        </div>
    );
};

export default Voice;
