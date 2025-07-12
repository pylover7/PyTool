from wechatpayv3 import WeChatPay, WeChatPayType

from app.settings.config import pay_config

with open(pay_config.get_config("wechat", "private_key"), "r") as f:
    private_key = f.read()

with open(pay_config.get_config("wechat", "public_key"), "r") as f:
    public_key = f.read()

wxpay = WeChatPay(
        wechatpay_type=WeChatPayType.NATIVE,
        mchid=pay_config.get_config("wechat", "mchid"),
        private_key=private_key,
        cert_serial_no=pay_config.get_config("wechat", "cert_serial_no"),
        apiv3_key=pay_config.get_config("wechat", "apiv3_key"),
        appid=pay_config.get_config("wechat", "appid"),
        partner_mode=False,
        public_key=public_key,
        public_key_id=pay_config.get_config("wechat", "public_key_id"),
    )