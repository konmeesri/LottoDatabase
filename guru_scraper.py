import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime

class LottoDataFactory:
    def __init__(self, target_url, draw_date):
        self.target_url = target_url
        self.draw_date = draw_date
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def fetch_raw_news(self):
        """1. วิ่งไปดูดหน้าเว็บข่าวต้นฉบับ"""
        try:
            print(f"🌐 กำลังเชื่อมต่อกับ: {self.target_url}")
            response = requests.get(self.target_url, headers=self.headers, timeout=15)
            response.encoding = 'utf-8'
            if response.status_code == 200:
                return BeautifulSoup(response.text, 'html.parser')
            return None
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return None

    def extract_guru_content(self, soup):
        """2. แกะพาดหัวข่าวและสกัดตัวเลขด้วย Regex"""
        if not soup: return []
        
        articles = soup.find_all('a', title=True)
        gurus_list = []
        id_counter = 1

        for art in articles:
            title = art['title']
            # กรองเฉพาะข่าวที่มีแนวทางเลขเด็ด
            if any(keyword in title for keyword in ["เลขเด็ด", "แม่น้ำหนึ่ง", "เจ๊ฟองเบียร์", "เจ๊นุ๊ก", "ดุ่ย"]):
                
                # สกัดเลข 2 ตัว และ 3 ตัว (Regex แบบแม่นยำ)
                two_digits = list(set(re.findall(r'(?<!\d)\d{2}(?!\d)', title)))
                three_digits = list(set(re.findall(r'(?<!\d)\d{3}(?!\d)', title)))

                if two_digits or three_digits:
                    # วิเคราะห์หาชื่อสำนักจากพาดหัว
                    name = "สำนักดัง"
                    if "แม่น้ำหนึ่ง" in title: name = "แม่น้ำหนึ่ง"
                    elif "ฟองเบียร์" in title: name = "เจ๊ฟองเบียร์"
                    elif "เจ๊นุ๊ก" in title: name = "เจ๊นุ๊ก บารมีมหาเฮง"
                    elif "ดุ่ย" in title: name = "ดุ่ย ภรัญฯ"
                    elif "ปฏิทินจีน" in title: name = "เลขปฏิทินจีน"

                    guru_item = {
                        "id": f"g{id_counter:02d}",
                        "name": name,
                        "tag": "ข่าวสดใหม่",
                        "isHot": True if len(three_digits) > 0 else False,
                        "views": f"{10 + id_counter}K", # จำลองยอดวิวเริ่มต้น
                        "image": "https://placehold.co/400x600/1F1F2A/FFD700.png?text=News",
                        "numbers": {
                            "highlight": two_digits[0] if two_digits else (three_digits[0][0] if three_digits else "-"),
                            "two_digits": two_digits,
                            "three_digits": three_digits
                        }
                    }
                    gurus_list.append(guru_item)
                    id_counter += 1
            
            if len(gurus_list) >= 10: break # เอามาเป็นตัวอย่าง 10 สำนักพอ
            
        return gurus_list

    def save_to_json(self, data):
        """3. ประกอบร่าง JSON พร้อม Metadata และบันทึกไฟล์"""
        output = {
            "metadata": {
                "draw_date": self.draw_date,
                "last_updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "source": "Fahlikhit_Auto_Scraper_V1",
                "status": "active"
            },
            "data": data
        }

        filename = "gurus_data.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"✅ บันทึกไฟล์ {filename} เรียบร้อยแล้ว! (ประจำงวด {self.draw_date})")

# ==========================================
# 🚀 ส่วนการรันโปรแกรม
# ==========================================
if __name__ == "__main__":
    # --- ตั้งค่าตรงนี้ก่อนรันทุกงวด ---
    TARGET_DRAW_DATE = "02/05/2026" 
    NEWS_URL = "https://news.sanook.com/lotto/"
    # ----------------------------

    factory = LottoDataFactory(NEWS_URL, TARGET_DRAW_DATE)
    
    print("✨ เริ่มกระบวนการสกัดข้อมูลเลขเด็ด...")
    soup_data = factory.fetch_raw_news()
    final_data = factory.extract_guru_content(soup_data)
    
    if final_data:
        factory.save_to_json(final_data)
        print(f"📊 สกัดข้อมูลสำเร็จทั้งหมด {len(final_data)} สำนัก")
    else:
        print("⚠️ ไม่พบข้อมูลใหม่ในขณะนี้")