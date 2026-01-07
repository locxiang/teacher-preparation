<template>
  <div class="bg-white border border-gray-200 rounded shadow-sm">
    <div class="px-6 py-5 border-b border-gray-200 bg-gray-50">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div class="flex items-center">
          <svg
            class="w-5 h-5 mr-2 text-gray-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
            />
          </svg>
          <div>
            <h3 class="text-sm font-semibold text-gray-900">
              教师列表
            </h3>
            <p class="text-xs text-gray-500 mt-0.5">
              共 {{ teachers.length }} 位教师
            </p>
          </div>
        </div>
        <div class="relative">
          <input
            type="text"
            placeholder="搜索教师..."
            class="pl-8 pr-3 py-1.5 text-sm bg-white border border-gray-300 rounded focus:ring-2 focus:ring-nanyu-500 focus:border-transparent outline-none w-full sm:w-64 transition-all"
          >
          <svg
            class="absolute left-2.5 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400"
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
        </div>
      </div>
    </div>

    <div
      v-if="teachers.length === 0"
      class="p-12 text-center"
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
          d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
        />
      </svg>
      <p class="text-sm text-gray-500 font-medium">
        暂无教师
      </p>
      <p class="text-xs text-gray-400 mt-1">
        请在上方添加新教师
      </p>
    </div>

    <div
      v-else
      class="divide-y divide-gray-200"
    >
      <div
        v-for="teacher in teachers"
        :key="teacher.id"
        class="p-4 hover:bg-gray-50 transition-colors"
      >
        <div class="flex items-start justify-between">
          <div class="flex items-start space-x-3 flex-1 min-w-0">
            <!-- Avatar -->
            <div
              class="shrink-0 w-10 h-10 rounded flex items-center justify-center text-sm font-bold"
              :class="teacher.has_voiceprint
                ? 'bg-nanyu-600 text-white'
                : 'bg-gray-200 text-gray-500'"
            >
              {{ teacher.name[0] }}
            </div>

            <!-- Info -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1.5">
                <h4 class="text-sm font-semibold text-gray-900">
                  {{ teacher.name }}
                </h4>
                <span class="px-2 py-0.5 bg-gray-100 text-gray-700 text-xs rounded font-medium">
                  {{ teacher.subject }}
                </span>
              </div>

              <!-- Status and IDs -->
              <div class="space-y-1">
                <div class="flex items-center gap-2 flex-wrap">
                  <span
                    v-if="teacher.has_voiceprint"
                    class="inline-flex items-center px-2 py-0.5 bg-green-50 text-green-700 rounded text-xs font-medium"
                  >
                    <span class="w-1.5 h-1.5 bg-green-500 rounded-full mr-1" />
                    已注册声纹
                  </span>
                  <span
                    v-else
                    class="inline-flex items-center px-2 py-0.5 bg-gray-100 text-gray-500 rounded text-xs font-medium"
                  >
                    <span class="w-1.5 h-1.5 bg-gray-400 rounded-full mr-1" />
                    未注册
                  </span>
                </div>

                <div class="flex flex-col gap-0.5 text-xs text-gray-500">
                  <div>
                    <span class="font-medium">教师ID:</span>
                    <span class="ml-1 font-mono text-gray-700">{{ teacher.id }}</span>
                  </div>
                  <div v-if="teacher.feature_id">
                    <span class="font-medium">特征ID:</span>
                    <span class="ml-1 font-mono text-blue-600 break-all">{{ teacher.feature_id }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-2 ml-4 shrink-0">
            <button
              class="px-3 py-1.5 text-xs rounded transition-colors font-medium"
              :class="teacher.has_voiceprint
                ? 'bg-white text-nanyu-600 border border-nanyu-200 hover:border-nanyu-400 hover:bg-nanyu-50'
                : 'bg-nanyu-600 text-white hover:bg-nanyu-700'"
              @click="$emit('record', teacher)"
            >
              {{ teacher.has_voiceprint ? '更新声纹' : '注册声纹' }}
            </button>
            <button
              class="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors rounded"
              title="删除教师"
              @click="$emit('delete', teacher.id)"
            >
              <svg
                class="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Teacher } from '../../services/teacher'

defineProps<{
  teachers: Teacher[]
}>()

defineEmits<{
  record: [teacher: Teacher]
  delete: [teacherId: number]
}>()
</script>

