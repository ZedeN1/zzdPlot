# ZZD Convergence Dashboard

A high-performance Dash application for visualizing and analyzing ZZD simulation result files. This tool helps engineers quickly identify convergence issues, model instability, and fatal crashes without parsing massive log files manually.

### Key Features

* **⚡ High-Speed Parsing:** Uses optimized Regex iterators and memory mapping to parse large binary-encoded ZZD files in seconds.
* **📈 Convergence Analysis:** Interactive plots for Discharge (DQ) and Head (DH) convergence violations with configurable tolerance thresholds (QTOL/HTOL).
* **⚠️ Warning Heatmaps:** Visualizes the temporal distribution of model warnings (W2000, E1999, etc.) to pinpoint instability "hotspots."
* **🔍 "Binned" Scatter Plots:** Uses a hybrid binning algorithm to ensure even single-event warnings are visible on long-duration timelines.
* **🐳 Docker Ready:** Fully containerized with a production-grade Gunicorn server setup.

### Usage

The dashboard accepts raw `.zzd` files via drag-and-drop. It automatically infers simulation start/end times and highlights fatal errors if the model crashed.

* **HTOL Input:** Filter Head tolerance violations (default: 0.01m).
* **QTOL Input:** Filter Flow tolerance violations (default: 0.01m³/s).
