"""
API测试脚本
"""
import requests
import json
import time

# 配置
BASE_URL = 'http://localhost:5001'  # 默认端口5001
TEST_USERNAME = 'test_user'
TEST_EMAIL = 'test@example.com'
TEST_PASSWORD = 'test123456'


class APITester:
    """API测试类"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.user_id = None
        self.meeting_id = None
    
    def print_response(self, name: str, response):
        """打印响应"""
        print(f"\n{'='*50}")
        print(f"{name}")
        print(f"{'='*50}")
        print(f"状态码: {response.status_code}")
        try:
            print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        except:
            print(f"响应: {response.text}")
    
    def test_health(self):
        """测试健康检查"""
        print("\n[测试] 健康检查")
        response = requests.get(f"{self.base_url}/health")
        self.print_response("健康检查", response)
        return response.status_code == 200
    
    def test_register(self):
        """测试用户注册"""
        print("\n[测试] 用户注册")
        data = {
            'username': TEST_USERNAME,
            'email': TEST_EMAIL,
            'password': TEST_PASSWORD
        }
        response = requests.post(
            f"{self.base_url}/api/auth/register",
            json=data
        )
        self.print_response("用户注册", response)
        
        if response.status_code == 201:
            result = response.json()
            if result.get('success'):
                self.token = result['data']['access_token']
                self.user_id = result['data']['user']['id']
                return True
        return False
    
    def test_login(self):
        """测试用户登录"""
        print("\n[测试] 用户登录")
        data = {
            'username': TEST_USERNAME,
            'password': TEST_PASSWORD
        }
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json=data
        )
        self.print_response("用户登录", response)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                self.token = result['data']['access_token']
                self.user_id = result['data']['user']['id']
                return True
        return False
    
    def test_get_current_user(self):
        """测试获取当前用户"""
        print("\n[测试] 获取当前用户")
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(
            f"{self.base_url}/api/auth/me",
            headers=headers
        )
        self.print_response("获取当前用户", response)
        return response.status_code == 200
    
    def test_create_meeting(self):
        """测试创建会议"""
        print("\n[测试] 创建会议")
        headers = {'Authorization': f'Bearer {self.token}'}
        data = {
            'name': '测试会议',
            'description': '这是一个测试会议'
        }
        response = requests.post(
            f"{self.base_url}/api/meetings",
            json=data,
            headers=headers
        )
        self.print_response("创建会议", response)
        
        if response.status_code == 201:
            result = response.json()
            if result.get('success'):
                self.meeting_id = result['data']['id']
                return True
        return False
    
    def test_list_meetings(self):
        """测试列出会议"""
        print("\n[测试] 列出会议")
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(
            f"{self.base_url}/api/meetings",
            headers=headers
        )
        self.print_response("列出会议", response)
        return response.status_code == 200
    
    def test_get_meeting(self):
        """测试获取会议"""
        if not self.meeting_id:
            print("\n[跳过] 获取会议（没有会议ID）")
            return False
        
        print("\n[测试] 获取会议")
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(
            f"{self.base_url}/api/meetings/{self.meeting_id}",
            headers=headers
        )
        self.print_response("获取会议", response)
        return response.status_code == 200
    
    def test_update_transcript(self):
        """测试更新转写文本"""
        if not self.meeting_id:
            print("\n[跳过] 更新转写文本（没有会议ID）")
            return False
        
        print("\n[测试] 更新转写文本")
        headers = {'Authorization': f'Bearer {self.token}'}
        data = {
            'transcript': '这是测试转写文本。会议讨论了项目进度和下一步计划。'
        }
        response = requests.put(
            f"{self.base_url}/api/meetings/{self.meeting_id}/transcript",
            json=data,
            headers=headers
        )
        self.print_response("更新转写文本", response)
        return response.status_code == 200
    
    def test_generate_summary(self):
        """测试生成摘要"""
        if not self.meeting_id:
            print("\n[跳过] 生成摘要（没有会议ID）")
            return False
        
        print("\n[测试] 生成摘要")
        headers = {'Authorization': f'Bearer {self.token}'}
        data = {'type': 'brief'}
        response = requests.post(
            f"{self.base_url}/api/meetings/{self.meeting_id}/summary",
            json=data,
            headers=headers
        )
        self.print_response("生成摘要", response)
        return response.status_code == 200
    
    def test_extract_key_points(self):
        """测试提取要点"""
        if not self.meeting_id:
            print("\n[跳过] 提取要点（没有会议ID）")
            return False
        
        print("\n[测试] 提取要点")
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.post(
            f"{self.base_url}/api/meetings/{self.meeting_id}/key-points",
            headers=headers
        )
        self.print_response("提取要点", response)
        return response.status_code == 200
    
    def test_stop_meeting(self):
        """测试停止会议"""
        if not self.meeting_id:
            print("\n[跳过] 停止会议（没有会议ID）")
            return False
        
        print("\n[测试] 停止会议")
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.post(
            f"{self.base_url}/api/meetings/{self.meeting_id}/stop",
            headers=headers
        )
        self.print_response("停止会议", response)
        return response.status_code == 200
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*50)
        print("开始API测试")
        print("="*50)
        
        results = []
        
        # 基础测试
        results.append(("健康检查", self.test_health()))
        
        # 认证测试
        results.append(("用户注册", self.test_register()))
        if not self.token:
            results.append(("用户登录", self.test_login()))
        results.append(("获取当前用户", self.test_get_current_user()))
        
        # 会议测试
        results.append(("创建会议", self.test_create_meeting()))
        results.append(("列出会议", self.test_list_meetings()))
        results.append(("获取会议", self.test_get_meeting()))
        results.append(("更新转写文本", self.test_update_transcript()))
        results.append(("生成摘要", self.test_generate_summary()))
        results.append(("提取要点", self.test_extract_key_points()))
        results.append(("停止会议", self.test_stop_meeting()))
        
        # 打印结果
        print("\n" + "="*50)
        print("测试结果汇总")
        print("="*50)
        for name, result in results:
            status = "✓ 通过" if result else "✗ 失败"
            print(f"{name}: {status}")
        
        passed = sum(1 for _, r in results if r)
        total = len(results)
        print(f"\n总计: {passed}/{total} 通过")


if __name__ == '__main__':
    tester = APITester()
    tester.run_all_tests()

