export function exportJSON(results) {

  const blob = new Blob(
    [JSON.stringify(results, null, 2)],
    { type: "application/json" }
  )

  const url = URL.createObjectURL(blob)

  const a = document.createElement("a")

  a.href = url
  a.download = "benchmark_results.json"

  a.click()

  URL.revokeObjectURL(url)
}



export function exportCSV(results) {

  const headers = ["Model", "TTFT", "Latency", "Tokens/sec"]

  const rows = results.map(r => [
    r.model,
    r.avg_ttft,
    r.avg_latency,
    r.tokens_per_sec
  ])

  const csvContent =
    [headers, ...rows]
      .map(row => row.join(","))
      .join("\n")

  const blob = new Blob([csvContent], { type: "text/csv" })

  const url = URL.createObjectURL(blob)

  const a = document.createElement("a")

  a.href = url
  a.download = "benchmark_results.csv"

  a.click()

  URL.revokeObjectURL(url)
}