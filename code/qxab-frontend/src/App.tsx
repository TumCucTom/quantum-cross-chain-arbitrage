import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import ArbitrageDashboard from './components/ArbitageDashboard';

function App() {

  return (
    <>
      <div className="App">
      <header>
        <h1>Quantum-Enhanced Cross-Chain Arbitrage Bot (QXAB)</h1>
      </header>
      <main>
        <ArbitrageDashboard />
      </main>
    </div>
    </>
  )
}

export default App
