import { useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import { binanceAPI } from '../api/binance'

function statusClass(s) {
  if (!s) return ''
  const m = s.toLowerCase()
  if (m === 'new')                return 'new'
  if (m === 'filled')             return 'filled'
  if (m === 'canceled')           return 'canceled'
  if (m.includes('partial'))      return 'partial'
  return ''
}

export default function OpenOrders() {
  const [rows, setRows]     = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError]   = useState(null)
  const [symbol, setSymbol] = useState('')
  const [canceling, setCanceling] = useState(null)

  const load = (sym = '') => {
    setLoading(true); setError(null)
    binanceAPI.getOpenOrders(sym || undefined)
      .then(r => setRows(r.data))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const handleCancel = async (sym, id) => {
    if (!window.confirm(`Cancel order #${id} for ${sym}?`)) return
    setCanceling(id)
    try {
      await binanceAPI.cancelOrder(sym, id)
      toast.success(`Order #${id} cancelled`)
      load(symbol)
    } catch (err) {
      toast.error(err.message)
    } finally { setCanceling(null) }
  }

  const handleFilter = e => { e.preventDefault(); load(symbol) }

  return (
    <div>
      <div className="d-flex align-items-center justify-content-between mb-4 flex-wrap gap-2">
        <div>
          <div className="page-title">Open Orders</div>
          <div className="page-subtitle">{rows.length} open order{rows.length !== 1 ? 's' : ''}</div>
        </div>
        <form className="d-flex gap-2" onSubmit={handleFilter}>
          <input
            className="form-control"
            style={{ width: 140 }}
            placeholder="Filter symbol"
            value={symbol}
            onChange={e => setSymbol(e.target.value.toUpperCase())}
          />
          <button type="submit" className="btn-accent btn" style={{ padding: '.4rem .9rem', fontSize: '.85rem' }}>
            <i className="bi bi-funnel" />
          </button>
          <button type="button" className="btn btn-outline-secondary" style={{ padding: '.4rem .9rem', fontSize: '.85rem', borderColor: 'var(--border)', color: 'var(--txt2)' }} onClick={() => { setSymbol(''); load('') }}>
            Clear
          </button>
        </form>
      </div>

      {loading && <div className="spinner-wrap"><div className="spinner-border" /></div>}
      {error   && <div className="dash-card" style={{ color: 'var(--danger)' }}><i className="bi bi-exclamation-triangle me-2" />{error}</div>}

      {!loading && !error && (
        rows.length === 0
          ? <div className="empty-state"><i className="bi bi-list-ul" /><div>No open orders</div></div>
          : (
            <div className="table-wrap">
              <table className="dark-table">
                <thead>
                  <tr>
                    {['Order ID','Symbol','Side','Type','Price','Qty','Filled','Status','Time','Action'].map(h => (
                      <th key={h}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.map(o => (
                    <tr key={o.orderId}>
                      <td style={{ color: 'var(--txt2)', fontSize: '.8rem' }}>{o.orderId}</td>
                      <td><strong style={{ color: 'var(--accent)' }}>{o.symbol}</strong></td>
                      <td>
                        <span style={{ color: o.side === 'BUY' ? 'var(--success)' : 'var(--danger)', fontWeight: 700 }}>
                          {o.side}
                        </span>
                      </td>
                      <td>{o.type}</td>
                      <td>{o.price}</td>
                      <td>{o.origQty}</td>
                      <td>{o.executedQty}</td>
                      <td><span className={`status-badge ${statusClass(o.status)}`}>{o.status}</span></td>
                      <td style={{ fontSize: '.75rem', color: 'var(--txt2)' }}>
                        {o.time ? new Date(o.time).toLocaleString() : '—'}
                      </td>
                      <td>
                        <button
                          className="btn btn-sm"
                          style={{ background: 'rgba(248,81,73,.15)', color: 'var(--danger)', border: '1px solid rgba(248,81,73,.3)', borderRadius: 6 }}
                          disabled={canceling === o.orderId}
                          onClick={() => handleCancel(o.symbol, o.orderId)}
                        >
                          {canceling === o.orderId
                            ? <span className="spinner-border spinner-border-sm" />
                            : <><i className="bi bi-x-circle me-1" />Cancel</>
                          }
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
      )}
    </div>
  )
}
