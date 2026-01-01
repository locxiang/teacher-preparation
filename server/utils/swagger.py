"""
Swagger API文档配置
"""
try:
    from flask_swagger_ui import get_swaggerui_blueprint
    SWAGGER_AVAILABLE = True
except ImportError:
    # 如果flask-swagger-ui未安装，使用备用方案
    import warnings
    warnings.warn("flask-swagger-ui未安装，Swagger文档功能将被禁用。安装命令: pip install flask-swagger-ui")
    get_swaggerui_blueprint = None
    SWAGGER_AVAILABLE = False

SWAGGER_URL = '/api/docs'  # Swagger UI的URL
API_URL = '/api/swagger.json'  # API文档JSON的URL

# 只有在flask-swagger-ui可用时才创建blueprint
if SWAGGER_AVAILABLE and get_swaggerui_blueprint:
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "会议系统API文档",
            'docExpansion': 'list',
            'defaultModelsExpandDepth': 3,
            'defaultModelExpandDepth': 3,
        }
    )
else:
    swaggerui_blueprint = None


def get_swagger_spec():
    """生成Swagger API规范"""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "会议系统API",
            "description": "基于Flask和通义听悟的会议系统后端API文档",
            "version": "1.0.0",
            "contact": {
                "name": "API支持",
                "email": "support@example.com"
            }
        },
        "servers": [
            {
                "url": "http://localhost:5001",
                "description": "开发环境"
            }
        ],
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
        },
        "paths": {
            "/health": {
                "get": {
                    "tags": ["健康检查"],
                    "summary": "健康检查",
                    "description": "检查服务运行状态",
                    "responses": {
                        "200": {
                            "description": "服务正常",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "status": "ok",
                                        "message": "服务运行正常"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/auth/register": {
                "post": {
                    "tags": ["用户认证"],
                    "summary": "用户注册",
                    "description": "注册新用户",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["username", "email", "password"],
                                    "properties": {
                                        "username": {
                                            "type": "string",
                                            "example": "testuser"
                                        },
                                        "email": {
                                            "type": "string",
                                            "format": "email",
                                            "example": "test@example.com"
                                        },
                                        "password": {
                                            "type": "string",
                                            "example": "password123"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "注册成功",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "success": True,
                                        "data": {
                                            "user": {
                                                "id": 1,
                                                "username": "testuser",
                                                "email": "test@example.com"
                                            },
                                            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
                                        },
                                        "message": "注册成功"
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "请求参数错误"
                        }
                    }
                }
            },
            "/api/auth/login": {
                "post": {
                    "tags": ["用户认证"],
                    "summary": "用户登录",
                    "description": "用户登录，获取访问令牌",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["password"],
                                    "properties": {
                                        "username": {
                                            "type": "string",
                                            "example": "testuser"
                                        },
                                        "email": {
                                            "type": "string",
                                            "format": "email",
                                            "example": "test@example.com"
                                        },
                                        "password": {
                                            "type": "string",
                                            "example": "password123"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "登录成功",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "success": True,
                                        "data": {
                                            "user": {
                                                "id": 1,
                                                "username": "testuser"
                                            },
                                            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
                                        },
                                        "message": "登录成功"
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "用户名或密码错误"
                        }
                    }
                }
            },
            "/api/auth/me": {
                "get": {
                    "tags": ["用户认证"],
                    "summary": "获取当前用户信息",
                    "description": "获取当前登录用户的信息",
                    "security": [{"bearerAuth": []}],
                    "responses": {
                        "200": {
                            "description": "成功",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "success": True,
                                        "data": {
                                            "id": 1,
                                            "username": "testuser",
                                            "email": "test@example.com"
                                        }
                                    }
                                }
                            }
                        },
                        "401": {
                            "description": "未授权"
                        }
                    }
                }
            },
            "/api/meetings": {
                "get": {
                    "tags": ["会议管理"],
                    "summary": "列出所有会议",
                    "description": "获取当前用户的所有会议列表",
                    "security": [{"bearerAuth": []}],
                    "parameters": [
                        {
                            "name": "status",
                            "in": "query",
                            "schema": {
                                "type": "string",
                                "enum": ["running", "stopped", "completed"]
                            },
                            "description": "会议状态筛选"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "成功",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "success": True,
                                        "data": [],
                                        "total": 0
                                    }
                                }
                            }
                        }
                    }
                },
                "post": {
                    "tags": ["会议管理"],
                    "summary": "创建会议",
                    "description": "创建一个新的会议",
                    "security": [{"bearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["name"],
                                    "properties": {
                                        "name": {
                                            "type": "string",
                                            "example": "项目讨论会"
                                        },
                                        "description": {
                                            "type": "string",
                                            "example": "讨论项目进度"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "创建成功",
                            "content": {
                                "application/json": {
                                    "example": {
                                        "success": True,
                                        "data": {
                                            "id": "meeting-uuid",
                                            "name": "项目讨论会",
                                            "status": "running"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/meetings/{meeting_id}": {
                "get": {
                    "tags": ["会议管理"],
                    "summary": "获取会议信息",
                    "description": "获取指定会议的详细信息",
                    "security": [{"bearerAuth": []}],
                    "parameters": [
                        {
                            "name": "meeting_id",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "string"
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "成功"
                        },
                        "404": {
                            "description": "会议不存在"
                        }
                    }
                }
            },
            "/api/meetings/{meeting_id}/stop": {
                "post": {
                    "tags": ["会议管理"],
                    "summary": "停止会议",
                    "description": "停止指定的会议",
                    "security": [{"bearerAuth": []}],
                    "parameters": [
                        {
                            "name": "meeting_id",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "string"
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "停止成功"
                        }
                    }
                }
            },
            "/api/meetings/{meeting_id}/transcript": {
                "put": {
                    "tags": ["会议管理"],
                    "summary": "更新转写文本",
                    "description": "更新会议的转写文本",
                    "security": [{"bearerAuth": []}],
                    "parameters": [
                        {
                            "name": "meeting_id",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "string"
                            }
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["transcript"],
                                    "properties": {
                                        "transcript": {
                                            "type": "string",
                                            "example": "转写文本内容..."
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "更新成功"
                        }
                    }
                }
            },
            "/api/meetings/{meeting_id}/summary": {
                "post": {
                    "tags": ["会议管理"],
                    "summary": "生成会议摘要",
                    "description": "为会议生成摘要",
                    "security": [{"bearerAuth": []}],
                    "parameters": [
                        {
                            "name": "meeting_id",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "string"
                            }
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "type": {
                                            "type": "string",
                                            "enum": ["brief", "detailed"],
                                            "default": "brief",
                                            "example": "brief"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "生成成功"
                        }
                    }
                }
            },
            "/api/meetings/{meeting_id}/key-points": {
                "post": {
                    "tags": ["会议管理"],
                    "summary": "提取会议要点",
                    "description": "提取会议的关键要点",
                    "security": [{"bearerAuth": []}],
                    "parameters": [
                        {
                            "name": "meeting_id",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "string"
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "提取成功"
                        }
                    }
                }
            },
            "/api/audio/upload/{meeting_id}": {
                "post": {
                    "tags": ["音频管理"],
                    "summary": "上传音频文件",
                    "description": "上传音频文件到指定会议",
                    "security": [{"bearerAuth": []}],
                    "parameters": [
                        {
                            "name": "meeting_id",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "string"
                            }
                        },
                        {
                            "name": "convert_to_wav",
                            "in": "query",
                            "schema": {
                                "type": "boolean",
                                "default": False
                            },
                            "description": "是否转换为WAV格式"
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "file": {
                                            "type": "string",
                                            "format": "binary"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "上传成功"
                        },
                        "400": {
                            "description": "文件格式不支持"
                        },
                        "413": {
                            "description": "文件大小超过限制"
                        }
                    }
                }
            },
            "/api/audio/info/{meeting_id}": {
                "get": {
                    "tags": ["音频管理"],
                    "summary": "列出会议音频文件",
                    "description": "获取指定会议的所有音频文件列表",
                    "security": [{"bearerAuth": []}],
                    "parameters": [
                        {
                            "name": "meeting_id",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "string"
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "成功"
                        }
                    }
                }
            }
        }
    }

