LLM Benchmarking App

A lightweight benchmarking tool designed to evaluate the performance of locally running Large Language Models (LLMs). This project allows developers to compare different models across key performance metrics to better understand their speed and efficiency during inference.

This tool is especially useful when working with local LLMs through Ollama or other local inference frameworks, helping developers choose the best model for their applications.

Features

Benchmark multiple LLMs

Measure important performance metrics

Compare different models easily

Lightweight and simple to run

Easily extendable for additional models

Metrics Measured

The benchmarking tool records the following metrics:

Average Latency

Average time taken by the model to generate a response.

TTFT (Time To First Token)

Measures how quickly the model begins generating output after receiving the prompt.

Tokens Per Second

Speed of token generation during response generation.

Total Time Taken

Total time required to complete the full response.

Supported Models

The tool can benchmark any locally running model. Example models tested include:

llama3.2

mistral

phi

Additional models can easily be added.

Project Structure
LLM-Benchmarking-App
│
├── benchmarking
│   ├── benchmark_model.py
│   ├── model_comparison.py
│
├── structured_output
│   ├── schema.py
│
├── results
│   ├── benchmark_results.csv
│
├── README.md
└── requirements.txt
Installation
1 Clone the repository
git clone https://github.com/Kartikg13/LLM-Benchmarking-APP.git
cd LLM-Benchmarking-APP
2 Create virtual environment
python -m venv .venv

Activate environment:

Mac / Linux

source .venv/bin/activate

Windows

.venv\Scripts\activate
3 Install dependencies
pip install -r requirements.txt
Running the Benchmark

Run the model comparison script:

python benchmarking/model_comparison.py

The script will run inference across all configured models and record performance metrics.

Example Output
Benchmark Results

Model        Average Latency    TTFT    Tokens/sec    Total Time
---------------------------------------------------------------
llama3.2     12.37              0.33        30.73        123.76
mistral      18.53              0.62        13.08        185.39
phi          9.42               0.28        35.10        94.20
How It Works

A prompt is sent to the selected model

The response stream is monitored

Timing metrics are recorded

Results are aggregated across multiple runs

Final performance statistics are displayed

Use Cases

This project is useful for:

Evaluating local LLM performance

Comparing models before deploying them

Optimizing AI assistants

Benchmarking inference speed

Testing hardware performance with LLMs

Future Improvements

Possible improvements include:

GPU utilization tracking

Memory usage benchmarking

Visualization dashboards

Benchmark result graphs

Web interface for running benchmarks

Automatic model discovery

Contributing

Contributions are welcome.

If you would like to improve the project:

1 Fork the repository
2 Create a new branch
3 Submit a pull request

License

This project is licensed under the MIT License.

Author

Kartik Gavande

GitHub
https://github.com/kartikgx13

⭐ If you find this project useful, consider starring the repository.
