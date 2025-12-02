/**
 * 阿里云通义听悟直接WebSocket连接服务
 * 前端直接连接到阿里云WebSocket，不通过后端中转
 */
import type { RecognitionCallback, ErrorCallback } from './aliyun-asr'

// 识别结果接口
interface RecognitionResult {
  text: string
  isFinal: boolean
  timestamp: number
  speaker?: string
  confidence?: number
}

export class AliyunASRDirectService {
  private ws: WebSocket | null = null
  private meetingId: string | null = null
  private isRecording = false
  private onResultCallback: RecognitionCallback | null = null
  private onErrorCallback: ErrorCallback | null = null
  private audioContext: AudioContext | null = null
  private mediaStream: MediaStream | null = null
  private audioProcessor: ScriptProcessorNode | AudioWorkletNode | null = null
  private analyser: AnalyserNode | null = null
  private audioDataCallback: ((data: Uint8Array) => void) | null = null
  private audioDataBuffer: number[] = [] // 音频数据缓冲区
  private sendInterval: number | null = null // 发送定时器
  private connectionEvent: Promise<void> | null = null // 连接事件
  private startTranscriptionSent = false // 是否已发送StartTranscription

  /**
   * 连接WebSocket
   * @param wsUrl WebSocket URL（从后端获取的MeetingJoinUrl）
   */
  async connect(wsUrl: string): Promise<void> {
    console.log('=== 开始连接阿里云WebSocket ===')
    console.log('WebSocket URL:', wsUrl)

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log('WebSocket已连接，跳过')
      return
    }

