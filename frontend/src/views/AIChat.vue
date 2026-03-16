<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部固定栏 - 企业级设计 -->
    <div class="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
      <div class="max-w-[1600px] mx-auto px-8 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-semibold text-gray-900">
              AI 智能对话
            </h1>
            <p class="text-sm text-gray-500 mt-1">
              选择会议并输入聊天记录，南博士将为您提供智能回答
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="max-w-[1600px] mx-auto px-8 py-6">
      <div class="max-w-4xl mx-auto space-y-5">
        <div class="bg-white border border-gray-200 rounded shadow-sm">
          <!-- 会议选择区域 -->
          <div class="px-6 py-5 border-b border-gray-200 bg-gray-50">
            <h3 class="text-sm font-semibold text-gray-900">
              选择会议
            </h3>
          </div>
          <div class="p-6">
            <div
              v-if="isLoadingMeetings"
              class="text-center py-4"
            >
              <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-nanyu-600" />
              <p class="mt-2 text-sm text-gray-500">
                加载会议列表...
              </p>
            </div>
            <select
              v-else
              v-model="selectedMeetingId"
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-nanyu-500 focus:border-transparent outline-none transition-all"
            >
              <option value="">
                请选择会议
              </option>
              <option
                v-for="meeting in meetings"
                :key="meeting.id"
                :value="meeting.id"
              >
                {{ meeting.name }} ({{ formatDate(meeting.created_at) }})
              </option>
            </select>
            <p
              v-if="errorMessage"
              class="text-red-500 text-xs mt-2"
            >
              {{ errorMessage }}
            </p>
          </div>

          <!-- 聊天记录输入区域 -->
          <div class="px-6 py-5 border-b border-gray-200 bg-gray-50">
            <h3 class="text-sm font-semibold text-gray-900">
              聊天记录
            </h3>
          </div>
          <div class="p-6">
            <!-- 样例按钮 -->
            <div class="mb-3 flex flex-wrap gap-2">
              <button
                v-for="(sample, index) in sampleChats"
                :key="index"
                class="px-2.5 py-1 text-xs bg-nanyu-50 text-nanyu-700 border border-nanyu-200 rounded hover:bg-nanyu-100 hover:border-nanyu-300 transition-colors font-medium"
                @click="loadSample(index)"
              >
                {{ sample.label }}
              </button>
            </div>

            <textarea
              v-model="chatHistory"
              placeholder="请输入聊天记录内容..."
              class="w-full h-40 px-3 py-2 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-nanyu-500 focus:border-transparent outline-none resize-none"
            />
            <p class="text-xs text-gray-500 mt-2">
              可以粘贴会议聊天记录或其他文本内容，或点击上方样例按钮快速填充
            </p>
          </div>

          <!-- 提交按钮 -->
          <div class="px-6 py-5 border-t border-gray-200 bg-gray-50">
            <div class="flex items-center justify-between mb-3">
              <label class="flex items-center cursor-pointer">
                <input
                  v-model="enableVoice"
                  type="checkbox"
                  class="w-4 h-4 text-nanyu-600 border-gray-300 rounded focus:ring-nanyu-500"
                >
                <span class="ml-2 text-sm text-gray-700">启用语音播放</span>
              </label>
              <button
                v-if="isPlayingVoice"
                class="px-3 py-1.5 text-xs bg-red-50 text-red-700 border border-red-200 rounded hover:bg-red-100 transition-colors font-medium"
                @click="stopVoice"
              >
                🛑 停止播放
              </button>
            </div>
            <button
              :disabled="isSubmitting || (!selectedMeetingId && !chatHistory.trim())"
              class="w-full px-4 py-2 text-sm bg-nanyu-600 text-white rounded hover:bg-nanyu-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
              @click="handleSubmit"
            >
              <span
                v-if="isSubmitting"
                class="inline-flex items-center"
              >
                <span class="inline-block animate-spin mr-2">⏳</span>
                AI正在思考...
              </span>
              <span v-else>开始对话</span>
            </button>
            <p
              v-if="errorMessage"
              class="text-red-500 text-xs mt-3 text-center"
            >
              {{ errorMessage }}
            </p>
          </div>
        </div>

        <!-- AI回答区域 -->
        <div
          v-if="aiResponse || isSubmitting"
          class="bg-white border border-gray-200 rounded shadow-sm"
        >
          <div class="px-6 py-5 border-b border-gray-200 bg-gray-50">
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
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                />
              </svg>
              AI 回答
              <span
                v-if="isSubmitting"
                class="ml-2 inline-block animate-pulse text-nanyu-600 text-xs"
              >正在输入...</span>
            </h3>
          </div>
          <div class="p-6">
            <div class="prose prose-sm max-w-none prose-headings:text-gray-800 prose-p:text-gray-700 prose-strong:text-gray-900 prose-code:text-nanyu-600 prose-pre:bg-gray-100">
              <div class="bg-gray-50 p-4 rounded border border-gray-200 min-h-[100px] markdown-content">
                <div
                  v-if="aiResponse"
                  class="markdown-body"
                  v-html="renderedMarkdown"
                />
                <div
                  v-else-if="isSubmitting"
                  class="text-gray-400 italic text-sm"
                >
                  等待AI回答...
                </div>
                <!-- 打字光标效果 -->
                <span
                  v-if="isSubmitting && aiResponse"
                  class="inline-block w-2 h-4 bg-nanyu-600 ml-1 animate-pulse"
                />
              </div>
            </div>
            <div
              v-if="aiResponse && !isSubmitting"
              class="mt-4 flex justify-end space-x-2"
            >
              <button
                class="px-3 py-1.5 text-xs bg-white border border-gray-300 text-gray-700 rounded hover:bg-gray-50 transition-colors font-medium"
                @click="copyResponse"
              >
                复制内容
              </button>
              <button
                class="px-3 py-1.5 text-xs bg-white border border-gray-300 text-gray-700 rounded hover:bg-gray-50 transition-colors font-medium"
                @click="clearResponse"
              >
                清空
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { marked } from 'marked'
import { getMeetings, type Meeting, formatDate } from '@/services/meeting'
import { streamAIChat } from '@/services/ai-chat'
import { AliyunTTSService, getTTSToken } from '@/services/aliyun-tts'

