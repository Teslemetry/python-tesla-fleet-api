# 能源设备接口中文指南

[中文目录](README.md) · [英文详细示例](../fleet_api_energy_sites.md)

## 什么是能源站

这里的能源站（Energy Site）指 Powerwall 等能源设备所属的站点，不是车辆对象。
`energy_site_id` 与 VIN 不同，可从账号有权限访问的 `api.products()` 结果中取得。
是否可在中国区账号使用，需要按实际设备和服务授权验证。

以下完整示例只读取站点信息：

```python
import asyncio
import os

import aiohttp
from tesla_fleet_api import TeslaFleetApi
from tesla_fleet_api.exceptions import TeslaFleetError


async def main():
    async with aiohttp.ClientSession() as session:
        api = TeslaFleetApi(
            session=session,
            access_token=os.environ["TESLA_ACCESS_TOKEN"],
            region="cn",
        )
        site = api.energySites.create(int(os.environ["TESLA_ENERGY_SITE_ID"]))
        try:
            data = await site.site_info()
            print(data)
        except TeslaFleetError:
            print("读取能源站失败，请检查账号授权、区域和设备支持情况。")


if __name__ == "__main__":
    asyncio.run(main())
```

## 日常读取与设置

| 方法 | 中文含义 | 类型 |
|---|---|---|
| `site_info()` | 站点配置信息 | 读取 |
| `live_status()` | 当前能源功率与状态 | 读取 |
| `backup_history(...)` | 备电事件历史 | 读取 |
| `charge_history(...)` | 充电历史 | 读取 |
| `energy_history(...)` | 能量历史 | 读取 |
| `backup(backup_reserve_percent=20)` | 将备电保留比例设为 20% | 修改 |
| `grid_import_export(...)` | 电网输入/输出相关设置 | 修改 |
| `off_grid_vehicle_charging_reserve(...)` | 离网车辆充电保留设置 | 修改 |
| `operation(...)` | 运行模式设定 | 修改 |
| `storm_mode(enabled=...)` | 风暴模式开关 | 修改 |
| `time_of_use_settings(settings=...)` | 分时电价配置 | 修改 |

省略号代表需要按方法签名补齐参数，不能原样复制当作真实配置。
读写权限不同：设备信息通常需要 `energy_device_data`，命令需要相应的 `energy_cmds` 授权。
本分支 MCP 目前只开放车辆相关工具，没有能源设备 MCP 工具。

## 分时电价怎么读取

`unwrap_tariff_v2` 从站点响应或电价对象中提取电价结构；`get_tariff_periods` 在本地解析当前买卖电价，
不会发起 API 请求：

```python
from datetime import datetime
from zoneinfo import ZoneInfo

from tesla_fleet_api import get_tariff_periods, unwrap_tariff_v2

# 在已创建 site 的异步函数中使用
info = await site.site_info()
tariff = unwrap_tariff_v2(info)
# 用站点实际 installation_time_zone 替换；不要固定使用本机时区
site_timezone = ZoneInfo("Asia/Shanghai")
now = datetime.now(site_timezone)
resolution = get_tariff_periods(tariff, now, horizon_hours=24)
```

时间必须带时区并对应站点本地时间。没有覆盖当前时间的季节配置时，解析可返回 `None`。
缺失价格保留为 `None`，真实零价格仍是 `0.0`；不能把缺数据当作免费用电。
不合法或缺少关键字段的电价输入会抛出 `InvalidResponse`。

## 设备命令和网关授权

能源网关还提供设备级命令。部分端点没有完整公开架构，SDK 包装存在不代表已经在所有硬件上验证。

| 方法 | 中文作用 |
|---|---|
| `get_system_info()` | 系统、固件及设备身份信息 |
| `get_networking_status()` | 网络连接状态 |
| `wifi_scan()` | 可用 Wi-Fi 扫描 |
| `get_device_cert()` | 设备证书 |
| `list_authorized_clients()` | 原始已授权客户端列表 |
| `add_authorized_client(...)` | 注册本地签名客户端公钥 |
| `remove_authorized_client(...)` | 移除公钥；Fleet 路径存在未硬件验证的边界 |
| `get_signed_commands_public_key()` | 网关的签名命令公钥 |
| `get_backup_events()` | 备电事件 |
| `schedule_backup_event(...)` / `cancel_backup_event()` | 安排 / 取消备电事件 |
| `dispatch_battery_power(power_watts, duration_seconds)` | 临时指定电池功率 |
| `resume_battery_operation()` | 释放临时功率设定 |

电池功率单位是瓦：正数放电、负数充电；持续时间为 1–86400 秒整数。
接口确认不等于功率已经达到目标，还需要读取 `live_status()` 验证，网关仍会施加自身的储备与电网限制。

## 为什么不能直接通过云端切换离网

当前云端 `set_island_mode()`、`go_off_grid()`、`reconnect_grid()` 会抛出
`SignedCommandRequired`。原因是未签名命令可能被网关接收但不实际切换接触器。
不要捕获异常后当作切换成功，也不要删除这个保护来获得看似成功的响应。
本地签名方案见[能源本地控制](energy_local_control.md)，实际电气操作仍需要核对设备状态。
