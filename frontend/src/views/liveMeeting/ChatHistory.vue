<template>
  <div class="bg-white border border-gray-200 rounded shadow-sm flex flex-col overflow-hidden grow min-h-0">
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
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
          />
        </svg>
        对话记录
      </h3>
      <div class="flex space-x-2">
        <!-- 停止 AI 播放按钮 -->
        <button
          v-if="isAISpeaking"
          class="px-3 py-1.5 text-xs rounded border transition-colors flex items-center bg-red-50 text-red-700 hover:bg-red-100 border-red-200"
          title="停止 AI 声音播放"
          @click="emit('stop-ai-voice')"
        >
          <svg
            class="w-4 h-4 mr-1"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9V8h2v8zm4 0h-2V8h2v8z" />
          </svg>
          停止播放
        </button>
        <!-- 触发 AI 按钮 -->
        <button
          :disabled="!isRecording || isAIGenerating || isAISpeaking"
          class="px-3 py-1.5 text-xs rounded border transition-colors flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
          :class="isRecording && !isAIGenerating && !isAISpeaking
            ? 'bg-purple-50 text-purple-700 hover:bg-purple-100 border-purple-200'
            : 'bg-gray-50 text-gray-400 border-gray-200'"
          title="手动触发 AI 回答"
          @click="emit('trigger-ai')"
        >
          <svg
            class="w-4 h-4 mr-1"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M13 10V3L4 14h7v7l9-11h-7z"
            />
          </svg>
          {{ isAIGenerating ? '生成中...' : isAISpeaking ? 'AI 说话中' : '触发 AI' }}
        </button>
      </div>
    </div>

    <div
      ref="messagesContainer"
      class="grow overflow-y-auto p-4 space-y-4 scroll-smooth"
    >
      <!-- Messages (倒序显示，最新的在上面) -->
      <div
        v-for="message in reversedMessages"
        :key="message.id"
        class="flex space-x-3"
      >
        <div
          class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold border shrink-0"
          :class="message.type === 'ai'
            ? 'bg-nanyu-600 text-white border-nanyu-600'
            : message.speaker === '张老师'
              ? 'bg-blue-100 text-blue-600 border-blue-200'
              : message.speaker === '李老师'
                ? 'bg-pink-100 text-pink-600 border-pink-200'
                : 'bg-gray-100 text-gray-600 border-gray-200'"
        >
          {{ message.type === 'ai' ? '🤖' : message.speaker[0] }}
        </div>
        <div class="flex-1">
          <div class="flex items-center mb-1">
            <span
              class="text-sm font-semibold mr-2"
              :class="message.type === 'ai' ? 'text-nanyu-700' : 'text-gray-800'"
            >
              {{ message.speaker }}
            </span>
            <span
              v-if="message.relativeTime !== undefined"
              class="text-xs text-gray-500 mr-1"
            >
              {{ formatRelativeTime(message.relativeTime) }}
            </span>
            <span class="text-xs text-gray-400">{{ formatTime(message.timestamp) }}</span>
            <span
              v-if="message.stageIndex !== currentStageIndex"
              class="ml-2 text-xs bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded"
            >
              {{ stages[message.stageIndex]?.name }}
            </span>
          </div>
          <div
            class="rounded rounded-tl-none border p-3 text-sm"
            :class="[
              message.type === 'ai'
                ? 'bg-nanyu-50 border-nanyu-100 text-gray-800'
                : message.isFinal === false
                  ? 'bg-gray-100 border-gray-200 text-gray-500 italic'
                  : 'bg-white border-gray-200 text-gray-700'
            ]"
          >
            <!-- AI 消息使用 markdown 渲染 -->
            <!-- eslint-disable vue/no-v-html -->
            <div
              v-if="message.type === 'ai'"
              class="prose prose-sm max-w-none prose-headings:text-gray-800 prose-p:text-gray-700 prose-strong:text-gray-900 prose-code:text-nanyu-600 prose-pre:bg-gray-100 markdown-content"
              v-html="renderMarkdown(message.content)"
            />
            <!-- eslint-enable vue/no-v-html -->
            <!-- 人类消息使用普通文本 -->
            <template v-else>
              {{ message.content }}
              <span
                v-if="message.isFinal === false"
                class="ml-2 text-xs text-gray-400"
              >(识别中...)</span>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, nextTick } from 'vue'
import { marked } from 'marked'
import type { MarkedOptions } from 'marked'
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-expect-error - katex 类型定义路径问题，但实际可用
import katex from 'katex'
import 'katex/dist/katex.min.css'

interface Stage {
  id: string
  name: string
  description: string
}

interface Message {
  id: string
  type: 'human' | 'ai'
  speaker: string
  content: string
  timestamp: number // 绝对时间戳（真实时间）
  relativeTime?: number // 相对时间（从录音开始的毫秒数）
  stageIndex: number
  isFinal?: boolean
}

interface Props {
  messages: Message[]
  stages: Stage[]
  currentStageIndex: number
  isRecording?: boolean
  isAIGenerating?: boolean
  isAISpeaking?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isRecording: false,
  isAIGenerating: false,
  isAISpeaking: false,
})

const emit = defineEmits<{
  'trigger-ai': []
  'stop-ai-voice': []
}>()

const messagesContainer = ref<HTMLElement | null>(null)

// 倒序显示消息（最新的在上面）
const reversedMessages = computed(() => {
  return [...props.messages].reverse()
})

// 当有新消息时，滚动到顶部（因为倒序显示，最新的在上面）
watch(() => props.messages.length, () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = 0
    }
  })
})

