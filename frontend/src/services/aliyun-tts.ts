/**
 * 阿里云流式语音合成服务（TTS）
 * 参考文档：https://help.aliyun.com/zh/isi/developer-reference/websocket-protocol-description
 * 基于阿里云官方demo实现
 */

// 使用相对路径，让浏览器自动使用当前访问的域名/IP
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

// WebSocket URL（北京地域）
const NLS_WS_URL = 'wss://nls-gateway-cn-beijing.aliyuncs.com/ws/v1'

interface TTSConfig {
  token: string
  appKey: string
  voice?: string // 发音人，默认longxiaochun
  format?: string // 音频格式，PCM/pcm/wav/mp3，默认PCM
  sampleRate?: number // 采样率，默认24000
  volume?: number // 音量，0-100，默认100
  speechRate?: number // 语速，-500到500，默认0
  pitchRate?: number // 语调，-500到500，默认0
}

/**
 * PCM音频播放器（基于阿里云demo）
 */
class PCMAudioPlayer {
  private sampleRate: number
  private audioContext: AudioContext | null = null
  private audioQueue: ArrayBuffer[] = []
  private isPlaying = false
  private currentSource: AudioBufferSourceNode | null = null
  private onPlaybackCompleteCallback: (() => void) | null = null // 播放完成回调

  constructor(sampleRate: number) {
    this.sampleRate = sampleRate
  }

  /**
   * 设置播放完成回调
   */
  setOnPlaybackComplete(callback: () => void): void {
    this.onPlaybackCompleteCallback = callback
  }