const meetings = ref<Meeting[]>([])
const isLoadingMeetings = ref(false)
const selectedMeetingId = ref('')
const chatHistory = ref('')
const isSubmitting = ref(false)
const errorMessage = ref('')
const aiResponse = ref('')
const enableVoice = ref(true)
const isPlayingVoice = ref(false)

// 语音合成服务实例
let ttsService: AliyunTTSService | null = null
let pendingTextBuffer = ''  // 待合成的文本缓冲区
let synthesisTimer: ReturnType<typeof setInterval> | null = null

// 样例聊天记录
const sampleChats = ref([
  {
    label: '样例1：语文备课讨论',
    content: `时间：2025年12月1日 下午4:00
参与人员：高一语文组 王芳（组长，教龄15年）、李梅（教龄10年，擅长文本细读）、张伟（教龄8年，侧重活动设计）、刘青（教龄3年，新教师）

核心主题：人教版高一上册《背影》教学方案研讨

王芳：各位老师，今天咱们集中碰一下《背影》的备课思路。这篇是经典篇目，但越经典越容易教得浮于表面。咱们先说说各自的初步想法，重点聚焦"怎么让现在的学生读懂父亲的'背影'"这个核心问题。李老师，你先从文本角度说说？

李梅：好的王姐。我反复读了几遍，发现这篇文章的情感张力全在"细节"里。比如父亲买橘子那段，"蹒跚地走到铁道边，慢慢探身下去"，"蹒跚""探"这两个词特别有画面感。还有父亲的衣着——"黑布大马褂，深青布棉袍"，和当时家境的"惨淡"形成呼应，这些细节都是引导学生体会父爱的关键。但我有点担心，现在的学生和父辈沟通方式不一样，可能很难理解这种"不善言辞"的爱。

刘青：李老师这点我特别有感触。上次试讲片段，有学生问"为什么父亲不直接打车去车站，非要自己买橘子？"还有人说"觉得父亲有点笨拙"。这说明他们对那个年代的生活背景不了解，也没法共情这种含蓄的表达。我觉得是不是得先补充时代背景？比如朱自清写这篇文章时，家庭正遭遇变故，父子关系也曾有过隔阂。

张伟：背景补充是必要的，但光靠讲容易枯燥。我设计了两个活动，大家看看行不行。第一个是"细节品读会"，让学生分组圈画文中描写父亲动作、神态、语言的词句，然后用"我从____这个词里，看到了一个____的父亲"这样的句式分享。第二个是"古今父爱对话"，让学生结合自己的生活，说说父亲表达爱的方式和文中父亲的异同，比如有的学生父亲会默默帮他整理书包，有的会用微信发暖心消息，这样就能把文本和生活联系起来了。

王芳：张老师这个活动设计得不错，能让学生动起来。不过"古今对话"要注意引导，别变成单纯的生活分享，得拉回到文本的情感核心上。另外，我觉得可以加一个"配乐朗读"环节，选一段舒缓的音乐，让学生读父亲买橘子的段落，通过语气、语速的变化，感受文字里的情感重量。

李梅：配乐朗读这个建议好，能强化语感。还有一个点，文章结尾"在晶莹的泪光中，又看见那肥胖的、青布棉袍黑布马褂的背影"，这个"又"字很有深意，既呼应前文，又体现出作者多年后的愧疚和思念。这里可以设计一个问题："作者为什么会'又'想起父亲的背影？这个'背影'在他心中有什么变化？"引导学生理解情感的升华。

刘青：我补充一下，针对学生觉得"父亲笨拙"的问题，我准备了一张老照片——民国时期的火车站场景，还有当时的交通条件介绍，让学生直观感受"买橘子"这件事在当时有多不容易，这样他们就能理解父亲的"蹒跚"里藏着的爱了。另外，课后作业我想设计成"给父亲写一段话"，不用太长，就写一个父亲让自己感动的瞬间，把阅读收获转化为情感表达。

张伟：这个作业好，既能落实情感目标，又能锻炼表达。对了，要不要加一个拓展阅读？比如链接朱自清的《给亡妇》，或者当代作家写父爱的短文，让学生对比不同年代的父爱表达，但会不会增加学生负担？

王芳：拓展阅读可以作为选做内容，给学有余力的学生。咱们现在把思路整合一下：导入用"你的父亲有哪些让你难忘的瞬间"提问，接着补充时代背景和作者经历，核心环节是细节品读会+配乐朗读，然后通过"古今父爱对话"联系生活，最后用"解读'又'字"升华主题，作业是写一段话给父亲。这样流程就清晰了，重点突出，也贴合学生学情。`,
  },
  {
    label: '样例2：数学教学讨论',
    content: `时间：2025年12月2日 上午10:00
参与人员：高二数学组

主题：函数概念教学难点突破

张老师：函数概念是高中数学的基础，但学生理解起来有困难，大家有什么好的方法？

李老师：我觉得可以用生活中的例子，比如温度和时间的关系，让学生先有直观感受。

王老师：对，还可以用图像帮助学生理解函数的对应关系。`,
  },
  {
    label: '样例3：英语教学研讨',
    content: `时间：2025年12月3日 下午2:00
参与人员：高三英语组

主题：阅读理解能力提升策略

陈老师：学生阅读理解得分不高，主要是词汇量不够。

刘老师：我建议增加词汇教学时间，同时加强阅读技巧训练。

赵老师：可以设计一些有趣的阅读活动，提高学生的阅读兴趣。`,
  },
])

