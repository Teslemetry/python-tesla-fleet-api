# 能源网关本地控制中文指南

[中文目录](README.md) · [英文完整流程](../energy_local_control.md)

## 本地控制与云端控制有什么区别

云端路径通过 Tesla/Teslemetry 服务访问能源站；本地路径通过局域网访问能源网关。
上游说明使用独立的 `aiopowerwall` 包作为本地适配器，再由 `EnergySiteRouter` 组合本地与云端。
本仓库不自动安装该第三方包，也没有在本分支验证这套方案在中国区设备上的兼容性。

## 配置顺序

1. 生成或加载 RSA 私钥。
2. 通过支持的云端授权接口注册其公钥。
3. 由设备持有人按网关要求完成现场确认。
4. 等待授权状态变为可用；有本地连接时再用签名读取确认。
5. 把同一份私钥提供给本地适配器，再按需求组合路由。

这是一套设备配对过程，不能只靠创建私钥文件或获得 HTTP 成功响应就判定完成。
物理操作应遵循设备操作说明，由具备相应条件的人执行；本文不提供断电或开关断路器的自动化步骤。

## RSA 私钥与车辆私钥不要混淆

车辆签名通常使用 EC 私钥，网关 LAN TEDapi v1r 路径使用 RSA。
`get_rsa_private_key(path)` 加载现有 RSA 私钥，缺失时创建新钥匙；
默认新密钥生成尽量不阻塞异步循环，已有钥匙有一致性检查。
只有明确知道现有钥匙可信时才考虑跳过昂贵检查，不要为了排障随意关闭验证。

```python
# 局部片段：api 为已创建的、支持此流程的 Teslemetry 客户端
await api.get_rsa_private_key("/absolute/private/path/tedapi_rsa_private.pem")
site = api.energySites.create(energy_site_id)
# 注册会改变设备授权状态，只在本人明确需要配对时调用：
# await site.add_authorized_client(
#     api.rsa_public_der_pkcs1_b64,
#     description="个人研究客户端",
# )
```

同一个私钥文件后续交给本地适配器，不能注册一份公钥却用另一份私钥通信。
网关本地密码也不是 Tesla 账号密码。

## 配对状态的中文含义

| 状态 | 含义 |
|---|---|
| `PENDING_VERIFICATION` | 已注册，等待现场验证 |
| `PENDING_VERIFICATION_TIMEOUT` | 验证窗口已过期，属于终止状态 |
| `VERIFIED` | 网关报告已验证 |
| `REMOVED` | 已移除 |
| `INVALID` 或未知状态 | 不应当作已验证 |

Teslemetry 的 `wait_until_paired()` 提供有界等待流程；原始客户端列表只可作为状态信号，
不能把空响应、空列表或无法解析的数据都解释为“还没配对”。
`live_status()` 的成功本地签名读取可以进一步验证钥匙确实能通信。
本地适配器未实现的 `get_system_info()` 等方法不能拿来代替这个测试。

## 发现网关地址

`find_gateway_address()` 是 Teslemetry 能源站的辅助方法，会解析以太网或 Wi-Fi 的 IPv4 地址，
不把蜂窝网络当作局域网。没有可用地址可返回 `None`；结构不合法应产生 `InvalidResponse`。
不能把网关的示例地址或其他人的 IP 写死为自己的设备地址。

## 本地优先、云端回退

```python
from tesla_fleet_api.router import EnergySiteRouter

# 局部片段：两种站点对象由调用方预先完成创建、授权和连接
router = EnergySiteRouter(local_energysite, cloud_energysite)
status = await router.live_status()
```

路由返回某一个后端的完整响应，不会自动混合两个来源的数据。
本地未实现的方法可能回退到云端。写操作中途失败也可能引起重复提交，
不能因为使用 Router 就认为它具备事务或恰好一次执行保证。

`health` 判断只影响第一个后端，不是每个后端各自的健康检查表。
`on_result(exception, backend, method_name)` 可观察成功或失败，按实际需求阻止某些失败后的回退。
`async with Router(...)` 不会替你管理后端的蓝牙或网关连接生命周期。

## 需要合并本地和云端数据时

```python
from tesla_fleet_api.router.energysite import merge_live_status, merge_site_info

# 局部片段：cloud_status / local_status 是调用者分别读取的返回值
merged_status = merge_live_status(cloud_status, local_status)
merged_info = merge_site_info(cloud_info, local_info)
```

合并函数只覆盖其负责且确实出现在本地响应中的字段，不是任意字典拼接；
本地读取整体失败并以 `None` 传入时保留云端结果。
本地明确给出的 `None` 与本地根本没有该字段并非同一语义，不能擅自用真值判断统一替换。

离网/并网接触器控制尤其不能只看返回值：云端路径会抛出 `SignedCommandRequired`，
本地签名路径也可能受固件影响而只确认、不执行。必须按设备状态核验，不能依赖自动重发推断成功。
