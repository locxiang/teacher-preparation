<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部固定栏 - 企业级设计 -->
    <div class="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
      <div class="max-w-[1600px] mx-auto px-8 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <router-link
              to="/"
              class="text-gray-500 hover:text-gray-700 transition-colors"
            >
              <svg
                class="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M10 19l-7-7m0 0l7-7m-7 7h18"
                />
              </svg>
            </router-link>
            <div>
              <h1 class="text-2xl font-semibold text-gray-900">
                创建新会议
              </h1>
              <p class="text-sm text-gray-500 mt-1">
                请填写会议基本信息，以便南博士更好地辅助备课
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="max-w-[1600px] mx-auto px-8 py-6">
      <div class="max-w-3xl mx-auto">
        <!-- Steps -->
        <div class="mb-6 flex items-center justify-center space-x-4 text-sm font-medium">
          <div class="flex items-center text-nanyu-600">
            <div class="w-6 h-6 rounded-full bg-nanyu-600 text-white flex items-center justify-center text-xs mr-2">
              1
            </div>
            填写基本信息
          </div>
          <div class="w-12 h-0.5 bg-gray-200" />
          <div class="flex items-center text-gray-400">
            <div class="w-6 h-6 rounded-full border-2 border-gray-300 flex items-center justify-center text-xs mr-2">
              2
            </div>
            上传资料
          </div>
          <div class="w-12 h-0.5 bg-gray-200" />
          <div class="flex items-center text-gray-400">
            <div class="w-6 h-6 rounded-full border-2 border-gray-300 flex items-center justify-center text-xs mr-2">
              3
            </div>
            完成
          </div>
        </div>

        <div class="bg-white border border-gray-200 rounded shadow-sm">
          <div class="px-6 py-5 border-b border-gray-200 bg-gray-50">
            <h2 class="text-sm font-semibold text-gray-900">
              基本信息
            </h2>
          </div>
          <form
            class="p-6 space-y-5"
            @submit.prevent="handleSubmit"
          >
            <!-- Title -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">会议标题 <span class="text-red-500">*</span></label>
              <input
                v-model="meetingName"
                type="text"
                required
                placeholder="请输入会议标题（如：三年级数学教案讨论）"
                class="w-full px-3 py-2 text-sm rounded border border-gray-300 focus:ring-2 focus:ring-nanyu-500 focus:border-transparent outline-none transition-all"
              >
            </div>

            <!-- Subject & Grade -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">学科</label>
                <select
                  v-model="subject"
                  class="w-full px-3 py-2 text-sm rounded border border-gray-300 focus:ring-2 focus:ring-nanyu-500 focus:border-transparent outline-none transition-all bg-white"
                >
                  <option value="">
                    选择学科
                  </option>
                  <option>语文</option>
                  <option>数学</option>
                  <option>英语</option>
                  <option>思想政治</option>
                  <option>历史</option>
                  <option>地理</option>
                  <option>物理</option>
                  <option>化学</option>
                  <option>生物</option>
                  <option>音乐</option>
                  <option>美术</option>
                  <option>体育</option>
                  <option>道德与法治</option>
                  <option>信息科技</option>
                  <option>信息技术</option>
                  <option>通用技术</option>
                  <option>心理健康</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">年级</label>
                <select
                  v-model="grade"
                  class="w-full px-3 py-2 text-sm rounded border border-gray-300 focus:ring-2 focus:ring-nanyu-500 focus:border-transparent outline-none transition-all bg-white"
                >
                  <option value="">
                    选择年级
                  </option>
                  <option>初一年级</option>
                  <option>初二年级</option>
                  <option>初三年级</option>
                  <option>高一年级</option>
                  <option>高二年级</option>
                  <option>高三年级</option>
                </select>
              </div>
            </div>

            <!-- Lesson Type -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">备课类型</label>
              <select
                v-model="lessonType"
                class="w-full px-3 py-2 text-sm rounded border border-gray-300 focus:ring-2 focus:ring-nanyu-500 focus:border-transparent outline-none transition-all bg-white"
              >
                <option value="">
                  选择备课类型
                </option>
                <option>新课</option>
                <option>复习</option>
                <option>专题</option>
                <option>练习课</option>
                <option>实验课</option>
                <option>其他</option>
              </select>
            </div>

            <!-- Topic -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">教学主题</label>
              <textarea
                v-model="topic"
                rows="3"
                placeholder="请输入本次备课的教学主题和主要内容（可选）"
                class="w-full px-3 py-2 text-sm rounded border border-gray-300 focus:ring-2 focus:ring-nanyu-500 focus:border-transparent outline-none transition-all"
              />
            </div>

            <!-- Participants -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1.5">参与教师 <span class="text-red-500">*</span></label>
              <div class="flex flex-wrap gap-2 p-3 border border-gray-200 rounded bg-gray-50 min-h-[50px]">
                <!-- Selected Teachers -->
                <span
                  v-for="teacher in selectedTeachers"
                  :key="teacher.id"
                  class="bg-white border text-gray-700 px-2.5 py-1 rounded text-xs flex items-center"
                  :class="hostTeacherId === teacher.id ? 'border-nanyu-500 bg-nanyu-50' : 'border-gray-200'"
                >
                  <span
                    v-if="hostTeacherId === teacher.id"
                    class="mr-1 text-nanyu-600"
                  >👑</span>
                  {{ teacher.name }} ({{ teacher.subject }})
                  <span
                    v-if="hostTeacherId === teacher.id"
                    class="ml-1 text-xs text-nanyu-600"
                  >主持人</span>
                  <button
                    type="button"
                    class="ml-1.5 text-gray-400 hover:text-red-500 transition-colors"
                    @click.stop="removeTeacher(teacher.id)"
                  >
                    &times;
                  </button>
                </span>

                <!-- Add Teacher Button -->
                <button
                  type="button"
                  class="text-nanyu-600 hover:text-nanyu-700 text-xs font-medium px-2 py-1 flex items-center transition-colors"
                  @click="openTeacherSelector"
                >
                  + 添加教师
                </button>

                <!-- Empty State -->
                <div
                  v-if="selectedTeachers.length === 0"
                  class="text-gray-400 text-xs flex items-center"
                >
                  请选择参与教师
                </div>
              </div>

              <!-- Host Selection -->
              <div
                v-if="selectedTeachers.length > 0"
                class="mt-3"
              >
                <label class="block text-sm font-medium text-gray-700 mb-1.5">选择主持人 <span class="text-red-500">*</span></label>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="teacher in selectedTeachers"
                    :key="teacher.id"
                    type="button"
                    class="px-3 py-1.5 rounded text-xs font-medium transition-all"
                    :class="hostTeacherId === teacher.id
                      ? 'bg-nanyu-600 text-white'
                      : 'bg-white border border-gray-300 text-gray-700 hover:border-nanyu-300 hover:text-nanyu-600'"
                    @click="hostTeacherId = teacher.id"
                  >
                    <span
                      v-if="hostTeacherId === teacher.id"
                      class="mr-1"
                    >👑</span>
                    {{ teacher.name }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Teacher Selector Modal -->
            <div
              v-if="showTeacherSelector"
              class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 backdrop-blur-sm p-4"
              @click.self="showTeacherSelector = false"
            >
              <div class="bg-white border border-gray-200 rounded shadow-lg w-full max-w-md max-h-[80vh] overflow-hidden flex flex-col">
                <!-- Header -->
                <div class="px-5 py-3 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
                  <h3 class="text-sm font-semibold text-gray-900">
                    选择教师
                  </h3>
                  <button
                    class="text-gray-400 hover:text-gray-600"
                    @click="showTeacherSelector = false"
                  >
                    <svg
                      class="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  </button>
                </div>

                <!-- Teacher List -->
                <div class="flex-1 overflow-y-auto p-4">
                  <!-- Loading -->
                  <div
                    v-if="isLoadingTeachers"
                    class="text-center py-8"
                  >
                    <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-nanyu-600" />
                    <p class="mt-4 text-sm text-gray-600">
                      加载中...
                    </p>
                  </div>

                  <!-- Error -->
                  <div
                    v-else-if="teacherError"
                    class="text-red-600 text-xs text-center py-4"
                  >
                    {{ teacherError }}
                  </div>

                  <!-- Empty -->
                  <div
                    v-else-if="availableTeachers.length === 0"
                    class="text-center py-8 text-gray-500"
                  >
                    <p class="text-sm">
                      还没有添加教师
                    </p>
                    <router-link
                      to="/settings"
                      class="text-nanyu-600 hover:text-nanyu-700 mt-2 inline-block text-xs"
                      @click="showTeacherSelector = false"
                    >
                      前往设置页面添加教师
                    </router-link>
                  </div>

                  <!-- Teacher List -->
                  <div
                    v-else
                    class="space-y-2"
                  >
                    <div
                      v-for="teacher in availableTeachers"
                      :key="teacher.id"
                      class="p-3 rounded border cursor-pointer transition-all"
                      :class="isTeacherSelected(teacher.id)
                        ? 'border-nanyu-500 bg-nanyu-50'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'"
                      @click="toggleTeacher(teacher)"
                    >
                      <div class="flex items-center justify-between">
                        <div>
                          <div class="text-sm font-medium text-gray-800">
                            {{ teacher.name }}
                          </div>
                          <div class="text-xs text-gray-500 mt-0.5">
                            {{ teacher.subject }}
                          </div>
                        </div>
                        <div class="flex items-center space-x-2">
                          <span
                            v-if="teacher.has_voiceprint"
                            class="text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded"
                          >
                            有声纹
                          </span>
                          <span
                            v-else
                            class="text-xs px-2 py-0.5 bg-gray-100 text-gray-500 rounded"
                          >
                            无声纹
                          </span>
                          <span
                            v-if="isTeacherSelected(teacher.id)"
                            class="text-nanyu-600 text-base"
                          >
                            ✓
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Footer -->
                <div class="px-5 py-3 border-t border-gray-200 bg-gray-50 flex justify-end space-x-2">
                  <button
                    class="px-3 py-1.5 text-xs text-gray-600 hover:bg-gray-100 rounded transition-colors"
                    @click="showTeacherSelector = false"
                  >
                    取消
                  </button>
                  <button
                    class="px-3 py-1.5 text-xs bg-nanyu-600 text-white rounded hover:bg-nanyu-700 transition-colors"
                    @click="confirmSelection"
                  >
                    确定
                  </button>
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="px-6 py-4 border-t border-gray-200 bg-gray-50 flex justify-end space-x-3">
              <router-link
                to="/"
                class="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded transition-colors font-medium"
              >
                取消
              </router-link>
              <button
                type="submit"
                class="px-4 py-2 text-sm bg-nanyu-600 text-white rounded hover:bg-nanyu-700 transition-colors font-medium"
              >
                下一步：上传资料
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getTeachers, type Teacher } from '@/services/teacher'
import { createMeeting } from '@/services/meeting'

