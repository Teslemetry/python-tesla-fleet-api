# Tessie 服务中文指南

[中文目录](README.md) · [英文详细示例及全部命令参数](../tessie.md)

## 初始化与权限

Tessie 是第三方车辆数据和控制服务，使用它自己的访问令牌。
本仓库的 `Tessie` 适配器不代表中国区车辆或当前服务方案已经验证可用。
不要把第三方令牌、Tesla Token 和 MCP Bearer 混用。

```python
import asyncio
import os

import aiohttp
from tesla_fleet_api import Tessie
from tesla_fleet_api.exceptions import TeslaFleetError


async def main():
    async with aiohttp.ClientSession() as session:
        api = Tessie(
            session=session,
            access_token=os.environ["TESSIE_ACCESS_TOKEN"],
        )
        try:
            vehicles = await api.list_vehicles()
            print(vehicles)
        except TeslaFleetError:
            print("Tessie 查询失败，请检查该服务的账号与权限。")


if __name__ == "__main__":
    asyncio.run(main())
```

## 顶层方法与车辆对象

| 方法 | 中文含义 |
|---|---|
| `scopes()` | 查询授权范围 |
| `list_vehicles()` | 查询服务账号下的车辆 |
| `list_vehicles(only_active=True)` | 只查询活动车辆 |
| `all_battery_health()` | 多车辆电池健康信息 |
| `charging_invoices()` | 充电账单信息 |

通过 `vehicle = api.vehicles.create(vin)` 创建单车对象。不要照搬其他适配器的方法名，
Tessie 的不少原生名称与 Fleet API 不同。

## 查询状态、行程和充电记录

| 方法 | 中文作用 |
|---|---|
| `state()` 或 `vehicle()` | 车辆状态，通常可用缓存 |
| `state(use_cache=False)` | 显式要求不使用该缓存选项 |
| `vehicle_status()` | 车辆状态接口，不接受 `use_cache` 参数 |
| `battery()` / `battery_health()` | 电池数据 / 电池健康 |
| `states(start=..., end=..., results=...)` | 指定时间范围的状态历史 |
| `location()` | 位置 |
| `firmware_alerts()` | 固件提醒 |
| `map(width=..., height=..., zoom=...)` | 地图相关数据 |
| `consumption_since_charge()` | 上次充电后的能耗 |
| `weather()` | 天气信息 |
| `drives(...)` / `path(...)` | 驾驶记录 / 轨迹 |
| `charges(...)` / `idles(...)` / `last_idle_state()` | 充电 / 停驶 / 最近停驶状态 |

`start`、`end` 等时间参数按对应服务接口和 SDK 签名填写。
定位、轨迹与账单都是隐私数据，不应公开输出；缓存状态也不能当作车辆当前状态的保证。

## 常见控制名称对照

| Tessie 方法 | 中文含义 |
|---|---|
| `wake()` | 唤醒 |
| `lock()` / `unlock()` | 锁车 / 解锁 |
| `activate_front_trunk()` / `activate_rear_trunk()` | 操作前备箱 / 后备箱 |
| `vent_windows()` / `close_windows()` | 车窗通风 / 关闭 |
| `start_climate()` / `stop_climate()` | 开启 / 关闭空调 |
| `set_temperatures(temperature=...)` | 设定温度 |
| `set_seat_heat(seat=..., level=...)` | 设定座椅加热 |

这张表是查名称用的，不是一段应连续执行的控制流程。
车型支持、参数允许值和设备限制仍由实际服务与车辆决定。

## 等待完成和重试参数

Tessie 客户端及许多车辆命令支持 `wait_for_completion` 和 `max_attempts`。
单次调用传入值可覆盖客户端默认值。
“等待服务完成”或“多次尝试”不等于车辆物理动作已核验，也不保证危险命令仅执行一次。
结果不明确时先检查车辆，不能单纯把尝试次数调大。
本分支 MCP 不使用 Tessie 作为自动回退后端。
