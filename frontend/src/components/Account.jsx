import { useEffect, useState } from 'react'
import { binanceAPI } from '../api/binance'

function InfoCard({ label, value, color }) {
  return (
    <div className="dash-card">
      <div className="card-label">{label}</div>
      <div className="card-value mt-1" style={{ fontSize: '1.15rem', color: color || 'var(--txt)' }}>
        {value ?? '—'}
      </div>
    </div>
  )
}

export default function Account() {
  const [data, setData]     = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]   = useState(null)

  useEffect(() => {
    binanceAPI.getAccount()
      .then(r => setData(r.data))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const fmt = n => n != null ? parseFloat(n).toFixed(4) : '—'
  const pnl = data ? parseFloat(data.totalUnrealizedProfit || 0) : 0

  return (
    <div>
      <div className="mb-4">
        <div className="page-title">Account</div>
        <div className="page-subtitle">Futures wallet overview</div>
      </div>

      {loading && <div className="spinner-wrap"><div className="spinner-border" /></div>}
      {error   && <div className="dash-card" style={{ color: 'var(--danger)' }}><i className="bi bi-exclamation-triangle me-2" />{error}</div>}

      {data && (
        <>
          <div className="row g-3 mb-4">
            <div className="col-6 col-md-3"><InfoCard label="Wallet Balance"    value={`${fmt(data.totalWalletBalance)} USDT`} /></div>
            <div className="col-6 col-md-3"><InfoCard label="Available Balance" value={`${fmt(data.availableBalance)} USDT`}    color="var(--info)" /></div>
            <div className="col-6 col-md-3"><InfoCard label="Unrealized PnL"    value={`${pnl >= 0 ? '+' : ''}${fmt(pnl)} USDT`} color={pnl >= 0 ? 'var(--success)' : 'var(--danger)'} /></div>
            <div className="col-6 col-md-3"><InfoCard label="Margin Balance"    value={`${fmt(data.totalMarginBalance)} USDT`}   color="var(--accent)" /></div>
          </div>

          <div className="row g-3 mb-4">
            <div className="col-6 col-md-3"><InfoCard label="Initial Margin"   value={`${fmt(data.totalInitialMargin)} USDT`} /></div>
            <div className="col-6 col-md-3"><InfoCard label="Maint. Margin"    value={`${fmt(data.totalMaintMargin)} USDT`} /></div>
            <div className="col-6 col-md-3"><InfoCard label="Cross Wallet Bal" value={`${fmt(data.totalCrossWalletBalance)} USDT`} /></div>
            <div className="col-6 col-md-3"><InfoCard label="Max Withdraw"     value={`${fmt(data.maxWithdrawAmount)} USDT`} /></div>
          </div>

          <div className="row g-3">
            <div className="col-6 col-md-3">
              <InfoCard label="Can Trade"   value={data.canTrade   ? '✅ Yes' : '❌ No'} color={data.canTrade ? 'var(--success)' : 'var(--danger)'} />
            </div>
            <div className="col-6 col-md-3">
              <InfoCard label="Can Deposit" value={data.canDeposit ? '✅ Yes' : '❌ No'} color={data.canDeposit ? 'var(--success)' : 'var(--danger)'} />
            </div>
            <div className="col-6 col-md-3">
              <InfoCard label="Fee Tier"    value={data.feeTier ?? '—'} />
            </div>
            <div className="col-6 col-md-3">
              <InfoCard label="Pos. Count"  value={data.positions?.filter(p => parseFloat(p.positionAmt) !== 0).length ?? 0} />
            </div>
          </div>
        </>
      )}
    </div>
  )
}
