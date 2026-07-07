import { useEffect, useState, useCallback } from 'react'
import { binanceAPI } from '../api/binance'

function StatCard({ icon, label, value, sub, color = 'var(--txt)' }) {
  return (
    <div className="dash-card h-100">
      <div className="d-flex align-items-center gap-2 mb-2">
        <i className={`bi ${icon}`} style={{ color: 'var(--accent)', fontSize: '1.1rem' }} />
        <span className="card-label mb-0">{label}</span>
      </div>
      <div className="card-value" style={{ color, fontSize: '1.3rem' }}>{value}</div>
      {sub && <div style={{ fontSize: '.75rem', color: 'var(--txt2)', marginTop: '.25rem' }}>{sub}</div>}
    </div>
  )
}

export default function Dashboard() {
  const [status, setStatus]   = useState(null)   // 'online'|'offline'
  const [time, setTime]       = useState(null)
  const [account, setAccount] = useState(null)
  const [loading, setLoading] = useState(true)
  const [lastRefresh, setLastRefresh] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [pingRes, timeRes, accRes] = await Promise.allSettled([
        binanceAPI.ping(),
        binanceAPI.serverTime(),
        binanceAPI.getAccount(),
      ])
      setStatus(pingRes.status === 'fulfilled' ? 'online' : 'offline')
      if (timeRes.status === 'fulfilled') setTime(timeRes.value.data.serverTime)
      if (accRes.status  === 'fulfilled') setAccount(accRes.value.data)
    } catch {
      setStatus('offline')
    } finally {
      setLoading(false)
      setLastRefresh(new Date())
    }
  }, [])

  useEffect(() => { load(); const t = setInterval(load, 30000); return () => clearInterval(t) }, [load])

  const fmt    = n  => n != null ? parseFloat(n).toFixed(2) : '—'
  const fmtTs  = ts => ts ? new Date(ts).toUTCString().replace(' GMT', ' UTC') : '—'
  const pnl    = account ? parseFloat(account.totalUnrealizedProfit || 0) : null

  return (
    <div>
      {/* Header */}
      <div className="d-flex align-items-center justify-content-between mb-4">
        <div>
          <div className="page-title">Dashboard</div>
          <div className="page-subtitle">Binance Futures Testnet — live overview</div>
        </div>
        <button className="btn-accent btn" onClick={load} disabled={loading} style={{ padding: '.4rem 1rem', fontSize: '.85rem' }}>
          <i className={`bi bi-arrow-clockwise me-1 ${loading ? 'spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Status row */}
      <div className="row g-3 mb-3">
        <div className="col-6 col-md-3">
          <div className="dash-card h-100">
            <div className="card-label">API Status</div>
            {status === null
              ? <div className="spinner-border spinner-border-sm mt-1" />
              : <div className="d-flex align-items-center gap-2 mt-1">
                  <span className={`dot ${status}`} />
                  <span style={{ fontWeight: 700, color: status === 'online' ? 'var(--success)' : 'var(--danger)' }}>
                    {status === 'online' ? 'Online' : 'Offline'}
                  </span>
                </div>
            }
          </div>
        </div>
        <div className="col-6 col-md-3">
          <StatCard icon="bi-clock" label="Server Time" value={time ? new Date(time).toLocaleTimeString() : '—'} sub={fmtTs(time)} />
        </div>
        <div className="col-6 col-md-3">
          <StatCard icon="bi-activity" label="Last Refresh" value={lastRefresh ? lastRefresh.toLocaleTimeString() : '—'} sub="Auto every 30s" />
        </div>
        <div className="col-6 col-md-3">
          <div className="dash-card h-100">
            <div className="card-label">Network</div>
            <div style={{ fontSize: '.8rem', marginTop: '.5rem' }}>
              <div style={{ color: 'var(--txt2)' }}>Testnet REST API</div>
              <div style={{ color: 'var(--info)', fontWeight: 600, fontSize: '.75rem', marginTop: '.2rem' }}>
                testnet.binancefuture.com
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Balance row */}
      {loading && !account
        ? <div className="spinner-wrap"><div className="spinner-border" /></div>
        : account
          ? (
            <div className="row g-3">
              <div className="col-6 col-md-3">
                <StatCard icon="bi-wallet2" label="Wallet Balance" value={`${fmt(account.totalWalletBalance)} USDT`} color="var(--txt)" />
              </div>
              <div className="col-6 col-md-3">
                <StatCard icon="bi-cash-stack" label="Available Balance" value={`${fmt(account.availableBalance)} USDT`} color="var(--info)" />
              </div>
              <div className="col-6 col-md-3">
                <StatCard
                  icon="bi-graph-up-arrow"
                  label="Unrealized PnL"
                  value={`${pnl >= 0 ? '+' : ''}${fmt(pnl)} USDT`}
                  color={pnl >= 0 ? 'var(--success)' : 'var(--danger)'}
                />
              </div>
              <div className="col-6 col-md-3">
                <StatCard icon="bi-shield" label="Margin Balance" value={`${fmt(account.totalMarginBalance)} USDT`} color="var(--accent)" />
              </div>
            </div>
          )
          : (
            <div className="dash-card text-center py-4" style={{ color: 'var(--txt2)' }}>
              <i className="bi bi-exclamation-triangle" style={{ fontSize: '2rem', color: 'var(--warning)' }} />
              <div className="mt-2">Could not load account data. Check your API credentials in <code>.env</code>.</div>
            </div>
          )
      }
    </div>
  )
}
