
import numpy as np
import re
import json
from pathlib import Path


def parse_circuit_file(filename):
    """Parse the SPICE circuit file to extract component values."""
    components = {}
    
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('L'):
                # Extract inductor value
                parts = line.split()
                if len(parts) >= 4:
                    value_str = parts[3]
                    value = parse_spice_value(value_str)
                    components['L'] = value
            elif line.startswith('C'):
                # Extract capacitor value
                parts = line.split()
                if len(parts) >= 4:
                    value_str = parts[3]
                    value = parse_spice_value(value_str)
                    components['C'] = value
            elif line.startswith('R'):
                # Extract resistor value
                parts = line.split()
                if len(parts) >= 4:
                    value_str = parts[3]
                    value = parse_spice_value(value_str)
                    components['R'] = value
    
    return components

def parse_spice_value(value_str):
    """Parse SPICE value with units (e.g., '159.15u' -> 159.15e-6)."""
    # Remove any whitespace
    value_str = value_str.strip()
    
    # Define unit multipliers
    units = {
        'f': 1e-15,  # femto
        'p': 1e-12,  # pico
        'n': 1e-9,   # nano
        'u': 1e-6,   # micro
        'm': 1e-3,   # milli
        'k': 1e3,    # kilo
        'meg': 1e6,  # mega
        'g': 1e9,    # giga
        't': 1e12,   # tera
    }
    
    # Try to match number followed by unit
    match = re.match(r'([+-]?\d*\.?\d+)([a-zA-Z]*)', value_str)
    if match:
        number = float(match.group(1))
        unit = match.group(2).lower()
        
        if unit in units:
            return number * units[unit]
        else:
            return number
    
    return float(value_str)

def calculate_transfer_function(freq, L, C, R):
    """Calculate the transfer function of RLC band pass filter."""
    omega = 2 * np.pi * freq
    
    # Impedances
    Z_L = 1j * omega * L
    Z_C = 1 / (1j * omega * C)
    Z_R = R
    
    # Total impedance
    Z_total = Z_L + Z_C + Z_R
    
    # Transfer function H(jω) = V_out/V_in = Z_R / Z_total
    H = Z_R / Z_total
    
    return H

