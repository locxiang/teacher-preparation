/**
 * 阿里云智能语音交互（ISI）实时语音识别服务
 * 使用WebSocket协议直接连接阿里云NLS服务
 * 参考文档：https://help.aliyun.com/zh/isi/developer-reference/websocket-protocol-description
 */

// API 基础 URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

// NLS WebSocket网关地址（上海）
const NLS_WS_URL = 'wss://nls-gateway-cn-shanghai.aliyuncs.com/ws/v1'

// 识别结果回调类型
export type RecognitionCallback = (result: RecognitionResult) => void
export type ErrorCallback = (error: Error) => void

// 识别结果接口
export interface RecognitionResult {
  text: string
  isFinal: boolean
  timestamp: number
  confidence?: number
}

export class AliyunISIASRService {
  private ws: WebSocket | null = null
  private isRecording = false
  private onResultCallback: RecognitionCallback | null = null
  private onErrorCallback: ErrorCallback | null = null
  private audioContext: AudioContext | null = null
  private mediaStream: MediaStream | null = null
  private audioProcessor: ScriptProcessorNode | AudioWorkletNode | null = null
  private analyser: AnalyserNode | null = null
  private audioDataCallback: ((data: Uint8Array) => void) | null = null

  private taskId = '' // 任务ID，32位hex字符串
  private appKey = '' // AppKey
  private token = '' // Token

  private startTranscriptionSent = false // 是否已发送StartTranscription
  private recordingStartTime = 0 // 录音开始时间

