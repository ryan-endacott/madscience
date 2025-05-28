# Whale Stranding Dual-Cue Hypothesis Analysis

## 🐋 Overview

This repository tests a novel hypothesis for pilot whale mass strandings: that the co-occurrence of specific magnetic field gradients and acoustic conditions creates "navigation traps" leading to mass stranding events.

**⚠️ SURPRISING DISCOVERY**: Initial analysis revealed that stranding sites have POSITIVE (landward-increasing) magnetic gradients, opposite to the original hypothesis! This suggests whales may be trapped by magnetic fields that strengthen toward shore.

## 📊 Key Findings

| Location | Magnetic Gradient | Stranding History |
|----------|------------------|-------------------|
| Farewell Spit, NZ | **+20.35 nT/km** | Major hotspot |
| Cape Cod, USA | **+1.93 nT/km** | Major hotspot |
| Dutch Wadden Sea | **-2.55 nT/km** | No mass strandings |

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/whale-stranding-dual-cue.git
cd whale-stranding-dual-cue

# Install dependencies
pip install -r requirements.txt

# Download NOAA data
# Visit: https://www.fisheries.noaa.gov/s3fs-public/2022-08/LargeWhales_2005to2015.csv
# Save as: LargeWhales_2005to2015.csv

# Run analysis
python whale_stranding_quick_test.py

# Visualize magnetic gradients
python magnetic_gradient_visualizer.py
```

## 📁 Repository Structure

```
whale-stranding-dual-cue/
├── README.md                          # This file
├── EXPERIMENT_DESIGN.md               # Detailed experimental design
├── requirements.txt                   # Python dependencies
├── data/
│   ├── magnetic_gradients.csv        # Measured magnetic field data
│   └── LargeWhales_2005to2015.csv    # NOAA stranding data (download separately)
├── scripts/
│   ├── whale_stranding_quick_test.py # Main analysis script
│   └── magnetic_gradient_visualizer.py # Gradient visualization
└── results/
    ├── dual_cue_hypothesis_test.png   # Analysis results
    └── magnetic_gradient_surprise.png  # Gradient comparison
```

## 🔬 Hypothesis Evolution

### Original Hypothesis
- Stranding sites have seaward-declining (negative) magnetic gradients
- Non-stranding sites have landward-rising (positive) gradients
- Whales follow magnetic "downhill" into shallow water

### Revised Hypothesis (Based on Data)
- Stranding sites have landward-rising (positive) magnetic gradients
- Magnetic "uphill" may prevent whales from returning to deep water
- Combined with acoustic factors, creates an inescapable trap

## 📈 Data Sources

1. **Magnetic Field Data**: NOAA WMM-2010 model via [NCEI Calculator](https://www.ngdc.noaa.gov/geomag/calculators/magcalc.shtml)
2. **Stranding Data**: [NOAA Marine Mammal Stranding Database](https://www.fisheries.noaa.gov/national/marine-mammal-protection/marine-mammal-stranding-data)
3. **Acoustic Proxy**: [USGS Earthquake API](https://earthquake.usgs.gov/fdsnws/event/1/) (seismic events as low-frequency acoustic sources)

## 🎯 Next Steps

1. **Deploy sensors** at test sites to measure real-time conditions
2. **Correlate** stranding events with magnetic/acoustic measurements
3. **Test interventions** based on revised understanding
4. **Develop predictive models** for stranding risk assessment

## 📖 Citation

If using this work, please cite:
```
[Your Name] (2025). Whale Stranding Dual-Cue Hypothesis Analysis.
GitHub repository, https://github.com/yourusername/whale-stranding-dual-cue
```

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with clear descriptions

## ⚖️ License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- NOAA for magnetic field and stranding data
- USGS for seismic/acoustic data
- Project Jonah and stranding response networks worldwide

---

**Note**: This is active research. Findings may evolve as more data becomes available.