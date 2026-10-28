# 中文排障与常见问题

[中文目录](README.md) · [中国区 MCP 配置](../cn_mcp_server.md)

## 安装和启动

| 现象 | 中文含义和检查方向 |
|---|---|
| 找不到 `uv` | 当前系统尚未配置该工具；也可按首页用 pip 安装项目 |
| `requires-python >=3.13` | 当前 Python 版本不满足要求，需要 3.13 或更高版本 |
| `No module named mcp` | 只装了 SDK，尚未装 MCP extra；在仓库执行 `uv sync --locked --extra mcp` |
| 找不到 `tesla-cn-mcp` | 当前终端没有使用项目环境；使用 `uv run --extra mcp tesla-cn-mcp ...` |
| 修改 `.env` 后没有变化 | 服务不自动加载 `.env`；导入配置并重启服务 |
| `Operation stopped (...)` | 本机命令已停止；括号里是错误类型，服务刻意不输出敏感响应 |
| `BlockingIOError` | 相同状态目录已有服务或 login 进程持有锁；先检查已有进程 |

不要同时用多个状态目录复用同一套轮换令牌。MCP 服务使用 macOS/Linux 的进程锁和文件权限，
本期不承诺 Windows 原生运行。

## OAuth 和 Token

| 现象 | 说明 |
|---|---|
| 授权失败或拿不到车辆 | 检查区域、开发者应用、回调注册、账号和实际授予的范围 |
| `OAuth state invalid or expired` | 回调校验值不匹配或已超时；重新开始一次登录，不复用旧链接 |
| `Callback URL does not match registered redirect` | 粘贴的回调地址与配置中的 scheme/host/path 不符 |
| `OAuth code exchange failed` | 授权码交换失败，检查授权码有效性和应用配置 |
| `OAuth token refresh failed` | 刷新失败；可能需要重新授权，不要靠重发车辆命令处理 |
| `Stored tokens belong to another region/application` | 当前状态目录保存的凭证属于另一区域或应用 |
| `Token persistence failed` | 轮换后的凭证没能保存，应停止服务，修复存储并恢复授权 |

MCP 登录成功后可在同一私密目录启动服务，不需要把 Token 复制进 AI 对话。
不要把账户密码当作 Client Secret，或者把 `MCP_BEARER_TOKEN` 当作 Tesla Access Token。
独立使用 SDK 时，回调校验和令牌持久化由调用者负责。

## HTTP 和权限

| 返回或提示 | 中文含义 |
|---|---|
| HTTP `401 Unauthorized` | MCP Bearer 缺失或不匹配；检查请求头，不是让你把 Tesla Token 放进去 |
| HTTP `421` | 请求的 Host 不在允许范围内 |
| HTTP `403` | 可能是 Origin 检查拒绝；如果来自 Tesla API，则还要检查其账号和 scope 权限 |
| `Tool permission is disabled` | `TESLA_TOOLS` 没有放行该工具 |
| `Vehicle is not allowed` | VIN 格式不符，或不在 `TESLA_ALLOWED_VINS` 中 |
| `Vehicle commands are disabled` | 写操作总开关未开启 |
| `Experimental waypoint navigation is disabled` | 多途经点实验开关未开启 |
| `Location is unavailable` | 没有可用定位数据；检查位置权限、共享车隐私设置及车辆状态 |

`TESLA_TOOLS` 使用的是 `list_vehicles` 等配置名，MCP 客户端看到的是
`tesla_list_vehicles` 等工具名，两组名称不同。配置总开关使用小写 `true`。
修改配置需要重启；新增权限还可能需要重新进行 Tesla 授权。

## 命令返回状态的中文对照

| 状态 | 含义 | 下一步 |
|---|---|---|
| `pending` | 待本机人工确认，尚未发命令 | 操作者核对后使用本机 `approve` |
| `approved` | 已批准，但还没有提交该次执行 | 在原有效期内重复完全相同的原请求 |
| `expired` | 原始请求的确认窗口已过期 | 核实仍有操作需要后重新发起和人工确认 |
| `accepted` | 接口确认接收 | 按需核对车辆实际状态，不当作物理执行证明 |
| `rejected` | 返回明确拒绝 | 检查车辆限制，不自动循环重试 |
| `unknown` | 已保留提交记录，但无法确认最终结果 | 先核对车辆，不换新 ID 盲目重发 |

`request_id` 是本次操作的稳定编号，不是每次重试都换一个随机数。
相同 ID 改参数会被拒绝；相同载荷在原 300 秒窗口内换 ID，也会指向已有记录。
记录持久保留；清理记录会同时清理历史防重放保护，不能为了“让它再发一次”随便删除文件。
`reserved` 是内部提交前状态；进程中断后会被当作结果未知处理。

## 私钥与蓝牙错误

| 提示 | 中文含义 |
|---|---|
| `PrivateKeyError` / `unreadable` | 私钥无法读取 |
| `malformed` | 文件不是合法的预期私钥格式 |
| `encrypted` | 文件已加密，当前加载方式不支持 |
| `wrong_type` | 私钥类型与所需 EC/RSA 不匹配 |
| `No private key` | 未给签名客户端提供可用私钥 |
| `BluetoothUnconfirmedCommand` | 命令可能已经执行，停止自动回退和重发 |
| `SignedCommandRequired` | 当前路径无法提供要求的有效签名，尤其要注意能源离网控制 |

`PrivateKeyError` 属于本地 `LibraryError`，与 `TeslaFleetError` 不是相同错误分支。
`TeslaFleetError` 继承 `BaseException`，需要显式捕获。
完整蓝牙确认规则见[蓝牙指南](bluetooth_vehicles.md)。

## 如何看调试日志

SDK 的 `DEBUG` 日志可显示命令、传输路径及部分请求/响应，但也可能包含敏感参数。
本分支 MCP 默认将 `tesla_fleet_api` 日志限制为 `WARNING`，并关闭 HTTP 访问日志。
普通使用先查配置、时间戳、权限和本机记录，不需要开启全量调试。
确需单独调试 SDK 时，可在自己控制的本机环境设置日志，保存或分享前删除 Token、位置、VIN 等敏感信息。

| 日志字段 | 中文解释 |
|---|---|
| `command=vehicle_data` | 当前请求是读取车辆数据 |
| `transport=fleet` | 走 Tesla 云端 Fleet 接口 |
| `transport=bluetooth` | 走蓝牙 |
| `transport=teslemetry` / `tessie` | 走对应第三方服务 |
| `backend=...` | 路由当前尝试的后端类型 |
| `result=success` / `True` | 本次接口/协议调用报告成功，不代表全部车辆动作都已核实 |
| `reason=...` | 原始原因字段，具体解释取决于接口 |

如果还有问题，记录工具名、操作时间、错误类型和不含隐私的复现步骤。
提供排障信息时不要发送私钥、Secret、Token 或完整 OAuth 回调 URL。
