import assert from 'node:assert/strict';
import {
  simulate,
  runExperiment,
  validateSettings,
  DEFAULTS,
} from './simulation.ts';
import fixtures from './data/verification.json' with { type: 'json' };
let count = 0;
for (const expected of fixtures.runs) {
  const sc = fixtures.scenarios.find((s) => s.name === expected.scenario);
  const settings = {
    ...DEFAULTS,
    design: sc.lanes === 2 ? 'four' : 'inside',
    green: sc.green,
    coordinated: sc.coordinated,
    reduction: sc.reduction * 100,
    period: expected.period,
    share: expected.share * 100,
    saturation: expected.saturation,
    sideRate: expected.side_rate,
  };
  const actual = simulate(settings, expected.seed);
  for (const [a, b] of [
    ['mainDelay', 'main_delay_min'],
    ['sideDelay', 'side_delay_min'],
    ['allDelay', 'all_delay_min'],
    ['peakQueue', 'max_main_queue_vehicles'],
    ['remaining60', 'main_remaining_at_60min'],
    ['clearedBy', 'cleared_by_min'],
  ])
    assert.ok(
      Math.abs(actual[a] - expected[b]) < 1e-7,
      `${expected.scenario} ${a}: ${actual[a]} != ${expected[b]}`,
    );
  assert.ok(actual.residual < 1e-5);
  count++;
}
const a = simulate({ ...DEFAULTS, design: 'inside' }),
  b = simulate({ ...DEFAULTS, design: 'outside' });
assert.deepEqual(
  a,
  b,
  'Identical inside/outside lane geometry must produce identical traffic',
);
const original = simulate(DEFAULTS),
  reduced = simulate({ ...DEFAULTS, reduction: 20 });
assert.ok(Math.abs(reduced.generated / original.generated - 0.8) < 1e-10);
for (const patch of [
  { green: 100 },
  { sideRate: -1 },
  { reduction: NaN },
  { design: 'unknown' },
  { share: Infinity },
])
  assert.throws(() => validateSettings({ ...DEFAULTS, ...patch }));
for (const design of ['four', 'inside'])
  for (const green of [60, 90])
    for (const period of ['2027 AM', '2047 AM']) {
      const result = simulate({
        ...DEFAULTS,
        design,
        green,
        period,
        share: 70,
        saturation: 1600,
        sideRate: 700,
      });
      assert.ok(
        result.conservationError < 1e-5 && result.storageViolation < 1e-6,
      );
      assert.ok(
        result.mainDelay >= 0 &&
          result.sideDelay >= 0 &&
          result.frames.length > 60,
      );
    }
const exp = runExperiment({ ...DEFAULTS, reduction: 20 });
assert.equal(exp.baseline.generated, original.generated);
console.log(
  `PASS: browser model matches all ${count} published Python runs; geometry equivalence, demand scaling, input validation, and boundary conservation checks passed.`,
);
