--------------------创建表-----------------------------
--------------------库存管理和财务管理--------------------
--book(邓睿君)
CREATE TABLE book(
	book_id bigint primary key auto_increment,
	ISBN	varchar(13),
	book_name varchar(20) not null,
	publisher varchar(20),
	author varchar(20),
	publish_date date,
	unit_price decimal(9,2),
	link tinytext,
	book_rank decimal(2,1),
	book_class varchar(10),
	check (book_rank between 0 and 10),
	check (book_class in ("文学艺术",
"政治经济",
"军事法律",
"哲学宗教",
"数学物理",
"化学生物",
"机械能源",
"信息电脑",
"建筑交通",
"医学药学"))
)auto_increment = 0;

-- purchase(邓睿君)
CREATE TABLE purchase(
purchase_id bigint primary key auto_increment,
purchase_time timestamp default current_timestamp ,
cost_label decimal(9,2) not null,
purchase_status varchar(3) default "待提交",
operator varchar(20),
account_id bigint,
foreign key(account_id) references bill(account_id),
check (purchase_status in (
"待提交",
"待付款",
"处理中",
"已取消",
"已完成"
))
)auto_increment = 0;

-- subscribe(邓睿君)
CREATE TABLE subscribe(
subscribe_id bigint primary key auto_increment,
book_id bigint,
subscribe_time timestamp default current_timestamp,
supplier varchar(20),
amount integer,
subscribe_status varchar(3) default "未提交",
purchase_id bigint,
foreign key(book_id) references book(book_id),
foreign key(purchase_id) references purchase(purchase_id),
check (subscribe_status in ("未提交","已提交"))
)auto_increment = 0;

-- inventory(邓睿君)
CREATE TABLE inventory(
book_id bigint,
location varchar(20),
book_amount integer,
primary key(book_id,location),
foreign key(book_id) REFERENCES book(book_id),
foreign key(location) REFERENCES library(location),
check (book_amount>0)
);

-- 图书馆建筑(library)(邓睿君)
create table library(
  location varchar(20) primary key,
  branch_lib varchar(3) not null,
  check(branch_lib in ("文科馆","理科馆","医科馆"))
);

-- bill(邓睿君)
CREATE TABLE bill(
account_id bigint primary key auto_increment,
create_time timestamp default current_timestamp ,
stop_time timestamp,
account_class varchar(10),
amount decimal(9,2),
account_reason text,
operator varchar(20),
bill_status varchar(3),
check( account_class in ("采购图书","违规罚款")),
check( bill_status in ("待付款","已支付","已取消","待收款","已收款"))
)auto_increment = 0;

--------------------------用户管理和流通借还-----------------------------------
-- borrow
CREATE TABLE borrow(
borrow_id bigint primary key auto_increment,
student_id varchar(11),
book_id bigint,
borrow_date timestamp default current_timestamp,
foreign key(student_id) references student(student_id),
foreign key(book_id) references book(book_id),
continue_date int default 0
)auto_increment = 0;
-- student
CREATE TABLE student(
student_id varchar(11) primary key,
student_name varchar(20) not null,
student_secret varchar(32) not null,
student_integrity int default 30,
check (student_integrity>=0)
);
-- manage
CREATE TABLE manage(
manage_id varchar(7) primary key,
manage_name varchar(20) not null,
manage_secret varchar(32) not null
);
-- borrow_on
CREATE TABLE borrow_on(
borrow_on_id bigint primary key auto_increment,
borrow_id bigint,
foreign key (borrow_id) references borrow(borrow_id)
)auto_increment = 0;
-- return_b
CREATE TABLE return_b(
return_id bigint primary key auto_increment,
borrow_id bigint,
return_date timestamp default current_timestamp,
foreign key (borrow_id) references borrow(borrow_id)
)auto_increment = 0;
-- fine
CREATE TABLE fine(
fine_id bigint primary key auto_increment,
borrow_id bigint,
fine_fine decimal(9,2) default 0,
account_id bigint,
foreign key (borrow_id) references borrow(borrow_id),
foreign key (account_id) references bill(account_id)
)auto_increment = 0;


