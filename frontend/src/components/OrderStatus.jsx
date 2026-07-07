import { useState } from 'react'
import { binanceAPI } from '../api/binance'
import toast from 'react-hot-toast'

function statusColor(s) {
  if (!s) return 'var(--txt)'
  const m = s.toLowerCase()
  if (m === 'filled')   return 'var(--success)'
  if (m === 'canceled') return 'var(--txt2)'
  if (m === 'new')      return 'var(--info)'
  return 'var(--accent)'
}

export default function OrderStatus() {
  const [symbol,  setSymbol]  = useState('')
  const [orderId, setOrderId] = useState('')
  const [result,  setResult]  = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSearch = async e => {
    e.preventDefault()
    if (!symbol.trim()) return toast.error('Symbol is required')
    if (!orderId)        return toast.error('Order ID is required')
    setLoading(true); setResult(null)
    try {
      const res = await binanceAPI.getOrderStatus(symbol.trim().toUpperCase(), parseInt(orderId))
      setResult(res.data)
    } catch (err) { toast.error(err.message) }
    finally { setLoading(false) }
  }

  return (
    <div>
      <div className="mb-4">
        <div className="page-title">Order Status</div>
        <div className="page-subtitle">Look up any order by symbol and ID</div>
      </div>

      <div className="form-card">
        <form onSubmit={handleSearch}>
          <div className="row g-3 mb-4">
            <div className="col-6">
              <label className="form-label">Symbol</label>
              <input className="form-control" value={symbol} onChange={e => setSymbol(e.target.value.toUpperCase())} placeholder="BTCUSDT" required />
            </div>
            <div className="col-6">
              <label className="form-label">Order ID</label>
              <input className="form-control" type="number" value={orderId} onChange={e => setOrderId(e.target.value)} placeholder="e.g. 123456789" required />
            </div>
          </div>
          <button type="submit" className="btn-accent btn w-100" disabled={loading}>
            {loading ? <><span className="spinner-border spinner-border-sm me-2" />Searching…</> : <><i className="bi bi-search me-1" />Check Status</>}
          </button>
        </form>

        {result && (
          <div className="result-card mt-3">
            <div className="d-flex align-items-center justify-content-between mb-2">
              <strong>Order #{result.order_id}</strong>
              <span className="status-badge" style={{ color: statusColor(result.status), background: 'rgba(255,255,255,.05)' }}>
                {result.status}
              </span>
            </div>
            {[
              ['Symbol',        result.symbol],
              ['Side',          result.side],
              ['Type',          result.type],
              ['Price',         result.price],
              ['Original Qty',  result.orig_qty],
              ['Executed Qty',  result.executed_qty],
              ['Avg Price',     result.avg_price],
              ['Time in Force', result.time_in_force],
            ].map(([k, v]) => (
              <div className="result-row" key={k}>
                <span>{k}</span>
                <span style={{ color: k === 'Side' ? (v === 'BUY' ? 'var(--success)' : 'var(--danger)') : 'var(--txt)' }}>
                  {v ?? '—'}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
