import axios, { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios'

const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    // 对于blob响应（如PDF导出），直接返回response对象，让调用方处理response.data
    if (response.config.responseType === 'blob') {
      return response
    }
    // 对于JSON响应，返回data
    return response.data
  },
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    console.error('API Error:', message)
    return Promise.reject(error)
  }
)

// 类型包装：由于响应拦截器返回response.data，所以实际返回类型是T而不是AxiosResponse<T>
// 这里创建一个类型包装器来正确声明返回类型
interface ApiClient {
  get<T = any>(url: string, config?: any): Promise<T>
  post<T = any>(url: string, data?: any, config?: any): Promise<T>
  put<T = any>(url: string, data?: any, config?: any): Promise<T>
  delete<T = any>(url: string, config?: any): Promise<T>
}

// 将apiClient转换为正确的类型
const typedApiClient = apiClient as unknown as ApiClient

export default typedApiClient

