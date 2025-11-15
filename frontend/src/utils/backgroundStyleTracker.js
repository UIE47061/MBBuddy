import { API_BASE_URL } from '@/utils/api'

export class BackgroundStyleTracker {
  static async trackMeeting(meetingData) {
    try {
      const profile = await this.loadProfile()
      const analysis = this.analyzeMeeting(meetingData)
      
      // 更新風格檔案
      this.updateProfile(profile, analysis)
      
      // 生成新的 prompt
      const prompt = this.generatePrompt(profile)
      
      // 儲存到 JSON 檔案
      await this.saveProfile(profile)
      
      console.log('🎯 背景風格追蹤完成:', {
        meetingCount: profile.totalMeetings,
        dominantStyle: prompt.dominantStyle,
        prompt: prompt.text
      })
      
      return prompt
    } catch (error) {
      console.error('❌ 背景風格追蹤失敗:', error)
      return null
    }
  }
  
  static async loadProfile() {
    try {
      // 從後端 API 載入
      const response = await fetch(`${API_BASE_URL}/api/host-style`)
      if (response.ok) {
        const profile = await response.json()
        
        console.log('📄 從 JSON 檔案載入風格檔案 (第 ' + profile.totalMeetings + ' 次討論)')
        return profile
      } else {
        throw new Error('API 回應失敗')
      }
    } catch (error) {
      console.warn('JSON 檔案載入失敗:', error)
      
      // 降級到 localStorage
      const stored = localStorage.getItem('hostMeetingStyleData')
      if (stored) {
        console.log('📱 降級使用 localStorage')
        return JSON.parse(stored)
      }
      
      // 最後返回預設值
      console.log('🆕 使用預設風格檔案')
      return this.getDefaultProfile()
    }
  }
  