// 格式化绝对时间（真实时间）
const formatTime = (timestamp: number): string => {
  const date = new Date(timestamp)
  if (isNaN(date.getTime())) {
    return '00:00:00'
  }
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}:${date.getSeconds().toString().padStart(2, '0')}`
}

// 格式化相对时间（从录音开始的时长）
const formatRelativeTime = (milliseconds: number): string => {
  const totalSeconds = Math.floor(milliseconds / 1000)
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = totalSeconds % 60

  if (hours > 0) {
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  } else {
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }
}

// 配置 marked 选项
marked.setOptions({
  breaks: true, // 支持换行
  gfm: true, // 支持 GitHub Flavored Markdown
} as MarkedOptions)

// 将 markdown 转换为 HTML，并渲染数学公式
const renderMarkdown = (content: string): string => {
  if (!content) return ''
  try {
    // 先使用 marked 渲染 markdown（marked 可能返回 Promise，需要处理）
    const markedResult = marked(content)
    // 如果返回的是 Promise，需要等待（但通常同步版本返回字符串）
    let html: string
    if (typeof markedResult === 'string') {
      html = markedResult
    } else {
      // 如果是 Promise，同步等待（实际使用中 marked 默认是同步的）
      html = markedResult as unknown as string
    }

    // 使用临时标记避免冲突：先将块级公式替换为临时标记
    const blockPlaceholders: string[] = []
    html = html.replace(/\$\$([\s\S]*?)\$\$/g, (_match: string, formula: string) => {
      const placeholder = `__KATEX_BLOCK_${blockPlaceholders.length}__`
      blockPlaceholders.push(formula.trim())
      return placeholder
    })

    // 渲染行内公式 $...$（避免匹配块级公式）
    html = html.replace(/\$([^$\n]+?)\$/g, (match: string, formula: string) => {
      try {
        return katex.renderToString(formula.trim(), {
          displayMode: false,
          throwOnError: false,
        })
      } catch (error) {
        console.error('KaTeX 渲染错误（行内）:', error)
        return match
      }
    })

    // 恢复并渲染块级公式
    blockPlaceholders.forEach((formula, index) => {
      const placeholder = `__KATEX_BLOCK_${index}__`
      try {
        const rendered = katex.renderToString(formula, {
          displayMode: true,
          throwOnError: false,
        })
        html = html.replace(placeholder, rendered)
      } catch (error) {
        console.error('KaTeX 渲染错误（块级）:', error)
        html = html.replace(placeholder, `$$${formula}$$`)
      }
    })

    return html
  } catch (error) {
    console.error('Markdown 渲染错误:', error)
    // 如果渲染失败，返回原始文本（转义HTML）
    return content.replace(/</g, '&lt;').replace(/>/g, '&gt;')
  }
}
</script>

<style scoped>
/* Markdown 内容样式 */
.markdown-content :deep(.markdown-body) {
  line-height: 1.7;
}

/* 标题样式 */
.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3),
.markdown-content :deep(h4),
.markdown-content :deep(h5),
.markdown-content :deep(h6) {
  font-weight: 600;
  margin-top: 1em;
  margin-bottom: 0.5em;
  color: #1f2937;
}

.markdown-content :deep(h1) {
  font-size: 1.4em;
  border-bottom: 2px solid #e5e7eb;
  padding-bottom: 0.3em;
}

.markdown-content :deep(h2) {
  font-size: 1.2em;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 0.2em;
}

.markdown-content :deep(h3) {
  font-size: 1.1em;
}

/* 段落样式 */
.markdown-content :deep(p) {
  margin-bottom: 0.75em;
  line-height: 1.7;
}

/* 列表样式 */
.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 0.75em 0;
  padding-left: 1.5em;
}

.markdown-content :deep(li) {
  margin: 0.25em 0;
  line-height: 1.6;
}

/* 强调样式 */
.markdown-content :deep(strong) {
  font-weight: 600;
  color: #374151;
}

.markdown-content :deep(em) {
  font-style: italic;
}

/* 代码样式 */
.markdown-content :deep(code) {
  background-color: rgba(107, 44, 145, 0.1);
  padding: 0.15em 0.3em;
  border-radius: 0.25rem;
  font-size: 0.9em;
  color: #6b2c91;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.markdown-content :deep(pre) {
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  padding: 0.75em;
  overflow-x: auto;
  margin: 0.75em 0;
}

.markdown-content :deep(pre code) {
  background-color: transparent;
  padding: 0;
  color: #374151;
}

/* 引用样式 */
.markdown-content :deep(blockquote) {
  border-left: 3px solid #6b2c91;
  padding-left: 0.75em;
  margin: 0.75em 0;
  color: #6b7280;
  font-style: italic;
}

/* 链接样式 */
.markdown-content :deep(a) {
  color: #6b2c91;
  text-decoration: underline;
  transition: color 0.2s;
}

.markdown-content :deep(a:hover) {
  color: #562374;
}

/* 分隔线 */
.markdown-content :deep(hr) {
  border: none;
  border-top: 1px solid #e5e7eb;
  margin: 1em 0;
}

/* 表格样式 */
.markdown-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 0.75em 0;
  font-size: 0.9em;
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  border: 1px solid #e5e7eb;
  padding: 0.4em 0.6em;
  text-align: left;
}

.markdown-content :deep(th) {
  background-color: #f9fafb;
  font-weight: 600;
}

/* KaTeX 数学公式样式 */
.markdown-content :deep(.katex) {
  font-size: 1.1em;
}

.markdown-content :deep(.katex-display) {
  margin: 1em 0;
  overflow-x: auto;
  overflow-y: hidden;
}

.markdown-content :deep(.katex-display > .katex) {
  display: inline-block;
  text-align: left;
  padding: 0.5em 0;
}

/* 行内公式样式 */
.markdown-content :deep(.katex:not(.katex-display)) {
  font-size: 1em;
  vertical-align: baseline;
}
</style>