def create_html_chart(freq, magnitude_db, phase_deg, components, circuit_filename, f0):
    """Create an HTML file with Chart.js visualization."""
    
    # Convert numpy arrays to lists for JSON serialization
    freq_mhz = (freq / 1e6).tolist()
    magnitude_data = magnitude_db.tolist()
    phase_data = phase_deg.tolist()
    
    # Create data points for Chart.js
    magnitude_points = [{'x': f, 'y': m} for f, m in zip(freq_mhz, magnitude_data)]
    phase_points = [{'x': f, 'y': p} for f, p in zip(freq_mhz, phase_data)]
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Band Pass Filter - Frequency Response</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .chart-container {{
            position: relative;
            height: 400px;
            margin: 20px 0;
        }}
        .info-panel {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .component-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }}
        .component {{
            background-color: white;
            padding: 10px;
            border-radius: 4px;
            border-left: 4px solid #007bff;
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
        h2 {{
            color: #666;
            border-bottom: 2px solid #007bff;
            padding-bottom: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>1MHz Band Pass Filter - Frequency Response</h1>
        <p style="text-align: center; color: #666;">Circuit: {Path(circuit_filename).name}</p>
        
        <div class="info-panel">
            <h2>Circuit Components</h2>
            <div class="component-info">
                <div class="component">
                    <strong>Inductor (L)</strong><br>
                    {components.get('L', 159.15e-6)*1e6:.2f} µH
                </div>
                <div class="component">
                    <strong>Capacitor (C)</strong><br>
                    {components.get('C', 159.15e-12)*1e12:.2f} pF
                </div>
                <div class="component">
                    <strong>Resistor (R)</strong><br>
                    {components.get('R', 50)} Ω
                </div>
                <div class="component">
                    <strong>Resonant Frequency</strong><br>
                    {f0/1e6:.3f} MHz
                </div>
            </div>
        </div>

        <div class="chart-container">
            <canvas id="magnitudeChart"></canvas>
        </div>
        
        <div class="chart-container">
            <canvas id="phaseChart"></canvas>
        </div>
    </div>

    <script>
        // Magnitude Chart
        const magnitudeCtx = document.getElementById('magnitudeChart').getContext('2d');
        const magnitudeChart = new Chart(magnitudeCtx, {{
            type: 'line',
            data: {{
                datasets: [{{
                    label: 'Magnitude (dB)',
                    data: {json.dumps(magnitude_points)},
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    pointRadius: 0,
                    pointHoverRadius: 4
                }}, {{
                    label: 'Resonant Frequency',
                    data: [{{x: {f0/1e6:.3f}, y: Math.max(...{json.dumps(magnitude_data)})}}],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgb(255, 99, 132)',
                    borderWidth: 2,
                    pointRadius: 6,
                    showLine: false
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Magnitude Response'
                    }},
                    legend: {{
                        display: true
                    }}
                }},
                scales: {{
                    x: {{
                        type: 'logarithmic',
                        display: true,
                        title: {{
                            display: true,
                            text: 'Frequency (MHz)'
                        }},
                        min: 0.001,
                        max: 100
                    }},
                    y: {{
                        display: true,
                        title: {{
                            display: true,
                            text: 'Magnitude (dB)'
                        }}
                    }}
                }},
                interaction: {{
                    intersect: false,
                    mode: 'index'
                }}
            }}
        }});

        // Phase Chart
        const phaseCtx = document.getElementById('phaseChart').getContext('2d');
        const phaseChart = new Chart(phaseCtx, {{
            type: 'line',
            data: {{
                datasets: [{{
                    label: 'Phase (degrees)',
                    data: {json.dumps(phase_points)},
                    borderColor: 'rgb(255, 159, 64)',
                    backgroundColor: 'rgba(255, 159, 64, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    pointRadius: 0,
                    pointHoverRadius: 4
                }}, {{
                    label: 'Resonant Frequency',
                    data: [{{x: {f0/1e6:.3f}, y: 0}}],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgb(255, 99, 132)',
                    borderWidth: 2,
                    pointRadius: 6,
                    showLine: false
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Phase Response'
                    }},
                    legend: {{
                        display: true
                    }}
                }},
                scales: {{
                    x: {{
                        type: 'logarithmic',
                        display: true,
                        title: {{
                            display: true,
                            text: 'Frequency (MHz)'
                        }},
                        min: 0.001,
                        max: 100
                    }},
                    y: {{
                        display: true,
                        title: {{
                            display: true,
                            text: 'Phase (degrees)'
                        }}
                    }}
                }},
                interaction: {{
                    intersect: false,
                    mode: 'index'
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    
    return html_content

def plot_frequency_response(components, circuit_filename):
    """Plot the frequency response of the band pass filter."""
    # Extract component values
    L = components.get('L', 159.15e-6)  # Default values if not found
    C = components.get('C', 159.15e-12)
    R = components.get('R', 50)
    
    print(f"Circuit components:")
    print(f"L = {L*1e6:.2f} µH")
    print(f"C = {C*1e12:.2f} pF") 
    print(f"R = {R} Ω")
    
    # Calculate resonant frequency
    f0 = 1 / (2 * np.pi * np.sqrt(L * C))
    print(f"Resonant frequency: {f0/1e6:.3f} MHz")
    
    # Create frequency range (1 kHz to 100 MHz)
    freq = np.logspace(3, 8, 1000)  # 1 kHz to 100 MHz
    
    # Calculate transfer function
    H = calculate_transfer_function(freq, L, C, R)
    
    # Calculate magnitude and phase
    magnitude_db = 20 * np.log10(np.abs(H))
    phase_deg = np.angle(H) * 180 / np.pi
    
    # Create HTML chart
    html_content = create_html_chart(freq, magnitude_db, phase_deg, components, circuit_filename, f0)
    
    # Save the HTML file
    output_filename = 'bandpass_filter_response_tett.html'
    with open(output_filename, 'w') as f:
        f.write(html_content)
    
    print(f"\nInteractive chart saved as: {output_filename}")
    print("Open this file in a web browser to view the frequency response charts.")
    
    return freq, magnitude_db, phase_deg

def main(circuit_file):
    print("Processing circuit file:", circuit_file)
    
    # Check if circuit file exists
    if not Path(circuit_file).exists():
        print(f"Error: Circuit file '{circuit_file}' not found!")
        return
    
    print(f"Reading circuit file: {circuit_file}")
    
    components = parse_circuit_file(circuit_file)
    print("Components found:", components)
    
    plot_frequency_response(components, circuit_file)

def python_run(circuit):
    """Main function to run the circuit analysis."""
    # Write circuit.cir file in python
    circuit_file = 'bandpass_filter_1mhz.cir'
    
    with open(circuit_file, 'w') as f:
        f.write(circuit)
    
    main(circuit_file)

python_run("""
.subckt filter 1 2 3
L1 1 2 159.15u
C1 2 3 159.15p
R1 3 1 50
.ends filter
""")

