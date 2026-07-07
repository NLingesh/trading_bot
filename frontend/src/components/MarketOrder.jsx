import { useState } from 'react'
import toast from 'react-hot-toast'
import { binanceAPI } from '../api/binance'

export default function MarketOrder() {
  const [symbol,   setSymbol]   = useState('BTCUSDT')
  const [side,     setSide]     = useState('BUY')
  const [qty,      setQty]      = useState('')
  const [loading,  setLoading]  = useState(false)
  const [result,   setResult]   = useState(null)

  const handleSubmit = async e => {
    e.preventDefault()
    if (!symbol.trim()) return toast.error('Symbol is required')
    if (!qty || parseFloat(qty) <= 0) return toast.error('Quantity must be > 0')

    setLoading(true); setResult(null)
    try {
      const res = await binanceAPI.placeMarket({ symbol: symbol.trim().toUpperCase(), side, quantity: parseFloat(qty) })
      setResult(res.data)
      toast.success(`Market ${side} order placed!`)
    } catch (err) {
      toast.error(err.message)
    } finally { setLoading(false) }
  }

  return (
    <div>
      <div className="mb-4">
        <div className="page-title">Market Order</div>
        <div className="page-subtitle">Execute instantly at the current market price</div>
      </div>

      <div className="form-card">
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label className="form-label">Symbol</label>
            <input className="form-control" value={symbol} onChange={e => setSymbol(e.target.value.toUpperCase())} placeholder="BTCUSDT" required />
          </div>

          <div className="mb-3">
            <label className="form-label">Side</label>
            <div className="d-flex gap-2">
              <button type="button" className={`btn-side buy w-100${side === 'BUY' ? ' active' : ''}`} onClick={() => setSide('BUY')}>
                <i className="bi bi-arrow-up-circle me-1" /> BUY
              </button>
              <button type="button" className={`btn-side sell w-100${side === 'SELL' ? ' active' : ''}`} onClick={() => setSide('SELL')}>
                <i className="bi bi-arrow-down-circle me-1" /> SELL
              </button>
            </div>
          </div>

          <div className="mb-4">
            <label className="form-label">Quantity</label>
            <input className="form-control" type="number" step="any" min="0" value={qty} onChange={e => setQty(e.target.value)} placeholder="e.g. 0.001" required />
          </div>

          <button type="submit" className="btn-accent btn w-100" disabled={loading}>
            {loading ? <><span className="spinner-border spinner-border-sm me-2" />Placing…</> : <><i className="bi bi-lightning-charge-fill me-1" />Place Market Order</>}
          </button>
        </form>

        {result && (
          <div className="result-card mt-3">
            <div className="d-flex align-items-center gap-2 mb-2">
              <i className="bi bi-check-circle-fill" style={{ color: 'var(--success)' }} />
              <strong>Order Placed</strong>
            </div>
            {[['Order ID', result.order_id], ['Symbol', result.symbol], ['Side', result.side],
              ['Type', result.type], ['Status', result.status], ['Qty', result.orig_qty]].map(([k, v]) => (
              <div className="result-row" key={k}><span>{k}</span><span>{v ?? '—'}</span></div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
