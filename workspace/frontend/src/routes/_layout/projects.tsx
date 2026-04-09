/**
 * 项目列表页面
 */
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"
import { Plus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { ProjectCard } from "@/components/ProjectCard"
import {
  useProjects,
  useCreateProject,
  useStartProject,
  usePauseProject,
  useResumeProject,
  useDeleteProject,
} from "@/hooks/useProjects"
import { useNavigate } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/projects")({
  component: ProjectsPage,
})

function ProjectsPage() {
  const navigate = useNavigate()
  const { data: projectsData, isLoading } = useProjects()
  const createMutation = useCreateProject()
  const startMutation = useStartProject()
  const pauseMutation = usePauseProject()
  const resumeMutation = useResumeProject()
  const deleteMutation = useDeleteProject()

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [projectName, setProjectName] = useState("")
  const [projectDescription, setProjectDescription] = useState("")
  const [requirements, setRequirements] = useState("")
  const [techStack, setTechStack] = useState("")
  const [inputDocumentDir, setInputDocumentDir] = useState("./input_docs")
  const [projectPath, setProjectPath] = useState("./projects")

  const handleCreateProject = () => {
    if (!projectName.trim()) return

    createMutation.mutate(
      {
        name: projectName,
        description: projectDescription || undefined,
        requirements: requirements || "# 项目需求\n\n请填写项目需求...",
        tech_stack: techStack || "# 技术栈\n\n- FastAPI\n- React\n- PostgreSQL",
        input_document_dir: inputDocumentDir || "./input_docs",
        project_path: projectPath || "./projects",
      },
      {
        onSuccess: () => {
          setIsCreateDialogOpen(false)
          setProjectName("")
          setProjectDescription("")
          setRequirements("")
          setTechStack("")
          setInputDocumentDir("./input_docs")
          setProjectPath("./projects")
        },
      }
    )
  }

  const handleViewProject = (projectId: number) => {
    navigate({ to: '/projects/$projectId', params: { projectId: String(projectId) } })
  }

  const handleStartProject = (projectId: number) => {
    startMutation.mutate(projectId)
  }

  const handlePauseProject = (projectId: number) => {
    pauseMutation.mutate(projectId)
  }

  const handleResumeProject = (projectId: number) => {
    resumeMutation.mutate(projectId)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">加载中...</div>
      </div>
    )
  }

  const projects = projectsData?.data || []

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">项目管理</h1>
          <p className="text-gray-600 mt-1">管理所有自动化AI编程项目</p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              创建项目
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>创建新项目</DialogTitle>
              <DialogDescription>
                创建一个新的AI自动化编程项目
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              {/* 基础信息 */}
              <div>
                <Label htmlFor="name">项目名称 *</Label>
                <Input
                  id="name"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  placeholder="输入项目名称"
                />
              </div>
              <div>
                <Label htmlFor="description">项目描述</Label>
                <Input
                  id="description"
                  value={projectDescription}
                  onChange={(e) => setProjectDescription(e.target.value)}
                  placeholder="输入项目描述（可选）"
                />
              </div>
              
              {/* 项目配置 */}
              <div className="border-t pt-4 mt-4">
                <h4 className="font-semibold mb-3">项目配置</h4>
                <div className="space-y-3">
                  <div>
                    <Label htmlFor="requirements">项目需求</Label>
                    <Textarea
                      id="requirements"
                      value={requirements}
                      onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setRequirements(e.target.value)}
                      placeholder="详细描述项目需求、功能要求、业务场景等..."
                      rows={4}
                    />
                  </div>
                  <div>
                    <Label htmlFor="techStack">技术栈</Label>
                    <Textarea
                      id="techStack"
                      value={techStack}
                      onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setTechStack(e.target.value)}
                      placeholder="列出项目使用的技术栈，如：- FastAPI&#10;- React&#10;- PostgreSQL"
                      rows={3}
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <Label htmlFor="inputDocumentDir">文档目录</Label>
                      <Input
                        id="inputDocumentDir"
                        value={inputDocumentDir}
                        onChange={(e) => setInputDocumentDir(e.target.value)}
                        placeholder="./input_docs"
                      />
                    </div>
                    <div>
                      <Label htmlFor="projectPath">项目路径</Label>
                      <Input
                        id="projectPath"
                        value={projectPath}
                        onChange={(e) => setProjectPath(e.target.value)}
                        placeholder="./projects"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                取消
              </Button>
              <Button onClick={handleCreateProject} disabled={!projectName.trim()}>
                创建
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* 项目列表 */}
      {projects.length === 0 ? (
        <div className="text-center py-12 border-2 border-dashed border-gray-300 rounded-lg">
          <p className="text-gray-600">暂无项目</p>
          <Button className="mt-4" onClick={() => setIsCreateDialogOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            创建第一个项目
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <ProjectCard
              key={project.id}
              project={project}
              onView={() => handleViewProject(project.id)}
              onStart={() => handleStartProject(project.id)}
              onPause={() => handlePauseProject(project.id)}
              onResume={() => handleResumeProject(project.id)}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default ProjectsPage
