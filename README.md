# DolphinDB FtpClient Plugin

ftpClient 是 DolphinDB 的 FTP 网络交互插件，底层基于 `libcurl` 实现。它为 DolphinDB 提供了强大的 FTP 文件传输能力，支持断点续传、目录递归同步及流式文件传输。

主要特性包括：
*   **全功能支持**：支持 FTP、FTPS（隐式/显式）。
*   **高性能 I/O**：支持流式文件上传与下载，极低内存占用。
*   **断点续传**：下载时自动检测本地文件大小，支持断点续传，跳过已完成文件。
*   **递归同步**：支持目录级递归下载，自动保留目录结构。
*   **兼容性**：自动处理 URL 编码及 Windows 中文路径乱码问题。
*   **智能编码兼容**：全函数支持 URL 自动编码（自动处理空格及中文路径）。
*   **跨平台路径支持**：在 Windows 环境下，自动处理本地中文文件名的编码转换（UTF-8 转 ANSI），彻底解决“找不到文件”或文件名乱码问题。

---

## 在插件市场安装插件
### 版本要求
- DolphinDB Server 3.00.4 及更高版本。
- 支持 Linux x64 和 Windows x64。
### 安装步骤
1. 在 DolphinDB 客户端中使用 `listRemotePlugins` 命令查看插件仓库中的插件信息。
```
login("admin", "123456")
listRemotePlugins()
```

2. 使用 `installPlugin` 完成安装。
```
installPlugin("ftpClient")
```
3. 使用 `loadPlugin` 加载插件。
```
loadPlugin("ftpClient")
```
## 接口说明
所有函数均定义在 `ftpClient` 命名空间下。

### ftpList
#### 语法
```
ftpClient::ftpList(url, [user], [password], [timeout])
```
#### 详情
列出 FTP 服务器指定目录下的文件信息。

注意：本函数支持智能 URL 编码。您可以直接传入包含中文或空格的路径（如 ftp://host/测试 目录/），插件会自动将其转换为符合标准的编码格式。
#### 参数
**url** 字符串。FTP 目录地址，建议以 / 结尾。例如 ftp://127.0.0.1:2121/data/。

**user** 字符串（可选）。用户名，默认为空。

**password** 字符串（可选）。密码，默认为空。

**timeout** 数值（可选）。超时时间（秒），默认 30.0。

#### 返回值
返回一个表（Table），包含以下列：
- filename：STRING，文件名
- isDir：BOOL，是否为目录
- size：LONG，文件大小（字节）
- lastModified：STRING，修改时间（依赖服务器 MLSD 支持，否则可能仅精确到分钟或日期）
#### 示例
```
url = "ftp://127.0.0.1:2121/"
// 列出根目录下所有的文件（不含子目录）
t = ftpClient::ftpList(url, "anonymous", "anonymous")
select * from t where isDir=false
```


### ftpUpload

#### 语法
```
ftpClient::ftpUpload(url, data, [user], [password], [timeout])
```
#### 详情
将内存中的数据（字符串或 Blob）直接上传到 FTP 服务器。适用于上传小文件或动态生成的文本。
#### 参数
**url** 字符串。完整的目标路径，必须包含文件名。例如 ftp://host/upload/data.csv。

**data** 字符串或 Blob。需要上传的数据内容。

**user** 字符串（可选）。用户名，默认为空。

**password** 字符串（可选）。密码，默认为空。

**timeout** 数值（可选）。超时时间（秒），默认 30.0。
#### 返回值
VOID。如果上传失败会抛出异常。
#### 示例
```
data = "id,value\n1,100\n2,200"
ftpClient::ftpUpload("ftp://127.0.0.1:2121/test.csv", data, "anonymous", "anonymous")
```
## ftpUploadFile

#### 语法
```
ftpClient::ftpUploadFile(url, localFile, [user], [password], [timeout])
```
#### 详情
将本地磁盘文件上传到 FTP 服务器。采用流式传输，内存占用极低，适合上传大文件。注意目前不支持上传 2GB 以上文件。
#### 参数
**url** 字符串。完整的目标路径，必须包含文件名。

**localFile** 字符串。本地文件的绝对路径。支持 Windows 路径（如 D:/data/file.zip）。
   - Windows 特性：支持包含中文的路径（如 D:/数据备份/2023年.zip），插件会自动处理编码转换，无需用户手动转码。

**user** 字符串（可选）。用户名，默认为空。

**password** 字符串（可选）。密码，默认为空。

**timeout** 数值（可选）。超时时间（秒），默认 30.0。
#### 返回值
VOID。如果文件不存在或上传中断会抛出异常。
#### 示例
```
localFile = "D:/data/large_backup.zip"
targetUrl = "ftp://127.0.0.1:2121/backup/large_backup.zip"
ftpClient::ftpUploadFile(targetUrl, localFile, "anonymous", "anonymous", 300)
```

### ftpDownloadDir

