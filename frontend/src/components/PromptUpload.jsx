import { useRef, useState } from "react"
import { uploadPrompts } from "../api/backend"
import { Download, Upload, Play, RotateCcw, FileDown } from "lucide-react"


function PromptUpload() {

  const fileInputRef = useRef(null)

  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState("")
  const [fileName, setFileName] = useState("")

  const handleClick = () => {
    fileInputRef.current.click()
  }

  const handleFileChange = async (e) => {

    const file = e.target.files[0]

    if (!file) return

    setFileName(file.name)

    setUploading(true)
    setMessage("")

    try {

      const res = await uploadPrompts(file)

      setMessage(`Uploaded ${res.data.num_prompts} prompts successfully.`)

    } catch {

      setMessage("Upload failed.")

    }

    setUploading(false)
  }

  return (

    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">

      <h2 className="text-xl font-semibold mb-4 text-gray-200">
        Upload Test Prompts
      </h2>

      <div className="flex items-center gap-4">

        <button
          onClick={handleClick}
          disabled={uploading}
  className="flex items-center gap-2 bg-purple-600 hover:bg-purple-500 px-5 py-2 rounded-lg cursor-pointer disabled:opacity-50"
        >
          <Upload size={16} />
          {uploading ? "Uploading..." : "Upload Prompts"}
        </button>

        {fileName && (
          <span className="text-gray-400 text-sm">
            Chosen file: {fileName}
          </span>
        )}

      </div>

      <input
        type="file"
        accept=".txt"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
      />

      {message && (
        <p className="mt-3 text-sm text-gray-400">
          {message}
        </p>
      )}

    </div>
  )
}

export default PromptUpload