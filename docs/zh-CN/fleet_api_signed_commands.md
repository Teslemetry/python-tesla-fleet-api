# 车辆签名命令中文指南

[中文目录](README.md) · [英文详细示例](../fleet_api_signed_commands.md)

## 为什么有 Token 还需要钥匙

Token 用于证明账号授权，签名私钥用于证明车辆认可的应用钥匙身份。
两者作用不同。通过 OAuth 获得权限，不等于车辆已经安装了应用的虚拟钥匙。
本指南解释 SDK 能力；具体中国区应用与钥匙注册条件见[中国区说明](../cn_mcp_server.md)。

## 创建签名车辆对象

以下片段在已创建 `api` 的异步函数里使用：

```python
# SDK 会加载现有 EC 私钥；路径不存在时会创建新私钥。
# 新私钥并不会自动取得车辆权限，不能替换已注册的钥匙。
await api.get_private_key("/absolute/private/path/vehicle-key.pem")
vehicle = api.vehicles.createSigned(vin)
await vehicle.handshakeInfotainment()  # 信息娱乐域，导航等操作使用此域
```

私钥要先于 `createSigned` 加载。当前代码按域提供 `handshakeVehicleSecurity()`（车辆安全）
和 `handshakeInfotainment()`（信息娱乐），签名调用也会在会话未就绪时自动握手；
不要照搬旧示例中的通用 `handshake()` 名称。不可读取、加密、格式错误或类型不匹配的现有钥匙会产生
`PrivateKeyError`，不要通过删除并重建文件来“修复”已经配对的钥匙。
MCP 服务要求使用已有私钥文件，不会在启动时替你创建配对钥匙。

## 支持的操作类型

| 类型 | 方法示例 | 中文解释 |
|---|---|---|
| 锁车 | `door_lock()` / `door_unlock()` | 改变车门锁定状态 |
| 充电 | `charge_start()` / `charge_stop()` | 开始或停止充电 |
| 充电设定 | `set_charge_limit(percent)`、`set_charging_amps(charging_amps)` | 电量上限与充电电流 |
| 充电模式 | `charge_standard()` / `charge_max_range()` | 标准或最大续航模式 |
| 空调 | `auto_conditioning_start()` / `auto_conditioning_stop()`、`set_temps(...)` | 预调节与温度设定 |
| 导航 | `navigation_request(value)` | 发送一个文本目的地 |
| 坐标导航 | `navigation_gps_request(lat, lon, order=0)` | 按经纬度和顺序参数发送导航 |
| 多途经点 | `navigation_waypoints_request(waypoints)` | 发送 Tesla 兼容的原始字符串 |
| 其他 | `flash_lights()`、`honk_horn()`、`dashcam_save_clip()` | 闪灯、鸣笛、保存行车记录片段 |
| 图像 | `vehicle_image_state(image_type, chunk_size=16384)` | 分页取得车辆渲染图像字节 |

方法存在不表示当前车辆、固件或地区一定接受。请按实际需求单独调用，不要把控制方法串成自动测试脚本。

## 导航参数怎么理解

```python
# 局部片段：只在确认目的地且车辆允许操作时执行
result = await vehicle.navigation_request("上海市人民广场")
```

`navigation_gps_request` 的 `order` 使用整数：`1` 替换路线、`2` 前插站点、`3` 追加站点，
默认 `0` 是协议的未知顺序值。不要用字符串或自己构造枚举包装器代替整数。
多次 GPS 调用不等于一个原子多途经点操作；中途失败可能只保留部分站点。

`navigation_waypoints_request` 目前接收字符串，而不是 Python 地址列表。本分支未确认
中国区有效载荷结构和固件兼容矩阵；不能声称把 `家,学校,公司` 拼起来就能使用。
MCP 的多途经点入口默认关闭，详细限制见[中国区说明](../cn_mcp_server.md)。

## 重试与结果确认

SDK 可能在 WAIT、epoch 或 Token 协议故障后重新签名并有限次重发。
这不保证物理动作恰好执行一次。切换播放、相对音量、增删日程等操作可能重复产生影响，
应检查绝对状态，不依赖“调用次数”推断执行结果。

`adjust_volume(volume)` 的绝对音量范围为 `0.0` 到 `11.0`，不是通常想象的 0–100。
`charge_standard()` 已经处于标准模式时，车辆可能返回 `already_standard`，而不是无操作成功。

充电日程和出发日程共用 `scheduled_charging_mode`，修改一项可能影响另一项。
需要保留原计划时先读取 `charge_state()`，记录原模式和字段，再设计恢复逻辑。
远程舒适设置关闭时，空调或加热操作可能被拒绝，不能仅靠重复请求解决。

## 图像与遥测配置

`VehicleImageType.AUTOPILOT_VISUALIZATION_WRAP` 和 `VehicleImageType.LICENSE_PLATE`
用于选择图像类型；`vehicle_image_state` 返回拼接后的 `bytes`，分块大小必须是正整数。

签名车辆还提供 `fleet_telemetry_config_create(config)`，复用 SDK 的 JWS 签名实现。
它与读取车辆当前状态不同，不应为了“试接口”覆盖已有遥测配置。
签名密钥和日志处理说明见[排障指南](troubleshooting.md)。
