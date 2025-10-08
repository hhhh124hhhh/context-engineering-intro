"""
健康检查路由
提供系统健康状态检查
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Dict, Any
import structlog
from datetime import datetime

from app.database.postgres import get_db
from app.database.redis import check_redis_health, get_redis_service
from app.core.config import settings

logger = structlog.get_logger()
router = APIRouter()


@router.get("/health", response_model=Dict[str, Any])
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    系统健康检查
    检查数据库、Redis连接和其他系统组件状态
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": getattr(settings, 'APP_VERSION', '1.0.0'),
        "environment": getattr(settings, 'ENVIRONMENT', 'development'),
        "services": {
            "database": {"status": "unknown"},
            "redis": {"status": "unknown"},
            "memory": {"status": "unknown"},
            "disk": {"status": "unknown"}
        },
        "checks_performed": []
    }

    all_healthy = True

    # 检查数据库连接
    try:
        result = await db.execute(text("SELECT 1 as health_check"))
        db_result = result.scalar()
        if db_result == 1:
            health_status["services"]["database"] = {
                "status": "healthy",
                "message": "数据库连接正常"
            }
            health_status["checks_performed"].append("database: ok")
        else:
            raise Exception("数据库健康检查返回意外结果")
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        health_status["services"]["database"] = {
            "status": "unhealthy",
            "message": f"数据库连接失败: {str(e)}"
        }
        health_status["checks_performed"].append(f"database: failed - {str(e)}")
        all_healthy = False

    # 检查Redis连接
    try:
        redis_healthy = check_redis_health()
        if redis_healthy:
            health_status["services"]["redis"] = {
                "status": "healthy",
                "message": "Redis连接正常"
            }
            health_status["checks_performed"].append("redis: ok")
        else:
            raise Exception("Redis健康检查失败")
    except Exception as e:
        logger.error("Redis health check failed", error=str(e))
        health_status["services"]["redis"] = {
            "status": "unhealthy",
            "message": f"Redis连接失败: {str(e)}"
        }
        health_status["checks_performed"].append(f"redis: failed - {str(e)}")
        all_healthy = False

    # 检查内存使用情况
    try:
        import psutil
        memory = psutil.virtual_memory()
        memory_usage_percent = memory.percent

        if memory_usage_percent < 80:
            health_status["services"]["memory"] = {
                "status": "healthy",
                "message": f"内存使用率: {memory_usage_percent:.1f}%",
                "usage_percent": memory_usage_percent,
                "available_gb": memory.available / (1024**3)
            }
            health_status["checks_performed"].append(f"memory: ok ({memory_usage_percent:.1f}%)")
        else:
            health_status["services"]["memory"] = {
                "status": "warning",
                "message": f"内存使用率较高: {memory_usage_percent:.1f}%",
                "usage_percent": memory_usage_percent,
                "available_gb": memory.available / (1024**3)
            }
            health_status["checks_performed"].append(f"memory: warning ({memory_usage_percent:.1f}%)")
    except ImportError:
        health_status["services"]["memory"] = {
            "status": "unknown",
            "message": "psutil未安装，无法检查内存使用情况"
        }
        health_status["checks_performed"].append("memory: unknown (psutil not available)")
    except Exception as e:
        logger.error("Memory health check failed", error=str(e))
        health_status["services"]["memory"] = {
            "status": "unhealthy",
            "message": f"内存检查失败: {str(e)}"
        }
        health_status["checks_performed"].append(f"memory: failed - {str(e)}")

    # 检查磁盘使用情况
    try:
        import psutil
        disk = psutil.disk_usage('/')
        disk_usage_percent = (disk.used / disk.total) * 100

        if disk_usage_percent < 85:
            health_status["services"]["disk"] = {
                "status": "healthy",
                "message": f"磁盘使用率: {disk_usage_percent:.1f}%",
                "usage_percent": disk_usage_percent,
                "free_gb": disk.free / (1024**3)
            }
            health_status["checks_performed"].append(f"disk: ok ({disk_usage_percent:.1f}%)")
        else:
            health_status["services"]["disk"] = {
                "status": "warning",
                "message": f"磁盘使用率较高: {disk_usage_percent:.1f}%",
                "usage_percent": disk_usage_percent,
                "free_gb": disk.free / (1024**3)
            }
            health_status["checks_performed"].append(f"disk: warning ({disk_usage_percent:.1f}%)")
    except ImportError:
        health_status["services"]["disk"] = {
            "status": "unknown",
            "message": "psutil未安装，无法检查磁盘使用情况"
        }
        health_status["checks_performed"].append("disk: unknown (psutil not available)")
    except Exception as e:
        logger.error("Disk health check failed", error=str(e))
        health_status["services"]["disk"] = {
            "status": "unhealthy",
            "message": f"磁盘检查失败: {str(e)}"
        }
        health_status["checks_performed"].append(f"disk: failed - {str(e)}")

    # 检查Redis功能测试
    try:
        redis_service = await get_redis_service()
        test_key = "health_check_test"
        test_value = {"timestamp": datetime.utcnow().isoformat()}

        # 测试设置
        set_result = redis_service.set(test_key, test_value, expire=10)
        if not set_result:
            raise Exception("Redis设置测试失败")

        # 测试获取
        get_result = redis_service.get(test_key, as_json=True)
        if not get_result or get_result.get("timestamp") != test_value["timestamp"]:
            raise Exception("Redis获取测试失败")

        # 测试删除
        delete_result = redis_service.delete(test_key)
        if delete_result == 0:
            raise Exception("Redis删除测试失败")

        health_status["services"]["redis"]["functionality_test"] = "passed"
        health_status["checks_performed"].append("redis functionality: ok")

    except Exception as e:
        logger.error("Redis functionality test failed", error=str(e))
        if "functionality_test" not in health_status["services"]["redis"]:
            health_status["services"]["redis"]["functionality_test"] = "failed"
        health_status["checks_performed"].append(f"redis functionality: failed - {str(e)}")
        all_healthy = False

    # 设置整体状态
    if not all_healthy:
        health_status["status"] = "unhealthy"

    # 检查是否有警告状态
    has_warnings = any(
        service.get("status") == "warning"
        for service in health_status["services"].values()
    )
    if has_warnings and all_healthy:
        health_status["status"] = "healthy_with_warnings"

    # 记录健康检查结果
    if all_healthy and not has_warnings:
        logger.info("Health check passed", status=health_status["status"])
    else:
        logger.warning("Health check completed with issues",
                      status=health_status["status"],
                      services=health_status["services"])

    # 如果状态不健康，返回503状态码
    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)

    return health_status


@router.get("/health/ready", response_model=Dict[str, Any])
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    就绪检查 - Kubernetes就绪探针
    只检查关键服务是否准备就绪
    """
    readiness_status = {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "database": "unknown",
            "redis": "unknown"
        }
    }

    # 检查数据库就绪状态
    try:
        result = await db.execute(text("SELECT 1"))
        if result.scalar() == 1:
            readiness_status["checks"]["database"] = "ok"
        else:
            readiness_status["checks"]["database"] = "failed"
            raise Exception("Database not ready")
    except Exception as e:
        readiness_status["status"] = "not_ready"
        readiness_status["checks"]["database"] = f"failed: {str(e)}"
        logger.error("Readiness check - database failed", error=str(e))

    # 检查Redis就绪状态
    try:
        redis_healthy = check_redis_health()
        if redis_healthy:
            readiness_status["checks"]["redis"] = "ok"
        else:
            readiness_status["checks"]["redis"] = "failed"
            raise Exception("Redis not ready")
    except Exception as e:
        readiness_status["status"] = "not_ready"
        readiness_status["checks"]["redis"] = f"failed: {str(e)}"
        logger.error("Readiness check - redis failed", error=str(e))

    if readiness_status["status"] == "not_ready":
        raise HTTPException(status_code=503, detail=readiness_status)

    return readiness_status