  /**
   * 生成32位hex字符串
   */
  private generateId(): string {
    const chars = '0123456789abcdef'
    let result = ''
    for (let i = 0; i < 32; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length))
    }
    return result
  }

  /**
   * 获取NLS Token和AppKey
   */
  private async getNLSToken(): Promise<{ token: string; app_key: string }> {
    const token = localStorage.getItem('access_token')
    if (!token) {
      throw new Error('未登录')
    }

    const response = await fetch(`${API_BASE_URL}/api/tts/token`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      const data = await response.json().catch(() => ({}))
      throw new Error(data.message || '获取Token失败')
    }

    const data = await response.json()
    return {
      token: data.token,
      app_key: data.app_key,
    }
  }

  /**
   * 连接WebSocket
   */
  private async connect(): Promise<void> {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      return
    }

    // 获取Token和AppKey
    const { token, app_key } = await this.getNLSToken()
    this.token = token
    this.appKey = app_key
    this.taskId = this.generateId()

    const wsUrl = `${NLS_WS_URL}?token=${token}`
    console.log('[ISI ASR] 连接WebSocket:', wsUrl.substring(0, 100) + '...')

    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(wsUrl)
        this.startTranscriptionSent = false

        this.ws.onopen = () => {
          console.log('[ISI ASR] WebSocket连接已建立')
          resolve()
        }

        this.ws.onmessage = (event) => {
          this.handleWebSocketMessage(event.data)
        }

        this.ws.onerror = (error) => {
          console.error('[ISI ASR] WebSocket错误:', error)
          this.onErrorCallback?.(new Error('WebSocket连接错误'))
          reject(new Error('WebSocket连接错误'))
        }

        this.ws.onclose = (event) => {
          console.log('[ISI ASR] WebSocket连接已关闭:', event.code, event.reason)
          this.isRecording = false
          this.startTranscriptionSent = false
        }
      } catch (error) {
        console.error('[ISI ASR] WebSocket连接异常:', error)
        reject(error)
      }
    })
  }

  /**
   * 发送StartTranscription指令
   */
  private sendStartTranscription(): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('[ISI ASR] WebSocket未连接，无法发送StartTranscription')
      return
    }

    if (this.startTranscriptionSent) {
      return
    }

    const messageId = this.generateId()
    const startMessage = {
      header: {
        appkey: this.appKey,
        message_id: messageId,
        task_id: this.taskId,
        namespace: 'SpeechTranscriber',
        name: 'StartTranscription',
      },
      payload: {
        format: 'PCM',
        sample_rate: 16000,
        enable_intermediate_result: true, // 返回中间结果
        enable_punctuation_prediction: true, // 添加标点
        enable_inverse_text_normalization: true, // 中文数字转阿拉伯数字
        max_sentence_silence: 2000, // 语音断句检测阈值，2000ms，避免无意义中断
      },
    }

    try {
      this.ws.send(JSON.stringify(startMessage))
      this.startTranscriptionSent = true
      this.recordingStartTime = Date.now()
      console.log('[ISI ASR] 已发送StartTranscription指令')
    } catch (error) {
      console.error('[ISI ASR] 发送StartTranscription失败:', error)
    }
  }

  /**
   * 发送StopTranscription指令
   */
  private sendStopTranscription(): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      return
    }

    const messageId = this.generateId()
    const stopMessage = {
      header: {
        appkey: this.appKey,
        message_id: messageId,
        task_id: this.taskId,
        namespace: 'SpeechTranscriber',
        name: 'StopTranscription',
      },
      payload: {},
    }

    try {
      this.ws.send(JSON.stringify(stopMessage))
      console.log('[ISI ASR] 已发送StopTranscription指令')
    } catch (error) {
      console.error('[ISI ASR] 发送StopTranscription失败:', error)
    }
  }

  /**
   * 处理WebSocket消息
   */
  private handleWebSocketMessage(data: string | ArrayBuffer | Blob): void {
    try {
      // 处理二进制数据（音频确认等）
      if (data instanceof ArrayBuffer || data instanceof Blob) {
        console.debug('[ISI ASR] 收到二进制消息，忽略')
        return
      }

      // 解析JSON消息
      const message = JSON.parse(data as string)
      console.log('[ISI ASR] 收到消息:', JSON.stringify(message, null, 2))

      const header = message.header || {}
      const payload = message.payload || {}
      const eventName = header.name || ''

      // 检查错误
      const status = header.status
      if (status !== undefined && status !== 20000000) {
        const statusText = header.status_text || '未知错误'
        console.error(`[ISI ASR] 错误: Status=${status}, Message=${statusText}`)
        this.onErrorCallback?.(new Error(`识别错误: ${statusText} (状态码: ${status})`))
        return
      }

      let text: string | null = null
      let isFinal = false
      let confidence: number | undefined = undefined

      // 根据事件类型处理
      switch (eventName) {
        case 'TranscriptionStarted':
          console.log('[ISI ASR] 语音识别已启动')
          break

        case 'TranscriptionResultChanged':
          // 中间结果
          text = payload.result || ''
          isFinal = false
          console.log('[ISI ASR] 中间结果:', text)
          break

        case 'SentenceEnd':
          // 最终结果
          text = payload.result || ''
          isFinal = true
          confidence = payload.confidence
          console.log('[ISI ASR] 最终结果:', text)
          break

        case 'TranscriptionCompleted':
          console.log('[ISI ASR] 语音识别已完成')
          this.isRecording = false
          break

        default:
          console.debug('[ISI ASR] 未处理的事件:', eventName)
      }

      // 调用回调
      if (text && this.onResultCallback) {
        this.onResultCallback({
          text,
          isFinal,
          timestamp: Date.now(),
          confidence,
        })
      }
    } catch (error) {
      console.error('[ISI ASR] 处理消息失败:', error)
    }
  }

  /**
   * 设置识别结果回调
   */
  onResult(callback: RecognitionCallback): void {
    this.onResultCallback = callback
  }

  /**
   * 设置错误回调
   */
  onError(callback: ErrorCallback): void {
    this.onErrorCallback = callback
  }

  /**
   * 设置音频数据回调（用于可视化）
   */
  onAudioData(callback: (data: Uint8Array) => void): void {
    this.audioDataCallback = callback
  }

  /**
   * 开始识别
   */
  async startRecognition(externalStream?: MediaStream): Promise<void> {
    if (this.isRecording) {
      console.warn('[ISI ASR] 已在录音中')
      return
    }

    try {
      // 1. 连接WebSocket
      await this.connect()

      // 2. 获取或使用外部MediaStream
      if (externalStream) {
        this.mediaStream = externalStream
        console.log('[ISI ASR] 使用外部MediaStream')
      } else {
        this.mediaStream = await navigator.mediaDevices.getUserMedia({
          audio: {
            sampleRate: 16000,
            channelCount: 1,
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true,
          },
        })
        console.log('[ISI ASR] 创建内部MediaStream')
      }

      // 3. 设置音频处理
      await this.setupAudioProcessing()

      // 4. 发送StartTranscription指令
      this.sendStartTranscription()

      this.isRecording = true
      console.log('[ISI ASR] 语音识别已启动')
    } catch (error) {
      this.isRecording = false
      const err = error instanceof Error ? error : new Error('启动识别失败')
      this.onErrorCallback?.(err)
      throw err
    }
  }

  /**
   * 设置音频处理
   */
  private async setupAudioProcessing(): Promise<void> {
    if (!this.mediaStream) {
      throw new Error('MediaStream未设置')
    }

    this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({
      sampleRate: 16000,
    })

    const source = this.audioContext.createMediaStreamSource(this.mediaStream)
    this.analyser = this.audioContext.createAnalyser()
    this.analyser.fftSize = 2048

    source.connect(this.analyser)

    // 创建音频处理器
    const bufferSize = 4096
    this.audioProcessor = this.audioContext.createScriptProcessor(bufferSize, 1, 1)

    this.audioProcessor.onaudioprocess = (event) => {
      if (!this.isRecording || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
        return
      }

      const inputData = event.inputBuffer.getChannelData(0)

      // 转换为16位PCM
      const pcmData = new Int16Array(inputData.length)
      for (let i = 0; i < inputData.length; i++) {
        const s = Math.max(-1, Math.min(1, inputData[i]))
        pcmData[i] = s < 0 ? s * 0x8000 : s * 0x7FFF
      }

      // 发送音频数据（Binary Frame）
      try {
        this.ws.send(pcmData.buffer)
      } catch (error) {
        console.error('[ISI ASR] 发送音频数据失败:', error)
      }

      // 音频可视化
      if (this.audioDataCallback) {
        const uint8Data = new Uint8Array(inputData.length)
        for (let i = 0; i < inputData.length; i++) {
          uint8Data[i] = Math.abs(inputData[i]) * 255
        }
        this.audioDataCallback(uint8Data)
      }
    }

    this.analyser.connect(this.audioProcessor)
    this.audioProcessor.connect(this.audioContext.destination)
  }

  /**
   * 停止识别
   */
  stopRecognition(): void {
    if (!this.isRecording) {
      return
    }

    // 发送StopTranscription指令
    this.sendStopTranscription()

    // 清理资源
    if (this.audioProcessor) {
      this.audioProcessor.disconnect()
      this.audioProcessor = null
    }

    if (this.analyser) {
      this.analyser.disconnect()
      this.analyser = null
    }

    if (this.audioContext) {
      this.audioContext.close()
      this.audioContext = null
    }

    if (this.mediaStream && !this.mediaStream.getTracks().some(track => track.readyState === 'ended')) {
      this.mediaStream.getTracks().forEach(track => track.stop())
    }
    this.mediaStream = null

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.close()
    }
    this.ws = null

    this.isRecording = false
    this.startTranscriptionSent = false
    console.log('[ISI ASR] 语音识别已停止')
  }
}

