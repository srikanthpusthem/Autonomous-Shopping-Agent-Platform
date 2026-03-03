import { FormEvent, useEffect, useMemo, useState } from "react";
import { api } from "./lib/api";
import { useRunEvents } from "./hooks/useRunEvents";
import type { Profile, RankedProduct, RunResponse } from "./types";

function commaSplit(value: string): string[] {
  return value
    .split(",")
    .map((entry) => entry.trim())
    .filter(Boolean);
}

export default function App() {
  const [token, setToken] = useState<string>(localStorage.getItem("token") ?? "");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [selectedProfileId, setSelectedProfileId] = useState<string>("");
  const [prompt, setPrompt] = useState("");
  const [activeRun, setActiveRun] = useState<RunResponse | null>(null);
  const [error, setError] = useState<string>("");

  const [newProfileName, setNewProfileName] = useState("Me");
  const [newProfileBudgetMin, setNewProfileBudgetMin] = useState<string>("");
  const [newProfileBudgetMax, setNewProfileBudgetMax] = useState<string>("");
  const [newProfilePreferredBrands, setNewProfilePreferredBrands] = useState("");
  const [newProfileAvoidBrands, setNewProfileAvoidBrands] = useState("");
  const [newProfileUseCases, setNewProfileUseCases] = useState("gym,work");
  const [shippingPreference, setShippingPreference] = useState<"fastest" | "balanced" | "cheapest">(
    "balanced",
  );

  const { events, connectionError } = useRunEvents(activeRun?.id ?? null);

  const topRecommendations = useMemo<RankedProduct[]>(() => {
    return activeRun?.final_output?.top_recommendations ?? [];
  }, [activeRun]);

  useEffect(() => {
    if (!token) {
      return;
    }
    fetchProfiles(token).catch((err) => {
      setError(err instanceof Error ? err.message : "Failed to load profiles");
    });
  }, [token]);

  async function fetchProfiles(activeToken: string) {
    const loaded = await api.getProfiles(activeToken);
    setProfiles(loaded);
    if (!selectedProfileId && loaded.length > 0) {
      setSelectedProfileId(loaded[0].id);
    }
  }

  async function handleAuth(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      const response =
        authMode === "login" ? await api.login(email, password) : await api.register(email, password);
      setToken(response.access_token);
      localStorage.setItem("token", response.access_token);
      await fetchProfiles(response.access_token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    }
  }

  async function handleCreateProfile(event: FormEvent) {
    event.preventDefault();
    if (!token) {
      return;
    }
    setError("");
    try {
      const created = await api.createProfile(token, {
        name: newProfileName,
        budget_min: newProfileBudgetMin ? Number(newProfileBudgetMin) : null,
        budget_max: newProfileBudgetMax ? Number(newProfileBudgetMax) : null,
        preferred_brands: commaSplit(newProfilePreferredBrands),
        avoid_brands: commaSplit(newProfileAvoidBrands),
        use_case_tags: commaSplit(newProfileUseCases),
        shipping_speed_preference: shippingPreference,
      });
      setProfiles((prev) => [...prev, created]);
      setSelectedProfileId(created.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create profile");
    }
  }

  async function handleStartRun(event: FormEvent) {
    event.preventDefault();
    if (!token || !selectedProfileId || !prompt.trim()) {
      return;
    }
    setError("");
    try {
      const run = await api.createRun(token, selectedProfileId, prompt.trim());
      setActiveRun(run);

      const interval = window.setInterval(async () => {
        const latest = await api.getRun(token, run.id);
        setActiveRun(latest);
        if (["done", "error"].includes(latest.status)) {
          window.clearInterval(interval);
        }
      }, 1200);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start run");
    }
  }

  async function handleFeedback(type: "pick" | "not_interested", product: RankedProduct) {
    if (!token || !selectedProfileId) {
      return;
    }
    try {
      await api.postFeedback(token, {
        profile_id: selectedProfileId,
        run_id: activeRun?.id,
        feedback_type: type,
        product_provider: product.provider,
        product_id: product.product_id,
        note: type === "pick" ? `User picked ${product.title}` : `User disliked ${product.title}`,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save feedback");
    }
  }

  if (!token) {
    return (
      <main className="mx-auto min-h-screen max-w-md px-6 py-14">
        <h1 className="text-3xl font-semibold">Shopping Copilot</h1>
        <p className="mt-2 text-sm text-slate-300">Sign in to start personalized shopping runs.</p>

        <form onSubmit={handleAuth} className="mt-8 space-y-3 rounded-xl border border-slate-800 bg-slate-900 p-4">
          <input
            className="w-full rounded bg-slate-800 px-3 py-2"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="Email"
            required
          />
          <input
            className="w-full rounded bg-slate-800 px-3 py-2"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Password"
            required
          />
          <button className="w-full rounded bg-cyan-500 px-3 py-2 font-medium text-slate-950" type="submit">
            {authMode === "login" ? "Login" : "Register"}
          </button>
          <button
            className="w-full rounded border border-slate-600 px-3 py-2 text-sm"
            type="button"
            onClick={() => setAuthMode((mode) => (mode === "login" ? "register" : "login"))}
          >
            Switch to {authMode === "login" ? "Register" : "Login"}
          </button>
        </form>

        {error ? <p className="mt-4 text-sm text-rose-300">{error}</p> : null}
      </main>
    );
  }

  return (
    <main className="mx-auto min-h-screen max-w-6xl px-6 py-10">
      <header className="mb-8 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-3xl font-semibold">Shopping Copilot</h1>
          <p className="text-sm text-slate-300">Multi-agent recommendations with live reasoning.</p>
        </div>
        <button
          className="rounded border border-slate-700 px-3 py-2 text-sm"
          onClick={() => {
            localStorage.removeItem("token");
            setToken("");
          }}
          type="button"
        >
          Logout
        </button>
      </header>

      <section className="grid gap-6 lg:grid-cols-[320px_1fr]">
        <aside className="space-y-4 rounded-xl border border-slate-800 bg-slate-900/80 p-4">
          <h2 className="text-lg font-medium">Profiles</h2>
          <button
            className="w-full rounded border border-slate-600 px-3 py-2 text-sm"
            onClick={() => fetchProfiles(token)}
            type="button"
          >
            Refresh profiles
          </button>

          <select
            className="w-full rounded bg-slate-800 px-3 py-2"
            value={selectedProfileId}
            onChange={(event) => setSelectedProfileId(event.target.value)}
          >
            <option value="">Select profile</option>
            {profiles.map((profile) => (
              <option key={profile.id} value={profile.id}>
                {profile.name}
              </option>
            ))}
          </select>

          <form onSubmit={handleCreateProfile} className="space-y-2 border-t border-slate-800 pt-3">
            <p className="text-sm text-slate-300">Create profile</p>
            <input
              className="w-full rounded bg-slate-800 px-3 py-2"
              value={newProfileName}
              onChange={(event) => setNewProfileName(event.target.value)}
              placeholder="Name"
            />
            <input
              className="w-full rounded bg-slate-800 px-3 py-2"
              value={newProfileBudgetMin}
              onChange={(event) => setNewProfileBudgetMin(event.target.value)}
              placeholder="Budget min"
            />
            <input
              className="w-full rounded bg-slate-800 px-3 py-2"
              value={newProfileBudgetMax}
              onChange={(event) => setNewProfileBudgetMax(event.target.value)}
              placeholder="Budget max"
            />
            <input
              className="w-full rounded bg-slate-800 px-3 py-2"
              value={newProfilePreferredBrands}
              onChange={(event) => setNewProfilePreferredBrands(event.target.value)}
              placeholder="Preferred brands (comma-separated)"
            />
            <input
              className="w-full rounded bg-slate-800 px-3 py-2"
              value={newProfileAvoidBrands}
              onChange={(event) => setNewProfileAvoidBrands(event.target.value)}
              placeholder="Avoid brands (comma-separated)"
            />
            <input
              className="w-full rounded bg-slate-800 px-3 py-2"
              value={newProfileUseCases}
              onChange={(event) => setNewProfileUseCases(event.target.value)}
              placeholder="Use cases (comma-separated)"
            />
            <select
              className="w-full rounded bg-slate-800 px-3 py-2"
              value={shippingPreference}
              onChange={(event) =>
                setShippingPreference(event.target.value as "fastest" | "balanced" | "cheapest")
              }
            >
              <option value="fastest">Fastest</option>
              <option value="balanced">Balanced</option>
              <option value="cheapest">Cheapest</option>
            </select>
            <button className="w-full rounded bg-cyan-500 px-3 py-2 font-medium text-slate-950" type="submit">
              Create profile
            </button>
          </form>
        </aside>

        <section className="space-y-4 rounded-xl border border-slate-800 bg-slate-900/80 p-4">
          <form onSubmit={handleStartRun} className="space-y-3">
            <textarea
              className="h-28 w-full rounded bg-slate-800 px-3 py-2"
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              placeholder="Example: I need durable gym headphones under $120 with fast shipping"
            />
            <button className="rounded bg-emerald-400 px-4 py-2 font-medium text-slate-950" type="submit">
              Start run
            </button>
          </form>

          {error ? <p className="text-sm text-rose-300">{error}</p> : null}
          {connectionError ? <p className="text-sm text-amber-300">{connectionError}</p> : null}

          <div className="grid gap-4 lg:grid-cols-[1fr_1fr]">
            <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
              <h3 className="mb-2 font-medium">Live agent events</h3>
              <div className="max-h-80 space-y-2 overflow-auto pr-2">
                {events.length === 0 ? (
                  <p className="text-sm text-slate-400">Run events will appear here.</p>
                ) : (
                  events.map((event, index) => (
                    <div key={`${event.timestamp}-${index}`} className="rounded border border-slate-800 p-2 text-sm">
                      <p className="font-medium text-cyan-300">
                        {event.agent_name} · {event.event_type}
                      </p>
                      <p className="text-slate-200">{event.message}</p>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
              <h3 className="mb-2 font-medium">Top recommendations</h3>
              <div className="max-h-80 space-y-3 overflow-auto pr-2">
                {topRecommendations.length === 0 ? (
                  <p className="text-sm text-slate-400">Recommendations appear when ranking finishes.</p>
                ) : (
                  topRecommendations.map((item) => (
                    <article key={`${item.provider}-${item.product_id}`} className="rounded border border-slate-800 p-3">
                      <h4 className="font-medium">{item.title}</h4>
                      <p className="text-sm text-slate-300">
                        ${item.price.toFixed(2)} · {item.rating.toFixed(1)}★ · ETA {item.eta_days}d
                      </p>
                      <p className="mt-2 text-sm text-emerald-300">Pros: {item.pros.join(", ") || "n/a"}</p>
                      <p className="text-sm text-rose-300">Cons: {item.cons.join(", ") || "n/a"}</p>
                      <p className="mt-2 text-sm text-slate-200">Why: {item.why_recommended}</p>
                      <p className="text-sm text-slate-400">Tradeoff: {item.tradeoffs}</p>
                      <div className="mt-3 flex gap-2">
                        <button
                          className="rounded bg-emerald-400 px-3 py-1 text-sm font-medium text-slate-950"
                          onClick={() => handleFeedback("pick", item)}
                          type="button"
                        >
                          Pick this
                        </button>
                        <button
                          className="rounded border border-slate-600 px-3 py-1 text-sm"
                          onClick={() => handleFeedback("not_interested", item)}
                          type="button"
                        >
                          Not interested
                        </button>
                      </div>
                    </article>
                  ))
                )}
              </div>
            </div>
          </div>
        </section>
      </section>
    </main>
  );
}
