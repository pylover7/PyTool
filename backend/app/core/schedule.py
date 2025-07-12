from sqlmodel import Session

from app.controllers.order import orderController
from app.settings.log import logger


async def update_expired_orders(session: Session):
    """
    更新过期订单的状态及其关联的卡的状态。

    本函数从数据库中查询所有状态为锁定状态并且创建时间小于当前时间减去某个时间阈值的订单。
    这些订单被视为已过期，需要更新其状态为已取消，同时将其关联的卡密的状态更新为未使用。

    参数:
    - session: Session - 数据库会话，用于执行数据库操作。
    """
    # 遍历所有查询到的过期订单
    try:
        await orderController.cancel(session)
        logger.debug("定时更新过期订单...")
    except Exception as e:
        logger.error(f"更新过期订单失败: {e}")
        session.rollback()
