import { useState } from 'react'
import toast from 'react-hot-toast'
import { binanceAPI } from '../api/binance'

export default function LimitOrder() {
  const [symbol, setSymbol] = useState('BTCUSDT')
  const [side,   setSide]   = useState('BUY')
  const [qty,    setQty]    = useState('')
  const [price,  setPrice]  = useState('')
  const [tif,    setTif]    = useState('GTC')
  const [loading, setLoading] = useState(false)
  const [result,  setResult]  = useState(null)

  const handleSubmit = async e => {
    e.preventDefault()
    if (!symbol.trim()) return toast.error('Symbol is required')
    if (!qty   || parseFloat(qty)   <= 0) return toast.error('Quantity must be > 0')
    if (!price || parseFloat(price) <= 0) return toast.error('Price must be > 0')

    setLoading(true); setResult(null)
    try {
      const res = await binanceAPI.placeLimit({
        symbol: symbol.trim().toUpperCase(), side,
        quantity: parseFloat(qty), price: parseFloat(price), time_in_force: tif,
      })
      setResult(res.data)
      toast.success(`Limit ${side} order placed!`)
    } catch (err) {
      toast.error(err.message)
    } finally { setLoading(false) }
  }

  return (
    <div>
      <div className="mb-4">
        <div className="page-title">Limit Order</div>
        <div className="page-subtitle">Execute at your specified price or better</div>
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

          <div className="row g-3 mb-3">
            <div className="col-6">
              <label className="form-label">Quantity</label>
              <input className="form-control" type="number" step="any" min="0" value={qty} onChange={e => setQty(e.target.value)} placeholder="0.001" required />
            </div>
            <div className="col-6">
              <label className="form-label">Price (USDT)</label>
              <input className="form-control" type="number" step="any" min="0" value={price} onChange={e => setPrice(e.target.value)} placeholder="50000" required />
            </div>
          </div>

          <div className="mb-4">
            <label className="form-label">Time in Force</label>
            <select className="form-select" value={tif} onChange={e => setTif(e.target.value)}>
              <option value="GTC">GTC — Good Till Cancel</option>
              <option value="IOC">IOC — Immediate or Cancel</option>
              <option value="FOK">FOK — Fill or Kill</option>
            </select>
          </div>

          <button type="submit" className="btn-accent btn w-100" disabled={loading}>
            {loading ? <><span className="spinner-border spinner-border-sm me-2" />Placing…</> : <><i className="bi bi-sliders me-1" />Place Limit Order</>}
          </button>
        </form>

        {result && (
          <div className="result-card mt-3">
            <div className="d-flex align-items-center gap-2 mb-2">
              <i className="bi bi-check-circle-fill" style={{ color: 'var(--success)' }} />
              <strong>Order Placed</strong>
            </div>
            {[['Order ID', result.order_id], ['Symbol', result.symbol], ['Side', result.side],
              ['Type', result.type], ['Status', result.status], ['Price', result.price],
              ['Qty', result.orig_qty], ['TIF', result.time_in_force]].map(([k, v]) => (
              <div className="result-row" key={k}><span>{k}</span><span>{v ?? '—'}</span></div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
