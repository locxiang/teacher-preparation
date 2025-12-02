<template>
  <div v-if="visible" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 backdrop-blur-sm p-4">
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden transform transition-all scale-100 flex flex-col">
      <!-- Header -->
      <div class="bg-gray-50 px-6 py-3 border-b border-gray-100 flex justify-between items-center shrink-0">
        <h3 class="font-bold text-gray-800 text-lg">声纹注册 - {{ teacher?.name }}</h3>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 text-xl">&times;</button>
      </div>

      <!-- Content Area (Scrollable) -->
      <div class="p-6 overflow-y-auto flex-1">
        <!-- Recording State -->
        <div v-if="!recordedAudioUrl" class="text-center mb-6">
          <div class="w-16 h-16 bg-nanyu-50 rounded-full mx-auto flex items-center justify-center mb-3 relative">
            <div v-if="isRecording" class="absolute inset-0 rounded-full border-4 border-nanyu-200 animate-ping"></div>
            <span class="text-3xl z-10">{{ isRecording ? '🎙️' : '🎤' }}</span>
          </div>
          <h4 class="text-base font-bold text-gray-800 mb-1">
            {{ isRecording ? '正在录音...' : '点击下方按钮开始录音' }}
          </h4>
          <p class="text-gray-500 text-xs">
            请用自然语速朗读一段文字，时长建议 10 秒以上
          </p>
          <!-- Recording Timer -->
          <div v-if="isRecording" class="mt-4 font-mono text-3xl text-nanyu-600 font-bold">
            {{ formatTime(recordingSeconds) }}
          </div>
        </div>

        <!-- Audio Preview Section (After Recording) -->
        <div v-if="recordedAudioUrl && audioInfo" class="space-y-4 mb-4">
          <!-- Audio Player and Info Side by Side -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Audio Player -->
            <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <h5 class="text-xs font-semibold text-gray-700 mb-2">录制预览</h5>
              <audio
                ref="audioPlayer"
                :src="recordedAudioUrl"
                class="w-full"
                controls
              ></audio>
            </div>

            <!-- Audio Info -->
            <div class="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <h5 class="text-xs font-semibold text-blue-800 mb-2">音频信息</h5>
              <div class="space-y-1.5 text-xs">
                <div class="flex justify-between">
                  <span class="text-blue-600 font-medium">编码格式:</span>
                  <span class="text-blue-800 font-mono text-[10px]">{{ audioInfo.mimeType }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-blue-600 font-medium">采样率:</span>
                  <span class="text-blue-800 font-mono">{{ audioInfo.sampleRate }} Hz</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-blue-600 font-medium">声道数:</span>
                  <span class="text-blue-800 font-mono">{{ audioInfo.channels }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-blue-600 font-medium">位深度:</span>
                  <span class="text-blue-800 font-mono">{{ audioInfo.bitDepth }} bit</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-blue-600 font-medium">时长:</span>
                  <span class="text-blue-800 font-mono">{{ audioInfo.duration }} 秒</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-blue-600 font-medium">文件大小:</span>
                  <span class="text-blue-800 font-mono">{{ audioInfo.fileSize }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Status Messages -->
        <div v-if="uploadProgress" class="mb-3 p-2.5 bg-blue-50 border border-blue-200 rounded-lg">
          <p class="text-xs text-blue-700 text-center">{{ uploadProgress }}</p>
        </div>

        <div v-if="errorMessage" class="mb-3 p-2.5 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-xs text-red-600 text-center">{{ errorMessage }}</p>
        </div>

        <!-- Recording Tips -->
        <div v-if="recordedAudioUrl && audioInfo && !uploadProgress && !errorMessage" class="mb-3 p-2.5 bg-green-50 border border-green-200 rounded-lg">
          <p class="text-xs text-green-700 text-center">✓ 录音完成！请先播放预览，确认无误后点击"提交"按钮上传</p>
        </div>

        <!-- Example Text (Compact) -->
        <div v-if="!recordedAudioUrl" class="bg-gray-50 p-3 rounded-lg text-left text-gray-600 text-xs leading-relaxed border border-gray-200">
          <span class="block text-gray-400 text-[10px] mb-1.5 font-semibold uppercase tracking-wider">朗读示例:</span>
          <span class="text-gray-700">"大家好，我是{{ teacher?.name }}。我主要负责{{ teacher?.subject || '本学科' }}的教学工作。在接下来的备课中，我希望我们能共同探讨，提升教学质量。"</span>
        </div>
      </div>

      <!-- Footer Actions -->
      <div class="px-6 py-4 border-t border-gray-100 bg-gray-50 flex justify-center space-x-3 shrink-0">
        <!-- 开始录音按钮 -->
        <button
          v-if="!isRecording && !recordedAudioUrl"
          @click="$emit('start-recording')"
          class="px-6 py-2.5 bg-nanyu-600 text-white rounded-lg font-semibold shadow-md hover:bg-nanyu-700 transition-all flex items-center text-sm">
          <span class="mr-2">●</span> 开始录音
        </button>

        <!-- 停止录音按钮 -->
        <button
          v-if="isRecording"
          @click="$emit('stop-recording')"
          class="px-6 py-2.5 bg-red-500 text-white rounded-lg font-semibold shadow-md hover:bg-red-600 transition-all flex items-center text-sm">
          <span class="mr-2">■</span> 停止录音
        </button>

        <!-- 录音完成后的操作按钮 -->
        <template v-if="recordedAudioUrl && !uploadProgress">
          <button
            @click="$emit('start-recording')"
            class="px-4 py-2.5 bg-gray-500 text-white rounded-lg font-medium hover:bg-gray-600 transition-all flex items-center text-sm"
            :disabled="isSubmitting">
            <span class="mr-1.5">🔄</span> 重新录制
          </button>
          <button
            @click="$emit('submit')"
            class="px-6 py-2.5 bg-nanyu-600 text-white rounded-lg font-semibold shadow-md hover:bg-nanyu-700 transition-all flex items-center text-sm"
            :disabled="isSubmitting || !!errorMessage">
            <span class="mr-2">{{ isSubmitting ? '⏳' : '✓' }}</span>
            {{ isSubmitting ? '提交中...' : '提交' }}
          </button>
        </template>

        <!-- 提交成功后的完成按钮 -->
        <button
          v-if="recordedAudioUrl && uploadProgress && uploadProgress.includes('成功')"
          @click="$emit('close')"
          class="px-6 py-2.5 bg-green-500 text-white rounded-lg font-semibold shadow-md hover:bg-green-600 transition-all flex items-center text-sm">
          <span class="mr-2">✓</span> 完成
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Teacher } from '../../services/teacher'

defineProps<{
  visible: boolean
  teacher: Teacher | null
  isRecording: boolean
  recordingSeconds: number
  recordedAudioUrl: string | null
  audioInfo: {
    mimeType: string
    sampleRate: number
    channels: number
    bitDepth: number
    duration: string
    fileSize: string
  } | null
  errorMessage: string
  uploadProgress: string
  isSubmitting: boolean
}>()

defineEmits<{
  close: []
  'start-recording': []
  'stop-recording': []
  submit: []
}>()

const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins < 10 ? '0' + mins : mins}:${secs < 10 ? '0' + secs : secs}`
}
</script>