const router = useRouter()

// 表单数据
const meetingName = ref('')
const subject = ref('')
const grade = ref('')
const topic = ref('')
const lessonType = ref('')
const selectedTeachers = ref<Teacher[]>([])
const hostTeacherId = ref<number | null>(null)

// 教师选择器
const showTeacherSelector = ref(false)
const availableTeachers = ref<Teacher[]>([])
const tempSelectedTeacherIds = ref<number[]>([])
const isLoadingTeachers = ref(false)
const teacherError = ref('')

// 检查教师是否已选择
const isTeacherSelected = (teacherId: number): boolean => {
  return tempSelectedTeacherIds.value.includes(teacherId)
}

// 切换教师选择状态
const toggleTeacher = (teacher: Teacher) => {
  const index = tempSelectedTeacherIds.value.indexOf(teacher.id)
  if (index > -1) {
    tempSelectedTeacherIds.value.splice(index, 1)
  } else {
    tempSelectedTeacherIds.value.push(teacher.id)
  }
}

// 确认选择
const confirmSelection = () => {
  selectedTeachers.value = availableTeachers.value.filter(teacher =>
    tempSelectedTeacherIds.value.includes(teacher.id),
  )
  showTeacherSelector.value = false
}

// 移除教师
const removeTeacher = (teacherId: number) => {
  selectedTeachers.value = selectedTeachers.value.filter(t => t.id !== teacherId)
  // 如果移除的是主持人，清空主持人选择
  if (hostTeacherId.value === teacherId) {
    hostTeacherId.value = null
  }
}

