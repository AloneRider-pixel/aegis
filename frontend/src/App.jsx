import React, { useState, useEffect } from 'react'

const API = '/api'

function getHeaders() {
  const token = localStorage.getItem('token')
  return { 'Content-Type': 'application/json', ...(token && { Authorization: `Bearer ${token}` }) }
}

// ─── Login Page ───
function Login({ onLogin }) {
  const [email, setEmail] = useState('admin@aegis.io')
  const [password, setPassword] = useState('admin123')
  const [error, setError] = useState('')
  const [isLoggingIn, setIsLoggingIn] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setIsLoggingIn(true)
    try {
      const res = await fetch(`${API}/auth/login`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })
      if (!res.ok) throw new Error('Invalid credentials')
      const data = await res.json()
      localStorage.setItem('token', data.access_token)
      onLogin(data)
    } catch (err) { setError(err.message) }
    finally { setIsLoggingIn(false) }
  }

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center">
      <div className="w-full max-w-md p-8">
        <div className="text-center mb-8">
          <span className="text-5xl">🛡️</span>
          <h1 className="text-2xl font-bold text-white mt-4">Aegis</h1>
          <p className="text-gray-400 text-sm mt-1">AI Incident Response Platform</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4 bg-gray-900 p-6 rounded-xl border border-gray-800">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-1">Email</label>
            <input id="email" type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="admin@aegis.io" className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500" required disabled={isLoggingIn} />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-1">Password</label>
            <input id="password" type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500" required disabled={isLoggingIn} />
          </div>
          {error && <p className="text-red-400 text-sm" role="alert">{error}</p>}
          <button type="submit" disabled={isLoggingIn} className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed">
            {isLoggingIn ? 'Signing In...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  )
}

// ─── Severity Badge ───
function SeverityBadge({ severity }) {
  const colors = { 'sev-1': 'bg-red-500/20 text-red-400', 'sev-2': 'bg-orange-500/20 text-orange-400', 'sev-3': 'bg-yellow-500/20 text-yellow-400', 'sev-4': 'bg-blue-500/20 text-blue-400' }
  return <span className={`px-2 py-0.5 rounded text-xs font-bold ${colors[severity] || 'bg-gray-700 text-gray-300'}`}>{severity?.toUpperCase()}</span>
}

// ─── Status Badge ───
function StatusBadge({ status }) {
  const colors = {
    detected: 'bg-red-500/20 text-red-400', acknowledged: 'bg-orange-500/20 text-orange-400',
    investigating: 'bg-yellow-500/20 text-yellow-400', root_cause_identified: 'bg-purple-500/20 text-purple-400',
    awaiting_approval: 'bg-indigo-500/20 text-indigo-400', remediating: 'bg-cyan-500/20 text-cyan-400',
    verifying: 'bg-teal-500/20 text-teal-400', resolved: 'bg-green-500/20 text-green-400',
    closed: 'bg-gray-500/20 text-gray-400', failed: 'bg-red-700/20 text-red-400',
  }
  return <span className={`px-2 py-0.5 rounded text-xs font-medium ${colors[status] || 'bg-gray-700 text-gray-300'}`}>{status?.replace(/_/g, ' ')}</span>
}

