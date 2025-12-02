import CryptoJS from 'crypto-js'

// 科大讯飞配置
export interface XunfeiConfig {
  appId: string
  accessKeyId: string
  accessKeySecret: string
}

// 识别结果
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
 * 科大讯飞实时语音转写服务
 */
export class XunfeiASRService {
  private config: XunfeiConfig
  private ws: WebSocket | null = null
  private audioContext: AudioContext | null = null
  private mediaStream: MediaStream | null = null
  private audioProcessor: ScriptProcessorNode | AudioWorkletNode | null = null
  private isRecording = false
  private onResultCallback: RecognitionCallback | null = null
  private onErrorCallback: ErrorCallback | null = null
  private currentSpeaker: string | null = null
  private silenceTimer: number | null = null
  private lastSpeechTime = 0
  private audioSendCount = 0
  private analyser: AnalyserNode | null = null
  private audioDataCallback: ((data: Uint8Array) => void) | null = null

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
    const timezoneOffset = -now.getTimezoneOffset() // 注意：getTimezoneOffset返回的是UTC与本地时间的差值（分钟）
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
      // 将值转换为字符串后再编码
      const value = String(params[key])
      const encodedValue = this.urlEncode(value)
      baseStringParts.push(`${encodedKey}=${encodedValue}`)
    }

    // 3. 拼接所有参数，用&连接
    const baseString = baseStringParts.join('&')

    console.log('=== Signature Generation ===')
    console.log('Base string:', baseString)

    // 4. 使用HmacSHA1加密（注意：文档要求使用HmacSHA1，不是HmacSHA256）
    const signatureSha = CryptoJS.HmacSHA1(baseString, this.config.accessKeySecret)
    const signature = CryptoJS.enc.Base64.stringify(signatureSha)

    console.log('Generated signature:', signature)
    console.log('===========================')

    return signature
  }


  /**
   * 构建 WebSocket URL
   * 使用实时语音转写大模型 API
   * 按照文档要求构建URL参数并生成签名
   */
  private buildWebSocketUrl(): string {
    const host = 'office-api-ast-dx.iflyaisol.com'
    const path = '/ast/communicate/v1'

    // 获取 UTC 时间字符串（格式：2025-09-04T15:38:07+0800）
    const utc = this.getUTCString()
    const uuid = this.generateUUID()

    // 构建请求参数（不包含signature）
    // 注意：如果遇到"功能异常"错误，可能需要调整以下参数：
    // 2. role_type: 0-关闭说话人分离，1-开启，2-开启（可能需要特殊权限）
    const params: Record<string, string | number> = {
      accessKeyId: this.config.accessKeyId,
      appId: this.config.appId,
      uuid: uuid,
      utc: utc,
      pd: 'edu',
      audio_encode: 'pcm_s16le',
      lang: 'autodialect',
      samplerate: '16000',
      role_type: 0, // 说话人分离：0-关闭，1-开启，2-开启（可能需要特殊权限）
    }

    // 生成签名
    const signature = this.generateSignature(params)

    // 添加signature到参数中
    params.signature = signature

    // 构建查询字符串（需要对每个参数进行URL编码）
    const queryParts: string[] = []
    for (const [key, value] of Object.entries(params)) {
      const encodedKey = this.urlEncode(key)
      const encodedValue = this.urlEncode(String(value))
      queryParts.push(`${encodedKey}=${encodedValue}`)
    }
    const queryString = queryParts.join('&')

    const fullUrl = `wss://${host}${path}?${queryString}`

    console.log('=== URL Building ===')
    console.log('Full WebSocket URL:', fullUrl.substring(0, 200) + '...')
    console.log('===================')

    return fullUrl
  }

  /**
   * 生成 UUID
   */
  private generateUUID(): string {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0
      const v = c === 'x' ? r : (r & 0x3) | 0x8
      return v.toString(16)
    })
  }


  /**
   * 初始化并开始识别
   * @param externalStream 外部传入的 MediaStream（可选），如果不传入则内部获取
   */
  async startRecognition(externalStream?: MediaStream): Promise<void> {
    if (this.isRecording) {
      console.warn('Already recording')
      return
    }

    try {
      // 1. 获取麦克风权限（如果外部没有传入 stream）
      if (externalStream) {
        this.mediaStream = externalStream
        console.log('Using external MediaStream')

        // 验证外部流的采样率
        const audioTrack = externalStream.getAudioTracks()[0]
        if (audioTrack) {
          const settings = audioTrack.getSettings()
          console.log('External stream audio settings:', settings)
          if (settings.sampleRate && settings.sampleRate !== 16000) {
            console.warn(`⚠️ 警告: 外部音频流采样率为 ${settings.sampleRate}Hz，不是16000Hz`)
            console.warn('⚠️ 这可能导致API返回"功能异常"错误，建议使用16000Hz采样率')
          }
        }
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

        // 验证实际采样率
        const audioTrack = this.mediaStream.getAudioTracks()[0]
        if (audioTrack) {
          const settings = audioTrack.getSettings()
          console.log('Internal stream audio settings:', settings)
          if (settings.sampleRate && settings.sampleRate !== 16000) {
            console.warn(`⚠️ 警告: 实际音频采样率为 ${settings.sampleRate}Hz，不是16000Hz`)
            console.warn('⚠️ 浏览器可能不支持16000Hz采样率，将使用AudioContext进行重采样')
          }
        }
      }

      // 2. 建立 WebSocket 连接
      await this.connectWebSocket()

      // 3. 设置音频处理
      await this.setupAudioProcessing()

      this.isRecording = true
      this.lastSpeechTime = Date.now()
      this.startSilenceTimer()
    } catch (error) {
      const err = error instanceof Error ? error : new Error('Failed to start recognition')
      this.onErrorCallback?.(err)
      throw err
    }
  }

  /**
   * 连接 WebSocket
   */
  private connectWebSocket(): Promise<void> {
    return new Promise((resolve, reject) => {
      const url = this.buildWebSocketUrl()
      console.log('Connecting to WebSocket:', url.substring(0, 100) + '...')

      this.ws = new WebSocket(url)

      this.ws.onopen = () => {
        console.log('=== WebSocket Connected Successfully ===')
        console.log('WebSocket URL:', url.substring(0, 200) + '...')
        console.log('Ready state:', this.ws?.readyState)
        console.log('Protocol:', this.ws?.protocol)
        console.log('===============================')
        resolve()
      }

      this.ws.onmessage = (event) => {
        this.handleWebSocketMessage(event.data)
      }

      this.ws.onerror = (error) => {
        console.error('=== WebSocket Error Details ===')
        console.error('Error event:', error)
        console.error('WebSocket readyState:', this.ws?.readyState)
        console.error('Full URL length:', url.length)
        console.error('Full URL:', url)
        console.error('Access Key ID:', this.config.accessKeyId.substring(0, 10) + '...')
        console.error('App ID:', this.config.appId)
        console.error('Access Key Secret:', this.config.accessKeySecret.substring(0, 10) + '...')
        console.error('==============================')

        const err = new Error(`WebSocket connection failed. Check console for details. Error code: ${this.ws?.readyState}`)
        this.onErrorCallback?.(err)
        reject(err)
      }

      this.ws.onclose = (event) => {
        console.log('=== WebSocket Close Event ===')
        console.log('Close code:', event.code)
        console.log('Close reason:', event.reason || 'No reason provided')
        console.log('Was clean:', event.wasClean)

        // 常见错误码说明
        const errorCodes: Record<number, string> = {
          1000: '正常关闭',
          1001: '端点离开',
          1002: '协议错误',
          1003: '数据类型错误',
          1006: '异常关闭（可能是签名验证失败、网络问题或服务器拒绝连接）',
          1007: '数据格式错误',
          1011: '服务器错误',
          1015: 'TLS握手失败',
        }
        console.log('Error meaning:', errorCodes[event.code] || 'Unknown error code')
        console.log('============================')

        // 如果是签名验证失败（1006），不自动重连
        if (event.code === 1006) {
          console.error('⚠️ WebSocket连接被异常关闭，可能是签名验证失败')
          console.error('请检查：')
          console.error('1. API密钥配置是否正确')
          console.error('2. 签名算法是否正确')
          console.error('3. 时间格式是否正确')
          console.error('4. 网络连接是否正常')
        }

        if (this.isRecording && event.code !== 1000 && event.code !== 1006) {
          // 非正常关闭且不是签名错误，尝试重连
          console.log('Attempting to reconnect in 3 seconds...')
          setTimeout(() => {
            if (this.isRecording) {
              this.connectWebSocket().catch(console.error)
            }
          }, 3000)
        }
      }
    })
  }

  /**
   * 处理 WebSocket 消息
   */
  private handleWebSocketMessage(data: string) {
    console.log('=== WebSocket Message Received ===')
    console.log('Raw data:', data)
    console.log('Data type:', typeof data)
    console.log('Data length:', data.length)

    try {
      const result = JSON.parse(data)
      console.log('Parsed JSON:', JSON.stringify(result, null, 2))

      // 检查错误码
      if (result.code && result.code !== 0) {
        console.error('=== Recognition Error ===')
        console.error('Error code:', result.code)
        console.error('Error message:', result.message || result.msg)
        console.error('Full error object:', result)
        this.onErrorCallback?.(new Error(result.message || result.msg || 'Recognition failed'))
        return
      }

      // 打印完整的 result 结构
      console.log('=== Result Structure ===')
      console.log('result:', result)
      console.log('result.data:', result.data)
      console.log('result.data?.result:', result.data?.result)
      console.log('result.result:', result.result)
      console.log('result.msg_type:', result.msg_type)
      console.log('result.res_type:', result.res_type)

      // 处理不同类型的消息
      // 1. 状态消息（功能恢复正常等）
      if (result.data && result.data.desc && result.data.normal !== undefined) {
        console.log('=== Status Message ===')
        console.log('Status:', result.data.desc)
        console.log('Normal:', result.data.normal)
        console.log('Detail:', result.data.detail)
        console.log('===============================')

        // 如果 normal 为 false，表示功能异常，应该触发错误回调
        if (result.data.normal === false) {
          const errorMsg = result.data.desc || '功能异常'
          const detail = result.data.detail ? JSON.stringify(result.data.detail) : ''
          const fullErrorMsg = detail ? `${errorMsg} (${detail})` : errorMsg
          console.error('=== Function Error Detected ===')
          console.error('Error description:', errorMsg)
          console.error('Error detail:', result.data.detail)
          console.error('================================')
          this.onErrorCallback?.(new Error(fullErrorMsg))
        }
        return
      }

      // 2. 识别结果消息
      // 根据日志，结果结构可能是：
      // - result.data.result (旧格式)
      // - result.result (旧格式)
      // - result.data (新格式，包含 data, msg_type, res_type)
      let resultData = result.data?.result || result.result || result

      // 如果 resultData 有 data 字段，可能是嵌套结构
      if (resultData && resultData.data && typeof resultData.data === 'object') {
        console.log('=== Nested Data Structure ===')
        console.log('resultData.data:', resultData.data)
        // 尝试从 resultData.data 中提取文本
        const nestedData = resultData.data
        if (nestedData.text || nestedData.ws || nestedData.result) {
          resultData = nestedData.result || nestedData
        }
      }

      console.log('=== Result Data ===')
      console.log('resultData:', resultData)
      console.log('resultData.text:', resultData?.text)
      console.log('resultData.ws:', resultData?.ws)
      console.log('resultData.data:', resultData?.data)
      console.log('resultData.role_id:', resultData?.role_id)
      console.log('resultData.speaker_id:', resultData?.speaker_id)
      console.log('resultData keys:', resultData ? Object.keys(resultData) : 'resultData is null/undefined')

      // 尝试多种方式提取文本
      let text = ''
      let isFinal = false
      let speakerId: string | undefined = undefined
      let confidence: number | undefined = undefined

      // 方式1: 直接文本字段
      if (resultData?.text) {
        text = resultData.text
        isFinal = resultData.is_final === 1 || resultData.final === true
        speakerId = resultData.role_id || resultData.speaker_id || resultData.speaker
        confidence = resultData.confidence
      }
      // 方式2: ws 对象中的文本
      else if (resultData?.ws) {
        text = resultData.ws.text || ''
        isFinal = resultData.ws.is_final === 1 || resultData.ws.final === true
        speakerId = resultData.ws.role_id || resultData.ws.speaker_id || resultData.ws.speaker
        confidence = resultData.ws.confidence
      }
      // 方式3: data 字段中的文本（处理 res_type='frc' 的情况）
      else if (resultData?.data) {
        const data = resultData.data
        if (typeof data === 'string') {
          text = data
          // frc 类型通常是最终结果
          isFinal = result?.res_type === 'frc'
        } else if (typeof data === 'object') {
          text = data.text || data.ws?.text || ''
          isFinal = data.is_final === 1 || data.ws?.is_final === 1 || data.final === true || result?.res_type === 'frc'
          speakerId = data.role_id || data.speaker_id || data.speaker || data.ws?.role_id
          confidence = data.confidence || data.ws?.confidence
        }
      }

      console.log('=== Extracted Text ===')
      console.log('Text:', text)
      console.log('Is Final:', isFinal)
      console.log('Speaker ID:', speakerId)
      console.log('Confidence:', confidence)

      if (text && text.trim()) {
        const recognitionResult: RecognitionResult = {
          text: text.trim(),
          isFinal: isFinal,
          timestamp: Date.now(),
          speaker: speakerId || this.currentSpeaker || undefined,
          confidence: confidence,
        }

        console.log('=== Recognition Result ===')
        console.log('Recognition result:', recognitionResult)
        console.log('Has callback?', !!this.onResultCallback)

        // 更新当前说话人和最后发言时间
        if (recognitionResult.speaker) {
          this.currentSpeaker = recognitionResult.speaker
        }
        if (text.trim()) {
          this.lastSpeechTime = Date.now()
        }

        if (this.onResultCallback) {
          console.log('Calling onResultCallback...')
          this.onResultCallback(recognitionResult)
          console.log('onResultCallback called successfully')
        } else {
          console.warn('⚠️ No onResultCallback registered!')
        }
      } else {
        console.log('⚠️ No text found in result')
        console.log('Full resultData structure:', JSON.stringify(resultData, null, 2))
      }
      console.log('===============================')
    } catch (error) {
      console.error('=== Failed to parse WebSocket message ===')
      console.error('Error:', error)
      console.error('Raw data:', data)
      console.error('===============================')
    }
  }

  /**
   * 设置音频处理
   */
  private async setupAudioProcessing() {
    console.log('=== Setting up Audio Processing ===')

    if (!this.mediaStream || !this.audioContext) {
      this.audioContext = new AudioContext({ sampleRate: 16000 })
      console.log('Created AudioContext with sample rate:', this.audioContext.sampleRate)
    }

    if (!this.mediaStream) {
      throw new Error('MediaStream is not available')
    }

    console.log('MediaStream tracks:', this.mediaStream.getTracks().map(t => ({
      kind: t.kind,
      enabled: t.enabled,
      readyState: t.readyState,
      label: t.label,
    })))

    const source = this.audioContext.createMediaStreamSource(this.mediaStream)
    console.log('Created MediaStreamSource')

    // 创建 AnalyserNode 用于音频可视化
    this.analyser = this.audioContext.createAnalyser()
    this.analyser.fftSize = 256 // 设置 FFT 大小，影响频率分辨率
    this.analyser.smoothingTimeConstant = 0.8 // 平滑系数，使波形更平滑
    source.connect(this.analyser)
    console.log('=== Created AnalyserNode ===')
    console.log('AnalyserNode:', this.analyser)
    console.log('fftSize:', this.analyser.fftSize)
    console.log('frequencyBinCount:', this.analyser.frequencyBinCount)
    console.log('smoothingTimeConstant:', this.analyser.smoothingTimeConstant)
    console.log('maxDecibels:', this.analyser.maxDecibels)
    console.log('minDecibels:', this.analyser.minDecibels)
    console.log('===========================')

    // 使用 AudioWorklet（现代方式，无弃用警告）
    try {
      await this.audioContext.audioWorklet.addModule('/audio-processor.worklet.js')
      this.audioProcessor = new AudioWorkletNode(this.audioContext, 'audio-processor')
      console.log('Created AudioWorkletNode')

      // 启动消息端口（重要：必须调用 start() 才能接收消息）
      this.audioProcessor.port.start()

      // 处理来自 AudioWorklet 的消息
      this.audioProcessor.port.onmessage = (event) => {
        if (!this.isRecording) {
          return
        }

        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
          console.warn('⚠️ WebSocket not ready, skipping audio processing. State:', this.ws?.readyState)
          return
        }

        // 检查消息类型
        if (event.data.type !== 'audioData') {
          console.warn('⚠️ Unexpected message type from AudioWorklet:', event.data.type)
          return
        }

        // AudioWorklet 发送的是普通数组，需要转换为 Float32Array
        const audioArray = event.data.data as number[]
        if (!audioArray || audioArray.length === 0) {
          console.warn('⚠️ Empty audio data from AudioWorklet')
          return
        }

        // 转换为 Float32Array
        const inputData = new Float32Array(audioArray)

        // 使用 AudioWorklet 提供的统计信息
        const maxAmplitude = event.data.maxAmplitude ?? 0
        const avgAmplitude = event.data.avgAmplitude ?? 0
        const hasAudio = maxAmplitude > 0.01

        // 验证音频数据大小是否符合API要求（640样本 = 1280字节）
        const expectedSamples = 640
        const expectedBytes = expectedSamples * 2 // 16bit = 2字节/样本
        if (inputData.length !== expectedSamples) {
          console.warn(`⚠️ Audio data size mismatch: got ${inputData.length} samples, expected ${expectedSamples} samples (${expectedBytes} bytes)`)
        }

        // 每100次打印一次音频输入信息
        if (this.audioSendCount % 100 === 0) {
          const actualBytes = inputData.length * 2
          console.log(`=== AudioWorklet Input === Has audio: ${hasAudio} | Max: ${maxAmplitude.toFixed(6)} | Avg: ${avgAmplitude.toFixed(6)} | Samples: ${inputData.length} (${actualBytes} bytes)`)
          console.log(`Expected: ${expectedSamples} samples = ${expectedBytes} bytes per 40ms`)
          // 打印前10个样本用于调试
          console.log('First 10 samples:', Array.from(inputData.slice(0, 10)).map(v => v.toFixed(6)))
          // 验证数据是否正确传递
          const actualMax = Math.max(...Array.from(inputData).map(Math.abs))
          console.log(`Data verification: Actual max from array=${actualMax.toFixed(6)}, Reported max=${maxAmplitude.toFixed(6)}`)
        }

        if (!hasAudio && this.audioSendCount % 500 === 0) {
          console.log('⚠️ No audio input detected (silence) - Max amplitude too low')
        }

        const pcmData = this.floatTo16BitPCM(inputData)

        // 发送音频数据
        this.sendAudioData(pcmData)
      }

      source.connect(this.audioProcessor)
      // AudioWorkletNode 需要连接到 destination 以保持音频图活跃
      // 使用 GainNode 静音输出，因为我们只需要处理音频数据
      const gainNode = this.audioContext.createGain()
      gainNode.gain.value = 0 // 静音输出
      this.audioProcessor.connect(gainNode)
      gainNode.connect(this.audioContext.destination)
      console.log('Audio processing pipeline connected (AudioWorklet)')
    } catch (error) {
      // AudioWorklet 是必需的，如果失败则抛出错误
      console.error('❌ Failed to initialize AudioWorklet:', error)
      throw new Error(`AudioWorklet initialization failed: ${error instanceof Error ? error.message : String(error)}`)
    }

    console.log('===============================')

    // 启动音频数据更新循环
    this.startAudioDataUpdate()
  }

  /**
   * 启动音频数据更新循环
   */
  private startAudioDataUpdate() {
    if (!this.analyser) {
      console.warn('⚠️ AnalyserNode not available, cannot start audio data update')
      return
    }

    console.log('=== Starting Audio Data Update Loop ===')
    console.log('AnalyserNode fftSize:', this.analyser.fftSize)
    console.log('AnalyserNode frequencyBinCount:', this.analyser.frequencyBinCount)
    console.log('AnalyserNode smoothingTimeConstant:', this.analyser.smoothingTimeConstant)
    console.log('Has audioDataCallback?', !!this.audioDataCallback)
    console.log('isRecording:', this.isRecording)

    let frameCount = 0
    let lastCallbackTime = Date.now()

    const updateAudioData = () => {
      // 检查是否还在录音
      if (!this.isRecording) {
        // 停止时重置
        if (this.audioDataCallback && this.analyser) {
          const emptyData = new Uint8Array(this.analyser.frequencyBinCount)
          this.audioDataCallback(emptyData)
        }
        return
      }

      if (!this.analyser) {
        console.warn('⚠️ AnalyserNode lost during update')
        return
      }

      // 获取频率数据（用于频谱显示）
      const frequencyData = new Uint8Array(this.analyser.frequencyBinCount)
      this.analyser.getByteFrequencyData(frequencyData)

      // 获取时域数据（用于波形显示）
      const timeData = new Uint8Array(this.analyser.frequencyBinCount)
      this.analyser.getByteTimeDomainData(timeData)

      // 每60帧打印一次详细信息（约1秒，假设60fps）
      if (frameCount % 60 === 0) {
        const now = Date.now()
        const timeSinceLastCallback = now - lastCallbackTime
        console.log('=== Audio Data Debug (every 60 frames) ===')
        console.log('Frame count:', frameCount)
        console.log('Time since last callback:', timeSinceLastCallback, 'ms')
        console.log('Frequency data length:', frequencyData.length)
        console.log('Frequency data sample (first 20):', Array.from(frequencyData.slice(0, 20)))
        console.log('Frequency data max:', Math.max(...Array.from(frequencyData)))
        console.log('Frequency data min:', Math.min(...Array.from(frequencyData)))
        console.log('Frequency data average:', Math.round(Array.from(frequencyData).reduce((a, b) => a + b, 0) / frequencyData.length))
        console.log('Time data length:', timeData.length)
        console.log('Time data sample (first 10):', Array.from(timeData.slice(0, 10)))
        console.log('Time data max:', Math.max(...Array.from(timeData)))
        console.log('Time data min:', Math.min(...Array.from(timeData)))
        console.log('Has audioDataCallback?', !!this.audioDataCallback)
        console.log('isRecording:', this.isRecording)
        console.log('=========================================')
        lastCallbackTime = now
      }

      // 调用回调函数传递音频数据（无论数据大小都要传递，让可视化组件处理）
      if (this.audioDataCallback) {
        try {
          this.audioDataCallback(frequencyData)
          if (frameCount === 0) {
            console.log('✓ First audio data callback called successfully')
          }
        } catch (error) {
          console.error('❌ Error in audioDataCallback:', error)
        }
      } else {
        if (frameCount % 60 === 0) {
          console.warn('⚠️ No audioDataCallback registered!')
        }
      }

      frameCount++
      // 继续更新
      requestAnimationFrame(updateAudioData)
    }

    // 立即开始第一次更新
    console.log('Starting requestAnimationFrame loop...')
    updateAudioData()
    console.log('✓ Audio data update loop started')
  }

  /**
   * 设置音频数据回调（用于可视化）
   */
  onAudioData(callback: (data: Uint8Array) => void) {
    console.log('=== Setting Audio Data Callback in Service ===')
    console.log('Callback function:', callback)
    this.audioDataCallback = callback
    console.log('Audio data callback set:', !!this.audioDataCallback)
    console.log('===============================================')

    // 如果已经在录音，立即触发一次更新
    if (this.isRecording && this.analyser) {
      const frequencyData = new Uint8Array(this.analyser.frequencyBinCount)
      this.analyser.getByteFrequencyData(frequencyData)
      try {
        callback(frequencyData)
        console.log('✓ Immediate callback call successful')
      } catch (error) {
        console.error('❌ Error in immediate callback:', error)
      }
    }
  }

  /**
   * 发送音频数据
   */
  private sendAudioData(pcmData: Int16Array) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('⚠️ Cannot send audio: WebSocket not open. State:', this.ws?.readyState)
      return
    }

    // 验证音频数据
    if (!pcmData || pcmData.length === 0) {
      console.warn('⚠️ Empty audio data, skipping send')
      return
    }

    // 检查音频数据是否有效（不应该全是0）
    const maxValue = Math.max(...Array.from(pcmData).map(Math.abs))
    if (maxValue === 0) {
      // 每100次打印一次警告，避免日志过多
      if (this.audioSendCount % 100 === 0) {
        console.warn('⚠️ Audio data is all zeros (silence), but still sending for API compatibility')
      }
    }

    // 将 Int16Array 转换为 Base64
    const base64 = this.arrayBufferToBase64(pcmData.buffer)

    // 验证Base64编码
    if (!base64 || base64.length === 0) {
      console.error('❌ Failed to encode audio data to Base64')
      return
    }

    // 发送音频数据
    const message = {
      data: {
        audio: base64,
        status: 0, // 0: 中间结果, 1: 结束
      },
    }

    const messageStr = JSON.stringify(message)

    // 每100次发送打印一次日志，避免日志过多
    if (!this.audioSendCount) {
      this.audioSendCount = 0
    }
    this.audioSendCount++

    if (this.audioSendCount % 100 === 0) {
      const expectedSamples = 640
      const expectedBytes = 1280
      const actualBytes = pcmData.length * 2
      console.log(`✓ Sent ${this.audioSendCount} audio packets | Audio: ${pcmData.length} samples (${actualBytes} bytes) | Base64: ${base64.length} chars | Message: ${messageStr.length} bytes | WS state: ${this.ws.readyState}`)
      console.log(`  Expected: ${expectedSamples} samples = ${expectedBytes} bytes per 40ms`)
      if (pcmData.length !== expectedSamples) {
        console.warn(`  ⚠️ Size mismatch: got ${pcmData.length} samples (${actualBytes} bytes), expected ${expectedSamples} samples (${expectedBytes} bytes)`)
      }
      console.log(`  Audio data sample (first 10): [${Array.from(pcmData.slice(0, 10)).join(', ')}]`)
      console.log(`  Audio data range: min=${Math.min(...Array.from(pcmData))}, max=${Math.max(...Array.from(pcmData))}`)
    }

    // 前几次发送时打印详细信息
    if (this.audioSendCount <= 3) {
      console.log(`=== First ${this.audioSendCount} Audio Packet ===`)
      console.log('PCM data length:', pcmData.length)
      console.log('PCM data sample:', Array.from(pcmData.slice(0, 20)))
      console.log('Base64 length:', base64.length)
      console.log('Base64 preview:', base64.substring(0, 50) + '...')
      console.log('Message:', messageStr.substring(0, 200) + '...')
      console.log('================================')
    }

    try {
      this.ws.send(messageStr)
    } catch (error) {
      console.error('❌ Failed to send audio data:', error)
      console.error('Error details:', {
        pcmLength: pcmData.length,
        base64Length: base64.length,
        messageLength: messageStr.length,
        wsState: this.ws.readyState,
      })
    }
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
    this.stopSilenceTimer()

    // 发送结束标志
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const endMessage = {
        data: {
          audio: '',
          status: 1, // 结束
        },
      }
      this.ws.send(JSON.stringify(endMessage))
    }

    // 关闭 WebSocket
    if (this.ws) {
      this.ws.close()
      this.ws = null
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

    this.currentSpeaker = null
  }

  /**
   * 设置识别结果回调
   */
  onResult(callback: RecognitionCallback) {
    console.log('=== Setting Result Callback ===')
    console.log('Callback function:', callback)
    this.onResultCallback = callback
    console.log('Result callback set:', !!this.onResultCallback)
    console.log('===============================')
  }

  /**
   * 设置错误回调
   */
  onError(callback: ErrorCallback) {
    console.log('=== Setting Error Callback ===')
    console.log('Callback function:', callback)
    this.onErrorCallback = callback
    console.log('Error callback set:', !!this.onErrorCallback)
    console.log('===============================')
  }

  /**
   * 开始沉默计时器
   */
  private startSilenceTimer() {
    this.stopSilenceTimer()
    this.silenceTimer = setInterval(() => {
      // 可以在这里触发沉默事件
      // const _silenceDuration = Date.now() - this.lastSpeechTime
    }, 1000)
  }

  /**
   * 停止沉默计时器
   */
  private stopSilenceTimer() {
    if (this.silenceTimer) {
      clearInterval(this.silenceTimer)
      this.silenceTimer = null
    }
  }

  /**
   * 获取当前说话人
   */
  getCurrentSpeaker(): string | null {
    return this.currentSpeaker
  }

  /**
   * 获取沉默时长（秒）
   */
  getSilenceDuration(): number {
    return Math.floor((Date.now() - this.lastSpeechTime) / 1000)
  }
}

