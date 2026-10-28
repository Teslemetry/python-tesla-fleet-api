# 车辆接口中文指南

[中文目录](README.md) · [英文详细示例](../fleet_api_vehicles.md)

## 选择正确的客户端

`TeslaFleetApi` 是访问 Tesla 云端接口的客户端；它接收一个 `aiohttp.ClientSession`、
访问令牌和区域参数。中国区示例使用 `region="cn"`。
只想先查电量时，可直接使用[首页的完整只读示例](../../README.md)。

```python
api = TeslaFleetApi(session=session, access_token=access_token, region="cn")
vehicle = api.vehicles.createFleet(vin)
```

上面是局部片段：`session`、`access_token`、`vin` 需要由调用者提供。
`createFleet` 只是创建本机车辆对象，不会替账号增加车辆权限或完成钥匙配对。

## OAuth 授权和自动刷新

优先通过[本机登录流程](../cn_mcp_server.md)管理 MCP 服务的授权。
如果独立使用 SDK，可以调用 `TeslaFleetOAuth`：

```python
import secrets

from tesla_fleet_api.const import Scope
from tesla_fleet_api.tesla.oauth import TeslaFleetOAuth

# 在已有的异步函数和 ClientSession 中使用
api = TeslaFleetOAuth(
    session=session,
    region="cn",
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
)
state = secrets.token_urlsafe(32)
url = api.get_login_url(
    [Scope.OPENID, Scope.OFFLINE_ACCESS, Scope.VEHICLE_DEVICE_DATA],
    state=state,
)
# 将 url 展示给用户。在应用收到回调后，先校验回调地址、state、错误参数和有效期。
# 校验通过后，才将回调里的授权码交给 SDK：
# await api.get_refresh_token(code)
```

这段是授权构造片段，不是完整回调服务器。SDK 不会替独立调用者校验回调 `state`，
也不会自动保存轮换后的 Token。应用需要安全保存 `refresh_token` 和过期时间；
`await api.access_token()` 得到当前有效访问令牌。不要把协程对象或令牌打印到公开日志。
本分支 MCP 的 `ManagedOAuth` 另有进程租约、刷新串行化和持久化保护。

## 查询列表、状态和位置

下面均在已创建 `api`、`vehicle` 的异步函数里使用，按需要选择调用：

```python
# 列出账号产品：可能同时包含车辆和能源站
products = await api.products()

# 按页查询车辆；返回的账号车辆范围由 Tesla 授权决定
vehicles = await vehicle.list(page=1, per_page=100)

# 读取电量与车辆状态，指定字段组减少无关数据
state = await vehicle.vehicle_data(endpoints=["charge_state", "vehicle_state"])

# 位置需要独立的 vehicle_location 授权
location = await vehicle.vehicle_data(endpoints=["location_data"])
```

返回值通常包含 `response`，不要在没有检查实际结构时硬取字段。
车辆离线时可能得到缓存数据，应查看返回时间戳。位置字段通常在 `drive_state` 中，
不能把 `native_latitude` / `native_longitude` 当作已经转换为某种地图坐标。
SDK 原始账号列表与 MCP 的 VIN 白名单过滤不同；直接使用 SDK 的调用者需要自行限制范围。

## 唤醒与等待

```python
# 发一次唤醒请求后立即返回
result = await vehicle.wake_up(wait=False)

# 或发起唤醒并查询车辆状态，直到上线或超时
# result = await vehicle.wake_up(wait=True, timeout=60)
```

这两个调用是不同用法，不需要先后执行。`wait=True` 通过查询车辆状态等待上线，
不是持续重复发送唤醒请求。等待超时可抛出 `VehicleOffline`。
MCP 的唤醒工具使用 `wait=False`，返回 `accepted` 不能证明车辆已经上线。

## 常见控制方法

| 方法 | 中文作用 | 注意事项 |
|---|---|---|
| `door_lock()` / `door_unlock()` | 锁车 / 解锁 | 属于实际控制，不应自动连续执行测试 |
| `charge_start()` / `charge_stop()` | 开始 / 停止充电 | 车辆可能因连接状态、设定限制等拒绝 |
| `set_charge_limit(80)` | 将充电上限设置为 80% | 应确认车型和当前充电目标 |
| `flash_lights()` | 闪灯 | 不能据此判断其他控制能力都可用 |
| `honk_horn()` | 鸣笛 | 会影响车辆周边环境 |
| `remote_start_drive()` | 远程授权驾驶 | 高风险，不是启动空调，也未开放为本分支 MCP 工具 |

现代车辆的控制通常需要虚拟钥匙与签名，见[签名命令指南](fleet_api_signed_commands.md)。
这里列出的是 SDK 方法，不代表 MCP 服务提供这些工具。

## 异常处理

SDK 的 `TeslaFleetError` 继承 `BaseException`，仅写 `except Exception` 不会捕获它：

```python
from tesla_fleet_api.exceptions import TeslaFleetError

try:
    data = await vehicle.vehicle_data(endpoints=["charge_state"])
except TeslaFleetError:
    print("Tesla 接口调用失败，请检查权限、令牌和车辆状态。")
```

普通参数错误和本地配置错误仍可能是 `ValueError` 等异常；需要时分别捕获。
错误响应和调试日志可能包含隐私，参见[排障指南](troubleshooting.md)。
