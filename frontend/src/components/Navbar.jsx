import { NavLink } from 'react-router-dom'

const links = [
  { to: '/',             icon: 'bi-grid-1x2-fill',    label: 'Dashboard' },
  { to: '/market-order', icon: 'bi-lightning-charge-fill', label: 'Market Order' },
  { to: '/limit-order',  icon: 'bi-sliders',           label: 'Limit Order' },
  { to: '/account',      icon: 'bi-wallet2',           label: 'Account' },
  { to: '/positions',    icon: 'bi-bar-chart-line-fill', label: 'Positions' },
  { to: '/open-orders',  icon: 'bi-list-ul',           label: 'Open Orders' },
  { to: '/order-status', icon: 'bi-search',            label: 'Order Status' },
]

export default function Navbar() {
  return (
    <aside className="sidebar">
      <NavLink to="/" className="sidebar-brand">
        <i className="bi bi-currency-bitcoin" />
        TradingBot
      </NavLink>

      <div style={{ padding: '1rem 0', flex: 1 }}>
        <div className="sidebar-label">Navigation</div>
        {links.map(l => (
          <NavLink
            key={l.to}
            to={l.to}
            end={l.to === '/'}
            className={({ isActive }) => `nav-link-item${isActive ? ' active' : ''}`}
          >
            <i className={`bi ${l.icon}`} />
            {l.label}
          </NavLink>
        ))}
      </div>

      <div style={{ padding: '1rem 1.25rem', borderTop: '1px solid var(--border)' }}>
        <div style={{ fontSize: '.7rem', color: 'var(--txt2)' }}>
          <i className="bi bi-shield-check me-1" style={{ color: 'var(--accent)' }} />
          Binance Futures Testnet
        </div>
      </div>
    </aside>
  )
}
