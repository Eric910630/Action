import apiClient from './client'

export interface AnalysisReport {
  id: string
  video_url: string
  video_info?: any
  basic_info?: any
  shot_table?: any[]
  golden_3s?: any
  highlights?: any[]
  viral_formula?: any
  keywords?: any
  production_tips?: any
  techniques?: any[]
  created_at: string
}

export interface AnalysisListResponse {
  total: number
  items: AnalysisReport[]
  limit: number
  offset: number
}

export const analysisApi = {
  // 获取报告列表
  getReports(params?: {
    video_url?: string
    limit?: number
    offset?: number
  }) {
    return apiClient.get<AnalysisListResponse>('/analysis/reports', { params })
  },

  // 获取报告详情
  getReportDetail(id: string) {
    return apiClient.get<AnalysisReport>(`/analysis/reports/${id}`)
  },

  // 分析视频
  analyzeVideo(video_url: string, options?: any) {
    return apiClient.post('/analysis/analyze', {
      video_url,
      options
    })
  },

  // 批量分析
  batchAnalyze(video_urls: string[]) {
    return apiClient.post('/analysis/batch', video_urls)
  }
}

