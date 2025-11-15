"""
任务状态查询API
"""
from fastapi import APIRouter, HTTPException
from app.celery_app import celery_app

router = APIRouter()


@router.get("/{task_id}")
async def get_task_status(task_id: str):
    """查询任务状态"""
    from celery.result import AsyncResult
    task = AsyncResult(task_id, app=celery_app)
    
    # 获取任务状态
    state = task.state
    
    # 处理各种状态
    if state == 'PENDING':
        response = {
            'task_id': task_id,
            'state': 'PENDING',
            'status': '任务等待中...'
        }
    elif state == 'STARTED':
        response = {
            'task_id': task_id,
            'state': 'PROGRESS',
            'status': '任务已开始...'
        }
    elif state == 'PROGRESS':
        info = task.info or {}
        response = {
            'task_id': task_id,
            'state': 'PROGRESS',
            'current': info.get('current', 0),
            'total': info.get('total', 1),
            'status': info.get('status', '任务进行中...')
        }
    elif state == 'SUCCESS':
        response = {
            'task_id': task_id,
            'state': 'SUCCESS',
            'result': task.result,
            'status': '任务完成'
        }
    elif state == 'FAILURE':
        response = {
            'task_id': task_id,
            'state': 'FAILURE',
            'error': str(task.info) if task.info else '未知错误',
            'status': '任务失败'
        }
    elif state == 'REVOKED':
        response = {
            'task_id': task_id,
            'state': 'FAILURE',
            'error': '任务已取消',
            'status': '任务已取消'
        }
    else:
        # 未知状态，返回原始状态
        response = {
            'task_id': task_id,
            'state': state or 'UNKNOWN',
            'status': f'任务状态: {state}' if state else '任务状态未知'
        }
    
    return response

