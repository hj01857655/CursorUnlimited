import subprocess
import winreg

print("=" * 80)
print("Windows 系统机器标识")
print("=" * 80)

# 1. MachineGuid (注册表)
try:
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography")
    machine_guid, _ = winreg.QueryValueEx(key, "MachineGuid")
    winreg.CloseKey(key)
    print(f"\n1. MachineGuid (HKLM\\SOFTWARE\\Microsoft\\Cryptography):")
    print(f"   {machine_guid}")
except Exception as e:
    print(f"\n1. MachineGuid: 读取失败 - {e}")

# 2. UUID (WMIC)
try:
    result = subprocess.run(['wmic', 'csproduct', 'get', 'UUID'], 
                          capture_output=True, text=True)
    uuid = result.stdout.strip().split('\n')[1].strip()
    print(f"\n2. System UUID (WMIC csproduct):")
    print(f"   {uuid}")
except Exception as e:
    print(f"\n2. System UUID: 读取失败 - {e}")

# 3. Product ID
try:
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
    product_id, _ = winreg.QueryValueEx(key, "ProductId")
    winreg.CloseKey(key)
    print(f"\n3. Product ID (HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion):")
    print(f"   {product_id}")
except Exception as e:
    print(f"\n3. Product ID: 读取失败 - {e}")

# 4. SQM Client ID
try:
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\SQMClient")
    sqm_id, _ = winreg.QueryValueEx(key, "MachineId")
    print(f"\n4. SQM MachineId (HKLM\\SOFTWARE\\Microsoft\\SQMClient):")
    print(f"   {sqm_id}")
except Exception as e:
    print(f"\n4. SQM MachineId: 不存在或读取失败")

# 5. Installation ID
try:
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
    install_time, _ = winreg.QueryValueEx(key, "InstallTime")
    install_date, _ = winreg.QueryValueEx(key, "InstallDate")
    winreg.CloseKey(key)
    print(f"\n5. Windows 安装信息:")
    print(f"   InstallTime: {install_time}")
    print(f"   InstallDate: {install_date}")
except Exception as e:
    print(f"\n5. Windows 安装信息: 读取失败 - {e}")

# 6. Computer HardwareId
try:
    result = subprocess.run(['wmic', 'bios', 'get', 'serialnumber'], 
                          capture_output=True, text=True)
    serial = result.stdout.strip().split('\n')[1].strip()
    print(f"\n6. BIOS Serial Number:")
    print(f"   {serial}")
except Exception as e:
    print(f"\n6. BIOS Serial: 读取失败 - {e}")

# 7. MAC Address (主网卡)
try:
    result = subprocess.run(['getmac', '/fo', 'csv', '/nh'], 
                          capture_output=True, text=True, encoding='gbk')
    lines = result.stdout.strip().split('\n')
    if lines:
        mac = lines[0].split(',')[0].strip('"')
        print(f"\n7. 主网卡 MAC Address:")
        print(f"   {mac}")
except Exception as e:
    print(f"\n7. MAC Address: 读取失败 - {e}")

print("\n" + "=" * 80)
print("总结：Cursor 可能使用的 Windows 标识")
print("=" * 80)
print("\n主要标识：")
print("  - MachineGuid: 最常用，Cursor 的 storage.serviceMachineId 使用此值")
print("  - System UUID: 主板/系统唯一标识")
print("  - MAC Address: 网卡物理地址")
print("\n次要标识：")
print("  - Product ID: Windows 产品密钥相关")
print("  - BIOS Serial: 硬件序列号")
