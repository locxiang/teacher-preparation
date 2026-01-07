<!-- eslint-disable vue/multi-word-component-names -->
<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <!-- 顶部固定栏 -->
    <div class="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
      <div class="max-w-[1600px] mx-auto px-8 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <div>
              <h1 class="text-2xl font-semibold text-gray-900 flex items-center">
                语音识别测试
                <span
                  v-if="taskInfo"
                  class="ml-3 text-xs px-2 py-1 rounded bg-green-100 text-green-700 font-medium"
                >
                  ● 任务运行中
                </span>
                <span
                  v-else
                  class="ml-3 text-xs px-2 py-1 rounded bg-gray-100 text-gray-600 font-medium"
                >
                  ○ 未开始
                </span>
              </h1>
              <p class="text-sm text-gray-500 mt-1">
                {{ formatTime(new Date()) }}
                <span
                  v-if="taskInfo?.TaskId"
                  class="ml-2 font-mono text-xs"
                >
                  Task ID: {{ taskInfo.TaskId.substring(0, 8) }}...
                </span>
                <span
                  v-if="historyList.length > 0"
                  class="ml-2"
                >
                  | {{ historyList.length }}条识别记录
                </span>
              </p>
            </div>
          </div>
          <div class="flex items-center space-x-2">
            <!-- 任务状态提示 -->
            <div
              v-if="!taskInfo?.MeetingJoinUrl && !isCreatingTask"
              class="text-xs text-yellow-600 px-3 py-1.5 rounded bg-yellow-50 border border-yellow-200"
            >
              ⚠️ 请先创建实时记录任务
            </div>

            <!-- 麦克风授权按钮 -->
            <button
              v-if="!hasMicrophonePermission && taskInfo?.MeetingJoinUrl"
              :disabled="isRequestingPermission"
              class="px-3 py-1.5 text-xs bg-blue-50 text-blue-700 hover:bg-blue-100 rounded border border-blue-200 transition-colors flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
              @click="requestMicrophonePermission"
            >
              <span class="mr-1">🎤</span>
              {{ isRequestingPermission ? '请求授权中...' : '授权麦克风' }}
            </button>

            <!-- 开始/停止录音按钮 -->
            <button
              v-else-if="hasMicrophonePermission && taskInfo?.MeetingJoinUrl"
              :disabled="status === 'init' || !taskInfo"
              :class="[
                'px-3 py-1.5 text-xs rounded border transition-colors flex items-center',
                status === 'ing'
                  ? 'bg-yellow-50 text-yellow-700 hover:bg-yellow-100 border-yellow-200'
                  : 'bg-green-50 text-green-700 hover:bg-green-100 border-green-200',
                (status === 'init' || !taskInfo) ? 'opacity-50 cursor-not-allowed' : ''
              ]"
              @click="toggleRecording"
            >
              <span class="mr-1">{{ status === 'ing' ? '⏸️' : '▶️' }}</span>
              {{ buttonText }}
            </button>

            <!-- WebSocket连接状态 -->
            <div
              :class="wsConnected ? 'bg-green-50 text-green-700 border-green-200' : 'bg-gray-50 text-gray-600 border-gray-200'"
              class="px-3 py-1.5 text-xs rounded border flex items-center"
            >
              <span
                :class="wsConnected ? 'bg-green-500' : 'bg-gray-400'"
                class="w-2 h-2 rounded-full mr-1.5"
                :style="wsConnected ? 'animation: pulse 1s infinite;' : ''"
              />
              {{ wsConnected ? '已连接' : '未连接' }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <div class="max-w-[1600px] mx-auto px-8 py-4 w-full flex-1 flex flex-col min-h-0">
        <div class="flex-1 flex space-x-4 overflow-hidden min-h-0">
          <!-- Left Sidebar -->
          <div class="w-80 flex flex-col space-y-4 overflow-y-auto shrink-0">
            <!-- 任务配置卡片 -->
            <div class="bg-white border border-gray-200 rounded shadow-sm p-4">
              <h3 class="text-sm font-semibold text-gray-900 mb-3 flex items-center">
                <svg
                  class="w-4 h-4 mr-2 text-gray-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
                任务配置
              </h3>

              <!-- 任务信息显示 -->
              <div
                v-if="taskInfo"
                class="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg"
              >
                <div class="text-xs text-gray-600 mb-1 font-medium">
                  任务ID:
                </div>
                <div class="text-xs font-mono text-gray-800 break-all mb-2">
                  {{ taskInfo.TaskId }}
                </div>
                <div
                  v-if="taskInfo.TaskStatus"
                  class="mt-2"
                >
                  <div class="text-xs text-gray-600 mb-1 font-medium">
                    任务状态:
                  </div>
                  <div class="text-xs font-medium text-green-700">
                    {{ taskInfo.TaskStatus }}
                  </div>
                </div>
              </div>

              <!-- 创建任务表单 -->
              <div
                v-if="!taskInfo"
                class="space-y-3"
              >
                <div>
                  <label class="block text-xs font-medium text-gray-700 mb-1">音频格式</label>
                  <select
                    v-model="createTaskParams.audio_format"
                    class="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="pcm">
                      PCM
                    </option>
                    <option value="opus">
                      OPUS
                    </option>
                    <option value="aac">
                      AAC
                    </option>
                    <option value="speex">
                      SPEEX
                    </option>
                    <option value="mp3">
                      MP3
                    </option>
                  </select>
                </div>

                <div>
                  <label class="block text-xs font-medium text-gray-700 mb-1">采样率</label>
                  <select
                    v-model="createTaskParams.sample_rate"
                    class="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option :value="16000">
                      16000 Hz
                    </option>
                    <option :value="8000">
                      8000 Hz
                    </option>
                  </select>
                </div>

                <div>
                  <label class="block text-xs font-medium text-gray-700 mb-1">源语言</label>
                  <select
                    v-model="createTaskParams.source_language"
                    class="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="cn">
                      中文
                    </option>
                    <option value="en">
                      英文
                    </option>
                    <option value="yue">
                      粤语
                    </option>
                    <option value="ja">
                      日语
                    </option>
                    <option value="ko">
                      韩语
                    </option>
                    <option value="multilingual">
                      多语种
                    </option>
                  </select>
                </div>

                <div>
                  <label class="block text-xs font-medium text-gray-700 mb-1">任务标识（可选）</label>
                  <input
                    v-model="createTaskParams.task_key"
                    type="text"
                    placeholder="自定义任务标识"
                    class="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                </div>

                <div class="space-y-1.5 pt-1">
                  <label class="flex items-center text-xs">
                    <input
                      v-model="createTaskParams.enable_summary"
                      type="checkbox"
                      class="mr-2"
                    >
                    <span class="text-gray-700">开启摘要</span>
                  </label>
                  <label class="flex items-center text-xs">
                    <input
                      v-model="createTaskParams.enable_key_points"
                      type="checkbox"
                      class="mr-2"
                    >
                    <span class="text-gray-700">开启要点提炼</span>
                  </label>
                  <label class="flex items-center text-xs">
                    <input
                      v-model="createTaskParams.enable_translation"
                      type="checkbox"
                      class="mr-2"
                    >
                    <span class="text-gray-700">开启翻译</span>
                  </label>
                </div>

                <button
                  :disabled="isCreatingTask"
                  class="w-full py-2 rounded text-sm font-medium transition-all duration-300 flex items-center justify-center bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50 disabled:cursor-not-allowed"
                  @click="createTask"
                >
                  <span
                    v-if="isCreatingTask"
                    class="mr-2"
                  >⏳</span>
                  <span
                    v-else
                    class="mr-2"
                  >➕</span>
                  {{ isCreatingTask ? '创建中...' : '创建实时记录' }}
                </button>
              </div>

              <!-- 停止任务按钮 -->
              <div
                v-if="taskInfo"
                class="space-y-2"
              >
                <button
                  :disabled="isStoppingTask"
                  class="w-full py-2 rounded text-sm font-medium transition-all duration-300 flex items-center justify-center bg-red-600 hover:bg-red-700 text-white disabled:opacity-50 disabled:cursor-not-allowed"
                  @click="stopTask"
                >
                  <span
                    v-if="isStoppingTask"
                    class="mr-2"
                  >⏳</span>
                  <span
                    v-else
                    class="mr-2"
                  >⏹️</span>
                  {{ isStoppingTask ? '停止中...' : '停止实时记录' }}
                </button>
                <button
                  class="w-full py-1.5 rounded text-sm font-medium transition-all duration-300 flex items-center justify-center bg-gray-200 hover:bg-gray-300 text-gray-700"
                  @click="resetTask"
                >
                  重置
                </button>
              </div>

              <!-- 错误信息 -->
              <div
                v-if="errorMessage"
                class="mt-3 p-2 bg-red-50 border border-red-200 rounded"
              >
                <p class="text-xs text-red-600">
                  {{ errorMessage }}
                </p>
              </div>
            </div>

            <!-- 音频波形可视化 -->
            <div class="bg-white border border-gray-200 rounded shadow-sm p-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs text-gray-500">音频波形</span>
                <span class="text-xs font-medium text-gray-700">
                  {{ status === 'ing' ? '录音中' : '等待中...' }}
                </span>
              </div>
              <div class="flex items-end justify-center space-x-0.5 h-20 bg-gray-50 rounded p-2">
                <div
                  v-for="(bar, index) in audioBars"
                  :key="index"
                  class="w-1 bg-blue-400 rounded-t transition-all duration-75"
                  :style="{ height: `${bar}%`, minHeight: '2px' }"
                />
              </div>
            </div>
          </div>

          <!-- Right Column: 识别结果和调试信息 -->
          <div class="flex-1 flex flex-col overflow-hidden min-h-0">
            <!-- 实时识别结果 -->
            <div class="bg-white border border-gray-200 rounded shadow-sm flex flex-col overflow-hidden mb-4 grow min-h-0">
              <div class="px-5 py-3 border-b border-gray-200 bg-gray-50 flex justify-between items-center shrink-0">
                <h3 class="text-sm font-semibold text-gray-900 flex items-center">
                  <svg
                    class="w-4 h-4 mr-2 text-gray-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                    />
                  </svg>
                  实时识别结果
                </h3>
              </div>

              <div class="grow overflow-y-auto p-4 space-y-3">
                <!-- 临时识别结果 -->
                <div
                  v-if="resultTextTemp"
                  class="p-4 bg-blue-50 border border-blue-200 rounded-lg"
                >
                  <div class="flex items-center mb-2">
                    <span class="text-xs font-medium text-blue-600 bg-blue-100 px-2 py-1 rounded">临时结果</span>
                    <span class="ml-2 text-xs text-gray-500">正在识别中...</span>
                    <span
                      v-if="currentSpeaker"
                      class="ml-auto text-xs font-medium text-blue-700 bg-blue-200 px-2 py-1 rounded"
                    >
                      {{ currentSpeaker }}
                    </span>
                  </div>
                  <p class="text-gray-800 text-sm">
                    {{ resultTextTemp }}
                  </p>
                </div>

                <!-- 最终识别结果 -->
                <div
                  v-if="resultText && !resultTextTemp"
                  class="p-4 bg-green-50 border border-green-200 rounded-lg"
                >
                  <div class="flex items-center mb-2">
                    <span class="text-xs font-medium text-green-600 bg-green-100 px-2 py-1 rounded">最终结果</span>
                    <span
                      v-if="currentSpeaker"
                      class="ml-auto text-xs font-medium text-green-700 bg-green-200 px-2 py-1 rounded"
                    >
                      {{ currentSpeaker }}
                    </span>
                  </div>
                  <p class="text-gray-800 text-sm">
                    {{ resultText }}
                  </p>
                </div>

                <!-- 空状态 -->
                <div
                  v-if="!resultText && !resultTextTemp"
                  class="text-center py-12 text-gray-400"
                >
                  <svg
                    class="w-12 h-12 mx-auto mb-3 text-gray-300"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                    />
                  </svg>
                  <p class="text-sm mb-1">
                    暂无识别结果
                  </p>
                  <p class="text-xs">
                    开始录音后，识别结果将显示在这里
                  </p>
                </div>
              </div>
            </div>

            <!-- 识别历史记录 -->
            <div
              class="bg-white border border-gray-200 rounded shadow-sm flex flex-col overflow-hidden mb-4"
              style="max-height: 300px;"
            >
              <div class="px-5 py-3 border-b border-gray-200 bg-gray-50 flex justify-between items-center shrink-0">
                <h3 class="text-sm font-semibold text-gray-900 flex items-center">
                  <svg
                    class="w-4 h-4 mr-2 text-gray-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  识别历史
                </h3>
                <button
                  class="text-xs text-gray-600 hover:text-gray-800 px-2 py-1 border border-gray-300 rounded hover:bg-gray-50 transition-colors"
                  @click="clearHistory"
                >
                  清空记录
                </button>
              </div>

              <div class="grow overflow-y-auto p-4 space-y-2">
                <div
                  v-for="(item, index) in historyList"
                  :key="index"
                  class="p-3 bg-gray-50 rounded border border-gray-200"
                >
                  <div class="flex items-center justify-between mb-1.5">
                    <span class="text-xs text-gray-500">{{ formatTimeForHistory(item.timestamp) }}</span>
                    <span
                      v-if="item.speaker"
                      class="text-xs font-medium text-purple-600 bg-purple-100 px-2 py-0.5 rounded"
                    >
                      {{ item.speaker }}
                    </span>
                  </div>
                  <p class="text-sm text-gray-800">
                    {{ item.text }}
                  </p>
                </div>

                <div
                  v-if="historyList.length === 0"
                  class="text-center py-6 text-gray-400"
                >
                  <p class="text-xs">
                    暂无历史记录
                  </p>
                </div>
              </div>
            </div>

            <!-- WebSocket消息调试输出 -->
            <div class="bg-white border border-gray-200 rounded shadow-sm flex flex-col overflow-hidden grow min-h-0">
              <div class="px-5 py-3 border-b border-gray-200 bg-gray-50 flex justify-between items-center shrink-0">
                <div class="flex items-center gap-3">
                  <h3 class="text-sm font-semibold text-gray-900 flex items-center">
                    <svg
                      class="w-4 h-4 mr-2 text-gray-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                      />
                    </svg>
                    WebSocket消息调试
                  </h3>
                  <span class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                    共 {{ wsMessages.length }} 条消息
                  </span>
                </div>
                <button
                  class="text-xs text-gray-600 hover:text-gray-800 px-2 py-1 border border-gray-300 rounded hover:bg-gray-50 transition-colors"
                  @click="clearWsMessages"
                >
                  清空消息
                </button>
              </div>

              <div class="grow overflow-y-auto p-4 space-y-2">
                <div
                  v-for="(msg, index) in wsMessages"
                  :key="index"
                  class="border rounded-lg overflow-hidden transition-all border-l-4"
                  :class="getMessageCardClass(msg.type)"
                >
                  <!-- 消息头部 -->
                  <div
                    class="px-3 py-2 cursor-pointer hover:bg-opacity-80 transition-colors"
                    :class="getMessageHeaderClass(msg.type)"
                    @click="toggleMessage(index)"
                  >
                    <!-- 第一行：基本信息 -->
                    <div class="flex items-center justify-between mb-1.5">
                      <div class="flex items-center gap-2 flex-1 min-w-0">
                        <span class="text-xs font-mono text-gray-600 whitespace-nowrap">{{ formatTime(msg.timestamp) }}</span>
                        <span
                          class="text-xs font-semibold px-1.5 py-0.5 rounded whitespace-nowrap"
                          :class="getMessageTypeBadgeClass(msg.type)"
                        >
                          {{ getMessageTypeLabel(msg.type) }}
                        </span>
                      </div>
                      <div class="flex items-center gap-2">
                        <span class="text-xs text-gray-500">{{ expandedMessages.has(index) ? '▼' : '▶' }}</span>
                      </div>
                    </div>

                    <!-- 第二行：识别文字（如果有） -->
                    <div
                      v-if="extractRecognizedText(msg.parsed)"
                      class="mt-1.5 pt-1.5 border-t border-gray-300 border-opacity-50"
                    >
                      <div class="flex items-start gap-2">
                        <span class="text-xs font-semibold text-gray-600 whitespace-nowrap">识别文字:</span>
                        <span class="text-xs font-medium text-gray-900 flex-1">{{ extractRecognizedText(msg.parsed) }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- 消息内容（可折叠） -->
                  <div
                    v-if="expandedMessages.has(index)"
                    class="px-3 py-2 bg-gray-50 border-t"
                  >
                    <pre class="text-xs text-gray-800 overflow-x-auto whitespace-pre-wrap wrap-break-word font-mono bg-white p-2 rounded border">{{ formatJson(msg.data, msg.parsed) }}</pre>
                  </div>
                </div>

                <div
                  v-if="wsMessages.length === 0"
                  class="text-center py-8 text-gray-400"
                >
                  <svg
                    class="w-10 h-10 mx-auto mb-2 text-gray-300"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                    />
                  </svg>
                  <p class="text-xs mb-1">
                    暂无WebSocket消息
                  </p>
                  <p class="text-xs">
                    开始录音后，WebSocket返回的消息将显示在这里
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { AliyunASRDirectService } from '@/services/aliyun-asr-direct'
import type { RecognitionResult } from '@/services/aliyun-asr'

// 识别结果接口（带说话人信息）
interface RecognitionResultWithSpeaker extends RecognitionResult {
  speakerName?: string
}

// 状态管理
const status = ref<'null' | 'init' | 'ing' | 'end'>('null')
const resultText = ref('')
const resultTextTemp = ref('')
const errorMessage = ref('')
const audioBars = ref<number[]>(Array(50).fill(2))
const historyList = ref<Array<{ text: string; timestamp: number; speaker?: string }>>([])
const currentSpeaker = ref<string | null>(null)
const wsMessages = ref<Array<{ timestamp: number; data: string; parsed?: unknown; type?: string }>>([])
const expandedMessages = ref<Set<number>>(new Set())

// 麦克风权限管理
const hasMicrophonePermission = ref(false)
const isRequestingPermission = ref(false)
let audioStream: MediaStream | null = null

// WebSocket连接状态
const wsConnected = ref(false)

// 任务管理
const taskInfo = ref<{ TaskId?: string; MeetingJoinUrl?: string; TaskStatus?: string } | null>(null)
const isCreatingTask = ref(false)
const isStoppingTask = ref(false)
const createTaskParams = ref({
  audio_format: 'pcm',
  sample_rate: 16000,
  source_language: 'cn',
  task_key: '',
  enable_summary: false,
  enable_key_points: false,
  enable_translation: false,
})

// 语音识别服务（直接连接阿里云WebSocket）
let asrService: AliyunASRDirectService | null = null
const isRecording = ref(false)

// 计算属性
const statusText = computed(() => {
  const statusMap: Record<string, string> = {
    null: '未开始',
    init: '初始化中',
    ing: '录音中',
    end: '已停止',
  }
  return statusMap[status.value] || '未知'
})

const buttonText = computed(() => {
  if (status.value === 'init') return '初始化中...'
  if (status.value === 'ing') return '暂停录音'
  return '开始录音'
})

/**
 * 格式化时间
 */
const formatTime = (date: Date): string => {
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${hours}:${minutes}:${seconds}`
}

/**
 * 请求麦克风权限
 */
const requestMicrophonePermission = async () => {
  isRequestingPermission.value = true
  errorMessage.value = ''

  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
        sampleRate: 16000,
        channelCount: 1,
      },
    })

    audioStream = stream
    hasMicrophonePermission.value = true
    wsConnected.value = true

    console.log('麦克风授权成功')
  } catch (error) {
    console.error('Failed to request microphone permission:', error)
    const err = error as DOMException
    errorMessage.value = err.name === 'NotAllowedError'
      ? '无法访问麦克风，请检查浏览器权限设置'
      : err.name === 'NotFoundError'
      ? '未找到麦克风设备'
      : '无法获取麦克风权限，请检查设备连接'

    hasMicrophonePermission.value = false
    if (audioStream) {
      audioStream.getTracks().forEach(track => track.stop())
      audioStream = null
    }
  } finally {
    isRequestingPermission.value = false
  }
}

/**
 * 处理识别结果
 */
const handleRecognitionResult = (result: RecognitionResult) => {
  console.log('=== 识别结果回调 ===')
  console.log('识别文本:', result.text)
  console.log('是否最终结果:', result.isFinal)

  if (result.isFinal) {
    // 最终结果：添加到历史记录
    const finalText = result.text.trim()
    if (finalText) {
      historyList.value.push({
        text: finalText,
        timestamp: result.timestamp,
        speaker: result.speaker || undefined,
      })

      // 记录到WebSocket消息列表
      wsMessages.value.push({
        timestamp: result.timestamp,
        data: JSON.stringify(result),
        parsed: result,
        type: 'transcript_update_final',
      })

      // 滚动到底部
      setTimeout(() => {
        const container = document.querySelector('.max-h-96.overflow-y-auto')
        if (container) {
          container.scrollTop = container.scrollHeight
        }
      }, 100)

      resultText.value = finalText
      resultTextTemp.value = ''
    }
  } else {
    // 临时结果：显示实时识别文本
    resultTextTemp.value = result.text
    resultText.value = ''

    // 记录到WebSocket消息列表
    wsMessages.value.push({
      timestamp: result.timestamp,
      data: JSON.stringify(result),
      parsed: result,
      type: 'transcript_update_temp',
    })
  }

  // 限制消息数量
  if (wsMessages.value.length > 100) {
    wsMessages.value.shift()
  }
}

/**
 * 处理识别错误
 */
const handleRecognitionError = (error: Error) => {
  console.error('Recognition error:', error)
  errorMessage.value = error.message || '语音识别错误'

  // 记录错误消息
  wsMessages.value.push({
    timestamp: Date.now(),
    data: JSON.stringify({ error: error.message }),
    parsed: { error: error.message },
    type: 'error',
  })
}

/**
 * 处理音频数据（用于可视化）
 */
const handleAudioData = (data: Uint8Array) => {
  if (!isRecording.value) {
    audioBars.value = Array(50).fill(2)
    return
  }

  const barCount = audioBars.value.length
  const dataLength = data.length

  if (dataLength === 0) {
    audioBars.value = Array(50).fill(2)
    return
  }

  const step = Math.floor(dataLength / barCount)
  const newBars: number[] = []

  for (let i = 0; i < barCount; i++) {
    const index = i * step
    if (index < dataLength) {
      const value = data[index] || 0
      const percentage = Math.max(2, Math.min(100, (value / 255) * 100))
      newBars.push(percentage)
    } else {
      newBars.push(2)
    }
  }

  audioBars.value = newBars
}

/**
 * 创建实时记录任务
 */
const createTask = async () => {
  isCreatingTask.value = true
  errorMessage.value = ''

  console.log('=== 开始创建实时记录任务 ===')
  console.log('请求参数:', createTaskParams.value)

  try {
    const requestBody = JSON.stringify(createTaskParams.value)
    console.log('请求体:', requestBody)

    const response = await fetch('/api/tytingwu/create-task', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: requestBody,
    })

    console.log('收到响应:', response.status, response.statusText)

    const result = await response.json()
    console.log('响应数据:', result)

    if (result.success && result.data) {
      taskInfo.value = result.data

      // 记录创建任务消息
      wsMessages.value.push({
        timestamp: Date.now(),
        data: JSON.stringify(result.data),
        parsed: result.data,
        type: 'task_created',
      })

      console.log('=== 实时记录创建成功 ===')
      console.log('TaskId:', result.data.TaskId)
      console.log('MeetingJoinUrl:', result.data.MeetingJoinUrl)
      console.log('TaskStatus:', result.data.TaskStatus)
    } else {
      console.error('创建任务失败:', result.message)
      console.error('错误类型:', result.error_type)
      throw new Error(result.message || '创建实时记录失败')
    }
  } catch (error) {
    console.error('=== 创建实时记录任务异常 ===')
    console.error('错误类型:', error instanceof Error ? error.constructor.name : typeof error)
    console.error('错误信息:', error)
    if (error instanceof Error) {
      console.error('错误堆栈:', error.stack)
    }
    console.error('=== 异常详情结束 ===')

    const err = error instanceof Error ? error : new Error('创建实时记录失败')
    errorMessage.value = err.message
  } finally {
    isCreatingTask.value = false
  }
}

/**
 * 停止实时记录任务
 */
const stopTask = async () => {
  if (!taskInfo.value?.TaskId) {
    errorMessage.value = '没有活动的任务'
    return
  }

  isStoppingTask.value = true
  errorMessage.value = ''

  try {
    const response = await fetch('/api/tytingwu/stop-task', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        task_id: taskInfo.value.TaskId,
      }),
    })

    const result = await response.json()

    if (result.success) {
      // 记录停止任务消息
      wsMessages.value.push({
        timestamp: Date.now(),
        data: JSON.stringify(result.data),
        parsed: result.data,
        type: 'task_stopped',
      })

      console.log('实时记录已停止:', result.data)

      // 如果正在录音，也停止录音
      if (status.value === 'ing') {
        stop()
      }
    } else {
      throw new Error(result.message || '停止实时记录失败')
    }
  } catch (error) {
    console.error('Failed to stop task:', error)
    const err = error instanceof Error ? error : new Error('停止实时记录失败')
    errorMessage.value = err.message
  } finally {
    isStoppingTask.value = false
  }
}

/**
 * 重置任务
 */
const resetTask = () => {
  taskInfo.value = null
  if (status.value === 'ing') {
    stop()
  }
  errorMessage.value = ''
}

/**
 * 开始录音
 */
const start = async () => {
  if (!hasMicrophonePermission.value || !audioStream) {
    errorMessage.value = '请先授权麦克风'
    return
  }

  if (!taskInfo.value?.MeetingJoinUrl) {
    errorMessage.value = '请先创建实时记录'
    return
  }

  status.value = 'init'
  errorMessage.value = ''
  resultText.value = ''
  resultTextTemp.value = ''

  const wsUrl = taskInfo.value.MeetingJoinUrl

  try {
    // 创建新的ASR服务实例
    asrService = new AliyunASRDirectService()

    // 设置回调
    asrService.onResult(handleRecognitionResult)
    asrService.onError(handleRecognitionError)
    asrService.onAudioData(handleAudioData)

    // 开始识别（直接连接阿里云WebSocket）
    await asrService.startRecognition(wsUrl, audioStream)

    status.value = 'ing'
    isRecording.value = true
    wsConnected.value = true

    // 记录识别启动消息
    wsMessages.value.push({
      timestamp: Date.now(),
      data: JSON.stringify({ ws_url: wsUrl, message: '语音识别已启动' }),
      parsed: { ws_url: wsUrl, message: '语音识别已启动' },
      type: 'recognition_started',
    })
  } catch (error) {
    console.error('Failed to start recording:', error)
    const err = error instanceof Error ? error : new Error('无法开始录音')
    errorMessage.value = err.message || '无法开始录音，请检查设备连接'
    status.value = 'null'
    isRecording.value = false
    wsConnected.value = false
    asrService = null
  }
}

/**
 * 停止录音
 */
const stop = () => {
  if (asrService) {
    asrService.stopRecognition()
    asrService = null
  }

  status.value = 'end'
  isRecording.value = false
  wsConnected.value = false

  // 记录停止消息
  wsMessages.value.push({
    timestamp: Date.now(),
    data: JSON.stringify({ message: '语音识别已停止' }),
    parsed: { message: '语音识别已停止' },
    type: 'recognition_stopped',
  })

  // 清理临时结果
  if (resultTextTemp.value) {
    resultTextTemp.value = ''
  }

  // 重置音频可视化
  audioBars.value = Array(50).fill(2)
}

/**
 * 切换录音状态
 */
const toggleRecording = () => {
  if (status.value === 'ing') {
    stop()
  } else {
    start()
  }
}

/**
 * 清空历史记录
 */
const clearHistory = () => {
  if (confirm('确定要清空所有识别历史记录吗？')) {
    historyList.value = []
    resultText.value = ''
    resultTextTemp.value = ''
  }
}

/**
 * 格式化时间（用于历史记录）
 */
const formatTimeForHistory = (timestamp: number): string => {
  const date = new Date(timestamp)
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  const milliseconds = String(date.getMilliseconds()).padStart(3, '0')
  return `${hours}:${minutes}:${seconds}.${milliseconds}`
}

/**
 * 格式化JSON显示
 */
const formatJson = (data: string, parsed?: unknown): string => {
  if (parsed) {
    try {
      return JSON.stringify(parsed, null, 2)
    } catch (error) {
      return data
    }
  }
  return data
}

/**
 * 切换消息展开/折叠
 */
const toggleMessage = (index: number): void => {
  if (expandedMessages.value.has(index)) {
    expandedMessages.value.delete(index)
  } else {
    expandedMessages.value.add(index)
  }
}

/**
 * 获取消息卡片样式类
 */
const getMessageCardClass = (type?: string): string => {
  const baseClass = 'border-l-4'
  switch (type) {
    case 'transcript_update_final':
    case 'transcript_update_temp':
      return `${baseClass} border-blue-500`
    case 'recognition_started':
      return `${baseClass} border-green-500`
    case 'error':
      return `${baseClass} border-red-500`
    case 'task_created':
      return `${baseClass} border-purple-500`
    case 'task_stopped':
      return `${baseClass} border-orange-500`
    default:
      return `${baseClass} border-gray-300`
  }
}

/**
 * 获取消息头部样式类
 */
const getMessageHeaderClass = (type?: string): string => {
  switch (type) {
    case 'transcript_update_final':
    case 'transcript_update_temp':
      return 'bg-blue-50'
    case 'recognition_started':
      return 'bg-green-50'
    case 'error':
      return 'bg-red-50'
    case 'task_created':
      return 'bg-purple-50'
    case 'task_stopped':
      return 'bg-orange-50'
    default:
      return 'bg-gray-50'
  }
}

/**
 * 获取消息类型标签样式类
 */
const getMessageTypeBadgeClass = (type?: string): string => {
  switch (type) {
    case 'transcript_update_final':
    case 'transcript_update_temp':
      return 'bg-blue-100 text-blue-700'
    case 'recognition_started':
      return 'bg-green-100 text-green-700'
    case 'error':
      return 'bg-red-100 text-red-700'
    case 'task_created':
      return 'bg-purple-100 text-purple-700'
    case 'task_stopped':
      return 'bg-orange-100 text-orange-700'
    default:
      return 'bg-gray-100 text-gray-700'
  }
}

/**
 * 获取消息类型标签文本
 */
const getMessageTypeLabel = (type?: string): string => {
  switch (type) {
    case 'transcript_update_final':
      return '最终结果'
    case 'transcript_update_temp':
      return '临时结果'
    case 'recognition_started':
      return '识别启动'
    case 'recognition_stopped':
      return '识别停止'
    case 'task_created':
      return '任务创建'
    case 'task_stopped':
      return '任务停止'
    case 'error':
      return '错误'
    default:
      return '未知'
  }
}

/**
 * 提取识别文字
 */
const extractRecognizedText = (parsed: unknown): string | null => {
  try {
    const obj = parsed as Record<string, unknown>
    if (obj.text && typeof obj.text === 'string') {
      return obj.text
    }
  } catch (error) {
    console.error('提取识别文字失败:', error)
  }
  return null
}

/**
 * 清空WebSocket消息
 */
const clearWsMessages = (): void => {
  wsMessages.value = []
  expandedMessages.value.clear()
}

// 组件卸载时清理资源
onUnmounted(() => {
  if (status.value === 'ing') {
    stop()
  }

  if (audioStream) {
    audioStream.getTracks().forEach(track => track.stop())
    audioStream = null
  }
})
</script>

<style scoped>
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
