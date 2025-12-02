<template>
  <div class="space-y-6">
    <AddTeacherCard
      :name="newTeacherName"
      :subject="newTeacherSubject"
      @update:name="newTeacherName = $event"
      @update:subject="newTeacherSubject = $event"
      @add="handleAddTeacher"
    />

    <TeacherList
      :teachers="teachers"
      @record="handleRecord"
      @delete="handleDeleteTeacher"
    />

    <RecordingModal
      :visible="showRecordModal"
      :teacher="currentTeacher"
      :is-recording="isRecording"
      :recording-seconds="recordingSeconds"
      :recorded-audio-url="recordedAudioUrl"
      :audio-info="audioInfo"
      :error-message="errorMessage"
      :upload-progress="uploadProgress"
      :is-submitting="isSubmitting"
      @close="handleCloseModal"
      @start-recording="handleStartRecording"
      @stop-recording="handleStopRecording"
      @submit="handleSubmitRecording"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { XunfeiVoiceprintService } from '../../services/xunfei-voiceprint'
import { VoiceprintStorage } from '../../utils/voiceprint-storage'
import { getTeachers, createTeacher, updateTeacher, deleteTeacher, type Teacher } from '../../services/teacher'
import AddTeacherCard from './AddTeacherCard.vue'
import TeacherList from './TeacherList.vue'
import RecordingModal from './RecordingModal.vue'

const teachers = ref<Teacher[]>([])
const isLoading = ref(false)

const newTeacherName = ref('')
const newTeacherSubject = ref('')
const showRecordModal = ref(false)
const currentTeacher = ref<Teacher | null>(null)
const isRecording = ref(false)
const recordingSeconds = ref(0)
const errorMessage = ref('')
const uploadProgress = ref('')
const recordedAudioUrl = ref<string | null>(null)
const audioInfo = ref<{
  mimeType: string
  sampleRate: number
  channels: number
  bitDepth: number
  duration: string
  fileSize: string
} | null>(null)
const isSubmitting = ref(false)

let timer: ReturnType<typeof setInterval> | null = null
let mediaRecorder: MediaRecorder | null = null
let audioChunks: Blob[] = []
let audioContext: AudioContext | null = null
let mediaStream: MediaStream | null = null
let recordedPcmData: Int16Array | null = null

// 获取科大讯飞配置
const getXunfeiConfig = () => {
  const appId = import.meta.env.VITE_XUNFEI_APP_ID || '98581248'
  const accessKeyId = import.meta.env.VITE_XUNFEI_ACCESS_KEY_ID || '346f75290d2889799758864b6a561c0c'
  const accessKeySecret = import.meta.env.VITE_XUNFEI_ACCESS_KEY_SECRET || 'MTdiZjJkY2E1ZTM5NmE2MjM2ZDFmZTI0'
  return { appId, accessKeyId, accessKeySecret }
}

// 加载教师列表
const loadTeachers = async () => {
  isLoading.value = true
  try {
    const data = await getTeachers()
    teachers.value = data
  } catch (error) {
    console.error('Failed to load teachers:', error)
  } finally {
    isLoading.value = false
  }
}

// 添加教师
const handleAddTeacher = async () => {
  if (!newTeacherName.value || !newTeacherSubject.value) {
    return
  }

  try {
    await createTeacher(newTeacherName.value, newTeacherSubject.value)
    newTeacherName.value = ''
    newTeacherSubject.value = ''
    await loadTeachers()
  } catch (error) {
    alert(error instanceof Error ? error.message : '添加教师失败')
  }
}

// 删除教师
const handleDeleteTeacher = async (teacherId: number) => {
  if (confirm('确定要删除该教师吗？')) {
    try {
      await deleteTeacher(teacherId)
      await loadTeachers()
    } catch (error) {
      alert(error instanceof Error ? error.message : '删除教师失败')
    }
  }
}

// 打开录音模态框
const handleRecord = (teacher: Teacher) => {
  currentTeacher.value = teacher
  showRecordModal.value = true
  isRecording.value = false
  recordingSeconds.value = 0
  errorMessage.value = ''
  uploadProgress.value = ''
}

