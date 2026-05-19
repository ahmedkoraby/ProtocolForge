"""ProtocolForge - Automated Dilution Protocol Generator (No RDKit)"""

import streamlit as st
import pandas as pd
import numpy as np
from calculations import (
    calculate_dilution_series, calculate_tube_volumes, dmso_matching_check,
    calculate_resource_planning, calculate_stock_preparation,
    calculate_constant_dmso_protocol, find_optimal_working_solutions,
    generate_plate_layout
)
from alerts import get_dmso_alert, get_assay_list, load_dmso_limits
from pdf_generator import generate_protocol_pdf, generate_batch_protocol_pdf

# Page config
st.set_page_config(
    page_title="ProtocolForge",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.markdown("# 🧬 ProtocolForge")
st.markdown("**Automated Dilution Protocol Generator for Cell-Based Assays**")
st.markdown("---")

# Mode selection
mode = st.radio(
    "Select Mode:",
    ["Stock Prep", "Single Compound", "Batch Mode", "Help"],
    horizontal=True
)

if mode == "Stock Prep":
    st.markdown("## Stock Solution Preparation Calculator")
    st.markdown("---")
    st.info("""
    Calculate optimal stock concentrations from compound mass and molecular weight.
    Helps you prepare working solutions for dilution protocols.
    """)
    
    # Input section
    st.markdown("### Step 1: Enter Compound Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        compound_code = st.text_input("Compound Code:", value="AO-c284", placeholder="e.g., AO-RVF-34")
    
    with col2:
        mw = st.number_input("Molecular Weight (g/mol):", value=421.4, min_value=0.0, format="%.2f")
    
    with col3:
        mass_mg = st.number_input("Mass Available (mg):", value=9.2, min_value=0.0, format="%.1f")
    
    st.markdown("---")
    
    if mw > 0 and mass_mg > 0:
        # Calculate
        result = calculate_stock_preparation(mw, mass_mg)
        
        if result:
            st.markdown("### Step 2: Stock Concentration Options")
            
            # Display moles calculation
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Moles Available", f"{result['moles_umol']:.2f} µmol")
            
            with col2:
                st.metric("Status", "⚠️ Limited" if result['is_limited'] else "✓ Good")
            
            with col3:
                st.metric("Reason", "Small mass" if result['is_limited'] else "Sufficient mass")
            
            st.markdown("---")
            
            # Stock options table
            st.markdown("### Stock Concentration Options")
            
            table_data = []
            for opt in result['stock_options']:
                table_data.append({
                    "Volume (mL)": f"{opt['volume_ml']:.1f}",
                    "Concentration (mM)": f"{opt['concentration_mM']:.2f}",
                    "Recommendation": "⭐ RECOMMENDED" if opt['is_recommended'] else ""
                })
            
            df_options = pd.DataFrame(table_data)
            st.dataframe(df_options, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            # Recommendation box
            rec_col1, rec_col2 = st.columns([3, 1])
            
            with rec_col1:
                st.success(f"""
                **✓ Recommended Stock Preparation:**
                
                - **Volume:** {result['recommended_volume_ml']:.1f} mL DMSO
                - **Concentration:** {result['recommended_conc_mM']:.2f} mM
                - **Compound:** {compound_code}
                - **Reason:** 1 mL is standard tube size, easy to pipette and store at 4°C
                
                **Storage:** 4°C (refrigerator) | **Stability:** 2-6 months in sealed tube
                """)
            
            st.markdown("---")
            
            # Downstream dilution options
            st.markdown("### Step 3: From This Stock → Working Solutions")
            
            dilution_scenario = st.radio(
                "What's your target assay?",
                ["50 µM Top (Uncertain EC50)", "100 nM Top (Nanomolar potency)", "Wide Scout (Find EC50)"],
                horizontal=True
            )
            
            if dilution_scenario == "50 µM Top (Uncertain EC50)":
                st.info(f"""
                **To make 50 µM working solution from {result['recommended_conc_mM']:.2f} mM stock:**
                
                For 1 mL working solution:
                - Stock needed: {(50 / result['recommended_conc_mM']):.2f} µL
                - DMSO (100%): {100 - (50 / result['recommended_conc_mM']):.2f} µL
                - Culture media: {900 - (50 / result['recommended_conc_mM']):.2f} µL
                - **Final:** 1 mL @ 50 µM, 0.2% DMSO
                
                Then do 3-fold serial dilutions: 50 → 16.7 → 5.6 → 1.85 → 0.62 → 0.21 → 0.07 → 0.023 µM
                """)
            
            elif dilution_scenario == "100 nM Top (Nanomolar potency)":
                st.info(f"""
                **To make 100 nM working solution from {result['recommended_conc_mM']:.2f} mM stock:**
                
                **Two-step approach (large dilution factor):**
                
                Step 1 - Make intermediate 10 µM solution:
                - Stock needed: {(10 / result['recommended_conc_mM']):.2f} µL
                - DMSO (100%): {100 - (10 / result['recommended_conc_mM']):.2f} µL
                - Media: {900 - (10 / result['recommended_conc_mM']):.2f} µL
                - **Result:** 1 mL @ 10 µM
                
                Step 2 - From 10 µM → make 100 nM working solution:
                - 10 µM stock: 10 µL
                - DMSO (100%): 5 µL
                - Media: 985 µL
                - **Result:** 1 mL @ 100 nM, 0.2% DMSO
                
                Then do 3-fold serial dilutions: 100 → 33 → 11 → 3.7 → 1.2 → 0.41 → 0.14 → 0.046 nM
                """)
            
            else:  # Wide Scout
                st.info(f"""
                **Scout Range (single-point test at different dilution factors):**
                
                Prepare these scout tubes directly from {result['recommended_conc_mM']:.2f} mM stock:
                
                | Dilution Factor | Final Conc (µM) | Stock (µL) | Notes |
                |---|---|---|---|
                | 1:100 | {result['recommended_conc_mM'] / 100:.2f} | {(result['recommended_conc_mM'] * 10) / 100:.2f} | High µM range |
                | 1:1,000 | {result['recommended_conc_mM'] / 1000:.3f} | {(result['recommended_conc_mM'] * 10) / 1000:.2f} | Mid µM range |
                | 1:10,000 | {result['recommended_conc_mM'] / 10000:.4f} | {(result['recommended_conc_mM'] * 10) / 10000:.2f} | Low µM/high nM |
                | 1:100,000 | {result['recommended_conc_mM'] / 100000:.5f} | {(result['recommended_conc_mM'] * 10) / 100000:.3f} | Nanomolar range |
                
                Test 1-2 compounds at these concentrations to find where activity appears.
                """)
            
            st.markdown("---")
            
            # Storage instructions
            st.markdown("### Storage & Labeling")
            st.markdown(f"""
            **Tube Label:**
            ```
            {compound_code} | {result['recommended_conc_mM']:.2f} mM | DMSO | 2025-05-19
            ```
            
            **Storage:**
            - **Container:** 1.5 mL Eppendorf (polypropylene, DMSO-resistant)
            - **Temperature:** 4°C (refrigerator, NOT freezer)
            - **Stability:** 2-6 months at 4°C in sealed tube
            - **Avoid:** Repeated freeze-thaw cycles
            """)

elif mode == "Help":
    st.markdown("""
    ## About ProtocolForge
    
    Automates dilution protocol generation for cell-based antiviral assays.
    
    ### Features
    - **Manual MW Entry**: Enter molecular weight directly (no SMILES parsing)
    - **Dilution Math**: Exact volume calculations for serial dilutions
    - **DMSO Matching**: Constant DMSO across all concentrations
    - **Safety Alerts**: Assay-specific DMSO limits
    - **PDF Protocols**: Professional, printable protocols
    - **Batch Mode**: Process multiple compounds at once
    - **Stock Prep**: Calculate optimal stock concentrations from mass
    """)

else:  # Single Compound or Batch Mode
    st.markdown("## Single Compound Dilution Protocol")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        input_method = st.radio("Input Method:", ["Manual", "Example"])
    
    st.markdown("---")
    
    if input_method == "Manual":
        st.subheader("Compound Information")
        compound_name = st.text_input("Compound Name:", value="Compound_1")
        mw = st.number_input("Molecular Weight (g/mol):", value=400.0, min_value=0.0)
        formula = st.text_input("Molecular Formula (optional):", value="")
    
    else:
        st.info("Loaded example compound")
        compound_name = "Example Compound"
        mw = 400.0
        formula = "C20H25NO5"
    
    st.markdown("---")
    st.subheader("Assay Setup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Compound Configuration**")
        stock_mM = st.number_input("Stock Concentration (mM):", value=50, min_value=1)
        top_dose_uM = st.number_input("Top Dose (µM):", value=100, min_value=1)
    
    with col2:
        st.markdown("**Dilution Series**")
        dilution_factor = st.number_input("Dilution Factor:", value=3, min_value=2, max_value=10)
        num_points = st.number_input("Number of Points:", value=8, min_value=2, max_value=15)
    
    st.markdown("---")
    st.subheader("DMSO & Assay Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        assay_type = st.selectbox("Assay Type:", get_assay_list())
    
    with col2:
        target_dmso = st.number_input("Target DMSO %:", value=0.2, min_value=0.01, max_value=5.0, step=0.1)
    
    with col3:
        final_volume_ul = st.number_input("Final Tube Volume (µL):", value=450, min_value=100)
    
    st.markdown("---")
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Direct Protocol", "🧪 Working Solutions", "🎯 Plate Layout", "📦 Resources"])
    
    # Calculate base protocol
    protocol_results = calculate_constant_dmso_protocol(
        stock_mM, top_dose_uM, target_dmso_pct=0.2,
        dilution_factor=dilution_factor, num_points=num_points,
        final_vol_uL=final_volume_ul
    )
    
    # Check for problematic volumes
    has_warning = False
    has_critical = False
    for result in protocol_results:
        if result['pipette_safety'] == 'critical':
            has_critical = True
        elif result['pipette_safety'] == 'warning':
            has_warning = True
    
    # TAB 1: Direct Protocol
    with tab1:
        st.subheader("Direct Addition (From Stock)")
        
        st.info("""
        **Constant DMSO Protocol:**
        - Maintains same DMSO % across all tubes (prevents solvent artifacts)
        - Extra DMSO added to lower-dose tubes
        - All compound additions shown to 4 decimals
        """)
        
        # Build display table
        table_data = []
        for result in protocol_results:
            compound_vol = result['compound_vol']
            compound_display = f"{compound_vol:.4f}"
            
            if result['pipette_safety'] == 'critical':
                compound_display += " ⚠️ CRITICAL"
            elif result['pipette_safety'] == 'warning':
                compound_display += " ⚠️"
            
            table_data.append({
                "Tube": f"T{result['tube']}",
                "Dose (µM)": f"{result['dose']:.3e}",
                "Dose (nM)": f"{result['dose']*1000:,.1f}",
                "Compound (µL)": compound_display,
                "Extra DMSO (µL)": f"{result['extra_dmso_vol']:.3f}",
                "Diluent (µL)": f"{result['diluent_vol']:.1f}",
                "Final DMSO %": f"{result['final_dmso_pct']:.3f}"
            })
        
        df_dilution = pd.DataFrame(table_data)
        st.dataframe(df_dilution, use_container_width=True, hide_index=True)
        
        # Show warnings
        if has_critical:
            st.error("""
            ⚠️ **CRITICAL: Some volumes <0.1 µL are NOT reliably pipettable!**
            
            **Solution:** Use Working Solutions tab to create intermediate dilutions.
            This keeps all pipetting volumes ≥1 µL (practical and accurate).
            """)
        elif has_warning:
            st.warning("""
            ⚠️ **WARNING: Some volumes 0.1–0.5 µL are difficult to pipette accurately.**
            
            **Recommendation:** Use Working Solutions tab for more practical volumes.
            """)
        else:
            st.success("✅ All volumes are practical and pipettable!")
    
    # TAB 2: Working Solutions
    with tab2:
        st.subheader("Intermediate Working Solutions")
        st.info("""
        Create intermediate dilutions to keep all pipetting volumes ≥1 µL.
        This is more practical and accurate than direct addition from stock.
        """)
        
        working_sols = find_optimal_working_solutions(
            stock_mM, 
            min(d['dose'] for d in protocol_results)
        )
        
        if working_sols:
            st.markdown("**Dilution Steps:**")
            for step in working_sols:
                st.markdown(f"""
                **{step['source_conc']:.1f} mM** → **{step['target_conc']:.2f} mM**
                - Dilution factor: {step['dilution_factor']:.1f}×
                - Take {step['source_vol']:.1f} µL of source
                - Add {step['diluent_vol']:.1f} µL diluent
                """)
        
        st.success("Use these intermediate solutions in your Direct Protocol calculations")
    
    # TAB 3: Plate Layout
    with tab3:
        st.subheader("96-Well Plate Layout")
        
        num_replicates = st.number_input("Number of Replicates:", value=3, min_value=1, max_value=12)
        
        plate_layout = generate_plate_layout(
            num_doses=num_points,
            num_replicates=num_replicates
        )
        
        st.markdown(f"""
        **Plate Configuration:**
        - {num_points} dose concentrations (rows A–{chr(64+num_points)})
        - {num_replicates} replicates per dose (columns 1–{num_replicates})
        - {12-num_replicates} control lanes (columns {num_replicates+1}–12)
        """)
        
        # Visual plate representation
        plate_html = '<div style="font-family: monospace; font-size: 12px; line-height: 1.5;">'
        plate_html += '     ' + ''.join([f'{i:3d}' for i in range(1, 13)]) + '<br>'
        
        for row_idx, row in enumerate(plate_layout):
            plate_html += f'{chr(65+row_idx)}    '
            for well in row:
                if well['type'] == 'dose':
                    plate_html += f'D{well["dose_number"]:1d} '
                elif well['type'] == 'control':
                    plate_html += 'C   '
                else:
                    plate_html += '.   '
            plate_html += '<br>'
        
        plate_html += '</div>'
        st.markdown(plate_html)
        st.caption("D = Dose wells | C = Control wells | . = Empty")
    
    # TAB 4: Resources
    with tab4:
        st.subheader("Resource Planning")
        
        num_replicates_res = st.number_input("Replicates:", value=3, min_value=1, key="res_replicates")
        
        resources = calculate_resource_planning(
            num_doses=num_points,
            num_replicates=num_replicates_res,
            num_compounds=1,
            final_volume_ul=final_volume_ul,
            num_plates=1
        )
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Media Needed (mL)", f"{resources['media_ml']:.1f}")
        with col2:
            st.metric("DMSO (mL)", f"{resources['dmso_ml']:.2f}")
        with col3:
            st.metric("Pipette Tips", resources['tips_needed'])
        with col4:
            st.metric("96-Well Plates", resources['plates_needed'])
        
        st.markdown("---")
        st.markdown("**Time Estimate**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Prep (min)", resources['working_solution_prep_min'])
        with col2:
            st.metric("Plating (min)", resources['plating_time_min'])
        with col3:
            st.metric("Incubation", "Per assay")
        with col4:
            st.metric("Readout (min)", resources['readout_time_min'])
        
        st.markdown("---")
        st.subheader("Preparation Checklist")
        
        checklist_items = [
            f"Prepare {resources['media_ml']:.1f} mL media",
            f"Prepare {resources['dmso_ml']:.2f} mL DMSO",
            f"Get {resources['plates_needed']} × 96-well plates",
            f"Prepare {resources['tips_needed']:,.0f} pipette tips",
            "Set up biosafety cabinet/hood"
        ]
        for item in checklist_items:
            st.checkbox(item)
    
    st.markdown("---")
    st.subheader("DMSO Safety Assessment")
    
    dmso_check = dmso_matching_check(stock_mM, top_dose_uM, target_dmso)
    alert = get_dmso_alert(assay_type, dmso_check['top_dose_dmso'])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("DMSO at Top Dose", f"{dmso_check['top_dose_dmso']:.3f}%")
    
    with col2:
        st.metric("Status", alert['status'].upper(), alert['emoji'])
    
    with col3:
        limits = load_dmso_limits()[assay_type]
        st.metric("Safe Limit", f"{limits['safe']}%")
    
    with col4:
        st.metric("Compound Name", compound_name)
    
    if alert['status'] == 'safe':
        st.success(f"✅ {alert['message']}")
    elif alert['status'] == 'caution':
        st.warning(f"⚠️ {alert['message']}")
    else:
        st.error(f"🔴 {alert['message']}")
    
    st.markdown("---")
    st.subheader("Generate Protocol")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Generate PDF Protocol", key="pdf_button"):
            try:
                pdf = generate_protocol_pdf(
                    compound_name, stock_mM, top_dose_uM,
                    dilution_factor, num_points
                )
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf,
                    file_name=f"{compound_name}_protocol.pdf",
                    mime="application/pdf",
                    key="pdf_download"
                )
                st.success("✅ PDF generated!")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    with col2:
        st.info(f"Protocol will include all {num_points} dilution points")

st.markdown("---")
st.markdown("""
**ProtocolForge** - Automated Dilution Protocol Generator  
Built for reproducible science | Ahmed K. Oraby @ University of Alberta
""")