// 加载样例
const loadSample = (index: number) => {
  if (sampleChats.value[index]) {
    chatHistory.value = sampleChats.value[index].content
  }
}

// 配置 marked 选项
marked.setOptions({
  breaks: true, // 支持换行
  gfm: true, // 支持 GitHub Flavored Markdown
})

// 将 markdown 转换为 HTML
const renderedMarkdown = computed(() => {
  if (!aiResponse.value) return ''
  try {
    return marked(aiResponse.value)
  } catch (error) {
    console.error('Markdown 渲染错误:', error)
    // 如果渲染失败，返回原始文本（转义HTML）
    return aiResponse.value.replace(/</g, '&lt;').replace(/>/g, '&gt;')
  }
})

// 加载会议列表
const loadMeetings = async () => {
  isLoadingMeetings.value = true
  try {
    const data = await getMeetings()
    meetings.value = data
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '加载会议列表失败'
  } finally {
    isLoadingMeetings.value = false
  }
}

// 初始化语音合成
const initTTS = async () => {
  if (!enableVoice.value) {
    console.log('[AIChat] 语音播放已禁用，跳过初始化')
    return
  }

  // 如果已经有TTS服务正在运行，先停止之前的播放和合成，避免两段音频同时播放
  if (ttsService) {
    console.log('[AIChat] 检测到已有TTS服务，先停止之前的播放和合成')
    try {
      ttsService.stopPlayback() // 停止音频播放
      ttsService.stopSynthesis() // 停止合成
      ttsService.close() // 关闭连接
    } catch (error) {
      console.error('[AIChat] 清理旧TTS服务失败:', error)
    }
    ttsService = null
    pendingTextBuffer = '' // 清空待发送的文本缓冲区
    isPlayingVoice.value = false // 重置状态
  }

  console.log('[AIChat] 开始初始化语音合成服务')
  try {
    // 获取Token
    console.log('[AIChat] 正在获取TTS Token...')
    const { token, app_key } = await getTTSToken()
    console.log('[AIChat] ✅ Token获取成功')

    // 创建TTS服务实例
    console.log('[AIChat] 创建TTS服务实例')
    ttsService = new AliyunTTSService()

    // 开始合成
    console.log('[AIChat] 启动语音合成服务')
    await ttsService.startSynthesis(
      {
        token,
        appKey: app_key,
        voice: 'longxiaochun',  // CosyVoice大模型音色
        format: 'PCM',  // 使用大写PCM，与demo一致
        sampleRate: 24000,  // 使用24000采样率，与demo一致
        volume: 100,  // 使用100音量，与demo一致
        speechRate: 0,
        pitchRate: 0,
      },
      () => {
        // 合成完成（WebSocket已关闭，但音频可能还在播放）
        console.log('[AIChat] ✅ 语音合成完成（WebSocket已关闭，音频继续播放）')
        // 注意：不在这里设置 isPlayingVoice = false，因为音频可能还在播放
        // 音频播放完成后会自动处理
      },
      (error: Error) => {
        // 错误处理
        console.error('[AIChat] ❌ 语音合成错误:', error)
        isPlayingVoice.value = false
        errorMessage.value = `语音合成失败: ${error.message}`
      },
      () => {
        // 音频播放完成回调
        console.log('[AIChat] ✅ 音频播放完成')
        isPlayingVoice.value = false
      },
    )

    console.log('[AIChat] ✅ 语音合成服务初始化成功')
    isPlayingVoice.value = true
  } catch (error) {
    console.error('[AIChat] ❌ 初始化语音合成失败:', error)
    enableVoice.value = false
    errorMessage.value = `语音合成初始化失败: ${error instanceof Error ? error.message : '未知错误'}`
  }
}