// 加载教师列表
const loadTeachers = async () => {
  isLoadingTeachers.value = true
  teacherError.value = ''

  try {
    const teachers = await getTeachers()
    availableTeachers.value = teachers

    // 初始化临时选择（已选择的教师）
    tempSelectedTeacherIds.value = selectedTeachers.value.map(t => t.id)
  } catch (error) {
    teacherError.value = error instanceof Error ? error.message : '获取教师列表失败'
  } finally {
    isLoadingTeachers.value = false
  }
}

// 打开教师选择器时加载教师列表
const openTeacherSelector = async () => {
  showTeacherSelector.value = true
  if (availableTeachers.value.length === 0) {
    await loadTeachers()
  } else {
    // 更新临时选择状态
    tempSelectedTeacherIds.value = selectedTeachers.value.map(t => t.id)
  }
}

// 提交表单
const handleSubmit = async (e: Event) => {
  e.preventDefault()

  if (!meetingName.value) {
    alert('请输入会议标题')
    return
  }

  if (selectedTeachers.value.length === 0) {
    alert('请至少选择一位参与教师')
    return
  }

  if (!hostTeacherId.value) {
    alert('请选择主持人')
    return
  }

  try {
    // 保存表单数据到 sessionStorage，不创建会议
    const teacherIds = selectedTeachers.value.map(t => t.id)
    const formData = {
      name: meetingName.value,
      description: topic.value,
      subject: subject.value,
      grade: grade.value,
      lesson_type: lessonType.value,
      teacherIds: teacherIds,
      hostTeacherId: hostTeacherId.value,
      teachers: selectedTeachers.value,
    }
    sessionStorage.setItem('meetingFormData', JSON.stringify(formData))
    // 跳转到上传资料页面（不需要 meetingId）
    router.push('/meeting/upload')
  } catch (error) {
    alert(error instanceof Error ? error.message : '保存表单数据失败')
  }
}

