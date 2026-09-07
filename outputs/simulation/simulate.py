"""Reproducible aggregate signal/queue simulation, Python 3 standard library.
This is an uncalibrated screening experiment, NOT a SUMO microsimulation or
a reconstruction of actual traffic operations. See simulation_report.md.
Run: python simulate.py. No network needed.
"""
import json, math, random, statistics
from pathlib import Path
HERE=Path(__file__).resolve().parent
NET=json.loads((HERE/'network.json').read_text())
LENGTHS=[x['length_m'] for x in NET['links']]
# GDOT concept package PDF p131. Interpreted as two-way design-hour volumes.
VOLUMES={'2027 AM':[4060,3880,3815,3795,3630,2790],
         '2027 PM':[2985,2765,2680,3095,2975,2425],
         '2047 AM':[4490,4285,4220,4205,4010,3080]}
SCENARIOS=[
 {'name':'Four lanes / reference offsets','lanes':2,'green':72,'coordinated':False,'reduction':0},
 {'name':'Four lanes / coordination only','lanes':2,'green':72,'coordinated':True,'reduction':0},
 {'name':'Four lanes / coordination + green split','lanes':2,'green':84,'coordinated':True,'reduction':0},
 {'name':'Four lanes / signals + 10% peak reduction','lanes':2,'green':84,'coordinated':True,'reduction':.10},
 {'name':'Four lanes / signals + 20% peak reduction','lanes':2,'green':84,'coordinated':True,'reduction':.20},
 {'name':'Six lanes / coordinated','lanes':3,'green':72,'coordinated':True,'reduction':0},
 {'name':'Six lanes / coordination + green split','lanes':3,'green':84,'coordinated':True,'reduction':0},
]

