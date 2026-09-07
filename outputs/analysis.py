"""Old Milton Parkway desk study. Standard-library Python; run: python analysis.py
Inputs: concept report approved 2022-03-21, PDF p14 and p129.
All money is historical concept-estimate dollars, not current bids.
Sensitivity inputs are hypothetical, not measured trees or agency valuations.
"""
import json
from pathlib import Path

ALTERNATIVES = {
    'inside': {'cost':29196795, 'row':1506000, 'parcels':18, 'months':30},
    'outside': {'cost':41800000, 'row':11200000, 'parcels':63, 'months':42},
    'grade_separation': {'cost':32500000, 'row':5300000, 'parcels':15, 'months':48},
}
# All seven signalized junctions named in concept p9; p129 delays transcribed.
# Order: no-build AM, build AM, no-build PM, build PM. Seconds/vehicle.
DELAYS = {
    'North Point Parkway': [31.0,34.2,40.4,35.5],
    'Cotton Creek / Brookside West': [6.4,2.2,6.4,5.7],
    'Vista Forest / Brookside East': [7.7,3.5,6.3,13.5],
    'Park Bridge / Alexander': [20.9,3.6,8.7,4.7],
    'Parkview / Southbridge': [9.3,11.3,9.5,10.8],
    'State Bridge Way': [2.8,6.7,2.5,1.8],
    'Kimball Bridge Road': [38.5,51.0,53.0,53.0],
}

def threshold(extra_cost, additional_trees):
    if additional_trees <= 0:
        raise ValueError('Additional surviving trees must be positive')
    return extra_cost / additional_trees

def run():
    base = ALTERNATIVES['inside']
    differences = {k:{f:v[f]-base[f] for f in base} for k,v in ALTERNATIVES.items()}
    delta = differences['outside']['cost']
    delay_changes = {k:{'AM':round(v[1]-v[0],1),'PM':round(v[3]-v[2],1)} for k,v in DELAYS.items()}
    results = {
        'status':'Historical desk study; no field measurements or tree-survival inventory',
        'alternatives':ALTERNATIVES,
        'differences_from_inside':differences,
        'outside_total_premium_percent':100*delta/base['cost'],
        'row_share_of_outside_premium_percent':100*differences['outside']['row']/delta,
        'typical_median':{'existing_ft':42,'proposed_ft':20,'reduction_ft':22,'reduction_percent':100*22/42},
        'opening_year_delay_change_seconds_per_vehicle':delay_changes,
        'delay_note':'Positive = worse. Do not sum/average into corridor delay without flows and routes.',
        'sensitivity_note':'All counts below are hypothetical net additional surviving mature trees across the entire affected corridor, including exterior losses. Not observed counts. No ecological valuation is asserted.',
        'outside_break_even_dollars_per_additional_tree': {str(n):threshold(delta,n) for n in [50,100,200,400]},
        'hypothetical_premium_grid': {str(c):{str(n):threshold(c,n) for n in [50,100,200,400]} for c in [1000000,3000000,6000000,delta]},
    }
    assert differences['outside']['cost']==12603205
    assert differences['outside']['row']==9694000
    assert differences['outside']['parcels']==45
    assert delay_changes['Kimball Bridge Road']['AM']==12.5
    assert delay_changes['North Point Parkway']['PM']==-4.9
    assert threshold(1000000,100)==10000
    try: threshold(1,0)
    except ValueError: pass
    else: raise AssertionError('Zero-tree case should be rejected')
    target=Path(__file__).with_name('analysis_results.json')
    target.write_text(json.dumps(results,indent=2),encoding='utf-8')
    print('Checks passed. Wrote',target.name)
    return results

if __name__=='__main__': run()
