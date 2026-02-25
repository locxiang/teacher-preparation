"""
配置文件
"""
import os
from pathlib import Path
from dotenv import load_dotenv


class ConfigError(Exception):
    """配置错误异常"""
    pass

# 尝试从多个位置加载.env文件
# 1. 当前目录（server目录）
# 2. 项目根目录（上一级目录）
env_paths = [
    Path(__file__).parent / '.env',  # server/.env
    Path(__file__).parent.parent / '.env',  # 项目根目录/.env
]

env_loaded = False
env_file_path = None
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path, override=False)  # override=False: 不覆盖已存在的环境变量
        env_loaded = True
        env_file_path = env_path
        print(f"✓ 已加载 .env 文件: {env_path}")
        break

if not env_loaded:
    # 如果找不到.env文件，尝试从当前目录加载（默认行为）
    # 在Docker环境中，环境变量通过docker-compose传递，不需要.env文件
    load_dotenv(override=False)
    print("ℹ 未找到 .env 文件，使用环境变量（Docker环境变量或系统环境变量）")


class Config:
    """应用配置类"""
    
    # Flask配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    # 默认使用5001端口，避免与macOS AirPlay Receiver冲突
    PORT = int(os.getenv('FLASK_PORT', 5001))
    
    # JWT配置
    JWT_SECRET_KEY = SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = False  # 可根据需要设置过期时间
    
    # 阿里云配置
    ALIBABA_CLOUD_ACCESS_KEY_ID = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID')
    ALIBABA_CLOUD_ACCESS_KEY_SECRET = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
    
    # 通义听悟配置（只需要AppKey）
    TYTINGWU_APP_KEY = os.getenv('TYTINGWU_APP_KEY')
    
    # 通义听悟API端点（根据官方文档：https://help.aliyun.com/zh/tingwu/interface-and-implementation）
    TYTINGWU_API_ENDPOINT = 'tingwu.cn-beijing.aliyuncs.com'
    TYTINGWU_API_VERSION = '2023-09-30'
    TYTINGWU_REGION = 'cn-beijing'
    
    # 阿里云智能语音交互（语音合成TTS）配置
    # 注意：语音合成需要使用智能语音交互服务的AppKey，可能与通义听悟不同
    NLS_APP_KEY = os.getenv('NLS_APP_KEY', TYTINGWU_APP_KEY)  # 默认使用通义听悟的AppKey
    NLS_REGION = 'cn-beijing'  # 北京地域
    
    # 阿里云百炼 DashScope 配置
    DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY')
    DASHSCOPE_APP_ID = os.getenv('DASHSCOPE_APP_ID')  # 智能体应用ID

    # SerpApi 网页搜索（相关资料搜索）https://serpapi.com/search-api
    SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY')
    
    @staticmethod
    def print_config():
        """打印配置信息（用于调试，隐藏敏感信息）"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info("=" * 60)
        logger.info("配置信息检查:")
        logger.info("=" * 60)
        
        # Flask配置
        logger.info(f"SECRET_KEY: {'已设置' if Config.SECRET_KEY and Config.SECRET_KEY != 'dev-secret-key-change-in-production' else '使用默认值（不安全）'}")
        logger.info(f"DEBUG: {Config.DEBUG}")
        logger.info(f"HOST: {Config.HOST}")
        logger.info(f"PORT: {Config.PORT}")
        
        # 阿里云配置
        logger.info(f"ALIBABA_CLOUD_ACCESS_KEY_ID: {'已设置' if Config.ALIBABA_CLOUD_ACCESS_KEY_ID else '未设置'}")
        if Config.ALIBABA_CLOUD_ACCESS_KEY_ID:
            # 只显示前4个字符和后4个字符，中间用*代替
            key_id = Config.ALIBABA_CLOUD_ACCESS_KEY_ID
            if len(key_id) > 8:
                masked_key = f"{key_id[:4]}...{key_id[-4:]}"
            else:
                masked_key = "***"
            logger.info(f"  -> 值: {masked_key}")
        
        logger.info(f"ALIBABA_CLOUD_ACCESS_KEY_SECRET: {'已设置' if Config.ALIBABA_CLOUD_ACCESS_KEY_SECRET else '未设置'}")
        if Config.ALIBABA_CLOUD_ACCESS_KEY_SECRET:
            secret = Config.ALIBABA_CLOUD_ACCESS_KEY_SECRET
            if len(secret) > 8:
                masked_secret = f"{secret[:4]}...{secret[-4:]}"
            else:
                masked_secret = "***"
            logger.info(f"  -> 值: {masked_secret}")
        
        logger.info(f"TYTINGWU_APP_KEY: {'已设置' if Config.TYTINGWU_APP_KEY else '未设置'}")
        if Config.TYTINGWU_APP_KEY:
            app_key = Config.TYTINGWU_APP_KEY
            if len(app_key) > 8:
                masked_app_key = f"{app_key[:4]}...{app_key[-4:]}"
            else:
                masked_app_key = "***"
            logger.info(f"  -> 值: {masked_app_key}")
        
        logger.info(f"TYTINGWU_API_ENDPOINT: {Config.TYTINGWU_API_ENDPOINT}")
        logger.info(f"TYTINGWU_REGION: {Config.TYTINGWU_REGION}")
        
        # DashScope配置
        logger.info(f"DASHSCOPE_API_KEY: {'已设置' if Config.DASHSCOPE_API_KEY else '未设置'}")
        logger.info(f"DASHSCOPE_APP_ID: {'已设置' if Config.DASHSCOPE_APP_ID else '未设置'}")
        logger.info(f"SERPAPI_API_KEY: {'已设置' if Config.SERPAPI_API_KEY else '未设置'}")
        
        # 环境变量检查（显示实际从环境变量读取的值）
        logger.info("-" * 60)
        logger.info("环境变量检查（从os.getenv读取）:")
        env_vars = [
            'SECRET_KEY',
            'ALIBABA_CLOUD_ACCESS_KEY_ID',
            'ALIBABA_CLOUD_ACCESS_KEY_SECRET',
            'TYTINGWU_APP_KEY',
            'DASHSCOPE_API_KEY',
            'DASHSCOPE_APP_ID',
        ]
        for var in env_vars:
            value = os.getenv(var)
            if value:
                # 显示值的长度和前几个字符（用于调试）
                preview = value[:10] + "..." if len(value) > 10 else value
                logger.info(f"  {var}: 已设置 (长度: {len(value)}, 预览: {preview})")
            else:
                logger.info(f"  {var}: 未设置 (None或空字符串)")
        
        # 检查配置类中的实际值
        logger.info("-" * 60)
        logger.info("配置类中的实际值:")
        logger.info(f"  Config.ALIBABA_CLOUD_ACCESS_KEY_ID: {'有值' if Config.ALIBABA_CLOUD_ACCESS_KEY_ID else 'None或空字符串'}")
        logger.info(f"  Config.ALIBABA_CLOUD_ACCESS_KEY_SECRET: {'有值' if Config.ALIBABA_CLOUD_ACCESS_KEY_SECRET else 'None或空字符串'}")
        logger.info(f"  Config.TYTINGWU_APP_KEY: {'有值' if Config.TYTINGWU_APP_KEY else 'None或空字符串'}")
        logger.info(f"  Config.DASHSCOPE_API_KEY: {'有值' if Config.DASHSCOPE_API_KEY else 'None或空字符串'}")
        logger.info(f"  Config.DASHSCOPE_APP_ID: {'有值' if Config.DASHSCOPE_APP_ID else 'None或空字符串'}")
        
        logger.info("=" * 60)
    
    @staticmethod
    def validate():
        """验证必要的配置项，如果关键配置缺失则抛出异常"""
        import logging
        logger = logging.getLogger(__name__)
        
        # 基础配置检查
        if not Config.SECRET_KEY or Config.SECRET_KEY == 'dev-secret-key-change-in-production':
            logger.warning("警告: 使用默认SECRET_KEY，生产环境请修改！")
        
        # 通义听悟配置检查（必需配置）
        # AccessKey用于API认证，AppKey是项目标识
        missing_configs = []
        
        if not Config.ALIBABA_CLOUD_ACCESS_KEY_ID:
            missing_configs.append('ALIBABA_CLOUD_ACCESS_KEY_ID')
        if not Config.ALIBABA_CLOUD_ACCESS_KEY_SECRET:
            missing_configs.append('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
        if not Config.TYTINGWU_APP_KEY:
            missing_configs.append('TYTINGWU_APP_KEY')
        
        if missing_configs:
            error_msg = (
                f"\n{'=' * 60}\n"
                f"❌ 配置错误: 通义听悟必需配置项未设置\n"
                f"{'=' * 60}\n"
                f"缺失的配置项:\n"
            )
            for config in missing_configs:
                error_msg += f"  - {config}\n"
            error_msg += (
                f"\n请设置以下环境变量或添加到 .env 文件:\n"
            )
            for config in missing_configs:
                error_msg += f"  {config}=your_value_here\n"
            error_msg += (
                f"\n配置方式:\n"
                f"1. 在项目根目录创建 .env 文件并添加上述配置\n"
                f"2. 或在 docker-compose.yml 中设置环境变量\n"
                f"3. 或通过系统环境变量设置\n"
                f"{'=' * 60}\n"
            )
            
            logger.error(error_msg)
            raise ConfigError(error_msg)

