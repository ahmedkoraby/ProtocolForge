"""SMILES parser with molecular weight calculation"""
import pandas as pd
import sys

# Try to import RDKit
try:
    from rdkit import Chem
    from rdkit.Descriptors import ExactMolWt
    from rdkit.Chem import rdMolDescriptors
    RDKIT_AVAILABLE = True
    RDKIT_ERROR = None
except ImportError as e:
    RDKIT_AVAILABLE = False
    RDKIT_ERROR = str(e)
    Chem = None

def get_rdkit_status():
    """Get RDKit availability status"""
    return {
        'available': RDKIT_AVAILABLE,
        'error': RDKIT_ERROR
    }

def validate_smiles(smiles_string):
    """Validate SMILES string"""
    if not smiles_string or not isinstance(smiles_string, str):
        return False
    
    if not RDKIT_AVAILABLE:
        return len(smiles_string.strip()) > 0
    
    try:
        mol = Chem.MolFromSmiles(smiles_string.strip())
        return mol is not None
    except:
        return False

def parse_smiles(smiles_string):
    """Parse SMILES and calculate molecular weight"""
    smiles_clean = smiles_string.strip() if smiles_string else ""
    
    if not smiles_clean:
        return {
            'valid': False,
            'error': 'Empty SMILES',
            'mw': 0.0,
            'formula': 'N/A',
            'mol': None
        }
    
    if not RDKIT_AVAILABLE:
        return {
            'valid': False,
            'error': f'RDKit not available. Please enter MW manually.',
            'mw': 0.0,
            'formula': 'N/A',
            'mol': None,
            'rdkit_error': RDKIT_ERROR
        }
    
    try:
        # Parse SMILES
        mol = Chem.MolFromSmiles(smiles_clean)
        
        if mol is None:
            return {
                'valid': False,
                'error': 'Invalid SMILES syntax',
                'mw': 0.0,
                'formula': 'N/A',
                'mol': None
            }
        
        # Calculate molecular weight
        try:
            mw = ExactMolWt(mol)
        except Exception as e:
            return {
                'valid': False,
                'error': f'Could not calculate MW: {str(e)}',
                'mw': 0.0,
                'formula': 'N/A',
                'mol': mol
            }
        
        # Calculate formula
        try:
            formula = rdMolDescriptors.CalcMolFormula(mol)
        except Exception as e:
            formula = 'N/A'
        
        # Validate results
        if mw <= 0:
            return {
                'valid': False,
                'error': f'Invalid MW: {mw}',
                'mw': 0.0,
                'formula': formula,
                'mol': mol
            }
        
        return {
            'valid': True,
            'mw': mw,
            'formula': formula,
            'error': None,
            'mol': mol
        }
        
    except Exception as e:
        return {
            'valid': False,
            'error': f"Parse error: {str(e)}",
            'mw': 0.0,
            'formula': 'N/A',
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
            mw_provided = item.get('mw', 0)
        else:
            name = f"Compound_{len(results)+1}"
            smiles = item
            stock = 50
            top_dose = 100
            notes = ""
            mw_provided = 0
        
        parsed = parse_smiles(smiles)
        final_mw = parsed['mw'] if parsed['mw'] > 0 else mw_provided
        
        results.append({
            'Compound': name,
            'SMILES': smiles,
            'MW': final_mw,
            'Formula': parsed['formula'],
            'Stock_mM': stock,
            'Top_Dose_uM': top_dose,
            'Valid': parsed['valid'],
            'Error': parsed['error'],
            'Notes': notes
        })
    
    return pd.DataFrame(results)

def draw_molecule(smiles, size=(300, 300)):
    """Draw 2D structure of molecule"""
    if not RDKIT_AVAILABLE:
        return None
    
    try:
        from rdkit.Chem import Draw
        mol = Chem.MolFromSmiles(smiles)
        
        if mol is None:
            return None
        
        img = Draw.MolToImage(mol, size=size)
        return img
    except:
        return None
