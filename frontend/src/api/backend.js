import axios from "axios"

const API = axios.create({
  baseURL: "http://127.0.0.1:8000"
})

export const getModels = () => API.get("/models/catalog")

export const downloadModel = (model) =>
  API.post(`/models/download?model=${model}`)

export const uploadPrompts = (file) => {
  const formData = new FormData()
  formData.append("file", file)

  return API.post("/prompts/upload", formData)
}

export const runBenchmark = (models) =>
  API.post("/benchmark/run", { models })

export function streamBenchmark(models) {

  const params = new URLSearchParams()

  models.forEach(m => params.append("models", m))

  const url = `http://127.0.0.1:8000/benchmark/stream?${params.toString()}`

  return new EventSource(url)

}

export async function deleteModel(model) {

  return axios.delete("http://127.0.0.1:8000/models/delete", {
    params: { model }
  })

}

export async function validateModel(model) {

  return axios.get("http://127.0.0.1:8000/models/validate", {
    params: { model }
  })

}

export const healthCheck = () => API.get("/health")