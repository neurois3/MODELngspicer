# ModelNgspicer

**ModelNgspicer** is a Python-based GUI tool for real-time circuit simulation and parameter tuning using Ngspice. Designed to accelerate device modeling and circuit design, it offers an intuitive interface for iterative adjustment, visualization, and comparison.

## 🚀 Features

- Adjust model parameters via an interactive GUI
- Run real-time simulations using Ngspice
- Plot simulation results with overlay support for comparison data

## 🖥️ System Requirements

To ensure proper functionality of **ModelNgspicer**, the following system configuration is recommended:

- **Operating System**: Windows 10 or later (64-bit)  
- **Python**: Version 3.13 or later  
- **Required packages**: PySide6, PyQtGraph, numpy  
- **Ngspice**: Version 43 or later is recommended

⚠️ Currently, ModelNgspicer is tested primarily on Windows. Compatibility with other platforms may vary.

## 🛠️ Installation (Windows)

To set up **ModelNgspicer** on Windows, follow these steps using [Chocolatey](https://chocolatey.org/)

1. Install Python and Ngspice

```powershell
choco install python
choco install ngspice
```

2. Install required Python packages

```bash
pip install PySide6 pyqtgraph numpy

```

3. Launch ModelNgspicer

Run the `run.vbs` script located in the project folder to start the application.

## 📄 License

This project is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html). You are free to use, modify, and distribute the software under the terms of this license.
