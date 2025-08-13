import { useState } from 'react'
import './App.css'
import LiveKitModal from './components/liveKitModal.jsx'

function App() {
  const [showSupport, setShowSupport] = useState(false); // State to control the visibility of the support modal
  const handleSupportClick = () => { // Function to handle the support button click
    setShowSupport(true);
  };



  return (
    <>
      <div className="App">
        <header className='header'>
          <div className='logo'>Auto Center</div>
        </header>
        <main>
          <section className='hero'>
            <h1>Get Your required service and parts the right way. Right Now</h1>
            <p>Free Next day Delivery on Eligible orders</p>
            <div className='search-bar'>
              <input type="text" placeholder='Enter Vehicle'></input>
              <button className='search-button'>Search</button>
            </div>
          </section>
          <button className='support-button' onClick={handleSupportClick}>Talk to an Agent!</button> 
        </main>
        {showSupport && <LiveKitModal setShowSupport={setShowSupport} />} 
      </div>
    </>
  )
}

export default App
