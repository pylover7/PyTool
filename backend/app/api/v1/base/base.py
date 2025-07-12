import json
from datetime import timedelta, datetime
from uuid import uuid4

from fastapi import APIRouter, Request, WebSocket
from fastapi.websockets import WebSocketState
from sqlmodel import select
from jwt.exceptions import ExpiredSignatureError
from wechatpayv3 import WeChatPayType

from app.controllers.department import deptController
from app.controllers.goods import goodsController, goodsCouponController, goodsCategoryController
from app.controllers.order import orderController
from app.controllers.user import userController
from app.settings.log import logger
from app.models.login import CredentialsSchema, JWTPayload, JWTOut, refreshTokenSchema, JWTReOut
from app.core.ctx import CTX_USER_ID
from app.core.dependency import DependAuth, SessionDep
from app.models import Api, Menu, Role, User, UpdatePassword, OrderCreate
from app.models.base import Fail, Success, FailAuth
from app.settings import settings
from app.utils import menuTree, now
from app.utils.jwtt import create_access_token, decode_access_token
from app.utils.password import get_password_hash, verify_password
from app.utils.pay import notify_url
from app.utils.pay.wechat import wxpay

router = APIRouter()


@router.post("/accessToken", summary="获取token")
async def login_access_token(
        session: SessionDep, request: Request, credentials: CredentialsSchema):
    user: User = await userController.authenticate(session=session, credentials=credentials, request=request)
    await userController.update_last_login(session=session, id=user.id.__str__())
    roles = [item.code for item in user.roles]
    try:
        depart = deptController.get_all_name(session, user)
    except Exception as e:
        logger.debug("获取部门名称失败")
        depart = ""
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(
        minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now() + access_token_expires
    expire_refresh = datetime.now() + refresh_token_expires

    data = JWTOut(
        username=user.username,
        avatar=user.avatar or "",
        depart=depart,
        roles=roles,
        accessToken=create_access_token(
            data=JWTPayload(
                user_id=user.id.__str__(),
                username=user.username,
                is_superuser=user.is_superuser,
                exp=expire,
            )
        ),
        refreshToken=create_access_token(
            data=JWTPayload(
                user_id=user.id.__str__(),
                username=user.username,
                is_superuser=user.is_superuser,
                exp=expire_refresh,
            )
        ),
        expires=expire.strftime("%Y-%m-%d %H:%M:%S")  # expire.timestamp()
    )
    return Success(data=data.model_dump())


@router.post("/refreshToken", summary="刷新token")
async def refresh_token(refreshToken: refreshTokenSchema):
    try:
        payload = decode_access_token(refreshToken.refreshToken)
    except ExpiredSignatureError:
        return FailAuth(msg="refreshToken已过期")
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(
        minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now() + access_token_expires
    expire_refresh = datetime.now() + refresh_token_expires

    data = JWTReOut(
        accessToken=create_access_token(
            data=JWTPayload(
                user_id=payload.user_id,
                username=payload.username,
                is_superuser=payload.is_superuser,
                exp=expire,
            )
        ),
        refreshToken=create_access_token(
            data=JWTPayload(
                user_id=payload.user_id,
                username=payload.username,
                is_superuser=payload.is_superuser,
                exp=expire_refresh,
            )
        ),
        expires=expire.strftime("%Y-%m-%d %H:%M:%S")  # expire.timestamp()
    )

    return Success(data=data.model_dump())


@router.get("/userinfo", summary="查看用户信息", dependencies=[DependAuth])
async def get_userinfo(session: SessionDep):
    user_id = CTX_USER_ID.get()
    user_obj = userController.get(session=session, id=user_id)
    data = await user_obj.to_dict(exclude_fields=["password"])
    return Success(data=data)


@router.get("/userMenu", summary="查看用户菜单", dependencies=[DependAuth])
async def get_user_menu(session: SessionDep):
    user_id = CTX_USER_ID.get()
    user_obj = await userController.get(session=session, id=user_id)
    menus: list[Menu] = []
    if user_obj.is_superuser:
        menus = session.exec(select(Menu)).all()
    else:
        role_objs: list[Role] = user_obj.roles
        for role_obj in role_objs:
            menu = role_obj.menus
            menus.extend(menu)
    parent_menus: list[Menu] = []
    for menu in menus:
        if menu.parentId is None:
            parent_menus.append(menu)
    res = []

    for parent_menu in parent_menus:
        parent_menu_dict = await parent_menu.to_dict()
        parent_menu_dict["children"] = []
        parent_menu_dict["meta"] = {}
        parent_menu_dict["meta"]["title"] = parent_menu_dict["title"]
        parent_menu_dict["meta"]["icon"] = parent_menu_dict["icon"]
        parent_menu_dict["meta"]["showLink"] = parent_menu_dict["showLink"]
        parent_menu_dict["meta"]["rank"] = parent_menu_dict["rank"]

        parent_menu_dict = await menuTree(parent_menu_dict, menus)
        res.append(parent_menu_dict)
    return Success(data=res)


@router.get("/userApi", summary="查看用户API", dependencies=[DependAuth])
async def get_user_api(session: SessionDep):
    user_id = CTX_USER_ID.get()
    user_obj = await userController.get(session=session, id=user_id)
    if user_obj.is_superuser:
        statement = select(Api)
        result = session.exec(statement)
        api_objs = result.all()
        apis = [api.method.lower() + api.path for api in api_objs]
        return Success(data=apis)
    role_objs: list[Role] = user_obj.roles
    apis = []
    for role_obj in role_objs:
        api_objs: list[Api] = role_obj.apis
        apis.extend([api.method.lower() + api.path for api in api_objs])
    apis = list(set(apis))
    return Success(data=apis)


@router.post("/updatePwd", summary="更新用户密码", dependencies=[DependAuth])
async def update_user_password(session: SessionDep, req_in: UpdatePassword):
    user_id = CTX_USER_ID.get()
    user = userController.get(session=session, id=user_id)
    verified = verify_password(req_in.current_password, user.password)
    if not verified:
        return Fail(msg="旧密码验证错误！")
    user.password = get_password_hash(req_in.new_password)
    session.add(user)
    session.commit()
    return Success(msg="修改成功")


@router.get("/allShopCate", summary="获取所有商品分类")
async def category_all(session: SessionDep):
    category_obj = await goodsCategoryController.all(session)
    result = [await item.to_dict() for item in category_obj]
    return Success(msg="商品分类列表查询成功！", data=result)


@router.get("/shopList", summary="获取所有商品")
async def goods_all(session: SessionDep, categoryId: str | None = None):
    goods_objs = await goodsController.all(session, categoryId)
    result = []
    for item in goods_objs:
        card_objs = item.card
        cardCount = len([card for card in card_objs if card.status == 1])
        couponCount = len(
            [coupon for coupon in item.coupon if coupon.status != 0])
        goods = await item.to_dict()
        goods["cardCount"] = cardCount
        goods["couponCount"] = couponCount
        result.append(goods)
    return Success(msg="商品列表查询成功！", data=result)


@router.get("/checkCoupon", summary="校验优惠券")
async def check_coupon(session: SessionDep, code: str, goods_id: str):
    coupon_obj = await goodsCouponController.get_by_code(session, code)
    if not coupon_obj:
        return Success(code=201, msg="优惠券不存在！")
    if coupon_obj.goods_id.__str__() != goods_id:
        return Success(code=201, msg="该商品没有此优惠券！")
    if coupon_obj.status == 0:
        return Success(code=201, msg="优惠券已使用！")
    if coupon_obj.end_time < now(0):
        return Success(code=201, msg="优惠券已过期！")
    if len(coupon_obj.order) >= coupon_obj.limit:
        return Success(code=201, msg="优惠券已使用完啦！")
    return Success(msg="优惠券校验成功！", data=await coupon_obj.to_dict())


@router.post("/notify/{name}", summary="支付回调")
async def notify(name: str, request: Request, session: SessionDep):
    match name:
        case "wechat":
            result = wxpay.callback(headers=request.headers, body=await request.body())
            if result and result.get('event_type') == 'TRANSACTION.SUCCESS':
                resource = result.get('resource')
                out_trade_no = resource.get('out_trade_no')
                # appid = resource.get('appid')
                # mchid = resource.get('mchid')
                # transaction_id = resource.get('transaction_id')
                # trade_type = resource.get('trade_type')
                # trade_state = resource.get('trade_state')
                # trade_state_desc = resource.get('trade_state_desc')
                # bank_type = resource.get('bank_type')
                # attach = resource.get('attach')
                # success_time = resource.get('success_time')
                # payer = resource.get('payer')
                # amount = resource.get('amount').get('total')
                await orderController.complete(session, out_trade_no)

                return Success(msg="支付成功")
            else:
                return Fail(msg="支付失败")


@router.websocket("/wechat", name="微信支付")
async def wechat_pay(websocket: WebSocket, session: SessionDep):
    await websocket.accept()
    order_code = uuid4().__str__().replace("-", "")[:10] + "-" + now(3)
    try:
        while True:
            data = await websocket.receive_json()
            # 检查是否有新的消息
            if data.get("type") == "heartbeat":
                logger.debug("心跳中...")
                continue
            else:
                # 处理普通信息
                data["code"] = order_code
                obj_in = OrderCreate.model_validate(data)
                order_obj = await orderController.get(session, data["id"])
                if order_obj is None:
                    order_obj = await orderController.create(session, obj_in)
                    code_url, message = wxpay.pay(
                        description=order_obj.goods.name,
                        out_trade_no=order_code,
                        amount={"total": order_obj.amount},
                        pay_type=WeChatPayType.NATIVE,
                        notify_url=notify_url("wechat"),
                    )
                    code_url = json.loads(message)["code_url"]
                    result = await order_obj.to_dict()
                    coupon = {"code": ""}
                    result["coupon"] = coupon
                else:
                    session.refresh(order_obj)
                    result = await order_obj.to_dict()
                    code_url = data["code_url"]
                result["code_url"] = code_url
                await websocket.send_json(result)

    except Exception as e:
        logger.debug(e)
        if websocket.client_state == WebSocketState.DISCONNECTED:
            logger.debug("客户端已断开连接")
        else:
            await websocket.close()
