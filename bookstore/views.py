from django.shortcuts import render,redirect
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.template import loader
# Create your views here.
import MySQLdb
import datetime
import time
from django.views.decorators.csrf import csrf_exempt

# book
bookTableList = [
    "book_id",
    "ISBN",
    "book_name",
    "publisher",
    "author",
    "publish_date",
    "unit_price",
    "link",
    "book_rank",
    "book_class"]

# 库存表inventory
inventoryTableList = [
    "book_id",
    "location",
    "book_amount",
]

# 库存展示
inventoryDisplayList = [
    "book_id",
    "book_name",
    "author",
    "ISBN",
    "publisher",
    "publish_date",
    "location",
    "book_amount"
]

# 流水帐目表
billTableList = [
    "account_id",
    "create_time",
    "stop_time",
    "account_class",
    "amount",
    "account_reason",
    "operator",
    "bill_status"
]

# 流水账展示表
billDisplayList = billTableList

# 采编账目表
subscribeTableList = [
    "subscribe_id",
    "book_id",
    "subscribe_time",
    "supplier",
    "amount",
    "subscribe_status",
    "purchase_id"
]

# 采编展示表
subscribeDisplayList = [
    "subscribe_id",
    "book_id",
    "book_name",
    "subscribe_time",
    "supplier",
    "amount",
    "unit_price",
    "total_price",
    "subscribe_status",
    "purchase_id"
]

# 进货表
purchaseTableList = [
    "purchase_id",
    "purchase_time",
    "cost_label",
    "purchase_status",
    "operator",
    "account_id"
]

# 进货表展示list
purchaseDisplayList = purchaseTableList


# 流水账展示表

# 数据库连接
# db = MySQLdb.connect(host="192.168.221.133", user="root", passwd="123456", db="bookwarehouse", port=3306)


# 把字典中的日期value改成string
def dic2str(dic):
    for i in dic.keys():
        if isinstance(dic[i],datetime.datetime):  # 如果是时间戳类型
            dic[i] = dic[i].strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(dic[i], datetime.date):  # 如果是日期类型
            dic[i] = dic[i].strftime('%Y-%m-%d')

    return dic



# 从数据库里面取得的元组转成列表，列表元素为字典
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

# 执行sql语句
def sql_query(sql_statement, sql_param_list=[]):
    """
    执行sql语句，返回list[dictionary{}]结构，日期类型转为“xxxx-xx-xx”式的字符串
    :param sql_statement:string
    :param sql_param_list:list
    :return: list[dictionary{}]
    """
    with connection.cursor() as cursor:
        cursor.execute(sql_statement, sql_param_list)
        queryList = dictfetchall(cursor)
        for dic in queryList:  # 把时间日期类型转成字符串
            dic = dic2str(dic)
        return queryList



## 管理者登录
# 登录界面
def login(request):
    return render(request, "bookstore/manageLog.html")


# 提交登录信息
def login_submit(request):
    if request.method == "POST":
        manage_id = request.POST.get("manage_id") # 用户id
        manage_secret = request.POST.get("manage_secret")  # 用户密码
        input=[manage_id,manage_secret]
        # call 登录
        try:
            with connection.cursor() as cursor:
                cursor.callproc('manage_log',input)
                # 成功
                result = dictfetchall(cursor)
                if "info" in result[0]:  # 登录失败:
                    message=result[0]["info"]  # 失败消息
                    return render(request, "userApp/login.html", locals())
                else:
                    request.session['manage_id'] = result[0]["manage_id"]
                    request.session['manage_name'] = result[0]["manage_name"]
                    request.session['manage_secret']= result[0]["manage_secret"]
                    return redirect('index')  # 重定向到管理界面
        except BaseException:# 失败
            message = "系统错误！"
            return render(request,"bookstore/manageLog.html",locals())


####################图书信息界面################################
def index(request):
    with connection.cursor() as cursor:
        sqlquery = """SELECT book_id,ISBN,book_name,publisher,
        author,publish_date,unit_price,
        link,book_rank,book_class 
        FROM book"""
        cursor.execute(sqlquery)
        queryBookList = dictfetchall(cursor)

    for dic in queryBookList:  # 把时间日期类型转成字符串
        dic = dic2str(dic)
    # template = loader.get_template()
    context = {
        'queryBookList': queryBookList,
        'bookTableList': bookTableList,
    }
    return render(request, 'bookstore/index.html', context)


