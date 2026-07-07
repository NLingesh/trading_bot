import { useEffect, useState } from 'react'
import { binanceAPI } from '../api/binance'

export default function Positions() {
  const [rows, setRows]         = useState([])
  const [loading, setLoading]   = useState(true)
  const [error, setError]       = useState(null)
  const [showAll, setShowAll]   = useState(false)

  useEffect(() => {
    binanceAPI.getPositions()
      .then(r => setRows(r.data))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const active = showAll ? rows : rows.filter(r => parseFloat(r.positionAmt) !== 0)
  const fmt = n => n != null ? parseFloat(n).toFixed(4) : '—'

  return (
    <div>
      <div className="d-flex align-items-center justify-content-between mb-4">
        <div>
          <div className="page-title">Positions</div>
          <div className="page-subtitle">{active.length} position{active.length !== 1 ? 's' : ''}</div>
        </div>
        <label className="d-flex align-items-center gap-2" style={{ cursor: 'pointer', fontSize: '.85rem', color: 'var(--txt2)' }}>
          <input type="checkbox" checked={showAll} onChange={e => setShowAll(e.target.checked)} />
          Show all (inc. zero)
        </label>
      </div>

      {loading && <div className="spinner-wrap"><div className="spinner-border" /></div>}
      {error   && <div className="dash-card" style={{ color: 'var(--danger)' }}><i className="bi bi-exclamation-triangle me-2" />{error}</div>}

      {!loading && !error && (
        active.length === 0
          ? <div className="empty-state"><i className="bi bi-bar-chart-line" /><div>No active positions</div></div>
          : (
            <div className="table-wrap">
              <table className="dark-table">
                <thead>
                  <tr>
                    {['Symbol','Side','Amount','Entry Price','Mark Price','Liq. Price','Unreal. PnL','Leverage','Margin Type'].map(h => (
                      <th key={h}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {active.map((p, i) => {
                    const pnl = parseFloat(p.unRealizedProfit || 0)
                    const amt = parseFloat(p.positionAmt || 0)
                    return (
                      <tr key={i}>
                        <td><strong style={{ color: 'var(--accent)' }}>{p.symbol}</strong></td>
                        <td>
                          <span className={`status-badge ${amt >= 0 ? 'new' : 'canceled'}`}>
                            {amt >= 0 ? 'LONG' : 'SHORT'}
                          </span>
                        </td>
                        <td>{fmt(p.positionAmt)}</td>
                        <td>{fmt(p.entryPrice)}</td>
                        <td>{fmt(p.markPrice)}</td>
                        <td>{fmt(p.liquidationPrice)}</td>
                        <td style={{ color: pnl >= 0 ? 'var(--success)' : 'var(--danger)', fontWeight: 600 }}>
                          {pnl >= 0 ? '+' : ''}{fmt(pnl)}
                        </td>
                        <td>{p.leverage}×</td>
                        <td style={{ textTransform: 'capitalize' }}>{p.marginType}</td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )
      )}
    </div>
  )
}
