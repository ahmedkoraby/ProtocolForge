# ProtocolForge Stock Prep Mode — Quick Start

## How to Use

### 1. Open ProtocolForge
Go to: **https://protocolforge.streamlit.app**

### 2. Select "Stock Prep" (top menu)
```
Select Mode: [Stock Prep] [Single Compound] [Batch Mode] [Help]
                ↑
             Click here
```

### 3. Enter Your Compound Info
Three inputs:
- **Compound Code:** e.g., "AO-c284"
- **Molecular Weight:** e.g., 421.4
- **Mass Available:** e.g., 9.2 (in mg)

### 4. Read the Output

You'll see:
- **Moles Available** (in µmol)
- **Status:** ⭐ Limited (if < 10 µmol) or ✓ Good
- **Stock Options Table** showing concentrations for 0.5 mL, 1.0 mL, 2.0 mL volumes
- **⭐ RECOMMENDED** — 1 mL volume at calculated concentration

### 5. Choose Your Assay Scenario
Three buttons to choose from:
- **50 µM Top** — Use if EC50 is probably micromolar (safest default)
- **100 nM Top** — Use if you expect nanomolar potency
- **Wide Scout** — Use if EC50 is totally unknown (test 1-2 compounds first)

### 6. Prepare Your Stock
Follow the exact volumes shown in the "Recommended Stock Preparation" box:
- Add X mg of compound to DMSO
- Mix until clear
- Label tube
- Store at 4°C

### 7. Note the Concentration
Use this concentration in **Single Compound** mode → **Assay Setup** → **Stock Concentration (mM)**

---

## Example Walkthrough: AO-RVF-34

**Step 1-3: Enter Data**
```
Compound Code: AO-RVF-34
MW: 434.91
Mass: [MISSING — you need to weigh this]
```

**Step 4: See Output (after you provide mass)**
```
Moles Available: XX µmol
Status: ✓ Good (or ⚠️ Limited)
```

**Stock Options:**
```
Volume (mL) | Concentration (mM) | Recommendation
0.5         | YYY.Y              |
1.0         | ZZZ.Z              | ⭐ RECOMMENDED
2.0         | AAA.A              |
```

**Step 5: Choose Scenario**
Since you're testing 10 compounds with unknown potency → **"50 µM Top"** is safest choice

**Step 6: Prepare**
Follow exact steps shown (e.g., "20 µL stock + 180 µL DMSO + 800 µL media")

**Step 7: Use Stock**
When you go to Single Compound mode:
- Stock Concentration: Enter the recommended concentration here

---

## For Your 10 Compounds

| Code | Mass (mg) | MW | Status | Recommended Stock |
|------|-----------|----|---------|----|
| AO-c284 | 9.2 | 421.4 | ✓ Good | 21.8 mM @ 1 mL |
| AO-c291 | 11.4 | 439.39 | ✓ Good | 25.9 mM @ 1 mL |
| AO-c300 | 3.3 | 437.09 | ⚠️ Limited | 7.55 mM @ 1 mL |
| AO-c301 | 4.5 | 417.44 | ⚠️ Limited | 10.8 mM @ 1 mL |
| AO-RVP-304 | 2.9 | 447.21 | ⚠️ Limited | 6.48 mM @ 1 mL |
| AO-RVP-310 | **MISSING** | 465.53 | ? | ? |
| AO-RVP-311 | 5.5 | 509.54 | ⚠️ Limited | 10.8 mM @ 1 mL |
| AO-RVF-33 | **MISSING** | 434.91 | ? | ? |
| AO-RVF-34 | **MISSING** | 434.91 | ? | ? |
| AO-RVF-35 | **MISSING** | 417.91 | ? | ? |

**Action:** Weigh the 4 missing compounds, then plug their masses into Stock Prep mode.

---

## Troubleshooting

### "Calculation not showing"
→ Make sure MW > 0 and Mass > 0

### "Stock concentration seems too high"
→ That's normal! DMSO can hold very high concentrations (up to 200+ mM). 1 mL is standard.

### "I have a different volume I want to use"
→ Use the table! Pick 0.5 mL or 2.0 mL if you prefer.

### "What if my stock precipitates?"
→ Unlikely with DMSO, but if it happens: reduce concentration (use 2 mL instead of 1 mL), or warm to room temp briefly

### "Can I freeze my stock?"
→ Not recommended. DMSO freezes; store at 4°C instead.

---

## Next: Single Compound Mode

Once you have your stocks prepared at the concentrations Stock Prep recommends:

1. Go back to app
2. Select **"Single Compound"** mode
3. Enter:
   - **Stock Concentration (mM):** Use your prepared stock concentration
   - **Top Dose (µM):** 50 (if you chose "50 µM Top" scenario)
   - Rest of settings as usual

Then you'll get the dilution protocol, plate layout, and resources needed!

---

## Questions?

Post in GitHub issues: https://github.com/ahmedkoraby/ProtocolForge/issues

Or reach out to Ahmed!
