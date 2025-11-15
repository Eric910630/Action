import apiClient from './client'

export interface DeepSeekApiKeyResponse {
  configured: boolean
  masked_key?: string
}

export interface DeepSeekApiKeyRequest {
  api_key: string
}

export const settingsApi = {
  // 获取DeepSeek API Key配置状态
  getDeepSeekApiKey() {
    return apiClient.get<DeepSeekApiKeyResponse>('/settings/deepseek-api-key')
  },

  // 设置DeepSeek API Key
  setDeepSeekApiKey(data: DeepSeekApiKeyRequest) {
    return apiClient.post('/settings/deepseek-api-key', data)
  }
}

