import { io, Socket } from 'socket.io-client'

// 识别结果接口
export interface RecognitionResult {
  text: string
  isFinal: boolean
  timestamp: number
  speaker?: string
  confidence?: number
}

// 识别回调
export type RecognitionCallback = (result: RecognitionResult) => void
export type ErrorCallback = (error: Error) => void

/**
 * 阿里云语音识别服务（通过后端WebSocket）
 */
export class AliyunASRService {
  private socket: Socket | null = null
  private meetingId: string | null = null
  private isRecording = false
  private onResultCallback: RecognitionCallback | null = null
  private onErrorCallback: ErrorCallback | null = null
  private audioContext: AudioContext | null = null
  private mediaStream: MediaStream | null = null
  private audioProcessor: ScriptProcessorNode | AudioWorkletNode | null = null
  private analyser: AnalyserNode | null = null
  private audioDataCallback: ((data: Uint8Array) => void) | null = null
  private audioDataBuffer: number[] = [] // 音频数据缓冲区（参考 DemoXunfei2.vue）
  private sendInterval: number | null = null // 发送定时器（参考 DemoXunfei2.vue）

  constructor(serverUrl = '') {
    // 如果没有提供serverUrl，使用当前域名
    // 在生产环境通过 Nginx 代理，WebSocket 会自动代理到后端
    const baseUrl = serverUrl || window.location.origin
    this.socket = io(baseUrl, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
      autoConnect: true, // 自动连接
    })

    this.setupSocketListeners()