#### 语法
```
ftpClient::ftpDownloadDir(url, localDir, [user], [password], [timeout])
```
#### 详情
功能强大的通用下载函数。支持下载单个文件或递归下载整个目录，并内置断点续传机制。核心特性如下：
 - 自动探测：插件会自动判断 *url* 是文件还是目录，无需手动指定。
 - 断点续传与增量同步：
   - 跳过：如果本地文件大小等于远程文件大小，视为已完成，直接跳过（节省带宽）。
   - 续传：如果本地文件大小小于远程文件大小，从断点处继续下载（追加模式）。
   - 覆盖：如果本地文件大小大于远程文件大小，视为异常，覆盖重新下载。
- 智能编码处理：
   - 自动处理 *URL* 中的特殊字符（如空格转义为 %20）。
   - 在 Windows 环境下，自动将 UTF-8 文件名转换为本地 ANSI （GBK）编码，防止中文乱码。
#### 参数
**url** 字符串。
  - 如果是目录（以 / 结尾或服务器判定为目录）：下载该目录下所有内容（递归）。
  - 如果是文件：下载该文件到本地。

**localDir** 字符串。本地保存目录的路径。如果目录不存在，插件会自动创建。

**user** 字符串（可选）。用户名，默认为空。

**password** 字符串（可选）。密码，默认为空。

**timeout** 数值（可选）。超时时间（秒），默认 30.0。
#### 返回值
INT。成功处理（下载或跳过）的文件总数。
#### 示例
```
// 场景1：下载整个目录（包含子目录，自动保持目录结构）
remoteDir = "ftp://127.0.0.1:2121/project_data/"
localSaveDir = "D:/Downloads/Project/"
count = ftpClient::ftpDownloadDir(remoteDir, localSaveDir, "anonymous", "anonymous", 120)
print("同步完成，共处理文件数：" + count)

// 场景2：下载单个文件
remoteFile = "ftp://127.0.0.1:2121/project_data/config.ini"
ftpClient::ftpDownloadDir(remoteFile, localSaveDir, "anonymous", "anonymous")
```

### ftpGet

#### 语法
```
ftpClient::ftpGet(url, [user], [password], [timeout])
```
#### 详情
将 FTP 服务器上的文件内容下载到内存中。适用于读取配置文件、日志文件或较小的数据文件。
#### 参数
**url** 字符串。远程文件的完整路径（支持智能编码）。例如 ftp://127.0.0.1/config.ini。

**user** 字符串（可选）。用户名，默认为空。

**password** 字符串（可选）。密码，默认为空。

**timeout** 数值（可选）。超时时间（秒），默认 30.0。
#### 返回值
STRING。返回文件的内容。

注意：由于返回类型为 STRING，建议仅用于下载文本文件或较小的二进制文件。如果需要下载大型文件，请使用 `ftpDownloadDir` 直接保存到磁盘。
#### 示例
```
url = "ftp://127.0.0.1:2121/config.ini"
// 获取文件内容
content = ftpClient::ftpGet(url, "anonymous", "anonymous")
print(content)
```

## 常见问题 (FAQ)
### Q1: Windows 上下载中文文件名出现乱码或无法创建文件？
**A**: 本插件原生支持 Unicode (UTF-8) 文件名。在 Windows 环境下，插件会自动处理系统级编码映射。若仍出现乱码，通常源于 FTP 服务器：
- 请确保 FTP 服务器开启了 UTF-8 支持（现代服务器如 vsftpd, pyftpdlib 默认开启）。
- 若服务器强制使用非标编码（如 GBK），请检查服务器端的 OPTS UTF8 ON 设置。

### Q2: 遇到 Access denied 或 550 错误？
**A**: 请检查：
- FTP 服务器用户是否有对应的写入（上传时）或读取（下载时）权限。
- *URL* 路径拼写是否正确。
- 如果是上传，确保 FTP 服务器允许上传。
### Q3: 为什么 `ftpList` 有时不显示精确的秒级时间？
**A**: 插件默认尝试使用 MLSD 命令获取高精度时间。如果服务器不支持 MLSD（如非常古老的服务器），将自动回退到传统的 LIST 命令，此时时间精度可能仅到分钟，且超过半年的文件可能只显示年份。

### Q4: 如何确保下载的是目录而非文件？

**A**: 强烈建议在目录类型的 *URL* 末尾加上斜杠 /。虽然插件有自动探测机制，但加上斜杠可以减少一次网络探测请求，提高性能并消除歧义。例如使用 ftp://host/data/ 而非 ftp://host/data。

### Q5: 我传入的 URL 包含空格或中文，需要自己手动进行 URL Encode 吗？

**A**: 不需要。插件的所有接口（`ftpList`, `ftpUpload`, `ftpUploadFile`, `ftpDownloadDir`）均内置了智能 URL 编码器。它会自动识别路径部分并进行转义，同时保留协议头（ftp://）不变。例如，您可以直接写 "ftp://127.0.0.1/我的 数据/"，插件会自动将其转换为 "ftp://127.0.0.1/%E6%88%91%E7%9A%84%20%E6%95%B0%E6%8D%AE/" 发送给服务器。





