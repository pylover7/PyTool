from sqlmodel import Session, create_engine, select
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.controllers.user import userController
from app.core.schedule import update_expired_orders
from app.models import *
from app.settings.log import logger
from app.utils.password import get_password_hash, md5_encrypt
from app.utils.staticFileUtils import check_dir_exists

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
scheduler = AsyncIOScheduler()


def init_api(app: FastAPI, session: Session):
    """
    初始化API
    :param app:
    :param session: Session
    :return:
    """
    apiOld = session.exec(select(Api)).all()
    apiList = []
    apis = app.openapi()["paths"]
    for path, value in apis.items():
        for method, value2 in value.items():
            tag = ",".join(value2.get("tags"))
            summary = value2.get("summary")
            if len(apiOld) == 0:
                api = Api(
                    path=path,
                    method=method.upper(),
                    tags=tag,
                    summary=summary
                )
                session.add(api)
                apiList.append(api.id)
                session.commit()
            else:
                apiIsNew = True
                for api in apiOld:
                    if api.path == path:
                        apiIsNew = False
                        api.method = method.upper()
                        api.summary = summary
                        api.tags = tag
                        session.add(api)
                        break
                if apiIsNew:
                    api = Api(
                        path=path,
                        method=method.upper(),
                        tags=tag,
                        summary=summary
                    )
                    session.add(api)
    session.commit()
    return apiList


