"""SMILES parser - NO external chemistry libraries"""
import pandas as pd

def validate_smiles(smiles_string):
    """Accept any non-empty string as valid SMILES"""
    if not smiles_string or not isinstance(smiles_string, str):
        return False
    return len(smiles_string.strip()) > 0

def parse_smiles(smiles_string):
    """Parse SMILES - no molecular weight calculation"""
    smiles_clean = smiles_string.strip() if smiles_string else ""
    
    if not smiles_clean:
        return {
            'valid': False,
            'error': 'Empty SMILES',
            'mw': 0.0,
            'formula': 'N/A',
            'mol': None
        }
    
    return {
        'valid': True,
        'mw': 0.0,
        'formula': 'N/A',
        'error': None,
        'mol': None
    }

def parse_smiles_batch(smiles_list):
    """Parse multiple SMILES"""
    results = []
    
    for item in smiles_list:
        if isinstance(item, dict):
            name = item.get('name', 'Unknown')
            smiles = item.get('smiles', '')
            stock = item.get('stock', 50)
            top_dose = item.get('top_dose', 100)
            notes = item.get('notes', '')
            mw = item.get('mw', 0)
        else:
            name = f"Compound_{len(results)+1}"
            smiles = item
            stock = 50
            top_dose = 100
            notes = ""
            mw = 0
        
        parsed = parse_smiles(smiles)
        
        results.append({
            'Compound': name,
            'SMILES': smiles,
            'MW': mw if mw > 0 else 'User-provided',
            'Formula': parsed['formula'],
            'Stock_mM': stock,
            'Top_Dose_uM': top_dose,
            'Valid': parsed['valid'],
            'Error': parsed['error'],
            'Notes': notes
        })
    
    return pd.DataFrame(results)

def draw_molecule(smiles, size=(300, 300)):
    """Structure drawing not available without RDKit"""
    return None
