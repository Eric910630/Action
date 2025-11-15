import apiClient from './client'

export interface LiveRoom {
  id: string
  name: string
  category: string
  keywords?: string[]
  ip_character?: string
  style?: string
  created_at: string
}

export interface LiveRoomListResponse {
  items: LiveRoom[]
}

export interface LiveRoomCreate {
  name: string
  category: string
  keywords?: string[]
  ip_character?: string
  style?: string
}

export const liveRoomsApi = {
  // 获取直播间列表
  getLiveRooms(category?: string) {
    return apiClient.get<LiveRoomListResponse>('/live-rooms', {
      params: { category }
    })
  },

  // 获取直播间详情
  getLiveRoomDetail(id: string) {
    return apiClient.get<LiveRoom>(`/live-rooms/${id}`)
  },

  // 创建直播间
  createLiveRoom(data: LiveRoomCreate) {
    return apiClient.post('/live-rooms', data)
  },

  // 更新直播间
  updateLiveRoom(id: string, data: Partial<LiveRoomCreate>) {
    return apiClient.put(`/live-rooms/${id}`, data)
  },

  // 删除直播间
  deleteLiveRoom(id: string) {
    return apiClient.delete(`/live-rooms/${id}`)
  }
}