---------------------------视图-----------------------------
-- 医科馆库存视图(邓睿君)
create or replace view med_lib_inventory(
book_id,
ISBN,
book_name,
publisher,
author,
publish_date,
unit_price,
link,
book_rank,
book_class,
location,
book_amount,
branch_lib
)as
select
book_id,
ISBN,
book_name,
publisher,
author,
publish_date,
unit_price,
link,
book_rank,
book_class,
location,
book_amount,
branch_lib
from book natural join inventory natural join library
where branch_lib = "医科馆";
-- 文科馆库存视图(邓睿君)
create or replace view arts_lib_inventory(
book_id,
ISBN,
book_name,
publisher,
author,
publish_date,
unit_price,
link,
book_rank,
book_class,
location,
book_amount,
branch_lib
)as
select book_id,
ISBN,
book_name,
publisher,
author,
publish_date,
unit_price,
link,
book_rank,
book_class,
location,
book_amount,
branch_lib
from book natural join inventory natural join library
where branch_lib = "文科馆";
-- 理科馆库存视图(邓睿君)
create or replace view sci_lib_inventory(
book_id,
ISBN,
book_name,
publisher,
author,
publish_date,
unit_price,
link,
book_rank,
book_class,
location,
book_amount,
branch_lib
)as
select book_id,
ISBN,
book_name,
publisher,
author,
publish_date,
unit_price,
link,
book_rank,
book_class,
location,
book_amount,
branch_lib
from book natural join inventory natural join library
where branch_lib = "理科馆";

-- 图书利用情况视图(邓睿君)
-- 图书id，年份，借阅次数
-- 按照借阅次数排序
create or replace view borrow_statistic(
book_id,
borrow_duration,
borrow_times
)as
select T.book_id,T.borrow_duration,count(book_id) as borrow_times
from (select book_id,EXTRACT(year from borrow.borrow_date)as borrow_duration
from borrow) as T
GROUP BY book_id,T.borrow_duration
ORDER BY borrow_times desc;

-- 待支付账单视图(邓睿君)
create or replace view bills_to_pay(account_id,
create_time,
account_class,
amount,
account_reason)
as
select
account_id,
create_time,
account_class,
amount,
account_reason
from bill
where bill_status = "待支付";


------------------------------系统配置------------------------
set global log_bin_trust_function_creators=TRUE;

--------------------------------数据------------------------------(叶鑫茹)
-- student 信息(叶鑫茹)
insert into student(student_id,student_name,student_secret)
values('19307130360','叶鑫茹',MD5('123456')),
('19307130361','甲',MD5('1234567')),
('19307130362','乙',MD5('1234568')),
('19307130363','丙',MD5('1234569')),
('19307130364','丁',MD5('12345610'));

-- manage 信息(叶鑫茹)
insert into manage(manage_id,manage_name,manage_secret)
values('1','admin',MD5('123456'));

-- book 信息(叶鑫茹)
insert into book(ISBN,book_name,publisher,author,publish_date,unit_price,book_class)
values('9787500159919','微表情心理学','北京中译出版社','王雄','2019-01-03','149.00','文学艺术'),
('9787520523608','新兵','北京中国文史出版社','北桥','2021-01-03','49.80','哲学宗教'),
('9787502486969','生物化学','北京冶金工业出版社','常雁红','2021-01-03','42.00','化学生物'),
('9787302573746','操作系统本质','北京清华大学出版社','陈鹏','2021-01-03','59.00','信息电脑'),
('9787500159915','表情心理学','北京中译出版社','王雄','2021-01-03','129.00','文学艺术');

-- inventory 信息(叶鑫茹)
INSERT INTO inventory
VALUES('1','文科综合书库',2),
('2','文学艺术书库',2),
('3','文科过刊库',2),
('4','期刊工作室',2),
('5','理科应用学科阅览室',2);