    // 如果socket还没有连接，尝试连接
    if (!this.socket.connected) {
      this.socket.connect()
    }
  }

  /**
   * 设置WebSocket事件监听
   */
  private setupSocketListeners() {
    if (!this.socket) return

    this.socket.on('connect', () => {
      console.log('WebSocket连接已建立')
    })

    this.socket.on('disconnect', () => {
      console.log('WebSocket连接已断开')
    })

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket连接错误:', error)
    })

    this.socket.on('connected', (data) => {
      console.log('服务器连接确认:', data)
    })

    this.socket.on('transcript_update', (data: {
      meeting_id: string
      text: string
      is_final?: boolean
      timestamp?: number
      confidence?: number
      speaker?: string
    }) => {
      if (this.onResultCallback) {
        const result: RecognitionResult = {
          text: data.text,
          isFinal: data.is_final ?? false,
          timestamp: data.timestamp ?? Date.now(),
          confidence: data.confidence,
          speaker: data.speaker, // 添加说话人信息
        }
        this.onResultCallback(result)
      }
    })

    this.socket.on('error', (data: { message: string }) => {
      console.error('WebSocket错误:', data)
      if (this.onErrorCallback) {
        this.onErrorCallback(new Error(data.message || '未知错误'))
      }
    })

    this.socket.on('recognition_started', (data) => {
      console.log('语音识别已启动:', data)
    })

    this.socket.on('recognition_stopped', (data) => {
      console.log('语音识别已停止:', data)
    })
  }

  /**
   * 等待WebSocket连接
   */
  private async waitForConnection(maxWaitTime = 5000): Promise<void> {
    if (this.socket && this.socket.connected) {
      return
    }

    return new Promise((resolve, reject) => {
      if (!this.socket) {
        reject(new Error('WebSocket未初始化'))
        return
      }

      const startTime = Date.now()
      const checkInterval = setInterval(() => {
        if (this.socket && this.socket.connected) {
          clearInterval(checkInterval)
          resolve()
        } else if (Date.now() - startTime > maxWaitTime) {
          clearInterval(checkInterval)
          reject(new Error('WebSocket连接超时'))
        }
      }, 100)
    })
  }

  /**
   * 初始化并开始识别
   * @param meetingId 会议ID
   * @param externalStream 外部传入的 MediaStream（可选）
   * @param streamUrl 通义听悟推流URL（可选，Demo场景使用）
   */
  async startRecognition(meetingId: string, externalStream?: MediaStream, streamUrl?: string): Promise<void> {
    if (this.isRecording) {
      console.warn('Already recording')
      return
    }

    // 等待WebSocket连接
    try {
      await this.waitForConnection()
      console.log('WebSocket已连接，可以开始识别')
    } catch (error) {
      console.error('等待WebSocket连接失败:', error)
      throw new Error('WebSocket连接失败，请稍后重试')
    }

    try {
      this.meetingId = meetingId

      // 1. 加入会议房间（Demo场景允许跳过）
      if (!meetingId.startsWith('mock_task_')) {
        this.socket.emit('join_meeting', { meeting_id: meetingId })
      }

      // 2. 启动语音识别（Demo场景传递stream_url）
      const startData: { meeting_id: string; stream_url?: string } = { meeting_id: meetingId }
      if (streamUrl) {
        startData.stream_url = streamUrl
      }
      this.socket.emit('start_recognition', startData)

      // 3. 获取麦克风权限（如果外部没有传入 stream）
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

      // 4. 设置音频处理
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
  private async setupAudioProcessing() {
    console.log('=== Setting up Audio Processing ===')

    if (!this.mediaStream) {
      throw new Error('MediaStream is not available')
    }

    if (!this.audioContext) {
      this.audioContext = new AudioContext({ sampleRate: 16000 })
      console.log('Created AudioContext with sample rate:', this.audioContext.sampleRate)
    }

    const source = this.audioContext.createMediaStreamSource(this.mediaStream)
    console.log('Created MediaStreamSource')

    // 创建 AnalyserNode 用于音频可视化
    this.analyser = this.audioContext.createAnalyser()
    this.analyser.fftSize = 256
    this.analyser.smoothingTimeConstant = 0.8
    source.connect(this.analyser)
    console.log('Created AnalyserNode')

    // 使用 AudioWorklet（现代方式）
    try {
      await this.audioContext.audioWorklet.addModule('/audio-processor.worklet.js')
      this.audioProcessor = new AudioWorkletNode(this.audioContext, 'audio-processor')
      console.log('Created AudioWorkletNode')

      this.audioProcessor.port.start()

      // 处理来自 AudioWorklet 的消息（参考 DemoXunfei2.vue）
      this.audioProcessor.port.onmessage = (event) => {
        if (!this.isRecording) {
          return
        }

        if (event.data.type !== 'audioData') {
          return
        }

        const audioArray = event.data.data as number[]
        if (!audioArray || audioArray.length === 0) {
          return
        }

        // 将音频数据添加到缓冲区（参考 DemoXunfei2.vue）
        this.audioDataBuffer.push(...audioArray)

        // 限制缓冲区大小，避免内存溢出（参考 DemoXunfei2.vue）
        if (this.audioDataBuffer.length > 12800) {
          this.audioDataBuffer = this.audioDataBuffer.slice(-6400) // 保留最近的数据
        }
      }

      source.connect(this.audioProcessor)
      const gainNode = this.audioContext.createGain()
      gainNode.gain.value = 0 // 静音输出
      this.audioProcessor.connect(gainNode)
      gainNode.connect(this.audioContext.destination)
      console.log('Audio processing pipeline connected (AudioWorklet)')
    } catch (error) {
      console.error('❌ Failed to initialize AudioWorklet:', error)
      throw new Error(`AudioWorklet initialization failed: ${error instanceof Error ? error.message : String(error)}`)
    }

    // 启动音频数据发送循环（参考 DemoXunfei2.vue，每40ms发送1280字节）
    this.startAudioDataSending()

    // 启动音频数据更新循环（用于可视化）
    this.startAudioDataUpdate()
  }

  /**
   * 启动音频数据发送循环（参考 DemoXunfei2.vue 的 webSocketSend）
   */
  private startAudioDataSending() {
    // 清理旧的定时器
    if (this.sendInterval !== null) {
      clearInterval(this.sendInterval)
      this.sendInterval = null
    }

    // 等待一些音频数据积累后再开始发送
    if (this.audioDataBuffer.length === 0) {
      console.log('音频数据为空，等待数据积累...')
      setTimeout(() => {
        if (this.isRecording) {
          this.startAudioDataSending()
        }
      }, 100)
      return
    }

    // 记录开始发送时间（用于精确控制发送节奏）
    let frameIndex = 0
    const startTime = Date.now()

    // 设置定时器，每40ms发送1280字节（参考 DemoXunfei2.vue）
    this.sendInterval = window.setInterval(() => {
      // WebSocket未连接
      if (!this.socket || !this.socket.connected) {
        console.warn('WebSocket未连接，停止发送音频数据')
        this.audioDataBuffer = []
        if (this.sendInterval !== null) {
          clearInterval(this.sendInterval)
          this.sendInterval = null
        }
        return
      }

      // 如果用户停止录音，停止发送音频数据
      if (!this.isRecording) {
        console.log('用户停止录音，停止发送音频数据')
        this.audioDataBuffer = []
        if (this.sendInterval !== null) {
          clearInterval(this.sendInterval)
          this.sendInterval = null
        }
        return
      }

      // 如果音频数据为空，继续等待
      if (this.audioDataBuffer.length === 0) {
        return
      }

      // 计算理论发送时间（基于开始时间和帧索引）
      const expectedSendTime = startTime + (frameIndex * 40)
      const currentTime = Date.now()
      const timeDiff = expectedSendTime - currentTime

      // 提取1280字节音频数据（参考 DemoXunfei2.vue）
      const audioDataChunk = this.audioDataBuffer.splice(0, 1280)

      if (audioDataChunk.length > 0) {
        // 转换为 Float32Array
        const inputData = new Float32Array(audioDataChunk)
        // 转换为 PCM Int16Array
        const pcmData = this.floatTo16BitPCM(inputData)
        // 转换为Base64
        const base64 = this.arrayBufferToBase64(pcmData.buffer)

        try {
          // 通过 Socket.IO 发送音频数据到后端（后端会转发到阿里云）
          if (this.meetingId) {
            this.socket.emit('audio_data', {
              meeting_id: this.meetingId,
              audio_data: base64,
              format: 'pcm',
            })
          }

          frameIndex++

          // 每10帧打印一次日志
          if (frameIndex % 10 === 0) {
            console.log(`【节奏控制】帧${frameIndex} | 理论时间：${expectedSendTime}ms | 实际时间：${currentTime}ms | 误差：${timeDiff.toFixed(1)}ms`)
          }
        } catch (error) {
          console.error('发送音频数据失败:', error)
        }
      }
    }, 40) as unknown as number
  }

  /**
   * 启动音频数据更新循环
   */
  private startAudioDataUpdate() {
    if (!this.analyser) {
      return
    }

    const updateAudioData = () => {
      if (!this.isRecording) {
        if (this.audioDataCallback && this.analyser) {
          const emptyData = new Uint8Array(this.analyser.frequencyBinCount)
          this.audioDataCallback(emptyData)
        }
        return
      }

      if (!this.analyser) {
        return
      }

      const frequencyData = new Uint8Array(this.analyser.frequencyBinCount)
      this.analyser.getByteFrequencyData(frequencyData)

      if (this.audioDataCallback) {
        try {
          this.audioDataCallback(frequencyData)
        } catch (error) {
          console.error('❌ Error in audioDataCallback:', error)
        }
      }

      requestAnimationFrame(updateAudioData)
    }

    updateAudioData()
  }

  /**
   * Float32Array 转 Int16Array (PCM)
   */
  private floatTo16BitPCM(input: Float32Array): Int16Array {
    const output = new Int16Array(input.length)
    for (let i = 0; i < input.length; i++) {
      const s = Math.max(-1, Math.min(1, input[i]))
      output[i] = s < 0 ? s * 0x8000 : s * 0x7FFF
    }
    return output
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

  /**
   * 停止识别
   */
  stopRecognition() {
    if (!this.isRecording) {
      return
    }

    this.isRecording = false

    // 停止音频数据发送定时器（参考 DemoXunfei2.vue）
    if (this.sendInterval !== null) {
      clearInterval(this.sendInterval)
      this.sendInterval = null
    }

    // 清空音频数据缓冲区
    this.audioDataBuffer = []

    // 停止语音识别
    if (this.socket && this.meetingId) {
      this.socket.emit('stop_recognition', { meeting_id: this.meetingId })
    }

    // 停止音频处理
    if (this.audioProcessor) {
      this.audioProcessor.disconnect()
      this.audioProcessor = null
    }

    // 停止音频流
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop())
      this.mediaStream = null
    }

    // 关闭音频上下文
    if (this.audioContext) {
      this.audioContext.close()
      this.audioContext = null
    }

    this.analyser = null
  }

  /**
   * 设置识别结果回调
   */
  onResult(callback: RecognitionCallback) {
    this.onResultCallback = callback
  }

  /**
   * 设置错误回调
   */
  onError(callback: ErrorCallback) {
    this.onErrorCallback = callback
  }

  /**
   * 设置音频数据回调（用于可视化）
   */
  onAudioData(callback: (data: Uint8Array) => void) {
    this.audioDataCallback = callback
  }

  /**
   * 断开连接
   */
  disconnect() {
    this.stopRecognition()

    if (this.socket) {
      if (this.meetingId) {
        this.socket.emit('leave_meeting', { meeting_id: this.meetingId })
      }
      this.socket.disconnect()
      this.socket = null
    }

    this.meetingId = null
  }
}

