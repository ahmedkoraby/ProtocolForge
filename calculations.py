"""Dilution calculations with practical lab considerations"""

def calculate_stock_preparation(mw, mass_mg, volume_options=[0.5, 1.0, 2.0]):
    """
    Calculate stock concentrations from mass and molecular weight.
    
    Args:
        mw: Molecular weight in g/mol
        mass_mg: Mass available in mg
        volume_options: List of volumes (mL) to calculate stocks for
    
    Returns:
        Dictionary with moles, stock options, and recommendations
    """
    if mw <= 0 or mass_mg <= 0:
        return None
    
    # Calculate moles
    moles_mmol = mass_mg / mw  # mmol
    moles_umol = moles_mmol * 1000  # µmol
    
    # Calculate concentrations for different volumes
    # IMPORTANT: mmol/mL = M, so multiply by 1000 to get mM
    stock_options = []
    for vol_ml in volume_options:
        conc_mM = (moles_mmol / vol_ml) * 1000  # Convert M → mM
        stock_options.append({
            'volume_ml': vol_ml,
            'concentration_mM': conc_mM,
            'is_recommended': vol_ml == 1.0  # 1 mL is our standard
        })
    
    # Determine if "limited" (small mass, limited flexibility)
    # Limited if moles < 10 µmol
    is_limited = moles_umol < 10
    
    # Recommended stock (at 1 mL)
    # mmol/mL = M, multiply by 1000 to get mM
    recommended_conc = (moles_mmol / 1.0) * 1000  # Convert M → mM
    
    return {
        'mw': mw,
        'mass_mg': mass_mg,
        'moles_mmol': moles_mmol,
        'moles_umol': moles_umol,
        'stock_options': stock_options,
        'recommended_conc_mM': recommended_conc,
        'recommended_volume_ml': 1.0,
        'is_limited': is_limited,
        'limited_reason': 'Small mass (<10 µmol) limits flexibility' if is_limited else 'Sufficient mass for flexible stock concentrations'
    }

def calculate_dilution_series(stock_mM, top_dose_uM, dilution_factor=3, num_points=8):
    """Calculate serial dilution series"""
    doses = []
    for i in range(num_points):
        dose = top_dose_uM / (dilution_factor ** i)
        doses.append(dose)
    return sorted(doses, reverse=True)

def calculate_tube_volumes(stock_conc_mM, dose_uM, final_vol_uL=450):
    """Calculate volumes for compound addition"""
    if stock_conc_mM <= 0:
        return 0
    stock_vol = (dose_uM * final_vol_uL) / (stock_conc_mM * 1000)
    return max(0, stock_vol)

def is_pipette_safe(volume_ul, warning_threshold=0.5, critical_threshold=0.1):
    """Check if volume is safe to pipette"""
    if volume_ul < critical_threshold:
        return 'critical'  # Cannot reliably pipette
    elif volume_ul < warning_threshold:
        return 'warning'   # Difficult to pipette accurately
    else:
        return 'safe'      # Safe to pipette

def calculate_constant_dmso_protocol(stock_mM, top_dose_uM, target_dmso_pct=0.2, 
                                     dilution_factor=3, num_points=8, final_vol_uL=450):
    """
    Calculate dilution protocol with CONSTANT DMSO across all tubes.
    
    Adds extra DMSO to tubes that need less compound volume, maintaining
    the same final DMSO concentration across all dilutions.
    """
    doses = calculate_dilution_series(stock_mM, top_dose_uM, dilution_factor, num_points)
    
    results = []
    
    for idx, dose in enumerate(doses, 1):
        # Compound volume from stock
        compound_vol = calculate_tube_volumes(stock_mM, dose, final_vol_uL)
        
        # DMSO that comes from compound stock (assuming pure DMSO or need to calculate)
        # For 100% DMSO stock:
        dmso_from_compound_pct = (compound_vol / final_vol_uL) * 100
        
        # Calculate extra DMSO needed to reach target DMSO %
        dmso_needed_pct = target_dmso_pct
        extra_dmso_vol = ((dmso_needed_pct - dmso_from_compound_pct) / 100) * final_vol_uL
        extra_dmso_vol = max(0, extra_dmso_vol)  # Don't go negative
        
        # Diluent volume (culture media, buffer, etc)
        diluent_vol = final_vol_uL - compound_vol - extra_dmso_vol
        
        # Safety check
        pipette_safety = is_pipette_safe(compound_vol)
        
        results.append({
            'tube': idx,
            'dose': dose,
            'compound_vol': compound_vol,
            'extra_dmso_vol': extra_dmso_vol,
            'diluent_vol': diluent_vol,
            'final_dmso_pct': dmso_needed_pct,
            'pipette_safety': pipette_safety,
            'dmso_from_compound': dmso_from_compound_pct
        })
    
    return results

def calculate_dmso_concentration(compound_stock_mM, dose_uM, stock_dmso_pct=100, final_dmso_pct=0.2):
    """Calculate DMSO concentration for a given dose"""
    if compound_stock_mM <= 0:
        return 0
    compound_vol = calculate_tube_volumes(compound_stock_mM, dose_uM)
    total_vol = 450
    dmso_from_compound = (compound_vol / total_vol) * stock_dmso_pct
    return dmso_from_compound