# 图书搜索查询
def search_book(request):
    if request.method == "POST":
        input_raw = []  # 储存图书信息 ,若没有输入某项查询，则值为空串""
        input_raw.append(request.POST.get("book_name"))  # 增添上图书信息的一个字段
        input_raw.append(request.POST.get("author"))  # 增添上图书信息的一个字段
        input_raw.append(request.POST.get("ISBN"))  # 增添上图书信息的一个字段

        # 执行sql语句
        with connection.cursor() as cursor:
            sqlquery = """SELECT *
            FROM book 
            WHERE book_name like '%%{}%%' and author like '%%{}%%' and ISBN like '%%{}%%';""".format(input_raw[0],
                                                                                                     input_raw[1],
                                                                                                     input_raw[2])
            cursor.execute(sqlquery)  # 执行sql语句
            queryBookList = dictfetchall(cursor)  # 取得执行结果

        for dic in queryBookList:  # 把时间日期类型转成字符串
            dic = dic2str(dic)
        template = loader.get_template('bookstore/index.html')  # 前端模板文件
        context = {  # 需要渲染到前端的数据
            'queryBookList': queryBookList,
            'bookTableList': bookTableList,
        }
        # 返回httpresponse 响应, 渲染前端
        return render(request, 'bookstore/index.html', context)


## 插入图书
def insert_book(request):
    if request.method == "POST":
        try:
            inputbook_raw = []  # 储存图书信息
            for name in bookTableList:
                inputbook_raw.append(request.POST.get(name))  # 增添上图书信息的一个字段
            # 未输入的值用None代替
            inputbook = [None if i == '' else i for i in inputbook_raw]
            sqlquery = "INSERT INTO book VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);"
            # 执行sql语句
            with connection.cursor() as cursor:
                cursor.execute(sqlquery, inputbook)
            return JsonResponse({"status": "0"})  # 插入成功
        except BaseException:
            return JsonResponse({"status": "1"})  # 插入失败


# 改图书信息
def modify_book(request):
    if request.method == "POST":
        try:
            inputbook_raw = []  # 储存图书信息
            for name in bookTableList:
                inputbook_raw.append(request.POST.get(name))  # 增添上图书信息的一个字段
            # 未输入的值用None代替
            modifybook = [None if i == '' else i for i in inputbook_raw]  # 输入的字段值
            sqlquery = """UPDATE book
                            SET 
                                ISBN=%s,
                                book_name=%s,
                                publisher=%s,
                                author=%s,
                                publish_date=%s,
                                unit_price=%s,
                                link=%s,
                                book_rank=%s,
                                book_class=%s
                                WHERE book_id=%s;"""
            modifybook.append(modifybook[0])  # 加上最后的book_id匹配参数
            # 执行sql语句
            with connection.cursor() as cursor:
                cursor.execute(sqlquery, modifybook)
            return JsonResponse({"status": "0"})  # 插入成功
        except BaseException:
            return JsonResponse({"status": "1"})  # 插入失败


# 删除图书信息
@csrf_exempt  # 屏蔽csrf（不安全）
def delete_book(request):
    if request.method == "POST":
        try:
            book_id = request.POST.get("book_id")

            sqlquery = """
            DELETE from book
            where book_id = %s
            """
            with connection.cursor() as cursor:
                cursor.execute(sqlquery, [book_id])
            return JsonResponse({"status": "0"})  # 删除成功
        except BaseException:
            return JsonResponse({"status": "1"})  # 删除失败

#########################inventory###############################
# inventory 页面：
def inventory(request):
    with connection.cursor() as cursor:
        sqlquery = """SELECT book_id,book_name,author,ISBN,publisher,publish_date,location,book_amount
        FROM inventory natural join book;"""
        cursor.execute(sqlquery)
        queryList = dictfetchall(cursor)

    for dic in queryList:  # 把时间日期类型转成字符串
        dic = dic2str(dic)
    template = loader.get_template('bookstore/inventory.html')
    context = {
        'queryList': queryList,
        'inventoryDisplayList': inventoryDisplayList,
        'inventoryTableList': inventoryTableList,
    }
    return HttpResponse(template.render(context, request))


