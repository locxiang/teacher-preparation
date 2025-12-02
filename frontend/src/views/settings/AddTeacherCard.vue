<template>
  <div class="bg-white border border-gray-200 rounded shadow-sm">
    <div class="px-6 py-5 border-b border-gray-200 bg-gray-50">
      <h3 class="text-sm font-semibold text-gray-900 flex items-center">
        <svg class="w-4 h-4 mr-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        添加新教师
      </h3>
    </div>
    <div class="p-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="md:col-span-1">
          <label class="block text-sm font-medium text-gray-700 mb-1.5">教师姓名</label>
          <input
            type="text"
            :value="name"
            @input="$emit('update:name', ($event.target as HTMLInputElement).value)"
            placeholder="请输入姓名"
            class="w-full px-3 py-2 text-sm rounded border border-gray-300 focus:ring-2 focus:ring-nanyu-500 focus:border-transparent outline-none transition-all"
          />
        </div>
        <div class="md:col-span-1">
          <label class="block text-sm font-medium text-gray-700 mb-1.5">学科</label>
          <select
            :value="subject"
            @change="$emit('update:subject', ($event.target as HTMLSelectElement).value)"
            class="w-full px-3 py-2 text-sm rounded border border-gray-300 focus:ring-2 focus:ring-nanyu-500 focus:border-transparent outline-none transition-all bg-white"
          >
            <option value="">选择学科</option>
            <option>语文</option>
            <option>数学</option>
            <option>英语</option>
            <option>物理</option>
            <option>化学</option>
            <option>生物</option>
            <option>历史</option>
            <option>地理</option>
            <option>政治</option>
          </select>
        </div>
        <div class="md:col-span-1 flex items-end">
          <button
            @click="$emit('add')"
            class="w-full px-4 py-2 text-sm bg-gray-800 text-white rounded hover:bg-gray-700 transition-colors font-medium flex items-center justify-center"
          >
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            添加教师
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  name: string
  subject: string
}>()

defineEmits<{
  'update:name': [value: string]
  'update:subject': [value: string]
  add: []
}>()
</script>

