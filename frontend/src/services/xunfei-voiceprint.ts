import CryptoJS from 'crypto-js'

// 科大讯飞配置
export interface XunfeiConfig {
  appId: string
  accessKeyId: string
  accessKeySecret: string
}

// 声纹注册响应
export interface VoiceprintRegisterResponse {
  code: string
  desc: string
  data: string // JSON字符串，包含 feature_id 和 status
  sid: string
}

// 声纹注册数据
export interface VoiceprintRegisterData {
  feature_id: string
  status: number
}

// 声纹注册完整响应
export interface VoiceprintRegisterFullResponse {
  feature_id: string
  status: number
  sid: string
  code: string
  desc: string
}

// 声纹更新响应
export interface VoiceprintUpdateResponse {
  code: string
  desc: string
  data: string // JSON字符串，包含 status
  sid: string
}

// 声纹更新数据
export interface VoiceprintUpdateData {
  status: number
}

// 声纹更新完整响应
export interface VoiceprintUpdateFullResponse {
  status: number
  sid: string
  code: string
  desc: string
}

/**
 * 科大讯飞声纹服务
 */
export class XunfeiVoiceprintService {
  private config: XunfeiConfig

  constructor(config: XunfeiConfig) {
    this.config = config
  }

  /**
   * 获取 UTC 时间字符串
   * 格式：2025-09-04T15:38:07+0800
   */
  private getUTCString(): string {
    const now = new Date()
    const year = now.getFullYear()
    const month = String(now.getMonth() + 1).padStart(2, '0')
    const day = String(now.getDate()).padStart(2, '0')
    const hours = String(now.getHours()).padStart(2, '0')
    const minutes = String(now.getMinutes()).padStart(2, '0')
    const seconds = String(now.getSeconds()).padStart(2, '0')

    // 获取时区偏移（+0800格式）
    const timezoneOffset = -now.getTimezoneOffset()
    const offsetHours = Math.floor(Math.abs(timezoneOffset) / 60)
    const offsetMinutes = Math.abs(timezoneOffset) % 60
    const offsetSign = timezoneOffset >= 0 ? '+' : '-'
    const timezone = `${offsetSign}${String(offsetHours).padStart(2, '0')}${String(offsetMinutes).padStart(2, '0')}`

    return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}${timezone}`
  }

  /**
   * URL编码（对键和值分别编码）
   */
  private urlEncode(str: string): string {
    return encodeURIComponent(str)
  }

  /**
   * 生成随机字符串
   */
  private generateRandomString(length = 16): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    let result = ''
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length))
    }
    return result
  }

  /**
   * 生成签名
   * 按照文档要求：
   * 1. 将所有请求参数（不包含signature）按参数名进行升序排序
   * 2. 对每个参数的键和值分别进行URL编码
   * 3. 按照"编码后的键=编码后的值&"的格式拼接所有参数
   * 4. 移除最后一个多余的"&"符号，得到baseString
   * 5. 以accessKeySecret为密钥，对baseString进行HmacSHA1加密
   * 6. 对HmacSHA1加密后的字节数组进行Base64编码
   */
  private generateSignature(params: Record<string, string | number>): string {
    // 1. 排除signature参数，并按参数名升序排序
    const sortedKeys = Object.keys(params)
      .filter(key => key !== 'signature')
      .sort()

    // 2. 对每个参数的键和值分别进行URL编码，并拼接
    const baseStringParts: string[] = []
    for (const key of sortedKeys) {
      const encodedKey = this.urlEncode(key)
      const value = String(params[key])
      const encodedValue = this.urlEncode(value)
      baseStringParts.push(`${encodedKey}=${encodedValue}`)
    }

    // 3. 拼接所有参数，用&连接
    const baseString = baseStringParts.join('&')

    // 4. 使用HmacSHA1加密
    const signatureSha = CryptoJS.HmacSHA1(baseString, this.config.accessKeySecret)
    const signature = CryptoJS.enc.Base64.stringify(signatureSha)

    return signature
  }

  /**
   * 注册声纹特征
   * @param audioData 音频数据（PCM格式的Int16Array）
   * @param audioType 音频类型：raw、speex、opus-ogg
   * @param uid 用户ID（可选）
   */
  async registerVoiceprint(
    audioData: Int16Array,
    audioType: 'raw' | 'speex' | 'opus-ogg' = 'raw',
    uid?: string,
  ): Promise<VoiceprintRegisterFullResponse> {
    // 将音频数据转换为Base64
    const audioBase64 = this.arrayBufferToBase64(audioData.buffer)

    // 获取请求时间
    const dateTime = this.getUTCString()
    const signatureRandom = this.generateRandomString()

    // 构建Query参数
    const queryParams: Record<string, string | number> = {
      appId: this.config.appId,
      accessKeyId: this.config.accessKeyId,
      dateTime: dateTime,
      signatureRandom: signatureRandom,
    }

    // 生成签名
    const signature = this.generateSignature(queryParams)

    // 构建请求URL（使用代理路径避免CORS问题）
    const baseUrl = '/api/xunfei-voiceprint/res/feature/v1/register'
    const queryString = Object.entries(queryParams)
      .map(([key, value]) => `${this.urlEncode(key)}=${this.urlEncode(String(value))}`)
      .join('&')
    const url = `${baseUrl}?${queryString}`

    // 构建请求体
    const body: Record<string, string> = {
      audio_data: audioBase64,
      audio_type: audioType,
    }
    if (uid) {
      body.uid = uid
    }

    // 发送请求
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        signature: signature,
      },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`)
    }

    const result: VoiceprintRegisterResponse = await response.json()

    if (result.code !== '000000') {
      throw new Error(`API error! code: ${result.code}, desc: ${result.desc}`)
    }

    // 解析data字段（JSON字符串）
    const data: VoiceprintRegisterData = JSON.parse(result.data)

    if (data.status !== 1) {
      throw new Error(`Registration failed! status: ${data.status}`)
    }

    // 返回完整响应信息
    return {
      feature_id: data.feature_id,
      status: data.status,
      sid: result.sid,
      code: result.code,
      desc: result.desc,
    }
  }

  /**
   * 更新声纹特征
   * @param featureId 声纹特征ID
   * @param audioData 音频数据（PCM格式的Int16Array）
   * @param audioType 音频类型：raw、speex、opus-ogg
   */
  async updateVoiceprint(
    featureId: string,
    audioData: Int16Array,
    audioType: 'raw' | 'speex' | 'opus-ogg' = 'raw',
  ): Promise<VoiceprintUpdateFullResponse> {
    // 将音频数据转换为Base64
    const audioBase64 = this.arrayBufferToBase64(audioData.buffer)

    // 获取请求时间
    const dateTime = this.getUTCString()
    const signatureRandom = this.generateRandomString()

    // 构建Query参数
    const queryParams: Record<string, string | number> = {
      appId: this.config.appId,
      accessKeyId: this.config.accessKeyId,
      dateTime: dateTime,
      signatureRandom: signatureRandom,
    }

    // 生成签名
    const signature = this.generateSignature(queryParams)

    // 构建请求URL（使用代理路径避免CORS问题）
    const baseUrl = '/api/xunfei-voiceprint/res/feature/v1/update'
    const queryString = Object.entries(queryParams)
      .map(([key, value]) => `${this.urlEncode(key)}=${this.urlEncode(String(value))}`)
      .join('&')
    const url = `${baseUrl}?${queryString}`

    // 构建请求体
    const body = {
      audio_data: audioBase64,
      audio_type: audioType,
      feature_id: featureId,
    }

    // 发送请求
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        signature: signature,
      },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`)
    }

    const result: VoiceprintUpdateResponse = await response.json()

    if (result.code !== '000000') {
      throw new Error(`API error! code: ${result.code}, desc: ${result.desc}`)
    }

    // 解析data字段（JSON字符串）
    const data: VoiceprintUpdateData = JSON.parse(result.data)

    if (data.status !== 1) {
      throw new Error(`Update failed! status: ${data.status}`)
    }

    // 返回完整响应信息
    return {
      status: data.status,
      sid: result.sid,
      code: result.code,
      desc: result.desc,
    }
  }

  /**
   * ArrayBuffer 转 Base64
   */
  private arrayBufferToBase64(buffer: ArrayBufferLike): string {
    const bytes = new Uint8Array(buffer as ArrayBuffer)
    let binary = ''
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i])
    }
    return btoa(binary)
  }
}