// 关闭录音模态框
const handleCloseModal = () => {
  if (isRecording.value) {
    handleStopRecording()
  }
  showRecordModal.value = false
  currentTeacher.value = null
  errorMessage.value = ''
  uploadProgress.value = ''
  isSubmitting.value = false
  if (recordedAudioUrl.value) {
    URL.revokeObjectURL(recordedAudioUrl.value)
    recordedAudioUrl.value = null
  }
  recordedPcmData = null
  audioInfo.value = null
}

// 开始录音
const handleStartRecording = async () => {
  try {
    errorMessage.value = ''
    uploadProgress.value = ''

    // 清理之前的录音数据
    if (recordedAudioUrl.value) {
      URL.revokeObjectURL(recordedAudioUrl.value)
      recordedAudioUrl.value = null
    }
    recordedPcmData = null
    audioInfo.value = null
    isSubmitting.value = false

    // 获取麦克风权限
    mediaStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        sampleRate: 16000,
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      },
    })

    // 创建 MediaRecorder
    mediaRecorder = new MediaRecorder(mediaStream, {
      mimeType: 'audio/webm',
    })

    audioChunks = []

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data)
      }
    }

    mediaRecorder.onstop = async () => {
      await prepareRecording()
    }

    mediaRecorder.start()
    isRecording.value = true
    recordingSeconds.value = 0

    timer = setInterval(() => {
      recordingSeconds.value++
    }, 1000)
  } catch (error) {
    console.error('录音启动失败:', error)
    errorMessage.value = '无法访问麦克风，请检查权限设置'
  }
}

// 停止录音
const handleStopRecording = () => {
  if (mediaRecorder && isRecording.value) {
    mediaRecorder.stop()
    isRecording.value = false
    if (timer) {
      clearInterval(timer)
      timer = null
    }

    // 停止音频流
    if (mediaStream) {
      mediaStream.getTracks().forEach(track => track.stop())
      mediaStream = null
    }
  }
}

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 准备录音数据（不上传，只显示播放器）
const prepareRecording = async () => {
  if (!currentTeacher.value || audioChunks.length === 0) {
    errorMessage.value = '录音数据为空'
    return
  }

  try {
    errorMessage.value = ''
    uploadProgress.value = ''

    // 将 Blob 转换为 AudioBuffer
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' })
    const arrayBuffer = await audioBlob.arrayBuffer()

    // 创建 AudioContext 并解码音频
    audioContext = new AudioContext({ sampleRate: 16000 })
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)

    // 显示音频信息和播放器
    const mimeType = mediaRecorder?.mimeType || 'audio/webm'
    const sampleRate = audioBuffer.sampleRate
    const channels = audioBuffer.numberOfChannels
    const duration = audioBuffer.duration
    const fileSize = audioBlob.size

    // 创建音频 URL 用于播放
    recordedAudioUrl.value = URL.createObjectURL(audioBlob)

    // 显示音频信息
    audioInfo.value = {
      mimeType: mimeType,
      sampleRate: sampleRate,
      channels: channels,
      bitDepth: 16, // PCM 16-bit
      duration: duration.toFixed(2),
      fileSize: formatFileSize(fileSize),
    }

    // 转换为 PCM 格式（Int16Array）并保存
    recordedPcmData = convertToPCM(audioBuffer)

    // 检查音频时长（至少10秒，最多60秒）
    if (duration < 10) {
      errorMessage.value = `录音时长不足，当前 ${duration.toFixed(1)} 秒，需要至少 10 秒。请先播放预览，确认无误后可以重新录制。`
      return
    }
    if (duration > 60) {
      errorMessage.value = `录音时长过长，当前 ${duration.toFixed(1)} 秒，最多 60 秒。请先播放预览，确认无误后可以重新录制。`
      return
    }

    // 清理音频上下文
    if (audioContext) {
      await audioContext.close()
      audioContext = null
    }
  } catch (error) {
    console.error('处理录音失败:', error)
    errorMessage.value = error instanceof Error ? error.message : '处理录音失败，请重试'
  }
}

