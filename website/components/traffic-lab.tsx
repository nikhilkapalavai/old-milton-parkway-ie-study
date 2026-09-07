'use client';
import { useCallback, useEffect, useRef, useState } from 'react';
import {
  ArrowUpRight,
  Route,
  MapPin,
  SlidersHorizontal,
  Trees,
  FlaskConical,
  RotateCcw,
  ArrowDownRight,
  ArrowRight,
  ChevronDown,
  LoaderCircle,
  Activity,
  Check,
  AlertCircle,
} from 'lucide-react';
import { Slider } from '@/components/ui/slider';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from '@/components/ui/select';
import {
  DEFAULTS,
  PERIODS,
  validateSettings,
  type Settings,
  type Experiment,
  type Result,
} from '@/lib/simulation';
import { Corridor, QueueChart } from './corridor';
import { TreesAndTradeoffs, ModelNotes, GITHUB } from './study-notes';
type ToolContext = {
  registerTool: (
    tool: {
      name: string;
      description: string;
      inputSchema: object;
      annotations: { readOnlyHint: boolean };
      execute: (input: unknown) => unknown | Promise<unknown>;
    },
    options: { signal: AbortSignal },
  ) => void | Promise<void>;
};
function RangeControl({
  label,
  value,
  min,
  max,
  step = 1,
  unit = '',
  onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  unit?: string;
  onChange: (n: number) => void;
}) {
  return (
    <div className="range-control">
      <div className="slider-label">
        <span>{label}</span>
        <b>
          {value}
          <small> {unit}</small>
        </b>
      </div>
      <Slider
        aria-label={label}
        value={[value]}
        min={min}
        max={max}
        step={step}
        onValueChange={(v) => onChange(Array.isArray(v) ? v[0] : v)}
      />
      <div className="range-captions">
        <span>
          {min}
          {unit === '%' ? '%' : ''}
        </span>
        <span>
          {max}
          {unit === '%' ? '%' : ''}
        </span>
      </div>
    </div>
  );
}
function Metrics({ current, baseline }: { current: Result; baseline: Result }) {
  const diff =
    ((current.mainDelay - baseline.mainDelay) / baseline.mainDelay) * 100;
  return (
    <div className="metrics">
      <article className="metric panel main-metric">
        <span>Main-road delay</span>
        <div>
          {current.mainDelay.toFixed(2)} <small>min / trip</small>
        </div>
        <p className={diff < -0.01 ? 'improvement' : ''}>
          {Math.abs(diff) < 0.01
            ? 'Same as four-lane reference'
            : `${Math.abs(diff).toFixed(0)}% ${diff < 0 ? 'less' : 'more'} than reference`}
        </p>
      </article>
      <article className="metric panel">
        <span>Cross-street delay</span>
        <div>
          {current.sideDelay.toFixed(2)} <small>min / trip</small>
        </div>
        <p>Reference: {baseline.sideDelay.toFixed(2)} min / trip</p>
      </article>
      <article className="metric panel">
        <span>All modeled trips</span>
        <div>
          {current.allDelay.toFixed(2)} <small>min / trip</small>
        </div>
        <p>Includes both roads’ queues</p>
      </article>
    </div>
  );
}
function Takeaway({ experiment }: { experiment: Experiment }) {
  const { current: c, baseline: b, settings: s } = experiment;
  const improved = c.mainDelay < b.mainDelay - 0.05,
    sideHarm = c.sideDelay > b.sideDelay + 0.4;
  const title =
    c.residual > 1e-5
      ? 'Some traffic remains at the three-hour limit.'
      : sideHarm
        ? 'A faster main road comes with a side-street cost.'
        : improved
          ? 'Your changes reduce main-road queue delay.'
          : 'This is your starting point for comparison.';
  const body =
    c.residual > 1e-5
      ? 'The displayed delay excludes future waiting after the model stops, so it is a lower bound.'
      : sideHarm
        ? `Cross-street delay rises from ${b.sideDelay.toFixed(2)} to ${c.sideDelay.toFixed(2)} minutes per trip. Consider total delay before judging the scenario.`
        : improved
          ? `Average main-road delay falls from ${b.mainDelay.toFixed(2)} to ${c.mainDelay.toFixed(2)} minutes. ${s.design === 'four' ? 'Four lanes remain a candidate under these assumptions; tree feasibility still needs a separate assessment.' : 'The wider design adds capacity. Median-tree survival is not modeled.'}`
          : 'Try coordinating the signals, increasing main-road green, or reducing peak-hour trips. Watch what happens to cross-street delay, too.';
  return (
    <div
      className={
        'insight panel ' + (sideHarm || c.residual > 1e-5 ? 'caution' : '')
      }
    >
      <ArrowDownRight size={25} />
      <div>
        <b>{title}</b>
        <p>{body}</p>
      </div>
    </div>
  );
}
export default function TrafficLab() {
  const [settings, setSettings] = useState<Settings>({ ...DEFAULTS }),
    [experiment, setExperiment] = useState<Experiment | null>(null),
    [pending, setPending] = useState(true),
    [error, setError] = useState(''),
    [tab, setTab] = useState('playground');
  const worker = useRef<Worker | null>(null),
    sequence = useRef(0),
    experimentRef = useRef<Experiment | null>(null);
  const waiters = useRef<
    {
      resolve: (value: Experiment) => void;
      reject: (error: Error) => void;
      settings: Settings;
      timeout: ReturnType<typeof setTimeout>;
    }[]
  >([]);
  const update = useCallback(
    (patch: Partial<Settings>) =>
      setSettings((s) => validateSettings({ ...s, ...patch })),
    [],
  );
  const reset = () => setSettings({ ...DEFAULTS });
  const treePreset = () => {
    setTab('playground');
    setSettings((s) => ({
      ...s,
      design: 'four',
      coordinated: true,
      green: 84,
      reduction: 20,
    }));
  };
  useEffect(() => {
    const w = new Worker(
      new URL('../lib/simulation.worker.ts', import.meta.url),
      { type: 'module' },
    );
    worker.current = w;
    w.onmessage = ({ data }) => {
      if (data.id !== sequence.current) return;
      setPending(false);
      setError(data.error ?? '');
      if (data.result) {
        setExperiment(data.result);
        experimentRef.current = data.result;
      }
    };
    w.onerror = () => {
      setPending(false);
      setError(
        'The traffic model could not start. Reload the page to try again.',
      );
    };
    return () => {
      w.terminate();
      worker.current = null;
      for (const waiter of waiters.current) {
        clearTimeout(waiter.timeout);
        waiter.reject(new Error('The playground was closed.'));
      }
      waiters.current = [];
    };
  }, []);
  useEffect(() => {
    setPending(true);
    setError('');
    const id = ++sequence.current;
    const timer = setTimeout(
      () => worker.current?.postMessage({ id, settings }),
      180,
    );
    return () => clearTimeout(timer);
  }, [settings]);
  useEffect(() => {
    if (!experiment || pending) return;
    waiters.current = waiters.current.filter((waiter) => {
      if (
        JSON.stringify(waiter.settings) === JSON.stringify(experiment.settings)
      ) {
        clearTimeout(waiter.timeout);
        waiter.resolve(experiment);
        return false;
      }
      return true;
    });
  }, [experiment, pending]);
  useEffect(() => {
    const context = (document as Document & { modelContext?: ToolContext })
      .modelContext;
    if (!context?.registerTool) return;
    const lifecycle = new AbortController();
    const schema = {
      type: 'object',
      properties: {
        design: { type: 'string', enum: ['four', 'inside', 'outside'] },
        green: { type: 'number', minimum: 60, maximum: 90 },
        coordinated: { type: 'boolean' },
        reduction: { type: 'number', minimum: 0, maximum: 30 },
        period: { type: 'string', enum: PERIODS },
        share: { type: 'number', minimum: 50, maximum: 70 },
        saturation: { type: 'number', minimum: 1600, maximum: 2000 },
        sideRate: { type: 'number', minimum: 250, maximum: 700 },
      },
      required: Object.keys(DEFAULTS),
      additionalProperties: false,
    };
    const summarize = (e: Experiment) => ({
      settings: e.settings,
      mainDelayMinutes: e.current.mainDelay,
      sideDelayMinutes: e.current.sideDelay,
      allDelayMinutes: e.current.allDelay,
      referenceMainDelayMinutes: e.baseline.mainDelay,
      peakQueuedVehicles: e.current.peakQueue,
      remainingVehicles: e.current.residual,
      model: 'Uncalibrated aggregate queue experiment; not live traffic.',
    });
    const tools = [
      {
        name: 'run_traffic_scenario',
        description:
          'Run a complete road and signal scenario, update the visible playground, and return modeled queue delays. Uses historical forecasts and assumed operations.',
        inputSchema: schema,
        annotations: { readOnlyHint: false },
        execute: async (input: unknown) => {
          const next = validateSettings(input);
          setTab('playground');
          const result = await new Promise<Experiment>((resolve, reject) => {
            const timeout = setTimeout(() => {
              waiters.current = waiters.current.filter(
                (w) => w.timeout !== timeout,
              );
              reject(
                new Error('The scenario did not finish within 15 seconds.'),
              );
            }, 15000);
            waiters.current.push({ resolve, reject, settings: next, timeout });
            setSettings(next);
          });
          return summarize(result);
        },
      },
      {
        name: 'read_traffic_results',
        description:
          'Read the last completed scenario and its model assumptions.',
        inputSchema: {
          type: 'object',
          properties: {},
          additionalProperties: false,
        },
        annotations: { readOnlyHint: true },
        execute: () =>
          experimentRef.current
            ? summarize(experimentRef.current)
            : { status: 'The first scenario is still running.' },
      },
    ];
    for (const tool of tools) {
      try {
        void Promise.resolve(
          context.registerTool(tool, { signal: lifecycle.signal }),
        ).catch(() => {});
      } catch {
        /* Optional browser capability; the regular interface remains available. */
      }
    }
    return () => lifecycle.abort();
  }, []);
  return (
    <div className="site-shell">
      <a className="skip-link" href="#main">
        Skip to the traffic lab
      </a>
      <header className="site-header">
        <a className="brand" href="/">
          <span className="brand-mark">
            <Route size={25} />
          </span>
          <span>
            OLD MILTON<small>TRAFFIC LAB</small>
          </span>
        </a>
        <span className="header-credit">
          An IE study by <b>Nikhil Kapalavai</b>
        </span>
        <a
          className="header-link"
          href={GITHUB}
          target="_blank"
          rel="noreferrer"
        >
          View project <ArrowUpRight size={16} />
        </a>
      </header>
      <main id="main">
        <div className="page-title">
          <div>
            <div className="eyebrow">
              <MapPin size={13} /> ALPHARETTA, GEORGIA / SR 120
            </div>
            <h1>One road. Different possibilities.</h1>
            <p>
              Explore how road design, signals, and demand change the traffic
              equation.
            </p>
          </div>
          <span className="study-badge">
            <span /> EXPLORATORY MODEL
          </span>
        </div>
        <Tabs value={tab} onValueChange={(v) => setTab(String(v))}>
          <TabsList variant="line" className="lab-tabs">
            <TabsTrigger value="playground">
              <SlidersHorizontal />
              Traffic playground
            </TabsTrigger>
            <TabsTrigger value="trees">
              <Trees />
              Trees & tradeoffs
            </TabsTrigger>
            <TabsTrigger value="model">
              <FlaskConical />
              About the model
            </TabsTrigger>
          </TabsList>
          <TabsContent value="playground">
            <div className="scenario-shortcuts">
              <span>TRY AN IDEA</span>
              <button onClick={treePreset}>
                <Trees size={14} />
                Four lanes, fewer trips <ArrowUpRight size={13} />
              </button>
              <button
                onClick={() => {
                  update({
                    design: 'inside',
                    coordinated: true,
                    green: 72,
                    reduction: 0,
                  });
                }}
              >
                <Route size={14} />
                Six-lane widening <ArrowUpRight size={13} />
              </button>
              <button
                onClick={() =>
                  setSettings({
                    ...DEFAULTS,
                    green: 84,
                    coordinated: true,
                    period: '2047 AM',
                    share: 70,
                    saturation: 1600,
                    sideRate: 650,
                  })
                }
              >
                <Activity size={14} />
                Heavier traffic test <ArrowUpRight size={13} />
              </button>
            </div>
            <div className="playground">
              <aside className="controls panel">
                <div className="panel-heading">
                  <h2>Your scenario</h2>
                  <button
                    className="icon-button"
                    aria-label="Reset all scenario settings"
                    title="Reset all settings"
                    onClick={reset}
                  >
                    <RotateCcw size={16} />
                  </button>
                </div>
                <div className="control-block">
                  <div className="control-label">
                    01 <b>Choose the road design</b>
                  </div>
                  <RadioGroup
                    aria-label="Road design"
                    value={settings.design}
                    onValueChange={(v) =>
                      update({ design: v as Settings['design'] })
                    }
                  >
                    {[
                      ['four', 'Keep four lanes', 'Existing median footprint'],
                      ['inside', 'Widen inward', '6 lanes · use the median'],
                      [
                        'outside',
                        'Widen outward',
                        '6 lanes · more property needed',
                      ],
                    ].map(([id, label, desc]) => (
                      <label
                        className={
                          'road-option ' +
                          (settings.design === id ? 'selected' : '')
                        }
                        key={id}
                      >
                        <RadioGroupItem value={id} />
                        <span>
                          <b>{label}</b>
                          <small>{desc}</small>
                        </span>
                        {id === 'four' ? (
                          <Trees size={18} />
                        ) : (
                          <Route size={18} />
                        )}
                      </label>
                    ))}
                  </RadioGroup>
                </div>
                <div className="control-block">
                  <div className="control-label">
                    02 <b>Tune the signals</b>
                  </div>
                  <div className="switch-row">
                    <label htmlFor="coord">Coordinate signals</label>
                    <Switch
                      id="coord"
                      checked={settings.coordinated}
                      onCheckedChange={(v) => update({ coordinated: v })}
                    />
                  </div>
                  <RangeControl
                    label="Main-road green"
                    value={settings.green}
                    min={60}
                    max={90}
                    unit="sec"
                    onChange={(v) => update({ green: v })}
                  />
                  <div
                    className="signal-allocation"
                    role="img"
                    aria-label={`${settings.green} seconds main-road green, ${104 - settings.green} seconds cross-street green, 16 seconds lost time in each 120-second cycle`}
                  >
                    <span style={{ width: `${settings.green / 1.2}%` }} />
                    <span
                      style={{ width: `${(104 - settings.green) / 1.2}%` }}
                    />
                    <span style={{ width: `${16 / 1.2}%` }} />
                  </div>
                  <p className="small muted">
                    {104 - settings.green}s cross-street green · 16s lost time
                    <br />
                    120-second cycle · assumed two-phase plan
                  </p>
                </div>
                <div className="control-block">
                  <div className="control-label">
                    03 <b>Reduce peak-hour demand</b>
                  </div>
                  <RangeControl
                    label="Fewer main-road trips"
                    value={settings.reduction}
                    min={0}
                    max={30}
                    unit="%"
                    onChange={(v) => update({ reduction: v })}
                  />
                  <p className="small muted">
                    A target for carpooling, staggered shifts, or fewer solo
                    commutes.
                  </p>
                </div>
                <div className="control-block">
                  <label className="control-label" htmlFor="forecast">
                    04 <b>Choose the traffic forecast</b>
                  </label>
                  <Select
                    value={settings.period}
                    onValueChange={(v) => {
                      if (v) update({ period: v as Settings['period'] });
                    }}
                  >
                    <SelectTrigger id="forecast" className="forecast-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {PERIODS.map((p) => (
                        <SelectItem key={p} value={p}>
                          {p} · {p.endsWith('AM') ? 'morning' : 'evening'}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <p className="small muted forecast-note">
                    GDOT historical no-build forecasts
                  </p>
                </div>
                <details className="advanced">
                  <summary>
                    Advanced assumptions <ChevronDown size={16} />
                  </summary>
                  <div>
                    <RangeControl
                      label="Westbound demand share"
                      value={settings.share}
                      min={50}
                      max={70}
                      unit="%"
                      onChange={(v) => update({ share: v })}
                    />
                    <RangeControl
                      label="Discharge per lane"
                      value={settings.saturation}
                      min={1600}
                      max={2000}
                      step={50}
                      unit="veh/h"
                      onChange={(v) => update({ saturation: v })}
                    />
                    <RangeControl
                      label="Cross-street arrivals"
                      value={settings.sideRate}
                      min={250}
                      max={700}
                      step={25}
                      unit="veh/h"
                      onChange={(v) => update({ sideRate: v })}
                    />
                    <p className="small muted">
                      Cross-street rate applies at each of the seven junctions.
                      Coordination favors westbound travel at 40 mph.
                    </p>
                  </div>
                </details>
                <div className="control-footer">
                  <FlaskConical size={16} />
                  <span>
                    Historical forecasts, assumed signals. This is not live
                    traffic.
                  </span>
                </div>
              </aside>
              <div className="results-column">
                <div
                  className="results-status"
                  role="status"
                  aria-live="polite"
                >
                  <span>
                    {pending ? (
                      <>
                        <LoaderCircle size={14} className="spin" />
                        Recalculating your scenario…
                      </>
                    ) : error ? (
                      <>
                        <AlertCircle size={14} />
                        Calculation needs attention
                      </>
                    ) : (
                      <>
                        <Check size={14} />
                        Scenario updated
                      </>
                    )}
                  </span>
                  <small>{settings.period} · one reproducible run</small>
                </div>
                {error && (
                  <div className="error-panel" role="alert">
                    <p>{error}</p>
                    <button onClick={() => setSettings((s) => ({ ...s }))}>
                      Retry calculation
                    </button>
                  </div>
                )}
                {experiment ? (
                  <div
                    className={'live-results ' + (pending ? 'updating' : '')}
                    aria-busy={pending}
                  >
                    <Corridor experiment={experiment} />
                    <Metrics
                      current={experiment.current}
                      baseline={experiment.baseline}
                    />
                    <p className="metric-caption">
                      Queue delay per entering trip, including waiting after the
                      arrival hour. Driving time is excluded.
                    </p>
                    <Takeaway experiment={experiment} />
                    <QueueChart experiment={experiment} />
                    <section className="panel alternatives-panel">
                      <div className="section-heading">
                        <h2>Compare a few alternatives</h2>
                        <p>
                          Same forecast and advanced assumptions. Each row
                          states its own signal and demand changes.
                        </p>
                      </div>
                      <div className="comparison-labels">
                        <span>Scenario</span>
                        <span>Main road</span>
                        <span>Side streets</span>
                        <span />
                      </div>
                      {[
                        {
                          label: 'Four-lane reference',
                          settings: {
                            ...settings,
                            ...{
                              design: 'four' as const,
                              green: 72,
                              coordinated: false,
                              reduction: 0,
                            },
                          },
                          result: experiment.baseline,
                        },
                        ...experiment.alternatives,
                      ].map((a) => (
                        <div className="alternative-row" key={a.label}>
                          <span>
                            <b>{a.label}</b>
                            <small>
                              {a.settings.green}s green · {a.settings.reduction}
                              % demand reduction
                            </small>
                          </span>
                          <strong>
                            {a.result.mainDelay.toFixed(2)}
                            <small> min</small>
                          </strong>
                          <strong>
                            {a.result.sideDelay.toFixed(2)}
                            <small> min</small>
                          </strong>
                          <button
                            title={'Apply ' + a.label}
                            aria-label={'Apply ' + a.label}
                            onClick={() => setSettings({ ...a.settings })}
                          >
                            <ArrowRight size={17} />
                          </button>
                        </div>
                      ))}
                      <p className="table-footnote">
                        Inward and outward six-lane designs share identical
                        modeled traffic geometry. Their land and tree impacts
                        differ.
                      </p>
                    </section>
                  </div>
                ) : (
                  <div className="initial-loading panel">
                    <LoaderCircle className="spin" size={25} />
                    <h2>Running the corridor experiment</h2>
                    <p>
                      Building queues for seven junctions in both directions.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </TabsContent>
          <TabsContent value="trees">
            <TreesAndTradeoffs tryScenario={treePreset} />
          </TabsContent>
          <TabsContent value="model">
            <ModelNotes />
          </TabsContent>
        </Tabs>
      </main>
      <footer className="site-footer">
        <span>
          Old Milton Traffic Lab · Nikhil Kapalavai · AI-assisted study
        </span>
        <div>
          <button
            onClick={() => {
              setTab('model');
              window.scrollTo({ top: 0, behavior: 'smooth' });
            }}
          >
            Model & sources
          </button>
          <a href="/reports/traffic-study.pdf" target="_blank" rel="noreferrer">
            Read the report <ArrowUpRight size={13} />
          </a>
        </div>
      </footer>
    </div>
  );
}
