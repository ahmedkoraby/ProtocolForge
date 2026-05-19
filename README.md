# ProtocolForge 🧬

**Automated Dilution Protocol Generator for Cell-Based Assays**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://protocolforge.streamlit.app)
[![GitHub](https://img.shields.io/badge/GitHub-ahmedkoraby%2FProtocolForge-blue)](https://github.com/ahmedkoraby/ProtocolForge)

## Overview

ProtocolForge automates the generation of dilution protocols for cell-based antiviral assays. It handles:

✅ SMILES validation  
✅ Exact volume calculations for serial dilutions  
✅ DMSO matching across all concentrations  
✅ Assay-specific DMSO safety alerts  
✅ Batch handling (multiple compounds at once)  
✅ Professional PDF protocol generation  
✅ Resource planning (media, tips, plates needed)  
✅ Timeline optimization  

## Quick Start

### Online (No Installation)

Visit: https://protocolforge.streamlit.app

### Local Installation

```bash
# Clone repository
git clone https://github.com/ahmedkoraby/ProtocolForge.git
cd ProtocolForge

# Create virtual environment (Python 3.10+)
python3.10 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run app.py
```

Then open http://localhost:8501

## Features

### Single Compound Mode

1. Enter SMILES string (or manual compound data)
2. Specify stock concentration & top dose
3. Get instant DMSO safety assessment
4. Download printable PDF protocol

### Batch Mode

1. Upload CSV with multiple compounds
2. Auto-check DMSO compatibility across all compounds
3. Download master batch + individual protocols
4. Follow optimized timeline

### DMSO Matching

ProtocolForge ensures all concentrations in your dose-response curve contain the same DMSO percentage. This isolates compound effects from solvent artifacts:

- **Diluent Media**: Contains target DMSO % (default 0.2%)
- **All Tubes**: Mixed with diluent to preserve DMSO
- **Vehicle Control**: Has identical DMSO as highest compound dose
- **Result**: Clean dose-response curves with zero solvent confounding

### Smart Alerts

Assay-specific DMSO limits:

| Assay | Safe | Caution | Critical |
|-------|------|---------|----------|
| RSV (HeLa, fluorescence) | ≤0.3% | 0.3–0.5% | >0.5% |
| RSV (Vero, CPE) | ≤0.5% | 0.5–1.0% | >1.0% |
| MTT/CCK-8 | ≤0.1% | 0.1–0.3% | >0.3% |
| Primary Neurons | ≤0.05% | 0.05–0.1% | >0.1% |

## CSV Format for Batch Upload

```
Compound,SMILES,Stock_mM,Top_Dose_uM,Notes
Compound_1,CCO,50,100,Example 1
Compound_2,CC(C)c1ccccc1,10,50,Example 2
Reference,Cc1ccccc1O,100,100,Reference
```

## Requirements

- Python 3.10+ (**REQUIRED** for Streamlit Cloud)
- Streamlit
- pandas
- reportlab
- numpy

See `requirements.txt` for exact versions.

App is live at `https://protocolforge.streamlit.app`

## Troubleshooting

### "Invalid SMILES" Error

Make sure your SMILES string contains only valid chemical symbols and syntax.

Examples of valid SMILES:
- `CCO` (ethanol)
- `CC(C)Cc1ccc(cc1)C(C)C(O)=O` (ibuprofen)
- `Cc1ccccc1` (toluene)

### App Won't Load on Streamlit Cloud

1. Check that Python version is set to **3.10+** in app settings
2. Wait 2-3 minutes for initial deployment
3. Clear browser cache and refresh

## File Structure

```
ProtocolForge/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .gitignore
├── .streamlit/
│   └── config.toml       # Streamlit configuration
├── utils/
│   ├── __init__.py
│   ├── smiles_parser.py   # SMILES validation
│   ├── calculations.py    # Dilution math
│   ├── alerts.py          # DMSO alert system
│   └── pdf_generator.py   # PDF generation
├── data/
│   └── dmso_limits.json   # Assay-specific limits
└── templates/
    └── example_batch.csv  # Example batch data
```

## Contributing

Found a bug or want a feature? 

1. **Issues:** https://github.com/ahmedkoraby/ProtocolForge/issues
2. **Discussions:** https://github.com/ahmedkoraby/ProtocolForge/discussions
3. **Pull Requests:** Welcome!

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Built with [Streamlit](https://streamlit.io)
- PDF generation with [reportlab](https://www.reportlab.com)

---

**Built for reproducible science**

Ahmed K. Oraby @ University of Alberta