-- library 信息(叶鑫茹)
insert into library(location,branch_lib)
values('文科综合书库','文科馆'),
('文学艺术书库','文科馆'),
('文科过刊库','文科馆'),
('政经法阅览室','文科馆'),
('理科基础学科阅览室','理科馆'),
('理科应用学科阅览室','理科馆'),
('期刊工作室','医科馆'),
('复旦人著作陈列室','理科馆'),
('上医人文库','医科馆');

-----------------------函数和过程----------------------------
--------------用户管理---------------
-- 管理员登录验证:(叶鑫茹)
-- 输入：用户名、密码
-- 输出：提示错误语句或管理员信息(ID,姓名,密码)
-- 输入管理员id（manage_id）,登陆密码（manage_secret)，在manage表中查找，找到则成功登陆，失败则报错
CREATE DEFINER=`root`@`%` PROCEDURE `manage_log`(in manage_id varchar(11),in manage_secret varchar(20))
begin
-- 不存在该管理员(叶鑫茹)
if(not exists (select manage_id
from manage
where manage_id=manage.manage_id)) then
select 'not exists this id,please register first' as info;
else
-- 登陆密码错误(叶鑫茹)
if (not exists (select manage_id
from manage
where manage_id=manage.manage_id and MD5(manage_secret)=manage.manage_secret)) then
select 'secret is wrong,please cheak it' as info;
else
-- 返回管理者名字(叶鑫茹)
select manage_id,manage_name,manage_secret
from manage
where manage_id=manage.manage_id;
end if;
end if;
end



--用户登录(叶鑫茹)
-- 输入：用户名、密码
-- 输出：提示错误语句或用户信息(ID,姓名,诚信度,密码)
CREATE DEFINER=`root`@`%` PROCEDURE `stu_log`(in student_id varchar(11),in student_secret varchar(16))
begin
if(not exists (select student_id
from student
where student_id=student.student_id)) then
select 'not exists this id,please register first' as info;
else
if (not exists (select student_secret
from student
where student.student_id=student_id and MD5(student_secret)=student.student_secret)) then
select 'secret is wrong,please cheak it' as info;
else
select student_id,student_name,student_integrity,student_secret
from student
where student.student_id=student_id;
end if;
end if;
end


-- 修改用户密码 存密码的hash值（MD5算法）(叶鑫茹)
update student
Set student_secret=MD5(%s)
where student_id=%s;

-- 管理员查看用户信息(叶鑫茹)
SELECT student_id,student_name,student_integrity
from student

-- 管理员删除学生信息(叶鑫茹)
delete from student
where student_id=%s

-- 用户注册（管理员是系统开始时就写入数据库的）(叶鑫茹)
CREATE DEFINER=`root`@`%` PROCEDURE `stu_register`(in student_id varchar(11),in student_name varchar(20),in student_secret varchar(16))
begin
insert into student(student_id,student_name,student_secret)
values(student_id,student_name,MD5(student_secret));
select 'succeed';
end


---------------流通借还---------------------(叶鑫茹)
-- 查看当前用户正在借阅中的书
select borrow_on_id,book_name,author,publish_date,borrow_date,date_add(borrow_date,interval (90+continue_date) day) as due_date,continue_date
from borrow_on natural join borrow natural join book
where student_id =%s;

-- 查看当前用户借阅历史
select book_name,ISBN,author,publisher,borrow_date,continue_date,return_date,location
from borrow natural join book natural join return_b natural join inventory
where student_id=%s;

-- 查看当前用户罚单（可检索罚单状态）
select fine_id,book_name,author,publish_date,fine_fine,bill_status
from fine natural join borrow natural join book natural join bill
where student_id=%s and bill_status=%s

-- 用户查询图书信息
SELECT book_id,
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
FROM book natural join inventory natural join library


-- 用户借书
-- 返回用户诚信度
CREATE DEFINER=`root`@`%` FUNCTION `func_integrity`(student_id varchar(11)) RETURNS int
begin
declare s_integrity integer;
select student_integrity into s_integrity
from student
where student_id=student.student_id;
return s_integrity;
end


