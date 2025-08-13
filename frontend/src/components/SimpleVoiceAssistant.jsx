import { useVoiceAssistant, BarVisualizer, VoiceAssistantControlBar, useTrackTranscription, useLocalParticipant, ParticipantContextIfNeeded } from "@livekit/components-react";
import {Track} from "livekit-client";
import { use, useEffect, useState } from "react";
import "./SimpleVoiceAssistant.css"

const Message = ({type, text}) => { 
     return <div className="message">
        <strong className={`message-${type}`}>
            {type == "agent" ? "Agent: " : "You: "}
        </strong>
        <span className="message-text">{text}</span>
    </div>
}

const SimpleVoiceAssistant = () => {
    const {state, audioTrack, agentTranscriptions} = useVoiceAssistant(); // Hook to manage voice assistant state and audio track
    const localParticipant = useLocalParticipant(); // Hook to access local participant information
    const {segments: userTransciptions} = useTrackTranscription(
        {
        publication: localParticipant.microphoneTrack,
        source: Track.Source.Microphone,
        participant: localParticipant.localParticipant
        }
    ) // Hook to track transcription of the local participant's microphone input

    const [messages, setMessages] = useState([]); 

    useEffect(() => {
        const allMessages = [
            ...(agentTranscriptions?.map(t => ({...t, type:"agent"})) ?? []), // Map agent transcriptions to include type "agent"
            ...(userTransciptions?.map(t => ({...t, type:"user"})) ?? []) // Map user transcriptions to include type "user"
        ].sort((a, b) => a.firstRecieved - b.firstRecieved); // Combine and sort messages by the time they were received

        setMessages(allMessages)
    }, [agentTranscriptions, userTransciptions]) // Effect to update

    return <div className="voice-assistant-container">
        <div className="visualizer-container">
            <BarVisualizer 
            state={state}
            barCount={7}
            trackRef={audioTrack}
            />
        </div>
        <div className="control-section">
            <VoiceAssistantControlBar/>
            <div className="conversation">
                {messages.map((msg, index) => ( <Message key={msg.id || index} type={msg.type} text={msg.text}/>
                ))}
            </div>
        </div>
    </div>
}
export default SimpleVoiceAssistant;