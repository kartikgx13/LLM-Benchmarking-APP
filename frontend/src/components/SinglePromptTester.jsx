import { useEffect, useState, useRef } from "react"
import { getModels } from "../api/backend"
import toast from "react-hot-toast"

function SinglePromptTester({ refreshTrigger }) {

  const [models, setModels] = useState([])
  const [selectedModel, setSelectedModel] = useState("")
  const [prompt, setPrompt] = useState("")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [eventSource, setEventSource] = useState(null)

  const responseRef = useRef(null)

  // Fetch installed models
  const fetchModels = async () => {
    try {
      const res = await getModels()
      const installed = res.data.filter(m => m.installed)

      setModels(installed)
      setSelectedModel("")
    } catch {
      toast.error("Failed to load models")
    }
  }

  useEffect(() => {
    fetchModels()
  }, [refreshTrigger])

  // Auto scroll
  useEffect(() => {
    if (responseRef.current) {
      responseRef.current.scrollTop = responseRef.current.scrollHeight
    }
  }, [result?.response])

  // Run prompt (streaming)
  const handleRun = () => {

    if (!selectedModel) {
      toast.error("Please select a model")
      return
    }

    if (!prompt.trim()) {
      toast.error("Enter a prompt")
      return
    }

    setLoading(true)
    setResult(null)

    let fullText = ""

    const source = new EventSource(
      `http://127.0.0.1:8000/prompt/test-stream?model=${selectedModel}&prompt=${encodeURIComponent(prompt)}`
    )

    setEventSource(source)

    source.onmessage = (event) => {

      const data = JSON.parse(event.data)

      // streaming tokens
      if (data.token) {
        fullText += data.token

        setResult(prev => ({
          ...(prev || {}),
          response: fullText
        }))
      }

      // done
      if (data.done) {
        setResult(prev => ({
          ...(prev || {}),
          metrics: data.metrics
        }))

        setLoading(false)
        source.close()
        setEventSource(null)
      }
    }

    source.onerror = () => {
      toast.error("Streaming failed")
      setLoading(false)
      source.close()
      setEventSource(null)
    }
  }

  // Stop streaming
  const handleStop = () => {
    if (eventSource) {
      eventSource.close()
      setEventSource(null)
      setLoading(false)
      toast("Generation stopped")
    }
  }

  // Copy response
  const handleCopy = () => {
    if (result?.response) {
      navigator.clipboard.writeText(result.response)
      toast.success("Copied to clipboard")
    }
  }

  return (

    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 mt-10">

      <h2 className="text-xl font-semibold mb-4">
        Test Single Prompt
      </h2>

      {/* Input Bar */}
      <div className="flex items-center gap-3 bg-gray-800 border border-gray-700 rounded-xl p-3">

        {/* Dropdown */}
        <div className="relative w-40">

          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="appearance-none w-full bg-gray-900 border border-gray-600 rounded-lg px-3 py-2 pr-8 text-gray-200"
          >
            <option value="">Select Model</option>

            {models.map(m => (
              <option key={m.name} value={m.name}>
                {m.name}
              </option>
            ))}

          </select>

          <div className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-gray-400">
            ▼
          </div>

        </div>

        {/* Prompt Input */}
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Type your prompt..."
          className="flex-1 bg-transparent outline-none text-gray-200 px-2"
          onKeyDown={(e) => {
            if (e.key === "Enter") handleRun()
          }}
        />

        {/* Run / Stop Button */}
        <button
          onClick={loading ? handleStop : handleRun}
          className={`px-4 py-2 rounded-lg flex items-center justify-center ${
            loading
              ? "bg-red-600 hover:bg-red-500"
              : "bg-purple-600 hover:bg-purple-500"
          }`}
        >
          {loading ? (
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          ) : (
            "Run ▶"
          )}
        </button>

      </div>

      {/* Result Section */}
      {result && (

        <div
          ref={responseRef}
          className="mt-6 bg-gray-800 p-4 rounded-lg max-h-64 overflow-y-auto"
        >

          {/* Header */}
          <div className="flex justify-between items-center mb-2">

            <h3 className="text-lg text-gray-200">
              Response
            </h3>

            <button
              onClick={handleCopy}
              className="text-sm bg-gray-700 hover:bg-gray-600 px-3 py-1 rounded"
            >
              Copy
            </button>

          </div>

          {/* Response */}
          <p className="text-gray-300 whitespace-pre-wrap">
            {result?.response}

            {loading && (
              <span className="inline-block w-2 h-4 ml-1 bg-purple-400 animate-pulse"></span>
            )}
          </p>

          {/* Metrics */}
          {result?.metrics && (
            <div className="mt-4 border-t border-gray-700 pt-3 text-sm text-green-800 font-bold">

              <p>Latency: {result.metrics.latency.toFixed(2)}s</p>
              <p>TTFT: {result.metrics.ttft.toFixed(2)}s</p>
              <p>Tokens/sec: {result.metrics.tokens_per_sec.toFixed(2)}</p>
              <p>Total tokens: {result.metrics.tokens}</p>

            </div>
          )}

        </div>

      )}

    </div>
  )
}

export default SinglePromptTester