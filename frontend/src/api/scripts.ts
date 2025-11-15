import apiClient from './client'

export interface Script {
  id: string
  hotspot_id?: string
  product_id: string
  analysis_report_id?: string
  video_info?: any
  script_content?: string
  shot_list?: any[]
  production_notes?: any
  tags?: any
  status?: string
  created_at: string
}

export interface ScriptListResponse {
  total: number
  items: Script[]
  limit: number
  offset: number
}

export interface GenerateScriptRequest {
  hotspot_id: string
  product_id: string
  analysis_report_id?: string
  duration?: number
  adjustment_feedback?: string
  script_count?: number  // 生成脚本数量，默认5个
}

export interface RegenerateScriptRequest {
  adjustment_feedback: string
}

export const scriptsApi = {
  // 获取脚本列表
  getScripts(params?: {
    product_id?: string
    status?: string
    limit?: number
    offset?: number
  }) {
    return apiClient.get<ScriptListResponse>('/scripts', { params })
  },

  // 获取脚本详情
  getScriptDetail(id: string) {
    return apiClient.get<Script>(`/scripts/${id}`)
  },

  // 生成脚本
  generateScript(data: GenerateScriptRequest) {
    return apiClient.post('/scripts/generate', data)
  },

  // 更新脚本
  updateScript(id: string, data: Partial<Script>) {
    return apiClient.put(`/scripts/${id}`, data)
  },

  // 审核脚本
  reviewScript(id: string, action: 'approve' | 'reject', comment?: string) {
    return apiClient.post(`/scripts/${id}/review`, { action, comment })
  },

  // 获取优化建议
  optimizeScript(id: string) {
    return apiClient.post(`/scripts/${id}/optimize`)
  },

  // 重新生成脚本
  regenerateScript(id: string, data: RegenerateScriptRequest) {
    return apiClient.post(`/scripts/${id}/regenerate`, data)
  }
}