-- 书籍库存量是否>0
CREATE DEFINER=`root`@`%` FUNCTION `func_amount`(book_id bigint,location varchar(20)) RETURNS int
begin
declare b_amount integer;
select book_amount into b_amount
from inventory
where inventory.book_id=book_id and location=inventory.location;
return b_amount;
end

--  borrow 表插入一条元组 表示一条借阅记录
--  返回：新插记录的borrow_id
CREATE DEFINER=`root`@`%` FUNCTION `insert_borrow`(
student_id varchar(11),
book_id bigint) RETURNS bigint
BEGIN
insert into borrow(student_id,book_id)
values(student_id,book_id);
return LAST_INSERT_ID();
END

-- 借书存储过程proc_borrow,
-- 若学生的诚信度大于0和借的书库存量大于0，
-- 则向borrow表插入一条记录，否则提示对应的错误。
-- （借书存储过程，
-- 输入学生id，书籍id,借书时间：为当前操作时间；
-- 若书籍数量和诚信度大于0，向borrow,borrow_on表中插入一条记录,修改库存数量，
-- 否则抛出异常）
CREATE DEFINER=`root`@`%` PROCEDURE `proc_borrow`(in student_id varchar(11), in book_id bigint,in location varchar(20))
begin
-- 信用不够
declare b_i bigint;
if(func_integrity(student_id)=0) then
select 'No credits,please try again 30 days later' as info;
else
-- 没有库存了
if(func_amount(book_id,location)=0) then
select 'no book on the bookshelves' as info;
-- borrow中插入记录
else
set b_i=insert_borrow(student_id,book_id);
-- borrow_on中插入记录
insert into borrow_on(borrow_id)
values(b_i);
-- 库存表对应图书数量减1
update inventory
set book_amount=book_amount-1
where book_id=inventory.book_id and location=inventory.location;
-- 借书成功消息
select 'succeed borrow!' as succ;
end if;
end if;
end


--续借一本书
CREATE DEFINER=`root`@`%` PROCEDURE `proc_continue`(in b_o_id bigint)
begin
-- 从borrow_on_id 找 borrow_id
declare b_id bigint;
select borrow_id into b_id
from borrow_on
where borrow_on_id = b_o_id;
-- 增加续借时间
update borrow
set borrow.continue_date=30
where borrow.borrow_id=b_id;
end


-- 还书
-- 返回罚单支付状态
CREATE DEFINER=`root`@`%` FUNCTION `func_pay`(b_id bigint) RETURNS varchar(3) CHARSET utf8mb4
begin
declare b_s varchar(3);
select bill_state into b_s
from bill natural join fine
where b_id=borrow_id;
return b_s;
end



-- 还书过程proc_return，
-- 若还书时间超过预期还书时间,定时器产生罚单，
-- 提示先交完罚单后还书，
-- 之后在还书表return中插入一条记录（输入借阅编号），
-- 修改库存，删除borrow_on表
CREATE DEFINER=`root`@`%` PROCEDURE `proc_return`(in b_o_id bigint)
begin
-- 从borrow_on_id 取得 borrow_id
declare b_id bigint;
select borrow_id into b_id
from borrow_on
where borrow_on_id = b_o_id;
--  存在罚单且未支付，提示先交罚单
if(exists(select borrow_id
from fine
where b_id=fine.borrow_id)
and(func_pay(b_id)='待付款')) then
select 'please pay off the fine first' as info;
else
-- return 表中插入记录
insert into return_b(borrow_id)
values(b_id);
-- 删除borrow_on表
delete from borrow_on
where b_id=borrow_on.borrow_id;
-- 修改库存
update inventory
set book_amount=book_amount+1
where inventory.book_id=(select book_id
from borrow
where borrow.borrow_id=b_id);

select "succeeded return!" as succ;
end if;
end


-- 支付罚款
CREATE DEFINER=`root`@`%` PROCEDURE `proc_payoff`(in f_id bigint)
begin
update bill
set bill_status="已支付" ,stop_time=current_timestamp
where bill.account_id=(select account_id
from fine
where fine.fine_id=f_id);
end


