# Teslemetry 服务中文指南

[中文目录](README.md) · [英文详细示例](../teslemetry.md)

## 它和 Tesla 官方接口是什么关系

Teslemetry 是第三方服务。SDK 提供 `Teslemetry` 客户端来适配它，但它不是 Tesla 官方客户端的别名。
服务的访问令牌、授权、使用条件和账号可用范围由该服务决定，不能把 Tesla 中国区 Token 直接当作
Teslemetry Token，也不能假定第三方服务已验证中国区车辆支持。

## 初始化

完整示例只读取当前服务授权范围：

```python
import asyncio
import os

import aiohttp
from tesla_fleet_api import Teslemetry
from tesla_fleet_api.exceptions import TeslaFleetError


async def main():
    async with aiohttp.ClientSession() as session:
        api = Teslemetry(
            session=session,
            access_token=os.environ["TESLEMETRY_ACCESS_TOKEN"],
        )
        try:
            scopes = await api.scopes()
            print(scopes)
        except TeslaFleetError:
            print("Teslemetry 查询失败，请检查该服务的凭证和授权。")


if __name__ == "__main__":
    asyncio.run(main())
```

## 常用客户端方法

| 方法 | 中文作用 |
|---|---|
| `ping()` | 检查服务响应 |
| `test()` | 检查 API 身份验证 |
| `userdata()` | 用户数据 |
| `metadata()` | 元数据，包括部分授权信息 |
| `scopes()` | 当前权限范围 |
| `server_side_polling(vin)` | 查询服务端轮询设置 |
| `server_side_polling(vin, value=True/False)` | 开启 / 关闭服务端轮询 |
| `vehicle_data_refresh(vin)` | 要求刷新车辆数据 |
| `fields()` | 遥测字段及相关元数据 |
| `vehicle_config(vin)` | 已保存的车辆配置 |
| `streaming_config(vin)` | 遥测流配置 |
| `modify_streaming_config(vin, fields)` | 修改指定遥测字段配置 |
| `create_streaming_config(vin, fields)` | 创建或更新遥测配置 |
| `stop_streaming(vin)` | 停止遥测流 |

修改轮询和遥测配置会改变实际采集行为，不是普通只读查询。
轮询间隔、字段上报频率和位置采集应按隐私需求与服务规则设置；不要为了试用覆盖原配置。

## 车辆对象与自定义命令

```python
# 局部片段：api 是已初始化的 Teslemetry 客户端
vehicle = api.vehicles.create(vin)
```

除常见车辆方法外，SDK 还包装了服务特有的 PIN 管理、钥匙管理、状态刷新、门盖、座椅加热、
太阳能充电、行车记录、视频和灯光秀等方法。各类操作的参数并不完全相同，见英文逐项示例。
清除 PIN 或移除钥匙是授权/安全设置变更，不能自动运行一遍来验证是否“接口可用”。
这些方法也没有因为 SDK 包装存在而自动加入本分支 MCP 工具列表。

## 能源站授权、地址和功率控制

```python
# 在异步函数中使用，energy_site_id 为账号实际站点 ID
site = api.energySites.create(energy_site_id)
clients = await site.find_authorized_clients()
address = await site.find_gateway_address()
```

`find_authorized_clients()` 返回带类型的 `AuthorizedClients`：可读取
`clients`、每个客户端的 `public_key/state/roles/verification` 和原始 `raw`。
未知值保留；只有明确的空列表才表示没有客户端，结构不合法会抛出 `InvalidResponse`。
`list_authorized_clients()` 则保留原始响应。

`find_gateway_address()` 优先选择报告活动路由的以太网或 Wi-Fi IPv4，不选择蜂窝网络。
没有可用地址返回 `None`，不是自动使用一个默认网关地址。
配对等待与本地签名验证见[能源本地控制](energy_local_control.md)。

`dispatch_battery_power(power_watts, duration_seconds)` 中，正功率放电、负功率充电，单位为瓦；
时长 1–86400 秒。`resume_battery_operation()` 释放临时设定，实际状态需要单独核对。

## OAuth 迁移和动态注册

`migrate_to_oauth(client_id=...)` 对应服务的 OAuth 迁移流程。
`register_client(session, ...)` 是独立的 Teslemetry 动态注册辅助方法，不需要先构造已有账号客户端。
它每次都会注册新客户端，调用方必须保存返回的 `client_id`，而不是每次启动都重新注册。
失败可抛出 `TeslemetryRegistrationError`。

这个注册能力仅属于 Teslemetry，不能拿来代替 Tesla Fleet 中国区开发者应用注册或 Tessie 授权。