  connect(): void {
    if (!this.audioContext) {
      const AudioContextClass = window.AudioContext || (window as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext
      if (!AudioContextClass) {
        throw new Error('浏览器不支持AudioContext')
      }
      this.audioContext = new AudioContextClass({
        sampleRate: this.sampleRate,
      })
      console.log('[TTS Player] AudioContext已创建，采样率:', this.sampleRate)
    }
  }

  pushPCM(arrayBuffer: ArrayBuffer): void {
    console.log('[TTS Player] 收到PCM数据，大小:', arrayBuffer.byteLength, '字节')
    this.audioQueue.push(arrayBuffer)
    this._playNextAudio()
  }

  /**
   * 将ArrayBuffer转为AudioBuffer
   */
  private _bufferPCMData(pcmData: ArrayBuffer): AudioBuffer {
    if (!this.audioContext) {
      throw new Error('AudioContext未初始化')
    }

    const sampleRate = this.sampleRate
    const length = pcmData.byteLength / 2 // 假设PCM数据为16位，需除以2
    const audioBuffer = this.audioContext.createBuffer(1, length, sampleRate)
    const channelData = audioBuffer.getChannelData(0)
    const int16Array = new Int16Array(pcmData) // 将PCM数据转换为Int16Array

    for (let i = 0; i < length; i++) {
      // 将16位PCM转换为浮点数(-1.0到1.0)
      channelData[i] = int16Array[i] / 32768 // 16位数据转换范围
    }

    const audioLength = (length / sampleRate) * 1000
    console.log(`[TTS Player] 准备音频: ${length} 样本, ${audioLength.toFixed(2)} ms`)

    return audioBuffer
  }

  private async _playAudio(arrayBuffer: ArrayBuffer): Promise<void> {
    if (!this.audioContext) {
      console.error('[TTS Player] AudioContext未初始化')
      return
    }

    if (this.audioContext.state === 'suspended') {
      console.log('[TTS Player] 恢复AudioContext')
      await this.audioContext.resume()
    }

    const audioBuffer = this._bufferPCMData(arrayBuffer)

    this.currentSource = this.audioContext.createBufferSource()
    this.currentSource.buffer = audioBuffer
    this.currentSource.connect(this.audioContext.destination)

    this.currentSource.onended = () => {
      console.log('[TTS Player] 音频片段播放完成')
      this.isPlaying = false
      this.currentSource = null

      // 如果队列为空，说明所有音频都已播放完成
      if (this.audioQueue.length === 0) {
        console.log('[TTS Player] ✅ 所有音频播放完成')
        // 调用播放完成回调
        if (this.onPlaybackCompleteCallback) {
          this.onPlaybackCompleteCallback()
        }
      } else {
        // 播放队列中的下一个音频
        this._playNextAudio()
      }
    }

    this.currentSource.start()
    this.isPlaying = true
    console.log('[TTS Player] 开始播放音频')
  }

  private _playNextAudio(): void {
    if (this.audioQueue.length > 0 && !this.isPlaying) {
      // 计算总的字节长度
      const totalLength = this.audioQueue.reduce((acc, buffer) => acc + buffer.byteLength, 0)
      const combinedBuffer = new Uint8Array(totalLength)
      let offset = 0

      // 将所有audioQueue中的buffer拼接到一个新的Uint8Array中
      for (const buffer of this.audioQueue) {
        combinedBuffer.set(new Uint8Array(buffer), offset)
        offset += buffer.byteLength
      }

      // 清空audioQueue，因为我们已经拼接完所有数据
      this.audioQueue = []
      console.log('[TTS Player] 合并音频数据，总大小:', totalLength, '字节')
      // 发送拼接的audio数据给playAudio
      this._playAudio(combinedBuffer.buffer)
    } else if (this.audioQueue.length === 0 && !this.isPlaying) {
      // 队列为空且没有播放，说明所有音频都已播放完成
      console.log('[TTS Player] ✅ 所有音频播放完成（队列为空且未在播放）')
    }
  }

  stop(): void {
    if (this.currentSource) {
      this.currentSource.stop() // 停止当前音频播放
      this.currentSource = null // 清除音频源引用
      this.isPlaying = false // 更新播放状态
    }
    this.audioQueue = [] // 清空音频队列
    console.log('[TTS Player] 播放已停止，队列已清空')
  }

  /**
   * 等待播放完成
   * 返回Promise，当所有音频播放完成后resolve
   */
  waitForPlaybackComplete(): Promise<void> {
    return new Promise((resolve) => {
      // 如果当前没有播放，立即resolve
      if (!this.isPlaying && this.audioQueue.length === 0) {
        resolve()
        return
      }

      // 检查播放是否完成的函数
      const checkComplete = () => {
        if (!this.isPlaying && this.audioQueue.length === 0) {
          console.log('[TTS Player] 所有音频播放完成')
          resolve()
        } else {
          // 继续检查
          setTimeout(checkComplete, 100)
        }
      }

      checkComplete()
    })
  }

  close(): void {
    this.stop()
    if (this.audioContext) {
      this.audioContext.close()
      this.audioContext = null
      console.log('[TTS Player] AudioContext已关闭')
    }
  }
}

/**
 * 生成32位随机字符串（UUID）
 */
function generateUUID(): string {
  let d = new Date().getTime()
  const d2 = (performance && performance.now && performance.now() * 1000) || 0
  return 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    let r = Math.random() * 16 // random number between 0 and 16
    if (d > 0) {
      r = (d + r) % 16 | 0
      d = Math.floor(d / 16)
      return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16)
    } else {
      r = (d2 + r) % 16 | 0
      return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16)
    }
  })
}

export class AliyunTTSService {
  private ws: WebSocket | null = null
  private config: TTSConfig | null = null
  private taskId: string | null = null
  private isSynthesisStarted = false
  private hasError = false // 错误状态标志
  private player: PCMAudioPlayer | null = null
  private onCompleteCallback: (() => void) | null = null
  private onErrorCallback: ((error: Error) => void) | null = null
  private onPlaybackCompleteCallback: (() => void) | null = null // 音频播放完成回调

  /**
   * 生成WebSocket消息的头部信息
   */
  private getHeader(): {
    message_id: string
    task_id: string
    namespace: string
    name: string
    appkey: string
  } {
    if (!this.taskId || !this.config) {
      throw new Error('任务未初始化')
    }
    return {
      message_id: generateUUID(),
      task_id: this.taskId,
      namespace: 'FlowingSpeechSynthesizer',
      name: '',
      appkey: this.config.appKey,
    }
  }

