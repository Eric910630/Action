"""
异步任务等待工具
用于E2E测试中等待Celery任务完成
"""
import time
from celery.result import AsyncResult
from app.celery_app import celery_app
from loguru import logger


def wait_for_task(task_id: str, timeout: int = 300, poll_interval: int = 2) -> dict:
    """
    等待Celery任务完成
    
    Args:
        task_id: Celery任务ID
        timeout: 超时时间（秒），默认300秒
        poll_interval: 轮询间隔（秒），默认2秒
    
    Returns:
        任务结果字典
    
    Raises:
        TimeoutError: 任务超时
        Exception: 任务执行失败
    """
    result = AsyncResult(task_id, app=celery_app)
    
    start_time = time.time()
    logger.info(f"🔍 [探针] 开始等待任务完成: {task_id}")
    logger.info(f"🔍 [探针] 超时设置: {timeout}秒, 轮询间隔: {poll_interval}秒")
    
    # 初始状态检查
    initial_status = result.status
    logger.info(f"🔍 [探针] 任务初始状态: {initial_status}, ready: {result.ready()}")
    
    poll_count = 0
    last_status = initial_status
    
    while not result.ready():
        elapsed = time.time() - start_time
        poll_count += 1
        
        # 每10次轮询（约20秒）或状态变化时记录详细信息
        if poll_count % 10 == 0 or result.status != last_status:
            current_status = result.status
            logger.info(f"🔍 [探针 #{poll_count}] 任务状态检查: {current_status}, 已等待: {elapsed:.1f}秒, ready: {result.ready()}")
            if current_status != last_status:
                logger.info(f"🔍 [探针] 状态变化: {last_status} -> {current_status}")
                last_status = current_status
            
            # 如果是PENDING状态超过30秒，记录警告
            if current_status == "PENDING" and elapsed > 30:
                logger.warning(f"⚠️  [探针] 任务已PENDING超过30秒，可能未被Worker接收")
                # 尝试检查Worker状态
                try:
                    from celery import current_app
                    inspector = current_app.control.inspect()
                    active = inspector.active()
                    scheduled = inspector.scheduled()
                    reserved = inspector.reserved()
                    logger.info(f"🔍 [探针] Worker状态 - 活动任务: {len([t for tasks in (active or {}).values() for t in tasks])}, "
                              f"计划任务: {len([t for tasks in (scheduled or {}).values() for t in tasks])}, "
                              f"保留任务: {len([t for tasks in (reserved or {}).values() for t in tasks])}")
                except Exception as e:
                    logger.warning(f"⚠️  [探针] 无法检查Worker状态: {e}")
        
        if elapsed > timeout:
            logger.error(f"❌ [探针] 任务超时: {task_id}, 已等待 {elapsed:.1f}秒 (超时设置: {timeout}秒)")
            logger.error(f"❌ [探针] 最终状态: {result.status}, ready: {result.ready()}")
            raise TimeoutError(f"任务超时 ({timeout}秒): {task_id}")
        
        logger.debug(f"任务 {task_id} 仍在运行，已等待 {elapsed:.1f} 秒 (轮询 #{poll_count})")
        time.sleep(poll_interval)
    
    # 任务完成后的状态检查
    final_status = result.status
    elapsed = time.time() - start_time
    logger.info(f"🔍 [探针] 任务完成检查: 状态={final_status}, ready={result.ready()}, 总耗时={elapsed:.1f}秒, 总轮询次数={poll_count}")
    
    if result.failed():
        error_info = result.info
        logger.error(f"❌ [探针] 任务失败: {task_id}, 错误: {error_info}")
        raise Exception(f"任务执行失败: {error_info}")
    
    task_result = result.get()
    logger.info(f"✅ [探针] 任务成功完成: {task_id}, 耗时: {elapsed:.1f} 秒, 结果: {task_result}")
    
    return task_result


def get_task_status(task_id: str) -> dict:
    """
    获取任务状态
    
    Args:
        task_id: Celery任务ID
    
    Returns:
        任务状态字典，包含:
        - status: 任务状态 (PENDING, STARTED, SUCCESS, FAILURE, RETRY, REVOKED)
        - result: 任务结果（如果完成）
        - error: 错误信息（如果失败）
    """
    result = AsyncResult(task_id, app=celery_app)
    
    status_info = {
        "task_id": task_id,
        "status": result.status,
        "ready": result.ready(),
    }
    
    if result.ready():
        if result.successful():
            status_info["result"] = result.get()
        else:
            status_info["error"] = str(result.info)
    
    return status_info

