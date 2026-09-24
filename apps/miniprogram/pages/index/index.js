const app = getApp()

Page({
  data: { expiring: [], inventoryCount: 0, decision: null },

  onShow() {
    this.loadSummary()
  },

  loadSummary() {
    const base = app.globalData.apiBase
    wx.request({
      url: `${base}/api/inventory`,
      success: (res) => {
        this.setData({ inventoryCount: (res.data.items || []).length })
      }
    })
    wx.request({
      url: `${base}/api/inventory/expiring?days=3`,
      success: (res) => {
        this.setData({ expiring: res.data.items || [] })
      }
    })
    wx.request({
      url: `${base}/api/agent/decide`,
      method: 'POST',
      data: { question: '今天有什么建议？' },
      success: (res) => {
        this.setData({ decision: res.data.decision })
      }
    })
  }
})
