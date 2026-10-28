# 车辆蓝牙通信中文指南

[中文目录](README.md) · [英文详细说明与完整方法列表](../bluetooth_vehicles.md)

## 连接前需要准备什么

蓝牙路径通过本机蓝牙适配器或受支持的蓝牙代理与附近车辆通信，并不经过 Fleet API 云端。
它仍然需要正确 VIN、私钥及车辆认可的配对关系，不能用来绕过车辆授权。
蓝牙可用性、系统蓝牙权限和车辆距离需要在实际设备上确认。

## 扫描附近车辆

下面是一个只扫描、不发送车辆命令的完整示例：

```python
import asyncio

import bleak
from tesla_fleet_api import TeslaBluetooth


async def main():
    client = TeslaBluetooth()
    devices = await bleak.BleakScanner.discover()
    for device in devices:
        if client.valid_name(device.name):
            print("发现可能的 Tesla 蓝牙设备：", device.name)


if __name__ == "__main__":
    asyncio.run(main())
```

不要给扫描器设置 Tesla 的 `service_uuids` 过滤条件：车辆通过扫描响应中的 VIN 派生名称
广播，按服务 UUID 过滤可能根本发现不了。扫描到设备也不等于钥匙已经获得车辆授权。

## 创建对象与生命周期

以下是局部片段，在异步函数中使用：

```python
client = TeslaBluetooth()
await client.get_private_key("/absolute/private/path/vehicle-key.pem")
vehicle = client.vehicles.create(
    vin,
    confirmation="verify",
    raise_unconfirmed=True,
    keepalive_interval=None,
)
# 确实需要连接时再调用，完成后断开，避免长期阻止车辆休眠
await vehicle.connect()
try:
    state = await vehicle.vehicle_state()
finally:
    await vehicle.disconnect()
```

SDK 的 `get_private_key` 在文件不存在时会创建新钥匙，创建文件不等于完成配对。
需要新增车辆钥匙时使用 `await vehicle.pair()`，并由车主在车辆端完成确认。
`pair()` 有等待超时与状态轮询，不能在未见确认时盲目重复发送配对操作。

连接默认最多尝试三次；单次连接超时预算约 20 秒，实际总耗时取决于蓝牙环境。
可通过 `await vehicle.connect(max_attempts=4)` 调整次数，但更多尝试也意味着更久等待。
连接失败与命令已经提交后的超时是不同情况。

## 保活会不会影响车辆休眠

`keepalive_interval` 默认约 20 秒，空闲时通过被动 GATT 读取维持已经建立的连接。
`None` 或 `0` 表示关闭。保活读取不会主动唤醒车辆，但持续的连接流量可能延后休眠。
不再需要车辆通信时，关闭保活或断开连接。

## 确认模式与超时

| 配置 | 中文含义 | 适用边界 |
|---|---|---|
| `confirmation="optimistic"` | 乐观模式，减少等待确认 | 写入完成不能证明车辆已执行 |
| `confirmation="ack"` | 默认等待接收确认；锁车/解锁还可用广播确认 | 收不到确认时仍可能无法确定结果 |
| `confirmation="verify"` | 对支持的操作进一步读取目标状态 | 不是所有命令都有可读的状态证明 |
| `raise_unconfirmed=True` | 无法确定执行结果时抛出异常 | 便于调用者停止自动重发 |
| `wake_if_asleep=False` | 禁用默认的休眠车辆信息娱乐命令唤醒处理 | 避免调用者无意触发 SDK 的唤醒后重发流程 |

默认 `raise_unconfirmed=False` 时，无法确定的操作可能按尽力成功返回；
如果需要明确看到这种不确定性，应显式开启它。`verify` 也不能把鸣笛、闪灯、相对音量等
无可靠状态证明的命令变为“保证确认”。休眠情况下的信息娱乐命令有专门的处理规则，
完整确认阶梯见[英文原文](../bluetooth_vehicles.md#the-confirmation-ladder)。

| 异常 | 中文含义 | 处理方向 |
|---|---|---|
| `BluetoothTransportError` | 可证明发生在提交前的连接/传输失败 | 检查蓝牙连接和路径 |
| `BluetoothTimeout` | 等待响应超时；读取和写操作语境不同 | 写操作先确认是否已经执行 |
| `BluetoothUnconfirmedCommand` | 写命令可能已执行，但结果无法确认 | 停止自动重发和云端回退，先核对状态 |
| `BluetoothCommandFailed` | 状态核对证明目标操作未生效 | 检查车辆限制及实际目标状态 |

充电口开启在 `verify` 下还有物理锁扣/盖板确认要求；即便收到接收确认，未确认物理状态时
也可能抛出 `BluetoothUnconfirmedCommand`，不受默认尽力成功策略绕过。
SDK 的签名协议仍可能做有界会话修复，见[签名指南](fleet_api_signed_commands.md)。

## 读取车辆数据

蓝牙单项读取通常返回带类型的 protobuf 对象，和 REST 原始字典不同：

```python
charge = await vehicle.charge_state()
print("电量百分比：", charge.battery_level)
```

常见读取方法包括 `charge_state()`（电量）、`climate_state()`（空调）、
`drive_state()`（驾驶）、`location_state()`（位置）、`closures_state()`（门盖）、
`media_state()`（媒体）、`tire_pressure_state()`（胎压）、`software_update_state()`（软件更新）等。

以下三个名称不能互换：

- `vehicle_state()`：VCSEC 的 `VehicleStatus`。
- `legacy_vehicle_state()`：较早固件的旧版 CarServer 车辆状态。
- `current_vehicle_state()`：当前 CarServer 车辆状态。

`vehicle_data(endpoints)` 可显式指定复合读取，但蓝牙消息大小有限；多组数据组合可能超过 MTU。
优先按需逐项读取，不要直接照搬 REST 的“取所有字段”习惯。

## 导航、空调、充电和车门

蓝牙对象具有导航、行车记录、媒体、低功耗等签名能力；同名接口的参数应对照实际方法签名。
`Seat` 用于 0 起始座位编号，`AutoSeat` 用于 1 起始自动座椅气候编号，二者不能混用。
不同车型的车门关闭机构不相同，不能把单门 open/close 接口理解为保证有电动关门能力。
不要自动执行“开门、检查、再关门恢复”的实验序列。

## 广播监听与只监听模式

`listen_*` 方法可订阅已解码的 VCSEC 状态；`listen_broadcast(domain, callback)` 接收原始域广播。
`listen_connection_status(callback)` 用于连接状态变化通知。
需要取消订阅时按对应监听方法返回的取消函数处理，详见英文监听示例。

`key=False` 明确禁用签名，可用于被动监听；`key=None` 表示尝试继承父对象私钥，
不等于禁用签名。没有私钥的被动客户端不能发送需要签名的控制命令。
广播、连接成功或本机模拟测试都不能证明某个车辆写命令实际执行成功。