def dmso_matching_check(stock_mM, top_dose_uM, target_dmso=0.2):
    """Check if DMSO can be matched across dilution series"""
    top_dose_dmso = calculate_dmso_concentration(stock_mM, top_dose_uM)
    return {
        'top_dose_dmso': top_dose_dmso,
        'target_dmso': target_dmso,
        'achievable': top_dose_dmso <= target_dmso * 1.2,
        'note': 'DMSO levels are compatible' if top_dose_dmso <= target_dmso * 1.2 else 'May need adjustment'
    }

def find_optimal_working_solutions(stock_mM, lowest_dose_uM, min_pipette_vol=1.0, final_assay_vol=450):
    """
    Find optimal intermediate working solutions to keep all pipetting volumes practical.
    Returns list of (concentration_mM, dilution_factor) tuples.
    """
    working_solutions = []
    current_conc = stock_mM
    
    # Calculate minimum working concentration needed to pipette safely into lowest dose
    min_working_conc = (lowest_dose_uM * final_assay_vol) / (min_pipette_vol * 1000)  # in mM
    
    dilution_steps = []
    
    while current_conc > min_working_conc * 1.2:  # 1.2x safety margin
        # Try 10× dilution
        next_conc = current_conc / 10
        
        if next_conc >= min_working_conc * 0.8:
            dilution_steps.append({
                'source_conc': current_conc,
                'target_conc': next_conc,
                'dilution_factor': 10,
                'source_vol': 5,  # µL
                'diluent_vol': 45  # µL
            })
            current_conc = next_conc
        else:
            # Final dilution - calculate exact factor
            factor = current_conc / min_working_conc
            if factor > 1.5:
                dilution_steps.append({
                    'source_conc': current_conc,
                    'target_conc': current_conc / factor,
                    'dilution_factor': factor,
                    'source_vol': 50 / factor,
                    'diluent_vol': 50 - (50 / factor)
                })
            break
    
    return dilution_steps

def generate_plate_layout(num_doses=8, num_replicates=12, num_controls=4):
    """
    Generate 96-well plate layout visualization.
    Returns grid with dose assignments.
    """
    plate = []
    wells_per_row = 12
    
    for row_idx in range(8):
        row = []
        for col_idx in range(wells_per_row):
            if col_idx < num_replicates and row_idx < num_doses:
                well = {
                    'position': f"{chr(65+row_idx)}{col_idx+1}",
                    'type': 'dose',
                    'dose_number': row_idx + 1,
                    'replicate': col_idx + 1
                }
            elif col_idx >= num_replicates and row_idx < num_controls:
                control_types = ['Vehicle', 'Blank', 'Media', 'Positive']
                well = {
                    'position': f"{chr(65+row_idx)}{col_idx+1}",
                    'type': 'control',
                    'control_type': control_types[row_idx] if row_idx < len(control_types) else 'Empty'
                }
            else:
                well = {
                    'position': f"{chr(65+row_idx)}{col_idx+1}",
                    'type': 'empty'
                }
            row.append(well)
        plate.append(row)
    
    return plate

def calculate_resource_planning(num_doses=8, num_replicates=12, num_compounds=1, 
                               final_volume_ul=450, num_plates=1):
    """
    Calculate total resources needed for assay batch.
    """
    # Total wells with compound
    total_wells = num_doses * num_replicates * num_compounds
    
    # Each well = final_volume_ul µL
    total_assay_volume_ul = total_wells * final_volume_ul
    total_assay_volume_ml = total_assay_volume_ul / 1000
    
    # Add buffer (20% extra for losses)
    media_needed_ml = total_assay_volume_ml * 1.2
    
    # DMSO calculations (0.2% final)
    dmso_in_assay_ul = total_assay_volume_ul * 0.002  # 0.2% = 0.002
    # Add buffer for working solutions
    dmso_needed_ul = dmso_in_assay_ul * 1.3
    dmso_needed_ml = dmso_needed_ul / 1000
    
    # Pipette tips (roughly 3-4 per well: compound, DMSO, media)
    tips_per_well = 3
    tips_needed = total_wells * tips_per_well * 1.1  # 10% extra
    
    # Plates (96-well plates)
    plates_needed = int((total_wells / 96) + 0.5) if total_wells > 0 else num_plates
    
    # Time estimate (minutes)
    # Working solution prep: ~15 min
    # Plate setup: ~2 min per well = 2 min × total_wells
    # Incubation: varies
    # Readout: ~15 min per plate
    prep_time_min = 15 + (total_wells * 0.5) + (plates_needed * 15)
    
    return {
        'total_wells': total_wells,
        'media_ml': round(media_needed_ml, 1),
        'dmso_ml': round(dmso_needed_ml, 2),
        'tips_needed': int(tips_needed),
        'plates_needed': plates_needed,
        'prep_time_min': int(prep_time_min),
        'working_solution_prep_min': 15,
        'plating_time_min': int(total_wells * 0.5),
        'readout_time_min': plates_needed * 15
    }
