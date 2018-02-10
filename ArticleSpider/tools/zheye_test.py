from ArticleSpider.zheye import zheye

z = zheye()
positions = z.Recognize('captcha-cn.gif')
print(positions)