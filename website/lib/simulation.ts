import inputs from './data/model-inputs.json' with { type: 'json' };

export type Period = '2027 AM' | '2027 PM' | '2047 AM';
export type Design = 'four' | 'inside' | 'outside';
export type Settings = {
  design: Design;
  green: number;
  coordinated: boolean;
  reduction: number;
  period: Period;
  share: number;
  saturation: number;
  sideRate: number;
};
export type Frame = {
  minute: number;
  main: number;
  side: number;
  nodes: number[];
};
export type Result = {
  mainDelay: number;
  sideDelay: number;
  allDelay: number;
  peakQueue: number;
  generated: number;
  exited: number;
  remaining60: number;
  clearedBy: number;
  residual: number;
  conservationError: number;
  storageViolation: number;
  frames: Frame[];
};
export const DEFAULTS: Settings = {
  design: 'four',
  green: 72,
  coordinated: false,
  reduction: 0,
  period: '2027 AM',
  share: 60,
  saturation: 1800,
  sideRate: 450,
};
export const PERIODS: Period[] = ['2027 AM', '2027 PM', '2047 AM'];
export function validateSettings(input: unknown): Settings {
  if (!input || typeof input !== 'object')
    throw new Error('Supply a scenario object.');
  const s = input as Settings;
  if (
    !['four', 'inside', 'outside'].includes(s.design) ||
    !PERIODS.includes(s.period) ||
    typeof s.coordinated !== 'boolean'
  )
    throw new Error(
      'Choose a supported design, forecast, and coordination setting.',
    );
  for (const [key, min, max] of [
    ['green', 60, 90],
    ['reduction', 0, 30],
    ['share', 50, 70],
    ['saturation', 1600, 2000],
    ['sideRate', 250, 700],
  ] as const) {
    if (
      typeof s[key] !== 'number' ||
      !Number.isFinite(s[key]) ||
      s[key] < min ||
      s[key] > max
    )
      throw new Error(`${key} must be between ${min} and ${max}.`);
  }
  return {
    design: s.design,
    green: s.green,
    coordinated: s.coordinated,
    reduction: s.reduction,
    period: s.period,
    share: s.share,
    saturation: s.saturation,
    sideRate: s.sideRate,
  };
}
const sum = (a: number[]) => a.reduce((x, y) => x + y, 0);
const mod = (a: number, b: number) => ((a % b) + b) % b;
type Direction = {
  ready: number[];
  moving: number[];
  source: number[];
  storage: number[];
  entry: number[];
  cont: number[];
  travel: number[];
  offsets: number[];
  events: Map<number, [number, number][]>;
  generated: number;
  exited: number;
  delay: number;
};

/** Direct port of the published one-second Python fluid-queue model.
 * Python arrival factors are preserved for exact seed-by-seed reproduction.
 * No new counts, live traffic, turning movements, or tree survival are inferred.
 */
