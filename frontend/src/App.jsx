import { useEffect, useState } from "react"
import { healthCheck } from "./api/backend"
import ModelManager from "./components/ModelManager"
import PromptUpload from "./components/PromptUpload"
import BenchmarkRunner from "./components/BenchmarkRunner"
import InstalledModelsSelector from "./components/InstalledModelsSelector"
import OtherModels from "./components/OtherModels"
import { Toaster } from "react-hot-toast"

function App() {

  const [status, setStatus] = useState(null)
  const [selectedModels, setSelectedModels] = useState([])
  const [modelRefresh, setModelRefresh] = useState(0)

  const refreshModels = () => {
  setModelRefresh(prev => prev + 1)
}

  useEffect(() => {
    healthCheck()
      .then(res => setStatus(res.data))
      .catch(() => setStatus({ backend: "offline" }))
  }, [])

  return (
<div className="min-h-screen bg-gray-950 text-gray-100">

  <div className="max-w-6xl mx-auto p-8">

    <h1 className="text-4xl font-bold mb-8 text-white">
      LLM Benchmarking Dashboard
    </h1>
<ModelManager refreshTrigger={modelRefresh} />

<OtherModels refreshModels={refreshModels} />

<Toaster
    position="top-right"
    toastOptions={{
      style: {
        background: "#1f2937",
        color: "#fff",
      },
    }}
  />

<div className="mt-12">
  <PromptUpload />
</div>

<InstalledModelsSelector
  selectedModels={selectedModels}
  setSelectedModels={setSelectedModels}
/>

<BenchmarkRunner selectedModels={selectedModels} />
  </div>

</div>
  )
}

export default App