onMounted(async () => {
  // 从 sessionStorage 恢复表单数据（如果存在）
  const savedFormData = sessionStorage.getItem('meetingFormData')
  if (savedFormData) {
    try {
      const formData = JSON.parse(savedFormData)
      
      // 回显基本信息
      if (formData.name) meetingName.value = formData.name
      if (formData.subject) subject.value = formData.subject
      if (formData.grade) grade.value = formData.grade
      if (formData.lesson_type) lessonType.value = formData.lesson_type
      if (formData.description) topic.value = formData.description
    } catch (error) {
      console.error('恢复表单数据失败:', error)
      // 如果解析失败，清除无效数据
      sessionStorage.removeItem('meetingFormData')
    }
  }
  
  // 加载教师列表（在恢复基本信息之后）
  await loadTeachers()
  
  // 在教师列表加载完成后，恢复教师选择
  if (savedFormData) {
    try {
      const formData = JSON.parse(savedFormData)
      
      // 回显教师选择（需要等待教师列表加载完成）
      if (formData.teachers && Array.isArray(formData.teachers) && formData.teachers.length > 0) {
        // 根据教师ID从可用教师列表中匹配
        const teacherIds = formData.teachers.map((t: Teacher) => t.id)
        selectedTeachers.value = availableTeachers.value.filter(teacher => 
          teacherIds.includes(teacher.id),
        )
        
        // 如果匹配到的教师数量与保存的不一致，使用保存的教师数据（可能包含完整信息）
        if (selectedTeachers.value.length !== formData.teachers.length) {
          selectedTeachers.value = formData.teachers
        }
      }
      
      // 回显主持人选择
      if (formData.hostTeacherId) {
        // 确保主持人ID在已选择的教师中
        if (selectedTeachers.value.some(t => t.id === formData.hostTeacherId)) {
          hostTeacherId.value = formData.hostTeacherId
        }
      }
    } catch (error) {
      console.error('恢复教师选择失败:', error)
    }
  }
})
</script>