@router.get("/health/live", response_model=Dict[str, Any])
async def liveness_check():
    """
    存活检查 - Kubernetes存活探针
    简单检查应用是否仍在运行
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "应用程序正在运行"
    }


@router.get("/health/detailed", response_model=Dict[str, Any])
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """
    详细健康检查 - 包含更多系统信息
    """
    try:
        # 基础健康检查
        basic_health = await health_check(db)

        # 添加额外详细信息
        detailed_info = {
            "application": {
                "name": "Card Battle Arena",
                "version": getattr(settings, 'APP_VERSION', '1.0.0'),
                "environment": getattr(settings, 'ENVIRONMENT', 'development'),
                "debug": getattr(settings, 'DEBUG', False),
                "api_version": "v1"
            },
            "system": {
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "timezone": str(datetime.now().astimezone().tzinfo),
                "uptime_seconds": None  # 可以添加启动时间跟踪
            }
        }

        # 尝试获取系统信息
        try:
            import psutil
            detailed_info["system"].update({
                "cpu_count": psutil.cpu_count(),
                "cpu_usage_percent": psutil.cpu_percent(interval=1),
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
            })
        except ImportError:
            detailed_info["system"]["psutil"] = "not available"

        # 合并信息
        detailed_health = {**basic_health, **detailed_info}
        detailed_health["type"] = "detailed"

        return detailed_health

    except Exception as e:
        logger.error("Detailed health check failed", error=str(e))
        return {
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "type": "detailed"
        }