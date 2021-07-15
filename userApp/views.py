from django.shortcuts import render, reverse, redirect
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.template import loader
# Create your views here.
import MySQLdb
import datetime
import time
from django.views.decorators.csrf import csrf_exempt

# 读者图书查询展示图书表
readSearchDisplayList = [
    "book_id",
    "ISBN",
    "book_name",
    "publisher",
    "author",
    "publish_date",
    "link",
    "book_rank",
    "book_class",
    "location",
    "book_status"
]


# 把字典中的日期value改成string
def dic2str(dic):
    for i in dic.keys():
        if isinstance(dic[i], datetime.date):  # 如果是日期类型
            dic[i] = dic[i].strftime('%Y-%m-%d')
        # if type(dic[i])== "timestamp":
        #     dic[i]= dic[i].strftime('%Y-%m-%d',time.localtime())
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


# 登录界面
def login(request):
    return render(request, "userApp/login.html")


# 提交登录信息
def login_submit(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")  # 用户id
        student_secret = request.POST.get("student_secret")  # 用户密码
        input = [student_id, student_secret]
        # call 登录
        try:
            with connection.cursor() as cursor:
                cursor.callproc('stu_log', input)
                # 成功
                result = dictfetchall(cursor)
                if "info" in result[0]:  # 登录失败:
                    message = result[0]["info"]  # 失败消息
                    return render(request, "userApp/login.html", locals())
                else:  # 储存登录者信息在会话中
                    request.session['student_id'] = result[0]["student_id"]
                    request.session['student_name'] = result[0]["student_name"]
                    request.session['student_integrity'] = result[0]["student_integrity"]
                    request.session['student_secret'] = result[0]["student_secret"]
                    return redirect('selfInfo')  # 重定向到个人信息界面
        except BaseException:  # 失败
            message = "系统错误！"
            return render(request, "userApp/login.html", locals())


# 注册界面
def signin(request):
    return render(request, 'userApp/signin.html')


# 提交注册信息
def signin_submit(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        student_name = request.POST.get("student_name")
        student_secret = request.POST.get("student_secret")
        input = [student_id, student_name, student_secret]
        try:
            # call 注册
            with connection.cursor() as cursor:
                cursor.callproc('stu_register', input)  # 调用sql过程
            message = "注册成功！"
            return render(request, "userApp/signin.html", locals())
        except BaseException:
            message = "注册失败！"
            return render(request, "userApp/signin.html", locals())


# 个人信息界面
def self_info(request):
    return render(request, 'userApp/index.html', locals())


# 修改密码
def modify_password(request):
    if request.method == "POST":
        sqlquery = """
        update student
Set student_secret=MD5(%s)
where student_id=%s;
        """
        old_secret = request.POST.get("old_secret")
        new_secret = request.POST.get("new_secret")
        input = [new_secret, request.session.get("student_secret")]
        if old_secret == request.session.get("student_secret"):  # 原密码正确
            # try:
            # call 注册
            with connection.cursor() as cursor:
                cursor.execute(sqlquery, input)
            message = "修改成功！"
            request.session["student_secret"] = new_secret  # 修改当前会话密码
            return render(request, "userApp/index.html", locals())
            # return redirect('selfInfo')
        # except BaseException:
        #     message = "修改失败！"
        #     return render(request,"userApp/index.html",locals())
        else:  # 原密码不对
            message = "原密码不对！"
            return render(request, "userApp/index.html", locals())


# 流通界面 # 在借阅
def circulate(request):
    # 在借阅
    sqlquery = """
    select borrow_on_id,book_name,author,publish_date,borrow_date,date_add(borrow_date,interval (90+continue_date) day) as due_date,continue_date
from borrow_on natural join borrow natural join book 
where student_id =%s;
    """

    queryOnBorrowList = sql_query(sqlquery, [request.session.get("student_id")])
    # 借阅历史
    sqlquery = """
        select book_name,ISBN,author,publisher,borrow_date,continue_date,return_date,location
    from borrow natural join book natural join return_b natural join inventory
    where student_id=%s;
    """
    queryMyBorrowList = sql_query(sqlquery, [request.session.get("student_id")])
    # 罚单
    sqlquery = """
         select fine_id,book_name,author,publish_date,fine_fine,bill_status
    from fine natural join borrow natural join book natural join bill
    where student_id=%s
        """

    input_raw = []  # 储存sql参数""
    input_raw.append(request.POST.get("bill_status"))  # bill_status

    if input_raw[0] == '待付款' or input_raw[0] == '已支付':
        # sql 语句
        sqlquery += """
                      and  bill_status=%s"""
        queryFineList = sql_query(sqlquery, [request.session.get("student_id"), input_raw[0]])
    else:
        queryFineList = sql_query(sqlquery, [request.session.get("student_id")])
    context = {
        'queryOnBorrowList': queryOnBorrowList,
        'queryMyBorrowList': queryMyBorrowList,
        'queryFineList': queryFineList,
    }
    return render(request, 'userApp/circulate.html', context)


# 查询界面
def search(request):
    input_raw = []  # 储存图书信息 ,若没有输入某项查询，则值为空串""
    input_raw.append(request.POST.get("book_name"))  # book_name
    input_raw.append(request.POST.get("author"))  # 增添上图书信息的一个字段
    input_raw.append(request.POST.get("ISBN"))  # 增添上图书信息的一个字段
    # 馆藏：

    sqlquery = """SELECT book_id,
    ISBN,
    book_name,
    publisher,
    author,
    publish_date,
    link,
    book_rank,
    book_class,
    location,
    book_amount
                    FROM book natural join inventory natural join library"""
    if input_raw[0] != None:  # 如果用户输入了检索数据
        # sql 语句
        sqlquery += """
                        WHERE book_name like '%%{}%%' and author like '%%{}%%' and ISBN like '%%{}%%' """.format(
            input_raw[0],
            input_raw[1], input_raw[2])

    queryList = sql_query(sqlquery)  # 执行sql语句 取得所有项
    context = {
        'queryList': queryList,
        'readSearchDisplayList': readSearchDisplayList,
    }
    return render(request, 'userApp/search.html', context)


# 借一本书
@csrf_exempt  # 屏蔽csrf（不安全）
def borrow(request):
    if request.method == "POST":
        book_id = request.POST.get("book_id")  # 用户id
        location = request.POST.get("location")  # 用户密码
        student_id = request.session.get("student_id")
        # call 借书
        with connection.cursor() as cursor:
            cursor.callproc('proc_borrow', [student_id, book_id, location])
            result = dictfetchall(cursor)
            if "info" in result[0]:  # 借阅失败:
                message = result[0]["info"]  # 失败消息
                # 失败
                return JsonResponse({"status": "1", "message": message})  # 失败
            else:
                # 成功
                return JsonResponse({"status": "0"})  # 成功


# 续借一本书
@csrf_exempt  # 屏蔽csrf（不安全）
def continue_borrow(request):
    if request.method == "POST":
        borrow_on_id = request.POST.get("borrow_on_id")  # 用户id
        # call 续借
        # try:
        with connection.cursor() as cursor:
            cursor.callproc('proc_continue', [borrow_on_id])

        return JsonResponse({"status": "0"})  # 成功
        # except BaseException:
        # return JsonResponse({"status": "1"})  # 失败


# 还一本书
@csrf_exempt  # 屏蔽csrf（不安全）
def return_book(request):
    if request.method == "POST":
        borrow_on_id = request.POST.get("borrow_on_id")  # 外借编号
        # call 借书
        with connection.cursor() as cursor:
            cursor.callproc('proc_return', [borrow_on_id])
            result = dictfetchall(cursor)
            if "info" in result[0]:  # 借阅失败:
                message = result[0]["info"]  # 失败消息
                # 失败
                return JsonResponse({"status": "1", "message": message})  # 失败
            else:
                # 成功
                message = result[0]["succ"]  # 成功消息
                return JsonResponse({"status": "0", "message": message})  # 成功


# 支付罚款
@csrf_exempt  # 屏蔽csrf（不安全）
def pay_fine(request):
    if request.method == "POST":
        fine_id = request.POST.get("fine_id")  # 外借编号
        # call 借书
        try:
            with connection.cursor() as cursor:
                cursor.callproc('proc_payoff', [fine_id])
                result = dictfetchall(cursor)

                message = "支付失败"  # 失败消息
                # 失败
                return JsonResponse({"status": "1", "message": message})  # 失败
        except BaseException:
            # 成功
            message = "支付成功 "  # 成功消息
            return JsonResponse({"status": "0", "message": message})  # 成功
