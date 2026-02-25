<template>
  <div class="related-materials bg-white border border-gray-200 rounded shadow-sm flex flex-col overflow-hidden shrink-0 w-[280px] min-h-0">
    <div class="px-4 py-3 border-b border-gray-200 bg-gray-50 shrink-0">
      <div class="flex justify-between items-center mb-2">
        <h3 class="text-sm font-semibold text-gray-900 flex items-center">
          <svg
            class="w-4 h-4 mr-2 text-nanyu-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          相关资料
        </h3>
      </div>
      <!-- 手动搜索按钮（始终显示） -->
      <button
        type="button"
        class="w-full px-3 py-2 text-sm bg-nanyu-600 text-white rounded hover:bg-nanyu-700 transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        :disabled="isLoading"
        @click="handleManualSearch"
      >
        <svg
          class="w-4 h-4"
          :class="{ 'animate-spin': isLoading }"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
        {{ isLoading ? '搜索中...' : '搜索资料' }}
      </button>
    </div>

    <div class="flex-1 overflow-y-auto p-3 space-y-4 min-h-0">
      <!-- 错误 -->
      <div
        v-if="errorMessage"
        class="text-sm text-red-500 text-center py-4"
      >
        {{ errorMessage }}
        <button
          type="button"
          class="mt-2 text-nanyu-600 hover:underline"
          @click="handleManualSearch"
        >
          重试
        </button>
      </div>

      <!-- 空状态 -->
      <div
        v-else-if="searchHistory.length === 0"
        class="text-sm text-gray-400 text-center py-6"
      >
        点击上方「搜索资料」按钮，根据当前对话内容搜索相关资料
      </div>

      <!-- 本次会议搜索历史（按时间倒序，最新的在上） -->
      <div
        v-else
        class="space-y-4"
      >
        <section
          v-for="(record, recordIdx) in searchHistory"
          :key="recordIdx"
          class="border border-gray-100 rounded-lg overflow-hidden"
        >
          <!-- AI 分析后的搜索关键词 -->
          <div class="px-3 py-2 bg-gray-50 border-b border-gray-100 flex items-center justify-between">
            <span class="text-xs text-gray-500">分析关键词：</span>
            <span class="text-sm font-medium text-nanyu-700 truncate flex-1 mx-1" :title="record.keyword">
              {{ record.keyword || '（未分析）' }}
            </span>
            <span class="text-xs text-gray-400 shrink-0">{{ formatTime(record.timestamp) }}</span>
          </div>

          <!-- 按标签分门别类展示 -->
          <div
            v-if="record.data.length > 0"
            class="p-2 space-y-3"
          >
            <div
              v-for="(group, tag) in groupByTag(record.data)"
              :key="tag"
              class="space-y-1.5"
            >
              <div class="flex items-center gap-1.5">
                <span
                  class="inline-block px-2 py-0.5 text-xs rounded-full shrink-0"
                  :class="getTagClass(tag)"
                >
                  {{ tag }}
                </span>
              </div>
              <a
                v-for="(item, idx) in group"
                :key="idx"
                :href="item.url"
                target="_blank"
                rel="noopener noreferrer"
                class="block p-2 rounded border border-gray-100 hover:border-nanyu-200 hover:bg-nanyu-50/50 transition-colors group"
              >
                <div class="text-xs font-medium text-gray-900 group-hover:text-nanyu-700 line-clamp-2">
                  {{ item.title }}
                </div>
                <div class="text-xs text-gray-500 line-clamp-1 mt-0.5">
                  {{ item.snippet }}
                </div>
              </a>
            </div>
          </div>

          <div
            v-else
            class="p-3 text-xs text-gray-400 text-center"
          >
            暂无相关资料
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { searchRelatedMaterials, type RelatedMaterial } from '@/services/related-materials'

interface Message {
  id: string
  type: 'human' | 'ai'
  speaker: string
  content: string
  isFinal?: boolean
}

interface SearchRecord {
  keyword: string
  timestamp: number
  data: RelatedMaterial[]
}

interface Props {
  messages: Message[]
}

const props = defineProps<Props>()

