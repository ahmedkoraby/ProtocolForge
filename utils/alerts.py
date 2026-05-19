"""DMSO safety alerts"""
import json
import os

def load_dmso_limits():
    """Load DMSO safety limits"""
    limits_file = os.path.join(os.path.dirname(__file__), '../data/dmso_limits.json')
    
    if os.path.exists(limits_file):
        with open(limits_file, 'r') as f:
            return json.load(f)
    
    # Default limits if file not found
    return {
        "Influenza Inhibitor (HeLa, fluorescence)": {
            "safe": 0.3,
            "caution": 0.5,
            "critical": 1.0,
            "note": "HeLa cells: fluorescence artifacts >0.3%"
        },
        "Influenza Inhibitor (Vero, CPE)": {
            "safe": 0.5,
            "caution": 1.0,
            "critical": 2.0,
            "note": "Vero cells: tolerate higher DMSO"
        },
        "Cell Viability (MTT/CCK-8)": {
            "safe": 0.1,
            "caution": 0.3,
            "critical": 0.5,
            "note": "DMSO interferes with metabolic assays"
        }
    }

def get_dmso_alert(assay_type, dmso_percentage):
    """Get DMSO alert for assay type"""
    limits = load_dmso_limits()
    
    if assay_type not in limits:
        assay_type = list(limits.keys())[0]
    
    limit_data = limits[assay_type]
    safe = limit_data['safe']
    caution = limit_data['caution']
    critical = limit_data['critical']
    
    if dmso_percentage <= safe:
        return {
            'status': 'safe',
            'color': 'green',
            'emoji': '🟢',
            'message': f'DMSO {dmso_percentage:.2f}% - SAFE'
        }
    elif dmso_percentage <= caution:
        return {
            'status': 'caution',
            'color': 'orange',
            'emoji': '🟡',
            'message': f'DMSO {dmso_percentage:.2f}% - CAUTION'
        }
    else:
        return {
            'status': 'critical',
            'color': 'red',
            'emoji': '🔴',
            'message': f'DMSO {dmso_percentage:.2f}% - CRITICAL'
        }

def get_assay_list():
    """Get list of available assays"""
    limits = load_dmso_limits()
    return list(limits.keys())
