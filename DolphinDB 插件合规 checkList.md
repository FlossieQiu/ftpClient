# 插件合规 review

请对照如下各项进行检查，并填写检查结果

|      | **检查项**               | **检查内容**                                                 | **检查结果**                                                 |
| :--- | :----------------------- | :----------------------------------------------------------- | ------------------------------------------------------------ |
| 1    | 是否会修改本地文件系统   | 理论上插件只会使用 DolphinDB 内部的数据表存储数据，如果需要额外修改本地文件系统，需要说明用途，确保不会对 DolphinDB 运行产生影响。 | 不会修改                                                     |
| 2    | 是否使用第三方库         | 如果依赖第三方库，它会有额外的环境要求、编译器要求，与 DolphinDB 可能也有一定的兼容性问题。如果使用第三方库需要说明它的环境要求、编译器要求，是否存在已知的 bug。如果第三方库是开源的，需要注明开源协议，确保不侵犯第三方的版权，包括代码、文档和资源。 | 使用了4个开源库 [libcurl](https://github.com/curl)、[libssl&libcrypto](https://www.openssl.org/)和[zlib](http://www.zlib.net)，不侵犯第三方产权，其它详见表格后面第三方库依赖说明 (Third-Party Dependencies) |
| 3    | 是否使用额外的线程       | 理论上插件内也是用 DolphinDB 内部的线程处理数据，如果需要额外启用线程，或者第三方起线程，需要说明额外线程的用途、数量，避免对 DolphinDB 的稳定性和性能造成影响。 | 否                       |
| 4    | 是否需要联网             | DolphinDB 需要确保客户生产环境的安全性，因此如果插件中需要连接外网，需要说明联网的用途、联网的方式，确保系统的安全性。 | 需要连接外部 ftp 服务器                                    |
| 5    | 是否会收集数据、联网发送 | 确保客户的数据安全对 DolphinDB 来说至关重要，我们不允许插件收集客户的数据文件，本地环境信息，更不允许将这些数据通过联网发送到外部。 | 不会收集                                                     |



## 第三方库依赖说明 (Third-Party Dependencies)
本插件 (ftpClient) 在开发和运行过程中使用了以下开源第三方库。所有使用的库均遵循其相应的开源协议，未侵犯任何第三方的版权。使用者在分发或修改本插件时，需遵守以下协议规定。

- 1. cURL (libcurl)

libcurl 是一个用于传输数据的免费开源客户端 URL 传输库，支持 FTP, FTPS, HTTP 等多种协议。
  - 开源协议: curl License (基于 MIT/X11 衍生，极其宽松)
版权要求: 允许在商业和非商业应用中免费使用、修改和分发。唯一的要求是如果分发源代码，必须保留版权声明；如果分发二进制文件，虽然不是强制要求，但建议在文档中包含版权声明。
  - 环境要求:
    - Linux: 建议使用 CentOS 7 / Ubuntu 16.04 及以上版本。通常系统自带，但建议版本 >= 7.29.0 以支持较新的 TLS 特性。
    - Windows: Windows 7 及以上。需确保系统中存在对应的 DLL (如 libcurl.dll) 或静态链接到插件中。

  - 编译器要求:
    - 支持 C89/C90 标准的编译器（如 GCC 4.8+, MSVC 2015+）。
  - 已知问题 / 注意事项:
    - 线程安全: libcurl 初始化函数 curl_global_init 非线程安全，本插件已在加载时处理。
版本兼容性: 在 Linux 环境下，若链接系统自带的 libcurl，需注意不同发行版 SSL 后端（OpenSSL vs NSS）的差异，建议编译时指定 OpenSSL 后端。

- 2. OpenSSL (libssl & libcrypto)

libssl 和 libcrypto 是 OpenSSL 项目的核心组件。libcrypto 提供加密算法库，libssl 提供 SSL/TLS 协议实现。ftpClient 使用它们来实现 FTPS (FTP over SSL) 安全传输。
  - 开源协议:
    - OpenSSL 3.0.0 及以上: Apache License 2.0。
    - OpenSSL 1.1.1 及以下: OpenSSL License 和 SSLeay License (双重许可)。
  - 版权要求: 包含 OpenSSL 工具包中的软件（"This product includes software developed by the OpenSSL Project for use in the OpenSSL Toolkit"）。在分发产品时，必须在文档中保留版权声明和免责声明。
  - 环境要求:
    - Linux: 强烈建议与 libcurl 所依赖的版本保持一致，避免 ABI 冲突。DolphinDB Server 环境通常依赖 OpenSSL 1.0.x 或 1.1.x。
    - Windows: 需要相应的 DLL (libssl-1_1-x64.dll, libcrypto-1_1-x64.dll 或更新版本)。
  - 编译器要求:GCC 4.x+, MSVC。
  - 已知问题 / 注意事项:
    - 安全漏洞: 旧版本的 OpenSSL (如 1.0.1 之前的版本) 存在著名的 Heartbleed 等漏洞。请确保使用已打补丁的稳定版本（推荐 1.1.1w 或 3.0+ LTS）。本插件用了1.0.2u版本。
    - ABI 兼容性: OpenSSL 1.0.x, 1.1.x 和 3.x 之间 ABI 不兼容，编译插件时链接的版本必须与运行时环境加载的版本一致。

- 3. zlib

zlib 是一个通用的数据压缩库。libcurl 内部使用它来支持 HTTP/FTP 传输中的压缩流（如 gzip）。

  - 开源协议: zlib License
  - 版权要求: 非常宽松。允许用于商业软件。要求包括：不得声称你编写了原始软件；修改后的源版本必须标记为已修改；不得从源代码中删除版权声明。
  - 环境要求:
    -  Linux/Windows: 几乎所有操作系统均内置支持。
  - 编译器要求: ANSI C 编译器。
  - 已知问题 / 注意事项:
    - zlib 极其稳定，鲜有重大 Bug。建议使用 1.2.8 及以上版本以修复潜在的微小安全问题。