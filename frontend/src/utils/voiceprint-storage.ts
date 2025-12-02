// 声纹信息接口
export interface VoiceprintInfo {
  feature_id: string
  teacher_id: string
  teacher_name: string
  subject: string
  created_at: number
  updated_at: number
  sid?: string // 请求会话ID
  code?: string // 返回码
  desc?: string // 描述信息
}

// 教师信息接口
export interface TeacherInfo {
  id: string
  name: string
  subject: string
  feature_id?: string
  hasVoiceprint: boolean
}

const STORAGE_KEY = 'teacher-prep-ai:voiceprints'
const TEACHERS_STORAGE_KEY = 'teacher-prep-ai:teachers'

/**
 * 声纹存储服务
 */
export class VoiceprintStorage {
  /**
   * 保存声纹信息
   */
  static saveVoiceprint(voiceprint: VoiceprintInfo): void {
    const voiceprints = this.getAllVoiceprints()
    const existingIndex = voiceprints.findIndex(v => v.feature_id === voiceprint.feature_id)

    if (existingIndex >= 0) {
      // 更新现有声纹
      voiceprints[existingIndex] = {
        ...voiceprint,
        updated_at: Date.now(),
      }
    } else {
      // 添加新声纹
      voiceprints.push(voiceprint)
    }

    localStorage.setItem(STORAGE_KEY, JSON.stringify(voiceprints))
  }

  /**
   * 获取所有声纹信息
   */
  static getAllVoiceprints(): VoiceprintInfo[] {
    const data = localStorage.getItem(STORAGE_KEY)
    if (!data) return []
    try {
      return JSON.parse(data)
    } catch {
      return []
    }
  }

  /**
   * 根据教师ID获取声纹信息
   */
  static getVoiceprintByTeacherId(teacherId: string): VoiceprintInfo | null {
    const voiceprints = this.getAllVoiceprints()
    return voiceprints.find(v => v.teacher_id === teacherId) || null
  }

  /**
   * 根据feature_id获取声纹信息
   */
  static getVoiceprintByFeatureId(featureId: string): VoiceprintInfo | null {
    const voiceprints = this.getAllVoiceprints()
    return voiceprints.find(v => v.feature_id === featureId) || null
  }

  /**
   * 删除声纹信息
   */
  static deleteVoiceprint(featureId: string): void {
    const voiceprints = this.getAllVoiceprints()
    const filtered = voiceprints.filter(v => v.feature_id !== featureId)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered))
  }

  /**
   * 保存教师列表
   */
  static saveTeachers(teachers: TeacherInfo[]): void {
    localStorage.setItem(TEACHERS_STORAGE_KEY, JSON.stringify(teachers))
  }

  /**
   * 获取教师列表
   */
  static getTeachers(): TeacherInfo[] {
    const data = localStorage.getItem(TEACHERS_STORAGE_KEY)
    if (!data) return []
    try {
      return JSON.parse(data)
    } catch {
      return []
    }
  }

  /**
   * 添加教师
   */
  static addTeacher(teacher: TeacherInfo): void {
    const teachers = this.getTeachers()
    teachers.push(teacher)
    this.saveTeachers(teachers)
  }

  /**
   * 更新教师信息
   */
  static updateTeacher(teacherId: string, updates: Partial<TeacherInfo>): void {
    const teachers = this.getTeachers()
    const index = teachers.findIndex(t => t.id === teacherId)
    if (index >= 0) {
      teachers[index] = { ...teachers[index], ...updates }
      this.saveTeachers(teachers)
    }
  }

  /**
   * 删除教师
   */
  static deleteTeacher(teacherId: string): void {
    const teachers = this.getTeachers()
    const filtered = teachers.filter(t => t.id !== teacherId)
    this.saveTeachers(filtered)

    // 同时删除关联的声纹信息
    const voiceprint = this.getVoiceprintByTeacherId(teacherId)
    if (voiceprint) {
      this.deleteVoiceprint(voiceprint.feature_id)
    }
  }

  /**
   * 同步教师列表的声纹状态
   */
  static syncTeachersVoiceprintStatus(): TeacherInfo[] {
    const teachers = this.getTeachers()
    const voiceprints = this.getAllVoiceprints()

    return teachers.map(teacher => {
      const voiceprint = voiceprints.find(v => v.teacher_id === teacher.id)
      return {
        ...teacher,
        feature_id: voiceprint?.feature_id,
        hasVoiceprint: !!voiceprint,
      }
    })
  }
}

