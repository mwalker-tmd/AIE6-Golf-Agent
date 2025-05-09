import ChatBox from './components/ChatBox'
import './App.css' // Layout styles
import logo from './assets/logo_light_transparent.png'

function App() {
  return (
    <div className="app-root chat-mode">
      <div className="branding">
        <img
          src={logo}
          alt="Golf Caddie Logo"
          className="logo"
        />
        <h1>Golf Caddie AI</h1>
      </div>

      <div className="chat-section">
        <ChatBox />
      </div>
    </div>
  )
}

export default App