// 发送文本进行语音合成
const synthesizeText = (text: string) => {
  if (!ttsService || !enableVoice.value) {
    console.log('[AIChat] TTS服务不可用，跳过文本合成')
    return
  }

  try {
    console.log('[AIChat] 收到文本片段，长度:', text.length, '内容:', text.substring(0, 30) + (text.length > 30 ? '...' : ''))

    // 累积文本，每积累一定长度或遇到标点符号时发送
    pendingTextBuffer += text
    console.log('[AIChat] 当前缓冲区长度:', pendingTextBuffer.length)

    // 如果遇到句号、问号、感叹号，立即发送
    if (/[。！？\n]/.test(text)) {
      console.log('[AIChat] 检测到句子结束符，开始分段发送')
      const sentences = pendingTextBuffer.split(/([。！？\n])/)
      for (let i = 0; i < sentences.length - 1; i += 2) {
        const sentence = sentences[i] + sentences[i + 1]
        if (sentence.trim()) {
          console.log('[AIChat] 发送句子:', sentence.substring(0, 50) + (sentence.length > 50 ? '...' : ''))
          ttsService.sendText(sentence.trim())
        }
      }
      pendingTextBuffer = sentences[sentences.length - 1] || ''
      console.log('[AIChat] 剩余缓冲区:', pendingTextBuffer)
    } else if (pendingTextBuffer.length >= 20) {
      // 如果缓冲区超过20个字符，也发送
      console.log('[AIChat] 缓冲区达到阈值，发送文本:', pendingTextBuffer.substring(0, 50) + (pendingTextBuffer.length > 50 ? '...' : ''))
      ttsService.sendText(pendingTextBuffer)
      pendingTextBuffer = ''
    }
  } catch (error) {
    console.error('[AIChat] ❌ 发送文本到TTS失败:', error)
  }
}

