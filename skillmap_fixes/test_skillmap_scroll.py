
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class SkillmapScrollTest(unittest.TestCase):
    '''스킬맵 무한 스크롤 테스트'''
    
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.get('http://localhost:8000/dashboards/skillmap/')
        # 로그인 처리
        
    def tearDown(self):
        self.driver.quit()
        
    def test_scroll_loading(self):
        '''스크롤 시 추가 데이터 로딩 테스트'''
        # 초기 아이템 수 확인
        initial_items = len(self.driver.find_elements(By.CLASS_NAME, 'skill-item'))
        
        # 스크롤 다운
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # 로딩 대기
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'loading-indicator')))
        
        # 새 아이템 로드 대기
        time.sleep(2)
        
        # 아이템 수 증가 확인
        new_items = len(self.driver.find_elements(By.CLASS_NAME, 'skill-item'))
        self.assertGreater(new_items, initial_items)
        
    def test_no_infinite_loop(self):
        '''무한 루프 방지 테스트'''
        # 네트워크 요청 수 모니터링
        self.driver.execute_script('''
            window.apiCallCount = 0;
            const originalFetch = window.fetch;
            window.fetch = function(...args) {
                window.apiCallCount++;
                return originalFetch.apply(this, args);
            };
        ''')
        
        # 빠른 스크롤 여러 번
        for _ in range(5):
            self.driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(0.1)
        
        # API 호출 수 확인
        api_calls = self.driver.execute_script("return window.apiCallCount;")
        self.assertLess(api_calls, 10, "Too many API calls detected")
        
    def test_scroll_to_bottom(self):
        '''끝까지 스크롤 테스트'''
        # 계속 스크롤하여 끝 도달
        last_height = 0
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            new_height = self.driver.execute_script("return document.body.scrollHeight;")
            if new_height == last_height:
                break
            last_height = new_height
            
        # "더 이상 데이터 없음" 메시지 확인
        end_message = self.driver.find_element(By.CLASS_NAME, 'end-message')
        self.assertTrue(end_message.is_displayed())

if __name__ == '__main__':
    unittest.main()
