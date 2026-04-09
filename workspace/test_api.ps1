# 测试API接口脚本
# 用于诊断项目详情页面无法显示的问题

Write-Host "=== API接口诊断脚本 ===" -ForegroundColor Green
Write-Host ""

# 1. 测试后端服务是否运行
Write-Host "1. 测试后端服务状态..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/projects/" -Method GET -Headers @{
        "Authorization" = "Bearer $(Get-Content -Path "$env:USERPROFILE\.access_token" -ErrorAction SilentlyContinue)"
    } -ErrorAction Stop
    Write-Host "✓ 后端服务正常运行" -ForegroundColor Green
    Write-Host "  状态码: $($response.StatusCode)" -ForegroundColor Gray
} catch {
    Write-Host "✗ 后端服务异常: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 2. 测试项目列表API
Write-Host ""
Write-Host "2. 测试项目列表API..." -ForegroundColor Yellow
try {
    $token = Get-Content -Path "$env:USERPROFILE\.access_token" -ErrorAction SilentlyContinue
    if (-not $token) {
        Write-Host "✗ 未找到访问令牌，请先登录" -ForegroundColor Red
        Write-Host "  提示: 在浏览器控制台执行 localStorage.getItem('access_token')" -ForegroundColor Gray
        exit 1
    }
    
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
    }
    
    $projectsResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/projects/" -Method GET -Headers $headers
    Write-Host "✓ 项目列表API正常" -ForegroundColor Green
    Write-Host "  项目数量: $($projectsResponse.count)" -ForegroundColor Gray
    
    if ($projectsResponse.data.Count -gt 0) {
        $firstProject = $projectsResponse.data[0]
        Write-Host "  第一个项目: $($firstProject.name) (ID: $($firstProject.id))" -ForegroundColor Gray
        
        # 3. 测试项目详情API
        Write-Host ""
        Write-Host "3. 测试项目详情API..." -ForegroundColor Yellow
        try {
            $detailResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/projects/$($firstProject.id)" -Method GET -Headers $headers
            Write-Host "✓ 项目详情API正常" -ForegroundColor Green
            Write-Host "  项目名称: $($detailResponse.name)" -ForegroundColor Gray
            Write-Host "  项目状态: $($detailResponse.status)" -ForegroundColor Gray
            Write-Host "  当前阶段: $($detailResponse.current_stage)" -ForegroundColor Gray
            
            # 4. 测试流程阶段API
            Write-Host ""
            Write-Host "4. 测试流程阶段API..." -ForegroundColor Yellow
            try {
                $stagesResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/projects/$($firstProject.id)/stages" -Method GET -Headers $headers
                Write-Host "✓ 流程阶段API正常" -ForegroundColor Green
                Write-Host "  阶段数量: $($stagesResponse.count)" -ForegroundColor Gray
                
                if ($stagesResponse.count -eq 0) {
                    Write-Host "  提示: 该项目暂无流程阶段，这是正常的（新创建的项目）" -ForegroundColor Cyan
                }
            } catch {
                Write-Host "✗ 流程阶段API异常: $($_.Exception.Message)" -ForegroundColor Red
            }
            
        } catch {
            Write-Host "✗ 项目详情API异常: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "  提示: 暂无项目，请先创建项目" -ForegroundColor Cyan
    }
    
} catch {
    Write-Host "✗ 项目列表API异常: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== 诊断完成 ===" -ForegroundColor Green
Write-Host ""
Write-Host "如果所有API都正常，请检查浏览器控制台（F12）的错误信息" -ForegroundColor Cyan
Write-Host "常见问题:" -ForegroundColor Cyan
Write-Host "  1. 浏览器控制台有JavaScript错误" -ForegroundColor Gray
Write-Host "  2. 网络请求失败（检查Network标签）" -ForegroundColor Gray
Write-Host "  3. 认证令牌过期（重新登录）" -ForegroundColor Gray