// 停止语音播放
const stopVoice = () => {
  if (ttsService) {
    ttsService.stopPlayback()
    ttsService.stopSynthesis()
    ttsService.close()
    ttsService = null
  }
  isPlayingVoice.value = false
  pendingTextBuffer = ''
}

// 提交对话请求
const handleSubmit = async () => {
  if (!selectedMeetingId.value && !chatHistory.value.trim()) {
    errorMessage.value = '请至少选择会议或输入聊天记录'
    return
  }

  isSubmitting.value = true
  errorMessage.value = ''
  aiResponse.value = ''
  pendingTextBuffer = ''

  // 如果启用语音，初始化TTS
  if (enableVoice.value) {
    await initTTS()
  }

  try {
    await streamAIChat(
      selectedMeetingId.value || undefined,
      chatHistory.value,
      (chunk: string) => {
        // 实时追加文本
        aiResponse.value += chunk

        // 如果启用语音，实时合成语音
        if (enableVoice.value && ttsService) {
          synthesizeText(chunk)
        }
      },
      () => {
        // 流结束
        isSubmitting.value = false

        // 如果启用语音，发送剩余的文本并立即发送StopSynthesis
        if (enableVoice.value && ttsService) {
          // 发送剩余的文本（如果有）
          if (pendingTextBuffer.trim()) {
            console.log('[AIChat] 发送剩余的文本:', pendingTextBuffer.trim())
            ttsService.sendText(pendingTextBuffer.trim())
            pendingTextBuffer = ''
          }

          // 立即发送StopSynthesis指令，要求服务端停止合成并合成所有缓存文本
          // 重要：需要在文本流发送结束后立刻发送此指令，否则有可能丢失文本
          console.log('[AIChat] 文本流已结束，立即发送StopSynthesis指令')
          ttsService.stopSynthesis()
          // 注意：不要在这里关闭连接，等待SynthesisCompleted事件后再关闭
        }
      },
      (error: Error) => {
        // 错误处理
        errorMessage.value = error.message || 'AI对话失败，请重试'
        isSubmitting.value = false
        stopVoice()
      },
    )
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'AI对话失败，请重试'
    isSubmitting.value = false
    stopVoice()
  }
}

// 复制回答内容
const copyResponse = async () => {
  try {
    await navigator.clipboard.writeText(aiResponse.value)
    alert('AI回答已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    alert('复制失败，请手动复制')
  }
}

// 清空回答
const clearResponse = () => {
  aiResponse.value = ''
}

onMounted(() => {
  loadMeetings()
})

onUnmounted(() => {
  // 清理资源
  stopVoice()
  if (synthesisTimer) {
    clearInterval(synthesisTimer)
  }
})
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
  margin-top: 1.5em;
  margin-bottom: 0.75em;
  color: #1f2937;
}

.markdown-content :deep(h1) {
  font-size: 1.5em;
  border-bottom: 2px solid #e5e7eb;
  padding-bottom: 0.5em;
}

.markdown-content :deep(h2) {
  font-size: 1.3em;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 0.3em;
}

.markdown-content :deep(h3) {
  font-size: 1.1em;
}

/* 段落样式 */
.markdown-content :deep(p) {
  margin-bottom: 1em;
  line-height: 1.8;
}

/* 列表样式 */
.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 1em 0;
  padding-left: 2em;
}

.markdown-content :deep(li) {
  margin: 0.5em 0;
  line-height: 1.7;
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
  background-color: #f3f4f6;
  padding: 0.2em 0.4em;
  border-radius: 0.25rem;
  font-size: 0.9em;
  color: #6b2c91;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.markdown-content :deep(pre) {
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1em;
  overflow-x: auto;
  margin: 1em 0;
}

.markdown-content :deep(pre code) {
  background-color: transparent;
  padding: 0;
  color: #374151;
}

/* 引用样式 */
.markdown-content :deep(blockquote) {
  border-left: 4px solid #6b2c91;
  padding-left: 1em;
  margin: 1em 0;
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
  border-top: 2px solid #e5e7eb;
  margin: 2em 0;
}

/* 表格样式 */
.markdown-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1em 0;
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  border: 1px solid #e5e7eb;
  padding: 0.5em 1em;
  text-align: left;
}

.markdown-content :deep(th) {
  background-color: #f9fafb;
  font-weight: 600;
}
</style>

