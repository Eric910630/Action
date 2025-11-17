import apiClient from './client'

export interface Feedback {
  id: string
  user_name?: string
  content: string
  feedback_type?: string
  tags?: string[]
  status?: string
  response?: string
  created_at: string
  updated_at: string
}

export interface FeedbackListResponse {
  total: number
  items: Feedback[]
  limit: number
  offset: number
}

export interface FeedbackCreateRequest {
  user_name?: string
  content: string
  feedback_type?: string
  tags?: string[]
}

export interface FeedbackUpdateRequest {
  status?: string
  response?: string
}

export const feedbackApi = {
  // 获取反馈列表
  getFeedbacks(params?: {
    status?: string
    feedback_type?: string
    limit?: number
    offset?: number
  }) {
    return apiClient.get<FeedbackListResponse>('/feedback', { params })
  },

  // 创建反馈
  createFeedback(data: FeedbackCreateRequest) {
    return apiClient.post('/feedback', data)
  },

  // 更新反馈
  updateFeedback(id: string, data: FeedbackUpdateRequest) {
    return apiClient.put(`/feedback/${id}`, data)
  },

  // 删除反馈
  deleteFeedback(id: string) {
    return apiClient.delete(`/feedback/${id}`)
  }
}

