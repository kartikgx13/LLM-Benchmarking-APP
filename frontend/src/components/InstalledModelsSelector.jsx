import { useEffect, useState } from "react"
import { getModels } from "../api/backend"
import { Download, Upload, Play, RotateCcw, FileDown } from "lucide-react"

function InstalledModelsSelector({ selectedModels, setSelectedModels }) {

  const [installedModels, setInstalledModels] = useState([])

  const resetSelection = () => {
  setSelectedModels([])
}

  const fetchInstalledModels = async () => {

    const res = await getModels()

    const installed = res.data.filter(m => m.installed)

    setInstalledModels(installed)
  }

  useEffect(() => {
    fetchInstalledModels()
  }, [])

  const toggleModel = (modelName) => {

    if (selectedModels.includes(modelName)) {

      setSelectedModels(selectedModels.filter(m => m !== modelName))

    } else {

      setSelectedModels([...selectedModels, modelName])

    }

  }

  return (

    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 mt-8">

    <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold mb-4">
  Select Models for Benchmark
  <span className="text-xl font-semibold mb-4 px-4 text-purple-500">
  ({selectedModels.length} selected)
</span>
</h2>

<button
  onClick={resetSelection}
  disabled={selectedModels.length === 0}
  className="flex items-center gap-2 bg-gray-700 hover:bg-gray-600 px-4 py-1 rounded-lg text-sm cursor-pointer disabled:opacity-50"
>
  <RotateCcw size={16} />
  Reset Selection
</button>
    </div>

      <div className="flex flex-wrap gap-4">

        {installedModels.map(model => (

          <label
            key={model.name}
            className="flex items-center gap-2 bg-gray-800 px-4 py-2 rounded-lg cursor-pointer hover:bg-gray-700"
          >

            <input
              type="checkbox"
              checked={selectedModels.includes(model.name)}
              onChange={() => toggleModel(model.name)}
              className="accent-purple-500"
            />

            {model.name}

          </label>

        ))}

      </div>

    </div>
  )

}

export default InstalledModelsSelector