# 插入库存
def insert_inventory(request):
    if request.method == "POST":
        try:
            input_raw = []  # 储存输入的库存信息
            for name in inventoryTableList:  # 对库存表中的每个属性
                input_raw.append(request.POST.get(name))  # 把增添的这一行库存信息储存进list中
            # 未输入的值用None代替
            input = [None if i == '' else i for i in input_raw]
            sqlquery = """
            INSERT INTO inventory
            VALUES(%s,%s,%s);"""
            # 执行sql语句
            with connection.cursor() as cursor:
                cursor.execute(sqlquery, input)
            return JsonResponse({"status": "0"})  # 插入成功
        except BaseException:
            return JsonResponse({"status": "1"})  # 插入失败


# 查询库存
def search_inventory(request):
    if request.method == "POST":
        input_raw = []  # 储存图书信息 ,若没有输入某项查询，则值为空串""
        input_raw.append(request.POST.get("book_name"))  # 增添上图书信息的一个字段
        input_raw.append(request.POST.get("author"))  # 增添上图书信息的一个字段
        # 馆藏：
        if request.POST.get("lib_list") == '所有馆藏':
            sqlquery = """SELECT *
        FROM book natural join inventory natural join library"""
        elif request.POST.get("lib_list") == '医科馆':  # 医科馆：
            sqlquery = """SELECT *
                    from med_lib_inventory"""
        elif request.POST.get("lib_list") == '理科馆':  # 理科馆：
            sqlquery = """SELECT *
                    from sci_lib_inventory"""
        else :  # 文科馆：
            sqlquery = """SELECT *
                    from arts_lib_inventory"""
        if input_raw[0] or input_raw[1]:
            sqlquery += """  WHERE book_name like '%%{}%%' and author like '%%{}%%' """.format(input_raw[0], input_raw[1])
        queryList = sql_query(sqlquery)  # 执行sql语句 取得所有项

        context = {
            'queryList': queryList,
            'inventoryDisplayList': inventoryDisplayList,
            'inventoryTableList': inventoryTableList,
        }
        return render(request, 'bookstore/inventory.html', context)


# 修改库存信息
def modify_inventory(request):
    if request.method == "POST":
        try:
            inputbook_raw = []  # 储存图书信息
            inputbook_raw.append(request.POST.get("book_amount"))  # 增添上图书信息的一个字段
            inputbook_raw.append(request.POST.get("book_id"))  # 增添上图书信息的一个字段
            inputbook_raw.append(request.POST.get("location"))  # 增添上图书信息的一个字段
            # 未输入的值用None代替
            modifybook = [None if i == '' else i for i in inputbook_raw]  # 输入的字段值
            sqlquery = """update inventory
                            set
                            book_amount=%s
                            WHERE (book_id, location)=(%s,%s);"""
            # 执行sql语句
            with connection.cursor() as cursor:
                cursor.execute(sqlquery, modifybook)
            return JsonResponse({"status": "0"})  # 插入成功
        except BaseException:
            return JsonResponse({"status": "1"})  # 插入失败


# 删除库存
@csrf_exempt  # 屏蔽csrf（不安全）
def delete_inventory(request):
    if request.method == "POST":
        try:
            book_id = request.POST.get("book_id")
            location = request.POST.get("location")
            sqlquery = """
            DELETE FROM inventory 
	WHERE(book_id, location )=(%s,%s);
            """
            with connection.cursor() as cursor:
                cursor.execute(sqlquery, [book_id, location])
            return JsonResponse({"status": "0"})  # 删除成功
        except BaseException:
            return JsonResponse({"status": "1"})  # 删除失败


