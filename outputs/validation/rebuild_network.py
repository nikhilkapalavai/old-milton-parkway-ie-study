import xml.etree.ElementTree as ET, json, math, heapq, gzip
from pathlib import Path
HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'simulation'
nodes={};ways={}
for f in ['corridor.osm.gz','corridor_east.osm.gz']:
 r=ET.parse(gzip.open(SOURCE / f)).getroot()
 for n in r.findall('node'): nodes[n.attrib['id']]=[float(n.attrib['lat']),float(n.attrib['lon'])]
 for w in r.findall('way'):
  tags={t.attrib['k']:t.attrib['v'] for t in w.findall('tag')}
  if tags.get('highway'):ways[w.attrib['id']]={'id':w.attrib['id'],'tags':tags,'nodes':[n.attrib['ref'] for n in w.findall('nd')]}
omp=[w for w in ways.values() if w['tags'].get('name') in ['Old Milton Parkway','State Bridge Road'] and w['tags'].get('highway')=='trunk']; ids=set(n for w in omp for n in w['nodes'])
names=['North Point Parkway','Cotton Creek Drive','Vista Forest Drive','Park Bridge Parkway','Parkview Lane','State Bridge Way','Kimball Bridge Road']
def dist(a,b):
 a,b=nodes[a],nodes[b];return 6371000*2*math.asin(math.sqrt(math.sin(math.radians(b[0]-a[0])/2)**2+math.cos(math.radians(a[0]))*math.cos(math.radians(b[0]))*math.sin(math.radians(b[1]-a[1])/2)**2))
g={}
for w in omp:
 for a,b in zip(w['nodes'],w['nodes'][1:]):
  if a in nodes and b in nodes:
   g.setdefault(a,[]).append((b,dist(a,b)));g.setdefault(b,[]).append((a,dist(a,b)))
# Anchor the seven model nodes to the GDOT signal inventory coordinates
# (signals 7280, 7279, 7276, 7275, 7274, 7273) and the OSM signal at the
# Kimball Bridge terminus.  Averaging all nodes on the State Bridge Way
# approach previously placed that junction on a nearby connection west of the signal.
anchor_coords=[
 (34.06766,-84.26136), (34.06455,-84.25303), (34.06176,-84.24568),
 (34.06049,-84.24135), (34.05923,-84.23621), (34.05786,-84.23279),
 (34.0558344,-84.2310684),
]
# The OSM snapshot has separate one-way carriageway components.  Use the
# component containing State Bridge Way so every anchor is on one graph.
state_anchor=min(g,key=lambda x:(nodes[x][0]-34.05786)**2+(nodes[x][1]+84.23279)**2)
connected={state_anchor}; stack=[state_anchor]
while stack:
 a=stack.pop()
 for b,_ in g.get(a,[]):
  if b not in connected: connected.add(b); stack.append(b)
groups=[]
for name,(lat,lon) in zip(names,anchor_coords):
 n=min(connected,key=lambda x:(nodes[x][0]-lat)**2+(nodes[x][1]-lon)**2)
 s={n}
 print(name,[(n,nodes[n])])
 groups.append(s)
def shortest(starts,ends):
 h=[(0,n,[n]) for n in starts];heapq.heapify(h);seen=set()
 while h:
  d,n,p=heapq.heappop(h)
  if n in seen:continue
  seen.add(n)
  if n in ends:return d,p
  for nn,dd in g.get(n,[]):
   if nn not in seen:heapq.heappush(h,(d+dd,nn,p+[nn]))
 raise ValueError('No connected path')
links=[]
for i in range(6):
 d,p=shortest(groups[i],groups[i+1]);links.append({'from':names[i],'to':names[i+1],'length_m':round(d,1),'path':[nodes[n] for n in p]})
data={'source':'OpenStreetMap API snapshots downloaded 2026-09-07; copyright OpenStreetMap contributors, ODbL','attribution_url':'https://www.openstreetmap.org/copyright','method':'Shortest undirected path on the connected OSM trunk-road component between GDOT signal-inventory anchors; approximate signal spacing, not a surveyed lane network. Lane counts taken from GDOT concept, not OSM tags. GDOT signal inventory as-of dates are 2018-03-01 and modified 2022-05-31; verify current field locations before engineering use.','signal_inventory_url':'https://sigopsmetrics.dot.ga.gov/signal-info','junctions':[{'name':name,'lat':sum(nodes[n][0] for n in s)/len(s),'lon':sum(nodes[n][1] for n in s)/len(s)} for name,s in zip(names,groups)],'links':links}

(HERE / 'network.json').write_text(json.dumps(data,indent=2))
print('Lengths', [x['length_m'] for x in links],sum(x['length_m'] for x in links))
