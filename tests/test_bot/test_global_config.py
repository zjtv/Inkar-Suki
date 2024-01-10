
from .. import *


def test_global_update_grp_config():
    mc = MessageCallback()
    import src.plugins.jx3
    raw_matcher = src.plugins.jx3.global_cmd_update_grp_config
    src.plugins.jx3.global_cmd_update_grp_config = mc

    func = src.plugins.jx3.global_update_grp_config
    event = SFGroupMessageEvent()

    def callback_query(msg: str):
        assert 'new_value=Ellipsis' in msg
    mc.cb_send = callback_query
    mc.tag = '更新 1561234 server'
    event.message = obMessage(mc.tag)
    event.user_id = 'root'
    args = Jx3Arg.arg_factory(raw_matcher, event)
    task = func(event, args)
    asyncio.run(task)
    mc.check_counter()

    task = func(event, args)
    asyncio.run(task)
    mc.check_counter()
