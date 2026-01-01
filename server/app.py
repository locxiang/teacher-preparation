"""
Flask应用主文件
"""
import sys
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config, ConfigError
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 初始化Flask应用
app = Flask(__name__)
app.config.from_object(Config)
# 配置JSON响应不使用ASCII编码，确保中文正确显示
app.config['JSON_AS_ASCII'] = False

# 启用CORS
CORS(app)

# 初始化数据库
from database import init_db
init_db(app)

# 自动执行数据库迁移
from utils.migration_manager import run_migrations
run_migrations(app)

# 初始化JWT
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = Config.SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # 可根据需要设置过期时间

# 初始化SocketIO
from services.websocket_service import init_socketio
socketio = init_socketio(app)

# 导入路由
from routes import meeting_bp, health_bp, auth_bp, summary_bp, ai_chat_bp, tts_bp
from routes.teacher import teacher_bp
from routes.document import document_bp
from routes.tytingwu import tytingwu_bp

# 注册Swagger UI（如果可用）
try:
    from utils.swagger import swaggerui_blueprint, get_swagger_spec
    if swaggerui_blueprint:
        app.register_blueprint(swaggerui_blueprint)
    
    # 注册Swagger JSON端点
    @app.route('/api/swagger.json')
    def swagger_json():
        """返回Swagger API规范JSON"""
        import json
        return json.dumps(get_swagger_spec(), ensure_ascii=False, indent=2)
except Exception as e:
    app.logger.warning(f"Swagger UI未启用: {str(e)}")

# 注册蓝图
app.register_blueprint(health_bp)
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(meeting_bp, url_prefix='/api/meetings')
# audio_bp 已删除，现在直接使用 OutputMp3Path URL
app.register_blueprint(teacher_bp, url_prefix='/api/teachers')
app.register_blueprint(document_bp, url_prefix='/api/documents')
app.register_blueprint(tytingwu_bp, url_prefix='/api/tytingwu')
app.register_blueprint(summary_bp, url_prefix='/api/summary')
app.register_blueprint(ai_chat_bp, url_prefix='/api/ai-chat')
app.register_blueprint(tts_bp, url_prefix='/api/tts')

# 配置文件上传大小限制（50MB）
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# 文档上传大小限制（20MB）
DOCUMENT_MAX_SIZE = 20 * 1024 * 1024

# 注册错误处理器
from utils.error_handler import register_error_handlers
register_error_handlers(app)

# 验证配置（关键配置缺失时强制退出）
try:
    # 打印配置信息（用于调试）
    Config.print_config()
    Config.validate()
    app.logger.info("✓ 配置验证通过，服务启动中...")
except ConfigError as e:
    # 配置错误，强制退出
    app.logger.error("配置验证失败，服务无法启动")
    print(str(e), file=sys.stderr)
    sys.exit(1)
except Exception as e:
    # 其他异常也退出，避免无意义的运行
    app.logger.error(f"配置验证异常: {e}")
    print(f"配置验证异常: {e}", file=sys.stderr)
    sys.exit(1)


if __name__ == '__main__':
    # 开发环境启用热更新（reloader），生产环境禁用
    # 通过 FLASK_DEBUG 环境变量控制
    use_reloader = Config.DEBUG
    
    socketio.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
        allow_unsafe_werkzeug=True,  # 允许在开发环境使用Werkzeug
        use_reloader=use_reloader  # 开发环境启用热更新
    )