#####################subscribe################################
## 采编界面
def subscribe(request):
    sqlquery = """
SELECT
	subscribe_id,
	book.book_id,
    book.book_name,
	subscribe_time,
	supplier,
	amount,
	unit_price,
	amount*unit_price as total_price,
	subscribe_status,
	purchase_id 
	from subscribe natural join book
"""
    sqlparam=[]  # sql 语句参数
    subscribe_status = request.POST.get("status")  # 取得查询内容
    if subscribe_status and subscribe_status != '全部采编':  # 存在状态检索
        sqlparam=[subscribe_status]
        sqlquery+="""  where subscribe_status=%s """

    queryList = sql_query(sqlquery,sqlparam)  # 执行
    context = {
        'queryList': queryList,
        'subscribeTableList': subscribeTableList,
        'subscribeDisplayList': subscribeDisplayList,
    }
    return render(request, 'bookstore/subscribe.html', context)



# 添加采编项
def insert_subscribe(request):
    if request.method == "POST":
        try:
            input_raw = []  # 储存输入的库存信息
            for name in ["book_id","supplier","amount"]:  # 对采编表中的每个属性
                input_raw.append(request.POST.get(name))  # 把增添的这一行库存信息储存进list中
            # 未输入的值用None代替
            input = [None if i == '' else i for i in input_raw]
            sqlquery = """
            INSERT INTO subscribe (book_id,supplier,amount) 
            values(%s,%s,%s);"""
            # 执行sql语句
            with connection.cursor() as cursor:
                cursor.execute(sqlquery, input)
            return JsonResponse({"status": "0"})  # 插入成功
        except BaseException:
            return JsonResponse({"status": "1"})  # 插入失败



# 删除采编项
@csrf_exempt  # 屏蔽csrf（不安全）
def delete_subscribe(request):
    if request.method == "POST":
        try:
            subscribe_id = request.POST.get("subscribe_id")
            sqlquery = """
            	delete from subscribe
            	where subscribe_id=%s
            """
            with connection.cursor() as cursor:
                cursor.execute(sqlquery, [subscribe_id])
            return JsonResponse({"status": "0"})  # 删除成功
        except BaseException:
            return JsonResponse({"status": "1"})  # 删除失败





# 提交采编计划
@csrf_exempt  # 屏蔽csrf（不安全）
def submit_subscribe(request):
    operator = request.session.get("manage_name")  # 操作者名字
    try:
        with connection.cursor() as cursor:
            cursor.callproc('subscribe_to_purchase',[operator])
        return JsonResponse({"status": "0"})  # 提交成功

    except BaseException:
        return JsonResponse({"status": "1"})  # 提交失败



####################purchase###################################
# 进货界面
def purchase(request):
    sqlquery = """
    SELECT
    purchase_id,
    purchase_time,
    cost_label,
    purchase_status,
    operator,
    account_id
    from purchase
    """

    sqlparam = []  # sql 语句参数
    subscribe_status = request.POST.get("status")  # 取得查询内容
    if subscribe_status and subscribe_status != '全部进货':  # 存在状态检索
        sqlparam = [subscribe_status]
        sqlquery += """  where purchase_status=%s """

    queryList = sql_query(sqlquery, sqlparam)  # 执行
    print(queryList[0])

    context = {
        'queryList': queryList,
        'subscribeTableList': purchaseTableList,
        'subscribeDisplayList': purchaseDisplayList,
    }
    return render(request, 'bookstore/purchase.html', context)


# 提交进货表
@csrf_exempt  # 屏蔽csrf（不安全）
def submit_purchase(request):
    purchase_id= request.POST.get("purchase_id")
    account_reason = request.POST.get("account_reason")  # 提交说明
    try:
        with connection.cursor() as cursor:
            cursor.callproc('submit_purchase',[purchase_id,account_reason])
        return JsonResponse({"status": "0"})  # 提交成功

    except BaseException:
        return JsonResponse({"status": "1"})  # 提交失败


