### 一亩三分地 自动签到脚本

### 介绍

这是留学论坛一亩三分地的每日签到自动化脚本。

主要使用了`requests`来模拟发送请求，`pytesseract`来识别验证码。

在`Ubuntu 16.04`和`Windows 10`中都进行过测试。

在发布到这个repo之前，我已经稳定使用了5个多月。

- Development Environment: ``Windows 10``, `Ubuntu 16.04`
- Python Dependencies Library: ``requests``, ``Pillow``, ``pytesseract``, ``colorama``
- Software Dependencies: ``tesseract-ocr 4.0.0+``

本文只会简单介绍如何调用程序接口，如需部署自动化定时任务，你可能需要一台Linux服务器，然后了解一下`crontab`的用法；

如果你没有VPS或者不想折腾，可以使用一些云计算平台的`Serverless`服务，比如说AWS Lambda、腾讯云函数等等。

### 如何使用？

1. 安装依赖

```
pip install -r requirements.txt
```

2. 安装`tesseract-ocr 4.0.0+`

Tesseract的[使用教程](tesseract-tutorial.md)

3. example code

```
>>> from bot1p3a import checkin
>>> checkin("your username/account", "your password")
```


