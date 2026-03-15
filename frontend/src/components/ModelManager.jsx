import { useEffect, useState } from "react"
import { getModels, deleteModel } from "../api/backend"
import { Download, Trash } from "lucide-react"

function ModelManager({refreshTrigger}) {

  const [models, setModels] = useState([])
  const [downloadProgress, setDownloadProgress] = useState({})
  const [downloadStats, setDownloadStats] = useState({})

  const fetchModels = async () => {
    const res = await getModels()
    setModels(res.data)
  }

  useEffect(() => {
  fetchModels()
}, [refreshTrigger])

  const formatGB = (bytes) => {
    return (bytes / (1024 ** 3)).toFixed(2)
  }

  const handleDownload = (model) => {

    const source = new EventSource(
      `http://127.0.0.1:8000/models/download-stream?model=${model}`
    )

    source.onmessage = (event) => {

      const data = JSON.parse(event.data)

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

      if (data.status === "success") {

        source.close()

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

        fetchModels()
      }
    }
  }

  const handleDelete = async (model) => {

    const confirmDelete = window.confirm(
      `Are you sure you want to delete ${model}?`
    )

    if (!confirmDelete) return

    try {

      await deleteModel(model)

      fetchModels()

    } catch {

      alert("Failed to delete model")

    }
  }

  return (

    <div className="mt-10">

      <h2 className="text-2xl font-semibold mb-6 text-gray-200">
        Models (Popular + Installed)
      </h2>

      <div className="flex gap-6 overflow-x-auto py-4 px-4 scroll-smooth">

        {models.map((model) => (

          <div
            key={model.name}
            className="min-w-[300px] bg-gray-900 border border-gray-800 rounded-xl p-5 flex flex-col gap-4 hover:border-gray-600 hover:scale-[1.02] transition"
          >

            <div className="flex justify-between items-center">

              <h3 className="text-lg font-semibold">
                {model.name}
              </h3>

              {model.installed ? (
                <span className="bg-green-900 text-green-300 px-2 py-1 text-sm rounded">
                  Installed
                </span>
              ) : (
                <span className="bg-gray-800 text-gray-400 px-2 py-1 text-sm rounded">
                  Not Installed
                </span>
              )}

            </div>

            {model.installed ? (

              /* DELETE BUTTON */

              <button
                onClick={() => handleDelete(model.full_name)}
                className="flex items-center justify-center gap-2 bg-red-600 hover:bg-red-500 text-white py-2 rounded-lg transition cursor-pointer"
              >
                <Trash size={16} />
                Delete Model
              </button>

            ) : downloadProgress[model.name] !== undefined ? (

              /* PROGRESS BAR */

              <div>

                <div className="w-full bg-gray-800 rounded-full h-3">

                  <div
                    className="bg-purple-500 h-3 rounded-full transition-all duration-300"
                    style={{
                      width: `${downloadProgress[model.name]}%`
                    }}
                  />

                </div>

                <p className="text-xs text-gray-400 mt-1 text-center">

                  Downloading... {downloadProgress[model.name]}%

                  {downloadStats[model.name] && (
                    <> • {downloadStats[model.name].completed}GB / {downloadStats[model.name].total}GB</>
                  )}

                </p>

              </div>

            ) : (

              /* DOWNLOAD BUTTON */

              <button
                onClick={() => handleDownload(model.name)}
                className="flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white py-2 rounded-lg transition cursor-pointer"
              >
                <Download size={16} />
                Download Model
              </button>

            )}

          </div>

        ))}

      </div>

    </div>

  )
}

export default ModelManager