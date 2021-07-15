from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='manageLog'),  # 管理者登录界面
    path('manageLogSubmit', views.login_submit, name='manageLogSubmit'),  # 提交登录信息
    path('index', views.index, name='index'),
    path('insertBook', views.insert_book, name="insertBook"),
    path('modifyBook', views.modify_book, name="modifyBook"),
    path('deleteBook', views.delete_book, name="deleteBook"),
    path('searchBook', views.search_book, name="searchBook"),  # 搜索图书
    path('inventory', views.inventory, name="inventory"),  # 图书库存页面
    path('insertInventory', views.insert_inventory, name="insertInventory"),  # 增加库存
    path('modifyInventory', views.modify_inventory, name="modifyInventory"),
    path('deleteInventory', views.delete_inventory, name="deleteInventory"),
    path('searchInventory', views.search_inventory, name="searchInventory"),  # 查询库存
    path('subscribe', views.subscribe, name="subscribe"),  # 采编页面
    path('insertSubscribe', views.insert_subscribe, name="insertSubscribe"),
    path('deleteSubscribe', views.delete_subscribe, name="deleteSubscribe"),
    path('submitSubscribe', views.submit_subscribe, name="submitSubscribe"),
    path('purchase', views.purchase, name="purchase"),  # 进货界面
    path('submitPurchase', views.submit_purchase, name="submitPurchase"),  # 提交进货
    path('cancelPurchase', views.cancel_purchase, name="cancelPurchase"),  # 取消进货
    path('confirmReceipt', views.confirm_receipt, name="confirmReceipt"),  # 确认收货
    path('finance', views.finance, name="finance"),  # 财务流水账页面
    path('payBill', views.pay_bill, name="payBill"),  # 支付某笔流水
    path('cancelBill', views.cancel_bill, name="cancelBill"),  # 取消某笔流水
    path('receiveMoney', views.receive_money, name="receiveMoney"),  # 确认收款
    path('user',views.user,name='user'),  # 用户管理页面
    path('deleteUser',views.delete_user,name='delete_user'), # 删除用户
]
