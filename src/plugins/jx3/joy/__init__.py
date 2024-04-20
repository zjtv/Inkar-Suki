from .api import *

from nonebot.rule import to_me

jx3_cmd_saohua_random = on_command("jx3_random", aliases={"骚话", "烧话"}, priority=5)


@jx3_cmd_saohua_random.handle()
async def jx3_saohua_random():
    """
    召唤一条骚话：

    Example：-骚话
    """
    full_link = f"{Config.jx3api_link}/data/saohua/random"
    info = await get_api(full_link)
    msg = info["data"]["text"]
    await jx3_cmd_saohua_random.finish(msg)

jx3_cmd_saohua_tiangou = on_command("jx3_tiangou", aliases={"舔狗"}, priority=5)


@jx3_cmd_saohua_tiangou.handle()
async def jx3_saohua_tiangou():
    """
    获取一条舔狗日志：

    Example：-舔狗
    """
    full_link = f"https://www.jx3api.com/data/saohua/content?token={token}"
    info = await get_api(full_link)
    msg = info["data"]["text"]
    await jx3_cmd_saohua_tiangou.finish(msg)

async def post_url(url: str, **kwargs):
    async with httpx.AsyncClient(follow_redirects=False) as client:
        resp = await client.post(url, **kwargs)
        return resp.json()

watermelon = on_command("jx3_watermelon", aliases={"吃瓜"}, rule=to_me(), priority=5)
@watermelon.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    tid = args.extract_plain_text()
    if tid == "":
        url = f"https://www.jx3api.com/data/tieba/random?subclass=818&token={token}&limit=1"
        data = await get_api(url)
        data = data["data"][0]
        name = data["name"]
        title = data["title"]
        server = data["server"]
        url = data["url"]
        date = data["date"]
        msg = f"咚！音卡为您找了一个瓜！\n标题：{title}\n{url}\n来源：{name}吧（{server}）\n日期：{date}"
        await watermelon.finish(msg)
    if not checknumber(tid):
        await watermelon.finish("唔……请直接给出帖子的ID（通常是链接最后那一串数字）！")
    else:
        data = await post_url(
            url = "https://api.sissy.dog/gossip_summarize", 
            headers = {"Authorization": "Bearer OmegaIsMe", "Content-Type": "application/json"}, 
            json = {"gossip_id": tid, "only_thread_author": True},
            timeout = None
        )
        msg = data["msg"]
        msg = msg + "\n以上内容由AI自动生成，请注意甄别！"
        await watermelon.finish(msg)