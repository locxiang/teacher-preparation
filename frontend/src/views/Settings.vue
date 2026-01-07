<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部固定栏 - 企业级设计 -->
    <div class="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
      <div class="max-w-[1600px] mx-auto px-8 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-semibold text-gray-900">
              系统设置
            </h1>
            <p class="text-sm text-gray-500 mt-1">
              管理系统用户、教师信息和API密钥配置
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="max-w-[1600px] mx-auto px-8 py-6">
      <div class="grid grid-cols-12 gap-6">
        <!-- Left Sidebar: Settings Navigation -->
        <div class="col-span-12 lg:col-span-3">
          <SettingsNavigation
            :active-tab="activeTab"
            @tab-change="activeTab = $event"
          />
        </div>

        <!-- Right Content -->
        <div class="col-span-12 lg:col-span-9">
          <!-- User Management -->
          <UserManagement v-if="activeTab === 'users'" />

          <!-- API Keys Management -->
          <ApiKeysManagement v-if="activeTab === 'api'" />

          <!-- Voiceprint Management -->
          <VoiceprintManagement v-if="activeTab === 'voiceprint'" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import SettingsNavigation from './settings/SettingsNavigation.vue'
import UserManagement from './settings/UserManagement.vue'
import ApiKeysManagement from './settings/ApiKeysManagement.vue'
import VoiceprintManagement from './settings/VoiceprintManagement.vue'

const activeTab = ref<'voiceprint' | 'users' | 'api'>('voiceprint')
</script>
