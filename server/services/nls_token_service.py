"""
阿里云智能语音交互（NLS）Token服务
用于生成WebSocket连接所需的Token
参考文档：https://help.aliyun.com/zh/isi/developer-reference/websocket-protocol-description
使用阿里云SDK方式生成Token
"""
import logging
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from aliyunsdkcore.auth.credentials import AccessKeyCredential
from config import Config

logger = logging.getLogger(__name__)


class NLSTokenService:
    """NLS Token生成服务"""
    
    def __init__(self):
        self.access_key_id = Config.ALIBABA_CLOUD_ACCESS_KEY_ID
        self.access_key_secret = Config.ALIBABA_CLOUD_ACCESS_KEY_SECRET
        self.app_key = Config.NLS_APP_KEY
        self.region = Config.NLS_REGION
        
        if not self.access_key_id or not self.access_key_secret:
            logger.warning("NLS Token服务配置不完整：缺少AccessKey")
        if not self.app_key:
            logger.warning("NLS Token服务配置不完整：缺少AppKey")
        
        # 初始化AcsClient
        # 注意：Token接口使用cn-shanghai区域，而不是业务区域
        if self.access_key_id and self.access_key_secret:
            try:
                credentials = AccessKeyCredential(
                    self.access_key_id,
                    self.access_key_secret
                )
                # Token接口使用cn-shanghai区域
                self.client = AcsClient(
                    region_id='cn-shanghai',
                    credential=credentials
                )
                logger.info("NLS AcsClient初始化成功（使用cn-shanghai区域用于Token生成）")
            except Exception as e:
                logger.error(f"初始化NLS AcsClient失败: {str(e)}")
                self.client = None
        else:
            self.client = None
    
    def generate_token(self, expire_time: int = 3600) -> str:
        """
        生成NLS WebSocket连接Token
        使用阿里云SDK方式调用CreateToken接口
        参考官方示例：https://help.aliyun.com/zh/isi/getting-started/obtain-an-access-token-1
        
        Args:
            expire_time: Token过期时间（秒），默认3600秒（1小时），此参数在API中不使用，由服务端决定
        
        Returns:
            Token字符串
        """
        if not self.client:
            raise ValueError("AcsClient未初始化，无法生成Token")
        
        try:
            # 根据官方示例，使用POST方法调用CreateToken接口
            # 域名：nls-meta.cn-shanghai.aliyuncs.com（注意：使用shanghai区域）
            # 注意：Token接口使用cn-shanghai区域，而不是业务区域
            request = CommonRequest()
            request.set_method('POST')
            request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
            request.set_version('2019-02-28')
            request.set_action_name('CreateToken')
            
            logger.info("调用CreateToken接口获取Token")
            
            # 发送请求
            response = self.client.do_action_with_exception(request)
            
            # 解析响应
            import json
            data = json.loads(response.decode('utf-8'))
            
            logger.info(f"CreateToken响应: {json.dumps(data, ensure_ascii=False)}")
            
            # 检查响应格式
            if 'Token' in data and 'Id' in data['Token']:
                token = data['Token']['Id']
                expire_time_actual = data['Token'].get('ExpireTime', expire_time)
                logger.info(f"成功生成NLS Token，过期时间: {expire_time_actual}秒")
                return token
            else:
                error_msg = data.get('Message', data.get('message', '未知错误'))
                logger.error(f"生成Token失败: {error_msg}, 响应: {data}")
                raise Exception(f"生成Token失败: {error_msg}")
                
        except Exception as e:
            logger.error(f"生成Token时出错: {str(e)}", exc_info=True)
            raise Exception(f"生成Token失败: {str(e)}")