def simulate(scenario,period='2027 AM',seed=0,share=.60,sat=1800,side_rate=450,speed=40):
    """One-hour arrival pulse from empty, followed by up to two hours draining.
    Both directions, seven signals, six finite-storage links each direction.
    Fractional vehicle flow; minute-wise lognormal arrival variation CV~10%.
    No lane changing, detailed turns, pedestrian or construction simulation.
    """
    rng=random.Random(seed)
    factors=[rng.lognormvariate(-.005,.1) for _ in range(60)]
    factors=[x/(sum(factors)/60) for x in factors] # preserve hourly demand
    lanes=scenario['lanes']; green=scenario['green']; cycle=120;lost=16
    side_green=cycle-green-lost
    tt=[max(1,round(l/(speed*.44704))) for l in LENGTHS]
    # Westbound progression at selected speed. Reference offsets are invented.
    west_offsets=[sum(tt[i:])%cycle for i in range(7)]
    offsets=west_offsets if scenario['coordinated'] else [0,35,80,15,65,100,45]
    volumes=[v*(1-scenario['reduction']) for v in VOLUMES[period]]
    dirs=[]
    for reverse,portion in [(False,1-share),(True,share)]:
        seq=list(reversed(volumes)) if reverse else volumes
        seq=[v*portion for v in seq]
        lengths=list(reversed(LENGTHS)) if reverse else LENGTHS
        travel=list(reversed(tt)) if reverse else tt
        prev=[0]+seq; nxt=seq+[0]
        total=[max(a,b) for a,b in zip(prev,nxt)]
        dirs.append({'ready':[0.]*7,'moving':[0.]*7,'source':[0.]*7,
                     'storage':[1e9]+[l*lanes/7.5 for l in lengths],
                     'entry':[max(0,b-a)/3600 for a,b in zip(prev,nxt)],
                     'continue':[b/q if q else 0 for b,q in zip(nxt,total)],
                     'travel':travel,'offsets':list(reversed(offsets)) if reverse else offsets,
                     'events':{},'generated':0.,'exited':0.,'delay':0.,'systemtime':0.})
    side=[0.]*7;side_generated=side_exit=side_delay=0.
    peak_total=peak_side=0.;peak_node=[0.]*7;series=[];pulse_exits=0.;pulse_remaining=0.
    for t in range(10800):
        factor=factors[t//60] if t<3600 else 0
        for di,d in enumerate(dirs):
            for j,a in d['events'].pop(t,[]):d['moving'][j]-=a;d['ready'][j]+=a
            for j in range(7):
                a=d['entry'][j]*factor;d['source'][j]+=a;d['generated']+=a
                room=max(0,d['storage'][j]-d['ready'][j]-d['moving'][j])
                a=min(d['source'][j],room);d['source'][j]-=a;d['ready'][j]+=a
            # Compute transfers against a synchronous occupancy snapshot.
            flows=[]
            for j in range(7):
                cap=sat*lanes/3600 if (t-d['offsets'][j])%cycle<green else 0
                f=min(d['ready'][j],cap); p=d['continue'][j]
                if j<6 and p>0:
                    room=max(0,d['storage'][j+1]-d['ready'][j+1]-d['moving'][j+1])
                    f=min(f,room/p)
                flows.append(f)
            for j,f in enumerate(flows):
                d['ready'][j]-=f;p=d['continue'][j];d['exited']+=f*(1-p)
                if j<6 and f*p>0:
                    a=f*p;d['moving'][j+1]+=a
                    d['events'].setdefault(t+d['travel'][j],[]).append((j+1,a))
                assert d['ready'][j]>=-1e-7
                assert d['ready'][j]+d['moving'][j]<=d['storage'][j]+1e-6
            d['delay']+=sum(d['ready'])+sum(d['source'])
            d['systemtime']+=sum(d['ready'])+sum(d['source'])+sum(d['moving'])
        for j in range(7):
            a=side_rate/3600*factor;side[j]+=a;side_generated+=a
            phase=(t-offsets[j])%cycle
            cap=2*sat/3600 if green+8<=phase<cycle-8 else 0
            f=min(side[j],cap);side[j]-=f;side_exit+=f
        side_delay+=sum(side)
        mq=sum(sum(d['ready'])+sum(d['source']) for d in dirs)
        peak_total=max(peak_total,mq);peak_side=max(peak_side,max(side))
        for j in range(7):peak_node[j]=max(peak_node[j],dirs[0]['ready'][j]+dirs[0]['source'][j]+dirs[1]['ready'][6-j]+dirs[1]['source'][6-j])
        if t%60==0:series.append([t/60,round(mq,1),round(sum(side),1)])
        if t==3599:
            pulse_exits=sum(d['exited'] for d in dirs)
            pulse_remaining=sum(d['generated']-d['exited'] for d in dirs)
        if t>=3600 and mq+sum(side)+sum(sum(d['moving']) for d in dirs)<1e-6:break
    generated=sum(d['generated'] for d in dirs);exited=sum(d['exited'] for d in dirs)
    residue=generated-exited
    for d in dirs:
        assert abs(d['generated']-d['exited']-sum(d['ready'])-sum(d['moving'])-sum(d['source']))<1e-5
    assert abs(side_generated-side_exit-sum(side))<1e-5
    return {'period':period,'scenario':scenario['name'],'seed':seed,'share':share,'saturation':sat,'side_rate':side_rate,
            'main_generated':generated,'main_exited_at_60min':pulse_exits,'main_remaining_at_60min':pulse_remaining,
            'main_delay_min':sum(d['delay'] for d in dirs)/max(1,generated)/60,
            'main_time_min':sum(d['systemtime'] for d in dirs)/max(1,generated)/60,
            'side_delay_min':side_delay/max(1,side_generated)/60,
            'all_delay_min':(sum(d['delay'] for d in dirs)+side_delay)/max(1,generated+side_generated)/60,
            'max_main_queue_vehicles':peak_total,'max_side_queue_per_junction':peak_side,
            'peak_main_queue_by_junction':peak_node,'cleared_by_min':(t+1)/60,
            'residual_at_end':residue+sum(side),'queue_series':series}

def main():
    runs=[]
    profiles=[('2027 AM',.6,1800,450),('2027 PM',.6,1800,450),
              ('2027 AM',.5,1800,450),('2027 AM',.7,1800,450),
              ('2027 AM',.6,1600,450),('2027 AM',.6,1800,650),
              ('2047 AM',.6,1800,450),('2047 AM',.7,1600,650)]
    for period,share,sat,side in profiles:
        for sc in SCENARIOS:
            group=[simulate(sc,period,seed,share,sat,side) for seed in range(5)]
            for x in group:
                if not (period=='2027 AM' and share==.6 and sat==1800 and side==450 and x['seed']==0):x.pop('queue_series')
            runs.extend(group)
        print('Completed profile',period,share,sat,side,flush=True)
    result={'model':'Uncalibrated aggregate finite-storage corridor queue model; historical demand forecasts, observed OSM geometry, assumed operations','run_count':len(runs),'scenarios':SCENARIOS,'volumes':VOLUMES,'runs':runs}
    (HERE/'results.json').write_text(json.dumps(result,indent=2))
    for sc in SCENARIOS:
        g=[x for x in runs if x['period']=='2027 AM' and x['share']==.6 and x['saturation']==1800 and x['side_rate']==450 and x['scenario']==sc['name']]
        print(sc['name'], 'main',round(statistics.mean(x['main_delay_min'] for x in g),2),'side',round(statistics.mean(x['side_delay_min'] for x in g),2),'all',round(statistics.mean(x['all_delay_min'] for x in g),2))
if __name__=='__main__':main()