# 取消进货表
@csrf_exempt  # 屏蔽csrf（不安全）
def cancel_purchase(request):
    purchase_id = request.POST.get("purchase_id")
    operator = request.session.get("manage_name")  # 操作者名字
    sqlquery="""
    update purchase
set purchase_status = "已取消",operator=%s
where purchase_id = %s;
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(sqlquery,[operator,purchase_id])
        return JsonResponse({"status": "0"})  # 成功

    except BaseException:
        return JsonResponse({"status": "1"})  # 失败


####################finance###################################

## 财务管理界面
def finance(request):
    sqlquery = """
    SELECT *
    from bill
    """

    sqlparam = []  # sql 语句参数
    subscribe_status = request.POST.get("status")  # 取得查询内容
    if subscribe_status and subscribe_status != '全部流水':  # 存在状态检索
        sqlparam = [subscribe_status]
        sqlquery += """  where bill_status=%s """

    queryList = sql_query(sqlquery, sqlparam)  # 执行

    context = {
        'queryList': queryList,
        'billTableList': billTableList,
        'billDisplayList': billDisplayList,
    }
    return render(request, 'bookstore/finance.html', context)


# 确认收货
@csrf_exempt  # 屏蔽csrf（不安全）
def confirm_receipt(request):
    purchase_id = request.POST.get("purchase_id")
    operator = request.session.get("manage_name")  # 操作者名字
    sqlquery = """
        update purchase
    set purchase_status = "已完成",operator=%s
    where purchase_id = %s;
        """
    try:
        with connection.cursor() as cursor:
            cursor.execute(sqlquery, [operator,purchase_id])
        return JsonResponse({"status": "0"})  # 成功

    except BaseException:
        return JsonResponse({"status": "1"})  # 失败




# 支付某笔流水
@csrf_exempt  # 屏蔽csrf（不安全）
def pay_bill(request):
    account_id = request.POST.get("account_id")
    operator = request.session.get("manage_name")  # 操作者
    sqlquery = """
        update bill
set stop_time = CURRENT_TIMESTAMP,operator = %s,bill_status = "已支付"
where account_id=%s;"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(sqlquery, [operator,account_id])
        return JsonResponse({"status": "0"})  # 成功

    except BaseException:
        return JsonResponse({"status": "1"})  # 失败


# 取消某笔流水
@csrf_exempt  # 屏蔽csrf（不安全）
def cancel_bill(request):
    account_id = request.POST.get("account_id")
    operator = request.session.get("manage_name")  # 操作者
    sqlquery = """
            update bill
set stop_time = CURRENT_TIMESTAMP,operator = %s,bill_status = "已取消"
where account_id=%s;"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(sqlquery, [operator,account_id])
        return JsonResponse({"status": "0"})  # 成功

    except BaseException:
        return JsonResponse({"status": "1"})  # 失败

# 收取金钱
@csrf_exempt  # 屏蔽csrf（不安全）
def receive_money(request):
    account_id = request.POST.get("account_id")
    operator = request.session.get("manage_name")  # 操作者
    sqlquery = """
            update bill
set stop_time = CURRENT_TIMESTAMP,operator = %s,bill_status = "已支付"
where account_id=%s;"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(sqlquery, [operator,account_id])
        return JsonResponse({"status": "0"})  # 成功

    except BaseException:
        return JsonResponse({"status": "1"})  # 失败

##################用户管理#########################
def user(request):
    sqlquery = """
    SELECT student_id,student_name,student_integrity
    from student
    """

    sqlparam = []  # sql 语句参数
    student_id = request.POST.get("student_id")  # 取得查询内容
    student_name = request.POST.get("student_name")  # 取得查询内容
    if student_id or student_name:  # 存在状态检索
        sqlparam = [student_id,student_name]
        sqlquery += """  where student_id=%s or student_name=%s """

    queryList = sql_query(sqlquery, sqlparam)  # 执行

    context = {
        'queryList': queryList,
    }
    return render(request, 'bookstore/user.html', context)

# 删除学生
@csrf_exempt  # 屏蔽csrf（不安全）
def delete_user(request):
    if request.method == "POST":
        try:
            student_id = request.POST.get("student_id")
            sqlquery = """
                delete from student
                where student_id=%s
            """
            with connection.cursor() as cursor:
                cursor.execute(sqlquery, [student_id])
            return JsonResponse({"status": "0"})  # 删除成功
        except BaseException:
            return JsonResponse({"status": "1"})  # 删除失败