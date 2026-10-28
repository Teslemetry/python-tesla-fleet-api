# 中国区 Tesla Fleet SDK + MCP Server

保留 `tesla_fleet_api` SDK 独立可用，新增可选的 `mcp_server` 服务层。
Python ≥3.13；本期服务支持 macOS/Linux（使用 POSIX 文件权限与进程锁）。
这是**单车主、单 Tesla 账号、单进程**服务，不是多租户平台。共享 MCP Bearer
的客户端共享同一组权限。不能直接当作面向公众的 OAuth 登录服务。

## 已实现与验证边界

| MCP 工具 | SDK 调用 | 权限开关 | 返回说明 |
|---|---|---|---|
| `tesla_list_vehicles(page=1)` | `VehicleFleet.list` | `list_vehicles` | 按页读取后过滤 VIN，仅输出 VIN/名称/在线状态 |
| `tesla_get_vehicle_state(vin)` | `vehicle_data` 指定 charge/climate/vehicle state | `get_vehicle_state` | 电量、充电、温度、锁车、里程、固件及时间戳的正向字段白名单 |
| `tesla_get_location(vin)` | `vehicle_data(endpoints=["location_data"])` | `get_location` | 返回 drive_state 内的位置字段及时间戳，保留 native_type |
| `tesla_wake_vehicle(vin, request_id)` | `wake_up(wait=False)` | `wake_vehicle` + 命令总开关 | 不自动轮询，不代表车辆已上线 |
| `tesla_navigate_to(vin, destination, request_id)` | `VehicleSigned.navigation_request` | `navigate_to` + 命令总开关 | 签名导航文本目的地，不做地理编码 |
| `tesla_navigate_waypoints(vin, waypoints, request_id)` | `VehicleSigned.navigation_waypoints_request` | `navigate_waypoints` + 命令总开关 + 实验开关 | 将 Tesla 兼容的原始字符串交给 SDK |

六个工具均注册，未启用的工具会在调用时拒绝。没有通用 REST 代理或任意命令工具，
没有开锁、启动车辆、擦除数据等高风险能力。本期所有写操作都要求本机人工确认。

已完成的自动测试只验证本地逻辑、模拟 Tesla 响应和真实 MCP 传输，不使用真实账号或车辆。
没有中国区 OAuth 联调、车辆授权、私钥配对或实车测试结果。
`accepted` 只表示接口确认接收；不能作为车辆屏幕已显示路线、已上线或物理执行成功的证据。
状态与位置可能来自缓存；必须查看原始时间戳，不伪造实时坐标、不进行坐标系推断或转换。

## 中国区接口核实（2026-10-28）