-- 罚单定时生成事件；
-- 定时器（timeclock),每天自动触发一次,
-- 当发现当前的预期归还时间小于当前时间，生成罚单（定时触发proc_gen_fine)
drop event if exists timeclock;
create event timeclock
on schedule every 1 day
on completion preserve disable
do
call proc_gen_fine();
set global event_scheduler=1;
alter event timeclock on completion preserve enable;


-- bill中插入罚单流水
CREATE DEFINER=`root`@`%` PROCEDURE `insert_bill_fine`(in fine decimal(9,2),in b_i bigint,in s_id varchar(11))
begin
declare a_i bigint;
-- 插入bill
insert into bill(account_class,amount,bill_status)
values('违规罚款',fine,'待付款');
set a_i=LAST_INSERT_ID();
-- 插入fine
insert into fine(borrow_id,fine_fine,account_id)
values(b_i,fine,a_i);
-- 学生信用减1
update student
set student_integrity=student_integrity-1
where student_id=s_i;
end


-- 罚单生成
-- 当当前日期超出归还时间90天，fine,bill表中新增一条记录。
-- 在bill、fine表中插入记录
CREATE DEFINER=`root`@`%` PROCEDURE `proc_gen_fine`()
begin
declare s_i varchar(11);
declare a_i,b_i bigint;
declare fine_fee_1 decimal(9,2);
-- 游标结束标志
declare done int default 0;
-- 定义游标cur
declare cur cursor for select student_id, borrow_id,0.1*(datediff(borrow_date,'2021-05-03 12:21:12')-continue_date)
from borrow_on natural join borrow natural join student
where (datediff(borrow_date,'2021-05-03 12:21:12')-continue_date)>0;
-- 指定游标循环结束时的返回值
declare continue handler for not found set done = 1;
open cur;
-- while 循环
while done!=1 do
fetch cur into s_i,b_i,fine_fee_1;
-- 插入bill
if(exists (select borrow_id
from fine
where borrow_id=b_i)) then
update bill
set amount=fine_fee_1
where account_id=(select account_id
from fine
where borrow_id=b_i);
update fine
set fine_fine=fine_fee_1
where borrow_id=b_i;
else
call insert_bill_fine(fine_fee_1,b_i,s_i);
end if;
end while;
-- 关闭游标
close cur;
end

------------------------库存管理和财务管理-----------------(邓睿君)
-- 图书信息查询
SELECT book_id,ISBN,book_name,publisher,
        author,publish_date,unit_price,
        link,book_rank,book_class
        FROM book

-- 图书信息查询(带上搜索信息)
SELECT *
FROM book
WHERE book_name like '%%{}%%' and author like '%%{}%%' and ISBN like '%%{}%%';


-- 插入图书
INSERT INTO book VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);

-- 修改图书信息
UPDATE book
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
WHERE book_id=%s;

-- 删除图书信息
DELETE from book
where book_id = %s;

-- 库存查询
SELECT book_id,book_name,author,ISBN,publisher,publish_date,location,book_amount
FROM inventory natural join book;

-- 库存查询(带上搜索)
SELECT *
FROM book natural join inventory natural join library
WHERE book_name like '%%{}%%' and author like '%%{}%%' and branch_lib=%s

-- 查看各馆馆藏

-- 插入库存
INSERT INTO inventory
VALUES(%s,%s,%s);


-- 修改库存信息
update inventory
set
book_amount=%s
WHERE (book_id, location)=(%s,%s);


-- 删除库存信息
DELETE FROM inventory
WHERE(book_id, location )=(%s,%s);


-- 查询采编项
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
where subscribe_status=%s


-- 添加采编项
INSERT INTO subscribe (book_id,supplier,amount)
values(%s,%s,%s);



-- 删除采编项
delete from subscribe
where subscribe_id=%s


-- 提交采编项
CREATE DEFINER=`root`@`%` PROCEDURE `subscribe_to_purchase`(in op varchar(20))
BEGIN
-- 计算采编的总金额
declare cost decimal(9,2);
declare pur_id bigint;
select sum(total_price) into cost
					from (select unit_price*amount as total_price
									from subscribe natural join book
									where subscribe_status='未提交') as T;
