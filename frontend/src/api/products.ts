import apiClient from './client'

export interface Product {
  id: string
  name: string
  brand?: string
  category: string
  live_room_id: string
  price: number
  selling_points?: string[]
  description?: string
  hand_card?: string
  live_date?: string
  created_at: string
}

export interface ProductListResponse {
  total: number
  items: Product[]
  limit: number
  offset: number
}

export interface ProductCreate {
  name: string
  brand?: string
  category: string
  live_room_id: string
  price: number
  selling_points?: string[]
  description?: string
  hand_card?: string
  live_date: string
}

export const productsApi = {
  // 获取商品列表
  getProducts(params?: {
    live_room_id?: string
    live_date?: string
    limit?: number
    offset?: number
  }) {
    return apiClient.get<ProductListResponse>('/products', { params })
  },

  // 获取商品详情
  getProductDetail(id: string) {
    return apiClient.get<Product>(`/products/${id}`)
  },

  // 创建商品
  createProduct(data: ProductCreate) {
    return apiClient.post('/products', data)
  },

  // 更新商品
  updateProduct(id: string, data: Partial<ProductCreate>) {
    return apiClient.put(`/products/${id}`, data)
  }
}

