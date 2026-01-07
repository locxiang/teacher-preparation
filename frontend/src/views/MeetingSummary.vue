<template>
  <div class="max-w-[1600px] mx-auto px-6 pb-12">
    <!-- Loading State -->
    <div v-if="isLoading || isGenerating" class="min-h-screen flex items-center justify-center">
      <div class="text-center w-full max-w-md">
        <div class="mb-8">
          <div class="w-20 h-20 mx-auto mb-4 bg-nanyu-100 rounded-full flex items-center justify-center">
            <span class="text-4xl animate-spin">⏳</span>
          </div>
          <h2 class="text-2xl font-bold text-gray-800 mb-2">
            {{ isGenerating ? '正在生成会议总结...' : '加载会议信息...' }}
          </h2>
          <p class="text-gray-500 text-sm mb-6">
            {{ isGenerating ? 'AI正在分析会议内容，请稍候' : '正在获取会议数据' }}
          </p>
        </div>

        <!-- Progress Bar -->
        <div class="bg-gray-200 rounded-full h-3 overflow-hidden mb-4">
          <div
            class="bg-gradient-to-r from-nanyu-500 to-nanyu-600 h-full rounded-full transition-all duration-300 ease-out"
            :style="{ width: `${progress}%` }"
          ></div>
        </div>

        <!-- Progress Steps -->
        <div class="space-y-2 text-left">
          <div v-for="(step, index) in progressSteps" :key="index" class="flex items-center text-sm">
            <div
              class="w-5 h-5 rounded-full flex items-center justify-center mr-3 flex-shrink-0 transition-all"
              :class="step.completed
                ? 'bg-green-500 text-white'
                : step.active
                  ? 'bg-nanyu-500 text-white animate-pulse'
                  : 'bg-gray-200 text-gray-400'"
            >
              <span v-if="step.completed">✓</span>
              <span v-else-if="step.active">{{ index + 1 }}</span>
              <span v-else>{{ index + 1 }}</span>
            </div>
            <span
              :class="step.completed
                ? 'text-green-600 font-medium'
                : step.active
                  ? 'text-nanyu-600 font-medium'
                  : 'text-gray-400'"
            >
              {{ step.label }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Content State - 只要有会议数据就显示，即使没有摘要或出现错误 -->
    <div v-else-if="meeting" class="min-h-screen bg-gray-50">
      <!-- 错误提示横幅（如果有错误） -->
      <div v-if="errorMessage" class="bg-red-50 border-b border-red-200 sticky top-0 z-20">
        <div class="max-w-[1600px] mx-auto px-8 py-3">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <svg class="w-5 h-5 text-red-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p class="text-sm text-red-800 font-medium">{{ errorMessage }}</p>
            </div>
            <button
              @click="errorMessage = ''"
              class="text-red-600 hover:text-red-800 transition-colors"
              title="关闭"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>
      <!-- 顶部固定栏 - 企业级设计 -->
      <div class="bg-white border-b border-gray-200 sticky shadow-sm" :class="errorMessage ? 'top-[52px] z-10' : 'top-0 z-10'">
        <div class="max-w-[1600px] mx-auto px-8 py-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-6">
              <h1 class="text-2xl font-semibold text-gray-900">{{ meeting.name || '会议总结' }}</h1>
              <div class="flex items-center space-x-5 text-sm text-gray-500">
                <span class="flex items-center">
                  <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {{ formatDuration(meeting) }}
                </span>
                <span class="flex items-center">
                  <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                  {{ participantCount }}人
                </span>
                <span class="flex items-center">
                  <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  {{ messageCount }}条
                </span>
              </div>
            </div>
            <div class="flex items-center space-x-3">
              <button
                @click="handleDownloadSummary"
                :disabled="!summaryData"
                class="px-4 py-2 text-sm border border-gray-300 rounded text-gray-700 hover:bg-gray-50 font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                <span>下载总结</span>
              </button>
              <button
                @click="regenerateSummary"
                :disabled="isRegenerating"
                class="px-4 py-2 text-sm border border-gray-300 rounded text-gray-700 hover:bg-gray-50 font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ isRegenerating ? '重新生成中...' : '重新生成' }}
              </button>
              <router-link
                to="/"
                class="px-4 py-2 text-sm bg-nanyu-600 text-white rounded font-medium hover:bg-nanyu-700 transition-colors"
              >
                返回列表
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- 主内容区域 -->
      <div class="max-w-[1600px] mx-auto px-8 py-6">
        <div class="grid grid-cols-12 gap-6">
          <!-- 左侧主内容区 -->
          <div class="col-span-12 xl:col-span-8 space-y-5">
            <!-- 会议录音 - 紧凑设计 -->
            <div v-if="audioFiles.length > 0" class="bg-white border border-gray-200 rounded shadow-sm">
              <div class="px-5 py-3 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
                <div class="flex items-center space-x-3">
                  <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                  </svg>
                  <h3 class="text-sm font-semibold text-gray-900">会议录音</h3>
                  <span v-if="audioFiles[0].duration" class="text-xs text-gray-500">
                    {{ formatAudioDuration(audioFiles[0].duration) }}
                  </span>
                </div>
                <button
                  @click="downloadAudio(audioFiles[0].filename)"
                  class="text-xs px-3 py-1.5 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded transition-colors flex items-center space-x-1.5"
                  title="下载音频"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  <span>下载</span>
                </button>
              </div>
              <div class="p-4">
                <audio
                  :src="audioFiles[0].audioUrl"
                  controls
                  class="w-full h-10"
                  preload="none"
                >
                  您的浏览器不支持音频播放。
                </audio>
              </div>
            </div>
            <!-- 全文摘要 -->
            <div v-if="summaryData && (summaryData.paragraph_summary || summaryData.summary)" class="bg-white border border-gray-200 rounded shadow-sm">
              <div class="px-5 py-3 border-b border-gray-200 bg-gray-50">
                <h3 class="text-sm font-semibold text-gray-900 flex items-center">
                  <svg class="w-4 h-4 mr-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  全文摘要
                </h3>
              </div>
              <div class="p-5">
                <div class="text-gray-700 leading-relaxed whitespace-pre-wrap text-sm">
                  {{ summaryData.paragraph_summary || summaryData.summary }}
                </div>
              </div>
            </div>
            
            <!-- 无摘要数据时的提示 -->
            <div v-else-if="!summaryData && !isGenerating" class="bg-yellow-50 border border-yellow-200 rounded shadow-sm">
              <div class="p-5">
                <div class="flex items-start">
                  <svg class="w-5 h-5 text-yellow-600 mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <div class="flex-1">
                    <h3 class="text-sm font-semibold text-yellow-800 mb-1">暂无会议摘要</h3>
                    <p class="text-sm text-yellow-700 mb-3">会议摘要生成失败或尚未生成，您可以查看下方的完整对话记录。</p>
                    <button
                      v-if="meeting?.task_id"
                      @click="regenerateSummary"
                      :disabled="isRegenerating"
                      class="px-4 py-2 text-sm bg-yellow-600 text-white rounded font-medium hover:bg-yellow-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {{ isRegenerating ? '重新生成中...' : '重新生成摘要' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 发言总结 -->
            <div v-if="summaryData?.conversational_summary && summaryData.conversational_summary.length > 0" class="bg-white border border-gray-200 rounded shadow-sm">
              <div class="px-5 py-3 border-b border-gray-200 bg-gray-50">
                <h3 class="text-sm font-semibold text-gray-900 flex items-center">
                  <svg class="w-4 h-4 mr-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                  发言总结
                </h3>
              </div>
              <div class="p-5">
                <div class="space-y-4">
                  <div
                    v-for="(speaker, index) in summaryData.conversational_summary"
                    :key="index"
                    class="border border-gray-200 rounded p-4 hover:border-blue-300 hover:bg-blue-50/50 transition-colors"
                  >
                    <div class="flex items-start mb-2">
                      <div class="w-6 h-6 bg-blue-500 rounded flex items-center justify-center text-white text-xs font-semibold mr-3 mt-0.5 flex-shrink-0">
                        {{ index + 1 }}
                      </div>
                      <div class="flex-1 min-w-0">
                        <div class="font-semibold text-gray-900 text-sm mb-1">
                          {{ speaker.SpeakerName || speaker.SpeakerId || `发言人${index + 1}` }}
                          <span v-if="speaker.SpeakerId" class="text-xs text-gray-500 ml-2 font-normal">(ID: {{ speaker.SpeakerId }})</span>
                        </div>
                        <p class="text-gray-700 leading-relaxed text-sm">{{ speaker.Summary }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 问答回顾 -->
            <div v-if="summaryData?.questions_answering_summary && summaryData.questions_answering_summary.length > 0" class="bg-white border border-gray-200 rounded shadow-sm">
              <div class="px-5 py-3 border-b border-gray-200 bg-gray-50">
                <h3 class="text-sm font-semibold text-gray-900 flex items-center">
                  <svg class="w-4 h-4 mr-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  问答回顾
                </h3>
              </div>
              <div class="p-5">
                <div class="space-y-4">
                  <div
                    v-for="(qa, index) in summaryData.questions_answering_summary"
                    :key="index"
                    class="border border-gray-200 rounded p-4 hover:border-green-300 hover:bg-green-50/50 transition-colors"
                  >
                    <div class="mb-3">
                      <div class="flex items-start">
                        <span class="inline-flex items-center justify-center w-5 h-5 bg-green-500 text-white text-xs font-semibold rounded mr-3 mt-0.5 flex-shrink-0">Q</span>
                        <p class="text-gray-900 font-medium text-sm flex-1 leading-relaxed">{{ qa.Question }}</p>
                      </div>
                    </div>
                    <div class="pt-3 border-t border-gray-200">
                      <div class="flex items-start">
                        <span class="inline-flex items-center justify-center w-5 h-5 bg-emerald-500 text-white text-xs font-semibold rounded mr-3 mt-0.5 flex-shrink-0">A</span>
                        <p class="text-gray-700 leading-relaxed text-sm flex-1">{{ qa.Answer }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 思维导图 -->
            <div v-if="summaryData?.mind_map_summary && summaryData.mind_map_summary.length > 0" class="bg-white border border-gray-200 rounded shadow-sm">
              <div class="px-5 py-3 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
                <h3 class="text-sm font-semibold text-gray-900 flex items-center">
                  <svg class="w-4 h-4 mr-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                  </svg>
                  思维导图
                </h3>
              </div>
              <div class="p-5">
                <div
                  v-if="mindMapMermaidSyntax"
                  ref="mermaidRef"
                  class="mermaid relative"
                >
                    <button
                      @click="toggleFullscreen"
                      class="absolute top-3 right-3 z-10 px-3 py-1.5 text-xs bg-white border border-gray-300 rounded text-gray-700 hover:bg-gray-50 shadow-sm flex items-center space-x-1"
                      title="全屏查看"
                    >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                    </svg>
                    <span>全屏</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- 完整对话记录 -->
            <div class="bg-white border border-gray-200 rounded shadow-sm">
              <div
                class="px-5 py-3 border-b border-gray-200 bg-gray-50 flex justify-between items-center cursor-pointer hover:bg-gray-100 transition-colors"
                @click="showTranscript = !showTranscript"
              >
                <h3 class="text-sm font-semibold text-gray-900 flex items-center">
                  <svg class="w-4 h-4 mr-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  完整对话记录
                  <span class="ml-2 text-xs font-normal text-gray-500">({{ messageCount }}条)</span>
                </h3>
                <svg
                  class="w-4 h-4 text-gray-400 transform transition-transform"
                  :class="{ 'rotate-180': showTranscript }"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
              <div v-if="showTranscript" class="p-5 max-h-[500px] overflow-y-auto">
                <div class="space-y-3">
                  <div
                    v-for="(message, index) in messages"
                    :key="index"
                    class="p-3 border border-gray-200 rounded hover:border-gray-300 hover:bg-gray-50 transition-colors"
                  >
                    <div class="flex items-center justify-between mb-2">
                      <span v-if="message.speaker" class="text-xs font-medium text-gray-700 bg-gray-100 px-2 py-0.5 rounded">
                        {{ message.speaker }}
                      </span>
                      <span class="text-xs text-gray-400 font-mono">{{ formatTime(message.timestamp) }}</span>
                    </div>
                    <p class="text-gray-800 text-sm leading-relaxed">{{ message.content }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 右侧固定边栏 -->
          <div class="col-span-12 xl:col-span-4 space-y-5">
            <!-- 关键词 -->
            <div v-if="summaryData?.meeting_assistance?.keywords && summaryData.meeting_assistance.keywords.length > 0" class="bg-white border border-gray-200 rounded shadow-sm">
              <div class="px-5 py-3 border-b border-gray-200 bg-gray-50">
                <h3 class="text-sm font-semibold text-gray-900 flex items-center">
                  <svg class="w-4 h-4 mr-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                  </svg>
                  关键词
                </h3>
              </div>
              <div class="p-4">
                <div class="flex flex-wrap gap-2">
                  <span
                    v-for="(keyword, index) in summaryData.meeting_assistance.keywords"
                    :key="index"
                    class="px-2.5 py-1 bg-gray-100 text-gray-700 rounded text-xs font-medium border border-gray-200 hover:bg-gray-200 transition-colors cursor-default"
                  >
                    {{ keyword }}
                  </span>
                </div>
              </div>
            </div>

            <!-- 重点内容 -->
            <div v-if="summaryData?.meeting_assistance?.key_sentences && summaryData.meeting_assistance.key_sentences.length > 0" class="bg-white border border-gray-200 rounded shadow-sm">
              <div class="px-5 py-3 border-b border-gray-200 bg-gray-50">
                <h3 class="text-sm font-semibold text-gray-900 flex items-center">
                  <svg class="w-4 h-4 mr-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                  </svg>
                  重点内容
                </h3>
              </div>
              <div class="p-4">
                <div class="space-y-3">
                  <div
                    v-for="(sentence, index) in summaryData.meeting_assistance.key_sentences"
                    :key="index"
                    class="p-3 border border-gray-200 rounded hover:border-indigo-300 hover:bg-indigo-50/50 transition-colors"
                  >
                    <div class="flex items-center justify-between mb-2">
                      <span class="text-xs font-semibold text-indigo-700 bg-indigo-100 px-2 py-0.5 rounded">
                        重点 {{ index + 1 }}
                      </span>
                      <span v-if="sentence.Start !== undefined && sentence.End !== undefined" class="text-xs text-gray-500 font-mono">
                        {{ formatDurationFromMs(sentence.Start) }} - {{ formatDurationFromMs(sentence.End) }}
                      </span>
                    </div>
                    <p class="text-gray-800 text-xs leading-relaxed">{{ sentence.Text }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- 待办事项 -->
            <div class="bg-white border border-gray-200 rounded shadow-sm">
              <div class="px-5 py-3 border-b border-gray-200 bg-gray-50">
                <h3 class="text-sm font-semibold text-gray-900 flex items-center">
                  <svg class="w-4 h-4 mr-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                  待办事项
                </h3>
              </div>
              <div class="p-4">
                <!-- 新格式：meeting_assistance.actions -->
                <div v-if="summaryData?.meeting_assistance?.actions && summaryData.meeting_assistance.actions.length > 0" class="space-y-2">
                  <div
                    v-for="(action, index) in summaryData.meeting_assistance.actions"
                    :key="index"
                    class="flex items-start p-2.5 border border-gray-200 rounded hover:border-teal-300 hover:bg-teal-50/50 transition-colors"
                  >
                    <input
                      type="checkbox"
                      class="mt-0.5 mr-2.5 w-3.5 h-3.5 rounded border-gray-300 text-teal-600 focus:ring-teal-500 cursor-pointer"
                    />
                    <div class="flex-1 min-w-0">
                      <p class="text-gray-800 text-xs leading-relaxed">{{ action.Text }}</p>
                      <div v-if="action.Start !== undefined && action.End !== undefined" class="mt-1 text-xs text-gray-500 font-mono">
                        {{ formatDurationFromMs(action.Start) }} - {{ formatDurationFromMs(action.End) }}
                      </div>
                    </div>
                  </div>
                </div>
                <!-- 旧格式：action_items -->
                <div v-else-if="summaryData?.action_items && summaryData.action_items.length > 0" class="space-y-2">
                  <div
                    v-for="(item, index) in summaryData.action_items"
                    :key="index"
                    class="flex items-start p-2.5 border border-gray-200 rounded hover:border-teal-300 hover:bg-teal-50/50 transition-colors"
                  >
                    <input
                      type="checkbox"
                      :checked="item.completed"
                      class="mt-0.5 mr-2.5 w-3.5 h-3.5 rounded border-gray-300 text-teal-600 focus:ring-teal-500 cursor-pointer"
                    />
                    <div class="flex-1 min-w-0">
                      <p class="text-gray-800 text-xs leading-relaxed">{{ item.task }}</p>
                      <div v-if="item.assignee || item.deadline" class="mt-1 flex items-center flex-wrap gap-1.5 text-xs">
                        <span v-if="item.assignee" class="text-gray-600">
                          负责人: <span class="font-medium">{{ item.assignee }}</span>
                        </span>
                        <span v-if="item.deadline" class="text-red-600">
                          截止: <span class="font-medium">{{ item.deadline }}</span>
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                <!-- 无待办事项时的提示 -->
                <div v-else class="text-center py-6 text-gray-400">
                  <svg class="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                  <p class="text-xs">暂无待办事项</p>
                </div>
              </div>
            </div>

            <!-- 参与统计 -->
            <div v-if="participants.length > 0" class="bg-white border border-gray-200 rounded shadow-sm">
              <div class="px-5 py-3 border-b border-gray-200 bg-gray-50">
                <h3 class="text-sm font-semibold text-gray-900 flex items-center">
                  <svg class="w-4 h-4 mr-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                  参与统计
                </h3>
              </div>
              <div class="p-4">
                <div class="space-y-4">
                  <div
                    v-for="(participant, index) in participants"
                    :key="index"
                    class="space-y-1.5"
                  >
                    <div class="flex items-center justify-between">
                      <div class="flex items-center min-w-0 flex-1">
                        <span
                          class="w-3 h-3 rounded-full mr-2 flex-shrink-0"
                          :class="participant.color"
                        ></span>
                        <span class="text-sm font-medium text-gray-800 truncate">{{ participant.name }}</span>
                      </div>
                      <div class="flex items-center text-gray-600 space-x-2 ml-2 flex-shrink-0">
                        <span class="text-xs">{{ participant.count }}次</span>
                        <span class="text-gray-300">|</span>
                        <span class="text-xs font-semibold">{{ participant.percentage }}%</span>
                      </div>
                    </div>
                    <div class="w-full bg-gray-100 rounded-full h-1.5 overflow-hidden">
                      <div
                        class="h-1.5 rounded-full transition-all duration-300"
                        :class="participant.color"
                        :style="{ width: `${participant.percentage}%` }"
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="errorMessage" class="min-h-screen flex items-center justify-center">
      <div class="text-center">
        <div class="w-20 h-20 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center">
          <span class="text-4xl">❌</span>
        </div>
        <h2 class="text-2xl font-bold text-gray-800 mb-2">加载失败</h2>
        <p class="text-gray-500 mb-6">{{ errorMessage }}</p>
        <button
          @click="loadMeetingData"
          class="bg-nanyu-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-nanyu-700 transition-colors"
        >
          重试
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch, type ComponentPublicInstance } from 'vue'
import { useRoute } from 'vue-router'
import { getMeeting, completeMeeting, downloadSummary, type Meeting } from '@/services/meeting'
import mermaid from 'mermaid'

interface SummaryData {
  // 全文摘要
  paragraph_summary?: string
  summary?: string  // 兼容旧格式

  // 发言总结
  conversational_summary?: Array<{
    SpeakerId?: string
    SpeakerName?: string
    Summary?: string
  }>

  // 问答回顾
  questions_answering_summary?: Array<{
    Question?: string
    Answer?: string
    SentenceIdsOfQuestion?: number[]
    SentenceIdsOfAnswer?: number[]
  }>

  // 思维导图
  mind_map_summary?: Array<{
    Title?: string
    Topic?: Array<{
      Title?: string
      Topic?: any[]
    }>
  }>

  // 要点提炼
  meeting_assistance?: {
    keywords?: string[]  // 关键词
    key_sentences?: Array<{  // 重点内容（关键句）
      Id?: number
      SentenceId?: number
      Start?: number
      End?: number
      Text?: string
    }>
    actions?: Array<{  // 待办事项
      Id?: number
      SentenceId?: number
      Start?: number
      End?: number
      Text?: string
    }>
  }

  // MP3 音频 URL（来自 OutputMp3Path）
  mp3_url?: string

  // 兼容旧格式
  key_points?: Array<{ title?: string; content?: string }>
  consensus?: string[]
  disputes?: string[]
  action_items?: Array<{
    task: string
    assignee?: string
    deadline?: string
    completed?: boolean
  }>
}

interface Message {
  content: string
  speaker?: string
  timestamp: number
}

interface Participant {
  name: string
  count: number
  percentage: number
  color: string
}

const route = useRoute()
const meetingId = ref(route.params.id as string)

const isLoading = ref(true)
const isGenerating = ref(false)
const isRegenerating = ref(false)
const progress = ref(0)
const errorMessage = ref('')
const meeting = ref<Meeting | null>(null)
const summaryData = ref<SummaryData | null>(null)
const messages = ref<Message[]>([])
const showTranscript = ref(false)
const audioFiles = ref<Array<{ filename: string; duration?: number; fileSize?: number; audioUrl?: string }>>([])

// 进度步骤
const progressSteps = ref([
  { label: '查询任务状态', completed: false, active: false },
  { label: '分析会议内容', completed: false, active: false },
  { label: '下载摘要结果', completed: false, active: false },
  { label: '下载要点提炼', completed: false, active: false },
  { label: '保存摘要结果', completed: false, active: false },
])

// 进度跟踪
let queryCount = 0 // 查询任务状态的次数
const QUERY_PHASE_PROGRESS = 80 // 查询阶段占80%的进度
const DOWNLOAD_PHASE_PROGRESS = 20 // 下载和保存阶段占20%的进度

// 更新进度
const updateProgress = () => {
  if (!isGenerating.value) return

  const steps = progressSteps.value
  const completedSteps = steps.filter(s => s.completed).length

  // 根据步骤计算进度
  if (completedSteps === steps.length) {
    // 所有步骤都完成了
    progress.value = 100
  } else if (steps[0].active) {
    // 步骤0（查询任务状态）激活中
    // 根据查询次数平滑增长到80%
    // 假设最多查询30次，每次增加约2.67%
    const maxQueries = 30
    const progressPerQuery = QUERY_PHASE_PROGRESS / maxQueries
    const queryProgress = Math.min(queryCount * progressPerQuery, QUERY_PHASE_PROGRESS)
    progress.value = queryProgress
  } else if (steps[0].completed && completedSteps < steps.length) {
    // 查询阶段完成，进入下载和保存阶段
    // 基础进度80% + 后续步骤的进度（20%）
    const baseProgress = QUERY_PHASE_PROGRESS
    const remainingSteps = steps.length - 1 // 除了查询步骤外的其他步骤
    const completedAfterQuery = completedSteps - 1 // 查询步骤后的已完成步骤数
    const stepProgress = (completedAfterQuery / remainingSteps) * DOWNLOAD_PHASE_PROGRESS
    progress.value = Math.min(baseProgress + stepProgress, 100)
  } else {
    // 其他情况，使用已完成步骤的进度
    progress.value = (completedSteps / steps.length) * 100
  }
}

// 开始进度模拟
const startProgressSimulation = () => {
  progress.value = 0
  progressSteps.value.forEach(step => {
    step.completed = false
    step.active = false
  })

  // 步骤1: 加载会议信息
  progressSteps.value[0].active = true
  updateProgress()

  setTimeout(() => {
    progressSteps.value[0].completed = true
    progressSteps.value[0].active = false
    progressSteps.value[1].active = true
    updateProgress()

    // 步骤2: 分析会议内容
    setTimeout(() => {
      progressSteps.value[1].completed = true
      progressSteps.value[1].active = false
      progressSteps.value[2].active = true
      updateProgress()

      // 步骤3: 生成会议摘要
      setTimeout(() => {
        progressSteps.value[2].completed = true
        progressSteps.value[2].active = false
        progressSteps.value[3].active = true
        updateProgress()

        // 步骤4: 提取关键要点
        setTimeout(() => {
          progressSteps.value[3].completed = true
          progressSteps.value[3].active = false
          progressSteps.value[4].active = true
          updateProgress()

          // 步骤5: 完成
          setTimeout(() => {
            progressSteps.value[4].completed = true
            progressSteps.value[4].active = false
            progress.value = 100
            updateProgress()
          }, 500)
        }, 800)
      }, 1000)
    }, 600)
  }, 0)
}

// 解析转写文本为消息列表（支持 JSONL 格式和旧格式）
const parseTranscriptToMessages = (transcriptText: string): Message[] => {
  if (!transcriptText || !transcriptText.trim()) {
    return []
  }

  const lines = transcriptText.split('\n').filter(line => line.trim())
  const parsedMessages: Message[] = []

  lines.forEach((line, index) => {
    try {
      // 尝试解析 JSONL 格式（新格式）
      const messageData = JSON.parse(line)
      if (messageData.name && messageData.time && messageData.type && messageData.content) {
        parsedMessages.push({
          content: messageData.content,
          speaker: messageData.name,
          timestamp: messageData.time,
        })
        return
      }
    } catch {
      // 不是 JSON 格式，尝试解析旧格式
    }

    // 尝试解析旧格式（说话人: 内容）
    const match = line.match(/^(.+?)[：:]\s*(.+)$/)
    if (match) {
      const speakerName = match[1].trim()
      const content = match[2].trim()
      parsedMessages.push({
        content,
        speaker: speakerName,
        timestamp: Date.now() - (lines.length - index) * 1000, // 模拟时间戳
      })
    } else if (line.trim()) {
      // 如果没有匹配到格式，作为普通消息
      parsedMessages.push({
        content: line.trim(),
        speaker: undefined,
        timestamp: Date.now() - (lines.length - index) * 1000,
      })
    }
  })

  return parsedMessages
}

// 加载会议数据
const loadMeetingData = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const data = await getMeeting(meetingId.value)
    meeting.value = data

    // 如果会议状态是 running，自动将其更新为 completed
    if (data.status === 'running') {
      try {
        const updatedMeeting = await completeMeeting(meetingId.value)
        meeting.value = updatedMeeting
      } catch (error) {
        console.warn('更新会议状态失败:', error)
        // 不影响后续流程，继续执行
      }
    }

    // 解析转写记录为消息列表（支持 JSONL 格式和旧格式）
    if (data.transcripts && data.transcripts.length > 0) {
      // 使用最新的转写记录
      const latestTranscript = data.transcripts[data.transcripts.length - 1]
      if (latestTranscript.text) {
        messages.value = parseTranscriptToMessages(latestTranscript.text)
      }
    }

    // 检查是否已有摘要（从数据库中的 transcripts 获取）
    if (data.transcripts && data.transcripts.length > 0) {
      const latestTranscript = data.transcripts[data.transcripts.length - 1]
      if (latestTranscript.summary) {
        // 已有摘要，直接显示（从数据库读取）
        summaryData.value = latestTranscript.summary
        // 从 summaryData 中获取音频 URL
        if (summaryData.value?.mp3_url) {
          audioFiles.value = [{
            filename: '会议录音.mp3',
            audioUrl: summaryData.value.mp3_url,
          }]
        }
        isLoading.value = false
        return
      }
    }

    // 如果没有摘要，检查是否有 task_id，如果有则尝试从 API 获取
    if (data.task_id) {
      isLoading.value = false
      await generateSummary()
    } else {
      // 没有 task_id，无法生成摘要
      errorMessage.value = '会议没有关联的通义听悟任务，无法生成摘要'
      isLoading.value = false
    }

    // 从 summaryData 中获取音频 URL（不需要单独调用接口）
    if (summaryData.value?.mp3_url) {
      audioFiles.value = [{
        filename: '会议录音.mp3',
        audioUrl: summaryData.value.mp3_url,
      }]
    }
  } catch (error) {
    console.error('加载会议数据失败:', error)
    errorMessage.value = error instanceof Error ? error.message : '加载会议数据失败'
    isLoading.value = false
  }
}

// 不再需要 loadAudioFiles 函数，音频 URL 直接从 summaryData.mp3_url 获取

// 下载音频文件
const downloadAudio = async (filename: string) => {
  try {
    // 从 audioFiles 中找到对应的文件，使用其完整的 URL
    const audioFile = audioFiles.value.find(file => file.filename === filename)
    if (!audioFile || !audioFile.audioUrl) {
      throw new Error('找不到音频文件 URL')
    }

    // 直接使用 URL 下载（OutputMp3Path 已经是完整的 URL）
    const response = await fetch(audioFile.audioUrl, {
      method: 'GET',
    })

    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } else {
      throw new Error('下载失败')
    }
  } catch (error) {
    console.error('下载音频文件失败:', error)
    alert('下载音频文件失败，请稍后重试')
  }
}

// 下载会议总结
const handleDownloadSummary = async () => {
  try {
    await downloadSummary(meetingId.value)
  } catch (error) {
    console.error('下载会议总结失败:', error)
    alert(error instanceof Error ? error.message : '下载会议总结失败，请稍后重试')
  }
}

// 格式化音频时长（秒转 MM:SS）
const formatAudioDuration = (seconds: number): string => {
  if (!seconds) return '00:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
}

// 生成摘要 - 使用 SSE 流式接口
const generateSummary = async () => {
  // 设置生成状态，关闭初始加载状态
  isLoading.value = false
  isGenerating.value = true
  errorMessage.value = ''
  progress.value = 0

  // 重置进度步骤和查询计数
  progressSteps.value.forEach(step => {
    step.completed = false
    step.active = false
  })
  queryCount = 0

  try {
    // 使用相对路径，让浏览器自动使用当前访问的域名/IP
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
    const token = localStorage.getItem('access_token')

    const response = await fetch(`${API_BASE_URL}/api/meetings/${meetingId.value}/summary/stream`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`)
    }

    if (!response.body) {
      throw new Error('响应体为空')
    }

    // 读取 SSE 流
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()

      if (done) {
        break
      }

      // 解码数据块
      buffer += decoder.decode(value, { stream: true })

      // 处理 SSE 格式的数据
      const lines = buffer.split('\n')
      buffer = lines.pop() || '' // 保留最后一个不完整的行

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6) // 移除 'data: ' 前缀

          // 检查是否是结束标记
          if (data === '[DONE]') {
            progress.value = 100
            // 标记所有步骤为完成
            progressSteps.value.forEach(step => {
              step.completed = true
              step.active = false
            })
            isGenerating.value = false
            // 跳出 while 循环
            reader.cancel()
            return
          }

          try {
            // 解析 JSON 数据
            const parsed = JSON.parse(data)

            // 根据消息类型更新 UI
            switch (parsed.type) {
              case 'start':
                // 开始查询任务状态
                progressSteps.value[0].active = true
                queryCount = 0
                updateProgress()
                break

              case 'status':
                // 根据消息内容更新进度步骤
                const message = parsed.message || ''

                if (message.includes('开始查询任务状态')) {
                  // 步骤0: 开始查询任务状态
                  if (!progressSteps.value[0].active) {
                    progressSteps.value[0].active = true
                  }
                  queryCount = 0
                  updateProgress()
                } else if (message.includes('正在查询任务状态')) {
                  // 步骤0: 正在查询任务状态，增加查询计数
                  queryCount++
                  if (!progressSteps.value[0].active) {
                    progressSteps.value[0].active = true
                  }
                  updateProgress()
                } else if (message.includes('任务状态: COMPLETED') || message.includes('任务已完成')) {
                  // 完成步骤0，激活步骤1
                  progressSteps.value[0].completed = true
                  progressSteps.value[0].active = false
                  progressSteps.value[1].active = true
                  updateProgress()
                } else if (message.includes('任务状态: PAUSED') || message.includes('任务已暂停')) {
                  // 任务已暂停，保持当前步骤激活，显示等待状态
                  if (!progressSteps.value[0].active) {
                    progressSteps.value[0].active = true
                  }
                  updateProgress()
                } else if (message.includes('等待恢复中')) {
                  // 任务暂停后等待恢复，保持当前步骤激活
                  if (!progressSteps.value[0].active) {
                    progressSteps.value[0].active = true
                  }
                  updateProgress()
                } else if (message.includes('正在下载摘要结果')) {
                  // 激活步骤2
                  progressSteps.value[1].completed = true
                  progressSteps.value[1].active = false
                  progressSteps.value[2].active = true
                  updateProgress()
                } else if (message.includes('摘要结果下载完成')) {
                  // 完成步骤2，激活步骤3
                  progressSteps.value[2].completed = true
                  progressSteps.value[2].active = false
                  progressSteps.value[3].active = true
                  updateProgress()
                } else if (message.includes('正在下载要点提炼结果')) {
                  // 保持步骤3激活
                  if (!progressSteps.value[3].active) {
                    progressSteps.value[3].active = true
                  }
                  updateProgress()
                } else if (message.includes('要点提炼结果下载完成')) {
                  // 完成步骤3，激活步骤4
                  progressSteps.value[3].completed = true
                  progressSteps.value[3].active = false
                  progressSteps.value[4].active = true
                  updateProgress()
                } else if (message.includes('正在下载音频文件')) {
                  // 保持步骤4激活（音频下载是额外步骤，不影响主要流程）
                  if (!progressSteps.value[4].active) {
                    progressSteps.value[4].active = true
                  }
                  updateProgress()
                } else if (message.includes('音频文件下载完成')) {
                  // 音频下载完成，继续步骤4
                  updateProgress()
                } else if (message.includes('正在保存摘要结果')) {
                  // 保持步骤4激活
                  if (!progressSteps.value[4].active) {
                    progressSteps.value[4].active = true
                  }
                  updateProgress()
                }
                break

              case 'warning':
                console.warn('警告:', parsed.message)
                break

              case 'error':
                throw new Error(parsed.message)

              case 'complete':
                // 完成所有步骤
                progressSteps.value.forEach(step => {
                  step.completed = true
                  step.active = false
                })
                progress.value = 100

                // 更新会议数据
                if (parsed.data) {
                  meeting.value = parsed.data

                  // 解析摘要数据（从 transcripts 中获取）
                  if (parsed.data.transcripts && parsed.data.transcripts.length > 0) {
                    const latestTranscript = parsed.data.transcripts[parsed.data.transcripts.length - 1]
                    if (latestTranscript.summary) {
                      summaryData.value = latestTranscript.summary
                      // 调试日志：检查思维导图数据
                      console.log('摘要数据已更新，思维导图数据:', summaryData.value?.mind_map_summary)
                    }
                  } else if (parsed.data.summary) {
                    // 兼容旧格式
                    if (typeof parsed.data.summary === 'string') {
                      try {
                        summaryData.value = JSON.parse(parsed.data.summary)
                      } catch {
                        summaryData.value = { summary: parsed.data.summary }
                      }
                    } else {
                      summaryData.value = parsed.data.summary
                    }
                    // 调试日志：检查思维导图数据
                    console.log('摘要数据已更新（旧格式），思维导图数据:', summaryData.value?.mind_map_summary)
                  }

                  // 从 summaryData 中获取音频 URL
                  if (summaryData.value?.mp3_url) {
                    audioFiles.value = [{
                      filename: '会议录音.mp3',
                      audioUrl: summaryData.value.mp3_url,
                    }]
                  }

                  // 解析转写记录为消息列表（支持 JSONL 格式和旧格式）
                  if (parsed.data.transcripts && parsed.data.transcripts.length > 0) {
                    const latestTranscript = parsed.data.transcripts[parsed.data.transcripts.length - 1]
                    if (latestTranscript.text) {
                      messages.value = parseTranscriptToMessages(latestTranscript.text)
                    }
                  }
                }

                // 从 summaryData 中获取音频 URL（不需要单独调用接口）
                if (summaryData.value?.mp3_url) {
                  audioFiles.value = [{
                    filename: '会议录音.mp3',
                    audioUrl: summaryData.value.mp3_url,
                  }]
                }

                // 关闭生成状态
                isGenerating.value = false
                
                // 如果摘要数据已更新，重新渲染思维导图
                if (summaryData.value?.mind_map_summary && summaryData.value.mind_map_summary.length > 0) {
                  // 使用 nextTick 确保 DOM 已更新
                  await nextTick()
                  renderMermaidMindmap()
                }
                break
            }
          } catch (parseError) {
            // 如果不是 JSON，忽略
            console.warn('解析 SSE 数据失败:', parseError)
          }
        } else if (line.trim() === '') {
          // 空行，忽略
          continue
        }
      }
    }
  } catch (error) {
    console.error('生成摘要失败:', error)
    errorMessage.value = error instanceof Error ? error.message : '生成摘要失败'
    // 标记所有步骤为未完成
    progressSteps.value.forEach(step => {
      step.completed = false
      step.active = false
    })
    isGenerating.value = false
  } finally {
    // 确保在结束时关闭生成状态
    if (isGenerating.value) {
      isGenerating.value = false
    }
    if (progress.value < 100) {
      progress.value = 100
    }
  }
}

// 重新生成摘要
const regenerateSummary = async () => {
  isRegenerating.value = true
  // 清除旧的摘要数据，确保重新生成时显示新数据
  summaryData.value = null
  // 清空思维导图容器
  if (mermaidRef.value) {
    mermaidRef.value.innerHTML = ''
  }
  // 清空错误消息
  errorMessage.value = ''
  errorBannerMessage.value = ''
  showErrorBanner.value = false
  // 重新生成摘要
  await generateSummary()
  isRegenerating.value = false
}

// 计算参与统计
// 转换思维导图数据为 Mermaid 语法（递归函数）
const convertToMermaidSyntax = (node: { Title?: string; Topic?: any[] }, indent = 0): string => {
  const indentStr = '    '.repeat(indent)
  const title = (node.Title || '未命名节点').replace(/\n/g, ' ')
  let result = `${indentStr}${title}\n`

  if (node.Topic && node.Topic.length > 0) {
    node.Topic.forEach(subNode => {
      result += convertToMermaidSyntax(subNode, indent + 1)
    })
  }

  return result
}

// 思维导图 Mermaid 语法（转换为 Mermaid 需要的格式）
const mindMapMermaidSyntax = computed(() => {
  if (!summaryData.value?.mind_map_summary || summaryData.value.mind_map_summary.length === 0) {
    return ''
  }

  // 只处理第一个思维导图节点
  const rootNode = summaryData.value.mind_map_summary[0]
  const content = convertToMermaidSyntax(rootNode, 1)
  // 使用默认样式，不配置主题
  return `
mindmap
${content}`
})

// Mermaid 容器引用
const mermaidRef = ref<HTMLElement | null>(null)

// 渲染 Mermaid 思维导图
const renderMermaidMindmap = async () => {
  if (!mermaidRef.value || !mindMapMermaidSyntax.value) {
    return
  }

  const mermaidElement = mermaidRef.value
  mermaidElement.innerHTML = '' // 清空容器

  try {
    // 使用 mermaid.render，返回 Promise
    const uniqueId = `mermaid-mindmap-${Date.now()}`
    const { svg } = await mermaid.render(uniqueId, mindMapMermaidSyntax.value)
    mermaidElement.innerHTML = svg
  } catch (error) {
    console.error('Mermaid 渲染失败:', error)
    mermaidElement.innerHTML = '<div class="text-center text-gray-500 p-4">思维导图渲染失败</div>'
  }
}

// 监听思维导图数据变化，自动渲染
watch(() => mindMapMermaidSyntax.value, (newValue) => {
  console.log('思维导图语法已更新:', newValue ? '有数据' : '无数据')
  if (newValue) {
    nextTick(() => {
      renderMermaidMindmap()
    })
  } else if (mermaidRef.value) {
    // 如果没有数据，清空容器
    mermaidRef.value.innerHTML = ''
  }
}, { immediate: true })

const participants = computed<Participant[]>(() => {
  const speakerCounts: Record<string, number> = {}
  messages.value.forEach(msg => {
    // 只统计有说话人且不是"未知"的消息
    if (msg.speaker && msg.speaker !== '未知') {
      speakerCounts[msg.speaker] = (speakerCounts[msg.speaker] || 0) + 1
    }
  })

  const total = messages.value.length
  const colors = ['bg-blue-500', 'bg-pink-500', 'bg-green-500', 'bg-yellow-500', 'bg-purple-500']

  return Object.entries(speakerCounts)
    .map(([name, count], index) => ({
      name,
      count,
      percentage: total > 0 ? Math.round((count / total) * 100) : 0,
      color: colors[index % colors.length],
    }))
    .sort((a, b) => b.count - a.count)
})

// 参与人数：直接使用会议创建时选择的教师数量
const participantCount = computed(() => {
  return meeting.value?.teachers?.length || 0
})

// 消息数量：统计所有有内容的消息（包括没有说话人的）
const messageCount = computed(() => {
  return messages.value.filter(msg => msg.content && msg.content.trim()).length
})

// 格式化时长
const formatDuration = (meeting: Meeting): string => {
  if (!meeting.created_at) return '0分0秒'
  const start = new Date(meeting.created_at).getTime()
  const end = meeting.updated_at ? new Date(meeting.updated_at).getTime() : Date.now()
  const duration = Math.floor((end - start) / 1000)
  const minutes = Math.floor(duration / 60)
  const seconds = duration % 60
  return `${minutes}分${seconds}秒`
}

// 格式化时间
const formatTime = (timestamp: number): string => {
  const date = new Date(timestamp)
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}:${date.getSeconds().toString().padStart(2, '0')}`
}

// 格式化毫秒为时间（MM:SS）
const formatDurationFromMs = (ms: number): string => {
  const seconds = Math.floor(ms / 1000)
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`
}

// 全屏切换
const toggleFullscreen = () => {
  if (!mermaidRef.value) return

  if (!document.fullscreenElement) {
    mermaidRef.value.requestFullscreen().catch((err: Error) => {
      console.error(`全屏模式失败: ${err.message}`)
      alert('无法进入全屏模式，请检查浏览器设置')
    })
  } else {
    document.exitFullscreen().catch((err: Error) => {
      console.error(`退出全屏失败: ${err.message}`)
    })
  }
}

onMounted(async () => {
  // 初始化 Mermaid API（参考博客文章的方式）
  mermaid.mermaidAPI.initialize()

  await loadMeetingData()

  // 数据加载完成后渲染思维导图
  await nextTick()
  if (mindMapMermaidSyntax.value) {
    renderMermaidMindmap()
  }
})

</script>
