# -*- coding: utf-8 -*-
from datetime import datetime

from openerp import models, fields, api


# class books_management(models.Model):
#     _name = 'books_management.books_management'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

# 创建一个书架模型
# 书架名（char 必填）
# 图书列表（one2many）
class BookCase(models.Model):
    _name = 'books_management.book_case'

    name = fields.Char(string='书架名', required=True)

    book_list = fields.One2many(comodel_name='books_management.book', inverse_name='bookcase_id', string='图书列表')


# 创建图书标签模型
# 标签名（char 必填）
# 图书列表（many2many）
class BookTag(models.Model):
    _name = 'books_management.book_tag'

    name = fields.Char(string='标签名', required=True)
    book_tag_ids = fields.Many2many(comodel_name='books_management.book', relation='book_book_tag', string='图书列表')


# 创建图书模型
# 书名(char，必填)
# 作者(char)
# 出版日期(date)
# 出版社（char）
# 所在书架（many2one 必填）
# 图书标签（many2many）
# 借阅状态（selection 必填）
class Book(models.Model):
    _name = 'books_management.book'

    name = fields.Char(string='图书名', required=True)
    author = fields.Char(string='作者名')
    pub_date = fields.Date(string='出版日期')
    pub_house = fields.Char(string='出版社')
    book_num = fields.Integer(string='图书数量', default=1)
    bookcase_id = fields.Many2one(comodel_name='books_management.book_case', string='所在书架', required=True)
    book_tag_ids = fields.Many2many(comodel_name='books_management.book_tag', relation='book_book_tag', string='图书标签')
    # [(value, string), ...]
    borrow_status = fields.Selection([('default', '存在'), ('lend', '已借完')], string='借阅状态',
                                     default='default', required=True)

    @api.onchange('book_num')
    def update_borrow_status(self):
        if self.book_num > 0:
            self.borrow_status = 'default'
        elif self.book_num == 0:
            self.borrow_status = 'lend'
        else:
            self.book_num = 0
            self.borrow_status = 'lend'
            return '图书数量不能为负数'


# 创建图书借阅表
# 用户：（many2one 必填）关联res.users模型
# 借阅的图书：（many2one 必填）关联图书表
# 借阅时间（datetime，必填，default=datetime.now()）
# 归还时间（datetime，点击“还书”按钮之后自动把当前时间写入该字段）
class BorrowBook(models.Model):
    _name = 'books_management.borrow_book'
    _rec_name = 'book_name'

    user = fields.Many2one('res.users', string='用户', required=True)
    book_name = fields.Many2one('books_management.book', string='书名', domain=[('borrow_status', '=', 'default')],
                                required=True)
    borrow_time = fields.Datetime(string='借书时间', required=True, default=datetime.now())
    return_time = fields.Datetime(string='还书时间')
    states = fields.Selection([
        ('lend_book', "在借"),
        ('return_book', "已还"),
    ], default='lend_book', string='图书状态')

    @api.model
    def create(self, vals):
        # 该函数需要返回一个创建的对象
        borrow = super(BorrowBook, self).create(vals)
        if borrow.book_name.book_num > 1:
            print borrow.book_name.book_num
            borrow.book_name.book_num -= 1
        elif borrow.book_name.book_num == 1:
            borrow.book_name.book_num = 0
            borrow.book_name.borrow_status = 'lend'
        if borrow.return_time:
            if borrow.borrow_time > borrow.return_time:
                raise BaseException
        return borrow

    @api.multi
    def return_book(self):
        # 还书的逻辑
        if self.states == 'lend_book':
            self.states = 'return_book'
            self.book_name.borrow_status = 'default'
            self.book_name.book_num += 1
            self.return_time = datetime.now()


# 创建向导模型
# 输入书名（必填）、作者、出版日期、出版社 “下一步”按钮，点击进入下一页
# 向导第二页：输入采购数量(必填)、放置书架（必填），“上一步”按钮返回上一页，“确定”按钮保存，保存完成之后将向导中填写的信息存放到“图书表”
class Wizard(models.TransientModel):
    _name = 'books_management.wizard'

    name = fields.Char(string='图书名', required=True)
    author = fields.Char(string='作者名')
    pub_date = fields.Date(string='出版日期')
    pub_house = fields.Char(string='出版社')
    book_num = fields.Integer(string='采购数量', required=True, default=1)
    bookcase_id = fields.Many2one(comodel_name='books_management.book_case', string='放置书架')
    # book_tag_ids = fields.Many2many(comodel_name='books_management.book_tag', relation='book_book_tag', string='图书标签')
    # [(value, string), ...]
    state = fields.Selection([('step1', '第一步'), ('step2', '第二步')],
                             string='当前步骤', default='step1', readonly=True)

    @api.multi
    def wizard_step1(self):
        self.state = 'step1'
        print self.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'books_management.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            # 'view_type': 'form',
            # 'views': [(False, 'form')],
            'target': 'new',
        }

    @api.multi
    def wizard_step2(self):
        self.state = 'step2'
        print self.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'books_management.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    @api.multi
    def add_book(self):
        self.env['books_management.book'].create({'name': self.name, 'author': self.author, 'pub_date': self.pub_date,
                                                  'pub_house': self.pub_house, 'book_num': self.book_num,
                                                  'bookcase_id': self.bookcase_id.id})
