# ProtocolForge Update: Stock Preparation Calculator

## Summary

Added a new **"Stock Prep"** mode to ProtocolForge that calculates optimal stock concentrations from compound mass and molecular weight. This is the **first step** users should take before entering the Single Compound mode.

---

## What's New

### 1. New "Stock Prep" Mode

**Location:** Top navigation menu (first option)

```
Select Mode: [Stock Prep] [Single Compound] [Batch Mode] [Help]
```

### 2. Workflow

#### Step 1: Enter Compound Information
- **Compound Code** (e.g., "AO-RVF-34")
- **Molecular Weight** (g/mol)
- **Mass Available** (mg)

#### Step 2: Stock Concentration Options
The calculator displays:
- **Moles available** (in µmol)
- **Status flag:** "⭐ Limited" if mass < 10 µmol, else "✓ Good"
- **Stock concentration options** for 0.5 mL, 1.0 mL, and 2.0 mL volumes
- **Recommended stock:** 1 mL @ calculated concentration (flagged with ⭐)

#### Step 3: Downstream Dilution Scenarios
Three preset options:
1. **50 µM Top** (if EC50 uncertain, micromolar range)
2. **100 nM Top** (if EC50 is nanomolar potency)
3. **Wide Scout** (test 1-2 compounds to find real EC50)

Each scenario shows:
- Exact volumes to prepare working solutions
- Step-by-step instructions
- Serial dilution series (3-fold)
- Two-step dilution for large dilution factors (nM range)

#### Step 4: Storage Instructions
- Label format
- Storage temperature (4°C)
- Stability window (2-6 months)

---

## Code Changes

### 1. **calculations.py** — New Function

```python
def calculate_stock_preparation(mw, mass_mg, volume_options=[0.5, 1.0, 2.0]):
    """
    Calculate stock concentrations from mass and molecular weight.
    
    Returns:
    - moles_mmol, moles_umol
    - stock_options: concentrations for each volume
    - recommended_conc_mM: at 1 mL
    - is_limited: True if mass < 10 µmol
    - limited_reason: explanation
    """
```

**Key logic:**
- Moles = mass (mg) / MW
- For each volume (0.5, 1.0, 2.0 mL): concentration_mM = moles_mmol / volume_ml
- "Limited" flag if moles_umol < 10 (small mass → limited downstream flexibility)
- Recommendation: 1 mL volume (standard tube, easy to handle)

### 2. **app.py** — New Mode Section

**Additions:**
- Imported `calculate_stock_preparation` from calculations
- Added "Stock Prep" to mode radio button
- Implemented full Stock Prep UI with:
  - Input form (compound code, MW, mass)
  - Output metrics (moles, status, reason)
  - Stock options table
  - Recommendation box
  - Downstream dilution calculator
  - Storage/labeling instructions

**Structure:**
```
if mode == "Stock Prep":
    [Step 1: Input]
    [Step 2: Options Table]
    [Step 3: Downstream Scenarios]
    [Step 4: Storage Info]
```

---

## Example: AO-c300

**Input:**
- Code: AO-c300
- MW: 437.09 g/mol
- Mass: 3.3 mg

**Output:**
- Moles: 7.55 µmol ⚠️ **LIMITED**
- Stock options:
  - 0.5 mL → 15.1 mM
  - **1.0 mL → 7.55 mM** ⭐ RECOMMENDED
  - 2.0 mL → 3.78 mM

**Why limited?** Only 7.55 µmol total = limited downstream flexibility

**Downstream (50 µM scenario):**
```
From 7.55 mM stock → 50 µM working solution:
- Stock: 6.62 µL
- DMSO: 93.38 µL
- Media: 900 µL
→ 1 mL @ 50 µM, 0.2% DMSO
```

---

## Integration with Existing Workflow

### Before (User's manual process):
1. Weigh compound → record mass
2. Calculate moles on paper
3. Decide stock concentration manually
4. Prepare stock → guess at dilution approach
5. Enter stock conc in Single Compound mode

### After (ProtocolForge):
1. **Stock Prep mode:** Enter mass + MW → get recommended stock
2. **Prepare stock** (exact concentration)
3. **Single Compound mode:** Enter that stock concentration
4. Generate protocols from there

---

## Files Modified

### **calculations.py**
- Added `calculate_stock_preparation()` function (~45 lines)
- No changes to existing functions

### **app.py**
- Added import: `calculate_stock_preparation`
- Rewrote imports to include missing functions (`calculate_constant_dmso_protocol`, `find_optimal_working_solutions`, `generate_plate_layout`)
- Added "Stock Prep" to mode selection
- Added full Stock Prep mode implementation (~190 lines)

---

## Next Steps

### To Deploy:

1. **Local Testing (optional):**
   ```bash
   cd /path/to/ProtocolForge
   streamlit run app.py
   ```
   Test Stock Prep mode with your 10 compounds

2. **Push to GitHub:**
   ```bash
   git add app.py calculations.py
   git commit -m "Add Stock Prep calculator mode"
   git push origin main
   ```

3. **Streamlit Cloud:** Automatically redeploys (watch https://protocolforge.streamlit.app)

### To Use with Your 10 Compounds:

1. Open https://protocolforge.streamlit.app
2. Select **"Stock Prep"** mode
3. For each compound, enter:
   - Compound code (AO-c284, etc.)
   - MW (from your data)
   - Mass (from your data)
4. Review recommended stocks
5. Prepare 1 mL stocks in DMSO per recommendation
6. Label and store at 4°C
7. Use recommended concentration in **Single Compound** mode

---

## Features Matching the HTML Guide

✅ Moles calculation from mass + MW  
✅ Stock concentration options for different volumes  
✅ "Limited" flag for small mass  
✅ Recommended stock (1 mL @ X mM)  
✅ Downstream 50 µM scenario with exact volumes  
✅ Downstream 100 nM scenario (two-step dilution)  
✅ Scout range for EC50 unknown  
✅ Storage/labeling instructions  
✅ Status metrics (moles, good/limited, reason)  

---

## Questions?

- **Mole calculation off?** Check if MW and mass units are correct
- **Stock concentration too high?** That's normal for DMSO — DMSO can hold high concentrations
- **Which scenario should I use?** Start with "50 µM Top" if unsure, or "Wide Scout" if EC50 is truly unknown

Ahmed, once you test this, let me know if any outputs need tweaking (e.g., rounding, table formatting, dilution factor defaults).
