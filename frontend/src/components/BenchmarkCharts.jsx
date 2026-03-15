import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from "chart.js"

import { Bar } from "react-chartjs-2"

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

function BenchmarkCharts({ results }) {

  if (!results || results.length === 0) return null

  const labels = results.map(r => r.model)

  const latencyData = {
    labels,
    datasets: [
      {
        label: "Average Latency (s)",
        data: results.map(r => r.avg_latency),
        backgroundColor: "rgba(59,130,246,0.7)"
      }
    ]
  }

  const tpsData = {
    labels,
    datasets: [
      {
        label: "Tokens per Second",
        data: results.map(r => r.tokens_per_sec),
        backgroundColor: "rgba(16,185,129,0.7)"
      }
    ]
  }

  const ttftData = {
    labels,
    datasets: [
      {
        label: "Time To First Token (s)",
        data: results.map(r => r.avg_ttft),
        backgroundColor: "rgba(234,179,8,0.7)"
      }
    ]
  }

  return (

    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 mt-8">

      <h2 className="text-xl font-semibold mb-6">
        Benchmark Charts
      </h2>

      <div className="space-y-10">

        <div>
          <Bar data={latencyData} />
        </div>

        <div>
          <Bar data={tpsData} />
        </div>

        <div>
          <Bar data={ttftData} />
        </div>

      </div>

    </div>

  )

}

export default BenchmarkCharts