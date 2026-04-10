/**
 * 项目管理相关 Hooks
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { ProjectsService } from "@/client"
import useCustomToast from "./useCustomToast"
import type { ProjectCreate, ProjectUpdate } from "@/client"

/**
 * 获取项目列表
 */
export function useProjects(params?: { skip?: number; limit?: number }) {
  return useQuery({
    queryKey: ["projects", params],
    queryFn: () => ProjectsService.readProjects(params || {}),
  })
}

/**
 * 获取单个项目详情
 */
export function useProject(projectId: number) {
  return useQuery({
    queryKey: ["project", projectId],
    queryFn: () => ProjectsService.readProject({ projectId }),
    enabled: !!projectId,
  })
}

/**
 * 创建项目
 */
export function useCreateProject() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  return useMutation({
    mutationFn: (data: ProjectCreate) =>
      ProjectsService.createProject({ requestBody: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] })
      showSuccessToast("项目创建成功")
    },
    onError: (error: Error) => {
      showErrorToast(`创建失败: ${error.message}`)
    },
  })
}

/**
 * 更新项目
 */
export function useUpdateProject() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  return useMutation({
    mutationFn: ({ projectId, data }: { projectId: number; data: ProjectUpdate }) =>
      ProjectsService.updateProject({ projectId, requestBody: data }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["projects"] })
      queryClient.invalidateQueries({ queryKey: ["project", variables.projectId] })
      showSuccessToast("项目更新成功")
    },
    onError: (error: Error) => {
      showErrorToast(`更新失败: ${error.message}`)
    },
  })
}

/**
 * 删除项目
 */
export function useDeleteProject() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  return useMutation({
    mutationFn: (projectId: number) =>
      ProjectsService.deleteProject({ projectId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] })
      showSuccessToast("项目删除成功")
    },
    onError: (error: Error) => {
      showErrorToast(`删除失败: ${error.message}`)
    },
  })
}

/**
 * 启动项目
 */
export function useStartProject() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  return useMutation({
    mutationFn: (projectId: number) =>
      ProjectsService.startProject({ projectId }),
    onSuccess: (_, projectId) => {
      queryClient.invalidateQueries({ queryKey: ["projects"] })
      queryClient.invalidateQueries({ queryKey: ["project", projectId] })
      queryClient.invalidateQueries({ queryKey: ["projects", projectId, "stages"] })
      showSuccessToast("项目已启动")
    },

    onError: (error: Error) => {
      showErrorToast(`启动失败: ${error.message}`)
    },
  })
}

/**
 * 暂停项目
 */
export function usePauseProject() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  return useMutation({
    mutationFn: (projectId: number) =>
      ProjectsService.pauseProject({ projectId }),
    onSuccess: (_, projectId) => {
      queryClient.invalidateQueries({ queryKey: ["projects"] })
      queryClient.invalidateQueries({ queryKey: ["project", projectId] })
      queryClient.invalidateQueries({ queryKey: ["projects", projectId, "stages"] })
      showSuccessToast("项目已暂停")
    },

    onError: (error: Error) => {
      showErrorToast(`暂停失败: ${error.message}`)
    },
  })
}

/**
 * 恢复项目
 */
export function useResumeProject() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  return useMutation({
    mutationFn: (projectId: number) =>
      ProjectsService.resumeProject({ projectId }),
    onSuccess: (_, projectId) => {
      queryClient.invalidateQueries({ queryKey: ["projects"] })
      queryClient.invalidateQueries({ queryKey: ["project", projectId] })
      queryClient.invalidateQueries({ queryKey: ["projects", projectId, "stages"] })
      showSuccessToast("项目已恢复")
    },

    onError: (error: Error) => {
      showErrorToast(`恢复失败: ${error.message}`)
    },
  })
}

/**
 * 获取项目的流程阶段
 */
export function useProjectStages(projectId: number) {
  return useQuery({
    queryKey: ["projects", projectId, "stages"],
    queryFn: () => ProjectsService.readProjectStages({ projectId }),
    enabled: !!projectId,
  })
}
