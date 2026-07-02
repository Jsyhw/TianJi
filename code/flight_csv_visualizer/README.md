# FlightCSVVisualizer

FlightCSVVisualizer is a lightweight desktop tool for comparing aircraft or flight simulation CSV data. It loads one or more CSV files, draws a 3D trajectory, displays the default 3 x 3 velocity/attitude/angular-rate plots, and supports custom comparison plots.

## Run

```powershell
cd D:\szt\NKUpro\study\TianJiVision\code\flight_csv_visualizer
python main.py
```

## Test

```powershell
pytest
```

## Package

```powershell
scripts\build_windows.bat
```

The first release uses PyInstaller folder mode for faster startup and more reliable dependency loading.
