import apiClient from './client'

export interface TaskStatus {
  task_id: string
  state: 'PENDING' | 'PROGRESS' | 'SUCCESS' | 'FAILURE'
  status: string
  current?: number
  total?: number
  result?: any
  error?: string
}

export const tasksApi = {
  // 获取任务状态
  getTaskStatus(taskId: string) {
    return apiClient.get<TaskStatus>(`/tasks/${taskId}`)
  }
}

