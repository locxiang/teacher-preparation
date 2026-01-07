<template>
  <div class="bg-white border border-gray-200 rounded shadow-sm p-4">
    <div class="flex items-center justify-between mb-2">
      <span class="text-xs text-gray-500">正在发言</span>
      <span class="text-xs font-medium text-gray-700">
        <span
          v-if="isAISpeaking || isAIGenerating"
          class="text-nanyu-600 flex items-center"
        >
          <span class="inline-block animate-pulse mr-1">🤖</span>
          {{ isAIGenerating ? 'AI思考中...' : 'AI正在说话' }}
        </span>
        <span v-else>{{ currentSpeaker || '等待中...' }}</span>
      </span>
    </div>
    <!-- Real-time Audio Waveform -->
    <div class="flex items-end justify-center space-x-0.5 h-16 bg-gray-50 rounded p-2">
      <div
        v-for="(bar, index) in audioBars"
        :key="index"
        class="w-1 rounded-t transition-all duration-50"
        :class="isAISpeaking || isAIGenerating ? 'bg-nanyu-500' : 'bg-nanyu-400'"
        :style="{ height: `${bar}%`, minHeight: '2px' }"
      />
    </div>
    <!-- 静默计时器 -->
    <div
      v-if="isRecording"
      class="mt-3 pt-3 border-t border-gray-200"
    >
      <div class="flex items-center justify-between">
        <span class="text-xs text-gray-500">静默时长</span>
        <span
          class="text-sm font-semibold"
          :class="silenceDuration >= 30 ? 'text-red-600' : silenceDuration >= 10 ? 'text-yellow-600' : 'text-gray-700'"
        >
          {{ formatSilenceDuration(silenceDuration) }}
        </span>
      </div>
      <!-- AI状态提示 -->
      <div
        v-if="isAISpeaking || isAIGenerating"
        class="mt-2 pt-2 border-t border-gray-200"
      >
        <div class="flex items-center justify-between">
          <span class="text-xs text-gray-500">AI状态</span>
          <span class="text-xs font-medium text-nanyu-600 flex items-center">
            <span class="inline-block animate-pulse mr-1">●</span>
            {{ isAIGenerating ? '生成中' : '播放中' }}
          </span>
        </div>
      </div>
    </div>
    <p
      v-if="!isRecording"
      class="text-center text-xs text-gray-400 mt-2"
    >
      等待中...
    </p>
  </div>
</template>

<script setup lang="ts">
interface Props {
  audioBars: number[]
  currentSpeaker: string | null
  isRecording: boolean
  silenceDuration: number
  isAISpeaking: boolean
  isAIGenerating: boolean
}

defineProps<Props>()

const formatSilenceDuration = (seconds: number): string => {
  if (seconds < 60) {
    return `${seconds}秒`
  }
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}分${remainingSeconds}秒`
}
</script>

