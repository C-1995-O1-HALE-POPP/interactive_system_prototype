import { useState, useEffect } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2, Heart, Brain, MessageSquare, BarChart3, Upload, Settings } from 'lucide-react'
import apiService from './lib/api'
import './App.css'

function App() {
  const [currentUser, setCurrentUser] = useState('demo_user_001')
  const [systemStatus, setSystemStatus] = useState(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  // 检查系统状态
  useEffect(() => {
    checkSystemHealth()
  }, [])

  const checkSystemHealth = async () => {
    try {
      const health = await apiService.getHealth()
      setSystemStatus(health)
    } catch (error) {
      console.error('系统健康检查失败:', error)
    }
  }

  const showMessage = (text, type = 'info') => {
    setMessage({ text, type })
    setTimeout(() => setMessage(''), 5000)
  }

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-6xl mx-auto">
        {/* 头部 */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-foreground mb-2">
            RIS系统前端 🤖💝
          </h1>
          <p className="text-muted-foreground">
            智能关系管理系统 - 让AI理解你的情感世界
          </p>
          
          {/* 系统状态指示器 */}
          <div className="flex items-center gap-4 mt-4">
            <Badge variant={systemStatus?.status === 'healthy' ? 'default' : 'destructive'}>
              系统状态: {systemStatus?.status || '检查中...'}
            </Badge>
            <Badge variant={systemStatus?.system_info?.llm_service_status?.is_available ? 'default' : 'secondary'}>
              LLM服务: {systemStatus?.system_info?.llm_service_status?.is_available ? '可用' : '不可用'}
            </Badge>
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">当前用户:</span>
              <Input 
                value={currentUser} 
                onChange={(e) => setCurrentUser(e.target.value)}
                className="w-32 h-8"
                placeholder="用户ID"
              />
            </div>
          </div>
        </div>

        {/* 消息提示 */}
        {message && (
          <Alert className="mb-4">
            <AlertDescription>{message.text}</AlertDescription>
          </Alert>
        )}

        {/* 主要功能标签页 */}
        <Tabs defaultValue="interaction" className="w-full">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="interaction" className="flex items-center gap-2">
              <MessageSquare className="w-4 h-4" />
              交互处理
            </TabsTrigger>
            <TabsTrigger value="emotion" className="flex items-center gap-2">
              <Heart className="w-4 h-4" />
              情感分析
            </TabsTrigger>
            <TabsTrigger value="llm" className="flex items-center gap-2">
              <Brain className="w-4 h-4" />
              LLM服务
            </TabsTrigger>
            <TabsTrigger value="reports" className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              报告生成
            </TabsTrigger>
            <TabsTrigger value="multimedia" className="flex items-center gap-2">
              <Upload className="w-4 h-4" />
              多媒体
            </TabsTrigger>
            <TabsTrigger value="management" className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              管理
            </TabsTrigger>
          </TabsList>

          {/* 交互处理标签页 */}
          <TabsContent value="interaction">
            <InteractionTab currentUser={currentUser} showMessage={showMessage} />
          </TabsContent>

          {/* 情感分析标签页 */}
          <TabsContent value="emotion">
            <EmotionTab currentUser={currentUser} showMessage={showMessage} />
          </TabsContent>

          {/* LLM服务标签页 */}
          <TabsContent value="llm">
            <LLMTab currentUser={currentUser} showMessage={showMessage} />
          </TabsContent>

          {/* 报告生成标签页 */}
          <TabsContent value="reports">
            <ReportsTab currentUser={currentUser} showMessage={showMessage} />
          </TabsContent>

          {/* 多媒体标签页 */}
          <TabsContent value="multimedia">
            <MultimediaTab currentUser={currentUser} showMessage={showMessage} />
          </TabsContent>

          {/* 管理标签页 */}
          <TabsContent value="management">
            <ManagementTab currentUser={currentUser} showMessage={showMessage} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

// 交互处理组件
function InteractionTab({ currentUser, showMessage }) {
  const [text, setText] = useState('')
  const [inputType, setInputType] = useState('topic')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleProcessInteraction = async () => {
    if (!text.trim()) {
      showMessage('请输入交互内容', 'error')
      return
    }

    setLoading(true)
    try {
      const response = await apiService.processInteraction({
        user_id: currentUser,
        text: text,
        input_type: inputType,
        context: {
          timestamp: new Date().toISOString(),
          source: 'frontend'
        }
      })
      
      setResult(response.result)
      showMessage('交互处理成功！', 'success')
    } catch (error) {
      showMessage(`交互处理失败: ${error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>交互内容处理</CardTitle>
          <CardDescription>
            输入文本内容，系统将自动进行情感分析、角色识别和回忆生成
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium">交互内容</label>
            <Textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="例如：今天和张三一起去北京出差，心情很好！我们讨论了新项目的计划。"
              className="mt-1"
              rows={3}
            />
          </div>
          
          <div>
            <label className="text-sm font-medium">输入类型</label>
            <select 
              value={inputType} 
              onChange={(e) => setInputType(e.target.value)}
              className="mt-1 w-full p-2 border rounded-md"
            >
              <option value="topic">话题</option>
              <option value="photo">照片</option>
              <option value="voice">语音</option>
            </select>
          </div>

          <Button 
            onClick={handleProcessInteraction} 
            disabled={loading}
            className="w-full"
          >
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            处理交互
          </Button>
        </CardContent>
      </Card>

      {/* 处理结果 */}
      {result && (
        <Card>
          <CardHeader>
            <CardTitle>处理结果</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* 情感分析结果 */}
              {result.emotion_analysis && (
                <div>
                  <h4 className="font-medium mb-2">情感分析</h4>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">愉悦度:</span>
                      <span className="ml-2 font-medium">
                        {(result.emotion_analysis.pad_values?.pleasure * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">唤醒度:</span>
                      <span className="ml-2 font-medium">
                        {(result.emotion_analysis.pad_values?.arousal * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">支配度:</span>
                      <span className="ml-2 font-medium">
                        {(result.emotion_analysis.pad_values?.dominance * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                  <div className="mt-2">
                    <Badge variant={result.emotion_analysis.emotion_label === 'positive' ? 'default' : 
                                  result.emotion_analysis.emotion_label === 'negative' ? 'destructive' : 'secondary'}>
                      {result.emotion_analysis.emotion_label}
                    </Badge>
                  </div>
                </div>
              )}

              {/* 创建的角色 */}
              {result.personas_created && result.personas_created.length > 0 && (
                <div>
                  <h4 className="font-medium mb-2">识别的角色</h4>
                  <div className="flex flex-wrap gap-2">
                    {result.personas_created.map((persona, index) => (
                      <Badge key={index} variant="outline">
                        {persona.name} ({persona.relationship})
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* 创建的回忆 */}
              {result.memories_created && result.memories_created.length > 0 && (
                <div>
                  <h4 className="font-medium mb-2">生成的回忆</h4>
                  <div className="space-y-2">
                    {result.memories_created.map((memory, index) => (
                      <div key={index} className="p-2 bg-muted rounded-md text-sm">
                        <div>{memory.content}</div>
                        <Badge size="sm" className="mt-1">
                          {memory.emotion_annotation}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

// 情感分析组件
function EmotionTab({ currentUser, showMessage }) {
  const [text, setText] = useState('')
  const [result, setResult] = useState(null)
  const [trends, setTrends] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleAnalyzeEmotion = async () => {
    if (!text.trim()) {
      showMessage('请输入要分析的文本', 'error')
      return
    }

    setLoading(true)
    try {
      const response = await apiService.analyzeEmotion({
        text: text,
        context: {
          user_id: currentUser,
          timestamp: new Date().toISOString()
        }
      })
      
      setResult(response.result)
      showMessage('情感分析完成！', 'success')
    } catch (error) {
      showMessage(`情感分析失败: ${error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleGetTrends = async () => {
    setLoading(true)
    try {
      const response = await apiService.getEmotionTrends(currentUser, 'week')
      setTrends(response.trends)
      showMessage('情感趋势获取成功！', 'success')
    } catch (error) {
      showMessage(`获取情感趋势失败: ${error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>情感分析</CardTitle>
          <CardDescription>
            基于PAD三维情感模型进行情感分析
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium">分析文本</label>
            <Textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="例如：今天工作压力很大，但是完成了重要项目，感觉很有成就感"
              className="mt-1"
              rows={3}
            />
          </div>

          <div className="flex gap-2">
            <Button 
              onClick={handleAnalyzeEmotion} 
              disabled={loading}
              className="flex-1"
            >
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              分析情感
            </Button>
            <Button 
              onClick={handleGetTrends} 
              disabled={loading}
              variant="outline"
            >
              获取趋势
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 分析结果 */}
      {result && (
        <Card>
          <CardHeader>
            <CardTitle>分析结果</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary">
                    {(result.pad_values?.pleasure * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-muted-foreground">愉悦度</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary">
                    {(result.pad_values?.arousal * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-muted-foreground">唤醒度</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary">
                    {(result.pad_values?.dominance * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-muted-foreground">支配度</div>
                </div>
              </div>
              
              <div>
                <Badge variant={result.emotion_label === 'positive' ? 'default' : 
                              result.emotion_label === 'negative' ? 'destructive' : 'secondary'}>
                  {result.emotion_label}
                </Badge>
              </div>

              {result.detected_emotions && (
                <div>
                  <h4 className="font-medium mb-2">检测到的情感</h4>
                  <div className="flex flex-wrap gap-2">
                    {result.detected_emotions.map((emotion, index) => (
                      <Badge key={index} variant="outline">{emotion}</Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 情感趋势 */}
      {trends && (
        <Card>
          <CardHeader>
            <CardTitle>情感趋势</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="text-sm bg-muted p-4 rounded-md overflow-auto">
              {JSON.stringify(trends, null, 2)}
            </pre>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

// LLM服务组件
function LLMTab({ currentUser, showMessage }) {
  const [prompt, setPrompt] = useState('')
  const [messages, setMessages] = useState([])
  const [result, setResult] = useState(null)
  const [llmStatus, setLlmStatus] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    checkLLMStatus()
  }, [])

  const checkLLMStatus = async () => {
    try {
      const response = await apiService.getLLMStatus()
      setLlmStatus(response.status)
    } catch (error) {
      showMessage(`获取LLM状态失败: ${error.message}`, 'error')
    }
  }

  const handleLLMGenerate = async () => {
    if (!prompt.trim()) {
      showMessage('请输入提示文本', 'error')
      return
    }

    setLoading(true)
    try {
      const response = await apiService.llmGenerate({
        prompt: prompt,
        model: 'deepseek-v3',
        max_tokens: 2048,
        temperature: 0.7
      })
      
      setResult(response.result)
      showMessage('文本生成成功！', 'success')
    } catch (error) {
      showMessage(`文本生成失败: ${error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleLLMChat = async () => {
    if (!prompt.trim()) {
      showMessage('请输入聊天内容', 'error')
      return
    }

    setLoading(true)
    try {
      const newMessages = [...messages, { role: 'user', content: prompt }]
      
      const response = await apiService.llmChat({
        messages: newMessages,
        model: 'deepseek-v3',
        max_tokens: 2048,
        temperature: 0.7
      })
      
      setMessages([...newMessages, { role: 'assistant', content: response.result.content }])
      setPrompt('')
      showMessage('聊天回复成功！', 'success')
    } catch (error) {
      showMessage(`聊天失败: ${error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleLLMEmotionAnalysis = async () => {
    if (!prompt.trim()) {
      showMessage('请输入要分析的文本', 'error')
      return
    }

    setLoading(true)
    try {
      const response = await apiService.llmEmotionAnalysis({
        text: prompt,
        context: { user_id: currentUser },
        model: 'deepseek-v3'
      })
      
      setResult(response.result)
      showMessage('LLM情感分析完成！', 'success')
    } catch (error) {
      showMessage(`LLM情感分析失败: ${error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      {/* LLM状态 */}
      <Card>
        <CardHeader>
          <CardTitle>LLM服务状态</CardTitle>
        </CardHeader>
        <CardContent>
          {llmStatus ? (
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Badge variant={llmStatus.is_available ? 'default' : 'destructive'}>
                  {llmStatus.is_available ? '可用' : '不可用'}
                </Badge>
                <span className="text-sm text-muted-foreground">
                  {llmStatus.service_name}
                </span>
              </div>
              <div className="text-sm">
                <span className="text-muted-foreground">默认模型:</span>
                <span className="ml-2">{llmStatus.default_model}</span>
              </div>
              <div className="text-sm">
                <span className="text-muted-foreground">支持的模型:</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {llmStatus.supported_models?.map((model, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {model}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div>加载中...</div>
          )}
        </CardContent>
      </Card>

      {/* LLM操作 */}
      <Card>
        <CardHeader>
          <CardTitle>LLM操作</CardTitle>
          <CardDescription>
            使用百炼平台DeepSeek模型进行文本生成、聊天和情感分析
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium">输入内容</label>
            <Textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="例如：请写一首关于人工智能的诗"
              className="mt-1"
              rows={3}
            />
          </div>

          <div className="flex gap-2">
            <Button 
              onClick={handleLLMGenerate} 
              disabled={loading || !llmStatus?.is_available}
              className="flex-1"
            >
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              文本生成
            </Button>
            <Button 
              onClick={handleLLMChat} 
              disabled={loading || !llmStatus?.is_available}
              variant="outline"
            >
              聊天对话
            </Button>
            <Button 
              onClick={handleLLMEmotionAnalysis} 
              disabled={loading || !llmStatus?.is_available}
              variant="outline"
            >
              情感分析
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 聊天历史 */}
      {messages.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>聊天历史</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {messages.map((msg, index) => (
                <div key={index} className={`p-2 rounded-md ${
                  msg.role === 'user' ? 'bg-primary text-primary-foreground ml-8' : 'bg-muted mr-8'
                }`}>
                  <div className="text-xs opacity-70 mb-1">
                    {msg.role === 'user' ? '用户' : 'AI助手'}
                  </div>
                  <div className="text-sm">{msg.content}</div>
                </div>
              ))}
            </div>
            <Button 
              onClick={() => setMessages([])} 
              variant="outline" 
              size="sm" 
              className="mt-2"
            >
              清空历史
            </Button>
          </CardContent>
        </Card>
      )}

      {/* LLM结果 */}
      {result && (
        <Card>
          <CardHeader>
            <CardTitle>LLM结果</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {typeof result === 'string' ? (
                <div className="whitespace-pre-wrap text-sm">{result}</div>
              ) : (
                <pre className="text-sm bg-muted p-4 rounded-md overflow-auto">
                  {JSON.stringify(result, null, 2)}
                </pre>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

// 报告生成组件
function ReportsTab({ currentUser, showMessage }) {
  const [weeklyReport, setWeeklyReport] = useState(null)
  const [monthlyReport, setMonthlyReport] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleGetWeeklyReport = async () => {
    setLoading(true)
    try {
      const response = await apiService.getWeeklyReport(currentUser)
      setWeeklyReport(response.report)
      showMessage('周报告生成成功！', 'success')
    } catch (error) {
      showMessage(`生成周报告失败: ${error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleGetMonthlyReport = async () => {
    setLoading(true)
    try {
      const response = await apiService.getMonthlyReport(currentUser)
      setMonthlyReport(response.report)
      showMessage('月报告生成成功！', 'success')
    } catch (error) {
      showMessage(`生成月报告失败: ${error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>报告生成</CardTitle>
          <CardDescription>
            生成用户的情绪轨迹报告和统计分析
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Button 
              onClick={handleGetWeeklyReport} 
              disabled={loading}
              className="flex-1"
            >
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              生成周报告
            </Button>
            <Button 
              onClick={handleGetMonthlyReport} 
              disabled={loading}
              variant="outline"
              className="flex-1"
            >
              生成月报告
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 周报告 */}
      {weeklyReport && (
        <Card>
          <CardHeader>
            <CardTitle>周报告</CardTitle>
            <CardDescription>{weeklyReport.period}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* 摘要 */}
              {weeklyReport.summary && (
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary">
                      {weeklyReport.summary.total_interactions}
                    </div>
                    <div className="text-sm text-muted-foreground">总交互次数</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary">
                      {weeklyReport.summary.dominant_emotion}
                    </div>
                    <div className="text-sm text-muted-foreground">主导情绪</div>
                  </div>
                </div>
              )}

              {/* 情绪分布 */}
              {weeklyReport.emotion_distribution && (
                <div>
                  <h4 className="font-medium mb-2">情绪分布</h4>
                  <div className="grid grid-cols-3 gap-2">
                    <div className="text-center p-2 bg-green-50 rounded-md">
                      <div className="font-bold text-green-600">
                        {weeklyReport.emotion_distribution.positive}%
                      </div>
                      <div className="text-xs text-green-600">积极</div>
                    </div>
                    <div className="text-center p-2 bg-red-50 rounded-md">
                      <div className="font-bold text-red-600">
                        {weeklyReport.emotion_distribution.negative}%
                      </div>
                      <div className="text-xs text-red-600">消极</div>
                    </div>
                    <div className="text-center p-2 bg-gray-50 rounded-md">
                      <div className="font-bold text-gray-600">
                        {weeklyReport.emotion_distribution.neutral}%
                      </div>
                      <div className="text-xs text-gray-600">中性</div>
                    </div>
                  </div>
                </div>
              )}

              {/* 角色交互 */}
              {weeklyReport.persona_interactions && (
                <div>
                  <h4 className="font-medium mb-2">角色交互频率</h4>
                  <div className="space-y-2">
                    {Object.entries(weeklyReport.persona_interactions).map(([name, count]) => (
                      <div key={name} className="flex justify-between items-center">
                        <span className="text-sm">{name}</span>
                        <Badge variant="outline">{count}次</Badge>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 月报告 */}
      {monthlyReport && (
        <Card>
          <CardHeader>
            <CardTitle>月报告</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="text-sm bg-muted p-4 rounded-md overflow-auto">
              {JSON.stringify(monthlyReport, null, 2)}
            </pre>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

// 多媒体组件
function MultimediaTab({ currentUser, showMessage }) {
  const [audioFile, setAudioFile] = useState(null)
  const [imageFile, setImageFile] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleAudioUpload = async () => {
    if (!audioFile) {
      showMessage('请选择音频文件', 'error')
      return
    }

    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('audio', audioFile)
      formData.append('language', 'zh-CN')

      const response = await apiService.uploadAudio(formData)
      setResult(response.result)
      showMessage('音频识别成功！', 'success')
    } catch (error) {
      showMessage(`音频识别失败: ${error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleImageUpload = async () => {
    if (!imageFile) {
      showMessage('请选择图像文件', 'error')
      return
    }

    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('image', imageFile)
      formData.append('language', 'chi_sim')

      const response = await apiService.uploadImage(formData)
      setResult(response.result)
      showMessage('图像识别成功！', 'success')
    } catch (error) {
      showMessage(`图像识别失败: ${error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>多媒体识别</CardTitle>
          <CardDescription>
            上传音频或图像文件进行识别和分析
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* 音频上传 */}
          <div>
            <label className="text-sm font-medium">音频文件</label>
            <div className="mt-1 flex items-center gap-2">
              <Input
                type="file"
                accept="audio/*"
                onChange={(e) => setAudioFile(e.target.files[0])}
                className="flex-1"
              />
              <Button 
                onClick={handleAudioUpload} 
                disabled={loading || !audioFile}
              >
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                识别音频
              </Button>
            </div>
          </div>

          {/* 图像上传 */}
          <div>
            <label className="text-sm font-medium">图像文件</label>
            <div className="mt-1 flex items-center gap-2">
              <Input
                type="file"
                accept="image/*"
                onChange={(e) => setImageFile(e.target.files[0])}
                className="flex-1"
              />
              <Button 
                onClick={handleImageUpload} 
                disabled={loading || !imageFile}
              >
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                识别图像
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 识别结果 */}
      {result && (
        <Card>
          <CardHeader>
            <CardTitle>识别结果</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="text-sm bg-muted p-4 rounded-md overflow-auto">
              {JSON.stringify(result, null, 2)}
            </pre>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

// 管理组件
function ManagementTab({ currentUser, showMessage }) {
  const [personas, setPersonas] = useState([])
  const [memories, setMemories] = useState([])
  const [userStats, setUserStats] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleCreateUser = async () => {
    setLoading(true)
    try {
      await apiService.createUser(currentUser)
      showMessage('用户创建成功！', 'success')
      await handleGetUserStats()
    } catch (error) {
      showMessage(`用户创建失败: ${error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleGetPersonas = async () => {
    setLoading(true)
    try {
      const response = await apiService.getPersonas(currentUser)
      setPersonas(response.personas || [])
      showMessage('角色列表获取成功！', 'success')
    } catch (error) {
      showMessage(`获取角色列表失败: ${error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleGetMemories = async () => {
    setLoading(true)
    try {
      const response = await apiService.getMemories(currentUser, { limit: 20 })
      setMemories(response.memories || [])
      showMessage('回忆列表获取成功！', 'success')
    } catch (error) {
      showMessage(`获取回忆列表失败: ${error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleGetUserStats = async () => {
    setLoading(true)
    try {
      const response = await apiService.getUserStats(currentUser)
      setUserStats(response.stats)
      showMessage('用户统计获取成功！', 'success')
    } catch (error) {
      showMessage(`获取用户统计失败: ${error.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>用户管理</CardTitle>
          <CardDescription>
            管理用户、角色和回忆数据
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-2">
            <Button 
              onClick={handleCreateUser} 
              disabled={loading}
            >
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              创建用户
            </Button>
            <Button 
              onClick={handleGetUserStats} 
              disabled={loading}
              variant="outline"
            >
              获取统计
            </Button>
            <Button 
              onClick={handleGetPersonas} 
              disabled={loading}
              variant="outline"
            >
              获取角色
            </Button>
            <Button 
              onClick={handleGetMemories} 
              disabled={loading}
              variant="outline"
            >
              获取回忆
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 用户统计 */}
      {userStats && (
        <Card>
          <CardHeader>
            <CardTitle>用户统计</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="text-sm bg-muted p-4 rounded-md overflow-auto">
              {JSON.stringify(userStats, null, 2)}
            </pre>
          </CardContent>
        </Card>
      )}

      {/* 角色列表 */}
      {personas.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>角色列表</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {personas.map((persona, index) => (
                <div key={index} className="p-2 border rounded-md">
                  <div className="font-medium">{persona.name}</div>
                  <div className="text-sm text-muted-foreground">
                    {persona.description}
                  </div>
                  <div className="flex gap-1 mt-1">
                    {persona.personality_traits?.map((trait, i) => (
                      <Badge key={i} variant="outline" className="text-xs">
                        {trait}
                      </Badge>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 回忆列表 */}
      {memories.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>回忆列表</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {memories.map((memory, index) => (
                <div key={index} className="p-2 border rounded-md">
                  <div className="text-sm">{memory.content}</div>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant="outline" className="text-xs">
                      {memory.emotion_annotation}
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      {new Date(memory.timestamp).toLocaleString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default App

