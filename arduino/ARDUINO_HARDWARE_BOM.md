# Arduino版硬件清单 Arduino Hardware BOM

## 核心差异 Key Differences from Raspberry Pi

| 项目 | 树莓派 Raspberry Pi | Arduino ESP32 |
|------|---------------------|---------------|
| 编程语言 | Python | C/C++ |
| WiFi内置 | 是 | 是 (ESP32) |
| 功耗 | 5W | 0.5W |
| 价格 | ¥350 | ¥30-50 |
| 处理能力 | 强 | 中等 |
| 适合场景 | 复杂运算 | 传感器控制 |

---

## 必需硬件 Required Hardware

### 1. 主控板 Main Controller - **¥30-50**

**推荐: ESP32 DevKit V1** ⭐
- **WiFi内置:** 802.11 b/g/n
- **蓝牙:** BLE 4.2
- **引脚:** 30+ GPIO (包含I2C, SPI, ADC)
- **电压:** 3.3V逻辑
- **RAM:** 520KB
- **Flash:** 4MB
- **为什么:** 便宜, WiFi内置, I2C支持, Arduino IDE兼容

**淘宝搜索:** `ESP32开发板 DevKit` 或 `NodeMCU-32S`

**备选方案:**
1. **Arduino Uno + ESP8266 WiFi模块** (¥25 + ¥15 = ¥40)
   - 需要额外连线
   - 更复杂
   
2. **Arduino Nano 33 IoT** (¥150)
   - WiFi内置但贵
   - 官方Arduino品牌

---

### 2. 传感器 Sensors (相同 Same as Pi)

**A. 浊度 Turbidity - ¥180-250**
```
DFRobot SEN0554 I2C浊度传感器
或: I2C浊度模块 0-1000NTU
淘宝: DFRobot浊度传感器 I2C
```

**B. pH传感器 - ¥150-400**
```
选项1: Atlas Scientific EZO-pH I2C (¥400) - 高精度
选项2: DFRobot pH传感器 模拟输出 (¥150) - 实惠
淘宝: pH传感器 I2C 或 模拟pH传感器
包含: pH校准液 4.0/7.0/10.0
```

**C. 温度 Temperature - ¥15-30**
```
DS18B20防水温度传感器 1-Wire
4.7kΩ上拉电阻
淘宝: DS18B20 防水温度传感器
```

---

### 3. 执行器 Actuators

**水泵 Water Pump - ¥30-60**
```
12V直流水泵 微型潜水泵
流量: 0.5-1.5L/分钟
淘宝: 12V直流水泵 微型
```

**电磁阀 Solenoid Valve - ¥20-40**
```
12V电磁阀 常闭型 DN15
淘宝: 12V电磁阀 常闭
```

**继电器模块 Relay - ¥8-15**
```
2路继电器 3.3V触发 (ESP32用3.3V!)
或: 5V继电器 (需要电平转换)
淘宝: 2路继电器模块 3.3V低电平触发
```

---

### 4. 电源 Power Supply

**5V电源 - ¥15-25**
```
5V 3A电源适配器 Micro-USB (for ESP32)
或: 5V适配器 + USB线
淘宝: 5V 3A电源适配器
```

**12V电源 - ¥15-25**
```
12V 2A电源适配器 (泵和阀门)
淘宝: 12V 2A电源适配器
```

**可选: 面包板电源模块 - ¥5**
```
面包板电源 双路输出 3.3V/5V
淘宝: 面包板电源模块
```

---

### 5. 接线材料 Wiring (相同)

```
杜邦线 公对公/公对母/母对母   ¥25-40
面包板 830孔                 ¥10
接线端子 螺丝端子            ¥8
电阻包 (含4.7kΩ)            ¥15
```

---

### 6. 管道系统 Piping (相同)

```
PVC管 25mm + 管帽           ¥15-30
硅胶管 12mm 食品级 2-3米    ¥15-25
变径接头 25mm转12mm         ¥5
防水胶/环氧树脂             ¥10
```

---

## 关键区别 Key Differences

