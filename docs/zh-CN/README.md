# 简体中文文档导航

[返回项目首页](../../README.md) · [英文文档入口](../../README.en.md)

这里提供与本仓库实现对应的中文使用指南，按实际使用流程重新组织，不是逐行翻译。
英文详细示例仍然保留；方法名、环境变量和返回字段继续使用代码中的原始名称，避免复制后无法运行。
中国区接口的外部使用条件与尚未验证项集中列在[中国区 MCP 说明](../cn_mcp_server.md)，不要把上游其他地区的经验当作中国区实车结论。

## 阅读顺序

1. [项目首页](../../README.md)：了解项目、安装方式、只读示例和使用边界。
2. [车辆接口](fleet_api_vehicles.md)：了解授权、车辆列表、数据、定位和唤醒。
3. [中国区 MCP 服务](../cn_mcp_server.md)：配置 AI 接入、权限及人工确认。
4. 需要进一步开发时再看[签名命令](fleet_api_signed_commands.md)和[蓝牙通信](bluetooth_vehicles.md)。
5. 接入能源设备或第三方服务时，看下表对应页面。

## 文档目录

| 中文主题 | 对应英文详细文档 |
|---|---|
| [车辆接口](fleet_api_vehicles.md) | [Fleet API for Vehicles](../fleet_api_vehicles.md) |
| [签名命令](fleet_api_signed_commands.md) | [Signed Vehicle Commands](../fleet_api_signed_commands.md) |
| [蓝牙通信](bluetooth_vehicles.md) | [Bluetooth for Vehicles](../bluetooth_vehicles.md) |
| [能源设备](fleet_api_energy_sites.md) | [Fleet API for Energy Sites](../fleet_api_energy_sites.md) |
| [能源本地控制](energy_local_control.md) | [Energy Local Control](../energy_local_control.md) |
| [Teslemetry 服务](teslemetry.md) | [Teslemetry](../teslemetry.md) |
| [Tessie 服务](tessie.md) | [Tessie](../tessie.md) |
| [排障和常见问题](troubleshooting.md) | 结合本仓库异常类型、MCP 提示和配置整理 |

## 常用英文术语

| 名称 | 中文含义 | 在本项目中的用途 |
|---|---|---|
| SDK | 软件开发工具包 | 在 Python 程序里调用车辆和设备接口 |
| MCP Server | MCP 工具服务 | 把受控能力提供给 AI 客户端 |
| Fleet API | Tesla 车队接口 | 访问 Tesla 云端数据及命令 |
| OAuth | 用户授权流程 | 用户在 Tesla 页面登录，允许应用获得指定权限 |
| Client ID / Client Secret | 应用标识 / 应用密钥 | 来自开发者应用；不是车主账号密码 |
| Access Token | 访问令牌 | 调用接口时使用，有有效期 |
| Refresh Token | 刷新令牌 | 交换新的访问令牌；轮换后要保存新值 |
| Scope | 授权范围 | 如车辆数据、定位、车辆命令等权限 |
| VIN | 车辆识别代号 | 用于指定车辆，通常为 17 位字符 |
| Region | 服务区域 | `cn` 中国区、`na` 北美及部分亚太、`eu` 欧洲等区域 |
| Virtual Key | 虚拟钥匙 | 让车辆认可应用的命令签名公钥 |
| Private Key | 私钥 | 用于签名，只能保存在受保护的本机位置 |
| BLE | 低功耗蓝牙 | 在车辆附近直接通信 |
| REST | HTTP 接口调用方式 | SDK 云端接口使用的形式 |
| Streamable HTTP | MCP 的 HTTP 传输方式 | 本项目 HTTP MCP 接入方式 |
| stdio | 标准输入输出传输 | MCP 客户端在本机启动服务子进程 |
| Bearer | 请求头携带访问凭据的方式 | HTTP MCP 使用独立 Bearer，不使用 Tesla Token |
| ACK | 接收确认 | 不一定等于物理动作已完成 |
| Retry / Failover | 重试 / 故障切换 | 结果不明确时可能导致同一动作重复执行 |
| Idempotency | 幂等性 | 重复相同请求是否会产生额外影响 |
| Cache / Timestamp | 缓存 / 时间戳 | 判断拿到的数据是否足够新 |

## 配置名称怎么看

`.env.example` 的注释已提供中文说明。主要开关如下：

| 配置 | 中文含义 |
|---|---|
| `TESLA_REGION` | 账号与应用所属区域，本分支默认 `cn` |
| `TESLA_CLIENT_ID` / `TESLA_CLIENT_SECRET` | 开发者应用的标识与密钥 |
| `TESLA_REDIRECT_URI` | 已注册的 HTTPS 授权回调地址 |
| `TESLA_ALLOWED_VINS` | 允许 MCP 访问的车辆 VIN，逗号分隔 |
| `TESLA_STATE_DIR` | 保存授权令牌和命令确认记录的私密目录 |
| `TESLA_TOOLS` | 允许调用的工具名称，逗号分隔 |
| `TESLA_ENABLE_COMMANDS` | 写操作总开关，只有精确值 `true` 才启用 |
| `TESLA_ENABLE_WAYPOINTS` | 多途经点实验功能开关 |
| `TESLA_PRIVATE_KEY` | 已注册签名私钥文件的路径 |
| `MCP_PORT` | 本机 HTTP 服务端口，默认 8000 |
| `MCP_BEARER_TOKEN` | AI 客户端访问 MCP 的独立密钥 |

说明文档不会替代[原许可证](../../LICENSE)或[风险声明](../../DISCLAIMER.md)。
