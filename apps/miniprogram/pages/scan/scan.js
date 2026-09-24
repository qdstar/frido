const app = getApp()

Page({
  scanImage() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      success: (res) => {
        wx.uploadFile({
          url: `${app.globalData.apiBase}/api/vision/scan`,
          filePath: res.tempFiles[0].tempFilePath,
          name: 'file',
          formData: { question: '识别冰箱内所有食材' },
          success: (uploadRes) => {
            const data = JSON.parse(uploadRes.data)
            wx.showModal({ title: '识别结果', content: JSON.stringify(data.vision, null, 2), showCancel: false })
          }
        })
      }
    })
  }
})