  static async saveProfile(profile) {
    try {
      // 更新迭代計數
      if (!profile.metadata) {
        profile.metadata = {}
      }
      profile.metadata.iterationCount = (profile.metadata.iterationCount || 0) + 1
      profile.lastUpdated = new Date().toISOString()
      
      // 主要：存到後端 JSON 檔案
      const response = await fetch(`${API_BASE_URL}/api/update-host-style`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(profile)
      })
      
      if (response.ok) {
        console.log('✅ 風格檔案已更新到 JSON 檔案 (第 ' + profile.metadata.iterationCount + ' 次迭代)')
      } else {
        throw new Error('API 更新失敗')
      }
      
      // 備份：同時存到 localStorage
      localStorage.setItem('hostMeetingStyleData', JSON.stringify(profile))
      
    } catch (error) {
      console.error('JSON 檔案更新失敗，使用 localStorage 備份:', error)
      // 降級到 localStorage
      localStorage.setItem('hostMeetingStyleData', JSON.stringify(profile))
    }
  }
  
  static getDefaultProfile() {
    return {
      version: '1.0',
      created: new Date().toISOString(),
      totalMeetings: 0,
      lastUpdated: null,
      styles: {
        democratic: 0,
        efficient: 0,
        engaging: 0,
        structured: 0
      },
      patterns: {
        avgParticipants: 0,
        avgComments: 0,
        avgInteraction: 0,
        avgBalance: 0
      },
      recentMeetings: [],
      currentPrompt: null,
      metadata: {
        hostId: this.generateHostId(),
        userAgent: 'MBBuddy_Host',
        iterationCount: 0
      }
    }
  }
  
  static generateHostId() {
    return 'host_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now()
  }
  
  static async writeToJSONFile(profile) {
    try {
      // 由於瀏覽器安全限制，無法直接寫入本地檔案
      // 這裡我們使用一個模擬的 API 請求來更新檔案
      const response = await fetch('/api/update-host-style', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(profile)
      })
      
      if (!response.ok) {
        throw new Error('無法更新 JSON 檔案')
      }
      
      console.log('📝 JSON 檔案已更新')
    } catch (error) {
      // 如果 API 不存在，我們降級到 localStorage 作為備份
      console.warn('JSON 檔案寫入失敗，降級到 localStorage:', error)
      localStorage.setItem('hostMeetingStyleData', JSON.stringify(profile))
    }
  }
  
  static analyzeMeeting(meetingData) {
    const participants = Array.isArray(meetingData.participants) ? meetingData.participants : []
    const allQuestions = Array.isArray(meetingData.questions) ? meetingData.questions : []
    const comments = allQuestions.filter(q => q && !q.isAISummary) || []
    const totalVotes = allQuestions.reduce((sum, q) => 
      sum + (q?.vote_good || 0) + (q?.vote_bad || 0), 0) || 0
    
    // 計算參與平衡度
    const participantCounts = {}
    comments.forEach(q => {
      if (q && q.nickname) {
        participantCounts[q.nickname] = (participantCounts[q.nickname] || 0) + 1
      }
    })
    
    const counts = Object.values(participantCounts)
    let balance = 1
    if (counts.length > 1) {
      const mean = this.calculateMean(counts)
      const variance = this.calculateVariance(counts)
      if (mean > 0) {
        balance = Math.max(0, Math.min(1, 1 - (variance / Math.pow(mean, 2))))
      }
    }
    
    return {
      participantCount: participants.length,
      commentCount: comments.length,
      interactionLevel: comments.length > 0 ? totalVotes / comments.length : 0,
      participantBalance: balance,
      avgCommentLength: comments.length > 0 ? 
        comments.reduce((sum, c) => sum + (c?.content?.length || 0), 0) / comments.length : 0,
      hasAISummaries: allQuestions.filter(q => q && q.isAISummary).length > 0,
      uniqueParticipants: Object.keys(participantCounts).length
    }
  }
  
  static updateProfile(profile, analysis) {
    // 更新統計
    profile.totalMeetings += 1
    profile.lastUpdated = new Date().toISOString()
    
    // 更新平均值
    const total = profile.totalMeetings
    const weight = Math.min(total, 10)
    
    profile.patterns.avgParticipants = 
      ((profile.patterns.avgParticipants * (weight - 1)) + analysis.participantCount) / weight
    profile.patterns.avgComments = 
      ((profile.patterns.avgComments * (weight - 1)) + analysis.commentCount) / weight
    profile.patterns.avgInteraction = 
      ((profile.patterns.avgInteraction * (weight - 1)) + analysis.interactionLevel) / weight
    profile.patterns.avgBalance = 
      ((profile.patterns.avgBalance * (weight - 1)) + analysis.participantBalance) / weight
    
    // 分析風格傾向
    if (analysis.participantBalance > 0.7 && analysis.uniqueParticipants > 2) {
      profile.styles.democratic += 1
    }
    if (analysis.commentCount > 15 && analysis.interactionLevel > 0.3) {
      profile.styles.efficient += 1
    }
    if (analysis.interactionLevel > 0.6) {
      profile.styles.engaging += 1
    }
    if (analysis.hasAISummaries && analysis.avgCommentLength > 30) {
      profile.styles.structured += 1
    }
    
    // 保存最近討論記錄
    profile.recentMeetings.push({
      timestamp: new Date().toISOString(),
      meetingNumber: profile.totalMeetings,
      ...analysis
    })
    
    if (profile.recentMeetings.length > 5) {
      profile.recentMeetings = profile.recentMeetings.slice(-5)
    }
  }
  
  static generatePrompt(profile) {
    if (profile.totalMeetings === 0) return null
    
    const iterationCount = profile.metadata?.iterationCount || profile.totalMeetings || 0
    
    // 找出主導風格
    const styles = profile.styles
    const dominantStyle = Object.keys(styles).reduce((a, b) => 
      styles[a] > styles[b] ? a : b
    )
    
    const styleStrength = styles[dominantStyle] / profile.totalMeetings
    
    const styleDescriptions = {
      democratic: "重視所有參與者的聲音，善於平衡不同意見",
      efficient: "注重討論效率，能有效推進討論進度", 
      engaging: "擅長營造互動氛圍，激發參與者積極性",
      structured: "偏好結構化討論，注重深度分析和總結"
    }
    
    const trend = this.calculateTrend(profile)
    
    const prompt = {
      timestamp: new Date().toISOString(),
      meetingCount: profile.totalMeetings,
      iterationCount: iterationCount,
      dominantStyle: dominantStyle,
      styleStrength: Math.round(styleStrength * 100),
      trend: trend,
      text: `【第 ${profile.totalMeetings} 次討論風格分析】

🎯 主要風格: ${styleDescriptions[dominantStyle]} (${Math.round(styleStrength * 100)}% 傾向)

📊 當前表現:
• 平均參與者: ${profile.patterns.avgParticipants.toFixed(1)} 人
• 平均討論量: ${profile.patterns.avgComments.toFixed(1)} 條留言
• 互動活躍度: ${(profile.patterns.avgInteraction * 100).toFixed(0)}%
• 參與平衡度: ${(profile.patterns.avgBalance * 100).toFixed(0)}%

${trend ? `📈 變化趨勢: ${trend}` : ''}

💡 ${this.getStyleAdvice(dominantStyle, profile.patterns, profile.totalMeetings)}`
    }
    
    profile.currentPrompt = prompt
    return prompt
  }
  
  static calculateTrend(profile) {
    if (!profile.recentMeetings || profile.recentMeetings.length < 2) {
      return null
    }
    
    const recent = profile.recentMeetings.slice(-2)
    const [prev, current] = recent
    
    if (!prev || !current) {
      return null
    }
    
    const trends = []
    
    const interactionDiff = (current.interactionLevel || 0) - (prev.interactionLevel || 0)
    if (interactionDiff > 0.1) {
      trends.push("互動度提升")
    } else if (interactionDiff < -0.1) {
      trends.push("互動度下降")
    }
    
    const balanceDiff = (current.participantBalance || 0) - (prev.participantBalance || 0)
    if (balanceDiff > 0.1) {
      trends.push("參與更平衡")
    } else if (balanceDiff < -0.1) {
      trends.push("參與較集中")
    }
    
    const commentRatio = (current.commentCount || 0) / Math.max(prev.commentCount || 1, 1)
    if (commentRatio > 1.2) {
      trends.push("討論更熱烈")
    } else if (commentRatio < 0.8) {
      trends.push("討論較溫和")
    }
    
    return trends.length > 0 ? trends.join(", ") : "表現穩定"
  }
  
  static getStyleAdvice(style, patterns, meetingCount) {
    const advice = {
      democratic: patterns.avgComments < 10 ? 
        "建議增加引導性問題，鼓勵更多成員發言" : 
        "很好地維持了民主討論氛圍，繼續保持",
      efficient: patterns.avgInteraction < 0.5 ? 
        "在保持效率的同時，可適度增加互動時間" : 
        "效率與參與度平衡良好，值得延續",
      engaging: patterns.avgBalance < 0.6 ? 
        "注意避免少數人主導，可嘗試輪流發言機制" : 
        "成功營造了活躍且平衡的討論環境",
      structured: patterns.avgComments > 20 ? 
        "豐富的結構化討論，可考慮階段性總結重點" : 
        "可嘗試更多分析工具和總結技巧"
    }
    
    let baseAdvice = advice[style] || "持續觀察中，正在學習您的主持風格"
    
    if (meetingCount >= 5) {
      baseAdvice += "。經過多次討論觀察，您的風格已趨於穩定"
    }
    if (meetingCount >= 10) {
      baseAdvice += "，可考慮嘗試新的主持技巧來進一步提升"
    }
    
    return baseAdvice
  }
  
  static calculateMean(arr) {
    return arr.length > 0 ? arr.reduce((a, b) => a + b, 0) / arr.length : 0
  }
  
  static calculateVariance(arr) {
    const mean = this.calculateMean(arr)
    return arr.length > 0 ? 
      arr.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / arr.length : 0
  }
  
  static async getCurrentPrompt() {
    const profile = await this.loadProfile()
    return profile.currentPrompt
  }
  
  static async viewProfile() {
    const profile = await this.loadProfile()
    console.group('🎯 當前主持風格檔案 (JSON)')
    console.log('📊 基本資訊:', {
      總討論數: profile.totalMeetings,
      迭代次數: profile.metadata?.iterationCount || 0,
      建立時間: profile.created,
      最後更新: profile.lastUpdated
    })
    console.log('🎨 風格分布:', profile.styles)
    console.log('📈 行為模式:', profile.patterns)
    if (profile.currentPrompt) {
      console.log('💬 當前分析:', profile.currentPrompt.text)
    }
    console.groupEnd()
    return profile
  }
}