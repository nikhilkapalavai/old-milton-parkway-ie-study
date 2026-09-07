import {
  ArrowUpRight,
  Trees,
  ArrowRight,
  FileText,
  Route,
  Clock,
  Users,
  FlaskConical,
} from 'lucide-react';
import {
  Table,
  TableHeader,
  TableHead,
  TableRow,
  TableBody,
  TableCell,
} from '@/components/ui/table';
export const GITHUB =
  'https://github.com/nikhilkapalavai/old-milton-parkway-ie-study';
const GDOT =
  'https://www.dot.ga.gov/_layouts/GDOT.SharePoint.CustomHttpHandlers/PWDocumentDownloadHandler.ashx?DocGUID=11d2e65d-2e90-4a1a-a0a8-e75ae818d78f&Filename=0017187_CR_MAR2022.pdf';
export function TreesAndTradeoffs({
  tryScenario,
}: {
  tryScenario: () => void;
}) {
  return (
    <div className="notes-view">
      <section className="evidence-intro">
        <div className="evidence-icon">
          <Trees size={32} />
        </div>
        <div>
          <div className="eyebrow">THE QUESTION THAT STARTED THIS PROJECT</div>
          <h2>Did the median trees have to go?</h2>
          <p>
            The record explains why GDOT chose to widen into the median. It does
            not establish that every removed tree was unavoidable.
          </p>
        </div>
      </section>
      <div className="finding-grid">
        <article className="panel finding">
          <span className="eyebrow">01 / THE DOCUMENTED TRADEOFF</span>
          <h3>Less land. Lower project cost.</h3>
          <p>
            The 2022 concept comparison put inward widening at $29.2 million and
            outward widening at $41.8 million. Using the median reduced property
            impacts from 63 parcels to 18.
          </p>
          <a href={GDOT} target="_blank" rel="noreferrer">
            GDOT concept · PDF page 14 <ArrowUpRight size={15} />
          </a>
        </article>
        <article className="panel finding">
          <span className="eyebrow">02 / THE UNRESOLVED QUESTION</span>
          <h3>Could individual trees have survived?</h3>
          <p>
            That needs a tree inventory, final grading and drainage plans,
            utility layouts, and an arborist’s root-zone assessment. This
            traffic model cannot calculate a preservation count.
          </p>
          <a href="/reports/gdot-evidence.pdf" target="_blank" rel="noreferrer">
            Read the source excerpts <ArrowUpRight size={15} />
          </a>
        </article>
      </div>
      <section className="panel comparison-table">
        <div className="section-heading">
          <h2>Three paths, different costs</h2>
          <p>
            Historical concept estimates, not current bids or life-cycle costs.
          </p>
        </div>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Design alternative</TableHead>
              <TableHead>Travel lanes</TableHead>
              <TableHead>Total project estimate</TableHead>
              <TableHead>Right-of-way estimate</TableHead>
              <TableHead>Parcels affected</TableHead>
              <TableHead>Median-tree implication</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow>
              <TableCell>
                <b>Retain four lanes</b>
              </TableCell>
              <TableCell>4</TableCell>
              <TableCell>Not estimated here</TableCell>
              <TableCell>Not estimated here</TableCell>
              <TableCell>Not assessed</TableCell>
              <TableCell>
                A preservation candidate; bridge and tree feasibility unresolved
              </TableCell>
            </TableRow>
            <TableRow>
              <TableCell>
                <b>Widen inward</b>
                <small>Selected concept</small>
              </TableCell>
              <TableCell>6</TableCell>
              <TableCell>$29,196,795</TableCell>
              <TableCell>$1,506,000</TableCell>
              <TableCell>18</TableCell>
              <TableCell>Substantial median disturbance</TableCell>
            </TableRow>
            <TableRow>
              <TableCell>
                <b>Widen outward</b>
              </TableCell>
              <TableCell>6</TableCell>
              <TableCell>$41,800,000</TableCell>
              <TableCell>$11,200,000</TableCell>
              <TableCell>63</TableCell>
              <TableCell>
                Could reduce median encroachment; tree survival unverified
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
        <div className="source-note">
          The outward option is about <b>$12.6m more in total</b>, including
          about <b>$9.7m more in right-of-way costs</b>. The $12.6m difference
          is not all land acquisition.{' '}
          <a href={GDOT} target="_blank" rel="noreferrer">
            Source: GDOT 2022 concept comparison ↗
          </a>
        </div>
      </section>
      <section className="panel cross-section-panel">
        <div className="section-heading">
          <h2>What changes in the model?</h2>
          <p>
            Only traffic lanes and operating assumptions affect queues. Trees
            are not a traffic parameter.
          </p>
        </div>
        <div className="road-section">
          <span className="lane">←</span>
          <span className="lane">←</span>
          <span className="median">
            <Trees size={20} /> Existing median
          </span>
          <span className="lane">→</span>
          <span className="lane">→</span>
        </div>
        <div className="cross-label">Four lanes · preservation candidate</div>
        <div className="road-section">
          <span className="lane">←</span>
          <span className="lane">←</span>
          <span className="lane added">←</span>
          <span className="median narrow">Median</span>
          <span className="lane added">→</span>
          <span className="lane">→</span>
          <span className="lane">→</span>
        </div>
        <div className="cross-label">
          Six lanes with inward widening · diagram is not to scale
        </div>
        <p className="section-text">
          Inward and outward widening give identical traffic results here
          because both use the same six-lane geometry and settings. Real-world
          turns, access, construction, and environmental impacts could differ.
        </p>
      </section>
      <section className="alternatives-story">
        <div className="section-heading">
          <span className="eyebrow">IF REMOVAL WAS REQUIRED</span>
          <h2>There are still ways to improve traffic.</h2>
          <p>These measures can complement necessary road and bridge work.</p>
        </div>
        <div className="action-grid">
          {[
            [
              Clock,
              'Coordinate the signals',
              'Measure existing timing, then tune offsets and green time while protecting side streets and pedestrian crossings.',
            ],
            [
              Users,
              'Reduce the peak',
              'Test carpools, staggered shifts, and useful transit connections. A 20% target means about 812 fewer vehicles in the busiest modeled 2027 AM segment.',
            ],
            [
              Route,
              'Study specific bottlenecks',
              'Evaluate turn-lane storage and local access changes with actual movement counts. These geometry changes have not been simulated here.',
            ],
          ].map(([Icon, title, desc]) => {
            const I = Icon as typeof Clock;
            return (
              <article key={String(title)} className="panel action-card">
                <I size={23} />
                <h3>{String(title)}</h3>
                <p>{String(desc)}</p>
              </article>
            );
          })}
        </div>
        <button className="primary-button" onClick={tryScenario}>
          Try four lanes with signals + 20% fewer trips <ArrowRight size={17} />
        </button>
        <p className="small muted">
          Demand reductions are experiment targets, not proven outcomes of a
          specific program. Tree replanting restores canopy; it does not reduce
          traffic queues.
        </p>
      </section>
    </div>
  );
}
export function ModelNotes() {
  return (
    <div className="notes-view">
      <section className="evidence-intro">
        <div className="evidence-icon">
          <FlaskConical size={32} />
        </div>
        <div>
          <div className="eyebrow">UNDER THE HOOD</div>
          <h2>A transparent experiment, with limits.</h2>
          <p>
            A one-second aggregate queue model of seven junctions in both
            directions. It is an exploratory student study, not a calibrated
            forecast of today’s road.
          </p>
        </div>
      </section>
      <div className="finding-grid">
        <section className="panel finding">
          <h3>What comes from data</h3>
          <ul>
            <li>
              Road paths and six link lengths from OpenStreetMap snapshots.
            </li>
            <li>
              Historical GDOT no-build segment forecasts for 2027 AM, 2027 PM,
              and 2047 AM.
            </li>
            <li>GDOT’s concept cost and property-impact comparison.</li>
          </ul>
          <p>
            Mapped junction spacing totals 3.09 km (1.92 miles), which differs
            from the stated construction limits. It approximates stop-line
            spacing and is not a surveyed lane network.
          </p>
        </section>
        <section className="panel finding">
          <h3>What is assumed</h3>
          <ul>
            <li>
              A 120-second cycle, 16 seconds of lost time, 40 mph progression
              speed, and invented reference offsets.
            </li>
            <li>
              Directional split, saturation flow, synthetic side-road demand,
              and two aggregate side-road discharge lanes.
            </li>
            <li>
              An initially empty network and one hour of arrivals, followed by
              up to two hours of clearing.
            </li>
          </ul>
          <p>No Google Maps live traffic or current field counts are used.</p>
        </section>
      </div>
      <section className="panel finding wide-note">
        <h3>How to read the results</h3>
        <p>
          <b>Delay is queued time per entering trip.</b> It includes waiting
          after the first hour ends and excludes driving time. It is not the
          travel time from one end of the corridor to the other. Trips can enter
          or leave at intermediate junctions.
        </p>
        <p>
          The website uses one reproducible arrival pattern (seed 0). The report
          averages five patterns. Website values can therefore differ slightly
          from the report’s averages. Every slider change reruns the same
          mathematical model in your browser.
        </p>
        <p>
          The four-lane reference uses 72 seconds of main-road green, no demand
          reduction, and invented offsets. It is recalculated using your
          selected forecast, directional split, discharge rate, and side-road
          demand. It is not a measured “before construction” case.
        </p>
        <p>
          <b>
            Current traffic operations could already be better than this
            reference.
          </b>{' '}
          The model omits detailed turns, lane changes, pedestrian phases,
          side-road spillback, incidents, construction staging, and traffic
          rerouting or induced demand. It uses equal demand for widening
          comparisons to isolate lane capacity.
        </p>
      </section>
      <section className="panel finding wide-note">
        <h3>What was checked</h3>
        <p>
          The browser model was compared against all 280 published Python runs.
          Delay, peak queue, remaining traffic at minute 60, and clearing time
          match to numerical tolerance. Vehicle conservation, finite link
          storage, demand scaling, and input bounds are also checked. These
          checks verify the implementation; field calibration is still required.
        </p>
        <p>
          Before making a policy recommendation, obtain actual signal plans,
          turning counts, observed queues and travel times, final construction
          plans, and tree-survival assessments. Test the calibrated model on
          observations that were not used to tune it.
        </p>
      </section>
      <div className="resource-grid">
        <a
          className="panel resource"
          href="/reports/traffic-study.pdf"
          target="_blank"
          rel="noreferrer"
        >
          <FileText size={24} />
          <span>
            <b>Read the full study</b>
            <small>Methods, 280 runs, findings & limitations · PDF</small>
          </span>
          <ArrowUpRight size={18} />
        </a>
        <a
          className="panel resource"
          href={GITHUB}
          target="_blank"
          rel="noreferrer"
        >
          <Route size={24} />
          <span>
            <b>Explore the source</b>
            <small>Python model, input data, reports & website</small>
          </span>
          <ArrowUpRight size={18} />
        </a>
      </div>
      <section className="sources">
        <h3>Primary sources</h3>
        <a href={GDOT} target="_blank" rel="noreferrer">
          GDOT approved concept report (2022) · PDF p14 alternatives, p131
          demand <ArrowUpRight size={14} />
        </a>
        <a
          href="https://www.dot.ga.gov/applications/geopi/Pages/Dashboard.aspx?ProjectID=0017187"
          target="_blank"
          rel="noreferrer"
        >
          GDOT Project 0017187 dashboard <ArrowUpRight size={14} />
        </a>
        <a
          href="https://www.openstreetmap.org/copyright"
          target="_blank"
          rel="noreferrer"
        >
          © OpenStreetMap contributors · Open Database License{' '}
          <ArrowUpRight size={14} />
        </a>
      </section>
      <p className="authorship">
        Project by Nikhil Kapalavai · September 2026 · Prepared with AI
        assistance. This project documents a reproducible modeling study and
        source review; it does not claim fieldwork or official GDOT endorsement.
      </p>
    </div>
  );
}
