import {useState, useCallback} from "react";
import {LiveKitRoom, RoomAudioRenderer} from "@livekit/components-react";
import "@livekit/components-styles"
import SimpleVoiceAssistant from "./SimpleVoiceAssistant";

const LiveKitModal = ({setShowSupport}) => {
    const [isSubmittingName, setIsSubmittingName] = useState(true); // State to track if the user is submitting their name
    const[name, setName] = useState(""); // State to hold the user's name
    const [token, setToken] = useState(null) // State to hold the LiveKit token
    const [error, setError] = useState(null); // State to hold any errors
    
    const getToken = useCallback(async(userName)=>  {
        try {
            setError(null); // Clear any previous errors
            console.log(`Fetching token for user: ${userName}`); // Debug logging
            
            // Use environment variable for API URL
            const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5001';
            const response = await fetch(`${apiUrl}/getToken?name=${encodeURIComponent(userName)}`);
            
            console.log(`Response status: ${response.status}`); // Debug logging
            console.log(`Response headers:`, response.headers.get('content-type')); // Debug logging
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            // Always expect plain text JWT token response
            const tokenData = await response.text();
            
            // Verify it looks like a JWT (should have 3 parts separated by dots)
            if (!tokenData || tokenData.split('.').length !== 3) {
                throw new Error('Invalid JWT token received');
            }
            
            console.log(`Received JWT token: ${tokenData.substring(0, 50)}...`); // Debug logging (partial token)
            
            setToken(tokenData); // Set the token state with the fetched token
            setIsSubmittingName(false);
        } catch (error) {
            console.error("Error fetching token:", error);
            setError(`Failed to get token: ${error.message}`);
        }
    }, [])
    
    const handleSubmit = (e) => { // Function to handle the name submission
        e.preventDefault()
        if(name.trim()) {
            getToken(name); // Fetch the token using the provided name
        }
    }
    
    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <div className="support-room">
                    {isSubmittingName ? (
                        <form onSubmit={handleSubmit} className="name-form"> {/* If the user is submitting their name, show the form */}
                            <h2>Enter your name to connect with support</h2>
                            {error && <div className="error-message" style={{color: 'red', marginBottom: '10px'}}>{error}</div>}
                            <input 
                                type="text" 
                                value={name} 
                                onChange={(e) => setName(e.target.value)} 
                                placeholder="Your Name" 
                                required
                            /> {/* Input field for the user's name */}
                            <button type="submit">Connect</button>
                            <button type="button" className="cancel-button" onClick={() => setShowSupport(false)}>Cancel</button> {/* Cancel button to close the modal */}
                        </form>
                    ) : token ? ( // If the user has submitted their name, show the LiveKitRoom component
                        <LiveKitRoom
                            serverUrl={import.meta.env.VITE_LIVEKIT_URL} // LiveKit server URL from environment variable
                            token={token} // Token for authentication
                            video={false}
                            audio={true}
                            onDisconnected={() => {
                                setShowSupport(false)
                                setIsSubmittingName(true)
                                setToken(null)
                                setError(null)
                            }}
                        >
                           <RoomAudioRenderer/>
                           <SimpleVoiceAssistant/>
                        </LiveKitRoom>
                    ) : (
                        <div>Loading...</div>
                    )}
                </div>
            </div>
        </div>
    )
}

export default LiveKitModal;