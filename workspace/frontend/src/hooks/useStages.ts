/**
 * 流程阶段管理相关 Hooks
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { StagesService } from "@/client"
import useCustomToast from "./useCustomToast"
import type { StageUpdate } from "@/client"

/**
 * 获取阶段详情
 */
export function useStage(stageId: number) {
  return useQuery({
    queryKey: ["stage", stageId],
    queryFn: () => StagesService.readStage({ stageId }),
    enabled: !!stageId,
  })
}

/**
 * 更新阶段
 */
export function useUpdateStage() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  return useMutation({
    mutationFn: ({ stageId, data }: { stageId: number; data: StageUpdate }) =>
      StagesService.updateStage({ stageId, requestBody: data }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["stage", variables.stageId] })
      showSuccessToast("阶段更新成功")
    },
    onError: (error: Error) => {
      showErrorToast(`更新失败: ${error.message}`)
    },
  })
}

/**
 * 审批通过阶段
 */
export function useApproveStage() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  return useMutation({
    mutationFn: (stageId: number) =>
      StagesService.approveStage({ stageId }),
    onSuccess: (_, stageId) => {
      queryClient.invalidateQueries({ queryKey: ["stage", stageId] })
      showSuccessToast("审批通过")
    },
    onError: (error: Error) => {
      showErrorToast(`审批失败: ${error.message}`)
    },
  })
}

/**
 * 审批拒绝阶段
 */
export function useRejectStage() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  return useMutation({
    mutationFn: (stageId: number) =>
      StagesService.rejectStage({ stageId }),
    onSuccess: (stage, stageId) => {
      queryClient.invalidateQueries({ queryKey: ["stage", stageId] })
      if ((stage as any)?.project_id) {
        const projectId = (stage as any).project_id
        queryClient.invalidateQueries({ queryKey: ["project", projectId] })
        queryClient.invalidateQueries({ queryKey: ["projects", projectId, "stages"] })
      }
      queryClient.invalidateQueries({ queryKey: ["projects"] })
      showSuccessToast("审批拒绝")
    },

    onError: (error: Error) => {
      showErrorToast(`操作失败: ${error.message}`)
    },
  })
}

/**
 * 获取阶段的功能模块
 */
export function useStageModules(stageId: number) {
  return useQuery({
    queryKey: ["stage", stageId, "modules"],
    queryFn: () => StagesService.readStageModules({ stageId }),
    enabled: !!stageId,
  })
}

/**
 * 获取阶段的执行日志（分页）
 */
export function useStageLogs(stageId: number, params?: { page?: number; page_size?: number }) {
  return useQuery({
    queryKey: ["stage", stageId, "logs", params],
    queryFn: () => StagesService.readStageLogs({ stageId, ...params }),
    enabled: !!stageId,
  })
}

/**
 * 获取阶段的测试报告
 */
export function useStageReports(stageId: number) {
  return useQuery({
    queryKey: ["stage", stageId, "reports"],
    queryFn: () => StagesService.readStageReports({ stageId }),
    enabled: !!stageId,
  })
}
