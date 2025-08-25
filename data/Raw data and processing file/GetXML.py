import requests
import xmltodict
import json
import os

def download_xml(url, filename="file.xml"):
    """下载XML文件"""
    try:
        print(f"正在下载XML文件: {url}")
        response = requests.get(url)
        response.raise_for_status()  # 检查HTTP错误
        
        with open(filename, "wb") as f:
            f.write(response.content)
        
        print(f"下载完成! 文件保存为: {filename}")
        return filename
    except requests.RequestException as e:
        print(f"下载失败: {e}")
        return None

def xml_to_json(xml_file, json_file=None):
    """将XML文件转换为JSON格式"""
    if json_file is None:
        json_file = xml_file.replace('.xml', '.json')
    
    try:
        print(f"正在转换 {xml_file} 为JSON格式...")
        
        # 读取XML文件
        with open(xml_file, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        # 解析XML并转换为字典
        xml_dict = xmltodict.parse(xml_content)
        
        # 将字典转换为JSON并保存
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(xml_dict, f, indent=2, ensure_ascii=False)
        
        print(f"转换完成! JSON文件保存为: {json_file}")
        return json_file
        
    except Exception as e:
        print(f"转换失败: {e}")
        return None

def main():
    # XML文件URL
    url = "https://www.mbsonline.gov.au/internet/mbsonline/publishing.nsf/650f3eec0dfb990fca25692100069854/0b61e1e80b332754ca258c9e0000c7d8/$FILE/MBS-XML-20250701%20Version%203.XML"
    
    # 下载XML文件
    xml_file = download_xml(url)
    if not xml_file:
        return
    
    # 转换为JSON
    json_file = xml_to_json(xml_file)
    if json_file:
        print(f"\n处理完成!")
        print(f"XML文件: {xml_file}")
        print(f"JSON文件: {json_file}")
        
        # 显示文件大小
        xml_size = os.path.getsize(xml_file) / (1024 * 1024)  # MB
        json_size = os.path.getsize(json_file) / (1024 * 1024)  # MB
        print(f"XML文件大小: {xml_size:.2f} MB")
        print(f"JSON文件大小: {json_size:.2f} MB")

if __name__ == "__main__":
    main()
