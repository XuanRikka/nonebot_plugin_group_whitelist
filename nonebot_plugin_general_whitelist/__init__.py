from nonebot.plugin import PluginMetadata
from nonebot import get_driver
from nonebot import CommandGroup, on_message
from nonebot import logger
from nonebot.params import CommandArg
from nonebot.adapters import Message, Event
from nonebot.permission import SUPERUSER

from .config import Config

import json
import os

driver = get_driver()
global_config = driver.config
config = Config.parse_obj(global_config)

__plugin_meta__ = PluginMetadata(
    name="nonebot_plugin_general_whitelist",
    description="简易群聊白名单",
    usage="/whitelist.add <群号> 添加白名单\n"
          "/whitelist.remove <群号> 移除白名单\n"
          "/whitelist.lookup 列出白名单",
    type="application",
    homepage="https://github.com/Rikka-desu/nonebot_plugin_general_whitelist"
)


async def whitelist_block_rule(event: Event):
    if (session := event.get_session_id()).startswith("group_"):
        group_id = session.split("_")[1]
        return group_id not in global_config.whitelist
    return True


whitelist_block = on_message(priority=-1, block=True, rule=whitelist_block_rule)
whitelist_command_group = CommandGroup("whitelist", permission=SUPERUSER, priority=-2)
whitelist_add = whitelist_command_group.command("add")
whitelist_remove = whitelist_command_group.command("remove")
whitelist_lookup = whitelist_command_group.command("lookup")


async def save_whitelist():
    with open(r"./data/whitelist/whitelist.json", "w") as f:
        f.write(json.dumps([group_id for group_id in global_config.whitelist]))


@driver.on_startup
async def init_whitelist():  # 将存储的白名单写入全局配置中
    if not os.path.exists(r"./data/whitelist/"):
        os.makedirs(r"./data/whitelist/")
        with open(r"./data/whitelist/whitelist.json", "w") as f:
            f.write("[]")
    with open(r"./data/whitelist/whitelist.json", "r") as f:
        whitelists = json.loads(f.read())
    global_config.whitelist = {group_id for group_id in whitelists}
    logger.info(f"Whitelist:{global_config.whitelist}")


@whitelist_add.handle()
async def whitelist_add_handle(args: Message = CommandArg()):
    group_id: str = args.extract_plain_text().strip()
    if not group_id.isdigit():
        await whitelist_add.finish("输入的群号必须为纯数字")
    if group_id in global_config.whitelist:
        await whitelist_add.finish("白名单中已经存在此群")
    global_config.whitelist.add(group_id)
    await save_whitelist()
    await whitelist_add.finish("白名单添加成功")


@whitelist_remove.handle()
async def whitelist_remove_handle(args: Message = CommandArg()):
    group_id: str = args.extract_plain_text().strip()
    if not group_id.isdigit():
        await whitelist_remove.finish("群输入号必须是纯数字")
    if group_id not in global_config.whitelist:
        await whitelist_remove.finish("白名单里没有这个群")
    global_config.whitelist.remove(group_id)
    await save_whitelist()
    await whitelist_remove.finish("白名单删除成功")


@whitelist_lookup.handle()
async def whitelist_lookup_handle():
    msg = ''
    for i in global_config.whitelist:
        msg = f"{msg}{i}\n"
    await whitelist_lookup.finish(f"全部白名单为：\n{msg}".strip())


