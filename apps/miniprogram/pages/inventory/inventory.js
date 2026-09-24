const app = getApp()

Page({
  data: { items: [] },
  onShow() {
    wx.request({
      url: `${app.globalData.apiBase}/api/inventory`,
      success: (res) => this.setData({ items: res.data.items || [] })
    })
  }
})
