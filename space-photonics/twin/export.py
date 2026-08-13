"""
Export Digital Twin results to CSV/Excel for external analysis.
"""

import json
import csv
from pathlib import Path
from typing import List, Dict


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
    """Flatten nested dictionary for CSV export."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def export_to_csv(json_path: str, csv_path: str):
    """
    Export JSON results to CSV.
    
    Args:
        json_path: Path to simulation results JSON
        csv_path: Output CSV path
    """
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    results = data['results']
    
    if not results:
        print("No data to export")
        return
    
    # Flatten all records
    flat_records = [flatten_dict(r) for r in results]
    
    # Get all field names
    fieldnames = list(flat_records[0].keys())
    
    # Write CSV
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flat_records)
    
    print(f"Exported {len(flat_records)} records to {csv_path}")
    print(f"Columns: {', '.join(fieldnames[:10])}...")


def export_summary(json_path: str, txt_path: str):
    """Export summary statistics to text file."""
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    results = data['results']
    
    # Compute statistics
    import numpy as np
    
    snrs = [r['optical']['snr_db'] for r in results if np.isfinite(r['optical']['snr_db'])]
    rx_powers = [r['optical']['rx_power_dbm'] for r in results if np.isfinite(r['optical']['rx_power_dbm'])]
    pointing_errors = [r['optical']['pointing_error'] for r in results]
    
    with open(txt_path, 'w') as f:
        f.write("Space Photonics Digital Twin - Summary Report\n")
        f.write("="*60 + "\n\n")
        
        f.write(f"Simulation Duration: {results[-1]['time']:.3f} s\n")
        f.write(f"Data Points: {len(results)}\n\n")
        
        f.write("Optical Link Performance\n")
        f.write("-"*40 + "\n")
        f.write(f"Mean SNR: {np.mean(snrs):.2f} dB\n")
        f.write(f"Min SNR: {np.min(snrs):.2f} dB\n")
        f.write(f"Max SNR: {np.max(snrs):.2f} dB\n")
        f.write(f"SNR Std: {np.std(snrs):.2f} dB\n\n")
        
        f.write(f"Mean RX Power: {np.mean(rx_powers):.2f} dBm\n")
        f.write(f"Min RX Power: {np.min(rx_powers):.2f} dBm\n")
        f.write(f"Max RX Power: {np.max(rx_powers):.2f} dBm\n\n")
        
        f.write("Tracking Performance\n")
        f.write("-"*40 + "\n")
        f.write(f"Mean Pointing Error: {np.mean(pointing_errors):.4f}°\n")
        f.write(f"Max Pointing Error: {np.max(pointing_errors):.4f}°\n")
        f.write(f"Final Pointing Error: {pointing_errors[-1]:.4f}°\n")
    
    print(f"Summary exported to {txt_path}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Export simulation results")
    parser.add_argument('input', help='Input JSON file')
    parser.add_argument('--csv', help='Output CSV file')
    parser.add_argument('--summary', help='Output summary text file')
    
    args = parser.parse_args()
    
    if args.csv:
        export_to_csv(args.input, args.csv)
    
    if args.summary:
        export_summary(args.input, args.summary)
    
    if not args.csv and not args.summary:
        # Default: export both
        base = Path(args.input).stem
        export_to_csv(args.input, f"{base}.csv")
        export_summary(args.input, f"{base}_summary.txt")
