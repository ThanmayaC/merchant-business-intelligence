// Dashboard.jsx — KPI cards + charts, all fed by the analytics API.
import { useEffect, useState } from "react";
import {
  Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { api } from "../api.js";

// Indian number format: 1234567.8 -> "₹12,34,567.80"
const inr = (n) => "₹" + Number(n).toLocaleString("en-IN", { maximumFractionDigits: 2 });

function Kpi({ label, value }) {
  return (
    <div className="card kpi">
      <div className="muted">{label}</div>
      <div className="kpi-value">{value}</div>
    </div>
  );
}

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [seeding, setSeeding] = useState(false);

  // Fetch all four analytics endpoints in PARALLEL (Promise.all).
  async function load() {
    setError("");
    try {
      const [summary, top, failures, rates] = await Promise.all([
        api.getSummary(),
        api.getTopMerchants(5),
        api.getFailureReasons(),
        api.getMerchantSuccessRates(),
      ]);
      setData({ summary, top, failures, rates });
    } catch (err) {
      setError(err.message);
    }
  }

  async function seed() {
    setSeeding(true);
    try {
      await api.seed();
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setSeeding(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const empty = data && data.summary.total_transactions === 0;

  return (
    <div className="stack">
      <div className="row-between">
        <h2>Dashboard</h2>
        <button onClick={seed} disabled={seeding}>
          {seeding ? "Loading CSVs…" : "Load / reload sample data"}
        </button>
      </div>

      {error && <div className="card error">{error}</div>}
      {!data && !error && <p className="muted">Loading…</p>}
      {empty && <div className="card">No data yet. Click “Load / reload sample data”.</div>}

      {data && !empty && (
        <>
          <div className="grid kpis">
            <Kpi label="Total transactions" value={data.summary.total_transactions.toLocaleString("en-IN")} />
            <Kpi label="Success rate" value={`${data.summary.success_rate_pct}%`} />
            <Kpi label="Total volume" value={inr(data.summary.total_volume_inr)} />
            <Kpi label="Successful volume" value={inr(data.summary.successful_volume_inr)} />
            <Kpi label="Failed transactions" value={data.summary.failed_transactions} />
          </div>

          <div className="grid two">
            <div className="card">
              <h3>Top 5 merchants by successful volume</h3>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={data.top} layout="vertical" margin={{ left: 20, right: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                  <XAxis type="number" tickFormatter={(v) => `₹${Math.round(v / 1000)}k`} />
                  <YAxis type="category" dataKey="merchant_name" width={100} />
                  <Tooltip formatter={(v) => inr(v)} />
                  <Bar dataKey="successful_volume_inr" name="Successful volume" fill="#2a6fdb" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="card">
              <h3>Failure reasons</h3>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={data.failures} margin={{ left: 0, right: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="failure_reason" tick={{ fontSize: 11 }} interval={0} angle={-15} textAnchor="end" height={50} />
                  <YAxis allowDecimals={false} />
                  <Tooltip formatter={(v, _n, p) => [`${v} (${p.payload.share_pct}%)`, "Failures"]} />
                  <Bar dataKey="count" name="Failures" fill="#d9534f" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="card">
            <h3>Merchant success rates (lowest first)</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={data.rates} margin={{ left: 0, right: 10 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="merchant_name" tick={{ fontSize: 11 }} interval={0} angle={-25} textAnchor="end" height={60} />
                <YAxis domain={[80, 100]} unit="%" />
                <Tooltip formatter={(v) => `${v}%`} />
                <Bar dataKey="success_rate_pct" name="Success rate">
                  {/* Colour each bar: red below 95%, green otherwise. */}
                  {data.rates.map((r) => (
                    <Cell key={r.merchant_id} fill={r.success_rate_pct < 95 ? "#d9534f" : "#2e9e5b"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  );
}