const searchHistory = ref<SearchRecord[]>([])
const isLoading = ref(false)
const errorMessage = ref('')
const lastSearchTime = ref(0)
const MIN_SEARCH_INTERVAL = 30000 // 自动触发：30 秒内不重复搜索
const DEBOUNCE_DELAY = 4000 // 新消息后 4 秒再触发搜索

let debounceTimer: ReturnType<typeof setTimeout> | null = null

// 标签颜色映射
const TAG_COLORS: Record<string, string> = {
  教学策略: 'bg-blue-100 text-blue-700',
  课程标准: 'bg-amber-100 text-amber-700',
  案例分享: 'bg-green-100 text-green-700',
  学科知识: 'bg-purple-100 text-purple-700',
  教学资源: 'bg-cyan-100 text-cyan-700',
  教学设计: 'bg-indigo-100 text-indigo-700',
  课堂活动: 'bg-pink-100 text-pink-700',
  评价方法: 'bg-orange-100 text-orange-700',
  教材解读: 'bg-teal-100 text-teal-700',
  备课参考: 'bg-nanyu-100 text-nanyu-700',
}

const getTagClass = (tag: string): string => {
  return TAG_COLORS[tag] || 'bg-gray-100 text-gray-600'
}

// 按标签分组（取每条资料的主标签）
const groupByTag = (items: RelatedMaterial[]): Record<string, RelatedMaterial[]> => {
  const map: Record<string, RelatedMaterial[]> = {}
  for (const item of items) {
    const tag = item.tags?.[0] || '相关资料'
    if (!map[tag]) map[tag] = []
    map[tag].push(item)
  }
  return map
}

const formatTime = (ts: number): string => {
  const d = new Date(ts)
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

const doSearch = async (force = false) => {
  const finalMessages = props.messages.filter((m) => m.isFinal !== false && m.content?.trim())

  // 手动触发时，无对话内容也允许调用（后端会返回空）
  if (!force && finalMessages.length === 0) {
    return
  }

  const now = Date.now()
  if (!force && now - lastSearchTime.value < MIN_SEARCH_INTERVAL) {
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    const msgs = finalMessages.length > 0
      ? finalMessages.slice(-10).map((m) => ({
          role: (m.type === 'ai' ? 'assistant' : 'user') as 'user' | 'assistant',
          content: `${m.speaker || '未知'}: ${m.content}`,
        }))
      : [{ role: 'user' as const, content: '会议主题' }]

    const result = await searchRelatedMaterials(msgs)

    // 追加到本次会议搜索历史（最新的在最前）
    searchHistory.value = [
      {
        keyword: result.keyword,
        timestamp: Date.now(),
        data: result.data,
      },
      ...searchHistory.value,
    ]

    lastSearchTime.value = Date.now()
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : '搜索失败'
  } finally {
    isLoading.value = false
  }
}

// 手动触发搜索（不受 30 秒限制）
const handleManualSearch = () => {
  const hasContent = props.messages.some((m) => m.isFinal !== false && m.content?.trim())
  if (!hasContent) {
    errorMessage.value = '请先进行对话，再搜索相关资料'
    return
  }
  doSearch(true)
}

// 自动触发：监听消息变化
watch(
  () => props.messages.length,
  () => {
    const hasNewFinal = props.messages.some((m) => m.isFinal !== false && m.content?.trim())
    if (!hasNewFinal) return

    if (debounceTimer) clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => {
      debounceTimer = null
      doSearch(false)
    }, DEBOUNCE_DELAY)
  },
  { flush: 'post' },
)

watch(
  () => {
    const last = props.messages[props.messages.length - 1]
    return last ? `${last.id}-${last.isFinal}-${last.content?.slice(0, 50)}` : ''
  },
  () => {
    const hasNewFinal = props.messages.some((m) => m.isFinal !== false && m.content?.trim())
    if (!hasNewFinal) return

    if (debounceTimer) clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => {
      debounceTimer = null
      doSearch(false)
    }, DEBOUNCE_DELAY)
  },
  { flush: 'post' },
)

onMounted(() => {
  const hasFinal = props.messages.some((m) => m.isFinal !== false && m.content?.trim())
  if (hasFinal) {
    debounceTimer = setTimeout(() => {
      debounceTimer = null
      doSearch(false)
    }, DEBOUNCE_DELAY)
  }
})
</script>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
