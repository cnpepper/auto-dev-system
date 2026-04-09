/**
 * 配置管理页面
 */
import { createFileRoute } from "@tanstack/react-router"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Plus, Power } from "lucide-react"
import { useState } from "react"
import {
  useSystemConfigs,
  useCreateSystemConfig,
  useUpdateSystemConfig,
  useToolConfigs,
  useCreateToolConfig,
  useUpdateToolConfig,
  useActivateTool,
  useDeactivateTool,
} from "@/hooks/useConfigs"
import { formatDateTime } from "@/utils/project"

export const Route = createFileRoute("/_layout/configs")({
  component: ConfigsPage,
})

function ConfigsPage() {
  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-3xl font-bold">配置管理</h1>
        <p className="text-gray-600 mt-1">管理系统配置和工具配置</p>
      </div>

      {/* 配置标签页 */}
      <Tabs defaultValue="system" className="w-full">
        <TabsList>
          <TabsTrigger value="system">系统配置</TabsTrigger>
          <TabsTrigger value="tools">工具配置</TabsTrigger>
        </TabsList>

        {/* 系统配置 */}
        <TabsContent value="system">
          <SystemConfigsTab />
        </TabsContent>

        {/* 工具配置 */}
        <TabsContent value="tools">
          <ToolConfigsTab />
        </TabsContent>
      </Tabs>
    </div>
  )
}

/**
 * 系统配置标签页
 */
function SystemConfigsTab() {
  const { data: configsData, isLoading } = useSystemConfigs()
  const createMutation = useCreateSystemConfig()
  const updateMutation = useUpdateSystemConfig()

  const [showCreateForm, setShowCreateForm] = useState(false)
  const [formData, setFormData] = useState({
    config_key: "",
    config_value: "",
    description: "",
  })

  const configs = configsData?.data || []

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">加载中...</div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* 创建按钮 */}
      <div className="flex justify-end">
        <Button onClick={() => setShowCreateForm(!showCreateForm)}>
          <Plus className="h-4 w-4 mr-2" />
          添加配置
        </Button>
      </div>

      {/* 创建表单 */}
      {showCreateForm && (
        <Card>
          <CardHeader>
            <CardTitle>添加系统配置</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <Label htmlFor="config_key">配置键</Label>
                <Input
                  id="config_key"
                  value={formData.config_key}
                  onChange={(e) => setFormData({ ...formData, config_key: e.target.value })}
                  placeholder="配置键名"
                />
              </div>
              <div>
                <Label htmlFor="config_value">配置值</Label>
                <Input
                  id="config_value"
                  value={formData.config_value}
                  onChange={(e) => setFormData({ ...formData, config_value: e.target.value })}
                  placeholder="配置值"
                />
              </div>
              <div>
                <Label htmlFor="description">描述</Label>
                <Input
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="配置描述"
                />
              </div>
            </div>
            <div className="flex gap-2 mt-4">
              <Button
                onClick={() => {
                  createMutation.mutate(formData)
                  setShowCreateForm(false)
                  setFormData({ config_key: "", config_value: "", description: "" })
                }}
              >
                保存
              </Button>
              <Button variant="outline" onClick={() => setShowCreateForm(false)}>
                取消
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 配置列表 */}
      {configs.length === 0 ? (
        <div className="text-center py-12 border-2 border-dashed border-gray-300 rounded-lg">
          <p className="text-gray-600">暂无系统配置</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {configs.map((config) => (
            <Card key={config.id}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <CardTitle className="text-lg">{config.config_key}</CardTitle>
                  <Button size="sm" variant="outline">
                    编辑
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div>
                    <span className="font-medium">配置值:</span>
                    <p className="text-gray-600 mt-1 font-mono text-sm">{config.config_value}</p>
                  </div>
                  {config.description && (
                    <div>
                      <span className="font-medium">描述:</span>
                      <p className="text-gray-600 mt-1">{config.description}</p>
                    </div>
                  )}
                  <div className="text-sm text-gray-600">
                    更新时间: {formatDateTime(config.updated_at)}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

/**
 * 工具配置标签页
 */
function ToolConfigsTab() {
  const { data: toolsData, isLoading } = useToolConfigs()
  const createMutation = useCreateToolConfig()
  const activateMutation = useActivateTool()
  const deactivateMutation = useDeactivateTool()

  const tools = toolsData?.data || []

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">加载中...</div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* 创建按钮 */}
      <div className="flex justify-end">
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          添加工具
        </Button>
      </div>

      {/* 工具列表 */}
      {tools.length === 0 ? (
        <div className="text-center py-12 border-2 border-dashed border-gray-300 rounded-lg">
          <p className="text-gray-600">暂无工具配置</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {tools.map((tool) => (
            <Card key={tool.id}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-lg">{tool.tool_name}</CardTitle>
                    <p className="text-sm text-gray-600 mt-1">{tool.tool_type}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={tool.is_active ? "default" : "secondary"}>
                      {tool.is_active ? "已激活" : "未激活"}
                    </Badge>
                    <Switch
                      checked={tool.is_active || false}
                      onCheckedChange={(checked) => {
                        if (checked) {
                          activateMutation.mutate(tool.id)
                        } else {
                          deactivateMutation.mutate(tool.id)
                        }
                      }}
                    />
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div>
                    <span className="font-medium">配置信息:</span>
                    <pre className="text-gray-600 mt-1 text-sm bg-gray-50 p-2 rounded overflow-auto max-h-32">
                      {JSON.stringify(tool.config_json, null, 2)}
                    </pre>
                  </div>
                  <div className="text-sm text-gray-600">
                    更新时间: {formatDateTime(tool.updated_at)}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

export default ConfigsPage
