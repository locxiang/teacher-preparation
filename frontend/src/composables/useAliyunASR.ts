import { ref, onUnmounted } from 'vue'
import { AliyunASRService, type RecognitionResult } from '@/services/aliyun-asr'

// 识别结果接口（保持与原有接口兼容，扩展 speakerName）
export interface RecognitionResultWithSpeaker extends RecognitionResult {
  speakerName?: string
}

/**
 * 使用阿里云语音识别（通过后端WebSocket）
 */
export function useAliyunASR() {
  const isRecording = ref(false)
  const currentSpeaker = ref<string | null>(null)
  const silenceDuration = ref(0) // 沉默时长，单位毫秒
  const tempTranscript = ref('') // 临时识别结果

  let asrService: AliyunASRService | null = null
  let lastSpeechTime = 0 // 上次检测到语音的时间戳
  let silenceTimer: number | null = null
  let onResultCallback: ((result: RecognitionResultWithSpeaker) => void) | null = null
  let onErrorCallback: ((error: Error) => void) | null = null
  let onAudioDataCallback: ((data: Uint8Array) => void) | null = null

  // 说话人映射表（可以根据role_id映射到具体姓名）
  const speakerMapping: Record<string, string> = {
    '0': '说话人1',
    '1': '说话人2',
    '2': '说话人3',
  }

  /**
   * 初始化语音识别服务
   */
  const initASRService = (
    meetingId: string,
    onResult: (result: RecognitionResultWithSpeaker) => void,
    onError?: (error: Error) => void,
  ) => {
    onResultCallback = onResult
    onErrorCallback = onError || null

    // 获取后端服务器URL（从环境变量或使用当前域名）
    const serverUrl = import.meta.env.VITE_API_BASE_URL || ''
    asrService = new AliyunASRService(serverUrl)

    // 设置识别结果回调
    asrService.onResult((result: RecognitionResult) => {
      console.log('=== 识别结果回调 ===')
      console.log('识别文本:', result.text)
      console.log('是否最终结果:', result.isFinal)
      console.log('说话人ID:', result.speaker)

      // 更新当前说话人
      if (result.speaker) {
        currentSpeaker.value = result.speaker
      }

      // 更新临时识别结果
      if (!result.isFinal && result.text) {
        tempTranscript.value = result.text
      } else if (result.isFinal) {
        tempTranscript.value = ''
      }

      // 更新最后语音时间
      if (result.text && result.text.trim()) {
        lastSpeechTime = Date.now()
      }

      // 构建识别结果（包含speakerName）
      const resultWithSpeaker: RecognitionResultWithSpeaker = {
        ...result,
        speakerName: result.speaker ? speakerMapping[result.speaker] || `说话人${result.speaker}` : '未知',
      }

      console.log('调用识别结果回调:', resultWithSpeaker)
      onResultCallback?.(resultWithSpeaker)
    })

    // 设置错误回调
    asrService.onError((error: Error) => {
      console.error('语音识别错误:', error)
      onErrorCallback?.(error)
    })

    // 设置音频数据回调（用于可视化）
    if (onAudioDataCallback) {
      console.log('=== Setting Audio Data Callback ===')
      console.log('Callback function:', onAudioDataCallback)
      asrService.onAudioData(onAudioDataCallback)
      console.log('Audio data callback set')
      console.log('===================================')
    } else {
      console.warn('⚠️ No onAudioDataCallback provided')
    }
  }

  /**
   * 开始录音
   * @param meetingId 会议ID
   * @param onResult 识别结果回调
   * @param onError 错误回调
   * @param onAudioData 音频数据回调（用于可视化）
   * @param externalStream 外部传入的 MediaStream（可选），如果不传入则内部获取
   * @param streamUrl 通义听悟推流URL（可选，Demo场景使用）
   */
  const startRecording = async (
    meetingId: string,
    onResult: (result: RecognitionResultWithSpeaker) => void,
    onError?: (error: Error) => void,
    onAudioData?: (data: Uint8Array) => void,
    externalStream?: MediaStream,
    streamUrl?: string,
  ) => {
    if (!asrService) {
      onAudioDataCallback = onAudioData || null
      initASRService(meetingId, onResult, onError)
    } else {
      // 更新回调
      onResultCallback = onResult
      onErrorCallback = onError || null
      onAudioDataCallback = onAudioData || null
      // 更新音频数据回调
      if (onAudioDataCallback && asrService) {
        asrService.onAudioData(onAudioDataCallback)
      }
    }

    try {
      if (asrService) {
        await asrService.startRecognition(meetingId, externalStream, streamUrl)
        isRecording.value = true
        lastSpeechTime = Date.now()
        startSilenceTimer()
      }
    } catch (error) {
      isRecording.value = false
      const err = error instanceof Error ? error : new Error('Failed to start recording')
      onErrorCallback?.(err)
      throw err
    }
  }

  /**
   * 停止录音
   */
  const stopRecording = () => {
    if (asrService) {
      asrService.stopRecognition()
    }
    isRecording.value = false
    currentSpeaker.value = null
    tempTranscript.value = ''
    silenceDuration.value = 0
    stopSilenceTimer()
  }

  /**
   * 启动沉默计时器
   */
  const startSilenceTimer = () => {
    stopSilenceTimer()
    silenceTimer = setInterval(() => {
      const now = Date.now()
      silenceDuration.value = now - lastSpeechTime
    }, 1000)
  }

  /**
   * 停止沉默计时器
   */
  const stopSilenceTimer = () => {
    if (silenceTimer !== null) {
      clearInterval(silenceTimer)
      silenceTimer = null
      silenceDuration.value = 0
    }
  }

  /**
   * 断开连接
   */
  const disconnect = () => {
    stopRecording()
    if (asrService) {
      asrService.disconnect()
      asrService = null
    }
  }

  // 组件卸载时清理
  onUnmounted(() => {
    disconnect()
  })

  return {
    isRecording,
    currentSpeaker,
    silenceDuration,
    tempTranscript,
    initASRService,
    startRecording,
    stopRecording,
    disconnect,
  }
}

