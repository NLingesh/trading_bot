import axios from 'axios'

const API = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

API.interceptors.response.use(
  r => r,
  err => {
    const d = err.response?.data
    const msg = d?.message || d?.detail || err.message || 'Unknown error'
    return Promise.reject(new Error(msg))
  }
)

export const binanceAPI = {
  ping:            ()             => API.get('/ping'),
  serverTime:      ()             => API.get('/server-time'),
  exchangeInfo:    (symbol)       => API.get('/exchange-info', { params: symbol ? { symbol } : {} }),
  getAccount:      ()             => API.get('/account'),
  getPositions:    (symbol)       => API.get('/positions',    { params: symbol ? { symbol } : {} }),
  getOpenOrders:   (symbol)       => API.get('/open-orders',  { params: symbol ? { symbol } : {} }),
  getOrderStatus:  (sym, id)      => API.get(`/order-status/${sym}/${id}`),
  placeMarket:     (data)         => API.post('/order/market', data),
  placeLimit:      (data)         => API.post('/order/limit',  data),
  cancelOrder:     (sym, id)      => API.delete(`/cancel/${sym}/${id}`),
}