  /**
   * 开始语音合成
   */
  async startSynthesis(
    config: TTSConfig,
    onComplete?: () => void,
    onError?: (error: Error) => void,
    onPlaybackComplete?: () => void, // 音频播放完成回调
  ): Promise<void> {
    console.log('[TTS] 开始初始化语音合成服务')
    this.config = config
    this.onCompleteCallback = onComplete || null
    this.onErrorCallback = onError || null
    this.onPlaybackCompleteCallback = onPlaybackComplete || null
    this.hasError = false // 重置错误标志

    // 初始化音频播放器
    const sampleRate = config.sampleRate || 24000
    this.player = new PCMAudioPlayer(sampleRate)
    this.player.connect()
    this.player.stop() // 清空队列

    // 设置播放完成回调
    this.player.setOnPlaybackComplete(() => {
      console.log('[TTS] 音频播放完成回调')
      if (this.onPlaybackCompleteCallback) {
        this.onPlaybackCompleteCallback()
      }
    })

    // 构建WebSocket URL（带Token）
    const wsUrl = `${NLS_WS_URL}?token=${encodeURIComponent(config.token)}`
    console.log('[TTS] WebSocket URL:', wsUrl.replace(/token=[^&]+/, 'token=***'))

    return new Promise((resolve, reject) => {
      let synthesisStartedResolve: (() => void) | null = null
      let synthesisStartedReject: ((error: Error) => void) | null = null
      const synthesisStartedPromise = new Promise<void>((res, rej) => {
        synthesisStartedResolve = res
        synthesisStartedReject = rej
      })

      // 设置超时，防止无限等待
      const timeout = setTimeout(() => {
        if (synthesisStartedReject) {
          synthesisStartedReject(new Error('等待SynthesisStarted确认超时'))
        }
      }, 10000) // 10秒超时

      try {
        this.ws = new WebSocket(wsUrl)
        this.ws.binaryType = 'arraybuffer' // 重要：设置二进制类型为arraybuffer

        this.ws.onopen = () => {
          console.log('[TTS] ✅ WebSocket连接已建立')
          if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.taskId = generateUUID()
            console.log('[TTS] 任务ID:', this.taskId)

            const header = this.getHeader()
            const params = {
              header: { ...header, name: 'StartSynthesis' },
              payload: {
                voice: config.voice || 'longxiaochun',
                format: config.format || 'PCM', // 使用大写PCM
                sample_rate: config.sampleRate || 24000,
                volume: config.volume || 100,
                speech_rate: config.speechRate || 0,
                pitch_rate: config.pitchRate || 0,
                enable_subtitle: true, // 启用字幕
                platform: 'javascript', // 平台标识
              },
            }

            console.log('[TTS] 发送StartSynthesis指令:', JSON.stringify(params, null, 2))
            this.ws.send(JSON.stringify(params))
            // 不在这里resolve，等待SynthesisStarted确认
          }
        }

        this.ws.onmessage = (event) => {
          // 如果已经发生错误，忽略后续消息
          if (this.hasError) {
            console.log('[TTS] 已发生错误，忽略后续消息')
            return
          }

          const data = event.data
          console.log('[TTS] 收到消息，类型:', typeof data, '是否为ArrayBuffer:', data instanceof ArrayBuffer)

          // 如果收到的是二进制数据（ArrayBuffer类型）
          if (data instanceof ArrayBuffer) {
            console.log('[TTS] ✅ 收到音频数据，大小:', data.byteLength, '字节')
            if (this.player && !this.hasError) {
              this.player.pushPCM(data)
            }
          } else {
            // 如果收到的是文本消息
            try {
              const body = JSON.parse(data as string)
              console.log('[TTS] 收到文本消息:', JSON.stringify(body, null, 2))

              const header = body.header || {}
              const name = header.name
              const status = header.status
              const statusMessage = header.status_message

              // 如果消息名称为'SynthesisStarted'指令且状态为成功
              if (name === 'SynthesisStarted' && status === 20000000) {
                console.log('[TTS] ✅ 语音合成已开始')
                this.isSynthesisStarted = true
                clearTimeout(timeout)
                if (synthesisStartedResolve) {
                  synthesisStartedResolve()
                }
                return // 成功开始，继续处理
              }

              // 如果消息名称为'SynthesisCompleted'指令且状态为成功
              if (name === 'SynthesisCompleted' && status === 20000000) {
                console.log('[TTS] ✅ 语音合成已完成，所有文本已合成')
                // 调用完成回调
                if (this.onCompleteCallback) {
                  this.onCompleteCallback()
                }
                // 关闭连接（正常完成，不发送StopSynthesis，因为已经收到SynthesisCompleted）
                this.close(false)
                return // 正常完成，退出
              }

              // 检查是否有错误状态码（除了SynthesisStarted和SynthesisCompleted之外的消息，如果status不是20000000就是错误）
              // 注意：某些消息可能没有status字段，需要特殊处理
              if (name === 'TaskFailed' || (status !== undefined && status !== 20000000 && name !== 'SynthesisStarted' && name !== 'SynthesisCompleted')) {
                // 设置错误标志，防止处理后续消息和音频数据
                this.hasError = true

                // 从status_text中获取更详细的错误信息
                const statusText = header.status_text || ''
                const errorMsg = statusText || statusMessage || `语音合成失败 (错误码: ${status || '未知'})`
                console.error('[TTS] ❌ 语音合成失败:', errorMsg, '状态码:', status, '消息名称:', name)
                console.error('[TTS] 完整错误消息:', JSON.stringify(body, null, 2))

                // 如果还在等待SynthesisStarted，则reject Promise
                clearTimeout(timeout)
                if (synthesisStartedReject) {
                  synthesisStartedReject(new Error(errorMsg))
                }

                // 立即停止播放音频（这会清空队列并停止当前播放）
                console.log('[TTS] 立即停止播放音频并清空队列')
                this.stopPlayback()

                // 关闭连接
                if (this.ws) {
                  try {
                    this.ws.close()
                  } catch (e) {
                    console.error('[TTS] 关闭WebSocket失败:', e)
                  }
                  this.ws = null
                }

                // 重置状态
                this.isSynthesisStarted = false

                // 调用错误回调
                if (this.onErrorCallback) {
                  this.onErrorCallback(new Error(errorMsg))
                }
                return // 错误处理完成，退出
              }

              // 其他未知消息类型，记录日志但不处理
              if (name && name !== 'SynthesisStarted' && name !== 'SynthesisCompleted') {
                console.log('[TTS] 收到其他消息:', name, '状态:', status)
              }
            } catch (error) {
              console.error('[TTS] 解析文本消息失败:', error, '原始数据:', data)
            }
          }
        }

        this.ws.onerror = (error) => {
          console.error('[TTS] ❌ WebSocket错误:', error)
          clearTimeout(timeout)
          if (synthesisStartedReject) {
            synthesisStartedReject(error instanceof Error ? error : new Error('WebSocket连接错误'))
          }
          if (this.onErrorCallback) {
            this.onErrorCallback(new Error('WebSocket连接错误'))
          }
          reject(error)
        }

        this.ws.onclose = (event) => {
          console.log('[TTS] WebSocket连接已关闭，代码:', event.code, '原因:', event.reason, 'wasClean:', event.wasClean)
          
          // 如果还在等待SynthesisStarted，则reject Promise
          clearTimeout(timeout)
          if (synthesisStartedReject && !this.isSynthesisStarted) {
            synthesisStartedReject(new Error(`WebSocket连接关闭: ${event.reason || '未知原因'}`))
          }

          // WebSocket关闭不代表音频播放完成，音频播放速度更慢
          // 只有在发生错误时才停止播放，正常关闭时让音频继续播放
          if (this.hasError) {
            console.log('[TTS] 检测到错误，停止播放音频')
            this.stopPlayback()
          } else {
            console.log('[TTS] WebSocket正常关闭，音频将继续播放直到完成')
          }

          this.ws = null
          this.isSynthesisStarted = false
        }

        // 等待SynthesisStarted确认后再resolve
        synthesisStartedPromise
          .then(() => {
            console.log('[TTS] ✅ SynthesisStarted确认收到，startSynthesis完成')
            resolve()
          })
          .catch((error) => {
            console.error('[TTS] ❌ 等待SynthesisStarted失败:', error)
            reject(error)
          })
      } catch (error) {
        console.error('[TTS] ❌ 创建WebSocket失败:', error)
        clearTimeout(timeout)
        reject(error)
      }
    })
  }

  /**
   * 发送文本进行合成
   */
  sendText(text: string): void {
    if (!this.ws || !this.isSynthesisStarted) {
      console.error('[TTS] ❌ 无法发送文本: 合成未开始')
      throw new Error('Cannot send RunSynthesis: Synthesis has not started')
    }

    const header = this.getHeader()
    const params = {
      header: { ...header, name: 'RunSynthesis' },
      payload: {
        text,
      },
    }

    console.log('[TTS] 发送文本进行合成，长度:', text.length, '字符，内容:', text.substring(0, 50) + (text.length > 50 ? '...' : ''))
    console.log('[TTS] RunSynthesis消息:', JSON.stringify(params, null, 2))
    this.ws.send(JSON.stringify(params))
  }

  /**
   * 停止合成
   */
  stopSynthesis(): void {
    if (!this.ws || !this.isSynthesisStarted) {
      console.error('[TTS] ❌ 无法停止合成: 合成未开始')
      return
    }

    const header = this.getHeader()
    const params = {
      header: { ...header, name: 'StopSynthesis' },
    }

    console.log('[TTS] 发送StopSynthesis指令')
    this.ws.send(JSON.stringify(params))
  }

  /**
   * 停止播放
   */
  stopPlayback(): void {
    console.log('[TTS] 停止播放音频')
    if (this.player) {
      this.player.stop()
    }
    this.hasError = true // 设置错误标志，防止继续处理音频
  }

  /**
   * 关闭连接
   * @param sendStopSynthesis 是否发送StopSynthesis指令（默认false，因为通常已经在外部发送过了）
   * @param waitForPlayback 是否等待音频播放完成（默认false）
   */
  async close(sendStopSynthesis = false, waitForPlayback = false): Promise<void> {
    this.hasError = false // 重置错误标志（正常关闭时）
    if (this.ws) {
      // 只有在明确要求时才发送StopSynthesis（避免重复发送）
      if (sendStopSynthesis && this.isSynthesisStarted) {
        this.stopSynthesis()
      }
      // 等待一小段时间让StopSynthesis发送完成
      setTimeout(() => {
        if (this.ws) {
          this.ws.close()
          this.ws = null
        }
      }, 100)
    }

    // 如果需要等待播放完成
    if (waitForPlayback && this.player) {
      console.log('[TTS] 等待音频播放完成...')
      await this.player.waitForPlaybackComplete()
      console.log('[TTS] 音频播放已完成，关闭播放器')
      this.player.close()
      this.player = null
    } else if (this.player) {
      // 不等待播放完成，让音频继续播放
      console.log('[TTS] WebSocket已关闭，音频将继续播放直到完成')
      // 不关闭player，让音频继续播放
    }

    this.isSynthesisStarted = false
    console.log('[TTS] 服务已关闭')
  }
}

/**
 * 获取TTS Token
 */
export async function getTTSToken(): Promise<{ token: string; app_key: string; region: string }> {
  console.log('[TTS] 开始获取Token，API地址:', `${API_BASE_URL}/api/tts/token`)
  const token = localStorage.getItem('access_token')
  if (!token) {
    console.error('[TTS] ❌ 未登录，无法获取Token')
    throw new Error('未登录')
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/tts/token`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })

    console.log('[TTS] Token请求响应状态:', response.status, response.statusText)

    const data = await response.json()
    console.log('[TTS] Token响应数据:', { ...data, token: data.token ? `${data.token.substring(0, 10)}...` : 'null' })

    if (!response.ok) {
      console.error('[TTS] ❌ 获取Token失败:', data.message)
      throw new Error(data.message || '获取Token失败')
    }

    console.log('[TTS] ✅ Token获取成功，AppKey:', data.app_key ? `${data.app_key.substring(0, 10)}...` : 'null')
    return {
      token: data.token,
      app_key: data.app_key,
      region: data.region,
    }
  } catch (error) {
    console.error('[TTS] ❌ 获取Token异常:', error)
    throw error
  }
}
