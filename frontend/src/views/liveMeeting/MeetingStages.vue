<template>
  <div class="bg-white border border-gray-200 rounded shadow-sm mb-4 px-5 py-3">
    <div class="flex items-center">
      <div
        v-for="(stage, index) in stages"
        :key="stage.id"
        class="flex items-center"
      >
        <!-- Connector Line -->
        <div
          v-if="index > 0"
          class="flex-1 h-0.5 mx-2 rounded transition-colors duration-500"
          :class="currentStageIndex >= index ? 'bg-nanyu-500' : 'bg-gray-200'"
        />
        <!-- Stage Node -->
        <div class="flex items-center relative group px-2 py-1 rounded">
          <div
            class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-300 border mr-2"
            :class="[
              currentStageIndex > index ? 'bg-nanyu-100 text-nanyu-700 border-nanyu-500' :
              'bg-gray-100 text-gray-400 border-gray-300'
            ]"
          >
            <span v-if="currentStageIndex > index">✓</span>
            <span v-else-if="currentStageIndex === index">{{ index + 1 }}</span>
            <span v-else>{{ index + 1 }}</span>
          </div>
          <span class="text-xs font-medium transition-colors duration-300 whitespace-nowrap text-gray-500">
            {{ stage.name }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Stage {
  id: string
  name: string
  description: string
}

interface Props {
  stages: Stage[]
  currentStageIndex: number
}

defineProps<Props>()
</script>

