"""Dilution calculations"""

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
    
    # Volume of stock needed = (target_dose * final_vol) / (stock_conc * 1000)
    stock_vol = (dose_uM * final_vol_uL) / (stock_conc_mM * 1000)
    return max(0, stock_vol)

def calculate_dmso_concentration(compound_stock_mM, dose_uM, stock_dmso_pct=100, final_dmso_pct=0.2):
    """Calculate DMSO concentration for a given dose"""
    if compound_stock_mM <= 0:
        return 0
    
    compound_vol = calculate_tube_volumes(compound_stock_mM, dose_uM)
    total_vol = 450  # final volume in uL
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

def calculate_resource_planning(compounds_list, num_replicates=3):
    """Calculate total resources needed for batch"""
    total_media_ml = 0
    total_dmso_ul = 0
    tips_needed = 0
    plates_needed = 1
    
    for compound in compounds_list:
        # Rough estimate: 5 mL per compound per replicate
        total_media_ml += 5 * num_replicates
        total_dmso_ul += 10 * num_replicates
        tips_needed += 15 * num_replicates
    
    return {
        'media_ml': total_media_ml,
        'dmso_ul': total_dmso_ul,
        'tips_needed': tips_needed,
        'plates_needed': plates_needed
    }
