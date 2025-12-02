<template>
  <div class="bg-white border border-gray-200 rounded shadow-sm p-4 flex-grow flex flex-col min-h-0">
    <h3 class="text-xs font-semibold text-gray-900 mb-3 shrink-0 flex items-center">
      <svg class="w-4 h-4 mr-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      参考资料
    </h3>
    <div class="overflow-y-auto flex-grow space-y-1">
      <div class="flex items-center text-xs text-gray-600 hover:bg-gray-50 p-1.5 rounded cursor-pointer transition-colors">
        <span class="text-red-500 mr-1.5">📄</span>
        <span class="truncate">教学大纲.pdf</span>
      </div>
      <div class="flex items-center text-xs text-gray-600 hover:bg-gray-50 p-1.5 rounded cursor-pointer transition-colors">
        <span class="text-blue-500 mr-1.5">📝</span>
        <span class="truncate">教案模板.docx</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 参考资料组件，目前使用静态数据，后续可以扩展为动态数据
</script>

