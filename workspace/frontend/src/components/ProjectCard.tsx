/**
 * 项目卡片组件
 */
import { Link, useNavigate } from "@tanstack/react-router"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Play, Pause, RotateCcw } from "lucide-react"
import {
  formatProjectStatus,
  getProjectStatusColor,
  formatDateTime,
  calculateProgress,
} from "@/utils/project"
import type { ProjectPublic } from "@/client"

interface ProjectCardProps {
  project: ProjectPublic
  onStart?: () => void
  onPause?: () => void
  onResume?: () => void
}

export function ProjectCard({
  project,
  onStart,
  onPause,
  onResume,
}: ProjectCardProps) {
  const navigate = useNavigate()
  const projectId = String(project.id)
  const progress = calculateProgress(project.current_stage)

  const goDetail = () => {
    navigate({ to: "/projects/$projectId", params: { projectId } })
  }

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="flex justify-between items-start">
          <Link 
            to="/projects/$projectId" 
            params={{ projectId }}
            className="text-lg font-semibold leading-none tracking-tight hover:text-primary cursor-pointer"
          >
            {project.name}
          </Link>
          <Badge className={getProjectStatusColor(project.status)}>
            {formatProjectStatus(project.status)}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* 描述 */}
          {project.description && (
            <p className="text-sm text-gray-600 line-clamp-2">{project.description}</p>
          )}

          {/* 进度条 */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">当前阶段: {project.current_stage}</span>
              <span className="text-gray-600">{progress}%</span>
            </div>
            <Progress value={progress} />
          </div>

          {/* 时间信息 */}
          <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
            <div>
              <span className="font-medium">创建时间:</span>
              <br />
              {formatDateTime(project.created_at)}
            </div>
            <div>
              <span className="font-medium">启动时间:</span>
              <br />
              {formatDateTime(project.started_at)}
            </div>
          </div>

          {/* 操作按钮 */}
          <div className="flex gap-2 pt-2">
            {project.status === "idle" && onStart && (
              <Button size="sm" onClick={(e) => { e.stopPropagation(); onStart(); }} className="flex-1">
                <Play className="h-4 w-4 mr-1" />
                启动
              </Button>
            )}
            {project.status === "running" && onPause && (
              <Button size="sm" variant="outline" onClick={(e) => { e.stopPropagation(); onPause(); }} className="flex-1">
                <Pause className="h-4 w-4 mr-1" />
                暂停
              </Button>
            )}
            {project.status === "paused" && onResume && (
              <Button size="sm" onClick={(e) => { e.stopPropagation(); onResume(); }} className="flex-1">
                <RotateCcw className="h-4 w-4 mr-1" />
                恢复
              </Button>
            )}
            <Button size="sm" variant="outline" className="flex-1" onClick={goDetail}>
              查看详情
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

