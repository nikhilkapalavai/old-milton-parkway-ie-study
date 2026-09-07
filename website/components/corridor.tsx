'use client';
import { useEffect, useState } from 'react';
import { Pause, Play, ArrowUpRight } from 'lucide-react';
import { Slider } from '@/components/ui/slider';
import network from '@/lib/data/network.json';
import type { Experiment, Frame, Result } from '@/lib/simulation';
const names = [
  'North Point',
  'Cotton Creek',
  'Vista Forest',
  'Park Bridge',
  'Parkview',
  'State Bridge',
  'Kimball Bridge',
];
const point = (lat: number, lon: number) => [
  ((lon + 84.26136) / 0.03015) * 740 + 70,
  ((34.06769 - lat) / 0.01188) * 210 + 65,
];
const road = network.links
  .flatMap((l) => l.path)
  .map(([lat, lon]) => point(lat, lon).join(','))
  .join(' ');
const at = (result: Result, minute: number): Frame =>
  result.frames.find((f) => f.minute >= minute) ??
  result.frames[result.frames.length - 1];
const color = (q: number) =>
  q > 100 ? '#f3a16c' : q > 30 ? '#ead486' : '#6ee4c2';
export function Corridor({ experiment }: { experiment: Experiment }) {
  const [minute, setMinute] = useState(30),
    [playing, setPlaying] = useState(false),
    [junction, setJunction] = useState(0);
  const end = Math.ceil(experiment.current.clearedBy);
  useEffect(() => {
    setMinute(30);
    setPlaying(false);
  }, [experiment]);
  useEffect(() => {
    if (!playing) return;
    const timer = setInterval(
      () =>
        setMinute((t) => {
          if (t >= end) {
            setPlaying(false);
            return end;
          }
          return t + 1;
        }),
      400,
    );
    return () => clearInterval(timer);
  }, [playing, end]);
  const frame = at(experiment.current, minute),
    ref = at(experiment.baseline, minute),
    queue = frame.nodes[junction];
  return (
    <section className="corridor-panel" aria-label="Corridor queue replay">
      <div className="map-heading">
        <div>
          <div className="eyebrow">THE CORRIDOR</div>
          <h2>Old Milton Parkway</h2>
        </div>
        <span className="map-chip">
          {experiment.settings.design === 'four' ? '4' : '6'} lanes · 7
          junctions
        </span>
      </div>
      <div className="map-scroll">
        <svg
          className="corridor-map"
          viewBox="0 0 900 365"
          role="img"
          aria-label="Approximate mapped corridor. Junction circle size represents modeled queued vehicles; use the numbered buttons below for details."
        >
          <defs>
            <pattern
              id="mapgrid"
              width="30"
              height="30"
              patternUnits="userSpaceOnUse"
            >
              <path
                d="M30 0H0V30"
                fill="none"
                stroke="white"
                strokeOpacity=".045"
              />
            </pattern>
          </defs>
          <rect width="900" height="365" fill="url(#mapgrid)" />
          <polyline
            points={road}
            fill="none"
            stroke="#264e5d"
            strokeWidth="24"
            strokeLinejoin="round"
            strokeLinecap="round"
          />
          <polyline
            points={road}
            fill="none"
            stroke="#6ee4c2"
            strokeWidth="8"
            strokeLinejoin="round"
            strokeLinecap="round"
          />
          <polyline
            points={road}
            fill="none"
            stroke="#123241"
            strokeWidth="2"
            strokeDasharray="5 8"
          />
          {network.junctions.map((n, i) => {
            const [x, y] = point(n.lat, n.lon),
              q = frame.nodes[i];
            return (
              <g key={n.name}>
                <circle
                  cx={x}
                  cy={y}
                  r={21 + Math.min(29, Math.sqrt(q) * 1.3)}
                  fill={color(q)}
                  opacity=".12"
                />
                <circle
                  cx={x}
                  cy={y}
                  r="17"
                  fill="#112d39"
                  stroke={color(q)}
                  strokeWidth={i === junction ? 3 : 1.5}
                />
                <text
                  x={x}
                  y={y + 5}
                  textAnchor="middle"
                  fill="white"
                  fontSize="14"
                  fontWeight="600"
                >
                  {i + 1}
                </text>
                <text
                  x={x}
                  y={y + (i % 2 ? 57 : -43)}
                  textAnchor="middle"
                  fill="#c8dce4"
                  fontSize="14"
                >
                  {names[i]}
                </text>
              </g>
            );
          })}
          <text x="45" y="339" fill="#a8c0ca" fontSize="12">
            N ↑ · Approximate OSM geometry
          </text>
          <text x="850" y="339" fill="#a8c0ca" textAnchor="end" fontSize="12">
            Circles show queue size · both directions
          </text>
        </svg>
      </div>
      <div
        className="junction-selector"
        role="group"
        aria-label="Select a junction"
      >
        {names.map((n, i) => (
          <button
            key={n}
            title={network.junctions[i].name}
            aria-label={`Junction ${i + 1}: ${network.junctions[i].name}`}
            aria-pressed={junction === i}
            onClick={() => setJunction(i)}
            className={junction === i ? 'active' : ''}
          >
            {i + 1}
            <span>{n}</span>
          </button>
        ))}
      </div>
      <div className="junction-detail">
        <span>
          <b>{network.junctions[junction].name}</b>
          <small>Queued vehicles at minute {minute}</small>
        </span>
        <div>
          <b style={{ color: color(queue) }}>{Math.round(queue)}</b>
          <span>your scenario</span>
        </div>
        <div>
          <b>{Math.round(ref.nodes[junction])}</b>
          <span>reference</span>
        </div>
      </div>
      <div className="playback">
        <button
          className="play-button"
          aria-label={playing ? 'Pause queue replay' : 'Play queue replay'}
          onClick={() => {
            if (minute >= end) setMinute(0);
            setPlaying((p) => !p);
          }}
        >
          {playing ? <Pause size={16} /> : <Play size={16} />}
        </button>
        <span className="time-label">
          {String(minute).padStart(2, '0')}
          <small> min</small>
        </span>
        <Slider
          aria-label="Replay minute"
          min={0}
          max={end}
          step={1}
          value={[minute]}
          onValueChange={(v) => {
            setPlaying(false);
            setMinute(Array.isArray(v) ? v[0] : v);
          }}
        />
        <span className="end-time">{end} min</span>
      </div>
      <div className="map-footer">
        <span>
          <i className="dot mint" />
          {minute < 60
            ? 'Traffic entering · 1-hour pulse'
            : 'Arrivals ended · queues clearing'}
        </span>
        <a
          href="https://www.openstreetmap.org/copyright"
          target="_blank"
          rel="noreferrer"
        >
          © OpenStreetMap contributors <ArrowUpRight size={12} />
        </a>
      </div>
    </section>
  );
}
export function QueueChart({ experiment }: { experiment: Experiment }) {
  const series = [
    { result: experiment.baseline, color: '#97a6b2', name: '4-lane reference' },
    { result: experiment.current, color: '#1b856b', name: 'Your scenario' },
  ];
  const maxTime = Math.max(...series.map((s) => s.result.clearedBy)),
    maxQ =
      Math.max(
        10,
        ...series.flatMap((s) => s.result.frames.map((f) => f.main)),
      ) * 1.15;
  const path = (r: Result) =>
    r.frames
      .map(
        (f, i) =>
          `${i ? 'L' : 'M'}${50 + (f.minute / maxTime) * 630},${192 - (f.main / maxQ) * 155}`,
      )
      .join(' ');
  return (
    <section className="panel chart-panel">
      <div className="chart-heading">
        <div>
          <h2>How the queue builds</h2>
          <p>Total main-road vehicles waiting over time</p>
        </div>
        <div className="chart-legend">
          {series.map((s) => (
            <span key={s.name}>
              <i style={{ background: s.color }} />
              {s.name}
            </span>
          ))}
        </div>
      </div>
      <svg
        viewBox="0 0 710 240"
        role="img"
        aria-label={`Queue comparison. Your peak: ${Math.round(experiment.current.peakQueue)} vehicles; reference peak: ${Math.round(experiment.baseline.peakQueue)} vehicles.`}
      >
        {[0, 0.5, 1].map((f) => (
          <g key={f}>
            <line
              x1="50"
              x2="680"
              y1={192 - f * 155}
              y2={192 - f * 155}
              stroke="#e4eaf0"
              strokeDasharray="3 4"
            />
            <text
              x="40"
              y={196 - f * 155}
              textAnchor="end"
              fill="#6c7d88"
              fontSize="12"
            >
              {Math.round(maxQ * f)}
            </text>
          </g>
        ))}
        <line
          x1={50 + (60 / maxTime) * 630}
          x2={50 + (60 / maxTime) * 630}
          y1="27"
          y2="192"
          stroke="#c8d3dc"
          strokeDasharray="5 4"
        />
        <text
          x={Math.min(560, 50 + (60 / maxTime) * 630)}
          y="18"
          fill="#6c7d88"
          fontSize="12"
        >
          Arrivals stop at 60 min
        </text>
        <path
          d={
            path(experiment.current) +
            ` L${50 + (experiment.current.clearedBy / maxTime) * 630},192 L50,192 Z`
          }
          fill="#1b856b"
          fillOpacity=".07"
        />
        {series.map((s) => (
          <path
            key={s.name}
            d={path(s.result)}
            fill="none"
            stroke={s.color}
            strokeWidth="2.5"
            strokeLinejoin="round"
            strokeDasharray={s.name.startsWith('4') ? '5 4' : undefined}
          />
        ))}
        {[0, 15, 30, 45, 60, 90, 120, 150, 180]
          .filter((t) => t <= maxTime)
          .map((t) => (
            <text
              key={t}
              x={50 + (t / maxTime) * 630}
              y="219"
              textAnchor="middle"
              fill="#6c7d88"
              fontSize="12"
            >
              {t}
            </text>
          ))}
        <text x="680" y="237" textAnchor="end" fill="#6c7d88" fontSize="12">
          Minutes since arrivals began
        </text>
      </svg>
      <div className="chart-summary">
        <span>
          Your peak queue{' '}
          <b>{Math.round(experiment.current.peakQueue)} vehicles</b>
        </span>
        <span>
          Reference peak{' '}
          <b>{Math.round(experiment.baseline.peakQueue)} vehicles</b>
        </span>
      </div>
    </section>
  );
}