// ─── Dashboard Page ───
function DashboardPage({ user }) {
  const [incidents, setIncidents] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API}/incidents?limit=10`, { headers: getHeaders() })
      .then(r => r.json()).then(d => { setIncidents(d.incidents || []); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  const active = incidents.filter(i => !['resolved', 'closed'].includes(i.status)).length
  const sev1 = incidents.filter(i => i.severity === 'sev-1' && !['resolved', 'closed'].includes(i.status)).length

  return (
    <div>
      <h2 className="text-xl font-bold text-white mb-6">Operations Dashboard</h2>
      <div className="grid grid-cols-4 gap-4 mb-8">
        <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
          <p className="text-gray-400 text-sm">Active Incidents</p>
          <p className="text-3xl font-bold text-white mt-1">{active}</p>
        </div>
        <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
          <p className="text-gray-400 text-sm">SEV-1 Open</p>
          <p className="text-3xl font-bold text-red-400 mt-1">{sev1}</p>
        </div>
        <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
          <p className="text-gray-400 text-sm">Total Incidents</p>
          <p className="text-3xl font-bold text-white mt-1">{incidents.length}</p>
        </div>
        <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
          <p className="text-gray-400 text-sm">AI Investigations</p>
          <p className="text-3xl font-bold text-blue-400 mt-1">{incidents.filter(i => i.probable_root_cause).length}</p>
        </div>
      </div>
      <h3 className="text-lg font-semibold text-white mb-4">Recent Incidents</h3>
      <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
        <table className="w-full">
          <thead><tr className="border-b border-gray-800 text-gray-400 text-sm">
            <th className="px-4 py-3 text-left">Severity</th>
            <th className="px-4 py-3 text-left">Title</th>
            <th className="px-4 py-3 text-left">Status</th>
            <th className="px-4 py-3 text-left">Root Cause</th>
            <th className="px-4 py-3 text-left">Confidence</th>
          </tr></thead>
          <tbody>
            {loading ? <tr><td colSpan="5" className="px-4 py-8 text-center text-gray-500">Loading...</td></tr> :
             incidents.length === 0 ? <tr><td colSpan="5" className="px-4 py-8 text-center text-gray-500">No incidents yet. Trigger a scenario from the Simulator tab.</td></tr> :
             incidents.map(inc => (
              <tr key={inc.id} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                <td className="px-4 py-3"><SeverityBadge severity={inc.severity} /></td>
                <td className="px-4 py-3 text-white text-sm">{inc.title}</td>
                <td className="px-4 py-3"><StatusBadge status={inc.status} /></td>
                <td className="px-4 py-3 text-gray-400 text-sm max-w-xs truncate">{inc.probable_root_cause || '—'}</td>
                <td className="px-4 py-3 text-gray-400 text-sm">{inc.confidence ? `${(inc.confidence * 100).toFixed(0)}%` : '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

// ─── Simulator Page ───
function SimulatorPage() {
  const [scenarios, setScenarios] = useState([])
  const [triggering, setTriggering] = useState(null)
  const [result, setResult] = useState(null)

  useEffect(() => {
    fetch(`${API}/simulator/scenarios`, { headers: getHeaders() }).then(r => r.json()).then(d => setScenarios(d.scenarios || []))
  }, [])

  const trigger = async (id) => {
    setTriggering(id)
    setResult(null)
    try {
      const res = await fetch(`${API}/simulator/scenarios/${id}/trigger`, { method: 'POST', headers: getHeaders() })
      const data = await res.json()
      setResult(data)
    } catch (err) { setResult({ error: err.message }) }
    setTriggering(null)
  }

  return (
    <div>
      <h2 className="text-xl font-bold text-white mb-2">Failure Simulator</h2>
      <p className="text-gray-400 text-sm mb-6">Trigger realistic failure scenarios to test the AI investigation agent.</p>
      <div className="grid grid-cols-2 gap-4">
        {scenarios.map(s => (
          <div key={s.id} className="bg-gray-900 rounded-xl p-4 border border-gray-800">
            <div className="flex justify-between items-start mb-2">
              <h3 className="text-white font-medium">{s.name}</h3>
              <SeverityBadge severity={s.severity} />
            </div>
            <p className="text-gray-400 text-sm mb-3">{s.description}</p>
            <div className="flex gap-2">
              <span className="px-2 py-0.5 bg-gray-800 text-gray-300 rounded text-xs">{s.category}</span>
              <span className="px-2 py-0.5 bg-gray-800 text-gray-300 rounded text-xs">{s.service}</span>
            </div>
            <button onClick={() => trigger(s.id)} disabled={triggering === s.id}
              className="mt-3 w-full py-2 bg-red-600/20 text-red-400 rounded-lg text-sm font-medium hover:bg-red-600/30 disabled:opacity-50">
              {triggering === s.id ? 'Triggering...' : '⚡ Trigger Scenario'}
            </button>
          </div>
        ))}
      </div>
      {result && (
        <div className="mt-6 bg-gray-900 rounded-xl p-4 border border-green-800">
          <h3 className="text-green-400 font-medium mb-2">✅ Scenario Triggered</h3>
          <p className="text-gray-300 text-sm">Incident created: <strong>{result.incident_id}</strong></p>
          <p className="text-gray-400 text-sm mt-1">Telemetry generated. Go to Incidents to investigate with AI.</p>
        </div>
      )}
    </div>
  )
}

// ─── Incidents Page ───
function IncidentsPage() {
  const [incidents, setIncidents] = useState([])
  const [selected, setSelected] = useState(null)
  const [investigating, setInvestigating] = useState(false)
  const [investigationResult, setInvestigationResult] = useState(null)

  const loadIncidents = () => {
    fetch(`${API}/incidents?limit=20`, { headers: getHeaders() }).then(r => r.json()).then(d => setIncidents(d.incidents || []))
  }

  useEffect(loadIncidents, [])

  const investigate = async (id) => {
    setInvestigating(true)
    setInvestigationResult(null)
    try {
      const res = await fetch(`${API}/incidents/${id}/investigate`, { method: 'POST', headers: getHeaders() })
      const data = await res.json()
      setInvestigationResult(data)
      loadIncidents()
    } catch (err) { setInvestigationResult({ error: err.message }) }
    setInvestigating(false)
  }

  const approve = async (id) => {
    await fetch(`${API}/incidents/${id}/approve-remediation`, { method: 'POST', headers: { ...getHeaders(), 'Content-Type': 'application/json' }, body: JSON.stringify({ approved: true }) })
    loadIncidents()
  }

  return (
    <div className="flex gap-6">
      <div className="w-1/2">
        <h2 className="text-xl font-bold text-white mb-4">Incidents</h2>
        <div className="space-y-2">
          {incidents.map(inc => (
            <div key={inc.id} onClick={() => setSelected(inc)}
              className={`p-4 rounded-xl border cursor-pointer ${selected?.id === inc.id ? 'bg-blue-900/20 border-blue-700' : 'bg-gray-900 border-gray-800 hover:border-gray-700'}`}>
              <div className="flex justify-between items-start">
                <SeverityBadge severity={inc.severity} />
                <StatusBadge status={inc.status} />
              </div>
              <p className="text-white text-sm mt-2 font-medium">{inc.title}</p>
              {inc.probable_root_cause && <p className="text-gray-400 text-xs mt-1 truncate">🤖 {inc.probable_root_cause}</p>}
              {inc.status === 'detected' && (
                <button onClick={(e) => { e.stopPropagation(); investigate(inc.id) }} disabled={investigating}
                  className="mt-2 px-3 py-1 bg-blue-600/20 text-blue-400 rounded text-xs hover:bg-blue-600/30">
                  {investigating ? '🔄 Investigating...' : '🤖 Investigate with AI'}
                </button>
              )}
              {inc.status === 'awaiting_approval' && (
                <button onClick={(e) => { e.stopPropagation(); approve(inc.id) }}
                  className="mt-2 px-3 py-1 bg-green-600/20 text-green-400 rounded text-xs hover:bg-green-600/30">
                  ✅ Approve Remediation
                </button>
              )}
            </div>
          ))}
          {incidents.length === 0 && <p className="text-gray-500 text-center py-8">No incidents. Trigger a scenario from the Simulator.</p>}
        </div>
      </div>
      <div className="w-1/2">
        {investigationResult && !investigationResult.error ? (
          <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
            <h3 className="text-lg font-bold text-white mb-4">🤖 AI Investigation Report</h3>
            <div className="space-y-4">
              <div>
                <p className="text-gray-400 text-sm">Root Cause</p>
                <p className="text-white font-medium">{investigationResult.root_cause}</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Confidence</p>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-800 rounded-full h-2">
                    <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${(investigationResult.confidence || 0) * 100}%` }} />
                  </div>
                  <span className="text-white text-sm">{((investigationResult.confidence || 0) * 100).toFixed(0)}%</span>
                </div>
              </div>
              {investigationResult.recommended_remediation && (
                <div>
                  <p className="text-gray-400 text-sm">Recommended Remediation</p>
                  <p className="text-white">{investigationResult.recommended_remediation.description}</p>
                  <p className="text-gray-500 text-xs mt-1">Risk: {investigationResult.recommended_remediation.risk}</p>
                </div>
              )}
              <div>
                <p className="text-gray-400 text-sm mb-2">Investigation Trace</p>
                <div className="space-y-1">
                  {(investigationResult.investigation_trace || []).map((step, i) => (
                    <div key={i} className="flex items-center gap-2 text-xs text-gray-400">
                      <span className="text-blue-400">→</span>
                      <span>{step.action || step.phase}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : selected ? (
          <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
            <div className="flex justify-between items-start mb-4">
              <SeverityBadge severity={selected.severity} />
              <StatusBadge status={selected.status} />
            </div>
            <h3 className="text-lg font-bold text-white">{selected.title}</h3>
            {selected.symptoms?.length > 0 && (
              <div className="mt-4">
                <p className="text-gray-400 text-sm mb-2">Symptoms</p>
                <ul className="list-disc list-inside text-gray-300 text-sm">
                  {selected.symptoms.map((s, i) => <li key={i}>{s}</li>)}
                </ul>
              </div>
            )}
          </div>
        ) : (
          <div className="bg-gray-900 rounded-xl p-12 border border-gray-800 text-center">
            <p className="text-gray-500">Select an incident to view details</p>
          </div>
        )}
      </div>
    </div>
  )
}

