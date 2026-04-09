/**
 * 配置管理相关 Hooks
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { ConfigsService } from "@/client"
import useCustomToast from "./useCustomToast"
import type { SystemConfigCreate, SystemConfigUpdate, ToolConfigCreate, ToolConfigUpdate } from "@/client"

/**
 * 获取所有系统配置
 */
export function useSystemConfigs() {
  return useQuery({
    queryKey: ["configs", "system"],
    queryFn: () => ConfigsService.readSystemConfigs(),
  })
}

/**
 * 获取单个系统配置
 */
export function useSystemConfig(configKey: string) {
  return useQuery({
    queryKey: ["configs", "system", configKey],
    queryFn: () => ConfigsService.readSystemConfig({ configKey }),
    enabled: !!configKey,
  })
}

/**
 * 创建系统配置
 */
export function useCreateSystemConfig() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  return useMutation({
    mutationFn: (data: SystemConfigCreate) =>
      ConfigsService.createSystemConfig({ requestBody: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["configs", "system"] })
      showSuccessToast("系统配置创建成功")
    },
    onError: (error: Error) => {
      showErrorToast(`创建失败: ${error.message}`)
    },
  })
}

/**
 * 更新系统配置
 */
export function useUpdateSystemConfig() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  return useMutation({
    mutationFn: ({ configId, data }: { configId: number; data: SystemConfigUpdate }) =>
      ConfigsService.updateSystemConfig({ configId, requestBody: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["configs", "system"] })
      showSuccessToast("系统配置更新成功")
    },
    onError: (error: Error) => {
      showErrorToast(`更新失败: ${error.message}`)
    },
  })
}

/**
 * 获取所有工具配置
 */
export function useToolConfigs() {
  return useQuery({
    queryKey: ["configs", "tools"],
    queryFn: () => ConfigsService.readToolConfigs(),
  })
}

/**
 * 获取单个工具配置
 */
export function useToolConfig(toolId: number) {
  return useQuery({
    queryKey: ["configs", "tools", toolId],
    queryFn: () => ConfigsService.readToolConfig({ toolId }),
    enabled: !!toolId,
  })
}

/**
 * 创建工具配置
 */
export function useCreateToolConfig() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  return useMutation({
    mutationFn: (data: ToolConfigCreate) =>
      ConfigsService.createToolConfig({ requestBody: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["configs", "tools"] })
      showSuccessToast("工具配置创建成功")
    },
    onError: (error: Error) => {
      showErrorToast(`创建失败: ${error.message}`)
    },
  })
}

/**
 * 更新工具配置
 */
export function useUpdateToolConfig() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  return useMutation({
    mutationFn: ({ toolId, data }: { toolId: number; data: ToolConfigUpdate }) =>
      ConfigsService.updateToolConfig({ toolId, requestBody: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["configs", "tools"] })
      showSuccessToast("工具配置更新成功")
    },
    onError: (error: Error) => {
      showErrorToast(`更新失败: ${error.message}`)
    },
  })
}

/**
 * 激活工具
 */
export function useActivateTool() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  return useMutation({
    mutationFn: (toolId: number) =>
      ConfigsService.activateTool({ toolId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["configs", "tools"] })
      showSuccessToast("工具已激活")
    },
    onError: (error: Error) => {
      showErrorToast(`激活失败: ${error.message}`)
    },
  })
}

/**
 * 停用工具
 */
export function useDeactivateTool() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  return useMutation({
    mutationFn: (toolId: number) =>
      ConfigsService.deactivateTool({ toolId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["configs", "tools"] })
      showSuccessToast("工具已停用")
    },
    onError: (error: Error) => {
      showErrorToast(`停用失败: ${error.message}`)
    },
  })
}
