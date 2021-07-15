from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),  # 登录页面
    path('loginSubmit', views.login_submit, name='loginSubmit'),  # 提交登录
    path('signin', views.signin, name='signin'),  # 注册页面
    path('signinSubmit', views.signin_submit, name='signinSubmit'),  # 提交注册
    path('selfInfo', views.self_info, name='selfInfo'),  # 个人信息
    path('circulate', views.circulate, name='circulate'),  # 流通借还
    path('search', views.search, name='readerSearch'),  # 借阅页面
    path('borrow', views.borrow, name='borrow'),  # 借一本书
    path('continueBorrow', views.continue_borrow, name='continueBorrow'),  # 续借一本书
    path('returnBook', views.return_book, name='returnBook'),  # 还一本书
    path('payFine',views.pay_fine,name='payFine'), # 支付罚金
    path('modifyPassword', views.modify_password, name='modifyPassword'),  # 修改密码
]