依据 [Tesla 区域说明](https://developer.tesla.com/docs/fleet-api/getting-started/regions-countries)，
中国区需中国 Tesla 账号、独立中国区开发者应用及 +86 手机号。
不要拿全球应用凭证直接替代中国区应用。

[中国区第三方令牌文档](https://developer.tesla.cn/docs/fleet-api/authentication/third-party-tokens)
列出 authorize、token 端点以及 Fleet API audience；代码保持以下区域绑定：

- authorize：`https://auth.tesla.cn/oauth2/v3/authorize`
- token（授权码交换、刷新）：`https://auth.tesla.cn/oauth2/v3/token`
- audience/API：`https://fleet-api.prd.cn.vn.cloud.tesla.cn`

OAuth scope 按启用工具申请：基础 `openid offline_access vehicle_device_data`；位置另加
`vehicle_location`；启用命令另加 `vehicle_cmds`。配置权限不能替代 Tesla 实际授权，
共享车辆的隐私限制或用户撤销权限仍由 Tesla 强制执行。变更工具权限后应重新运行 login 授权。
新 refresh token 必须持久化；不能让其他服务同时使用本服务的令牌文件。

[车辆端点](https://developer.tesla.cn/docs/fleet-api/endpoints/vehicle-endpoints)
定义了车辆列表、vehicle_data、wake_up。位置请求使用独立 `location_data`；不自动唤醒。

[中国区车辆指令](https://developer.tesla.cn/docs/fleet-api/endpoints/vehicle-commands)
与[全球车辆指令](https://developer.tesla.com/docs/fleet-api/endpoints/vehicle-commands)
列出了 `navigation_request`、`navigation_gps_request` 和 `navigation_waypoints_request`。
现代车辆通常需要虚拟钥匙和签名。服务直接复用 SDK 的 `createSigned` 和签名协议；
请先按 Tesla 开发者流程注册应用、公钥及车辆虚拟钥匙，不会自动配对或改写钥匙。
本服务不依赖 Go Command Proxy，也不将签名失败降级为未签名重发。

**多途经点限制：**公开端点目录确认接口存在，但本次未获得足以保证中国区车机可接受的
载荷结构、点数上限或固件兼容矩阵。现有 SDK 的参数是原始 `waypoints: str`，服务逐字传递
该参数，最大 16 KiB（本服务限制，不是 Tesla 官方上限）。不要自行假设 `"家,学校,公司"`
或 JSON 地址数组就是有效载荷。需要中国区可用样本后才能提供强类型地点列表转换。
因此该工具默认关闭，属于实验适配入口；不会把多个 GPS 请求串行发送来冒充原子多途经点导航。
[官方 Go 项目讨论](https://github.com/teslamotors/vehicle-command/issues/334)也记录过导航协议兼容问题，
不能把某一代理、SDK 或车辆固件的支持情况泛化到所有中国区车辆。

## 安装与配置

在仓库内：

```sh
uv sync --locked --extra mcp
cp .env.example .env
chmod 600 .env
# 先编辑 .env；仅对自己维护的本地配置执行以下导入：
set -a
. ./.env
set +a
```

仅使用 SDK 无需安装 MCP：`pip install .`。安装 MCP 服务：`pip install '.[mcp]'`。
SDK 模块不导入 `mcp_server`，也不要求 MCP 依赖。

必须填写中国区应用 ID、Secret、已注册 HTTPS 回调地址、显式 VIN 白名单和绝对状态目录。
VIN 使用大写 17 位格式，不支持通配符。默认权限仅包含车辆列表和不含位置的状态。
同一账号内未授权给 MCP 的其他 VIN 会在列表结果中被过滤。

状态目录首次自动以 0700 创建；现有目录若权限过宽则拒绝使用。令牌、命令记录以 0600
临时文件写入并原子替换、同步落盘。父目录与宿主机也应由操作者控制。
令牌文件是明文私密文件，应放在受保护磁盘，避免同步盘、公开目录和不受控备份。
单个目录只允许一个服务或 login 进程持有租约；approve 使用独立短锁。
使用不同状态目录启动多个实例不在本期去重与刷新保护范围内。

## OAuth 登录

```sh
uv run --extra mcp tesla-cn-mcp login
```

终端输出 Tesla 授权链接，使用浏览器登录并同意权限。将最终完整回调 URL 粘贴回本机终端
（隐藏输入，不写 shell 历史）。回调页可以由已有 HTTPS 应用提供，服务不会监听该地址。
本地检查 scheme/host/path、随机 state、单个 code 和 10 分钟有效期，随后通过现有 SDK 交换令牌。
OAuth 登录没有 MCP 工具入口；Secret、授权码与 Tesla token 不应进入模型对话。
随机 state 仅对这次进程有效，失败后重新运行 login，不复用链接。

服务提前 60 秒刷新过期令牌，进程内序列化刷新并立即保存轮换令牌。
持久化失败会阻止继续取 token，避免继续使用无法恢复的轮换状态。
失效、撤销授权、密码变更或刷新失败时由本机操作者停止服务后重新 login。
没有遇到 401 后重发车辆写请求的逻辑。

## Streamable HTTP

```sh
# MCP_BEARER_TOKEN 使用独立随机值，不可填写 Tesla access/refresh token。
uv run --extra mcp tesla-cn-mcp serve --transport streamable-http
```

地址：`http://127.0.0.1:8000/mcp`。每个 HTTP 请求（包括初始化、列工具、调用、DELETE）
都必须带 `Authorization: Bearer <MCP_BEARER_TOKEN>`，Bearer 至少 32 位 ASCII 无空白。
服务固定绑定回环地址，启用 Host/Origin 防护，关闭 HTTP 访问日志，最大请求体 64 KiB。
默认无 SSE 旧传输入口；Streamable HTTP 使用官方 MCP Python SDK v1 的无状态 JSON 模式。

小智 AI、Microsoft Agent Framework 或其他客户端需支持 **Streamable HTTP + 自定义
Authorization Header**，配置上述 URL 和 Bearer。客户端产品的具体接入配置尚未联调。
本期不提供 OAuth 自动发现/动态注册；仅支持 OAuth 接入的客户端需要额外网关适配。

远程接入应在受控网关反向代理并终止 HTTPS，保留 Authorization，转发到回环地址，
将上游 Host 设置为 `127.0.0.1:8000`（端口与 MCP_PORT 一致），关闭请求头与请求体敏感日志。
不能把 Bearer 放在 URL。浏览器来源默认只允许本机 Origin；远程浏览器来源需经过单独的
信任配置设计，不能为方便接入关闭 Origin 检查。共享 Bearer 并不提供按用户隔离。
本次未部署远程代理或公网服务。

## stdio

```sh
uv run --extra mcp tesla-cn-mcp serve --transport stdio
```

或在本机 MCP 客户端的配置中使用：

```json
{
  "mcpServers": {
    "tesla-cn": {
      "command": "/absolute/path/to/repository/.venv/bin/tesla-cn-mcp",
      "args": ["serve", "--transport", "stdio"],
      "env": {
        "TESLA_REGION": "cn",
        "TESLA_CLIENT_ID": "your-cn-client-id",
        "TESLA_ALLOWED_VINS": "YOUR_17_CHARACTER_VIN",
        "TESLA_STATE_DIR": "/absolute/private/path/tesla-mcp-state",
        "TESLA_TOOLS": "list_vehicles,get_vehicle_state"
      }
    }
  }
}
```

登录使用同一目录后，serve 不再需要 Secret。stdio 信任本机用户与启动它的客户端，
通过进程和文件权限控制访问，不使用 HTTP Bearer。日志写 stderr，stdout 留给 MCP。
不要把状态目录或本机 approve 命令权限授予不可信客户端。

## 启用命令与本机确认

按需把工具名加到 `TESLA_TOOLS`，例如
`list_vehicles,get_vehicle_state,get_location,wake_vehicle,navigate_to`，同时配置
`TESLA_ENABLE_COMMANDS=true`。导航还需 `TESLA_PRIVATE_KEY` 指向已有的 0600 P-256 私钥。
该钥匙必须已在 Tesla 应用/车辆完成注册，服务不会创建新的配对钥匙。
实验多途经点工具另需 `TESLA_ENABLE_WAYPOINTS=true`。
改完配置后重新授权 scope、重启服务。

1. 客户端第一次调用命令，传入稳定的 `request_id`（16–128 位字母/数字/下划线/短横线），
   例如 `tesla_navigate_to` 的参数：

   ```json
   {"vin":"YOUR_17_CHARACTER_VIN","destination":"上海市人民广场","request_id":"nav-request-20261028-0001"}
   ```

   返回 `pending`，此时没有发送车辆命令。
2. 操作者在同一台机器、相同状态目录的独立终端运行：

   ```sh
   uv run --extra mcp tesla-cn-mcp approve nav-request-20261028-0001
   ```

   阅读 VIN、区域、应用和完整命令参数后输入 `APPROVE`。确认不能由模型传一个布尔值绕过。
   不要自动化执行 approve。只对自己明确想执行的请求确认。
3. 客户端在原始准备时间起 **300 秒内**重复完全相同的工具、VIN、参数及 request_id，
   才会执行一次 SDK 调用。改动参数、超时或未确认均不执行。

命令状态为 `pending / approved / expired / accepted / rejected / unknown`。
执行前先持久化 `reserved`；进程崩溃、任务取消或交付超时后保留不确定状态。
同一 request_id 永久绑定原始参数并禁止重放；相同载荷即使用新 ID，在原准备的 300 秒
窗口内也会指向原记录，不创建第二次提交。过了窗口，新 ID 属于新的独立请求，仍需新的人工确认。
不能在未知结果时用新 ID 盲目再试，必须先人工核对车辆。SDK 内部签名协议的会话修复与
故障处理沿用上游实现；本服务保证的是提交记录与单次 SDK 调用边界，不宣称车辆端恰好执行一次。
不使用 Router/BLE 故障切换，不自动唤醒后再发送导航。

命令记录持久保存完整参数，便于本机确认，可能包含隐私地址。最多 10,000 条后拒绝新请求；
不自动删除去重记录。归档/清空只能在服务停止后由操作者进行，移除记录会同时移除历史去重保护。
服务层错误只返回固定安全消息，不转发 Tesla 原始错误体，默认禁止 SDK DEBUG 日志。
CLI 失败显示错误类型；排障时先检查环境配置、文件权限、登录状态及本机待确认记录，
不要以打开敏感 HTTP 日志或复制 token 到聊天作为排障方式。

## 开发验证

```sh
uv sync --locked --extra mcp
uv run --extra mcp ruff check tesla_fleet_api mcp_server tests
uv run --extra mcp pyright tesla_fleet_api mcp_server
uv run --extra mcp pytest tests -q
uv build
```

测试包含 SDK 原有测试、CN OAuth 回归、权限/确认/去重/轮换令牌、内存 MCP，以及本机真实
TCP Streamable HTTP 和 stdio 子进程的初始化、列工具与权限拒绝。传输测试使用模拟 SDK；
CI 安装 MCP extra，纯 SDK 环境跳过依赖 MCP 的传输测试。

仍需操作者使用实际中国区账号与车辆核验：应用审核和账号可用性、回调注册、scope 同意、
令牌首次交换及轮换、共享车定位权限、车型/固件差异、虚拟钥匙签名、休眠与唤醒、
单目的地识别、多途经点合法载荷/顺序/上限/屏幕效果，以及目标客户端接入。
未实车核验前不将“模拟响应通过”描述为“中国区实车支持”。