    return new Promise((resolve, reject) => {
      try {
        console.log('创建WebSocket实例...')
        this.ws = new WebSocket(wsUrl)
        this.startTranscriptionSent = false

        this.ws.onopen = () => {
          console.log('=== 阿里云WebSocket连接已建立 ===')
          console.log('ReadyState:', this.ws?.readyState)
          console.log('Protocol:', this.ws?.protocol)
          // 发送StartTranscription消息
          this.sendStartTranscription()
          resolve()
        }

        this.ws.onmessage = (event) => {
          console.debug('收到WebSocket消息:', event.data instanceof Blob ? `Blob(${event.data.size} bytes)` : event.data)
          this.handleWebSocketMessage(event.data)
        }

        this.ws.onerror = (error) => {
          console.error('=== WebSocket错误 ===')
          console.error('错误事件:', error)
          console.error('ReadyState:', this.ws?.readyState)
          console.error('URL:', wsUrl)
          const err = new Error('WebSocket连接错误')
          this.onErrorCallback?.(err)
          reject(err)
        }

        this.ws.onclose = (event) => {
          console.log('=== WebSocket连接已关闭 ===')
          console.log('关闭码:', event.code)
          console.log('关闭原因:', event.reason)
          console.log('是否正常关闭:', event.wasClean)
          this.isRecording = false
          this.startTranscriptionSent = false
        }

        console.log('WebSocket事件监听器已设置')
      } catch (error) {
        console.error('=== WebSocket连接异常 ===')
        console.error('异常类型:', error instanceof Error ? error.constructor.name : typeof error)
        console.error('异常信息:', error)
        if (error instanceof Error) {
          console.error('异常堆栈:', error.stack)
        }
        const err = error instanceof Error ? error : new Error('WebSocket连接失败')
        this.onErrorCallback?.(err)
        reject(err)
      }
    })
  }

  /**
   * 发送StartTranscription消息
   */
  private sendStartTranscription(): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket未连接，无法发送StartTranscription')
      return
    }

    if (this.startTranscriptionSent) {
      return
    }

    try {
      const startMessage = {
        header: {
          name: 'StartTranscription',
          namespace: 'SpeechTranscriber',
        },
        payload: {
          format: 'pcm',
          sample_rate: 16000,
        },
      }

      this.ws.send(JSON.stringify(startMessage))
      this.startTranscriptionSent = true
      console.log('已发送StartTranscription消息')
    } catch (error) {
      console.error('发送StartTranscription失败:', error)
    }
  }

  /**
   * 处理WebSocket消息
   */
  private handleWebSocketMessage(data: string | ArrayBuffer | Blob): void {
    try {
      // 处理二进制数据（音频确认等）
      if (data instanceof ArrayBuffer || data instanceof Blob) {
        console.debug('收到二进制消息，忽略')
        return
      }

      // 解析JSON消息
      const message = JSON.parse(data as string)
      console.log('收到阿里云WebSocket消息:', message)

      // 根据阿里云文档解析消息格式
      // 参考：https://help.aliyun.com/zh/tingwu/js-push-stream
      const header = message.header || {}
      const payload = message.payload || {}
      const eventName = header.name || ''

      // 检查错误
      if (message.ErrorCode || message.error) {
        const errorCode = message.ErrorCode || message.error?.code
        const errorMsg = message.ErrorMessage || message.error?.message || '未知错误'
        console.error(`通义听悟返回错误: Code=${errorCode}, Message=${errorMsg}`)
        this.onErrorCallback?.(new Error(`通义听悟错误: ${errorMsg}`))
        return
      }

      let text: string | null = null
      let isFinal = false
      let timestamp = Date.now()
      let speaker: string | undefined = undefined

      // 根据事件类型处理
      switch (eventName) {
        case 'TranscriptionStarted':
          // 转写已启动
          console.log('语音识别已启动，任务ID:', header.task_id)
          break

        case 'SentenceBegin':
          console.debug('句子开始:', payload.index)
          break

        case 'TranscriptionResultChanged':
          // 中间结果
          text = payload.result || ''
          isFinal = false
          timestamp = payload.time || Date.now()
          console.debug('中间结果:', text)
          break

        case 'SentenceEnd':
          // 最终结果
          const resultText = payload.result || ''
          text = resultText.trim()
          isFinal = true
          timestamp = payload.time || Date.now()
          // 提取说话人信息（如果有）
          const speakerId = payload.speaker_id || payload.speakerId || payload.role_id || payload.roleId
          if (speakerId !== undefined && speakerId !== null) {
            // 将说话人ID转换为名称（0 -> 说话人1, 1 -> 说话人2, 等）
            speaker = `说话人${Number(speakerId) + 1}`
          }
          console.log('最终结果:', text, '说话人:', speaker || '未知')
          break

        case 'ResultTranslated':
          // 翻译结果（暂不处理）
          console.debug('翻译结果:', payload.translate_result)
          break

        default:
          console.debug('未知事件类型:', eventName)
      }

      // 如果有识别文本，调用回调
      if (text && this.onResultCallback) {
        this.onResultCallback({
          text,
          isFinal,
          timestamp,
          speaker,
        })
      }
    } catch (error) {
      console.error('处理WebSocket消息失败:', error)
    }
  }

  /**
   * 开始识别
   * @param wsUrl WebSocket URL
   * @param externalStream 外部MediaStream（可选）
   */
  async startRecognition(wsUrl: string, externalStream?: MediaStream): Promise<void> {
    if (this.isRecording) {
      console.warn('Already recording')
      return
    }

    try {
      // 1. 连接WebSocket
      await this.connect(wsUrl)

      // 2. 获取或使用外部MediaStream
      if (externalStream) {
        this.mediaStream = externalStream
        console.log('Using external MediaStream')
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
        console.log('Created internal MediaStream')
      }

      // 3. 设置音频处理
      await this.setupAudioProcessing()

      this.isRecording = true
      console.log('语音识别已启动')
    } catch (error) {
      this.isRecording = false
      const err = error instanceof Error ? error : new Error('Failed to start recognition')
      this.onErrorCallback?.(err)
      throw err
    }
  }

  /**
   * 设置音频处理
   */
  private async setupAudioProcessing(): Promise<void> {
    if (!this.mediaStream) {
      throw new Error('MediaStream is not available')
    }

    if (!this.audioContext) {
      this.audioContext = new AudioContext({ sampleRate: 16000 })
      console.log('Created AudioContext with sample rate:', this.audioContext.sampleRate)
    }

    const source = this.audioContext.createMediaStreamSource(this.mediaStream)

    // 创建AnalyserNode用于音频可视化
    this.analyser = this.audioContext.createAnalyser()
    this.analyser.fftSize = 256
    this.analyser.smoothingTimeConstant = 0.8
    source.connect(this.analyser)

    // 创建ScriptProcessorNode用于音频数据处理
    const bufferSize = 4096
    this.audioProcessor = this.audioContext.createScriptProcessor(bufferSize, 1, 1)

    this.audioProcessor.onaudioprocess = (e) => {
      if (!this.isRecording) return

      const inputData = e.inputBuffer.getChannelData(0)

      // 转换为PCM格式（16位整数）
      const pcmData = new Int16Array(inputData.length)
      for (let i = 0; i < inputData.length; i++) {
        const s = Math.max(-1, Math.min(1, inputData[i]))
        pcmData[i] = s < 0 ? s * 0x8000 : s * 0x7fff
      }

      // 添加到缓冲区
      this.audioDataBuffer.push(...Array.from(pcmData))

      // 限制缓冲区大小
      if (this.audioDataBuffer.length > 12800) {
        this.audioDataBuffer = this.audioDataBuffer.slice(-6400)
      }

      // 更新音频可视化（同时发送频率数据和时域数据）
      if (this.analyser && this.audioDataCallback) {
        // 频率数据用于可视化
        const frequencyData = new Uint8Array(this.analyser.frequencyBinCount)
        this.analyser.getByteFrequencyData(frequencyData)

        // 时域数据用于音量检测
        const timeData = new Uint8Array(this.analyser.fftSize)
        this.analyser.getByteTimeDomainData(timeData)

        // 传递时域数据用于音量检测
        this.audioDataCallback(timeData)
      }
    }

    source.connect(this.audioProcessor)
    this.audioProcessor.connect(this.audioContext.destination)

    // 开始发送音频数据
    this.startSendingAudio()
  }

  /**
   * 开始发送音频数据
   */
  private startSendingAudio(): void {
    if (this.sendInterval) {
      clearInterval(this.sendInterval)
    }

    // 每40ms发送1280字节（16000Hz采样率，16位，单声道）
    this.sendInterval = window.setInterval(() => {
      if (!this.isRecording || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
        if (this.sendInterval) {
          clearInterval(this.sendInterval)
          this.sendInterval = null
        }
        return
      }

      // 确保已发送StartTranscription
      if (!this.startTranscriptionSent) {
        this.sendStartTranscription()
      }

      // 提取1280字节音频数据
      if (this.audioDataBuffer.length >= 1280) {
        const chunk = this.audioDataBuffer.splice(0, 1280)
        const audioBytes = new Int16Array(chunk)

        try {
          // 发送二进制音频数据
          this.ws.send(audioBytes.buffer)
        } catch (error) {
          console.error('发送音频数据失败:', error)
        }
      }
    }, 40)
  }

  /**
   * 停止识别
   */
  stopRecognition(): void {
    this.isRecording = false

    // 停止发送音频数据
    if (this.sendInterval) {
      clearInterval(this.sendInterval)
      this.sendInterval = null
    }

    // 发送StopTranscription消息
    if (this.ws && this.ws.readyState === WebSocket.OPEN && this.startTranscriptionSent) {
      try {
        const stopMessage = {
          header: {
            name: 'StopTranscription',
            namespace: 'SpeechTranscriber',
          },
          payload: {},
        }
        this.ws.send(JSON.stringify(stopMessage))
        console.log('已发送StopTranscription消息')
      } catch (error) {
        console.error('发送StopTranscription失败:', error)
      }
    }

    // 关闭WebSocket连接
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }

    // 清理音频资源
    if (this.audioProcessor) {
      this.audioProcessor.disconnect()
      this.audioProcessor = null
    }

    if (this.audioContext) {
      this.audioContext.close()
      this.audioContext = null
    }

    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach((track) => track.stop())
      this.mediaStream = null
    }

    this.startTranscriptionSent = false
    console.log('语音识别已停止')
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
}