def init_menus(session: Session):
    """
    初始化菜单
    :return:
    """
    menus = session.exec(select(Menu)).all()
    if len(menus) == 0:
        goods = Menu(
            menuType=0,
            title="商品管理",
            name="Goods",
            path="/goods",
            component="",
            rank=1,
            icon="ep:shop",
        )
        session.add(goods)
        session.commit()
        session.refresh(goods)

        goodsCategory = Menu(
            parentId=goods.id,
            menuType=0,
            title="商品分类",
            name="GoodsCategory",
            path="/goods/category",
            component="goods/category/index",
            icon="ri:dashboard-horizontal-fill",
        )
        goodsList = Menu(
            parentId=goods.id,
            menuType=0,
            title="商品列表",
            name="GoodsList",
            path="/goods/list",
            component="goods/list/index",
            icon="ri:shopping-basket-line",
        )
        goodsCoupon = Menu(
            parentId=goods.id,
            menuType=0,
            title="商品优惠券",
            name="GoodsCoupon",
            path="/goods/coupon",
            component="goods/coupon/index",
            icon="ri:coupon-line",
        )
        session.add(goodsCategory)
        session.add(goodsList)
        session.add(goodsCoupon)

        card = Menu(
            menuType=0,
            title="卡密管理",
            name="Card",
            path="/card",
            component="",
            rank=2,
            icon="ri:coupon-3-line",
        )
        session.add(card)
        session.commit()
        session.refresh(card)

        cardList = Menu(
            parentId=card.id,
            menuType=0,
            title="卡密列表",
            name="CardList",
            path="/card/list",
            component="card/index",
            rank=1,
            icon="ri:coupon-3-line",
        )
        session.add(cardList)

        order = Menu(
            menuType=0,
            title="订单管理",
            name="Order",
            path="/order",
            component="",
            rank=3,
            icon="ri:list-check-3",
        )
        session.add(order)
        session.commit()
        session.refresh(order)

        orderList = Menu(
            parentId=order.id,
            menuType=0,
            title="订单管理",
            name="OrderList",
            path="/order/list",
            component="order/index",
            rank=1,
            icon="ri:list-check-3",
        )
        session.add(orderList)

        pay = Menu(
            menuType=0,
            title="支付管理",
            name="Pay",
            path="/pay",
            component="",
            rank=4,
            icon="ri:secure-payment-fill",
        )
        session.add(pay)
        session.commit()
        session.refresh(pay)

        paySetting = Menu(
            parentId=pay.id,
            menuType=0,
            title="支付设置",
            name="PaySetting",
            path="/pay/base",
            component="pay/base/index",
            rank=1,
            icon="ri:secure-payment-fill",
        )
        session.add(paySetting)

        payWechat = Menu(
            parentId=pay.id,
            menuType=0,
            title="微信支付",
            name="PayWechat",
            path="/pay/wechat",
            component="pay/wechat/index",
            rank=2,
            icon="ri:wechat-pay-line",
        )
        session.add(payWechat)

        system = Menu(
            menuType=0,
            title="系统管理",
            name="system",
            path="/system",
            component="",
            rank=7,
            icon="ri:settings-3-line",
        )
        session.add(system)
        session.commit()
        session.refresh(system)
        systemUser = Menu(
            parentId=system.id,
            menuType=0,
            title="用户管理",
            name="SystemUser",
            path="/system/user",
            component="system/user/index",
            icon="ri:admin-line",
            rank=1
        )
        systemDept = Menu(
            parentId=system.id,
            menuType=0,
            title="部门管理",
            name="SystemDept",
            path="/system/dept",
            component="system/dept/index",
            icon="ri:git-branch-line",
            rank=4
        )
        systemRole = Menu(
            parentId=system.id,
            menuType=0,
            title="角色管理",
            name="SystemRole",
            path="/system/role",
            component="system/role/index",
            icon="ri:admin-fill",
            rank=2
        )
        systemMenu = Menu(
            parentId=system.id,
            menuType=0,
            title="菜单管理",
            name="SystemMenu",
            path="/system/menu",
            component="system/menu/index",
            icon="fluent:clover-48-regular",
        )
        session.add(systemMenu)
        session.add(systemRole)
        session.add(systemDept)
        session.add(systemUser)

        monitor = Menu(
            menuType=0,
            title="系统监控",
            name="Monitor",
            path="/monitor",
            component="",
            rank=8,
            icon="ep:monitor",
        )
        session.add(monitor)
        session.commit()
        session.refresh(monitor)
        loginLog = Menu(
            parentId=monitor.id,
            menuType=0,
            title="登录日志",
            name="LoginLog",
            path="/monitor/login-log",
            component="monitor/logs/login/index",
            icon="ri:window-line",
        )
        operationLog = Menu(
            parentId=monitor.id,
            menuType=0,
            title="操作日志",
            name="OperationLog",
            path="/monitor/operation-logs",
            component="monitor/logs/operation/index",
            icon="ri:history-fill",
        )
        systemLog = Menu(
            parentId=monitor.id,
            menuType=0,
            title="系统日志",
            name="SystemLog",
            path="/monitor/system-logs",
            component="monitor/logs/system/index",
            icon="ri:file-search-line",
        )
        session.add(loginLog)
        session.add(operationLog)
        session.add(systemLog)
        session.commit()


async def init_data(app: FastAPI) -> None:
    logger.info("初始化数据库...")
    SQLModel.metadata.create_all(engine)
    logger.info("检查静态文件目录...")
    check_dir_exists([
        settings.AVATAR_PATH,
        settings.GOODS_PATH,
        settings.CONFIG_PATH
    ])
    with Session(engine) as session:
        admin = session.exec(
            select(User).where(User.email == settings.FIRST_SUPERUSER)
        ).first()
        password = get_password_hash(
            md5_encrypt(settings.FIRST_SUPERUSER_PASSWORD))
        if not admin:
            logger.info("创建管理员账户...")
            user_in = UserCreate(
                username="admin",
                email=settings.FIRST_SUPERUSER,
                password=password,
                status=1,
                is_superuser=True,
            )
            admin = await userController.create(session=session, user_create=user_in)
            logger.info(f"创建管理员账户成功，管理员用户名为：{admin.username}")
        else:
            logger.info("管理员账户已存在，跳过管理员创建...")

        logger.info("初始化API...")
        init_api(app, session)
        logger.info("初始化菜单...")
        init_menus(session)
        logger.info("启动定时任务...")
        scheduler.add_job(
            update_expired_orders,
            "interval",
            args=[session],
            seconds=120)
        scheduler.start()