export function simulate(settings: Settings, seed = 0): Result {
  const s = validateSettings(settings);
  if (!Number.isInteger(seed) || seed < 0 || seed > 4)
    throw new Error('Seed must be an integer from 0 to 4.');
  const factors = inputs.factors[seed],
    lanes = s.design === 'four' ? 2 : 3,
    cycle = 120,
    green = s.green,
    sat = s.saturation;
  const tt = inputs.lengths.map((l) =>
    Math.max(1, Math.round(l / (40 * 0.44704))),
  );
  const offsets = s.coordinated
    ? Array.from({ length: 7 }, (_, i) => sum(tt.slice(i)) % cycle)
    : [0, 35, 80, 15, 65, 100, 45];
  const volumes = inputs.volumes[s.period].map(
    (v) => v * (1 - s.reduction / 100),
  );
  const dirs: Direction[] = [false, true].map((reverse) => {
    const seq = (reverse ? [...volumes].reverse() : volumes).map(
      (v) => v * (reverse ? s.share / 100 : 1 - s.share / 100),
    );
    const lengths = reverse ? [...inputs.lengths].reverse() : inputs.lengths,
      prev = [0, ...seq],
      next = [...seq, 0];
    const total = prev.map((a, i) => Math.max(a, next[i]));
    return {
      ready: Array(7).fill(0),
      moving: Array(7).fill(0),
      source: Array(7).fill(0),
      storage: [1e9, ...lengths.map((l) => (l * lanes) / 7.5)],
      entry: prev.map((a, i) => Math.max(0, next[i] - a) / 3600),
      cont: total.map((q, i) => (q ? next[i] / q : 0)),
      travel: reverse ? [...tt].reverse() : tt,
      offsets: reverse ? [...offsets].reverse() : offsets,
      events: new Map(),
      generated: 0,
      exited: 0,
      delay: 0,
    };
  });
  const side = Array(7).fill(0);
  let sideGenerated = 0,
    sideExit = 0,
    sideDelay = 0,
    peakQueue = 0,
    remaining60 = 0,
    storageViolation = 0,
    time = 0;
  const frames: Frame[] = [];
  for (let t = 0; t < 10800; t++) {
    time = t;
    const factor = t < 3600 ? factors[Math.floor(t / 60)] : 0;
    for (const d of dirs) {
      for (const [j, a] of d.events.get(t) ?? []) {
        d.moving[j] -= a;
        d.ready[j] += a;
      }
      d.events.delete(t);
      for (let j = 0; j < 7; j++) {
        let a = d.entry[j] * factor;
        d.source[j] += a;
        d.generated += a;
        const room = Math.max(0, d.storage[j] - d.ready[j] - d.moving[j]);
        a = Math.min(d.source[j], room);
        d.source[j] -= a;
        d.ready[j] += a;
      }
      const flows = d.ready.map((q, j) => {
        const cap =
          mod(t - d.offsets[j], cycle) < green ? (sat * lanes) / 3600 : 0;
        let f = Math.min(q, cap);
        const p = d.cont[j];
        if (j < 6 && p > 0)
          f = Math.min(
            f,
            Math.max(0, d.storage[j + 1] - d.ready[j + 1] - d.moving[j + 1]) /
              p,
          );
        return f;
      });
      for (let j = 0; j < 7; j++) {
        const f = flows[j],
          p = d.cont[j];
        d.ready[j] -= f;
        d.exited += f * (1 - p);
        if (j < 6 && f * p > 0) {
          const a = f * p,
            key = t + d.travel[j];
          d.moving[j + 1] += a;
          if (!d.events.has(key)) d.events.set(key, []);
          d.events.get(key)!.push([j + 1, a]);
        }
        storageViolation = Math.max(
          storageViolation,
          d.ready[j] + d.moving[j] - d.storage[j],
          -d.ready[j],
        );
      }
      d.delay += sum(d.ready) + sum(d.source);
    }
    for (let j = 0; j < 7; j++) {
      const a = (s.sideRate / 3600) * factor;
      side[j] += a;
      sideGenerated += a;
      const phase = mod(t - offsets[j], cycle),
        cap = green + 8 <= phase && phase < cycle - 8 ? (2 * sat) / 3600 : 0;
      const f = Math.min(side[j], cap);
      side[j] -= f;
      sideExit += f;
    }
    sideDelay += sum(side);
    const mq = sum(dirs.map((d) => sum(d.ready) + sum(d.source)));
    peakQueue = Math.max(peakQueue, mq);
    if (t % 60 === 0)
      frames.push({
        minute: t / 60,
        main: mq,
        side: sum(side),
        nodes: dirs[0].ready.map(
          (q, j) =>
            q +
            dirs[0].source[j] +
            dirs[1].ready[6 - j] +
            dirs[1].source[6 - j],
        ),
      });
    if (t === 3599) remaining60 = sum(dirs.map((d) => d.generated - d.exited));
    if (
      t >= 3600 &&
      mq + sum(side) + sum(dirs.map((d) => sum(d.moving))) < 1e-6
    )
      break;
  }
  const generated = sum(dirs.map((d) => d.generated)),
    exited = sum(dirs.map((d) => d.exited)),
    delay = sum(dirs.map((d) => d.delay));
  const conservationError = Math.max(
    ...dirs.map((d) =>
      Math.abs(
        d.generated - d.exited - sum(d.ready) - sum(d.moving) - sum(d.source),
      ),
    ),
    Math.abs(sideGenerated - sideExit - sum(side)),
  );
  if (conservationError > 1e-5 || storageViolation > 1e-6)
    throw new Error('The model failed an internal vehicle-balance check.');
  frames.push({
    minute: (time + 1) / 60,
    main: sum(dirs.map((d) => sum(d.ready) + sum(d.source))),
    side: sum(side),
    nodes: dirs[0].ready.map(
      (q, j) =>
        q + dirs[0].source[j] + dirs[1].ready[6 - j] + dirs[1].source[6 - j],
    ),
  });
  return {
    mainDelay: delay / Math.max(1, generated) / 60,
    sideDelay: sideDelay / Math.max(1, sideGenerated) / 60,
    allDelay: (delay + sideDelay) / Math.max(1, generated + sideGenerated) / 60,
    peakQueue,
    generated,
    exited,
    remaining60,
    clearedBy: (time + 1) / 60,
    residual: generated - exited + sum(side),
    conservationError,
    storageViolation,
    frames,
  };
}
export type Experiment = {
  settings: Settings;
  current: Result;
  baseline: Result;
  alternatives: { label: string; settings: Settings; result: Result }[];
};
export function runExperiment(settings: Settings): Experiment {
  const s = validateSettings(settings);
  const baselineSettings = {
    ...s,
    design: 'four' as Design,
    green: 72,
    coordinated: false,
    reduction: 0,
  };
  const alternatives = [
    {
      label: 'Four lanes + better signals',
      settings: {
        ...s,
        design: 'four' as Design,
        green: 84,
        coordinated: true,
        reduction: 0,
      },
    },
    {
      label: 'Four lanes + signals + 20% fewer trips',
      settings: {
        ...s,
        design: 'four' as Design,
        green: 84,
        coordinated: true,
        reduction: 20,
      },
    },
    {
      label: 'Six lanes + coordinated signals',
      settings: {
        ...s,
        design: 'inside' as Design,
        green: 72,
        coordinated: true,
        reduction: 0,
      },
    },
  ];
  return {
    settings: s,
    current: simulate(s),
    baseline: simulate(baselineSettings),
    alternatives: alternatives.map((a) => ({
      ...a,
      result: simulate(a.settings),
    })),
  };
}
