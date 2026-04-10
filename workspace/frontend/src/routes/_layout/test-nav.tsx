/**
 * 测试路由导航
 */
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { Button } from "@/components/ui/button"

export const Route = createFileRoute("/_layout/test-nav")({
  component: TestNavPage,
})

function TestNavPage() {
  const navigate = useNavigate()

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">路由导航测试</h1>
      
      <div className="space-y-4">
        <div>
          <p className="mb-2">测试跳转到项目详情页面（ID=1）：</p>
          <Button 
            onClick={() => {
              console.log('点击测试按钮')
              navigate({
                to: '/projects/$projectId',
                params: { projectId: '1' }
              })
            }}
          >
            跳转到项目1
          </Button>
        </div>
        
        <div>
          <p className="mb-2">测试使用路由路径：</p>
          <Button 
            onClick={() => {
              console.log('使用路径跳转')
              navigate({ to: '/projects' })
            }}
          >
            返回项目列表
          </Button>
        </div>
      </div>
    </div>
  )
}