// ─── Main App ───
export default function App() {
  const [user, setUser] = useState(null)
  const [page, setPage] = useState('dashboard')

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) setUser({ token })
  }, [])

  if (!user) return <Login onLogin={setUser} />

  const logout = () => { localStorage.removeItem('token'); setUser(null) }

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Header */}
      <header className="bg-gray-900 border-b border-gray-800 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🛡️</span>
          <div>
            <h1 className="text-lg font-bold text-white">Aegis</h1>
            <p className="text-xs text-gray-500">AI Incident Response Platform</p>
          </div>
        </div>
        <nav className="flex gap-1 bg-gray-800 rounded-lg p-1">
          {[['dashboard', '📊 Dashboard'], ['incidents', '🚨 Incidents'], ['simulator', '⚡ Simulator']].map(([id, label]) => (
            <button key={id} onClick={() => setPage(id)}
              className={`px-4 py-1.5 rounded-md text-sm font-medium transition ${page === id ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-white'}`}>
              {label}
            </button>
          ))}
        </nav>
        <button onClick={logout} className="text-sm text-gray-400 hover:text-white">Logout</button>
      </header>

      {/* Content */}
      <main className="p-6 max-w-7xl mx-auto">
        {page === 'dashboard' && <DashboardPage user={user} />}
        {page === 'incidents' && <IncidentsPage />}
        {page === 'simulator' && <SimulatorPage />}
      </main>
    </div>
  )
}