// 提交录音（上传声纹）
const handleSubmitRecording = async () => {
  if (!currentTeacher.value || !recordedPcmData) {
    errorMessage.value = '没有可提交的录音数据'
    return
  }

  // 检查音频时长
  if (!audioInfo.value) {
    errorMessage.value = '音频信息不完整'
    return
  }

  const duration = parseFloat(audioInfo.value.duration)
  if (duration < 10) {
    errorMessage.value = `录音时长不足，当前 ${duration.toFixed(1)} 秒，需要至少 10 秒`
    return
  }
  if (duration > 60) {
    errorMessage.value = `录音时长过长，当前 ${duration.toFixed(1)} 秒，最多 60 秒`
    return
  }

  try {
    isSubmitting.value = true
    errorMessage.value = ''
    uploadProgress.value = '正在上传声纹...'

    // 创建声纹服务实例
    const config = getXunfeiConfig()
    const voiceprintService = new XunfeiVoiceprintService(config)

    // 判断是注册还是更新
    if (currentTeacher.value.has_voiceprint && currentTeacher.value.feature_id) {
      // 更新声纹
      uploadProgress.value = '正在更新声纹...'
      const updateResult = await voiceprintService.updateVoiceprint(
        currentTeacher.value.feature_id,
        recordedPcmData,
        'raw',
      )

      // 更新后端教师信息
      await updateTeacher(currentTeacher.value.id, {
        feature_id: currentTeacher.value.feature_id,
      })

      // 更新本地存储（用于声纹识别）
      const voiceprint = VoiceprintStorage.getVoiceprintByFeatureId(currentTeacher.value.feature_id)
      if (voiceprint) {
        VoiceprintStorage.saveVoiceprint({
          ...voiceprint,
          updated_at: Date.now(),
          sid: updateResult.sid,
          code: updateResult.code,
          desc: updateResult.desc,
        })
      }
    } else {
      // 注册新声纹
      uploadProgress.value = '正在注册声纹...'
      const result = await voiceprintService.registerVoiceprint(
        recordedPcmData,
        'raw',
        String(currentTeacher.value.id),
      )

      // 更新后端教师信息
      await updateTeacher(currentTeacher.value.id, {
        feature_id: result.feature_id,
      })

      // 保存到本地存储（用于声纹识别）
      VoiceprintStorage.saveVoiceprint({
        feature_id: result.feature_id,
        teacher_id: String(currentTeacher.value.id),
        teacher_name: currentTeacher.value.name,
        subject: currentTeacher.value.subject,
        created_at: Date.now(),
        updated_at: Date.now(),
        sid: result.sid,
        code: result.code,
        desc: result.desc,
      })
    }

    uploadProgress.value = '声纹注册成功！'

    // 重新加载教师列表
    await loadTeachers()

    // 延迟关闭模态框
    setTimeout(() => {
      handleCloseModal()
    }, 1500)
  } catch (error) {
    console.error('声纹注册失败:', error)
    errorMessage.value = error instanceof Error ? error.message : '声纹注册失败，请重试'
    uploadProgress.value = ''
  } finally {
    isSubmitting.value = false
  }
}

// 将 AudioBuffer 转换为 PCM Int16Array
const convertToPCM = (audioBuffer: AudioBuffer): Int16Array => {
  const length = audioBuffer.length
  const pcmData = new Int16Array(length)
  const channelData = audioBuffer.getChannelData(0) // 获取单声道数据

  for (let i = 0; i < length; i++) {
    // 将 Float32 (-1.0 到 1.0) 转换为 Int16 (-32768 到 32767)
    const s = Math.max(-1, Math.min(1, channelData[i]))
    pcmData[i] = s < 0 ? s * 0x8000 : s * 0x7FFF
  }

  return pcmData
}

onMounted(() => {
  loadTeachers()
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
  if (mediaRecorder && isRecording.value) {
    mediaRecorder.stop()
  }
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop())
  }
  if (audioContext) {
    audioContext.close()
  }
})
</script>

