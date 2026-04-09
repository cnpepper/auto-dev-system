/**
 * 项目相关工具函数
 */

/**
 * 格式化项目状态
 */
export const formatProjectStatus = (status: string): string => {
  const statusMap: Record<string, string> = {
    idle: "空闲",
    running: "运行中",
    completed: "已完成",
    failed: "失败",
    paused: "已暂停",
  }
  return statusMap[status] || status
}

/**
 * 获取项目状态的样式类
 */
export const getProjectStatusColor = (status: string): string => {
  const colorMap: Record<string, string> = {
    idle: "bg-gray-100 text-gray-800",
    running: "bg-blue-100 text-blue-800",
    completed: "bg-green-100 text-green-800",
    failed: "bg-red-100 text-red-800",
    paused: "bg-yellow-100 text-yellow-800",
  }
  return colorMap[status] || "bg-gray-100 text-gray-800"
}

/**
 * 格式化流程阶段类型
 */
export const formatStageType = (stageType: string): string => {
  const typeMap: Record<string, string> = {
    development: "开发阶段",
    testing: "测试阶段",
    design: "设计阶段",
    review: "评审阶段",
  }
  return typeMap[stageType] || stageType
}

/**
 * 格式化阶段状态
 */
export const formatStageStatus = (status: string): string => {
  const statusMap: Record<string, string> = {
    pending: "待开始",
    in_progress: "进行中",
    completed: "已完成",
    failed: "失败",
    pending_review: "待审核",
    approved: "已通过",
    rejected: "已拒绝",
  }
  return statusMap[status] || status
}

/**
 * 获取阶段状态的样式类
 */
export const getStageStatusColor = (status: string): string => {
  const colorMap: Record<string, string> = {
    pending: "bg-gray-100 text-gray-800",
    in_progress: "bg-blue-100 text-blue-800",
    completed: "bg-green-100 text-green-800",
    failed: "bg-red-100 text-red-800",
    pending_review: "bg-yellow-100 text-yellow-800",
    approved: "bg-green-100 text-green-800",
    rejected: "bg-red-100 text-red-800",
  }
  return colorMap[status] || "bg-gray-100 text-gray-800"
}

/**
 * 格式化日志级别
 */
export const formatLogLevel = (level: string): string => {
  const levelMap: Record<string, string> = {
    info: "信息",
    warning: "警告",
    error: "错误",
    debug: "调试",
  }
  return levelMap[level] || level
}

/**
 * 获取日志级别的样式类
 */
export const getLogLevelColor = (level: string): string => {
  const colorMap: Record<string, string> = {
    info: "text-blue-600",
    warning: "text-yellow-600",
    error: "text-red-600",
    debug: "text-gray-600",
  }
  return colorMap[level] || "text-gray-600"
}

/**
 * 格式化日期时间
 */
export const formatDateTime = (dateString: string | null | undefined): string => {
  if (!dateString) return "-"
  const date = new Date(dateString)
  return date.toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  })
}

/**
 * 格式化持续时间（秒）
 */
export const formatDuration = (seconds: number): string => {
  if (seconds < 60) return `${seconds}秒`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}分钟`
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return `${hours}小时${minutes}分钟`
}

/**
 * 计算项目进度百分比
 */
export const calculateProgress = (currentStage: string): number => {
  const stages = ["idle", "development", "testing", "completed"]
  const index = stages.indexOf(currentStage)
  if (index === -1) return 0
  return Math.round((index / (stages.length - 1)) * 100)
}
