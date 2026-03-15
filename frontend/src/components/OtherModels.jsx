import { useState } from "react"
import { Download, Plus } from "lucide-react"
import toast from "react-hot-toast"
import { validateModel } from "../api/backend"

function OtherModels({refreshModels}) {

  const [models, setModels] = useState([])
  const [inputModel, setInputModel] = useState("")
  const [downloadProgress, setDownloadProgress] = useState({})
  const [downloadStats, setDownloadStats] = useState({})

  const formatGB = (bytes) => {
    return (bytes / (1024 ** 3)).toFixed(2)
  }

  const addModel = async () => {

  const model = inputModel.trim()

  if (!model) return

  if (models.includes(model)) {
    toast.error("Model already added")
    return
  }

  try {

    const res = await validateModel(model)

    if (!res.data.valid) {
      toast.error(`Model "${model}" does not exist on Ollama`)
      return
    }

    // Only add card if valid
    setModels(prev => [...prev, model])

    setInputModel("")

  } catch {

    toast.error("Failed to validate model")

  }

}

  const handleDownload = (model) => {

    const source = new EventSource(
      `http://127.0.0.1:8000/models/download-stream?model=${model}`
    )

source.onmessage = (event) => {

  const data = JSON.parse(event.data)

  // ❌ Invalid model
  if (data.error) {

    toast.error(`Model "${model}" does not exist on Ollama`)

    source.close()

    // remove card
    setModels(prev => prev.filter(m => m !== model))

    return
  }

  // progress updates
  if (data.completed && data.total) {

    const percent = Math.floor(
      (data.completed / data.total) * 100
    )

    setDownloadProgress(prev => ({
      ...prev,
      [model]: percent
    }))

    setDownloadStats(prev => ({
      ...prev,
      [model]: {
        completed: formatGB(data.completed),
        total: formatGB(data.total)
      }
    }))
  }

  // success
  if (data.status === "success") {

    source.close()

    setModels(prev => prev.filter(m => m !== model))

    setDownloadProgress(prev => {
      const updated = { ...prev }
      delete updated[model]
      return updated
    })

    setDownloadStats(prev => {
      const updated = { ...prev }
      delete updated[model]
      return updated
    })

    refreshModels()
  }
}
  }

  return (

    <div className="mt-10">

      <h2 className="text-2xl font-semibold mb-6 text-gray-200">
        Other Models
      </h2>

      {/* Input section */}

      <div className="flex gap-3 mb-6">

        <input
          type="text"
          placeholder="Enter Ollama model name (ex: qwen2.5)"
          value={inputModel}
          onChange={(e) => setInputModel(e.target.value)}
          className="bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-gray-200 w-80"
        />

        <button
          onClick={addModel}
          className="flex items-center gap-2 bg-purple-600 hover:bg-purple-500 px-4 py-2 rounded-lg"
        >
          <Plus size={16}/>
          Add Model
        </button>

      </div>

      {/* Model cards */}

      <div className="flex gap-6 overflow-x-auto py-4 px-4">

        {models.map((model) => (

          <div
            key={model}
            className="min-w-[300px] bg-gray-900 border border-gray-800 rounded-xl p-5 flex flex-col gap-4"
          >

            <h3 className="text-lg font-semibold">
              {model}
            </h3>

            {downloadProgress[model] !== undefined ? (

              <div>

                <div className="w-full bg-gray-800 rounded-full h-3">

                  <div
                    className="bg-purple-500 h-3 rounded-full transition-all duration-300"
                    style={{
                      width: `${downloadProgress[model]}%`
                    }}
                  />

                </div>

                <p className="text-xs text-gray-400 mt-1 text-center">

                  Downloading... {downloadProgress[model]}%

                  {downloadStats[model] && (
                    <> • {downloadStats[model].completed}GB / {downloadStats[model].total}GB</>
                  )}

                </p>

              </div>

            ) : (

              <button
                onClick={() => handleDownload(model)}
                className="flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 py-2 rounded-lg"
              >
                <Download size={16}/>
                Download Model
              </button>

            )}

          </div>

        ))}

      </div>

    </div>

  )
}

export default OtherModels