### ✅ Arduino优势:
- 更便宜 (ESP32 ¥40 vs 树莓派 ¥350)
- 更低功耗 (0.5W vs 5W)
- 更稳定 (无操作系统崩溃)
- 启动快 (1秒 vs 30秒)

### ⚠️ Arduino限制:
- 需要C/C++编程 (不能用Python)
- 处理能力弱 (但传感器足够)
- RAM小 (520KB vs 4GB)
- 无操作系统 (不能运行多任务)

---

## 接线图 ESP32 Wiring

```
ESP32 DevKit V1:
┌──────────────────────────────┐
│ 3V3  ●●  VIN (5V)            │
│ GND  ●●  GND                 │
│ GPIO21 (SDA) ●●  GPIO22 (SCL)│  I2C总线
│ GPIO4  ●●  GPIO17            │  DS18B20 / 继电器1
│ GPIO16 ●●  GPIO18            │  继电器2
└──────────────────────────────┘
```

### 传感器连接:
```
浊度传感器 (I2C 0x30):
  VCC → ESP32 3V3
  GND → ESP32 GND
  SDA → ESP32 GPIO21
  SCL → ESP32 GPIO22

pH传感器 (I2C 0x63):
  VCC → ESP32 3V3
  GND → ESP32 GND
  SDA → ESP32 GPIO21 (共享)
  SCL → ESP32 GPIO22 (共享)

温度传感器 (DS18B20):
  红线 VCC → ESP32 3V3
  黑线 GND → ESP32 GND
  黄线 Data → ESP32 GPIO4
  4.7kΩ电阻: VCC到Data之间

继电器模块:
  VCC → ESP32 VIN (5V)
  GND → ESP32 GND
  IN1 → ESP32 GPIO17 (水泵控制)
  IN2 → ESP32 GPIO16 (阀门控制)
```

---

## 总价对比 Price Comparison

### Arduino版 (ESP32):
- ESP32开发板: ¥40
- 传感器 (浊度+pH+温度): ¥350-500
- 执行器 (泵+阀+继电器): ¥60-115
- 电源+接线: ¥50-100
- 管道系统: ¥40-65

**总计: ¥540-820**

### 树莓派版:
- 树莓派4B套装: ¥400-500
- 传感器 (相同): ¥350-500
- 执行器 (相同): ¥60-115
- 电源+接线: ¥50-100
- 管道系统: ¥40-65

**总计: ¥900-1280**

**Arduino版省: ¥360-460**

---

## 编程工具 Programming Tools

### Arduino IDE (免费 Free)
- 下载: https://www.arduino.cc/en/software
- 支持: Windows, macOS, Linux
- 安装ESP32支持: 
  - 文件 → 首选项 → 附加开发板管理器网址
  - 添加: `https://dl.espressif.com/dl/package_esp32_index.json`

### 所需库 Required Libraries:
```
- WiFi.h (ESP32内置)
- HTTPClient.h (ESP32内置)
- Wire.h (I2C通信)
- OneWire.h (DS18B20)
- DallasTemperature.h (DS18B20)
- ArduinoJson.h (JSON处理)
```

---

## 推荐购买策略 Recommended Purchase

### 第一阶段 Phase 1 (核心系统 ~¥350):
✅ ESP32开发板
✅ DS18B20温度传感器 (便宜,先测试)
✅ 2路继电器模块
✅ 12V水泵
✅ 12V电磁阀
✅ 基础接线材料

**先测试温度+泵控制**

### 第二阶段 Phase 2 (完整传感 ~¥400):
✅ DFRobot浊度传感器
✅ pH传感器
✅ pH校准液
✅ PVC管道系统

**加入浊度和pH监测**

---

## ⚠️ 重要注意事项

1. **电压:** ESP32是3.3V逻辑, 继电器可能需要5V (检查兼容性)
2. **I2C上拉:** 某些ESP32板没有内置上拉电阻, 需要外接4.7kΩ
3. **电源:** ESP32和12V设备用不同电源, 共地GND
4. **WiFi:** ESP32需要2.4GHz WiFi (不支持5GHz)
