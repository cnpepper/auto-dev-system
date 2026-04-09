/**
 * 项目详情页面
 */
import { createFileRoute } from "@tanstack/react-router"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Play, Pause, RotateCcw, Check, X } from "lucide-react"
import { useProject, useProjectStages, useStartProject, usePauseProject, useResumeProject } from "@/hooks/useProjects"
import { useStageLogs, useApproveStage, useRejectStage } from "@/hooks/useStages"
import {
  formatProjectStatus,
  getProjectStatusColor,
  formatStageType,
  formatStageStatus,
  getStageStatusColor,
  formatLogLevel,
  getLogLevelColor,
  formatDateTime,
  calculateProgress,
} from "@/utils/project"

export const Route = createFileRoute("/_layout/projects/$projectId")({
  component: ProjectDetailPage,
})

function ProjectDetailPage() {
  const { projectId } = Route.useParams()
  const projectIdNum = parseInt(projectId)
  
  const { data: project, isLoading: projectLoading } = useProject(projectIdNum)
  const { data: stagesData } = useProjectStages(projectIdNum)
  const startMutation = useStartProject()
  const pauseMutation = usePauseProject()
  const resumeMutation = useResumeProject()
  const approveMutation = useApproveStage()
  const rejectMutation = useRejectStage()

  const stages = stagesData?.data || []

  if (projectLoading || !project) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">加载中...</div>
      </div>
    )
  }

  const progress = calculateProgress(project.current_stage)

  return (
    <div className="space-y-6">
      {/* 项目头部信息 */}
      <div className="flex justify-between items-start">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold">{project.name}</h1>
            <Badge className={getProjectStatusColor(project.status)}>
              {formatProjectStatus(project.status)}
            </Badge>
          </div>
          {project.description && (
            <p className="text-gray-600 mt-2">{project.description}</p>
          )}
        </div>
        
        {/* 操作按钮 */}
        <div className="flex gap-2">
          {project.status === "idle" && (
            <Button onClick={() => startMutation.mutate(projectIdNum)}>
              <Play className="h-4 w-4 mr-2" />
              启动项目
            </Button>
          )}
          {project.status === "running" && (
            <Button variant="outline" onClick={() => pauseMutation.mutate(projectIdNum)}>
              <Pause className="h-4 w-4 mr-2" />
              暂停项目
            </Button>
          )}
          {project.status === "paused" && (
            <Button onClick={() => resumeMutation.mutate(projectIdNum)}>
              <RotateCcw className="h-4 w-4 mr-2" />
              恢复项目
            </Button>
          )}
        </div>
      </div>

      {/* 项目概览卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">当前进度</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>{project.current_stage}</span>
                <span>{progress}%</span>
              </div>
              <Progress value={progress} />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">创建时间</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-semibold">{formatDateTime(project.created_at)}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">项目路径</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm font-mono truncate">{project.project_path}</p>
          </CardContent>
        </Card>
      </div>

      {/* 详情标签页 */}
      <Tabs defaultValue="stages" className="w-full">
        <TabsList>
          <TabsTrigger value="stages">流程阶段</TabsTrigger>
          <TabsTrigger value="logs">执行日志</TabsTrigger>
          <TabsTrigger value="reports">测试报告</TabsTrigger>
        </TabsList>

        {/* 流程阶段 */}
        <TabsContent value="stages" className="space-y-4">
          {stages.length === 0 ? (
            <div className="text-center py-8 border-2 border-dashed border-gray-300 rounded-lg">
              <p className="text-gray-600">暂无流程阶段</p>
            </div>
          ) : (
            <div className="space-y-4">
              {stages.map((stage) => (
                <StageCard
                  key={stage.id}
                  stage={stage}
                  onApprove={() => approveMutation.mutate(stage.id)}
                  onReject={() => rejectMutation.mutate(stage.id)}
                />
              ))}
            </div>
          )}
        </TabsContent>

        {/* 执行日志 */}
        <TabsContent value="logs">
          <Card>
            <CardHeader>
              <CardTitle>执行日志</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-600">
                请选择具体的流程阶段查看日志
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 测试报告 */}
        <TabsContent value="reports">
          <Card>
            <CardHeader>
              <CardTitle>测试报告</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-600">
                请选择具体的流程阶段查看测试报告
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

/**
 * 流程阶段卡片
 */
function StageCard({ stage, onApprove, onReject }: {
  stage: any
  onApprove: () => void
  onReject: () => void
}) {
  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-lg">{formatStageType(stage.stage_type)}</CardTitle>
            <p className="text-sm text-gray-600 mt-1">{stage.stage_name}</p>
          </div>
          <Badge className={getStageStatusColor(stage.status)}>
            {formatStageStatus(stage.status)}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* 时间信息 */}
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <span className="font-medium">开始时间:</span>
              <br />
              {formatDateTime(stage.started_at)}
            </div>
            <div>
              <span className="font-medium">完成时间:</span>
              <br />
              {formatDateTime(stage.completed_at)}
            </div>
            <div>
              <span className="font-medium">创建时间:</span>
              <br />
              {formatDateTime(stage.created_at)}
            </div>
          </div>

          {/* 审批按钮 */}
          {stage.status === "pending_review" && (
            <div className="flex gap-2 pt-2">
              <Button size="sm" onClick={onApprove}>
                <Check className="h-4 w-4 mr-1" />
                审批通过
              </Button>
              <Button size="sm" variant="destructive" onClick={onReject}>
                <X className="h-4 w-4 mr-1" />
                审批拒绝
              </Button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

export default ProjectDetailPage
