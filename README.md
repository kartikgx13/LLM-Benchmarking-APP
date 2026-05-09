# ⚒️ BenchForge — LLM Benchmarking Studio

**BenchForge** is a modern web application to **test, compare, and benchmark Large Language Models (LLMs)** locally using real-world prompts.

> ⚡ Forge insights. Compare models. Optimize performance.

---

## 📸 Preview

![BenchForge](./frontend/public/assets/screenshots/model-manager.png)

---

## 🚀 Features

### 🔹 Model Management

![Model Manager](./frontend/public/assets/screenshots/model-manager.png)

* View **installed + popular models**
* Download models with **live progress tracking**
* Cancel downloads in real-time
* Delete models easily

---

### 🔹 Search & Download Models

![Search Models](./frontend/public/assets/screenshots/search-model.png)

* Add and validate models dynamically
* Real-time download progress with stats
* Clean UI for managing external models

---

### 🔹 Single Prompt Testing

![Single Prompt](./frontend/public/assets/screenshots/single-prompt.png)

![Single Prompt Response](./frontend/public/assets/screenshots/single-prompt-ans.png)

* Quickly test a single prompt across models
* Ideal for **quick comparisons and debugging**

---

### 🔹 Benchmark Runner (Core Feature)

![Upload Prompts](./frontend/public/assets/screenshots/upload-prompt.png)

![Select Models](./frontend/public/assets/screenshots/select-models.png)

![Benchmark Results](./frontend/public/assets/screenshots/results-latency.png)

Run structured benchmarks across multiple prompts and models:

1. Upload prompt file (`.txt`)
2. Select installed models
3. Run benchmark

---

### 📊 Metrics Captured

![Latency](./frontend/public/assets/screenshots/results-latency.png)

![Tokens/sec](./frontend/public/assets/screenshots/results-token-speed.png)

![Export View](./frontend/public/assets/screenshots/results-latency.png)

* ⏱️ **Latency**
* ⚡ **Time to First Token (TTFT)**
* 🔢 **Tokens per second**

---

### 📈 Visualization & Export

![TTFT](./frontend/public/assets/screenshots/results-ttft.png)

* Interactive charts for comparison
* Export results as:

  * CSV
  * JSON

---

## 🧱 Tech Stack

### Frontend

* React (Vite)
* Tailwind CSS
* Lucide Icons
* React Hot Toast

### Backend

* FastAPI (Python)
* Server-Sent Events (SSE)
* Ollama API

---

## ⚙️ Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/benchforge.git
cd benchforge
```

---

### 2️⃣ Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Runs on:

```
http://127.0.0.1:8000
```

---

## 🧩 MCP Server (Model Context Protocol)

This repo includes an MCP server that exposes BenchForge functionality as **MCP tools** (stdio transport).

### Run the MCP server

```bash
cd backend
pip install -r requirements.txt
python -m mcp_server.server
```

### Available MCP tools

- `backend_info`
- `ollama_health`
- `list_ollama_models`
- `get_prompts` / `set_prompts`
- `run_ollama_benchmark`
- `run_unified_benchmark`
- `test_prompt_ollama`

### Example MCP client config

See `backend/mcp_server/mcp.example.json` for a ready-to-copy config snippet.

### 3️⃣ Install Ollama

Download:
👉 https://ollama.com

Start server:

```bash
ollama serve
```

---

### 4️⃣ Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Runs on:

```
http://localhost:5173
```

---

## 📂 Project Structure

```
benchforge/
│
├── backend/
│   ├── routes/
│   ├── services/
│   └── main.py
│
├── frontend/
│   ├── components/
│   ├── api/
│   └── App.jsx
│
└── README.md
```

---

## 🔄 How It Works

### 🔹 Model Download

* Uses Ollama `/api/pull`
* Streams progress via SSE

---

### 🔹 Benchmark Flow

1. Upload prompts
2. Models run sequentially
3. Metrics collected
4. Results streamed in real-time

---

### 🔹 Real-Time Streaming

BenchForge uses **SSE (Server-Sent Events)** to:

* Track model download progress
* Stream benchmark execution updates

---

## 🧠 Design Philosophy

* **Task-driven UI** → Focus on workflows, not features
* **Real-time feedback** → No blind waiting
* **Local-first** → Privacy-friendly, no cloud dependency
* **Developer-first** → Transparent and simple

---

## ⚠️ Known Limitations

* Ollama does not provide a direct model validation API
* Validation occurs during download
* Single benchmark execution at a time

---

## 🚀 Future Roadmap

* 🔍 Model search + autocomplete
* 📦 Download queue system
* 📊 Benchmark history
* ⚡ Parallel benchmarking
* 🧠 Smart model recommendations

---

## 🤝 Contributing

```bash
git checkout -b feature/your-feature
git commit -m "Add feature"
git push origin feature/your-feature
```

Pull requests are welcome!

---

## 📜 License

MIT License

---

## 👨‍💻 Author

**Kartik Gavande**

---

## ⭐ Support

If you like BenchForge, consider giving it a star ⭐
It helps a lot!
