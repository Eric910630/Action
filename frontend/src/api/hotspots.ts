import apiClient from './client'

export interface Hotspot {
  id: string
  title: string
  url: string
  platform: string
  tags?: string[]
  heat_score?: number
  match_score?: number
  publish_time?: string
  created_at: string
}

export interface HotspotListResponse {
  total: number
  items: Hotspot[]
  limit: number
  offset: number
}

export const hotspotsApi = {
  // 获取热点列表
  getHotspots(params?: {
    platform?: string
    live_room_id?: string
    start_date?: string
    end_date?: string
    limit?: number
    offset?: number
  }) {
    return apiClient.get<HotspotListResponse>('/hotspots', { params })
  },

  // 获取热点详情
  getHotspotDetail(id: string) {
    return apiClient.get<Hotspot>(`/hotspots/${id}`)
  },

  // 触发热点抓取
  // 如果不传platform参数，后端会抓取多个平台（douyin, zhihu, weibo, bilibili, xiaohongshu）
  fetchHotspots(platform?: string) {
    const params: any = {}
    if (platform) {
      params.platform = platform
    }
    return apiClient.post('/hotspots/fetch', null, {
      params
    })
  },

  // 筛选热点
  filterHotspots(keywords: string[], live_room_id?: string) {
    return apiClient.post('/hotspots/filter', {
      keywords,
      live_room_id
    })
  },

  // 获取可视化数据（气泡图）
  getVisualization(live_room_id?: string) {
    // 确保参数正确传递：如果 live_room_id 存在，则传递；否则不传递参数（获取所有数据）
    const params: any = {}
    if (live_room_id) {
      params.live_room_id = live_room_id
    }
    console.log('API调用 getVisualization，params:', params)
    return apiClient.get('/hotspots/visualization', { params })
  }
}

