import xml.etree.ElementTree as ET, json, math, heapq, gzip
from pathlib import Path
import os
os.chdir(Path(__file__).resolve().parent)
nodes={};ways={}
for f in ['corridor.osm.gz','corridor_east.osm.gz']:
 r=ET.parse(gzip.open(f)).getroot()
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
groups=[]
for name in names:
 s=set(n for w in ways.values() if w['tags'].get('name')==name for n in w['nodes'] if n in ids)
 print(name,[(n,nodes[n]) for n in s])
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
data={'source':'OpenStreetMap API snapshots downloaded 2026-09-07; copyright OpenStreetMap contributors, ODbL','attribution_url':'https://www.openstreetmap.org/copyright','method':'Shortest undirected path on named Old Milton Parkway / State Bridge Road trunk ways between shared intersection-node sets; approximate stop-line spacing, not a surveyed lane network. Lane counts taken from GDOT concept, not OSM tags.','junctions':[{'name':name,'lat':sum(nodes[n][0] for n in s)/len(s),'lon':sum(nodes[n][1] for n in s)/len(s)} for name,s in zip(names,groups)],'links':links}

Path('network.json').write_text(json.dumps(data,indent=2))
print('Lengths', [x['length_m'] for x in links],sum(x['length_m'] for x in links))