-- 插入进货表一行
insert into purchase(cost_label,operator)
values(cost,op);
-- 取得刚插入的id
set pur_id =  LAST_INSERT_ID();
-- 更新采编表的进货编号
update subscribe
set subscribe.purchase_id = pur_id
where subscribe.subscribe_status = '未提交';
-- 更新采编表的状态
update subscribe
set subscribe.subscribe_status='已提交'
where subscribe.subscribe_status = '未提交';
END


-- 查询进货项
SELECT
purchase_id,
purchase_time,
cost_label,
purchase_status,
operator,
account_id
from purchase
where purchase_status=%s



-- 提交进货表
CREATE DEFINER=`root`@`%` PROCEDURE `submit_purchase`(
in p_id BIGINT,
in a_r text
)
BEGIN
declare a_id BIGINT;
declare c_l decimal(9,2);
-- 取得进货编号对应的进货记录/元组的应付金额,储在变量中
select cost_label into c_l from purchase where purchase.purchase_id = p_id;
-- 流水账目表插入一个元组,取得返回值账目编号
set a_id = insert_bill("采购图书", c_l, a_r, "待付款");
-- 进货表修改账目编号属性
-- 把所有的待提交的purchase元组的状态都改为待付款
Update purchase
set purchase_status="待付款", account_id=a_id
where purchase_id = p_id;
END


-- 取消进货
update purchase
set purchase_status = "已取消",operator=%s
where purchase_id = %s;


-- 查看财务流水
SELECT *
from bill
where bill_status=%s


-- 确认收货
update purchase
set purchase_status = "已完成",operator=%s
where purchase_id = %s;


-- 支付某笔流水
update bill
set stop_time = CURRENT_TIMESTAMP,operator = %s,bill_status = "已支付"
where account_id=%s;


-- 取消某笔流水
update bill
set stop_time = CURRENT_TIMESTAMP,operator = %s,bill_status = "已取消"
where account_id=%s;


-- 收款
update bill
set stop_time = CURRENT_TIMESTAMP,operator = %s,bill_status = "已支付"
where account_id=%s;

-- 插入一条bill记录
-- 输入:账目类别，金额，缘由(采购图书,违规罚款),状态(待付款,已支付,已取消)
-- 返回：插入的该账目的账目编号
-- 功能:插入一条流水账，时间为当前时间,返回刚插入的记录的账目编号
CREATE DEFINER=`root`@`%` FUNCTION `insert_bill`(a_c varchar(10),b_a decimal(9,2),a_r text,b_s varchar(3)) RETURNS bigint
BEGIN
INSERT INTO bill(
account_class,
amount,
account_reason,
bill_status
)
VALUES
	(a_c , b_a, a_r, b_s );

return LAST_INSERT_ID();
END



-- 触发器：当对应的订单被支付，则修改进货单中对应元组的状态从"待支付"为"处理中"
create trigger purchase_in_process after update
on bill
for each row
BEGIN
-- 如果是支付了该采购图书订单
if (new.account_class='采购图书'and new.bill_status='已支付')
 -- 修改对应进货单的状态为"处理中"
then
update purchase
set purchase_status = "处理中"
where purchase.account_id = new.account_id;
end if;
-- 还要把“确认收货展示出来”
END;

-----------------------数据库服务器配置--------------------------(邓睿君)

-- 数据库服务器授权远程用户
-- 在开发环境下，这里为了方便，允许所有的ip访问数据库，
-- 但在生产环境下这样存在安全问题，需要设定特定的ip范围

-- 允许所有的ip以root用户身份访问数据库

update user set host = '%' where user ='root';
flush privileges;

-- 授权root 用户所有的权限，密码为123456

-- mysql -uroot -p
-- ## mysql>命令 begin
grant all privileges on *.* to 'root'@'%' identified by '123456';
flush privileges;
-- ## end
-- exit














