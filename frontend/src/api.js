import axios from 'axios'
const apiBase=import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL.replace(/\/$/, '')}/api`
  : 'http://localhost:8002/api'
const api=axios.create({baseURL:apiBase})
api.interceptors.request.use(config=>{const token=localStorage.getItem('tracker_token');if(token)config.headers.Authorization=`Bearer ${token}`;return config})
export default api
