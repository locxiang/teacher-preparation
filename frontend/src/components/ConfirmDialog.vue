<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="visible"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40"
        @click.self="handleCancel"
      >
        <Transition name="scale">
          <div
            v-if="visible"
            class="bg-white rounded shadow-lg max-w-md w-full mx-4 overflow-hidden border border-gray-200"
          >
            <!-- Header -->
            <div class="bg-red-600 px-5 py-3 border-b border-red-700">
              <div class="flex items-center">
                <svg class="w-5 h-5 text-white mr-3 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <div>
                  <h3 class="text-base font-semibold text-white">{{ title }}</h3>
                  <p class="text-red-100 text-xs mt-0.5">{{ subtitle }}</p>
                </div>
              </div>
            </div>

            <!-- Content -->
            <div class="px-5 py-4">
              <p class="text-sm text-gray-900 leading-relaxed mb-3">{{ message }}</p>
              <div v-if="details" class="p-3 bg-gray-50 rounded border border-gray-200">
                <p class="text-xs text-gray-600 leading-relaxed">{{ details }}</p>
              </div>
            </div>

            <!-- Actions -->
            <div class="px-5 py-3 bg-gray-50 flex justify-end space-x-2 border-t border-gray-200">
              <button
                @click="handleCancel"
                :disabled="loading"
                class="px-4 py-1.5 text-sm text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50 font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                取消
              </button>
              <button
                @click="handleConfirm"
                :disabled="loading"
                class="px-4 py-1.5 text-sm text-white bg-red-600 rounded hover:bg-red-700 font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                <span v-if="loading" class="inline-block animate-spin mr-2 w-3 h-3 border-2 border-white border-t-transparent rounded-full"></span>
                {{ confirmText }}
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Props {
  visible: boolean
  title?: string
  subtitle?: string
  message: string
  details?: string
  confirmText?: string
  cancelText?: string
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: '确认删除',
  subtitle: '此操作不可恢复',
  confirmText: '确认删除',
  cancelText: '取消',
  loading: false,
})

const emit = defineEmits<{
  confirm: []
  cancel: []
  'update:visible': [value: boolean]
}>()

const handleConfirm = () => {
  if (!props.loading) {
    emit('confirm')
  }
}

const handleCancel = () => {
  if (!props.loading) {
    emit('cancel')
    emit('update:visible', false)
  }
}

// 监听 ESC 键
watch(() => props.visible, (newVal) => {
  if (newVal) {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && !props.loading) {
        handleCancel()
      }
    }
    window.addEventListener('keydown', handleEsc)
    return () => {
      window.removeEventListener('keydown', handleEsc)
    }
  }
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.scale-enter-active,
.scale-leave-active {
  transition: all 0.3s ease;
}

.scale-enter-from,
.scale-leave-to {
  opacity: 0;
  transform: scale(0.9);
}
</style>

