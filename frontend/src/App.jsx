import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Navbar from './components/Navbar'
import Dashboard from './components/Dashboard'
import MarketOrder from './components/MarketOrder'
import LimitOrder from './components/LimitOrder'
import Account from './components/Account'
import Positions from './components/Positions'
import OpenOrders from './components/OpenOrders'
import OrderStatus from './components/OrderStatus'

export default function App() {
  return (
    <BrowserRouter>
      <div className="d-flex" style={{ minHeight: '100vh' }}>
        <Navbar />
        <div className="main-wrap w-100">
          <div className="page-content">
            <Routes>
              <Route path="/"             element={<Dashboard />} />
              <Route path="/market-order" element={<MarketOrder />} />
              <Route path="/limit-order"  element={<LimitOrder />} />
              <Route path="/account"      element={<Account />} />
              <Route path="/positions"    element={<Positions />} />
              <Route path="/open-orders"  element={<OpenOrders />} />
              <Route path="/order-status" element={<OrderStatus />} />
            </Routes>
          </div>
        </div>
      </div>
      <Toaster
        position="top-right"
        toastOptions={{
          style: { background: '#1e2430', color: '#e6edf3', border: '1px solid #30363d' },
          success: { iconTheme: { primary: '#3fb950', secondary: '#1e2430' } },
          error:   { iconTheme: { primary: '#f85149', secondary: '#1e2430' } },
        }}
      />
    </BrowserRouter>
  )
}
