const app = getApp()

Page({
  data: { input: '', messages: [] },

  onInput(e) { this.setData({ input: e.detail.value }) },

  send() {
    const q = this.data.input.trim()
    if (!q) return
    wx.request({
      url: `${app.globalData.apiBase}/api/agent/decide`,
      method: 'POST',
      data: { question: q },
      success: (res) => {
        const msgs = this.data.messages.concat([
          { role: 'user', text: q },
          { role: 'assistant', text: res.data.decision.reason }
        ])
        this.setData({ messages: msgs, input: '' })
      }
    })
  }
})
