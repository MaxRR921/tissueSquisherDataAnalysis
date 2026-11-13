"""CSV export for collected experiment data."""

import csv

import numpy as np


def generateCsvs(stageQueue, powermeter, polarimeter):
    """Export collected device data to CSV files in the working directory."""
    micrometerArray = []
    powermeter1Array = []
    powermeter2Array = []
    if stageQueue is not None:
        while not stageQueue.csvQueue.empty():
            micrometerArray.append(stageQueue.csvQueue.get())

    if powermeter is not None:
        while not powermeter.device1CsvQueue.empty():
            powermeter1Array.append(powermeter.device1CsvQueue.get())

        while not powermeter.device2CsvQueue.empty():
            powermeter2Array.append(powermeter.device2CsvQueue.get())

    if micrometerArray:
        with open("micrometertime.csv", mode="w", newline="") as f:
            writer = csv.writer(f)
            # Optionally, write a header row first:
            writer.writerow(["position (mm)", "time (seconds since jan 1 1975)"])
            # Each element of the tuple goes into its own CSV column
            for row_tuple in micrometerArray:
                writer.writerow(row_tuple)

    if powermeter1Array:
        with open("power1time.csv", mode="w", newline="") as f:
            writer = csv.writer(f)
            # Optionally, write a header row first:
            writer.writerow(["power 1 (W)", "time (seconds since jan 1 1975)"])
            # Each element of the tuple goes into its own CSV column
            for row_tuple in powermeter1Array:
                writer.writerow(row_tuple)

    if powermeter2Array:
        with open("power2time.csv", mode="w", newline="") as f:
            writer = csv.writer(f)
            # Optionally, write a header row first:
            writer.writerow(["power 2 (W)", "time (seconds since jan 1 1975)"])
            # Each element of the tuple goes into its own CSV column
            for row_tuple in powermeter2Array:
                writer.writerow(row_tuple)

        # ──────────────────────────────────────────────────────────────
        # 1.  Read the first column of each CSV and convert to float
        # ──────────────────────────────────────────────────────────────
        powermeter1CalcArray, powermeter2CalcArray = [], []

        for file_name, target in [
            ("power1time.csv", powermeter1CalcArray),
            ("power2time.csv", powermeter2CalcArray),
        ]:
            with open(file_name, mode="r", newline="") as f:
                reader = csv.reader(f)
                for row in reader:
                    if not row:  # skip blank lines
                        continue
                    try:
                        target.append(float(row[0]))
                    except ValueError:  # skip header / malformed
                        continue

        # Convert to NumPy for vector math

        pm1 = np.array(powermeter1CalcArray, dtype=float)
        pm2 = np.array(powermeter2CalcArray, dtype=float)

        min_len = min(pm1.size, pm2.size)
        pm1 = pm1[:min_len]
        pm2 = pm2[:min_len]

        # ──────────────────────────────────────────────────────────────
        # 2.  Compute power difference
        # ──────────────────────────────────────────────────────────────
        powerdifference = pm1 - pm2  # ΔP = P₁ – P₂

    if polarimeter is not None:
        if (
            polarimeter.dataAnalyzer.phase is not None
            and polarimeter.dataAnalyzer.strain is not None
        ):
            with open("polarimetertime.csv", mode="w", newline="") as f:
                writer = csv.writer(f)
                print(f"Phase: {polarimeter.dataAnalyzer.phase}")
                print(f"Strain: {polarimeter.dataAnalyzer.strain}")
                writer.writerow(["phase", "strain"])
                for phase_val, strain_val in zip(
                    polarimeter.dataAnalyzer.phase,
                    polarimeter.dataAnalyzer.strain,
                ):
                    writer.writerow([phase_val, strain_val])
                polarimeter.dataAnalyzer.strain = None
                polarimeter.dataAnalyzer.phase = None
