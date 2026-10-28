# Tesla Fleet API CN SDK + MCP Server

**简体中文** | [English / 上游 SDK 英文说明](README.en.md)

基于 Tesla Fleet API 的 Python 开发库，提供车辆与能源设备接口、签名命令、蓝牙通信，以及
本分支新增的中国区适配和独立 MCP Server。你可以在自己的 Python 程序里直接调用 SDK，
也可以让支持 MCP 的 AI 客户端通过受控工具查询或操作车辆。

## 上游来源与致谢

本项目基于 [Teslemetry/python-tesla-fleet-api](https://github.com/Teslemetry/python-tesla-fleet-api)
的分支进行二次开发，主要开展中国区适配与独立 MCP Server 集成，并非从零编写的 SDK。
衷心感谢原作者 **Brett Adams**、Teslemetry 团队及所有上游贡献者的开源工作与持续维护。
保留原项目作者署名、版权声明与 [Apache-2.0 许可证](LICENSE)。本分支不代表原作者、
Teslemetry 或 Tesla 官方的认可、背书及支持承诺。

本分支仅作为**个人技术学习、研究与接口适配实验**项目提供，不承诺生产或商用适用性。
商业使用请遵守原项目许可、Tesla API/开发者服务条款及适用商业协议；商业服务、技术支持
或另行授权请[联系原作者](https://github.com/Teslemetry/python-tesla-fleet-api)
（公开联系邮箱：[hello@teslemetry.com](mailto:hello@teslemetry.com)）。

本项目按现状提供，不提供明示或默示担保。使用者自行评估和承担相关风险；在适用法律允许的
范围内，原作者、上游贡献者与本分支维护者不承担使用或无法使用本项目产生的相关责任。
上述用途说明不替代或撤销已有开源许可授予的权利。请先阅读[完整声明](DISCLAIMER.md)。

## 先看哪份说明

| 你想做什么 | 建议阅读 |
|---|---|
| 查看完整架构、功能清单和代码目录 | [项目架构说明](docs/zh-CN/architecture.md) |
| 第一次使用，不理解 SDK、MCP、Token 等词 | [中文文档导航与术语表](docs/zh-CN/README.md) |
| 接入中国区 Tesla 账号，启动 MCP 服务 | [中国区配置与 MCP 完整说明](docs/cn_mcp_server.md) |
| 用 Python 查询车辆、电量、位置或唤醒车辆 | [车辆接口中文指南](docs/zh-CN/fleet_api_vehicles.md) |
| 理解虚拟钥匙、签名及导航命令 | [签名命令中文指南](docs/zh-CN/fleet_api_signed_commands.md) |
| 在车辆附近通过蓝牙连接 | [蓝牙中文指南](docs/zh-CN/bluetooth_vehicles.md) |
| 查询或设置 Powerwall 等能源设备 | [能源设备中文指南](docs/zh-CN/fleet_api_energy_sites.md) |
| 理解能源网关的局域网控制 | [能源本地控制中文指南](docs/zh-CN/energy_local_control.md) |
| 使用 Teslemetry 或 Tessie | [Teslemetry 中文说明](docs/zh-CN/teslemetry.md) / [Tessie 中文说明](docs/zh-CN/tessie.md) |
| 遇到英文错误提示，不知道怎么处理 | [中文排障与常见问题](docs/zh-CN/troubleshooting.md) |

## 已有能力与中国区验证状态

| 部分 | 提供的能力 | 当前边界 |
|---|---|---|
| 原有 SDK | 车辆、能源设备、签名命令、蓝牙及第三方服务适配 | 不同账号、车型、固件和服务商的支持范围可能不同 |
| 中国区 OAuth | 使用 `region="cn"` 对应的授权与 Token 地址 | 已有离线回归测试，未完成真实账号联调 |
| MCP 查询 | 车辆列表、状态、位置 | VIN 与工具权限白名单；默认不开放位置 |
| MCP 写操作 | 唤醒、单目的地导航 | 默认关闭，启用后仍需本机人工确认 |
| MCP 多途经点 | 透传 SDK 的 `waypoints` 原始字符串 | 实验功能，默认关闭；中国区格式及固件效果待验证 |
| MCP 连接 | Streamable HTTP 与 stdio | 已有本机传输测试；目标客户端尚未实际联调 |

**本分支未进行中国区实车验证。**模拟响应、测试通过或接口确认接收，都不等于车辆已执行成功。
原有 SDK 的能力也不等于已全部开放成 MCP 工具。

## 安装

需要 Python **3.13 或更高版本**。本期 MCP 服务支持 macOS/Linux；SDK 的其他平台支持由其依赖和硬件条件决定。

在本仓库目录内安装，才能使用这里的中国区与 MCP 改动：

```sh
# 安装开发依赖和可选 MCP 服务
uv sync --locked --extra mcp

# 或使用 pip 安装本地项目及 MCP 依赖
pip install '.[mcp]'
```

只需要 Python SDK 时，执行 `pip install .`，无需安装 MCP 依赖。
上游的 `pip install tesla-fleet-api` 安装的是发布到 PyPI 的版本，不保证包含本分支的改动。

## 只想通过 AI 使用车辆工具

推荐从只读配置开始。首次配置流程：

1. 准备中国区开发者应用、已注册的 HTTPS 回调地址及自己的车辆 VIN。
2. 将 `.env.example` 复制为 `.env`，按中文注释填写配置。
3. 在本机完成 Tesla 登录与授权。
4. 启动 MCP 服务，将地址和独立的 MCP 访问密钥配置给客户端。

```sh
cp .env.example .env
chmod 600 .env
# 编辑完成后，在当前终端导入你自己维护的配置
set -a
. ./.env
set +a

# 首次授权；按终端提示在浏览器操作
uv run --extra mcp tesla-cn-mcp login

# 启动 HTTP MCP 服务
uv run --extra mcp tesla-cn-mcp serve --transport streamable-http
```

默认地址为 `http://127.0.0.1:8000/mcp`，每次 HTTP 请求都需要
`Authorization: Bearer <MCP_BEARER_TOKEN>`。MCP 访问密钥必须与 Tesla Token 分开。
`.env` 不会自动加载；占位值需要替换，配置细节、远程 HTTPS 接入、命令确认和 stdio
请继续阅读[中国区 MCP 完整说明](docs/cn_mcp_server.md)。

## 只想用 Python SDK 查询车辆

下面是一个独立的只读示例，从环境变量读取访问令牌和 VIN，不在代码中写入账号密钥。
访问令牌必须来自已授权的中国区应用，且具有相应数据权限。

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
            region="cn",  # 中国区；其他区域不能直接使用中国区凭证
        )
        vehicle = api.vehicles.createFleet(os.environ["TESLA_VIN"])
        try:
            data = await vehicle.vehicle_data(endpoints=["charge_state"])
            # 返回值是接口原始结构；车辆离线时可能返回缓存数据
            print(data)
        except TeslaFleetError:
            print("车辆查询失败，请检查授权、权限和车辆在线状态。")


if __name__ == "__main__":
    asyncio.run(main())
```

`TESLA_ACCESS_TOKEN`、`TESLA_VIN` 是这个 SDK 示例使用的环境变量；MCP 服务读取自己的
令牌文件和 `TESLA_ALLOWED_VINS` 配置，两者不要混淆。直接使用 `TeslaFleetApi` 不会自动替你
刷新 Token；需要自动刷新可使用 `TeslaFleetOAuth`，示例见[车辆指南](docs/zh-CN/fleet_api_vehicles.md)。
不要打印、上传或提交 Token、Secret、私钥及完整授权回调 URL。

## 签名、蓝牙与自动切换怎么理解

- `createFleet(vin)`：通过云端 REST 接口访问车辆。
- `createSigned(vin)`：通过 SDK 的签名协议发送命令，需要匹配的私钥与已授权虚拟钥匙。
- `TeslaBluetooth`：通过附近蓝牙访问车辆，需要蓝牙条件和配对。
- `VehicleRouter`：按顺序尝试多个后端。失败切换可能重复执行已提交的命令，不能理解为“保证只执行一次”。

本分支 MCP 服务不使用 Router/BLE 自动回退，也不会在导航前自动唤醒车辆。
签名协议内部的会话修复沿用 SDK，和服务层的防重复提交不是同一个概念。

## 开发验证

```sh
uv run --extra mcp ruff check tesla_fleet_api mcp_server tests
uv run --extra mcp pyright tesla_fleet_api mcp_server
uv run --extra mcp pytest tests -q
uv build
```

测试可以验证程序逻辑和本地连接，不能替代实车测试。不要使用真实车辆测试来自动执行开锁、
启动车辆、清除信息或其他危险操作。新增中文文档中的方法名和配置键保持原代码名称，
以便复制使用；解释、步骤与注意事项使用简体中文。
